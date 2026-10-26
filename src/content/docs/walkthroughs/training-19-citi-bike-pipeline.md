---
title: "Walkthrough - Training 19: Citi Bike Pipeline (Bronze to Silver)"
description: "The story of the first half of the Citi Bike batch pipeline: Lambda, EventBridge Scheduler, S3, IAM and EMR Serverless."
sidebar:
  order: 190
---

Source material: [Training 19 notes](/training-notes-site/notes/training-19/) and the class demo. Service-by-service reference (commands, JSON, console clicks): [Reference - Training 19 (AWS Services Used in Class)](/training-notes-site/walkthroughs/training-19-aws-services-reference/).

**How to use this:** this is the *story* of what Evan built and *why each piece exists*. Read it once top to bottom. When you need exact commands, jump to the Reference doc. Then do the self-check at the end without looking back.

---

## The one-paragraph version

Evan built the first half of a real batch pipeline. A **Python script** downloads Citi Bike's live station data. It runs inside **Lambda** (so no computer has to stay on), on a timer from **EventBridge Scheduler** (every 5 minutes), and saves each download untouched into the **Bronze** folder of an **S3** bucket. Every service only gets the permissions it needs through an **IAM role**. Then a **Spark job on EMR Serverless** reads all those raw JSON files, flattens them into one row per station per snapshot, cleans them, and writes **Silver** Parquet files. Most of the class time went to *permissions errors*, and that's normal: on the cloud, wiring services together securely is a big part of the job.

---

## You already know most of this

| You did this before | Class | Today's AWS version | What changes |
|---|---|---|---|
| A Python script that calls an API (`requests`) | Training 2 | The ingestion script | Same code, but it saves to S3 instead of your disk |
| `cron` running a script on a timer | Training 1 | **EventBridge Scheduler + Lambda** | No computer of yours has to be on |
| Bronze/Silver/Gold folders | Training 5, 8 | **S3 prefixes** in one bucket | Folders are just key prefixes; they appear when code writes a file |
| `spark-submit` a PySpark job | Training 7–9 | **EMR Serverless job run** | You upload the script to S3 and AWS runs Spark for you |
| `explode()` on nested JSON | Training 8–9 | The Bronze → Silver script | Same function, same reason |
| File permissions (`chmod`) | Training 1 | **IAM policies + roles** | Permissions are per *service* and per *resource*, written in JSON |
| Reading a log file | Training 1 | **CloudWatch Logs** | Every Lambda run writes its `print()` output here |

---

## The story: "Where are the bikes?"

Citi Bike publishes a live feed (GBFS) of every station: how many bikes and docks are free *right now*. The feed only shows the current moment. Yesterday's numbers are gone. If you want to analyze patterns (which stations run empty at 8 AM?), you have to **save a snapshot every few minutes yourself**. That's the whole pipeline's reason to exist.

Each step below is a problem, and the AWS service is the answer.

---

## Step 1: "Where do we keep the snapshots?" → S3 with a Bronze layout

Evan's bucket: `citi-bike-nyc-pipeline` (yours: `<your-name>-citibike-pipeline`). Every file the ingester saves goes to a key like:

```
bronze/citibike/station_status/year=2026/month=10/day=07/hour=18/station_status_20261007T182800Z.json
```

- **Bronze = exactly what the API sent**, untouched. If a later step has a bug, you can always reprocess from Bronze.
- **`year=/month=/day=/hour=`** is **Hive-style partitioning**. Spark, Glue and Athena understand it and can skip folders they don't need (that's *partition pruning*, Training 8).
- **Times are UTC.** 2:28 PM in New York is `hour=18`. Everyone in a pipeline agrees on UTC so nobody has to convert time zones.
- **You never click "Create folder."** S3 has no real folders. The "folder" appears the moment a file with that prefix is written.

**Correction to class:** Evan said Block Public Access had to be turned off for the bucket to work. It doesn't. Lambda and EMR reach the bucket through **IAM**, which works with Block Public Access **on**. Leave it on. "Public" means "anyone on the internet," which is never what a pipeline needs.

---

## Step 2: "How do we grab a snapshot?" → the ingestion script

`ingest_to_s3.py` (in `class-demos/training-19-evan-citibike/`) does four things:

1. Downloads `gbfs.json`, the **discovery** file that lists the URLs of the other feeds.
2. Downloads `station_information` (names, locations, capacity: changes rarely) and `station_status` (bikes/docks free: changes constantly).
3. Saves each one **as-is** to S3 with `boto3` `put_object`, using the Bronze key above.
4. Prints a short summary.

Evan ran it **locally first** (with his `company` CLI profile) before putting it anywhere else. That's the professional habit: **prove the code works on your machine before you add the cloud on top.** If it fails in Lambda, you then know the problem is the *cloud setup*, not the code.

---

## Step 3: "Who is allowed to write there?" → IAM role for the Lambda

This is where most of the class time went, so it's worth understanding properly.

A **role** is a set of permissions that a *service* (not a person) can put on, like a badge. It needs **two** policies:

| Policy | Question it answers | For the ingestion Lambda |
|---|---|---|
| **Trust policy** | *Who* may wear this badge? | `lambda.amazonaws.com` |
| **Permissions policy** | What can the wearer *do*? | `s3:PutObject` on `bucket/bronze/citibike/*` + write CloudWatch logs |

That's **least privilege**: the Lambda can add files to Bronze and nothing else. It can't read Silver or delete anything. If its code were ever hijacked, the damage stays tiny.

Two details that bite people:
- **Bucket ARN vs object ARN.** `arn:aws:s3:::my-bucket` is the bucket itself (needed for `ListBucket`). `arn:aws:s3:::my-bucket/*` is the files in it (needed for `GetObject`/`PutObject`). Get them mixed up and you get AccessDenied. (Evan hit exactly this again in Training 20.)
- **`iam:PassRole`.** To attach a role to a service, *you* need permission to "pass" it. That's why students got blocked creating Lambdas even though Lambda itself was allowed.

---

## Step 4: "Run it without my laptop" → Lambda

Lambda runs one function when it's triggered and bills only for the milliseconds it runs. Evan's changes to make the script Lambda-ready:

| Local script | Lambda version | Why |
|---|---|---|
| `if __name__ == "__main__": main()` | `def lambda_handler(event, context):` | Lambda calls this function by name (`lambda_function.lambda_handler`) |
| `boto3.Session(profile_name="company")` | `boto3.client("s3")` | Inside AWS, credentials come from the **role**. No keys, no profile |
| Bucket name typed in the code | `os.environ["BUCKET_NAME"]` | Configuration lives in **environment variables**, so the same code works for any bucket |
| Runs until done | Timeout raised from 3 s to ~1 min | The default 3-second timeout is too short for 3 downloads |

**What happened in class:**
- The first test failed with **`NoSuchBucket`**: the code still pointed at an older bucket name. Fixed with the environment variable.
- Evan worried about packaging `boto3`. **You don't need to**: `boto3` is built into the Python Lambda runtime. You only package libraries AWS doesn't include (like `requests`. The script uses `urllib` from the standard library to avoid even that).
- He deleted and recreated the function to change the code. You can just **paste the new code and click Deploy**.

---

## Step 5: "Did it work?" → CloudWatch Logs

Every Lambda run sends its `print()` output and errors to **CloudWatch Logs**, in the log group `/aws/lambda/<function-name>`. When a test fails, this is the first place to look. The error message (e.g. `NoSuchBucket`, `AccessDenied`) almost always names the exact problem.

---

## Step 6: "Do it every 5 minutes" → EventBridge Scheduler

A **schedule** says "call this target on this timetable." Evan's: `citi-bike-ingestion-5-min`, `rate(5 minutes)`, target = the Lambda.

The Scheduler is *another service* that needs its *own* role. This tripped Evan twice:

| Attempt | Error / symptom | Why | Fix |
|---|---|---|---|
| 1 | "Execution role must allow EventBridge Scheduler to assume the role" | He picked the **Lambda's** role, which trusts `lambda.amazonaws.com`, not the scheduler | New role `CitiBikeSchedulerRole` trusting `scheduler.amazonaws.com` |
| 2 | Schedule saved, but no new files arrived | The new role had a trust policy but **no permissions policy** | Inline policy allowing `lambda:InvokeFunction` on the function |
| 3 | Works | | Files appeared every 5 minutes (hour=20 showed up) |

Also: the **start time** had to be at least a few minutes in the future, and the schedule had an **end time**. The next day it had silently stopped because that end time had passed (Training 20). Pipelines that "just stop" are very often a schedule or a permission, not the code.

**The pattern to remember:** every arrow between two services is a permission. *Scheduler → Lambda* needs `lambda:InvokeFunction`. *Lambda → S3* needs `s3:PutObject`. When something doesn't happen, ask "which arrow is missing its permission?"

---

## Step 7: "Turn raw JSON into a clean table" → Spark on EMR Serverless

Now Bronze fills up with JSON files. Analysts can't use those directly: each file is **one big document** holding a list of ~2,500 stations. Silver needs **one row per station per snapshot**, with proper types.

**EMR Serverless** runs Spark without a cluster to manage. Two concepts:

| | What it is | Analogy |
|---|---|---|
| **Application** (`citibike-spark`) | A Spark environment that's ready to accept work. Created once | A kitchen that's set up |
| **Job run** | One execution of your script | Cooking one meal |

Evan created the application through **EMR Studio → Manage applications** (to avoid the SageMaker Unified Studio setup), x86_64, defaults, **Create** (not start: it starts itself when a job arrives). The job also needs an **execution role** (`CitiBikeEMRRole`, trusting `emr-serverless.amazonaws.com`) that can read Bronze and the script, and write Silver.

**What the Spark script does** (`bronze_to_silver.py`):

| Step | Code idea | Why |
|---|---|---|
| Read | `spark.read.option("multiLine", True).json("s3://.../bronze/.../station_status/")` | Each file is ONE JSON document spread over many lines, not one object per line |
| Explode | `explode(col("data.stations"))` | One row per file → one row per station |
| Snapshot time | `input_file_name()` + `regexp_extract` + `to_timestamp(..., "yyyyMMdd'T'HHmmss'Z'")` | The time lives in the file name, so pull it out |
| Join | left join `station_status` to `station_information` on `station_id` | Add station name/capacity to the live numbers |
| Derive | utilization, `is_empty`, `is_full`, `is_operational` | Answer business questions directly |
| Write | `.write.mode(...).parquet("s3://.../silver/...")` | Parquet is columnar + compressed; Spark writes many `part-*` files, one per partition |

**What happened in class:** the first job run failed with **`FIELD_NOT_FOUND: num_vehicles_available`**. The AI-generated script guessed field names from a newer GBFS version. The real feed (GBFS 1.1) uses `num_bikes_available`. Evan fixed it by **giving ChatGPT a real sample of the data**, re-uploading the script and resubmitting, and the job succeeded with Silver Parquet files.

**Lesson:** never let anyone (human or AI) write a transform against data they haven't seen. Show it a real record first.

**Data quirk:** some stations report `last_reported: 86400` (a placeholder time in 1970) and zero docks. They're installed but not in service. Silver keeps them flagged `is_operational = false` rather than deleting them, because "this station is broken" is itself useful information.

---

## The whole picture

```
                     every 5 min
EventBridge Scheduler ───────────▶ Lambda (ingestion)
  role: CitiBikeSchedulerRole        role: lambda role
  (lambda:InvokeFunction)            (s3:PutObject on bronze/*)
                                          │
                                          ▼
                         S3  bronze/citibike/<feed>/year=/month=/day=/hour=/*.json
                                          │
                                          ▼  (job run, started by hand)
                         EMR Serverless app "citibike-spark"
                           role: CitiBikeEMRRole (read bronze + scripts, write silver)
                                          │
                                          ▼
                         S3  silver/citibike/station_status/part-*.parquet
                                          │
                                          ▼  (Training 20–21)
                         Glue → Redshift Serverless (Gold, star schema)
```

---

## Corrections to class (things said that aren't quite right)

| Said in class | What's actually true |
|---|---|
| Turn off Block Public Access or the bucket can't be used | IAM access works with it **on**. Keep it on |
| Fargate has no cost when idle | Fargate bills for every second a task is running. It only costs nothing if you stop the task |
| boto3 has to be packaged with the Lambda | boto3 is included in the Python Lambda runtime |
| (Implied) delete and recreate the Lambda to change its code | Edit the code in the console and click **Deploy**, or `aws lambda update-function-code` |

---

## Pairs people mix up

| These two | The difference |
|---|---|
| Trust policy vs permissions policy | *Who* can use the role vs *what* the role can do. A role needs both |
| User vs role | A user is a person with a password/keys. A role is a badge a service (or person) wears temporarily |
| Bucket ARN vs object ARN | `arn:aws:s3:::bucket` (list it) vs `arn:aws:s3:::bucket/*` (read/write files) |
| EMR application vs job run | The ready kitchen vs one meal cooked in it |
| Bronze vs Silver | Raw and untouched vs cleaned, typed, one row per thing |
| Lambda role vs Scheduler role | The Lambda's role lets it write to S3. The Scheduler's role lets *it* invoke the Lambda |
| Schedule start/end time vs rate | When the schedule is active vs how often it fires while active |
| Local profile vs role credentials | On your laptop: keys under a profile. Inside AWS: the role provides credentials automatically |

---

## Self-check

Answer out loud before opening each one.

<details><summary>1. Why does this pipeline need to exist at all? Why not just query Citi Bike's API when you need data?</summary>

The feed only shows the current moment. History is lost unless you save snapshots yourself, so the pipeline's first job is capturing a snapshot every 5 minutes.
</details>

<details><summary>2. Why is the Bronze data saved exactly as the API sent it?</summary>

So you can always reprocess. If the Silver logic has a bug (like `num_vehicles_available`), you fix the script and rerun it on the untouched Bronze files.
</details>

<details><summary>3. A file saved at 3:10 PM New York time (EDT) lands in which hour folder?</summary>

`hour=19`. EDT is UTC−4, and the keys use UTC.
</details>

<details><summary>4. The Lambda works when you click Test, but no files arrive on schedule. Name two likely causes.</summary>

The Scheduler's role is missing `lambda:InvokeFunction` (or trusts the wrong service), or the schedule's start time hasn't arrived / end time has passed.
</details>

<details><summary>5. Why can't the Scheduler just use the Lambda's role?</summary>

That role's trust policy only lets `lambda.amazonaws.com` assume it. The Scheduler is a different service and needs a role that trusts `scheduler.amazonaws.com`.
</details>

<details><summary>6. Why does the Spark read need `multiLine`?</summary>

Each Bronze file is one JSON document spread across many lines. Spark's default expects one JSON object per line (JSON Lines).
</details>

<details><summary>7. What does `explode` do here?</summary>

Turns one row per file (holding a list of ~2,500 stations) into one row per station.
</details>

<details><summary>8. What's the difference between an EMR Serverless application and a job run?</summary>

The application is the reusable Spark environment, created once. A job run is one execution of a script on it.
</details>

<details><summary>9. Inside Lambda, where do the AWS credentials come from?</summary>

From the function's IAM role. No access keys or profiles in the code.
</details>

<details><summary>10. Why keep stations with `last_reported: 86400` in Silver?</summary>

They're real stations that aren't in service. Flagging them `is_operational = false` keeps that information; deleting them would hide it.
</details>

---

## If an interviewer says "walk me through a pipeline you built on AWS"

"I built an incremental batch pipeline for NYC Citi Bike station data. A Python Lambda, triggered every five minutes by EventBridge Scheduler, pulls the public GBFS feed and lands the raw JSON in an S3 Bronze layer, partitioned by year, month, day and hour in UTC. Each service has its own least-privilege IAM role: the Lambda can only put objects under the Bronze prefix, and the scheduler can only invoke that one function. A PySpark job on EMR Serverless then reads the raw files, explodes the nested station array into one row per station per snapshot, joins in station metadata, derives utilization and status flags, and writes Parquet to a Silver layer. The next stage loads it into Redshift Serverless as a star schema. The hardest parts were IAM: trust versus permission policies, PassRole, and bucket versus object ARNs. I also learned to validate a transform against a real data sample, because our first run failed on a field name that didn't exist in that version of the feed."
