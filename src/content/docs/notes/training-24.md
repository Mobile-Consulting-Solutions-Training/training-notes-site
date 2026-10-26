---
title: "Training 24 - Incremental Pipelines"
description: "An incremental Citi Bike pipeline: batch windows, landing table, MERGE, stored procedures and checkpoints, orchestrated with Step Functions under Terraform, plus a Streamlit dashboard on EC2."
sidebar:
  order: 24
---

Teacher: Evan Flint

Syllabus Day 25 (per file numbering; Wed Oct 14). Topics: making the Citi Bike pipeline **incremental** (batch IDs, landing table, MERGE, stored procedure, checkpoint), then bringing the existing Step Functions orchestration under **Terraform** and running it. More filled in as class goes.

Note: I joined about an hour late, so the class walkthrough below starts mid-demo. Evan's shared chat (further down) fills in part of the first hour.

---

# Key Concepts

Q. What is an incremental pipeline?

A. (From class) Evan's takeaway after a day and a half of retrofitting: "in the future, it would be best to design these things to be incremental from the get go."

Expanded: A **full refresh** pipeline reprocesses all the data every run. An **incremental** pipeline only processes what's new since the last successful run. Each run gets a **batch window** (a start and end timestamp) and a **batch ID**, so every row can be traced back to the run that loaded it. Incremental pipelines are cheaper and faster, but they need two extra things. One is a **checkpoint**, so each run knows where the last one stopped. The other is **idempotent** loads, so re-running a batch doesn't create duplicates.

| | Full refresh | Incremental |
|---|---|---|
| Each run processes | Everything | Only new data since the checkpoint |
| Cost / time | Grows with total data size | Grows with new data only |
| Needs a checkpoint? | No | Yes |
| Re-run risk | Just slow | Duplicates, unless loads are idempotent |
| Retrofitting later | n/a | Painful (today's lesson) |

---

Q. What is idempotency?

A. (From class) "Verify idempotency" was the final validation step before orchestration, so the pipeline "continuously loads data into Redshift" safely.

Expanded: An operation is **idempotent** if running it once or many times gives the same result. For a pipeline, re-running a batch (after a failure, a retry or a scheduler hiccup) must not double the rows. Today's design gets that by loading into a **landing table** tagged with a `batch_id`, then using **MERGE** into the canonical table: rows that already exist are updated or skipped, and only new rows are inserted. Same idea as `INSERT … ON CONFLICT DO NOTHING` from the Training 22 homework. (In the final working procedure the insert step was written as `INSERT … WHERE NOT EXISTS` rather than `MERGE`: see "The load SQL" below.) General error-handling and idempotency notes: Training 0.

**Interview line (idempotent incremental load):** "Each run gets a batch window and a batch ID. The batch lands in a landing table, I deduplicate it on the business key with `ROW_NUMBER()`, then MERGE or insert-where-not-exists into the target in one transaction, and only after the validations pass do I advance the checkpoint. Re-running the same batch changes nothing."

---

Q. What is a stored procedure?

A. (From class) "A stored procedure is kind of like a function in a regular programming language. It'll just make it so that this is stored."

Expanded: A stored procedure is a named block of SQL saved **inside the database**, which you run with `CALL procedure_name(args);`. Instead of pasting the long merge-and-refresh SQL into the query editor every time, the logic lives in Redshift, and an orchestrator like Step Functions only has to call it with the new batch ID. Created with `CREATE OR REPLACE PROCEDURE`.

| | Pasted SQL script | Stored procedure |
|---|---|---|
| Where it lives | A file / the query editor | In the database |
| How you run it | Copy, paste, edit the batch ID, run | `CALL sp_name('<batch_id>');` |
| Easy to automate? | No | Yes, one call from Step Functions or a scheduler |
| Change it | Edit the file | `CREATE OR REPLACE PROCEDURE` |

---

Q. What is a checkpoint (for a batch pipeline), and where should it live?

A. (From class) Evan chose to keep the checkpoint in Redshift rather than add DynamoDB: "It's valid architecture, but it's an unnecessary complexity… I'm going to opt for simplicity and just allow Redshift to maintain the checkpoint, rather than introducing yet another AWS service."

Expanded: When we ran the Glue jobs by hand, we typed in the batch window ourselves. When Step Functions runs them automatically, something has to remember the **last successfully completed batch**, so the next run starts right after it. That record is the checkpoint, and it should only **advance after the stored procedure and the validations succeed**. If a run fails, the next run retries the same window instead of skipping data. (This is the batch version of the streaming checkpoint from Training 22.)

| Option | Pros | Cons |
|---|---|---|
| **DynamoDB table** (AI's suggestion) | Tiny, fast key-value store; common AWS pattern | Yet another service, with its own IAM permissions and cost |
| **Redshift table** (Evan's choice) | Already in the pipeline; can be updated in the same transaction as the load | Ties the checkpoint to the warehouse |

Design lesson: **don't add a service just because the AI suggested it.** Ask "what's the rationale?" and pick the simplest thing that works.

---

# The Load SQL (landing → canonical → Gold)

Q. What does the stored procedure's load SQL actually look like?

A. (From a homework rebuild of the class procedure; table names there are the non-`_v2` versions.) Deduplicate the batch on the business key with `QUALIFY ROW_NUMBER()`, then insert only keys that aren't in the target yet. Evan used `INSERT … WHERE NOT EXISTS` instead of `MERGE` because Redshift kept rejecting the `MERGE` syntax. For insert-only data, both give the same result.

```sql
CREATE OR REPLACE PROCEDURE public.sp_process_citibike_batch(p_batch_id IN VARCHAR)
AS $$
BEGIN
    -- 1. New observations into the canonical table (one row per business key)
    INSERT INTO public.citibike_station_snapshot (station_id, snapshot_ts, bikes_available, docks_available /* , ... */)
    SELECT station_id, snapshot_ts, bikes_available, docks_available /* , ... */
    FROM (
        SELECT *
        FROM public.citibike_station_snapshot_landing
        WHERE batch_id = p_batch_id
          AND station_id IS NOT NULL AND snapshot_ts IS NOT NULL
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY station_id, snapshot_ts
            ORDER BY station_name DESC NULLS LAST, capacity DESC NULLS LAST
        ) = 1
    ) src
    WHERE NOT EXISTS (
        SELECT 1 FROM public.citibike_station_snapshot tgt
        WHERE tgt.station_id = src.station_id AND tgt.snapshot_ts = src.snapshot_ts
    );

    -- 2. Missing dates into gold.dim_date      (same NOT EXISTS pattern)
    -- 3. Missing stations into gold.dim_station (latest row per station via QUALIFY)
    -- 4. Missing fact rows into gold.fact_station_snapshot (NOT EXISTS on station_id + snapshot_ts)
END;
$$ LANGUAGE plpgsql;
```

The wrapper `sp_complete_citibike_batch(p_batch_id, p_window_end)` then: raises an error if the batch has no landing rows → `CALL sp_process_citibike_batch` → raises if Gold is missing any canonical row → raises if `p_window_end` would move the checkpoint **backwards** → `UPDATE` the checkpoint. Any `RAISE EXCEPTION` rolls back the whole call, so the checkpoint never advances on a failed batch.

Expanded: the same step written as a Redshift `MERGE`. Stage the deduplicated batch first, then merge:

```sql
CREATE TEMP TABLE batch_src AS
SELECT *
FROM public.citibike_station_snapshot_landing_v2
WHERE batch_id = '<batch_id>'
QUALIFY ROW_NUMBER() OVER (PARTITION BY station_id, snapshot_ts ORDER BY station_name DESC NULLS LAST) = 1;

MERGE INTO public.citibike_station_snapshot_v2
USING batch_src AS src
ON  public.citibike_station_snapshot_v2.station_id  = src.station_id
AND public.citibike_station_snapshot_v2.snapshot_ts = src.snapshot_ts
WHEN MATCHED THEN UPDATE SET
     bikes_available = src.bikes_available,
     docks_available = src.docks_available
WHEN NOT MATCHED THEN INSERT (station_id, snapshot_ts, bikes_available, docks_available)
     VALUES (src.station_id, src.snapshot_ts, src.bikes_available, src.docks_available);
```

| Redshift `MERGE` rule | What it means here |
|---|---|
| A target row may match **only one** source row | Duplicate keys in landing make `MERGE` fail, so deduplicate first (a doubled `COPY` in one homework run, 15,112 rows vs 7,556 unique, would have broken it) |
| `MERGE … REMOVE DUPLICATES` is a simplified form | Updates matches and inserts the rest, using the source's columns, with no `WHEN` clauses to write |
| Grammar is stricter than Snowflake or Delta (e.g. no extra conditions on `WHEN MATCHED`) | Patterns copied from other warehouses often fail with "unexpected input". Check the Redshift docs |

| | `INSERT … WHERE NOT EXISTS` | `MERGE` |
|---|---|---|
| New keys | Inserted | Inserted |
| Existing keys | Left alone | Updated (or deleted) |
| Fits | Insert-only facts like station snapshots | Dimensions and records that change (SCD1, CDC) |

**Interview line:** "MERGE is an upsert: match source to target on the business key, update the matches, insert the rest. Before merging I deduplicate the source with ROW_NUMBER, because Redshift fails if two source rows match the same target row." See Training 21 for QUALIFY / ROW_NUMBER.

---

# Class Walkthrough: Automating the Incremental Pipeline

## The incremental pipeline, step by step

Evan worked from an AI-generated package, `citybike-incremental-v2.zip`, unzipped to `/tmp`. Steps:

| # | Step | Notes |
|---|---|---|
| 1 | Create a Redshift **landing table** like the snapshot table, plus a `batch_id` column | Where each new batch lands before it's merged |
| 2 | Upload the incremental Glue scripts to S3 | Included `incremental_jobs.py` |
| 3 | Run Glue job 1: **Bronze → Silver incremental (v2)** for one batch window | Silver output goes under a separate batch prefix in S3 |
| 4 | Verify the Silver batch in S3 | |
| 5 | Run Glue job 2: **Silver → Redshift incremental** | Loads the batch into the landing table |
| 6 | Validate the landing table | "We got a bunch of rows that landed" |
| 7 | **Merge into canonical staging and refresh Gold** | "The most important database step", see below |
| 8 | Validate referential integrity | Both checks returned 0 (no orphans) |
| 9 | Wrap the SQL in a **stored procedure** and test it with `CALL` | |
| 10 | Add a checkpoint, then automate with Step Functions | |

**Step 7, what the merge does, in one transaction:**
1. `MERGE` landing observations into `public.citibike_station_snapshot_v2` (the canonical table). (The final working version used deduplicate + `INSERT … WHERE NOT EXISTS`; see "The load SQL" above.)
2. Insert any missing calendar dates into `gold.dim_date`.
3. Insert new stations and update station metadata in `gold.dim_station`.
4. Insert new observations into the Gold fact snapshot table.
5. `COMMIT`.

Doing it all in one transaction means Gold is never half-updated: either the whole batch is applied or none of it is.

**Problems hit along the way (useful for your own homework):**
- **Glue job failed: permissions.** The job role lacked an S3 permission. The IAM policy simulator went from "implicit deny" to "allowed" after the policy fix.
- **Glue job failed: "missing required arguments".** The incremental jobs need parameters (the batch window and batch ID). Clicking "Run" in the console doesn't pass them, so Evan started the job from the CLI with `--arguments` instead.
- **Jobs not showing in the Glue UI.** The incremental jobs had run IDs but didn't appear in the main job list. Evan found them another way. (Worth checking the region first: it wasn't the cause here, but it often is.)
- **Tip from a student:** in a Glue job run, select it and click **View details**. The page updates live, so you don't have to keep clicking refresh.
- **Redshift `MERGE` syntax errors.** The AI kept going back and forth on `MERGE INTO` syntax, and the query editor showed "unexpected input". Redshift's `MERGE` is stricter than Postgres or Snowflake, so check the Redshift docs when it complains. The specific rules (one source row per target row, so deduplicate first; no extra conditions on `WHEN MATCHED`) are in "The load SQL" above. The final procedure avoided `MERGE` altogether.
- **Query editor v2 runs only the highlighted text.** If anything is highlighted, only that part runs. Deselect everything to run the whole script. (Evan: "the mouse should be a completely optional extra when it comes to computer programming.")
- **The AI gave the `CALL` before the `CREATE PROCEDURE`.** Create first, then call.

On waiting for jobs: "My favorite part of programming, waiting." Big data jobs can run for hours, so the real work is monitoring them for problems.

---

## Automating it: checkpoint and wrapper procedure

- Scheduling the existing incremental jobs every 5 minutes as-is would either **repeat old batches** or **leave gaps**, because nothing tracked which window was done. Hence the **durable checkpoint**, plus a fresh batch window generated for each execution.
- The checkpoint advances **only after** the stored procedure and the validations succeed.
- Evan rejected DynamoDB for the checkpoint and created it in Redshift (see Key Concepts).
- Instead of changing the working procedure, he created a **wrapper**: `sp_complete_citibike_batch(batch_id, window_end)`. It checks that the batch exists in landing, calls the working `sp_process_citibike_batch(batch_id)`, runs consistency checks, then advances the checkpoint. "I definitely don't want to replace a working procedure if I can help it." The wrapper must be called **outside an explicit transaction**.

---

## Terraform: importing existing Step Functions resources

The Step Functions state machine (`citibike-class-orchestration`) already existed, created before Terraform was involved. To manage it with Terraform:

| Step | Command | Why |
|---|---|---|
| Check state | `terraform state list` | Returned "no state file": Terraform didn't know about any existing resources |
| Initialize | `terraform init` | Download the AWS provider |
| **Import** existing resources | `terraform import <address> <aws-id>` for the CloudWatch log group, the IAM role, the inline policy and the state machine | Tells Terraform "this resource in my code = this real thing in AWS" |
| Check state again | `terraform state list` | Now lists the imported resources |
| Plan | `terraform plan` | **"No changes"** is the ideal result after an import: the code matches reality |
| Edit `main.tf` | Point the state machine at the **incremental** Glue jobs instead of the old ones; add the runtime arguments (Redshift workgroup, etc.) | |
| Plan + apply | `terraform plan -out <file>` then `terraform apply <file>` | Applies exactly the saved plan |

Q. How do you bring existing AWS resources under Terraform?

A. (From class) Write the matching resource blocks, `terraform import` each real resource into state, then run `terraform plan`. "No changes" means the code matches reality.

Expanded: **Terraform state** is Terraform's record of which real AWS resources belong to which blocks in your code. Without state, Terraform assumes nothing exists, and `apply` would try to create duplicates. `terraform import` connects existing resources to the code. That's the usual way to adopt Terraform for infrastructure first built by clicking or with the CLI.

What made it take over an hour:
- The AI's commands kept introducing new issues, such as a reference to `svv_redshift_procedures` that didn't exist as expected and a bad grep command.
- Evan ended up in the wrong directory, then went back to the original Terraform root, where the state lives.
- A JSON/Python mix-up in the state machine definition, around the coordinator script `coordinator.py`.
- Evan: "Terraform was supposed to simplify this." Fair, but Terraform pays off on the *next* change, not the first import.

Result: `Apply complete`. Infrastructure for an automated incremental pipeline is deployed. **Ingestion (the Lambda) already runs independently every 5 minutes**, and Step Functions orchestrates the processing (Bronze → Silver → Redshift → merge/Gold → checkpoint).

---

## First controlled Step Functions run

- Plan: run **one controlled execution** before enabling the schedule, then verify the database.
- Started with `aws stepfunctions start-execution`. Evan suggested watching it in the **Step Functions console**: it shows each state turning green or red.
- The execution **failed immediately (3:36 PM)**: permission denied. "Every frustrating problem in the cloud ultimately comes down to permissions errors." The Step Functions role needs permission for each service it calls: `glue:StartJobRun` / `glue:GetJobRun` on the jobs, `redshift-data:ExecuteStatement` / `DescribeStatement` for the procedure call, and so on.

- **Fix 1:** the failure was in `PrepareBatch`: `permission denied for relation citibike_pipeline_checkpoint`. The coordinator Lambda logs in to Redshift as the database user **`IAMR:CitiBikeBatchCoordinatorRole`**. Redshift creates that user automatically for the IAM role, but it has no table privileges until you `GRANT` them. Evan found the exact user name in Redshift query history / `pg_user`, because the AI kept guessing it wrong.
- **Retry:** Bronze → Silver ✅, Silver → Redshift ✅, then the **last step failed**: permission denied again. The coordinator's Redshift user could read the checkpoint table but **not the landing table** that the completion procedure uses. Fix: more `GRANT SELECT …` statements in Redshift.
- **Redrive from failure:** in the Step Functions console, **Redrive** restarts the execution from the failed state, so the two Glue jobs that already succeeded didn't run again. Before redriving, Evan checked that the **checkpoint hadn't advanced**, which it shouldn't have, since the batch never completed.
- **Result: green across the board.** "The first end-to-end Citi Bike incremental pipeline execution has finally succeeded."

### Validation after the first successful run

| Check | Expected | Result |
|---|---|---|
| Checkpoint audit: last completed batch / updated at | Updated by this run | Last completed 19:33 UTC, updated 19:51 UTC (about a minute before) ✅ |
| Canonical row count vs Gold fact row count | Equal | Equal ✅ |
| Duplicate observations query | 0 rows | 0 rows ✅, so idempotency holds |

Q. Why do AWS services need SQL GRANTs in Redshift as well as IAM permissions?

A. (From class) Both failures in this run were `permission denied for relation …` even though IAM allowed the Data API calls. The fix was `GRANT` statements inside Redshift for the role's database user (`IAMR:<role name>`).

Expanded: there are **two layers of permissions** when AWS services talk to Redshift. **IAM** decides whether the role may call the Redshift Data API at all. Then **inside Redshift**, the database user that role maps to needs normal SQL `GRANT`s: `EXECUTE` on procedures, and `SELECT`/`INSERT`/`UPDATE` on every table the procedure touches. Today's two failures were both the second layer. Same pattern as Aurora IAM auth in Training 22: IAM gets you in the door, `GRANT` decides what you can touch.

| Step Functions term | Meaning |
|---|---|
| **Execution** | One run of the state machine |
| **Redrive** | Restart a failed execution from the failed step, keeping the successful steps' results |
| **Graph view** | The console diagram: each state turns green (succeeded), red (failed) or blue (running) |

**Interview line (Redrive vs re-running):** "Redrive restarts a failed Standard execution from the failed state and reuses the results of the steps that already succeeded, so expensive Glue jobs don't run twice. A fresh execution starts from the top. Before either, I check the checkpoint didn't advance."

---

## Scheduling it: EventBridge Scheduler in Terraform

- **Interval: every 30 minutes.** The AI recommended it as "a reasonable balance between data freshness and Glue startup costs". Each run starts two Glue jobs, and every Glue job run has startup time and a minimum billed duration, so running every 5 minutes would cost much more for little benefit.
- New file **`scheduler.tf`** in the same Terraform directory as `main.tf`. Terraform reads **every `.tf` file in the folder** as one configuration, so splitting resources into files is just for organization.
- **Safe rollout pattern:**
  1. Create the schedule **disabled** first → `plan` (3 to add) → `apply`.
  2. Verify: `DISABLED`, `rate(30 minutes)`.
  3. Change `state` to `ENABLED` in the `.tf` → `plan` (1 to change) → `apply`.
- **Overlap guard:** EventBridge Scheduler doesn't stop a new execution from starting while the previous one is still running. A conservative safeguard checks for running executions first. Otherwise two runs could process the same batch window. Clean ways to do it: a first state that calls `ListExecutions` with status `RUNNING` and exits if another run is active, or a lock row in the checkpoint table that a run must claim before starting.
- Last validation: wait for the first scheduled run (30 min) and confirm it succeeds.
- **Result: a fully automated pipeline from ingestion to Gold.** Lambda puts data into Bronze every 5 minutes, Step Functions processes it every 30 minutes, and Terraform describes all of it.

```
EventBridge (5 min) ─▶ Lambda ─▶ S3 Bronze
EventBridge Scheduler (30 min) ─▶ Step Functions:
    Glue Bronze→Silver (incremental) ─▶ Glue Silver→Redshift landing ─▶ CALL sp_complete_citibike_batch
    (MERGE → canonical, refresh Gold dims/fact, advance checkpoint)
```

**AI workflow tip from Evan:** a very long ChatGPT chat starts making more mistakes. When a chat gets long, ask it to "summarize the work you've done so I can pass it to a new chat with full context", then continue in a fresh chat. Evan did this before the next topic.

**Next (after break):** a real-time **Streamlit dashboard** reading from Redshift, deployed on **EC2** (simpler than Fargate with only an hour left), set up in Terraform.

---

# From Evan's Shared ChatGPT Chat

Source: Evan's shared chat "Terraform Teaching Strategy". It covers Tuesday's and today's classes, including the first hour of today's class.

## The final architecture

```
EventBridge Scheduler (every 5 min) ─▶ Lambda citibike-ingestion ─▶ S3 Bronze (station_status + station_information JSON)

EventBridge Scheduler citibike-incremental-every-30-min ─▶ Step Functions citibike-class-orchestration (Standard):
   PrepareBatch      (coordinator Lambda: read checkpoint, compute window, make batch ID)
   BronzeToSilver    (Glue CitiBikeBronzeToSilverIncrementalV2)
   SilverToRedshift  (Glue CitiBikeSilverToRedshiftIncrementalV2 → landing table)
   CompleteBatch     (coordinator Lambda: CALL sp_complete_citibike_batch via Redshift Data API)
   PipelineSucceeded
```

The Step Functions workflow does **not** call the ingestion Lambda. Ingestion keeps landing files in Bronze on its own schedule, and orchestration processes whatever has piled up. This **decouples** ingestion from processing.

| Piece | Name | Notes |
|---|---|---|
| Coordinator Lambda | `citibike-batch-coordinator` (Python 3.12, boto3) | Two operations: `PrepareBatch` and `CompleteBatch` |
| Glue job 1 | `CitiBikeBronzeToSilverIncrementalV2` | Args `--BATCH_ID --START_AFTER_UTC --END_BEFORE_UTC`; writes `silver/citibike/incremental_batches_v2/batch_id=<id>/`; refuses to overwrite an existing batch folder |
| Glue job 2 | `CitiBikeSilverToRedshiftIncrementalV2` | Arg `--BATCH_ID`; loads into the landing table via the Glue connection `citibike-redshift-connection` |
| Landing table | `public.citibike_station_snapshot_landing_v2` | Can contain duplicates if a batch is appended twice. That's fine, the merge filters them |
| Canonical table | `public.citibike_station_snapshot_v2` | Deduplicated observations |
| Gold | `gold.dim_station`, `gold.dim_date`, `gold.fact_station_snapshot` | Star schema |
| Checkpoint | `public.citibike_pipeline_checkpoint` | Columns `pipeline_name`, `last_completed_utc`, `last_batch_id`, `updated_at`; pipeline name `citibike_incremental` |
| Procedures | `sp_process_citibike_batch(VARCHAR)`, `sp_complete_citibike_batch(VARCHAR, TIMESTAMP)` | |
| Terraform files | `main.tf`, `orchestration.tf`, `scheduler.tf`, `coordinator.py` | All in `citibike-stepfunctions-terraform/` |

## Design details worth knowing

| Detail | What it means | Why |
|---|---|---|
| **Window `[start, end)`** | Start inclusive, end exclusive | Back-to-back windows never count a file twice or skip one. A bug fix during class changed `start < ts < end` to `start <= ts < end` |
| **2-hour overlap** | Each new window starts 2 hours *before* the last checkpoint (e.g. checkpoint 18:00 → start 16:00) | Picks up **late-arriving** files. The MERGE/dedup makes the overlap harmless. Files more than 2 hours late are still missed |
| **Skip the newest 10 minutes** | The window ends 10 minutes before "now" | Files still being written aren't processed half-finished |
| **Batch ID = Step Functions execution name** | Each run's batch is traceable to its execution | Makes debugging and auditing easy |
| **Glue job bookmarks disabled** | Glue's built-in "what have I processed" tracking is off | The Redshift checkpoint controls the windows instead. Two trackers would conflict |
| **`.sync` Glue integration** | Step Functions waits for each Glue job to finish before the next state | Otherwise it would start the next step while Glue is still running |
| **SQL moved into the Lambda** | `CompleteBatch` builds and runs the `CALL` in Python, then polls the Data API | Building dynamic SQL inside the Step Functions definition (`Sql.$` with intrinsic functions) failed AWS validation |

## Why Terraform took so long (the full story)

1. Terraform was first initialized in a **new directory without the state file**. The plan said **7 to add**, meaning it would have tried to **recreate resources that already existed**.
2. Moving back to the original directory, where the state lives, gave the correct plan: **3 to add, 2 to change**.
3. The first apply **partially succeeded**, then failed on the invalid `Sql.$` syntax in the state machine.
4. Fix: move the SQL execution into the coordinator Lambda. Final apply: **0 added, 4 changed, 0 destroyed**, and the state machine kept its existing ARN.

Q. What does it mean when `terraform plan` wants to add resources you know already exist?

A. (From class) Terraform has lost track of its state, usually because it's running in a folder without the state file.

Expanded: **Lesson:** always run Terraform from the directory that holds `terraform.tfstate`. A plan that wants to *add* things you know already exist means Terraform has lost track of its state, so **stop and don't apply**.

## Baseline numbers before the first automated run

Canonical observations **1,579,415** = Gold fact observations **1,579,415**. No duplicate station/timestamp rows, and no orphan station or date keys in the fact table.

---

## Last hour: Streamlit dashboard on EC2, via Terraform (from Evan's second shared chat)

Source: Evan's second shared chat. This is also the basis for the **optional extra-credit homework**.

**Goal:** a "real-time" Citi Bike dashboard: a map with color-coded station markers (available bikes, e-bikes, empty docks or utilization, user-selectable), plus historical charts. It runs on **EC2** ("the easiest deployment option"), and **both the permissions and the deployment are in Terraform**, added to the existing project.

**Key design decision: two data sources with two refresh rates.**

| Part of the dashboard | Data source | Freshness |
|---|---|---|
| Live map | Citi Bike's public **GBFS API**, called directly by the app | Refreshes every ~60 s (as fresh as the feed) |
| Historical charts | **Redshift** (canonical/Gold) via the Redshift Data API | Only as fresh as the last 30-minute pipeline run |

This avoids "pretending that a 30-minute batch pipeline provides second-by-second warehouse data." A dashboard on Redshift is never truly real-time: it can only be as fresh as the last batch that loaded.

**What Terraform created (plan: 6 to add, 0 to change, 0 to destroy):**

| Resource | Purpose |
|---|---|
| EC2 instance (`t3.small`, Amazon Linux, 12 GB gp3 encrypted) | Runs Streamlit |
| Security group | Port **8501** (Streamlit's default) open **only to your own IP** (`/32` from `checkip.amazonaws.com`) |
| IAM role + instance profile | Lets the app call the Redshift Data API (and Systems Manager) **without access keys** |
| User data (bootstrap script) | On first boot: installs Python, creates a venv, installs requirements, sets up a **systemd service**, so Streamlit restarts on reboot |

**Problems hit:**
1. **Invalid HCL from the AI.** It wrote one-line blocks with commas: `variable "x" { type = string, default = "t3.small" }`. Terraform only allows one-line blocks with a **single** argument. Blocks with several arguments must be multi-line. `terraform fmt` + `terraform validate` catch this.
2. **Wrong directory again.** Terraform only reads the `.tf` files in the **current folder**, not subfolders. Running `validate` from the parent folder didn't even see `dashboard.tf`.
3. **Redshift permission denied (again!)**: `permission denied for relation citibike_station_snapshot_v2`. IAM let the EC2 role call the Data API, but its database user `IAMR:CitiBikeDashboardRole-…` had no `SELECT`. The suffix comes from Terraform's `name_prefix`, so look it up with `SELECT usename FROM pg_user WHERE usename LIKE 'IAMR:%Dashboard%';`. Fix: read-only grants: `GRANT USAGE ON SCHEMA public/gold` + `GRANT SELECT …`. IAM policies alone can **never** grant table access in Redshift.

**Stopping it overnight safely (Evan wanted "0% risk" to the main pipeline):**
- Don't `terraform destroy`: it could touch the pipeline resources in the same state. Don't terminate it either.
- **Stop** the instance with the CLI: `aws ec2 stop-instances --instance-ids $(terraform output -raw dashboard_instance_id)`. Start it again the next day. Stopping is an operational action, not an infrastructure change, so Terraform doesn't need to know.
- The **public IP changes** after stop/start (no Elastic IP), so `terraform output dashboard_url` goes stale. Get the new IP with `aws ec2 describe-instances … PublicIpAddress`.

| While EC2 is stopped | Charged? |
|---|---|
| EC2 compute | No |
| EBS volume (12 GB) | Yes (small) |
| Public IPv4 | Released, no charge |
| App, venv, systemd service | Kept on disk; Streamlit starts automatically on boot |
| The pipeline (Lambda every 5 min, Step Functions every 30 min) | **Still running and billing**, since stopping EC2 doesn't affect it |

---

# CDC and AWS DMS (roadmap topic, not demoed in class)

Q. What is CDC (change data capture)?

A. (Not covered in class.) Capturing every insert, update and delete from a source database as it happens, and applying those changes downstream, instead of re-copying whole tables.

Expanded:

| CDC method | How it finds changes | Catches deletes? | Load on the source |
|---|---|---|---|
| Query-based (`WHERE updated_at > checkpoint`) | Polls a timestamp column, like our batch window | No (hard deletes are invisible) | Repeated queries |
| Trigger-based | Triggers write each change to an audit table | Yes | High (extra writes on every transaction) |
| **Log-based** (DMS, Debezium) | Reads the database's transaction log: Postgres WAL via logical replication, MySQL binlog | Yes | Lowest. The preferred method |

**Interview line:** "CDC streams row-level changes out of a database. Log-based CDC reads the transaction log, so it catches deletes and barely touches the source. Downstream I land the changes, keep the latest change per key, and MERGE them into the target."

---

Q. How does AWS DMS do CDC?

A. (Not covered in class.) DMS (Database Migration Service) copies data from a source endpoint to a target endpoint, as a one-time full load, ongoing CDC, or both.

Expanded:

| DMS piece | Job |
|---|---|
| Replication instance (or DMS Serverless) | The compute that runs the copy |
| Source / target endpoints | Connection details, e.g. RDS Postgres → S3 or Redshift |
| Replication task | What to copy and how: **full load**, **CDC only**, or **full load + ongoing replication** |

- **Source setup:** Postgres needs logical replication turned on (`rds.logical_replication = 1` on RDS); MySQL needs `binlog_format = ROW`.
- **Common pattern:** DMS → S3 as Parquet. Each change row carries an `Op` column (`I`, `U`, `D`) and a commit timestamp. A Glue/Spark job keeps the **latest change per key**, then applies it to Redshift or Delta: delete the `D` keys, MERGE the rest. That is the same landing → dedupe → merge → checkpoint pattern as today's pipeline.

| | AWS DMS | Debezium → Kafka |
|---|---|---|
| Type | Managed AWS service | Open source, runs on Kafka Connect |
| Output | Directly to S3, Redshift, Kinesis, Kafka and more | Change events in Kafka topics |
| Best for | Migrations and AWS-native replication | Event-driven systems; many consumers reading the same changes |
| You operate | Almost nothing | Kafka + Connect cluster |

---

# Interview-ready from today

| Question | Your one-line answer |
|---|---|
| Full vs incremental load? | Full reprocesses everything each run; incremental processes only new data since a checkpoint, so it needs idempotent loads |
| How do you build an idempotent incremental load? | Batch window + batch ID → landing table → dedupe with ROW_NUMBER → MERGE / insert-where-not-exists in one transaction → advance the checkpoint only after validations pass |
| How do you handle late-arriving data? | Overlap each window with the previous one (we used 2 hours) and let the dedup/MERGE make the overlap harmless; skip the newest few minutes so half-written files aren't read |
| Where should a checkpoint live? | Somewhere durable that can be updated after the load succeeds; we used a Redshift table rather than adding DynamoDB |
| What is CDC and how does DMS do it? | Streaming row-level changes from a database; DMS reads the transaction log and delivers full load + ongoing changes to S3/Redshift/Kinesis |
| Redrive vs re-run? | Redrive resumes a failed execution from the failed step; a re-run starts over |
| Why GRANTs as well as IAM for Redshift? | IAM lets the role call the Data API; Redshift GRANTs decide which tables its database user can touch |
| Plan wants to add resources that exist? | Terraform lost its state (wrong folder). Stop, don't apply |
