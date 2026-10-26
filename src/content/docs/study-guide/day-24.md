---
title: Study Guide - Day 24
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 24: Incremental Pipelines"
sidebar:
  order: 240
---

Study Guide - Day 24 (source: notes/Training 24.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Incremental Pipeline.** A full refresh reprocesses everything each run; an incremental pipeline processes only what's new since the last successful run, using a **batch window** (start/end timestamps) and a **batch ID** on every row. Cheaper and faster, but it needs a **checkpoint** and **idempotent** loads. Evan's lesson: design incremental from the start; retrofitting is painful.

**Idempotency.** Running an operation once or many times gives the same result, so re-running a batch doesn't duplicate rows. Achieved by loading into a **landing table** tagged with `batch_id`, then **MERGE** into the canonical table (insert new, update or skip existing).

**Stored Procedure.** "Kind of like a function in a regular programming language", stored in the database. `CREATE OR REPLACE PROCEDURE`, run with `CALL sp_name('<batch_id>')`. Makes automation a single call. Create before calling.

**Checkpoint.** The record of the last completed batch, so the next run starts right after it. It advances **only after** the procedure and validations succeed; a failed run retries the same window. Evan kept it in a Redshift table instead of adding DynamoDB: don't add a service just because the AI suggested it.

**The Steps.** Landing table with `batch_id` → upload incremental Glue scripts → Glue 1 Bronze → Silver for one window (separate batch prefix) → verify → Glue 2 Silver → Redshift landing → validate → **merge in one transaction** (MERGE into canonical, add missing dates to `dim_date`, insert/update `dim_station`, insert Gold facts, COMMIT, so Gold is never half-updated) → referential integrity checks (0 orphans) → stored procedure → checkpoint → Step Functions. Gotchas: Glue jobs needing parameters must be started from the CLI with `--arguments`; Redshift's `MERGE` is stricter than Postgres/Snowflake; Query editor v2 runs only highlighted text. A **wrapper** procedure (`sp_complete_citibike_batch`) checks the batch, calls the working procedure, validates and advances the checkpoint, instead of replacing working code.

**Terraform Import.** The state machine already existed. `terraform state list` (no state) → `init` → `terraform import <address> <aws-id>` for the log group, IAM role, policy and state machine → `plan` should say **"No changes"** → edit to point at the incremental jobs → `plan -out` + `apply <file>`. **State** maps real resources to code; without it, `apply` tries to create duplicates. A plan that wants to **add** things you know exist means you're in the wrong directory or lost state: stop. Terraform reads every `.tf` file in the current folder only.

**First Step Functions Run.** Failed on permissions twice. Two layers: **IAM** lets the role call the Redshift Data API; inside Redshift the auto-created user (`IAMR:<RoleName>`) needs SQL `GRANT`s on every table and procedure. Find the real user name in `pg_user`. **Redrive** restarts from the failed step without rerunning succeeded Glue jobs; check the checkpoint didn't advance first. Validation: checkpoint updated, canonical count = Gold count, 0 duplicates.

**Scheduling.** EventBridge Scheduler every **30 minutes** (Glue startup and minimum billing make 5 minutes wasteful), in `scheduler.tf`. Safe rollout: create **disabled**, verify, then enable. Add an overlap guard so two runs don't process the same window. Final: Lambda → Bronze every 5 min; Step Functions (PrepareBatch → BronzeToSilver → SilverToRedshift → CompleteBatch) every 30 min, all in Terraform. Ingestion is **decoupled** from processing.

**Design Details.** Window is `[start, end)` (inclusive start, exclusive end). Each window starts 2 hours before the checkpoint to catch **late-arriving** files; MERGE makes the overlap harmless. Skip the newest 10 minutes (files still being written). Batch ID = Step Functions execution name. Glue job bookmarks off (one tracker only). `.sync` Glue integration waits for each job. Complex SQL moved into the coordinator Lambda.

**Streamlit Dashboard on EC2.** Live map from Citi Bike's GBFS API (~60 s refresh) plus historical charts from Redshift (only as fresh as the last 30-minute batch). Terraform created a `t3.small`, a security group opening port **8501 only to your IP**, an IAM role/instance profile (no access keys) and user data that installs a venv and a **systemd** service. Problems: invalid one-line HCL blocks with commas (`terraform fmt`/`validate`), wrong directory, and Redshift `permission denied` again (IAM never grants table access; use `GRANT USAGE` + `GRANT SELECT`). To pause safely, **stop** the instance with the CLI rather than `terraform destroy`; the public IP changes on restart; EBS still bills while stopped.

**AI Tip.** Long chats make more mistakes: ask for a summary and continue in a fresh chat.

---

# Part 2: Cheat Sheet

## Concepts
- Full refresh vs incremental · batch window + batch ID
- Idempotent = rerun-safe · landing table + MERGE
- Stored procedure: `CREATE OR REPLACE PROCEDURE` → `CALL`
- Checkpoint advances only after success · keep it simple (Redshift, not DynamoDB)

## Merge Transaction
- MERGE canonical → dim_date → dim_station → fact → COMMIT
- Validate: no orphans, counts match, 0 duplicates

## Terraform
- `state list` → `import` → `plan` = "No changes" → edit → `plan -out` → `apply file`
- Run from the folder with `terraform.tfstate` · unexpected "add" = stop
- Every `.tf` in the folder = one config · `fmt` + `validate`

## Permissions
- IAM = may call the API · Redshift `GRANT` = may touch the table
- User `IAMR:<Role>` → find in `pg_user`

## Step Functions
- Execution · Graph view · **Redrive** from failure · `.sync` waits for Glue
- PrepareBatch → BronzeToSilver → SilverToRedshift → CompleteBatch

## Windows
- `[start, end)` · 2 h lookback for late files · skip newest 10 min · batch ID = execution name · bookmarks off

## Scheduling
- 30-minute rate · create disabled → enable · overlap guard

## Dashboard
- GBFS live + Redshift history · EC2 + SG port 8501 /32 · instance profile · systemd
- Stop (not destroy) · IP changes · EBS still bills

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What's the difference between a full refresh and an incremental pipeline?
A: A full refresh reprocesses all the data every run. An incremental pipeline only processes what's new since the last successful run, using a batch window and a checkpoint, so it's cheaper and faster.

Q: What is idempotency and why does an incremental pipeline need it?
A: Running something once or many times gives the same result. Batches get retried after failures, so loads must not create duplicates when a batch runs twice.

Q: How did the class make loads idempotent?
A: Each batch landed in a landing table tagged with a batch ID, then a MERGE moved it into the canonical table, inserting only new rows and updating or skipping existing ones.

Q: What is a stored procedure?
A: A named block of SQL stored inside the database, like a function. You run it with CALL, which makes it easy for an orchestrator to trigger the whole merge with one statement.

Q: What is a checkpoint, and when should it advance?
A: The record of the last batch that completed, so the next run knows where to start. It should only advance after the load and validations succeed, so a failed run retries the same window.

Q: Why did Evan keep the checkpoint in Redshift instead of DynamoDB?
A: DynamoDB is valid but adds another service with its own permissions and cost. Redshift was already in the pipeline, so it was the simpler choice.

Q: Why run the whole merge in one transaction?
A: So Gold is never half-updated. Either the whole batch is applied to the canonical table and every Gold table, or none of it is.

Q: What does terraform import do?
A: It links an existing AWS resource to a block in your Terraform code, adding it to Terraform's state, so Terraform can manage infrastructure that was originally built by hand.

Q: After an import, what should terraform plan say?
A: No changes. That means the code matches what really exists.

Q: Your plan wants to add resources you know already exist. What do you do?
A: Stop and don't apply. You're probably in a folder without the state file, so Terraform thinks nothing exists and would create duplicates.

Q: Why did Step Functions fail with permission denied even though the IAM role was right?
A: There are two layers. IAM let the role call the Redshift Data API, but inside Redshift the role's database user had no GRANTs on the tables, so the SQL failed.

Q: What does Redrive do in Step Functions?
A: It restarts a failed execution from the failed step, keeping the results of the steps that already succeeded, so the Glue jobs didn't run again.

Q: Why schedule the pipeline every 30 minutes instead of every 5?
A: Each run starts two Glue jobs, and every Glue run has startup time and a minimum billed duration. Every 5 minutes would cost far more for little gain.

Q: Why create the schedule disabled first?
A: It's a safe rollout. You verify the schedule exists with the right settings, then enable it in a separate, small change.

Q: Why does each batch window start two hours before the checkpoint?
A: To pick up files that arrived late. The MERGE removes duplicates, so the overlap is harmless.

Q: Why use an inclusive start and exclusive end for the window?
A: So back-to-back windows never count the same file twice or skip one at the boundary.

Q: Why turn off Glue job bookmarks?
A: The Redshift checkpoint already tracks what's been processed. Two trackers would conflict.

Q: Why does the dashboard read live data from the GBFS API and history from Redshift?
A: Redshift is only as fresh as the last 30-minute batch, so it can't power a live map. The API gives fresh data, and Redshift gives the history.

Q: How do you pause the dashboard overnight without risking the pipeline?
A: Stop the EC2 instance with the CLI instead of terraform destroy, which could touch the pipeline resources in the same state. The public IP changes when it restarts.
