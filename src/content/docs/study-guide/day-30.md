---
title: Study Guide - Day 30
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 30: Delta Lake, Auto Loader and MLflow"
sidebar:
  order: 300
---

Study Guide - Day 30 (source: notes/Training 30.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Azure vs AWS.** Students found Azure + Databricks easier: on AWS a pipeline needed S3, EventBridge, Lambda, Glue, EMR and Redshift; on Azure you put data in ADLS and do most of the work inside Databricks. Organizations tend to prefer Snowflake, engineers tend to prefer Databricks. Having **opinions about frameworks** is an underrated interview quality: it shows hands-on experience.

**Profile Narratives.** Interviewers rarely ask table names, but you need a mental model of the tables. **Datadog** monitors infrastructure (throughput, lag, errors), not business data. **Airflow** schedules jobs, not data content, but it can halt downstream tasks based on a quality check (sensor, `ShortCircuitOperator`, a failing test task). A project that never launched is still a valid infrastructure story. PySpark is ETL, dbt is ELT and needs an engine (BigQuery). Keep one platform per project (not Databricks and Snowflake together). An LLM feature is a product for another team; follow **Occam's razor**, since anything you mention is fair game. **NVIDIA RAPIDS** (GPU Spark) is impressive but niche: is 4× the speed worth more than 2× the cost?

**Delta Lake Operations.** **MERGE** = an **upsert**: match source to target on a key, then update, insert or delete in **one atomic commit**. The source must have at most one row per key. **Time travel** queries an earlier version (`VERSION AS OF n`, `TIMESTAMP AS OF '...'`); all three open table formats support it. Delta keeps history **30 days** and files **7 days** after `VACUUM` by default; Snowflake's maximum is 90 days plus 7 days of Fail-safe. **RESTORE** rolls back by writing a **new commit**, so it shows in history. **VACUUM** deletes unreferenced old files and limits time travel. `LAG()` compares rows within one version; time travel compares whole versions.

**The Delta Demo.** Create a two-station table (version 0), `UPDATE` (version 1), read `VERSION AS OF 0`, a "production mistake" `UPDATE` with **no WHERE** (version 2), `DESCRIBE HISTORY` to find the last good version, `RESTORE ... TO VERSION AS OF 1`. Then `MERGE INTO ... USING ... ON ... WHEN MATCHED THEN UPDATE WHEN NOT MATCHED THEN INSERT`, run twice with no duplicates, and a CDC-style MERGE with `WHEN MATCHED AND op = 'DELETE' THEN DELETE`.

**Idempotency.** Running an operation once or many times gives the **same end state**, with no duplicates. Idempotent: keyed MERGE, partition overwrite, streaming with a checkpoint. Not idempotent: plain `INSERT` / append, `count = count + 1`. Evan: "memorize that word and its definition."

**CDC vs SCD (interview trap).** **CDC** (Change Data Capture) captures every change from a source as it happens: log-based (binlog, WAL, Debezium, AWS DMS) is best; timestamp polling misses hard deletes. Used for migrating **hot tables** and continuous replication. **SCD** (Slowly Changing Dimensions) stores long-term history in dimension tables. Type 0 keeps the original, Type 1 overwrites, **Type 2** closes the old row (`valid_to`, `is_current = false`) and inserts a new current row, Type 3 adds a previous-value column. CDC often feeds an SCD Type 2 MERGE.

**Auto Loader.** Incremental file ingestion in Databricks: `spark.readStream.format("cloudFiles").option("cloudFiles.format", "json")`. It finds only **new** files, remembers them in the **checkpoint**, and handles schema inference and evolution (`cloudFiles.schemaLocation`, `schemaEvolutionMode` default `addNewColumns`, `_rescued_data`). `writeStream` to Delta with `checkpointLocation` and `trigger(availableNow=True)` processes everything new, commits and stops: the cheap scheduled choice. Demo: 1230 rows, rerun still 1230, one new file → 1231.

**Checkpoints.** A fault-tolerance record of what was processed, so a restart resumes without loss or reloading: **exactly-once** with a Delta sink. One checkpoint per stream, never delete it casually (it reloads everything), keep it with the table. Checkpointing stops reprocessing the same **file**; deduplication stops the same **record** arriving in two files.

**Lakeflow Jobs.** Databricks' orchestrator: **tasks** (notebook, script, SQL, pipeline, dbt) in a DAG with dependencies, triggers, **retries**, timeouts and alerts. Evan first created an ETL pipeline by mistake (no Add task button), then a **Job** with two notebook tasks on serverless: Bronze+Silver, then Gold **depends on** it with **Run if: All succeeded**. If upstream fails, downstream is skipped (Upstream failed); **repair run** reruns only failed tasks. Transient failures (timeouts, throttling, capacity) can pass on retry; bugs won't. Job = orchestrator; ETL pipeline (DLT) = declarative framework. ADF and Jobs are separate schedulers.

**ETL vs ELT.** ETL isn't outdated. ELT is preferred for Bronze/Silver/Gold lakehouses and cloud warehouses; ETL fits simpler targets like Postgres/RDS, compliance masking before load, and existing pipelines that work.

**MLflow.** An **open-source** ML lifecycle platform created by Databricks: **Tracking** (experiments group **runs**; runs log **params**, **metrics**, **artifacts**), **Models** (flavors + signature), **Model Registry** (versioned, in Unity Catalog on Databricks), **Serving**, and **Tracing** for LLM apps (a tree of spans: inputs, outputs, tool calls, timings). MLflow records and deploys; your code trains. **Tabular ML** = traditional models (regression, random forest, gradient boosting) on rows and columns, unlike LLMs.

**The ML Demo.** Silver → features (station, hour, day of week) → `toPandas()` (pulls rows to the driver, so `limit` first) → time-based train/test split → `OneHotEncoder` + `RandomForestRegressor` → `with mlflow.start_run():` log params, MAE (10.07 bikes), RMSE (≥ MAE, punishes big misses) and the model. A random forest can do regression (predicting a number). **Fraud detection** is the classic narrative: streaming scoring, batch training. The data engineer's part of MLOps: pipelines, features, training data, infrastructure.

---

# Part 2: Cheat Sheet

## Delta SQL
- `DESCRIBE HISTORY t` · `SELECT * FROM t VERSION AS OF n` · `TIMESTAMP AS OF '...'`
- `RESTORE TABLE t TO VERSION AS OF n` · `VACUUM t [RETAIN n HOURS]`
- `MERGE INTO t USING s ON key WHEN MATCHED [AND ...] THEN UPDATE/DELETE WHEN NOT MATCHED THEN INSERT`
- `WHEN NOT MATCHED BY SOURCE THEN DELETE` · `UPDATE SET *` / `INSERT *`
- Retention: log 30 days · files 7 days · Snowflake max 90 + 7 Fail-safe

## Changes and History
- Idempotent: MERGE on key · partition overwrite · checkpointed stream
- CDC methods: log-based (best) · timestamp · trigger · Delta Change Data Feed
- SCD 0 keep · 1 overwrite · 2 new row + `valid_from/valid_to/is_current` · 3 previous column

## Auto Loader
- `readStream.format("cloudFiles").option("cloudFiles.format","json")`
- `cloudFiles.schemaLocation` · `schemaEvolutionMode` (addNewColumns, rescue, failOnNewColumns, none)
- `writeStream.option("checkpointLocation", ...).trigger(availableNow=True).toTable(...)`
- Triggers: default micro-batch · `processingTime` · `availableNow` · `once` (deprecated)

## Lakeflow Jobs
- Tasks · dependencies (DAG) · Run if: All succeeded (default) / All done / ...
- Retries · repair run · schedule / file arrival / table update / continuous triggers
- Job = orchestrator · ETL pipeline = declarative (`@dlt.table`) · ADF = separate scheduler

## MLflow
- Experiment → runs → params · metrics · artifacts · signature
- `set_tracking_uri("databricks")` · `set_registry_uri("databricks-uc")` · `set_experiment(path)`
- `with mlflow.start_run():` · `log_params` · `log_metric` · `mlflow.sklearn.log_model`
- Registry (UC) · serving · traces (`autolog()`, `@mlflow.trace`)
- MAE (avg error, target units) · RMSE ≥ MAE · overfitting · one-hot encoding

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What is Delta MERGE?
A: An upsert. It matches source rows to target rows on a key, then updates, inserts or deletes them, all in one atomic commit.

Q: What can make a MERGE fail?
A: The source having more than one row for the same key, which gives a "multiple source rows matched" error. Deduplicate the source first, for example with ROW_NUMBER.

Q: What is time travel?
A: Querying a table as it looked at an earlier version or timestamp, with VERSION AS OF or TIMESTAMP AS OF. It works because the transaction log keeps every version. Delta, Iceberg and Hudi all support it.

Q: How far back can Delta time travel go?
A: As long as the log and data files exist. By default history is kept 30 days and old files 7 days after VACUUM, and both are configurable. Snowflake's maximum is 90 days.

Q: What does RESTORE do?
A: It rolls a table back to an earlier version by writing a new commit that points to the old files. The restore shows up in the history, so nothing is erased.

Q: What's the difference between RESTORE, MERGE and VACUUM?
A: RESTORE rolls back to an old version, MERGE upserts new data, and VACUUM physically deletes old unreferenced files, which limits how far back you can time travel.

Q: Is time travel the same as the LAG function?
A: No. LAG is a read-only window function comparing rows within one version of the data. Time travel compares whole versions of the table at different points in time.

Q: How would you use time travel to find when bad records started?
A: Query older and older versions until you find one without the bad records, then use that version's timestamp from DESCRIBE HISTORY to see when the problem began.

Q: What is idempotency?
A: An operation is idempotent if running it once or many times gives the same end result, with no duplicates. Pipelines need it because jobs get rerun.

Q: Give examples of idempotent and non-idempotent writes.
A: A MERGE on a key, a partition overwrite and a checkpointed stream are idempotent. A plain INSERT or append with no key check, or count equals count plus one, are not.

Q: What is CDC?
A: Change Data Capture: recording every insert, update and delete from a source as it happens. It's used for migrating tables that are still being written to and for keeping a lake or warehouse in sync with an operational database.

Q: What's the best way to do CDC?
A: Log-based: read the database's transaction log, like the MySQL binlog or Postgres WAL, with a tool like Debezium or AWS DMS. Timestamp polling is simpler but misses hard deletes.

Q: What's the difference between CDC and SCD?
A: CDC captures changes from a source as they happen, in seconds or minutes. SCD stores the long-term history of dimension attributes in the warehouse. CDC often feeds an SCD Type 2 merge.

Q: What is SCD Type 2?
A: Each change closes the old row, setting valid_to and is_current false, and inserts a new current row. That keeps the full history, like every address a customer has had.

Q: What are SCD Types 0, 1 and 3?
A: Type 0 never changes the original value, Type 1 overwrites it with no history, and Type 3 adds a column holding the previous value.

Q: What problem does Auto Loader solve?
A: Incremental file ingestion. It picks up only new files in a folder, tracks which ones it loaded in a checkpoint, and handles schema inference and evolution, so you don't reread or duplicate files.

Q: How do you use Auto Loader?
A: readStream with format cloudFiles and the option cloudFiles.format set to the file type, like json. Then writeStream to a Delta table with a checkpoint location.

Q: What does trigger availableNow do?
A: It processes all the new data available, commits its progress and stops. It's the common choice for incremental batches run on a schedule.

Q: Why are checkpoints important?
A: They record what was processed, so after a crash or restart the stream resumes from the last committed batch with nothing lost and nothing loaded twice. With a Delta sink that's exactly-once.

Q: What's the difference between checkpointing and deduplication?
A: Checkpointing stops the same file or offset from being processed twice. Deduplication stops the same record from appearing twice, for example if it arrives in two different files.

Q: What happens if you delete an Auto Loader checkpoint?
A: Auto Loader forgets what it loaded and reloads every file, which creates duplicates.

Q: How does Auto Loader handle a new column?
A: In the default addNewColumns mode the stream stops once, records the new schema and works after a restart. Data that doesn't fit goes into the _rescued_data column.

Q: What is a Lakeflow Job?
A: Databricks' built-in orchestrator. It runs tasks like notebooks, pipelines, SQL or dbt in a DAG with dependencies, schedules, retries and alerts.

Q: What happens to downstream tasks when an upstream task fails?
A: With the default "All succeeded" setting they don't run and are marked upstream failed. You fix the problem and use a repair run to rerun only the failed tasks.

Q: Why might a failed task succeed on retry?
A: If the failure was transient, like a network timeout, API throttling, a capacity issue or a file still being written. A code bug or bad data will fail again.

Q: What's the difference between a Lakeflow Job and an ETL pipeline?
A: A Job is an orchestrator that runs any tasks in the order you set. An ETL pipeline, or DLT, is a declarative framework where you define tables and the engine works out the order, with expectations and automatic checkpoints.

Q: Are Databricks Jobs part of ADF?
A: No. They're two separate schedulers. Jobs run inside Databricks, while ADF orchestrates many Azure services and can call Databricks.

Q: Is ETL outdated?
A: No. ELT is preferred for lakehouses and cloud warehouses, but ETL still fits simpler targets like Postgres and pipelines that already work.

Q: What is MLflow?
A: An open-source platform for the machine learning lifecycle, created by Databricks. It tracks experiments and runs, packages models, keeps a versioned model registry and helps serve models.

Q: What's the difference between an experiment and a run?
A: An experiment groups attempts at one problem. A run is one training attempt with its own parameters, metrics and artifacts.

Q: What's the difference between a param, a metric and an artifact?
A: A param is an input setting you chose, like max depth. A metric is a measured result, like MAE. An artifact is a saved file, like the model itself or a plot.

Q: What are MLflow traces?
A: Step-by-step records of an LLM or agent app: each model call's input and output, tool calls, retrieval, timings and errors. They help you debug why the app answered the way it did.

Q: What is tabular ML?
A: Traditional machine learning on rows and columns, like regression, random forests and gradient boosting, predicting a number or a class. It's different from LLMs, which generate text.

Q: What's the difference between MAE and RMSE?
A: MAE is the average size of the error in the target's units, like off by 10 bikes. RMSE squares the errors first, so it punishes big misses more and is always at least as large as MAE.

Q: What does toPandas do, and what's the risk?
A: It converts a Spark DataFrame to a pandas DataFrame, pulling all the rows into the driver's memory. On big data that can crash the driver, so limit or sample first.

Q: What's a data engineer's role in MLOps?
A: Building the data pipelines and features, preparing training data, and deploying and running the infrastructure. Data scientists build the model itself.

Q: How does a fraud-detection pipeline work?
A: Transactions stream in through Kafka or Event Hubs, features are computed, and a served model flags each one as OK or suspicious in real time. Flagged ones notify the customer. Model training on historical data runs in batch.
