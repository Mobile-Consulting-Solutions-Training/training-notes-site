---
title: Study Guide - Day 19
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 19: AWS Batch Pipelines"
sidebar:
  order: 190
---

Study Guide - Day 19 (source: notes/Training 19.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Batch Pipeline on AWS.** Evan's reference shape: ingest into S3 → process with a Spark job on EMR Serverless → output to a data warehouse on Redshift Serverless → visualize with a Streamlit app hosted on ECS/Fargate. Batch = process data in chunks on a schedule or when files arrive (vs streaming, which processes each event as it happens). Every step is serverless; only the always-on web app bills while idle.

**EMR Serverless.** Spark (or Hive) without managing a cluster. Two concepts: an **application** (a ready Spark environment, created once; Evan's was `citibike-spark`, created via EMR Studio → Manage applications, x86_64, defaults, Create not Start) and a **job run** (one execution of a script). Needs an **execution role** trusting `emr-serverless.amazonaws.com` that can read Bronze and the script and write Silver.

**Visualization Layer.** Streamlit = a Python library that turns a script into a web app (charts, tables, filters). Packaged as a Docker container and hosted on **ECS** (Elastic Container Service, AWS's container orchestrator) with **Fargate** (serverless compute for containers: no EC2 instances to manage). Alternative: a BI tool such as **QuickSight** (AWS), Tableau or Power BI connected directly to Redshift. Correction to class: Fargate **does** bill while a task is running; it's only free when stopped.

**Citi Bike GBFS Feed.** The class data source: NYC's public live bike-share feed in GBFS 1.1 format. `gbfs.json` (discovery: lists feed URLs), `station_information` (names, locations, capacity: rarely changes), `station_status` (bikes/docks available now: changes constantly). The feed only shows the current moment, so the pipeline's job is to save a snapshot every few minutes to build history. Field is `num_bikes_available` (not `num_vehicles_available`, which is a newer GBFS version). `last_reported: 86400` is a placeholder for stations not in service.

**Bronze Layout in S3.** One bucket, prefixes per layer. Bronze keys: `bronze/citibike/<feed>/year=/month=/day=/hour=/<feed>_<YYYYMMDDTHHMMSSZ>.json`. Raw, untouched copies (so you can always reprocess). Hive-style partitions enable partition pruning. Times in UTC (2:28 PM EDT = hour 18). Folders are just key prefixes; they appear when code writes an object. Block Public Access can stay ON (correction to class): services reach the bucket via IAM.

**IAM Roles for Services.** A role is a set of permissions a service assumes. It needs a **trust policy** (who may assume it: `lambda.amazonaws.com`, `scheduler.amazonaws.com`, `emr-serverless.amazonaws.com`) and a **permissions policy** (what it may do). Least privilege: the ingestion Lambda can only `s3:PutObject` under `bronze/citibike/*`. Bucket ARN (`arn:aws:s3:::bucket`, for ListBucket) vs object ARN (`arn:aws:s3:::bucket/*`, for Get/Put). `iam:PassRole` is needed to attach a role to a service.

**Lambda Ingestion.** The local script became `lambda_function.lambda_handler(event, context)`. Inside AWS, `boto3.client("s3")` gets credentials from the role (no profile, no keys). Bucket name in an environment variable (`BUCKET_NAME`). Timeout raised from the 3-second default. boto3 is included in the Python runtime (no packaging needed). First test failed with `NoSuchBucket` (old bucket name). Logs go to CloudWatch Logs group `/aws/lambda/<function>`.

**EventBridge Scheduler.** Runs a target on a timetable: `citi-bike-ingestion-5-min`, `rate(5 minutes)`, target = the Lambda, with a start and end time (start must be a few minutes ahead). Needs its **own** role (`CitiBikeSchedulerRole`) trusting `scheduler.amazonaws.com` with `lambda:InvokeFunction`. Evan's failures: (1) picked the Lambda's role, giving "Execution role must allow EventBridge Scheduler to assume the role"; (2) new role had no permissions policy, so no files arrived; (3) fixed with an inline InvokeFunction policy. Rule of thumb: every arrow between two services is a permission.

**Bronze → Silver Spark Job.** `bronze_to_silver.py`: read with `multiLine` (each file is one JSON document) → `explode(data.stations)` (one row per station) → snapshot time from the file name (`input_file_name` + `regexp_extract` + `to_timestamp("yyyyMMdd'T'HHmmss'Z'")`) → left join station_status to station_information on `station_id` → derive utilization, `is_empty`, `is_full`, `is_operational` → write Parquet (`part-*` files) to Silver. First run failed with `FIELD_NOT_FOUND: num_vehicles_available`; fixed by giving ChatGPT a real data sample. Lesson: validate transforms against real data.

---

# Part 2: Cheat Sheet

## Batch Pipeline Shape
- S3 (ingest) → EMR Serverless (Spark) → Redshift Serverless (warehouse) → Streamlit on ECS/Fargate (visualize)
- Batch = chunks on a schedule; streaming = each event as it arrives

## EMR Serverless
- **Application** = ready Spark environment (create once) · **Job run** = one execution
- Execution role trusts `emr-serverless.amazonaws.com`
- Created via EMR Studio → Manage applications (avoids SageMaker Unified Studio setup)

## Visualization
- **Streamlit** = Python → web app · **Docker** container · **ECS** = container orchestration · **Fargate** = serverless container compute (bills while running)
- BI tools: **QuickSight**, Tableau, Power BI

## Citi Bike GBFS 1.1
- `gbfs.json` (discovery) · `station_information` (static) · `station_status` (live)
- `num_bikes_available` ✔ · `num_vehicles_available` ✘ (newer GBFS)
- `last_reported: 86400` = not in service → keep, flag `is_operational = false`

## Bronze Keys
- `bronze/citibike/<feed>/year=/month=/day=/hour=/<feed>_<UTC timestamp>.json`
- UTC · Hive partitions · prefixes not folders · Block Public Access stays on

## IAM Roles
- Trust policy = **who** · permissions policy = **what**
- Bucket ARN (ListBucket) vs object ARN `/*` (Get/Put/Delete)
- `iam:PassRole` to attach a role to a service

## Lambda
- Handler `lambda_function.lambda_handler` · role credentials · env var `BUCKET_NAME` · raise timeout · boto3 built in
- Edit code + **Deploy** (no need to recreate)
- Logs: CloudWatch `/aws/lambda/<name>`

## EventBridge Scheduler
- `rate(5 minutes)` · start/end time · own role trusting `scheduler.amazonaws.com` + `lambda:InvokeFunction`

## Spark Bronze → Silver
- `multiLine` → `explode` → `input_file_name`/`regexp_extract`/`to_timestamp` → join on `station_id` → derived flags → Parquet

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: Describe Evan's batch pipeline on AWS from start to finish.
A: Raw data lands in S3, a Spark job on EMR Serverless cleans and transforms it, the results are loaded into Redshift Serverless as a warehouse, and a Streamlit app running in a container on ECS with Fargate shows dashboards.

Q: Why does the Citi Bike pipeline need to exist at all?
A: The GBFS feed only shows the current moment. If you want history, like which stations run empty at rush hour, you have to save a snapshot every few minutes yourself.

Q: What are the three GBFS feeds we used and how are they different?
A: gbfs.json is the discovery file listing the other feeds' URLs, station_information has slow-changing details like name and capacity, and station_status has the live counts of bikes and docks available.

Q: Why is Bronze data stored exactly as the API returned it?
A: So you can always reprocess. If the Silver logic has a bug, you fix the script and rerun it on the untouched raw files.

Q: Why are the Bronze hour folders in UTC?
A: So everyone in the pipeline agrees on one time zone. A file saved at 2:28 PM New York time lands in hour 18.

Q: What's the difference between a trust policy and a permissions policy?
A: The trust policy says who is allowed to assume the role, like the Lambda service. The permissions policy says what the role can do once assumed, like PutObject on the Bronze prefix.

Q: Why can't the EventBridge Scheduler just use the Lambda's role?
A: That role only trusts lambda.amazonaws.com. The scheduler is a different service, so it needs its own role that trusts scheduler.amazonaws.com and allows lambda:InvokeFunction.

Q: The Lambda test works but nothing arrives on schedule. What do you check?
A: That the scheduler role has lambda:InvokeFunction and trusts the scheduler service, and that the schedule's start time has arrived and end time hasn't passed.

Q: Inside a Lambda, where do the AWS credentials come from?
A: From the function's IAM role. You just call boto3.client("s3") with no profile or keys.

Q: What's the difference between an EMR Serverless application and a job run?
A: The application is the reusable Spark environment you create once. A job run is a single execution of your script on it.

Q: Why does the Spark read need the multiLine option?
A: Each Bronze file is one JSON document spread over many lines, and Spark's default expects one JSON object per line.

Q: What does explode do in the Bronze to Silver job?
A: It turns one row per file, which holds a list of about 2,500 stations, into one row per station.

Q: Why did the first EMR job run fail, and what's the lesson?
A: The script referenced num_vehicles_available, a field from a newer GBFS version. The real feed uses num_bikes_available. The lesson is to always validate a transform against a real data sample.

Q: Does Fargate cost nothing when idle?
A: No. Fargate bills for every second a task runs. It only costs nothing if you stop the task, which a website usually can't do.

Q: Does Block Public Access need to be turned off for Lambda or EMR to use the bucket?
A: No. Those services reach the bucket through IAM, which works with Block Public Access on. Leave it on.
