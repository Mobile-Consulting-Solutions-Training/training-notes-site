---
title: Day 19 Vocabulary
description: Glossary of terms and definitions from the Training 19 study guide.
sidebar:
  order: 19
---

Vocabulary — Study Guide Day 19

## Pipeline Concepts
- **Batch pipeline** — Processes data in chunks on a schedule or when files arrive, rather than event by event.
- **Streaming pipeline** — Processes each event as it happens (Kafka, Kinesis).
- **Bronze layer** — Raw data stored exactly as received, so it can always be reprocessed.
- **Silver layer** — Cleaned, typed data, here one row per station per snapshot in Parquet.
- **Hive-style partitioning** — Folder keys like `year=2026/month=10/day=07/hour=18` that engines use to skip irrelevant data.
- **Partition pruning** — Reading only the partitions a query needs.
- **UTC** — Coordinated Universal Time; the single time zone used across the pipeline.

## Citi Bike Data
- **GBFS (General Bikeshare Feed Specification)** — Open standard for publishing live bike-share data; the class feed uses version 1.1.
- **gbfs.json** — Discovery file listing the URLs of the other feeds.
- **station_information** — Feed of slow-changing station details: name, location, capacity.
- **station_status** — Feed of live counts: bikes, e-bikes and docks available.
- **num_bikes_available** — GBFS 1.1 field for available bikes (`num_vehicles_available` is a newer-version field).
- **last_reported: 86400** — Placeholder timestamp marking a station that isn't in service.

## AWS Services
- **S3** — Object storage; folders are just key prefixes.
- **Block Public Access** — S3 setting preventing public internet access; services still work through IAM.
- **Lambda** — Runs one function on a trigger, billed per millisecond of run time.
- **Handler** — The function Lambda calls, e.g. `lambda_function.lambda_handler(event, context)`.
- **Environment variable** — Configuration value set on the function, e.g. `BUCKET_NAME`.
- **CloudWatch Logs** — Where Lambda's print output and errors go, in log group `/aws/lambda/<function>`.
- **EventBridge Scheduler** — Runs a target (like a Lambda) on a schedule such as `rate(5 minutes)`, between a start and end time.
- **EMR Serverless** — Runs Spark or Hive without managing a cluster.
- **EMR Serverless application** — A reusable Spark environment, created once.
- **Job run** — One execution of a script on an EMR Serverless application.
- **EMR Studio** — Console area used to create EMR Serverless applications.
- **Redshift Serverless** — AWS's serverless data warehouse.
- **ECS (Elastic Container Service)** — AWS service that runs and manages Docker containers.
- **Fargate** — Serverless compute for ECS containers; bills while tasks run.
- **Streamlit** — Python library that turns a script into a web app.
- **QuickSight** — AWS's BI (business intelligence) dashboard tool.
- **boto3** — The AWS SDK for Python; included in the Lambda Python runtime.

## IAM
- **IAM role** — A set of permissions a service (or person) assumes temporarily.
- **Trust policy** — The part of a role saying who may assume it.
- **Permissions policy** — The part of a role saying what it may do.
- **Least privilege** — Granting only the permissions a job needs.
- **ARN (Amazon Resource Name)** — Unique identifier of an AWS resource.
- **Bucket ARN vs object ARN** — `arn:aws:s3:::bucket` for bucket-level actions vs `arn:aws:s3:::bucket/*` for objects.
- **iam:PassRole** — Permission to attach a role to a service.
- **Execution role** — The role a service like EMR Serverless or Glue uses when running your job.

## Spark Transform
- **multiLine** — Spark JSON option for files where one JSON document spans many lines.
- **explode** — Spark function turning an array into one row per element.
- **input_file_name** — Spark function returning the source file path of each row.
- **regexp_extract** — Spark function pulling a pattern out of a string.
- **to_timestamp** — Spark function converting a string to a timestamp using a format.
- **Parquet** — Columnar, compressed file format; Spark writes one `part-*` file per partition.
- **is_operational** — Derived flag marking whether a station is actually in service.
