---
title: "Reference - Training 19: AWS Services Used in Class"
description: "Look-it-up reference: one section per AWS service from Training 19, with commands, console steps and gotchas."
sidebar:
  order: 191
---

Source: the class recording (Oct 7, 4h09m), what was on Evan's screen, and [Training 19 notes](/training-notes-site/notes/training-19/). This is a **look-it-up** reference: one section per service, in the order they showed up in class. For the story of what Evan built, step by step, see [Walkthrough - Training 19 (Citi Bike Pipeline Build)](/training-notes-site/walkthroughs/training-19-citi-bike-pipeline/).

Each section has:
- **What it is**, in one or two sentences
- **What Evan used it for**
- **Commands / console steps**, with the actual names from class (`citi-bike-nyc-pipeline`, `citibike-ingestion`, `CitiBikeLambdaRole`...)
- **Gotchas seen in class**, the errors that actually came up and why

**Your access is console-only** (no CLI access keys, not an admin in the training account). Evan built most of this with the CLI, so the CLI commands below show *what he did*. For your own work, use the console click-paths given for each service. The homework guide will be console-first. (CloudShell, the browser terminal, is **not** available to your user either: "Unable to create the environment ... insufficient permissions". So it's console clicks only.)

Never paste real access keys or the account ID into files or chat. In the commands below `<ACCOUNT_ID>` and `<...>` are placeholders.

---

## The big picture (what everything below adds up to)

```
Citi Bike GBFS API (public JSON, refreshes every 60 s)
        │
        │  EventBridge Scheduler: rate(5 minutes)
        ▼
Lambda  citibike-ingestion   (Python + boto3; runs as IAM role CitiBikeLambdaRole)
        │  s3:PutObject
        ▼
S3  citi-bike-nyc-pipeline / bronze/citibike/<feed>/year=/month=/day=/hour=/<feed>_<timestamp>.json
        │
        │  EMR Serverless job run "bronze-to-silver" (PySpark; runs as an EMR execution role)
        ▼
S3  .../silver/...  (Parquet: clean station state)
        │
        ▼   (later classes, not built yet)
Redshift Serverless → Streamlit on ECS/Fargate or QuickSight
```

| Service | Job in this pipeline |
|---|---|
| **AWS CLI** | Typing AWS commands in the terminal (create buckets, roles, Lambda...) |
| **IAM** | Who you are (user + access keys) and what each service is allowed to do (roles + policies) |
| **STS** | "Who am I logged in as?" (`get-caller-identity`) |
| **S3** | Stores the raw JSON (Bronze), the Spark script, and the clean Parquet (Silver) |
| **boto3** | Python's way to call AWS (the ingestion code uses it to write to S3) |
| **Lambda** | Runs the ingestion script in AWS without a server |
| **CloudWatch Logs** | Where Lambda's `print()` output and errors go |
| **EventBridge Scheduler** | Runs the Lambda every 5 minutes |
| **EMR Serverless / EMR Studio** | Runs the Spark job that turns Bronze JSON into Silver Parquet |

---

# 1. AWS CLI

**What it is:** a command-line program (`aws`) that lets you do almost anything from the AWS web console by typing commands. Every command has the shape:

```
aws <service> <action> --option value ...
aws s3api create-bucket --bucket citi-bike-nyc-pipeline ...
```

**What Evan used it for:** most of the build (S3 bucket, IAM role/policy, Lambda create/invoke, logs) was done from the terminal with the CLI, following ChatGPT's steps.

### Installing it

Evan posted two ways in the chat:

```bash
# Official installer script (Linux)
curl -fsSL https://awscli.amazonaws.com/v2/install.sh | bash

# Or with pip (older v1 CLI from PyPI)
pip install awscli --upgrade --user
```

On **your Mac**, the cleanest options are the official `.pkg` installer from AWS, or Homebrew:

```bash
brew install awscli
aws --version          # should print aws-cli/2.x ...
```

### Credentials and profiles

The CLI needs to know **who you are**. For a person that means an IAM user's **access key ID** + **secret access key** (from IAM → your user → Security credentials → Create access key).

```bash
aws configure --profile company
# AWS Access Key ID:     <your key id>
# AWS Secret Access Key: <your secret>
# Default region name:   us-east-2
# Default output format: json
```

That writes two files:

| File | Holds |
|---|---|
| `~/.aws/credentials` | The keys, under a `[company]` section |
| `~/.aws/config` | Region and output format, under `[profile company]` |

Then add `--profile company` to every command, or set it once per terminal: `export AWS_PROFILE=company`.

**A profile** is just a named set of credentials. Evan had two: `personal` (his own AWS account) and `company` (the training account). `--profile` picks which account a command runs against.

### How the CLI decides which credentials to use (order matters)

| Priority | Source |
|---|---|
| 1 (highest) | Command-line options like `--profile` |
| 2 | **Environment variables** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_PROFILE` |
| 3 | `~/.aws/credentials` / `~/.aws/config` (the `default` profile if none named) |
| 4 | An IAM role attached to the machine (EC2, Lambda, ECS) |

### Useful commands

```bash
aws sts get-caller-identity --profile company         # who am I? (see STS below)
aws s3 ls --profile company                            # list buckets
aws s3 ls s3://citi-bike-nyc-pipeline/bronze/ --recursive --profile company
aws <service> help                                     # built-in docs, e.g. aws s3api help
```

### Gotchas seen in class

| Error on screen | What it meant | Fix |
|---|---|---|
| `argument subcommand: Found invalid choice 'create-bucket'` from `aws s3 create bucket ...` | There are **two** S3 command sets. `aws s3` is the friendly one (`ls`, `cp`, `mb`, `sync`); `create-bucket` lives in the low-level **`aws s3api`** | `aws s3api create-bucket ...` or `aws s3 mb s3://name` |
| `InvalidAccessKeyId: The AWS Access Key Id you provided does not exist in our records` | The keys being used weren't real keys. Evan had `export AWS_ACCESS_KEY_ID=...` lines in `~/.bashrc` with placeholder values, and **environment variables override the default profile** | Remove/fix the exports, or pass `--profile company` |
| (Practice note) keys pasted into `.bashrc` | Works, but it's how keys leak (dotfiles get copied, shared, committed) | Use `aws configure --profile` instead |

---

# 2. IAM (and STS)

**What it is:** the permission system for the AWS account (Training 18). Today it showed up in **two different ways**, and keeping them apart is the key to the whole class:

| | For **you** (a person at a terminal) | For a **service** (Lambda, EMR) |
|---|---|---|
| Identity | **IAM user** (e.g. your name in the training account) | **IAM role** (e.g. `CitiBikeLambdaRole`) |
| Credentials | Long-term **access keys** in `~/.aws/credentials` | **Temporary** credentials AWS hands the service automatically |
| In code | `boto3.Session(profile_name="company")` | `boto3.client("s3")` with no keys at all |

### Console access for students

Late in class (3:13 PM) Evan posted the **console sign-in URL** for the training account: `https://<account-alias>.signin.aws.amazon.com/console`. An IAM user signs in there with **account alias + username + password**, not at the normal root login page.

**Gotcha seen in class:** `You may not be authorized to perform this action, or the new password does not comply with the account password policy set by your administrator.` That's the forced password change on first login. The new password has to meet the account's **password policy** (length, uppercase, numbers, symbols, not reusing the old one).

### STS: "who am I?"

**STS (Security Token Service)** issues temporary credentials (it's what makes roles work). The one command you'll use constantly:

```bash
aws sts get-caller-identity --profile company
```

```json
{
  "UserId": "AIDA...",
  "Account": "<ACCOUNT_ID>",
  "Arn": "arn:aws:iam::<ACCOUNT_ID>:user/<your-username>"
}
```

Run it **first** whenever something is denied: it proves which account and which identity your command is really using.

Grab the account ID into a shell variable (Evan did this to build ARNs):

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --profile company --query Account --output text)
echo $ACCOUNT_ID
```

`--query` picks one field out of the JSON (it's JMESPath syntax) and `--output text` drops the quotes.

### Roles need TWO policies (this is the part people trip on)

| Policy | Answers | File in class | Attached how |
|---|---|---|---|
| **Trust policy** | **Who may *become* (assume) this role?** | `lambda-trust-policy.json`, `emr-trust-policy.json` | Given when the role is created (`--assume-role-policy-document`) |
| **Permissions policy** | **What can the role *do* once assumed?** | `lambda-s3-policy.json` (policy `CitiBikeLambdaS3Write`) | `create-policy`, then `attach-role-policy` |

Trust policy for Lambda (lets the Lambda service assume the role):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "lambda.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
```

For EMR Serverless, the same file but `"Service": "emr-serverless.amazonaws.com"` (shown in class around 3:37).

Permissions policy (only write into the Bronze Citi Bike prefix: least privilege):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:PutObject"],
    "Resource": "arn:aws:s3:::citi-bike-nyc-pipeline/bronze/citibike/*"
  }]
}
```

The commands, in order (as in class):

```bash
# 1. Create the role with its trust policy
aws iam create-role \
  --role-name CitiBikeLambdaRole \
  --assume-role-policy-document file://lambda-trust-policy.json \
  --profile company

# 2. Let it write logs to CloudWatch (AWS-managed policy; the homework requires log access)
aws iam attach-role-policy \
  --role-name CitiBikeLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
  --profile company

# 3. Create your own S3-write policy from the JSON file
aws iam create-policy \
  --policy-name CitiBikeLambdaS3Write \
  --policy-document file://lambda-s3-policy.json \
  --profile company

# 4. Attach it to the role
aws iam attach-role-policy \
  --role-name CitiBikeLambdaRole \
  --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/CitiBikeLambdaS3Write \
  --profile company

# 5. Save the role's ARN for create-function
LAMBDA_ROLE_ARN=$(aws iam get-role --role-name CitiBikeLambdaRole \
  --query 'Role.Arn' --output text --profile company)
```

`file://` tells the CLI "read this argument from a local file."

**What the role ends up looking like** (ChatGPT's diagram on screen):

```
CitiBikeLambdaRole
   ├── CloudWatch logging     (AWSLambdaBasicExecutionRole)
   └── s3:PutObject  →  citi-bike-nyc-pipeline/bronze/citibike/*
```

**ARN** (Amazon Resource Name) is the full unique ID of anything in AWS: `arn:aws:<service>:<region>:<account>:<resource>`. S3 ARNs have no region/account (`arn:aws:s3:::bucket/key`) because bucket names are global.

**Gotcha:** right after creating a role, `create-function` can fail with "The role defined for the function cannot be assumed by Lambda." IAM changes take a few seconds to **propagate**. Wait 10–20 s and retry (ChatGPT's steps warned about this too).

---

# 3. S3 (hands-on this time)

Concepts are in Training 18. Today was the **practical** side.

### Creating a bucket

```bash
aws s3api create-bucket \
  --bucket citi-bike-nyc-pipeline \
  --region us-east-2 \
  --create-bucket-configuration LocationConstraint=us-east-2 \
  --profile company

# or the short form:
aws s3 mb s3://citi-bike-nyc-pipeline --region us-east-2 --profile company
```

### Gotchas seen in class

| Error | Meaning | Fix |
|---|---|---|
| `BucketAlreadyExists: The requested bucket name is not available. The bucket namespace is shared by all users of the system.` | Bucket names are **globally unique across all AWS accounts**, and someone already owns `citi-bike-nyc` | Pick a more specific name. Evan switched to `citi-bike-nyc-pipeline`. Homework: **use your name** in yours |
| `IllegalLocationConstraintException: The unspecified location constraint is incompatible for the region specific endpoint this request was sent to.` | **Every region except `us-east-1`** needs `--create-bucket-configuration LocationConstraint=<region>` | Add it (see above). ChatGPT on screen: "S3 has an odd special case: `us-east-1` doesn't require LocationConstraint, but other regions do." |

### Reading what landed

Console: S3 → `citi-bike-nyc-pipeline` → `bronze/` → `citibike/` → `gbfs_discovery/` → `year=2026/` → `month=10/` → `day=07/` → `hour=18/` → `gbfs_discovery_20261007T182800Z.json` (3.4 KB, Standard storage class). The "folders" are just parts of the key.

```bash
aws s3 ls s3://citi-bike-nyc-pipeline/bronze/citibike/ --recursive --profile company
aws s3 cp s3://citi-bike-nyc-pipeline/bronze/citibike/station_status/year=2026/month=10/day=07/hour=19/<file>.json - --profile company | head -c 500
```

(`cp ... -` prints the object to the terminal instead of saving it.)

**Hour folders are UTC.** A file written at 2:28 PM New York time lands in `hour=18` (EDT = UTC−4).

### Suggested layout for the homework bucket

```
s3://<yourname>-citi-bike-pipeline/
   bronze/citibike/<feed>/year=/month=/day=/hour=/...json    ← Lambda writes here
   scripts/bronze_to_silver.py                                ← the Spark script EMR runs
   silver/citibike/station_status/  (Parquet)                 ← EMR writes here
   silver/citibike/station_information/  (Parquet)
   emr-logs/                                                  ← EMR job logs
```

---

# 4. boto3 (the AWS SDK for Python)

**What it is:** the Python library for calling AWS. Anything the CLI can do, boto3 can do from code.

```python
import boto3

# On your laptop: use a named profile
session = boto3.Session(profile_name="company", region_name="us-east-2")
s3 = session.client("s3")

# Inside Lambda / EMR / ECS: NO profile, the role supplies credentials
s3 = boto3.client("s3")

s3.put_object(Bucket="citi-bike-nyc-pipeline",
              Key="bronze/citibike/test.json",
              Body=b'{"hello":"world"}',
              ContentType="application/json")
```

| Call | Does |
|---|---|
| `s3.put_object(Bucket, Key, Body)` | Upload bytes as one object |
| `s3.get_object(Bucket, Key)["Body"].read()` | Download an object |
| `s3.list_objects_v2(Bucket, Prefix)` | List keys under a prefix |
| `s3.upload_file(local_path, Bucket, Key)` | Upload a local file |

**Install:** `pip install boto3` locally (`pip show boto3` showed 1.38.x in class). **Lambda's Python runtime already includes boto3**, so the Lambda zip only needed `lambda_function.py`.

**Gotcha:** `boto3.Session(profile_name="company")` **fails inside Lambda** (there's no `~/.aws` folder there). That's why the local script and the Lambda version differ in exactly that line.

---

# 5. AWS Lambda (hands-on)

**What it is:** runs one function in AWS when triggered; no server; billed per request and per millisecond. Max **15 minutes** per run. (Concepts in Training 18.)

**What Evan used it for:** the ingestion script, as function **`citibike-ingestion`**: download the 3 GBFS feeds + discovery doc and write them to S3 Bronze.

### The code shape

The local script's `main()` becomes a **handler**:

```python
# lambda_function.py
import json, urllib.request
from datetime import datetime, timezone
import boto3

BUCKET = "citi-bike-nyc-pipeline"
s3 = boto3.client("s3")          # role credentials, no profile

def lambda_handler(event, context):
    snapshot_time = datetime.now(timezone.utc)
    # ... same discovery + get_json + write_json_to_s3 logic as ingest_to_s3.py ...
    return {
        "statusCode": 200,
        "snapshot_time": snapshot_time.isoformat(),
        "files_uploaded": len(uploaded) + 1,
        "objects": uploaded,
    }
```

The `--handler` setting `lambda_function.lambda_handler` means **file name** `.` **function name**.

### Deploying from the CLI

```bash
zip lambda.zip lambda_function.py

aws lambda create-function \
  --function-name citibike-ingestion \
  --runtime python3.14 \
  --role "$LAMBDA_ROLE_ARN" \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda.zip \
  --timeout 60 \
  --memory-size 256 \
  --region us-east-2 \
  --profile company

# After editing the code:
zip lambda.zip lambda_function.py
aws lambda update-function-code --function-name citibike-ingestion \
  --zip-file fileb://lambda.zip --region us-east-2 --profile company
```

| Option | Meaning |
|---|---|
| `--runtime` | Python version AWS runs it with (class used Python 3.14) |
| `--role` | The execution role's ARN, i.e. what the function is allowed to do |
| `--zip-file fileb://` | Upload a local zip (`fileb://` = binary file) |
| `--timeout 60` | Kill it after 60 s (default is only 3 s, too short for 4 downloads) |
| `--memory-size 256` | MB of RAM (CPU scales with it) |

The create response includes `"State": "Pending"`, "The function is being created." Wait for `Active` before invoking.

### Testing it by hand (do this before scheduling)

```bash
aws lambda invoke \
  --function-name citibike-ingestion \
  --payload '{}' \
  --region us-east-2 --profile company \
  response.json

cat response.json
```

Two different "status" values show up, which is confusing:

| Where | Example | Means |
|---|---|---|
| Printed by the CLI | `"StatusCode": 200` | Lambda **ran** the function (even if your code then crashed) |
| Inside `response.json` | `{"statusCode": 200, "files_uploaded": 4, "objects": [...]}` | What **your** handler returned |
| `"FunctionError": "Unhandled"` in the CLI output | — | Your code threw an exception; `response.json` holds the error and the logs have the traceback |

In class the successful run returned `files_uploaded: 4` (discovery + 3 feeds) at `hour=19`.

**Console route (same thing):** Lambda → Create function → Author from scratch → name, runtime, "Use an existing role" → paste code in the editor → **Deploy** → **Test** tab → create test event `{}` → **Test**.

---

# 6. CloudWatch Logs

**What it is:** AWS's log storage. Everything a Lambda `print()`s, plus every error, goes to a **log group** named `/aws/lambda/<function-name>`.

```bash
aws logs tail /aws/lambda/citibike-ingestion --region us-east-2 --profile company
aws logs tail /aws/lambda/citibike-ingestion --follow --since 30m --region us-east-2 --profile company
```

**What a run looks like in the log:**

```
INIT_START Runtime Version: python:3.14...        ← cold start
START RequestId: ...
CITI BIKE INGESTION
Snapshot: 2026-10-07T19:28:02...
Downloading: https://gbfs.lyft.com/gbfs/1.1/bkn/en/system_information.json
Uploaded 3,463 bytes -> s3://citi-bike-nyc-pipeline/bronze/citibike/gbfs_discovery/...
...
END RequestId: ...
REPORT RequestId: ... Duration: 1117.59 ms  Billed Duration: 1664 ms  Memory Size: 256 MB  Max Memory Used: 110 MB
```

| Log line | Tells you |
|---|---|
| `INIT_START` | A **cold start** (new environment loaded). Missing on warm runs |
| `REPORT ... Duration / Billed Duration` | How long it ran and what you paid for |
| `Max Memory Used` vs `Memory Size` | Whether you gave it too much or too little RAM |
| A `Traceback (most recent call last)` | The Python error, with file and line (`lambda_function.py, line 56, in write_json_to_s3 → s3.put_object`) |

ChatGPT's point on screen, worth remembering: production data engineers don't debug by staring at code. **They inspect observability data** (logs, metrics). `aws logs tail` is step one when a job misbehaves.

**Gotcha seen in class:** a run failed inside `write_json_to_s3` → `s3.put_object` (`lambda_function.py, line 102`) with:

```
[ERROR] NoSuchBucket: An error occurred (NoSuchBucket) when calling the PutObject operation: The specified bucket does not exist
```

The code still had the **old bucket name** (`citi-bike-nyc`, which belongs to someone else) instead of `citi-bike-nyc-pipeline`. The fix was changing `BUCKET`, re-zipping, and updating the function. A failure at `put_object` is almost always one of two things:

| Error | Cause |
|---|---|
| `NoSuchBucket` | Wrong bucket name in the code (typo, or the old name) |
| `AccessDenied` | The role's policy doesn't cover that bucket/prefix. Check the policy `Resource` matches the exact bucket and prefix the code writes to |

---

# 7. EventBridge Scheduler

**What it is:** AWS's managed scheduler, essentially **cron in the cloud**. It invokes a target (Lambda, Step Functions, ECS task...) on a schedule. It's the newer, separate cousin of "EventBridge rules" (event-pattern routing from Training 18).

**What Evan used it for:** run `citibike-ingestion` **every 5 minutes** so Bronze builds up a history of snapshots.

### Console steps (the route Evan took)

Lambda → `citibike-ingestion` → **Add trigger** → source **EventBridge** → choose **Schedule expression** → the console offers **"Continue in EventBridge Scheduler"** (the new scheduling capability) →

| Setting | Value in class | Meaning |
|---|---|---|
| Schedule type | Recurring, **rate-based** | "Every N minutes/hours/days" |
| Rate expression | `rate(5 minutes)` | Every 5 minutes |
| Flexible time window | **Off** | Run exactly on time (otherwise AWS may spread it across a window) |
| Timeframe: start | 2026/10/07 15:40 | Don't start before this |
| Timeframe: end | 2026/10/07 17:00 | **Stop automatically**: a cost guard for a demo |
| Payload | `{}` | The `event` passed to `lambda_handler` |
| Execution role | Evan's: **`CitiBikeSchedulerRole`** | The **scheduler's** own role, allowed to `lambda:InvokeFunction` (see below) |

### The Scheduler's own role (`CitiBikeSchedulerRole`)

The schedule doesn't run as you, and it doesn't use the Lambda's role either. EventBridge Scheduler assumes **its own role** whose only job is to invoke the function. Evan made it with the CLI (around 3:14–3:20):

```json
// scheduler-trust-policy.json: WHO can assume the role
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "scheduler.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
```

```json
// permissions policy: WHAT the role may do (only invoke this one function)
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "lambda:InvokeFunction",
    "Resource": "arn:aws:lambda:us-east-2:<ACCOUNT_ID>:function:citibike-ingestion"
  }]
}
```

The whole chain of roles (this is the homework's Part 5 diagram):

```
EventBridge Scheduler ──assumes──▶ CitiBikeSchedulerRole ──lambda:InvokeFunction──▶ Lambda citibike-ingestion
                                                                                      │ assumes
                                                                                      ▼
                                                                          CitiBikeLambdaRole ──s3:PutObject──▶ S3 bronze/
```

His schedule was named **`citi-bike-ingestion-5-min`** (in the `default` schedule group), checked with `aws scheduler list-schedules` and `aws scheduler get-schedule`.

**In the console** the Scheduler wizard can **create this role for you** ("Create new role for this schedule"). It builds both policies automatically. That's the console-only route, if your account is allowed to create roles.

**Watch for in class:** at ~4:25 PM the Bronze `station_status` prefix still held only 3 files (18:28 local run, 19:28 manual Lambda invoke, 20:25 UTC), not one every 5 minutes. So the scheduled runs weren't all landing yet when Evan moved on to Spark. That's why the homework's Part 6 says to **confirm the automation works before touching Spark**.

### Rate vs cron expressions

| Expression | Runs |
|---|---|
| `rate(5 minutes)` | Every 5 minutes |
| `rate(1 hour)` | Every hour |
| `cron(0 2 * * ? *)` | 2:00 AM every day (UTC by default; Scheduler lets you pick a time zone) |
| `cron(*/5 13-21 ? * MON-FRI *)` | Every 5 min, 1–9 PM, weekdays |

AWS cron has **6 fields** (minutes, hours, day-of-month, month, day-of-week, **year**) and needs `?` in one of the two day fields. Linux cron (Training 1) has 5.

```bash
aws scheduler list-schedules --region us-east-2 --profile company
aws scheduler get-schedule --name <schedule-name> --region us-east-2 --profile company
```

**Cost math for 5-minute ingestion:** 288 runs/day × ~1.1 s × 256 MB ≈ well under a cent a day for Lambda, plus ~1,150 small S3 objects/day. Cheap, but **set an end time or delete the schedule** when you're done (same habit as Evan's 17:00 end).

---

# 8. EMR Serverless and EMR Studio

**What it is:** Spark jobs without a cluster (concepts in [Training 19 notes](/training-notes-site/notes/training-19/)). You create an **application** once, then submit **job runs**; you pay only while jobs run.

**What Evan used it for:** `bronze_to_silver.py`, a PySpark job that reads the raw Bronze JSON, flattens it, and writes clean Silver data.

### The pieces you need

| Piece | Example | Why |
|---|---|---|
| **Script in S3** | `s3://citi-bike-nyc-pipeline/scripts/bronze_to_silver.py` | EMR Serverless can't read your laptop |
| **Execution role** | Evan's: **`CitiBikeEMRRole`** (trust `emr-serverless.amazonaws.com`) with policy **`CitiBikeEMRS3Access`** | What the Spark job may read/write (policy below) |
| **Application** | Type **Spark**, a recent EMR release | Reusable; costs nothing when idle |
| **Job run** | Name `bronze-to-silver`; entry point = the S3 script | One execution |

Evan's `emr-s3-policy.json` (`CitiBikeEMRS3Access`), from the screen at ~3:35:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::citi-bike-nyc-pipeline"] },
    { "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::citi-bike-nyc-pipeline/scripts/*",
                   "arn:aws:s3:::citi-bike-nyc-pipeline/bronze/*"] },
    { "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": ["arn:aws:s3:::citi-bike-nyc-pipeline/silver/*"] }
  ]
}
```

| Statement | Why it's needed |
|---|---|
| `ListBucket` on the **bucket** ARN (no `/*`) | Spark lists the folders to find files. Listing is a bucket-level action, so its Resource is the bucket itself |
| `GetObject` on `scripts/*` and `bronze/*` | Read the script, and read the raw JSON |
| `Get/Put/DeleteObject` on `silver/*` | Write Parquet. **Delete** is needed because `mode("overwrite")` removes old output first, and Spark cleans up temporary files |

This matches the homework's Part 7 exactly (READ bronze, READ scripts, READ/WRITE silver).

**Gotcha seen in class:** `aws s3 cp bronze_to_silver.py s3://...` failed with *"The user-provided path bronze_to_silver.py does not exist"* because the terminal was in the `citibike-lambda` folder, not `citibike-emr`. `cd` to the right folder, then retry. (In the console you upload by picking the file, so this can't happen.)

### CLI version

```bash
aws s3 cp bronze_to_silver.py s3://citi-bike-nyc-pipeline/scripts/ --profile company

aws emr-serverless create-application \
  --name citibike-spark --type SPARK --release-label <emr-7.x release> \
  --region us-east-2 --profile company

aws emr-serverless start-job-run \
  --application-id <app-id> \
  --execution-role-arn arn:aws:iam::$ACCOUNT_ID:role/<emr-execution-role> \
  --name bronze-to-silver \
  --job-driver '{"sparkSubmit": {"entryPoint": "s3://citi-bike-nyc-pipeline/scripts/bronze_to_silver.py"}}' \
  --configuration-overrides '{"monitoringConfiguration": {"s3MonitoringConfiguration": {"logUri": "s3://citi-bike-nyc-pipeline/emr-logs/"}}}' \
  --region us-east-2 --profile company

aws emr-serverless get-job-run --application-id <app-id> --job-run-id <run-id> --region us-east-2 --profile company
```

### Console version: EMR Studio

AWS console → **EMR** → **EMR Serverless** → **Get started / EMR Studio** → **Applications** → create (Spark) → open the application → **Submit job run** (name, runtime role, script S3 location, arguments) → watch **State**: `Submitted → Pending → Scheduled → Running → Success | Failed`. Click a run to see **Job details**, the error message, and **Spark UI / driver logs** (stdout/stderr).

### The Spark script's key moves (`bronze_to_silver.py`, on screen around 3:27)

GBFS files are **one big JSON object** with the stations in an array: `{"last_updated":..., "ttl":60, "data": {"stations": [ {...}, {...} ]}}`.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, input_file_name, regexp_extract, to_timestamp

spark = SparkSession.builder.appName("bronze-to-silver").getOrCreate()

STATUS_PATH = "s3://citi-bike-nyc-pipeline/bronze/citibike/station_status/"
INFO_PATH   = "s3://citi-bike-nyc-pipeline/bronze/citibike/station_information/"

# 1. Read: multiLine because each file is ONE JSON document, not one-object-per-line
status_raw = (spark.read
              .option("multiLine", "true")
              .option("recursiveFileLookup", "true")   # walk year=/month=/... folders (optional; Spark can also read them as partitions)
              .json(STATUS_PATH)
              .withColumn("source_file", input_file_name()))

# 2. Explode: one row per file -> one row per station
status = status_raw.select(col("source_file"),
                           explode(col("data.stations")).alias("station"))

# 3. Recover the snapshot time from the file name: station_status_20261007T192802Z.json
status = (status
    .withColumn("snapshot_string",
                regexp_extract(col("source_file"), r"station_status_(\d{8}T\d{6}Z)", 1))
    .withColumn("snapshot_timestamp",
                to_timestamp(col("snapshot_string"), "yyyyMMdd'T'HHmmss'Z'")))

# 4. Pick + rename the columns you need
status = status.select(
    col("station.station_id").alias("station_id"),
    col("snapshot_timestamp"),
    col("station.num_bikes_available").alias("bikes_available"),
    col("station.num_docks_available").alias("docks_available"),
    col("station.is_installed"), col("station.is_renting"), col("station.is_returning"),
)

# 5. Same idea for station_information (name, lat, lon, capacity), then join on station_id
# 6. Inspect, then write Silver as Parquet (what Evan's script did at the end)
silver.printSchema()
print(silver.count())
silver.show(20, truncate=False)
silver.write.mode("overwrite").parquet("s3://citi-bike-nyc-pipeline/silver/citibike/station_status/")
```

| Function | Does |
|---|---|
| `option("multiLine", "true")` | Read a JSON file that is one pretty-printed document (Spark's default expects **one JSON object per line**) |
| `explode(col("data.stations"))` | Turns an array column into **one row per element** |
| `input_file_name()` | Adds the S3 path of the file each row came from |
| `regexp_extract(col, pattern, 1)` | Pulls out regex capture group 1 |
| `to_timestamp(col, "yyyyMMdd'T'HHmmss'Z'")` | Parses `20261007T192802Z`; quoted `'T'` and `'Z'` are literal letters |
| `col("station.num_bikes_available")` | Reaches into a struct field with dot notation |

### Gotcha seen in class (the job run failed)

EMR Studio showed job run **`bronze-to-silver` → Failed** with:

```
pyspark.errors.exceptions.captured.AnalysisException:
[FIELD_NOT_FOUND] No such struct field `num_vehicles_available` in
 eightd_has_available_keys, is_installed, is_renting, is_returning, last_reported, legacy_id,
 num_bikes_available, num_bikes_disabled, num_docks_available, num_docks_disabled,
 num_ebikes_available, num_scooters_available, num_scooters_unavailable, station_id
```

**Why:** the script (ChatGPT-written) asked for `station.num_vehicles_available`, a field name from a **newer GBFS version (v3)**. Citi Bike's feed is **GBFS 1.1**, where the field is **`num_bikes_available`**. Spark helpfully lists every field that *does* exist.

**Lesson:** profile the real data first (that's what `explore_gbfs.py` was for) and build the `select` from fields you've actually seen. Never trust a generated schema blindly.

---

# 9. Mentioned at the start, not built yet

These were in Evan's opening architecture (see [Training 19 notes](/training-notes-site/notes/training-19/)) but the homework says **don't build them yet**:

| Service | Role later | Notes |
|---|---|---|
| **Redshift Serverless** | Data warehouse for the Gold layer, loaded with `COPY` | Training 18 notes + Training 19 notes |
| **ECS / Fargate** | Hosts the Streamlit dashboard container | Training 19 notes ("Fargate cost when idle" accuracy note) |
| **Streamlit** | Python dashboard app | Training 19 notes |
| **QuickSight** | No-code BI alternative to Streamlit | Training 19 notes |
| **SageMaker** | ML on the data | Training 18 notes |

---

# Quick command sheet (everything in one place)

```bash
# --- identity ---
aws configure --profile company
aws sts get-caller-identity --profile company
ACCOUNT_ID=$(aws sts get-caller-identity --profile company --query Account --output text)

# --- S3 ---
aws s3api create-bucket --bucket <name> --region us-east-2 \
  --create-bucket-configuration LocationConstraint=us-east-2 --profile company
aws s3 ls s3://<name>/ --recursive --profile company
aws s3 cp file.py s3://<name>/scripts/ --profile company

# --- IAM role for Lambda ---
aws iam create-role --role-name <Role> --assume-role-policy-document file://lambda-trust-policy.json --profile company
aws iam attach-role-policy --role-name <Role> --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole --profile company
aws iam create-policy --policy-name <Policy> --policy-document file://lambda-s3-policy.json --profile company
aws iam attach-role-policy --role-name <Role> --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/<Policy> --profile company

# --- Lambda ---
zip lambda.zip lambda_function.py
aws lambda create-function --function-name <fn> --runtime python3.14 --role <role-arn> \
  --handler lambda_function.lambda_handler --zip-file fileb://lambda.zip \
  --timeout 60 --memory-size 256 --region us-east-2 --profile company
aws lambda invoke --function-name <fn> --payload '{}' --region us-east-2 --profile company response.json
aws logs tail /aws/lambda/<fn> --follow --region us-east-2 --profile company

# --- Scheduler ---
aws scheduler list-schedules --region us-east-2 --profile company

# --- EMR Serverless ---
aws emr-serverless start-job-run --application-id <id> --execution-role-arn <arn> \
  --job-driver '{"sparkSubmit":{"entryPoint":"s3://<name>/scripts/bronze_to_silver.py"}}' \
  --region us-east-2 --profile company
```

On zsh (your Mac's shell), quote anything with `*`, `?` or `[` in it, e.g. `'cron(0 2 * * ? *)'`, or zsh tries to expand it as a filename.
