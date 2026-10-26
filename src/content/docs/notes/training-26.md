---
title: "Training 26 - Kinesis Streaming Ingestion"
description: "A Lambda producer streaming into Kinesis, an IAM service-linked role error, and shutting down EventBridge schedules and compute for the weekend."
sidebar:
  order: 26
---

Teacher: Evan Flint

Syllabus Day 27 (per file numbering; Fri Oct 16). Source: the class chat. Topics in chat: a **Kinesis streaming ingestion Lambda**, an **IAM service-linked role** error, and Evan's **weekend shutdown** of EventBridge schedules and compute.

---

# Streaming Ingestion: Lambda → Kinesis

Q. What does Evan's streaming Lambda do?

A. (From class chat) A Lambda that downloads Citi Bike's GBFS `station_status.json` and publishes one Kinesis record per station to the stream `citibike-station-stream` (us-east-2), using `put_records` in batches with retries.

Expanded: This is the **streaming** version of the Training 19 ingestion. The batch Lambda saved the *whole feed* as one JSON file in S3 Bronze. This one splits the feed into **one small event per station** and pushes those events into a **Kinesis Data Stream**. Downstream consumers read them continuously: Firehose to S3, Flink, or another Lambda (see Training 22).

| | Batch Lambda (Training 19) | Streaming Lambda (today) |
|---|---|---|
| Output | One JSON file per feed per run | One record per station per run |
| Destination | S3 Bronze (`put_object`) | Kinesis Data Stream (`put_records`) |
| Feeds | Discovery + 3 feeds | `station_status` only |
| Consumers | Glue/Spark batch jobs | Real-time consumers (Firehose, Flink, Lambda) |

---

## How the code works

```python
STREAM_NAME = "citibike-station-stream"
STATION_STATUS_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
kinesis = boto3.client("kinesis", region_name="us-east-2")   # created once, reused on warm starts

def lambda_handler(event, context):
    # 1. Download the feed (User-Agent header, 15 s timeout)
    # 2. For each station, build a small record:
    #    station_id, num_bikes_available, num_docks_available, last_reported, ingested_at (UTC)
    #    -> {"Data": json bytes, "PartitionKey": station_id}
    # 3. Send in chunks of 500, retrying only the records that failed
    for start in range(0, len(records), 500):
        pending = records[start:start + 500]
        for attempt in range(5):
            result = kinesis.put_records(StreamName=STREAM_NAME, Records=pending)
            failed = [orig for orig, resp in zip(pending, result["Records"]) if "ErrorCode" in resp]
            published += len(pending) - len(failed)
            pending = failed
            if not pending:
                break
            time.sleep(min(2 ** attempt, 8))      # 1, 2, 4, 8, 8 seconds
        if pending:
            raise RuntimeError(f"Failed to publish {len(pending)} records")
    return {"statusCode": 200, "stations_received": len(stations), "records_published": published}
```

| Piece | Why it's there |
|---|---|
| `PartitionKey = station_id` | Kinesis hashes the key to pick a **shard**. All updates for one station go to the same shard, so they stay **in order** |
| Chunks of **500** | `put_records` accepts at most 500 records per call (≈2,500 stations → 6 calls). The other per-call limits: **5 MB per request** and **1 MB per record** by default |
| Check each `ErrorCode` | `put_records` can **partially fail**: the call succeeds but some records are rejected (usually throttling). It doesn't raise an error, so you must check |
| Retry only `failed` | Re-sending the whole batch would **duplicate** the records that already succeeded |
| `min(2 ** attempt, 8)` | **Exponential backoff** with a cap, to give a throttled shard time to recover |
| `raise` after 5 tries | Fail loudly so Lambda marks the run as an error (visible in CloudWatch), instead of silently losing data |
| `ingested_at` | When *we* received it, separate from `last_reported` (when the station reported). Useful for latency checks and late data |

The Lambda's role needs `kinesis:PutRecords` on the stream, plus CloudWatch Logs.

---

# IAM: Service-Linked Roles

Q. What is a service-linked role?

A. (From class chat) Evan suggested `AWSServiceRoleForAmazonEventBridgeApiDestinations` for my EventBridge schedule. Trying to create it failed: "not authorized to perform: iam:CreateServiceLinkedRole on resource: arn:aws:iam::<account-id>:role/aws-service-role/apidestinations.events.amazonaws.com/AWSServiceRoleForAmazonEventBridgeApiDestinations because no identity-based policy allows the iam:CreateServiceLinkedRole action."

Expanded: A **service-linked role** is a special role that **AWS owns** on behalf of one service. It lives under the path `/aws-service-role/`. Its trust policy and permissions are fixed and can't be edited, and creating it needs its own permission, `iam:CreateServiceLinkedRole`, which the student policy doesn't include. This one belongs to **EventBridge API Destinations** (sending events to outside HTTP endpoints). It only trusts `apidestinations.events.amazonaws.com` and only reads Secrets Manager. So even if it existed, **EventBridge Scheduler couldn't use it to invoke a Lambda**.

| | Normal (customer-managed) role | Service-linked role |
|---|---|---|
| Who owns it | You | AWS, for one specific service |
| Name / path | Anything you choose | `AWSServiceRoleFor…`, path `/aws-service-role/…` |
| Trust and permissions | You write and edit them | Fixed by AWS, can't edit |
| Permission to create | `iam:CreateRole` | `iam:CreateServiceLinkedRole` |
| Usable by EventBridge **Scheduler** to call Lambda? | Yes, if it trusts `scheduler.amazonaws.com` and allows `lambda:InvokeFunction` | No (wrong service, wrong permissions) |

**Still needed for the scheduler:** a normal role trusting `scheduler.amazonaws.com` with `lambda:InvokeFunction` on `<your-name>-citibike-ingestion` (and `states:StartExecution` for the Training 24 Step Functions schedule). Either Evan creates it, or I get `iam:CreateRole` back.

---

# Weekend Shutdown (Evan's environment)

Q. How do you safely pause a cloud pipeline for the weekend?

A. (From class chat) Evan's AI-assisted shutdown: **disable** the ingestion and orchestration schedules (don't delete them), confirm no Step Functions executions are running, check classic EventBridge rules, then check and stop compute (EC2 dashboard, Glue, Redshift Serverless). "Disabling schedules does not stop compute already running."

Expanded: Schedules are what *start* work, and compute is what *costs* money while running. A safe shutdown handles both, and keeps everything easy to turn back on Monday.

**Schedules Evan disabled:**

| Schedule | Target |
|---|---|
| `Citi-bike-ingestion-5-min` | Evan's ingestion Lambda |
| `citibike-incremental-every-30-min` | The Step Functions pipeline (Training 24) |
| `<student>-citibike-every-5-min` | A student's ingestion Lambda |

A student's `…-dashboard-nightly-stop` schedule stayed enabled because it *stops* compute.

---

Q. Why not just run `aws scheduler update-schedule --state DISABLED`?

A. (From class chat) The first attempt failed because "you used the Lambda function ARN as the schedule name, and the example command contained placeholder values for the target and IAM role." Updating a schedule "requires preserving its existing configuration."

Expanded: `update-schedule` **replaces the whole schedule**, not just the field you change. Leave out the target or role and the call fails, or overwrites them. The safe pattern is **read → copy → change one field → write**:

```python
session = boto3.Session(profile_name="company", region_name="us-east-2")
# Safety check: refuse to run against the wrong AWS account
if session.client("sts").get_caller_identity()["Account"] != "<account-id>":
    raise RuntimeError("Wrong AWS account")

scheduler = session.client("scheduler")
fields = ["Name", "GroupName", "ScheduleExpression", "ScheduleExpressionTimezone", "StartDate",
          "EndDate", "Description", "KmsKeyArn", "FlexibleTimeWindow", "Target", "ActionAfterCompletion"]

for name in names:
    schedule = scheduler.get_schedule(Name=name, GroupName="default")
    if schedule["State"] == "DISABLED":
        continue                                   # don't touch what was already off
    request = {f: schedule[f] for f in fields if f in schedule}
    request["State"] = "DISABLED"                  # the only change
    scheduler.update_schedule(**request)
# then get_schedule again for each name to verify
```

| Good practice in this script | Why |
|---|---|
| Account-ID check via `sts get-caller-identity` | Prevents running against the wrong account or profile |
| Schedule **name**, not the target ARN | The API identifies schedules by name + group |
| Copy existing fields | Keeps the expression, target and role intact |
| Skip already-disabled schedules | On Monday, re-enable only what *was* on |
| Verify afterwards | Prove the state actually changed |

**Monday restart:** same script with `State = "ENABLED"`, run only on the schedules recorded as enabled before Friday.

---

**The rest of Evan's checklist:**

| Check | Command | Why |
|---|---|---|
| Step Functions idle? | `aws stepfunctions list-executions --state-machine-arn … --status-filter RUNNING` | Empty output = nothing running |
| Classic EventBridge rules | `aws events list-rules` → `list-targets-by-rule --rule <name>` | One rule ran daily on `cron(30 11 * * ? *)`. Check what it launches before disabling (`aws events disable-rule`) |
| AWS-managed rules | e.g. `AutoScalingManagedRule` | Leave alone |
| All schedules off? | `aws scheduler list-schedules --query 'Schedules[].[Name,State,Target.Arn]' --output table` | Final check |
| Dashboard EC2 | `aws ec2 describe-instances --instance-ids …` → `aws ec2 stop-instances` | **Stop**, not terminate, so it's back Monday |
| Glue jobs | `aws glue list-jobs` | Confirm nothing is running |
| Redshift Serverless | `aws redshift-serverless list-workgroups` | Check status and base capacity |
| Anything else | Other EC2, ECS tasks, EMR Serverless apps | Schedules don't stop compute that's already running |

**Takeaways:**
- **Disable, don't delete.** Monday is one command instead of a rebuild.
- **Schedules and compute are separate.** Turning off the trigger doesn't stop what's already running.
- **Check what a rule launches before disabling it.**
- These commands were for **Evan's account-wide shutdown**. Students shouldn't run them, because they change Evan's and other students' schedules. For my own resources: disable *my* schedules only, and stop *my* EC2 if I have one.

---

# Apache Airflow (roadmap topic for this day)

Not demoed in class (the Training 23 orchestration intro mentioned it). The orchestration tool table is in Training 23; cron syntax is in Training 1 and Training 23.

Q. What is Apache Airflow, and what are its parts?

A. (Not covered in class.) An open-source orchestrator where workflows are Python **DAGs** (directed acyclic graphs of tasks). It schedules them, runs tasks in dependency order, retries failures and shows every run in a web UI.

Expanded:

| Component | Job |
|---|---|
| Scheduler | Parses DAG files, decides which task instances are due, hands them to the executor |
| Executor | How tasks run: `LocalExecutor` (one machine), `CeleryExecutor` (worker pool + queue), `KubernetesExecutor` (one pod per task) |
| Workers | Run the task code |
| Metadata database (Postgres/MySQL) | State of every DAG run and task instance, XComs, connections |
| Webserver / API server | UI: graph view, logs, retries, manual triggers |

**Interview line:** "Airflow's scheduler reads Python DAG files, works out which tasks are due, and the executor runs them on workers; all state lives in a metadata database, and the web UI shows it."

---

Q. What do a DAG, operators and TaskFlow look like?

A. (Not covered in class.) A DAG holds the schedule and settings; **operators** are task templates; `>>` sets dependencies. TaskFlow (`@task`) turns plain Python functions into tasks.

Expanded: the Citi Bike pipeline as an Airflow DAG (Airflow 2.x syntax, Amazon provider package):

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator

with DAG(
    dag_id="citibike_incremental",
    schedule="*/30 * * * *",                 # cron, same as EventBridge
    start_date=datetime(2026, 10, 1),
    catchup=False,                           # don't run every missed interval since start_date
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
) as dag:
    wait_for_bronze = S3KeySensor(
        task_id="wait_for_bronze",
        bucket_key="s3://<bucket>/bronze/citibike/station_status/*",
        wildcard_match=True,
        mode="reschedule",                   # free the worker slot between checks
    )
    bronze_to_silver = GlueJobOperator(task_id="bronze_to_silver",
        job_name="CitiBikeBronzeToSilverIncrementalV2",
        script_args={"--BATCH_ID": "{{ run_id }}"})          # templated: unique per run
    complete_batch = RedshiftDataOperator(task_id="complete_batch",
        workgroup_name="<workgroup>", database="dev",
        sql="CALL public.sp_complete_citibike_batch('{{ run_id }}', '{{ data_interval_end }}');")

    wait_for_bronze >> bronze_to_silver >> complete_batch
```

| Term | Meaning |
|---|---|
| Operator | A task template: `PythonOperator`, `BashOperator`, provider operators like `GlueJobOperator` |
| Sensor | An operator that waits for something (a file, a partition, another DAG) |
| TaskFlow `@task` | Decorate a Python function to make it a task; return values pass via XCom automatically |
| Task instance | One task in one DAG run |

---

Q. What are sensors, XCom and retries?

A. (Not covered in class.)

Expanded:

| Feature | What to know |
|---|---|
| **Sensor `poke` mode** | Holds a worker slot the whole time it waits. Fine for short waits |
| **Sensor `reschedule` mode** | Releases the slot between checks. Use it for long waits (or deferrable operators) |
| **XCom** | Passes **small** values between tasks (an S3 path, a row count, a batch ID), stored in the metadata DB. Never pass DataFrames or files: write them to S3 and pass the path |
| **Retries** | `retries`, `retry_delay`, `retry_exponential_backoff` per task or in `default_args` |
| **SLAs / timeouts** | `execution_timeout` kills a stuck task; SLA misses / deadline alerts notify when a run is late |

**Interview line (XCom):** "XCom is for metadata, not data: I pass an S3 path or a count between tasks, never the dataset itself."

---

Q. What are catchup, backfill and the data interval?

A. (Not covered in class.) Every scheduled run covers a **data interval**. The `logical_date` (formerly `execution_date`) is the *start* of that interval, and the run starts after the interval ends.

Expanded:
- A daily DAG's run for Oct 20 (interval Oct 20 00:00 → Oct 21 00:00) actually starts just after midnight on Oct 21.
- **`catchup=True`** (the default in Airflow 2): when a DAG is turned on, Airflow creates a run for every interval since `start_date` that hasn't run. `catchup=False` runs only the latest.
- **Backfill** re-runs a chosen date range on purpose: `airflow dags backfill -s 2026-10-01 -e 2026-10-07 citibike_incremental`.
- Backfill only works safely if tasks are **idempotent** and use `{{ data_interval_start }}` / `{{ data_interval_end }}` instead of "now". That's the same `[start, end)` window as Training 24.

**Interview line (idempotent tasks):** "Each task processes exactly its data interval, writes with overwrite-partition or MERGE, and never uses the current time, so a retry or a backfill gives the same result."

---

Q. What is MWAA, and Airflow vs Step Functions?

A. (Not covered in class.) **Amazon MWAA** (Managed Workflows for Apache Airflow) is AWS-hosted Airflow: you upload DAGs and `requirements.txt` to S3, and AWS runs the scheduler, workers and database.

Expanded:

| | Airflow / MWAA | AWS Step Functions |
|---|---|---|
| Workflow definition | Python DAGs | JSON state machines (Amazon States Language) |
| Infrastructure | Always-on environment (MWAA bills per hour, even idle) | Serverless; pay per state transition |
| Scheduling, catchup, backfill | Built in | Needs EventBridge Scheduler; no backfill concept |
| Integrations | Thousands of operators, any cloud or on-prem | Deep AWS integrations (`.sync`, 200+ services) |
| Portability | Cloud-neutral | AWS only |
| Best for | Many interdependent batch pipelines, multi-cloud, date-based backfills | AWS-native, event-driven or low-volume workflows |

**Interview line:** "If everything is on AWS and the workflow is event-driven, Step Functions is cheaper and has nothing to run. If I have many date-partitioned batch pipelines, need backfills or span clouds, I'd pick Airflow, on AWS as MWAA."
