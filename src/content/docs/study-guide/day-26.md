---
title: Study Guide - Day 26
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 26: Streaming Ingestion with Lambda and Kinesis"
sidebar:
  order: 260
---

Study Guide - Day 26 (source: notes/Training 26.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences. This class's notes came from the class chat only, so this guide is short.

# Part 1: Quick Summary

**Streaming Ingestion Lambda.** The streaming version of the Training 19 ingestion: download `station_status.json` and publish **one Kinesis record per station** to `citibike-station-stream`, instead of saving the whole feed as one S3 file. Consumers (Firehose, Flink, Lambda) read it continuously.

**How the Code Works.** Each record has `station_id`, `num_bikes_available`, `num_docks_available`, `last_reported` and `ingested_at` (when we received it). `PartitionKey = station_id` keeps one station's updates on one shard, in order. `put_records` accepts at most **500 records per call** (~2,500 stations → 6 calls). It can **partially fail** without raising, so check each record's `ErrorCode` and **retry only the failed ones** (resending all would duplicate). **Exponential backoff** with a cap (`min(2 ** attempt, 8)`: 1, 2, 4, 8, 8 s). After 5 tries, `raise` so the run is marked failed instead of silently losing data. The client is created once outside the handler and reused on warm starts. The role needs `kinesis:PutRecords` and CloudWatch Logs.

**Service-Linked Roles.** A special role **AWS owns** for one service, named `AWSServiceRoleFor…` under `/aws-service-role/`, with fixed trust and permissions you can't edit; creating one needs `iam:CreateServiceLinkedRole`. The EventBridge **API Destinations** one only trusts `apidestinations.events.amazonaws.com`, so EventBridge **Scheduler** can't use it to call Lambda. The scheduler needs a normal role trusting `scheduler.amazonaws.com` with `lambda:InvokeFunction` (and `states:StartExecution` for Step Functions).

**Weekend Shutdown.** Schedules *start* work; compute *costs* money. **Disable** schedules (don't delete), confirm no Step Functions executions are running, check classic EventBridge rules and what they launch, then stop compute (EC2 stop not terminate, Glue, Redshift Serverless, ECS, EMR Serverless). Disabling schedules doesn't stop compute already running. Leave schedules that *stop* compute enabled.

**Safely Disabling a Schedule.** `update-schedule` **replaces the whole schedule**, so passing only `--state DISABLED` fails or wipes the target and role. Pattern: **read → copy → change one field → write** (`get_schedule`, copy fields, set `State`, `update_schedule`), using the schedule **name** (not the target ARN). Good practices: check the account ID with `sts get-caller-identity` first, skip already-disabled schedules (so Monday re-enables only what was on), verify afterwards. Students should only touch their own resources.

---

# Part 2: Cheat Sheet

## Streaming Lambda
- One record per station · `PartitionKey = station_id` (shard + order)
- `put_records` max 500 · check `ErrorCode` · retry failed only · backoff 1-2-4-8-8 · raise after 5
- `ingested_at` vs `last_reported` · client outside handler · `kinesis:PutRecords`

## Roles
- Service-linked: AWS-owned, `/aws-service-role/`, fixed, needs `iam:CreateServiceLinkedRole`
- Scheduler role: trusts `scheduler.amazonaws.com` + `lambda:InvokeFunction` / `states:StartExecution`

## Shutdown
- Disable, don't delete · schedules ≠ compute · check rule targets first
- Stop EC2 (not terminate) · check Glue, Redshift Serverless, ECS, EMR Serverless
- `list-executions --status-filter RUNNING` · `list-schedules` final check

## update-schedule
- Replaces the whole schedule → read, copy, change State, write
- Name not ARN · account-ID check · skip already disabled · verify

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: How is the streaming ingestion Lambda different from the batch one?
A: The batch Lambda saved the whole feed as one JSON file in S3. The streaming one splits it into one record per station and publishes them to a Kinesis stream for real-time consumers.

Q: Why use the station ID as the partition key?
A: Kinesis hashes the key to choose a shard, so every update for one station lands on the same shard and stays in order.

Q: Why does the code send records in chunks of 500?
A: put_records accepts at most 500 records per call, so about 2,500 stations take six calls.

Q: What's a partial failure in put_records, and how do you handle it?
A: The call succeeds but some records are rejected, usually from throttling, without raising an error. You check each record's error code and retry only the failed ones, because resending everything would create duplicates.

Q: What is exponential backoff?
A: Waiting longer after each failed attempt, like 1, 2, 4 and then 8 seconds, so a throttled shard has time to recover.

Q: Why raise an error after five failed attempts?
A: So Lambda marks the run as failed and it shows up in CloudWatch, instead of silently losing data.

Q: What is a service-linked role?
A: A role that AWS owns for one specific service. Its trust and permissions are fixed and can't be edited, and creating one needs the iam:CreateServiceLinkedRole permission.

Q: Why couldn't the API Destinations service-linked role run the scheduler?
A: It only trusts the EventBridge API Destinations service and only reads Secrets Manager. EventBridge Scheduler needs a normal role that trusts scheduler.amazonaws.com and allows lambda:InvokeFunction.

Q: How do you safely pause a cloud pipeline for the weekend?
A: Disable the schedules rather than delete them, confirm nothing is still running, check what any other rules launch, then stop compute like EC2 instances. Disabling a schedule doesn't stop work that's already running.

Q: Why does aws scheduler update-schedule with only the state fail?
A: Update replaces the whole schedule. If you leave out the target and role, it fails or overwrites them. You read the schedule, copy its fields, change only the state, and write it back.

Q: Why skip schedules that were already disabled?
A: So when you re-enable on Monday, you only turn back on what was running before, not something that was off on purpose.

Q: Why check the account ID before running a shutdown script?
A: To make sure you're in the right AWS account and profile, so you don't change someone else's resources.
