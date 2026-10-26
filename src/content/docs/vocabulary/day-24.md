---
title: Day 24 Vocabulary
description: Glossary of terms and definitions from the Training 24 notes.
sidebar:
  order: 24
---

Vocabulary — Study Guide Day 24

Source: notes/Training 24.md; walkthroughs/Walkthrough - Training 24 (Incremental Pipeline Homework).md

## Incremental Pipelines
- **Full refresh** — A pipeline that reprocesses all the data every run.
- **Incremental pipeline** — A pipeline that processes only what's new since the last successful run; best designed incremental from the start.
- **Batch window** — The start and end timestamps defining which data one run processes.
- **Half-open window [start, end)** — A window with an inclusive start and exclusive end, so back-to-back windows never double-count or skip a file.
- **Batch ID** — An identifier given to each run so every row can be traced to the run that loaded it.
- **Checkpoint** — A durable record of the last successfully completed batch, advanced only after the load and validations succeed.
- **Idempotent / Idempotency** — An operation that gives the same result whether run once or many times, so re-running a batch doesn't create duplicates.
- **Landing table** — A Redshift table where each new batch lands, tagged with `batch_id`, before being merged; it may contain duplicates.
- **Canonical table** — The deduplicated, authoritative table that landing data is merged into.
- **MERGE** — SQL statement that updates or skips rows that already exist and inserts only new ones; Redshift's syntax is stricter than Postgres or Snowflake.
- **INSERT … ON CONFLICT DO NOTHING** — Postgres idiom that skips rows that would violate a unique key, another idempotent-load technique.
- **Transaction** — A group of SQL statements applied all-or-nothing, so Gold is never half-updated.
- **COMMIT** — Ends a transaction and makes its changes permanent.
- **Referential integrity** — Every foreign key in a fact table points to an existing dimension row (no orphans).
- **Orphan key** — A fact row key with no matching dimension row.
- **Backfill** — Loading historical data that predates the incremental process.
- **Overlap window** — Starting each window some time (2 hours) before the last checkpoint to catch late-arriving files; deduplication makes it harmless.
- **Late-arriving data** — Records or files that show up after their time window was already processed.
- **Event time** — When something actually happened at the source.
- **Ingestion time** — When the data was saved by the ingestion step; the class windows use this (the filename timestamp).
- **Processing time** — When the pipeline processed the data.
- **At-least-once** — A guarantee that every record is processed, possibly more than once.
- **Exactly-once result** — Output that looks as if each record was processed once, achieved by merging on a stable key despite retries.
- **Decoupling** — Separating ingestion from processing so each runs on its own schedule.

## Redshift SQL Objects
- **Stored procedure** — A named block of SQL stored in the database, kind of like a function in a programming language, run with `CALL`.
- **CALL** — SQL command that runs a stored procedure with arguments.
- **CREATE OR REPLACE PROCEDURE** — Creates a stored procedure or updates an existing one; must run before `CALL`.
- **Wrapper procedure** — A new procedure that calls a working one and adds checks and checkpoint updates without changing the original.
- **GRANT** — SQL command giving a database user privileges such as `SELECT`, `INSERT`, `UPDATE`, `EXECUTE` or schema `USAGE`.
- **pg_user** — System table listing database users, used to find the exact name of an IAM-mapped user.
- **IAMR: user** — The Redshift database user automatically created for an IAM role, which has no table privileges until granted.
- **Redshift Data API** — An API that runs SQL against Redshift without a persistent connection (`ExecuteStatement`, `DescribeStatement`).
- **Query editor v2** — Redshift's browser SQL editor; it runs only highlighted text if anything is selected.

## Glue Job Details
- **Job arguments (--arguments)** — Parameters passed to a Glue job run, such as batch window and batch ID; the console Run button doesn't pass them.
- **Glue job bookmarks** — Glue's built-in tracking of which files a job has read; disabled here so it doesn't conflict with the Redshift checkpoint.
- **Glue connection** — A saved Glue configuration for reaching a data store such as Redshift.
- **Job run ID** — The identifier of one execution of a Glue job.
- **IAM policy simulator** — AWS tool that tests whether a principal is allowed an action, e.g. showing "implicit deny" vs "allowed".
- **Implicit deny** — The default IAM result when no policy explicitly allows an action.

## Step Functions
- **Execution** — One run of a Step Functions state machine.
- **start-execution** — AWS CLI command that starts a state machine execution.
- **Redrive** — Restarting a failed execution from the failed step, keeping successful steps' results.
- **Retry** — Automatic re-running of a step configured inside the state machine, unlike a manual redrive.
- **Graph view** — The console diagram where each state turns green (succeeded), red (failed) or blue (running).
- **.sync integration** — A Step Functions task pattern that waits for a Glue job to finish before moving to the next state.
- **Fire-and-forget** — Starting a task without waiting for it to finish, so the next step runs too early.
- **Coordinator Lambda** — A Lambda the workflow calls to prepare a batch (read checkpoint, compute window) and complete it (`CALL` the procedure).
- **Intrinsic functions** — Built-in Step Functions helpers for building values inside a definition; dynamic SQL built this way failed validation.
- **Overlap guard** — A check that prevents a new scheduled execution from starting while the previous one is still running.
- **Standard workflow** — A long-running Step Functions workflow type, used for this pipeline.

## Terraform Operations
- **Terraform state** — Terraform's record of which real resources belong to which blocks in your code; without it, Terraform assumes nothing exists.
- **terraform.tfstate** — The state file; always run Terraform from the directory that holds it.
- **terraform state list** — Lists the resources Terraform's state currently tracks.
- **terraform import** — Connects an existing AWS resource to a block in your code without changing it in AWS.
- **terraform plan -out / apply <file>** — Save a plan to a file and apply exactly that plan.
- **"No changes"** — The ideal plan result after an import, meaning code matches reality.
- **terraform fmt** — Formats Terraform files to standard style.
- **terraform validate** — Checks Terraform configuration for syntax and validity errors.
- **terraform output** — Prints output values, e.g. `-raw` for use in shell commands.
- **name_prefix** — Terraform argument that generates a unique name by appending a suffix to a prefix.
- **One-line block rule** — HCL allows single-line blocks only with a single argument; multiple arguments must be multi-line.
- **Configuration directory** — Terraform reads every `.tf` file in the current folder (not subfolders) as one configuration.
- **ARN (Amazon Resource Name)** — A resource's unique AWS identifier, kept unchanged when Terraform updates the state machine in place.

## Scheduling and Logging
- **EventBridge Scheduler** — AWS service that triggers targets on a schedule, here `rate(30 minutes)`.
- **rate expression** — EventBridge schedule syntax such as `rate(30 minutes)`.
- **Safe rollout** — Creating a schedule disabled, verifying it, then enabling it.
- **CloudWatch log group** — A container for related CloudWatch log streams, imported into Terraform here.
- **Inline policy** — A permission policy embedded directly in one IAM role.

## Dashboard on EC2
- **Streamlit** — Python library for interactive web dashboards; serves on port 8501 by default.
- **GBFS (General Bikeshare Feed Specification)** — The public API format Citi Bike publishes live station data in.
- **t3.small** — A small EC2 instance type used for the dashboard.
- **gp3** — A general-purpose SSD EBS volume type.
- **EBS (Elastic Block Store)** — Disk volumes attached to EC2; still billed while the instance is stopped.
- **Instance profile** — The container that attaches an IAM role to an EC2 instance so apps can call AWS without access keys.
- **/32** — A CIDR suffix meaning exactly one IP address.
- **User data** — A bootstrap script that runs on an EC2 instance's first boot.
- **venv (virtual environment)** — An isolated Python environment for a project's packages.
- **systemd service** — A Linux service definition that starts a program on boot and restarts it.
- **Systems Manager** — AWS service for managing and connecting to instances.
- **Stop vs terminate** — Stopping pauses an EC2 instance and keeps its disk; terminating deletes it.
- **Elastic IP** — A static public IP that survives stop/start; without one, the public IP changes.
- **describe-instances** — AWS CLI command that returns instance details such as the current public IP.
