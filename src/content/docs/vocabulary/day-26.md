---
title: Day 26 Vocabulary
description: Glossary of terms and definitions from the Training 26 notes.
sidebar:
  order: 26
---

Vocabulary — Study Guide Day 26

Source: notes/Training 26.md

## Streaming Ingestion
- **Streaming ingestion** — Pushing small per-event records into a stream continuously instead of saving whole files in batches.
- **Kinesis Data Stream** — AWS's managed stream that holds records for real-time consumers.
- **GBFS (General Bikeshare Feed Specification)** — The public feed format Citi Bike publishes, e.g. `station_status.json`.
- **station_status** — The GBFS feed with each station's available bikes and docks.
- **Lambda** — AWS serverless function; here it downloads the feed and publishes records to Kinesis.
- **lambda_handler** — The entry-point function Lambda calls on each invocation.
- **Warm start** — A Lambda invocation that reuses an already-initialized environment, so clients created outside the handler are reused.
- **put_records** — Kinesis API call that sends up to 500 records per call.
- **put_object** — S3 API call that writes one object, used by the batch Lambda.
- **Partial failure** — When `put_records` succeeds overall but rejects some records, flagged by `ErrorCode` in each response.
- **ErrorCode** — The field in a `put_records` result entry marking that record as failed.
- **Throttling** — A service rejecting requests because a limit, such as shard write capacity, was exceeded.
- **PartitionKey** — A value Kinesis hashes to choose a shard; using `station_id` keeps one station's records in order.
- **Shard** — A Kinesis unit of capacity and ordering, similar to a Kafka partition.
- **Exponential backoff** — Waiting progressively longer between retries (1, 2, 4, 8 s, capped) so a throttled resource can recover.
- **Retry only failed records** — Re-sending just the rejected records so successful ones aren't duplicated.
- **Fail loudly** — Raising an error after retries run out so the failure shows in CloudWatch instead of data being silently lost.
- **ingested_at** — The timestamp of when the pipeline received a record, separate from when the source reported it.
- **last_reported** — The timestamp of when the station itself reported its status.
- **Firehose** — Managed Kinesis consumer that delivers stream records to destinations like S3.
- **Flink** — A stream-processing engine that can consume Kinesis records in real time.
- **kinesis:PutRecords** — IAM action allowing a role to write batches of records to a stream.
- **CloudWatch Logs** — AWS logging service where Lambda writes its output and errors.

## IAM Roles
- **Service-linked role** — A special AWS-owned role for one specific service, under `/aws-service-role/`, with fixed trust and permissions you can't edit.
- **Customer-managed role** — A normal IAM role you create and whose trust and permissions you write.
- **iam:CreateServiceLinkedRole** — The separate permission required to create a service-linked role.
- **iam:CreateRole** — The permission required to create a normal role.
- **Trust policy** — The part of a role defining which principal or service may assume it, e.g. `scheduler.amazonaws.com`.
- **Identity-based policy** — A permission policy attached to a user, group or role.
- **EventBridge API Destinations** — EventBridge feature that sends events to outside HTTP endpoints; its service-linked role can't invoke Lambda.
- **Secrets Manager** — AWS service for storing secrets such as API credentials.
- **lambda:InvokeFunction** — IAM action allowing a caller to run a Lambda function.
- **states:StartExecution** — IAM action allowing a caller to start a Step Functions execution.

## Weekend Shutdown
- **EventBridge Scheduler** — AWS service that starts targets like Lambda or Step Functions on a schedule.
- **Classic EventBridge rule** — An older-style EventBridge rule that can run targets on a cron schedule or event pattern.
- **Disable vs delete** — Disabling turns a schedule off but keeps its configuration for an easy restart; deleting removes it.
- **Schedules vs compute** — Schedules start work, compute costs money while running; disabling a schedule doesn't stop compute already running.
- **update-schedule** — Scheduler API that replaces the whole schedule, so you must read, copy, change one field and write back.
- **get_schedule** — Scheduler API that returns a schedule's current configuration.
- **list-schedules** — Scheduler CLI command that lists schedules and their states.
- **Schedule group** — The grouping that, with the name, identifies a schedule (e.g. `default`).
- **State (ENABLED / DISABLED)** — A schedule's on/off setting.
- **Flexible time window** — A scheduler setting allowing the target to run within a window around the scheduled time.
- **sts get-caller-identity** — Returns which AWS account and identity the current credentials belong to, used as a safety check.
- **boto3.Session** — A boto3 object holding a profile and region from which service clients are created.
- **list-executions** — Step Functions CLI command; with `--status-filter RUNNING` it shows whether anything is running.
- **list-rules / list-targets-by-rule** — EventBridge commands that list rules and what each rule launches.
- **disable-rule** — EventBridge command that turns off a classic rule.
- **cron(30 11 \* \* ? \*)** — EventBridge's six-field cron syntax, here daily at 11:30 UTC.
- **AWS-managed rule** — A rule AWS creates for its own services (e.g. `AutoScalingManagedRule`); leave it alone.
- **stop-instances** — EC2 command that stops an instance but keeps its disk, unlike terminate.
- **Terminate** — Permanently deleting an EC2 instance.
- **Redshift Serverless workgroup** — The compute resource of Redshift Serverless, checked for status and base capacity.
- **Base capacity** — The baseline compute setting of a Redshift Serverless workgroup.
- **ECS task** — A running container in Amazon Elastic Container Service.
- **EMR Serverless application** — A serverless Spark environment that can keep running and billing independently of schedules.
- **list-jobs** — Glue CLI command listing jobs to confirm nothing is running.
