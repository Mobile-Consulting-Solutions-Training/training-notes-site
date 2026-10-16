---
title: "Training 20 - AWS Glue and Redshift"
description: "CLI keys and CloudWatch, restarting Citi Bike ingestion, AWS Glue Bronze to Silver, and Redshift Serverless as the Gold layer."
---

Teacher: Evan Flint

Syllabus Day 21 (per file numbering; Oct 8) - topic: catching up on access (CLI keys, CloudWatch), restarting the Citi Bike ingestion, AWS Glue (Bronze → Silver), and introducing Redshift Serverless as the Gold layer. The roadmap lists EC2 + Lambda for Day 21 and AWS Glue for Day 22; class is running ahead.

Built from the class recording (`transcriptions/Training 20 – 2026-10-08 13-23-23/`) since no live notes were taken. Evan's reference chat for the day: "AWS Glue Class Outline" (ChatGPT share link posted in the class chat).

---

# Access Setup

Q. How do you get AWS CLI access as an IAM user?

A. (Teacher's definition) Click your username in the top right → Security credentials → Access keys → Create access key → choose "Command Line Interface (CLI)" → confirm you understand the recommendation → no tag needed → download the CSV. "This is the only time you will ever be able to view this page." Then run `aws configure`: access key ID, secret access key, region `us-east-2`, output `json`. Test with `aws s3 ls`.

**Expanded:** An **access key** is a username/password pair for programs instead of people: the **access key ID** (like a username, safe-ish to show) and the **secret access key** (like a password, never show it). The CLI stores them in `~/.aws/credentials` and uses them to sign every request.

| Step | What it does |
|---|---|
| Create access key (console) | Generates the ID + secret. The secret is shown **once** |
| Download `.csv` | Your backup copy. Store it with your other secrets (password manager), not in a project folder |
| `aws configure` | Saves the keys + default region + output format to `~/.aws/` |
| `aws s3 ls` | Quick test that the keys work |
| `aws sts get-caller-identity` | Shows *who* the CLI thinks you are |

- **Paste, don't type** the keys (Evan: "better to copy it and paste it").
- **If a key leaks** (shown on screen, committed to GitHub), stop using it: deactivate and delete it, then create a new one. "It's trivial to create new access keys."
- **Tag errors don't matter.** Adding a description to the key tries to create a tag, which students aren't allowed to do. The key still works if you can see the ID and secret.

---

Q. Why did Evan's own CLI commands keep failing with "The security token included in the request is invalid"?

A. (Teacher's definition) He has a named profile (`company`) and has to add `--profile company` to every command. Students ran `aws configure` without a profile name, so their keys are the default and they don't need it.

**Expanded:** The CLI can hold several sets of keys, each under a **profile** name. With no `--profile`, it uses the `default` profile, which on Evan's machine holds old/other keys, so AWS rejects them as an *invalid token*. Inside `$(...)` command substitution, the `--profile` flag has to go *inside* the parentheses, on the inner command. Setting `export AWS_PROFILE=company` once avoids typing it every time.

---

Q. How do you view Lambda logs in CloudWatch?

A. (Teacher's definition) Search CloudWatch → Logs → Log groups (newer console: **Log Management**) → search for the function name → click a log stream.

**Expanded:** Each Lambda writes to a log group named `/aws/lambda/<function-name>`. Each container instance writes a **log stream** inside it. Evan added CloudWatch read access to the student group in class. Watch the **region**: one student saw 115 log groups instead of 436 because they were in N. Virginia (us-east-1) instead of Ohio (us-east-2). The name is **Citi**Bike, not CityBike.

---

# Restarting the Ingestion (Incremental Loading)

Q. Why did the Bronze data stop after hour 20 yesterday?

A. (Teacher's definition) The EventBridge schedule ran at hours 18, 19 and 20, then stopped. He edited the schedule `citi-bike-ingestion-5-min` with a new start (Oct 8, 14:15) and end (17:00) time. "We want to end today at 17:00, not yesterday."

**Expanded:** EventBridge Scheduler schedules can have a **start and end date/time**. Yesterday's end time had passed, so the schedule silently did nothing. Once fixed, new `gbfs_discovery` files appeared every 5 minutes in `day=08/hour=18`. Students tested the pipeline by invoking Evan's Lambda from the CLI (`aws lambda invoke ... response.json`, then `cat response.json`). A command copied across two lines failed; it has to be on one line or use `\` continuations.

---

Q. What is incremental loading?

A. (Teacher's definition) "Not quite a streaming job. You would refer to what's happening here as incremental loading. You are regularly bringing new data into a system, but it's not a continuous stream of data like you would use in Kafka. Every so often, in our case five minutes, an amount of data is accessed and brought into the system."

**Expanded:**

| | Full load | Incremental load | Streaming |
|---|---|---|---|
| What moves | Everything, every time | Only what's new since last time | Each event as it happens |
| Cadence | Occasional (nightly, weekly) | Regular small batches (every 5 min, hourly) | Continuous |
| Example in this course | Re-reading all of Bronze each EMR run | Lambda every 5 min; Glue job bookmarks | Kafka / Kinesis (Training 13–15) |
| Tools | Any batch job | Scheduler + batch job, bookmarks, watermarks | Kafka, Kinesis, Flink, Spark Structured Streaming |

---

# AWS Glue: Bronze → Silver

Q. What is AWS Glue, compared to EMR?

A. (Teacher's definition) "Glue is basically just going to be a substitute for EMR. We'll just see two different ways to do the same kind of processing." Later: "AWS Glue is a managed data integration framework using GlueContext, DynamicFrame, the Glue Data Catalog, crawlers, job parameters, and job bookmarks."

**Expanded:** Both run Spark without you managing servers. The Bronze → Silver Glue job used the **same PySpark code** as the EMR job with tiny edits (no GlueContext at all), which proved Glue can run plain Spark. The Silver → Gold job was written "the Glue way" to show the difference (see below).

---

Q. Why use Glue instead of EMR? (Evan asked the class this)

A. (Teacher's definition) "The classical answer is that EMR is not serverless and so you use it when you want something continuous. The thing is though, is that what we've been using for EMR is serverless... EMR is closer to the actual original technology than Glue is. EMR functions like Hadoop does, even in the serverless context, and the code that we put up there was literally just Spark code. Glue is capable of running something that's just Spark code, but it also has its own API with its own standards and its own data structures. One reason that you might have to run Glue is if you want to use the DynamicFrame API." He also said it's "not really about control. You can control whatever you need to control in either."

**Expanded:** A strong interview answer has three layers:

| Layer | EMR | Glue |
|---|---|---|
| Classic (pre-serverless) | Long-running cluster for continuous/heavy work | Serverless, for occasional ETL jobs |
| Evan's answer (today) | Closest to open-source Hadoop/Spark; your code is plain Spark | Plain Spark **plus** its own API: GlueContext, DynamicFrame, Data Catalog, crawlers, bookmarks |
| Practical | Big, custom, cost-tuned workloads; any framework (Spark, Hive, Presto...) | Standard ETL with little to manage; incremental runs via job bookmarks |

---

Q. What did it take to create the Glue job?

A. (Teacher's definition) Create a Glue execution role (separate from the EMR role "because the service trust relationship is different"), attach `AWSGlueServiceRole`, add an S3 policy, upload the script to `s3://<bucket>/scripts/glue/`, add `spark.conf.set("spark.sql.session.timeZone", "UTC")` right after creating the Spark session, then `aws glue create-job` (name, role ARN, `glueetl` command + script location, `PythonVersion 3`, worker type `G.1X`, 2 workers, timeout 10, max concurrent runs 1, bookmarks enabled, TempDir).

**Expanded:**

| Step | Why |
|---|---|
| Trust policy `glue.amazonaws.com` | Lets the Glue service assume the role. An EMR role trusts `emr-serverless.amazonaws.com`, so it can't be reused as-is |
| `AWSGlueServiceRole` managed policy | Basic Glue permissions (logs, catalog, etc.) |
| Inline S3 policy | Read Bronze + script, write Silver, use TempDir |
| `G.1X` × 2 workers | 1 DPU each = 8 vCPU / 32 GB total |
| `--timeout 10` | Kills a stuck job after 10 minutes (cost guard) |
| `MaxConcurrentRuns: 1` | Two runs can't overlap and double-write |
| `job-bookmark-enable` | Remembers which files were processed |

`cat > file.json <<'EOF' ... EOF` (a **heredoc**) writes everything between the two `EOF` markers into the file. Evan created the files in his editor instead.

---

Q. What went wrong while running the Glue job, and how was each issue fixed?

A. (Teacher's definition) Walked through live.

| # | Symptom | Cause | Fix |
|---|---|---|---|
| 1 | Job created successfully on the CLI but not visible in the console | CLI default region was **us-east-1**; the console was on us-east-2 | Delete the job in us-east-1, `aws configure set region us-east-2`, create again |
| 2 | Another student's job showed in Evan's console (pointing at the student's bucket) | **Shared account**: same job name → one overwrites the other | Use unique names (e.g. add initials) |
| 3 | Script file "does not exist" on `s3 cp` | Local file used hyphens, command used underscores | Rename to match |
| 4 | `Error downloading from S3 bucket ... key scripts/...` | IAM policy resources missing `/*`, so `s3:GetObject` was an **implicit deny** | Edit the inline policy: object ARNs end with `/*` |
| 5 | `not authorized to perform s3:DeleteObject` | Script wrote (overwrite mode) to `silver/.../station_status` but the policy only allowed `glue_station_status` | Point the script at the allowed prefix and switch to **append** mode (more realistic for new data each run) |
| 6 | Success | | ~2 minutes, Snappy Parquet files in Silver |

**Expanded:** **Implicit deny** = nothing *allowed* it. IAM denies by default, so a resource ARN that doesn't match (bucket ARN vs `bucket/*` object ARN) reads as "deny" even with no Deny statement. **Overwrite** mode deletes existing files first, which is why `DeleteObject` was needed. **Append** only adds files. Also: `aws glue start-job-run` (start) and `aws glue get-job-runs` (status, including older failures); runs started on the CLI also show in the console.

---

Q. What is a DPU?

A. (Teacher's definition) Data Processing Unit. Because Glue is serverless, AWS created a unit for the compute capacity assigned to a job instead of counting cluster nodes. One DPU = 4 vCPUs + 16 GB memory. Two G.1X workers = 8 vCPUs and 32 GB "just to move our data from Bronze to Silver," but each run took 1–2 minutes so it cost little. "A DPU measures allocated compute, not processing speed. More DPUs does not always mean a faster job."

**Expanded:**

| Worker type | DPU per worker | vCPU | Memory | Use |
|---|---|---|---|---|
| G.1X | 1 | 4 | 16 GB | Most jobs (what we used) |
| G.2X | 2 | 8 | 32 GB | Memory-heavy jobs |
| G.4X / G.8X | 4 / 8 | 16 / 32 | 64 / 128 GB | Very large jobs |

Billing = DPUs × run time (per second, with a 1-minute minimum on recent Glue versions). Redshift Serverless has the same idea, called **RPUs** (Redshift Processing Units).

---

# Redshift Serverless: the Gold Layer

Q. Why load Gold into Redshift instead of another S3 folder?

A. (Teacher's definition) "Another directory of Parquet files in S3 is a completely normal and reasonable kind of gold layer, but we also can use Redshift, and Redshift is going to be more enlightening." The Gold schema should be a **star schema** because dimensional modeling "is going to be highly relevant in a large number of projects." The core data engineering services interviewers care about: **S3, Lambda, EMR, Glue, Redshift.**

**Expanded:** Planned Gold model from Evan's chat: `dim_station` (one row per station: ID, name, location, capacity) and `fact_station_snapshot` (one row per station per 5-minute snapshot: bikes/e-bikes/docks available, utilization, flags). The first test table was simpler: `public.citibike_station_snapshot` with station ID, snapshot timestamp, station mode, bikes available, e-bikes available, docks available, capacity utilization, is_empty, is_full, is_operational.

---

Q. How was Redshift Serverless set up?

A. (Teacher's definition) Redshift console → create **workgroup** `citibike-wg` → performance: "price-performance target" (instead of base capacity) → latest version → default VPC, security group and subnets ("just handled for us") → no enhanced VPC routing → **namespace** `citibike-ns` → database `dev` → IAM credentials (no admin username/password at first) → create an IAM role with access to specific S3 buckets → create. Then **Query editor v2** → connect as a federated user.

**Expanded:**

| Piece | What it is |
|---|---|
| **Namespace** | The *storage* side: databases, schemas, tables, users, and the IAM roles Redshift uses (e.g. for `COPY`) |
| **Workgroup** | The *compute* side: RPUs, network (VPC/subnets/security group), the endpoint you connect to |
| **RPU** | Redshift Processing Unit, the compute unit (like Glue's DPU) |
| **Query editor v2** | The browser SQL editor. "This is going to be the main thing you look at when you actually use Redshift." |
| `dev` | The default database |
| Federated user | Log in to the query editor with your IAM identity instead of a database password |

---

Q. What is ingress vs egress?

A. (Teacher's definition) "Ingress basically refers to traffic that is coming into a system, as opposed to egress, which is traffic going out of a system." Used with `aws ec2 authorize-security-group-ingress` to let Glue workers talk to each other and to Redshift.

**Expanded:** Security groups have **inbound (ingress)** and **outbound (egress)** rules. For Glue + Redshift: a security group with a **self-referencing** inbound rule (all TCP from the same group) so Glue workers can talk to each other, and inbound **port 5439** (Redshift's port) from Glue's group. See `Training 21.md` → Cloud Networking.

---

Q. Why did creating the Glue → Redshift connection fail, even for an administrator?

A. (Teacher's definition) Creating the connection with a username and password makes Glue try to create a **Secrets Manager** secret for those credentials, and that was denied ("even if I have administrator access, there are restrictions"). The workgroup had been created with no admin username/password, so there was nothing to put in a secret. He set one with `aws redshift-serverless update-namespace` (admin username `admin`; the password needs an uppercase letter), then created the connection from the CLI. "Why can't I just specify a username and password? Why is this so complicated?"

**Expanded:** A **Glue connection** stores how to reach a data store: the JDBC URL (`jdbc:redshift://<workgroup-endpoint>:5439/dev`), credentials (or a Secrets Manager secret), and the network placement (subnet, security group, availability zone). **Secrets Manager** stores passwords so code never contains them. It's the secure way, but it needs its own permissions. **CloudTrail** records every API call and shows exactly who was denied what. Evan's password was deliberately weak "to be changed later." In real work, use a strong one stored in Secrets Manager.

---

Q. What does Glue-specific code look like (Silver → Gold)?

A. (Teacher's definition) "This is the difference in Glue code versus Spark code. We have all of these imports from Glue... we create a SparkContext, pass that to a GlueContext, and get a Spark session out of the GlueContext. Then the rest is slightly modified Spark code." It writes with `glueContext.write_dynamic_frame`. "A DynamicFrame is basically like a DataFrame, except that the number of columns doesn't have to be as strict. It's designed for handling JSON-type data, which is nested, so it's more flexible."

**Expanded:**

```python
import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from pyspark.context import SparkContext

args = getResolvedOptions(sys.argv, ["JOB_NAME"])   # job parameters
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session                   # plain Spark still available
job = Job(glueContext)
job.init(args["JOB_NAME"], args)                    # needed for bookmarks

df = spark.read.parquet("s3://<bucket>/silver/...")  # ...normal Spark transforms...
dyf = DynamicFrame.fromDF(df, glueContext, "gold")

glueContext.write_dynamic_frame.from_jdbc_conf(      # load into Redshift via the Glue connection
    frame=dyf,
    catalog_connection="<glue-connection-name>",
    connection_options={"dbtable": "public.citibike_station_snapshot", "database": "dev"},
    redshift_tmp_dir="s3://<bucket>/glue-temp/",    # Glue stages files here, then Redshift COPYs them
)
job.commit()                                         # saves the bookmark
```

| | Spark DataFrame | Glue DynamicFrame |
|---|---|---|
| Schema | Fixed, decided up front | Each record can differ; inconsistent types are kept as "choice" types to resolve later |
| Best for | Clean, consistent data | Messy or nested JSON, schema drift |
| Convert | `DynamicFrame.fromDF(df, glueContext, name)` | `dyf.toDF()` |
| Extras | Spark API | Catalog reads/writes, bookmarks, `resolveChoice`, `relationalize` (flattens nesting) |

---

Q. Where did the live demo end?

A. (Teacher's definition) The target table was created in the query editor, the Silver → Redshift Glue job was created and started, and it failed with "Could not find S3 endpoint or NAT gateway for subnet ID." "This is not an authentication problem. This is a networking problem, a low-level cloud setup problem." Too big to debug in 10 minutes, so it was carried over to the next class. "Frustrating problems like this that don't seem to make any sense are just a normal part of working on cloud services... They all have NAT gateways, they all have subnets and they all have annoying authentication problems. Even Google Cloud."

**Expanded:** The Glue connection placed the job inside Redshift's private subnet, which had no route to S3. Fix: an S3 Gateway Endpoint (see `Training 21.md`).

---

# Homework (Training 20)

Get as close as possible to loading Silver (S3) into Gold (Redshift); bonus for actually getting data in. Deliverable: explain progress and issues at the start of the next class. Evan:

- "Get as far along the same pathway as I have gotten, and bonus points if you can get farther." Once data is in, `SELECT * FROM public.citibike_station_snapshot;`
- You can use your own bucket and workgroup. "If you can't create your own because of a permissions issue, fall back on my infrastructure."
- Post the **exact name of any permission error** in the class group chat, and he'll look at granting it.
- Next up: ECS/Fargate ("slightly more niche"), then Kinesis replacing the ingestion job later. Three more days of AWS.

---
