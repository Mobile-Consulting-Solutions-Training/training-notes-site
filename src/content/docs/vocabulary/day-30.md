---
title: Day 30 Vocabulary
description: Glossary of terms and definitions from the Training 30 notes.
sidebar:
  order: 30
---

Vocabulary — Study Guide Day 30

Source: notes/Training 30.md

## Class Admin and Platform Comparisons
- **Professional profile narrative** — A conversational project story covering the business problem, architecture, your contributions, challenges and impact, prepared for interviews.
- **Elevator pitch** — A short spoken introduction of yourself and your experience, practiced for the start of an interview.
- **Microsoft Entra ID** — Azure's identity service for users and groups (formerly Azure Active Directory).
- **Managed identity** — An Azure identity assigned to a service so it can access other resources without stored credentials.
- **Storage Blob Data Contributor** — The Azure RBAC role that lets an identity read, write and delete data in a storage account.
- **Databricks vs. Snowflake** — The two main competing data platforms, which Evan said engineers and organizations respectively tend to prefer.

## Profile Narratives
- **Mental model of the tables** — Knowing roughly how your project's tables relate and where they live, even though interviewers rarely ask for table names.
- **Datadog** — An observability platform that monitors infrastructure and jobs (throughput, lag, errors) and alerts engineers, not a business analytics tool.
- **Observability** — Collecting metrics, logs and traces from systems so problems can be detected and fixed quickly.
- **Shard vs. partition** — Kinesis calls a stream's parallel unit a shard, while Event Hubs and Kafka call it a partition.
- **Airflow** — An open-source scheduler that decides whether and when tasks run; it doesn't inspect data content itself.
- **Airflow sensor** — An Airflow task that waits for a condition (a file, a check result) before downstream tasks continue.
- **ShortCircuitOperator** — An Airflow operator whose False result skips all downstream tasks, usable as a pipeline circuit breaker.
- **Trigger rule** — The Airflow setting (default `all_success`) that decides whether a task runs based on upstream results.
- **Circuit breaker / kill switch** — A pipeline control that halts downstream processing when a quality check or configuration flag says to stop.
- **Feature flag** — A configuration value that turns a feature or data flow on or off without a code change.
- **Malformed vs. incomplete data** — Malformed data breaks a processing job, while incomplete data flows through and is simply missing at the end.
- **Cloud Composer** — Google Cloud's managed Airflow service.
- **Pub/Sub** — Google Cloud's messaging and streaming ingestion service.
- **Dataflow** — Google Cloud's managed stream and batch processing service built on Apache Beam.
- **Dataproc** — Google Cloud's managed Hadoop/Spark cluster service, the equivalent of AWS EMR.
- **Google Cloud Storage (GCS)** — Google Cloud's object storage, the equivalent of S3 or ADLS.
- **BigQuery** — Google Cloud's serverless data warehouse, which can also serve as dbt's processing engine.
- **Apache Flink** — A stream processing engine used for real-time cleanup and transformation of event streams.
- **dbt** — A SQL transformation tool that always works ELT-style and needs a warehouse engine to run its models.
- **REST vs. GraphQL API** — Two API styles a pipeline may ingest from; REST uses fixed endpoints, GraphQL lets the client ask for specific fields.
- **Databricks on GCP** — Running Databricks on Google Cloud, letting Delta Lake hold Bronze/Silver with BigQuery as Gold.
- **LangChain** — A Python framework for calling LLMs and building the structure of AI apps, without Streamlit-style visualizations.
- **ChatOpenAI / chain.invoke** — LangChain's OpenAI chat model object and the call that runs a prompt-plus-model chain on user input.
- **S3 Vectors** — AWS vector storage built into S3 buckets, used for RAG embeddings.
- **pgvector** — A PostgreSQL extension that stores and searches vector embeddings.
- **Occam's razor (narratives)** — Keep the story as simple as possible, because anything you mention becomes fair game for follow-up questions.
- **NVIDIA RAPIDS** — NVIDIA's GPU data science libraries (2018), whose RAPIDS Accelerator for Apache Spark (2020) runs Spark SQL/DataFrame work on GPUs.
- **GPU Spark economics** — GPU clusters can be several times faster but cost much more per hour, so they only pay off for very large workloads.

## Delta Lake: MERGE, Time Travel, RESTORE
- **Delta Lake** — An open table format of Parquet files plus a transaction log that adds ACID transactions, versioning and schema enforcement.
- **Open table format** — A table layer over data lake files (Delta, Iceberg, Hudi) that adds transactions, versions and time travel.
- **Apache Hudi** — An open table format, alongside Delta and Iceberg, that supports upserts and time travel.
- **MERGE INTO** — A Delta SQL command that upserts (and optionally deletes) source rows into a target table on a key in one atomic commit.
- **Upsert** — Update a row if its key exists, otherwise insert it.
- **USING clause** — The part of MERGE that names the source table, view or subquery.
- **WHEN MATCHED / WHEN NOT MATCHED** — MERGE clauses that decide what to do when a key exists in both tables or only in the source.
- **WHEN NOT MATCHED BY SOURCE** — A MERGE clause that acts on target rows missing from the source, such as deleting them.
- **UPDATE SET * / INSERT *** — MERGE shortcuts that copy all columns when source and target share a schema.
- **Multiple source rows matched** — The MERGE error raised when the source has more than one row per key, fixed by deduplicating first.
- **Time travel** — Querying a table as it existed at an earlier version or timestamp.
- **VERSION AS OF** — Delta syntax to read a specific numbered table version.
- **TIMESTAMP AS OF** — Delta syntax to read the latest version committed at or before a given time, with no string conversion needed.
- **DESCRIBE HISTORY** — The Delta command listing every table version with its operation, user and timestamp.
- **delta.logRetentionDuration** — The table property (default 30 days) for how long Delta keeps table history.
- **delta.deletedFileRetentionDuration** — The table property (default 7 days) for how old unreferenced files must be before VACUUM removes them.
- **Snowflake Time Travel** — Snowflake's version of time travel, 1 day by default and up to 90 days on Enterprise edition.
- **Fail-safe** — Snowflake's extra 7 days after Time Travel during which only Snowflake support can recover data.
- **UNDROP TABLE** — A Snowflake command that recovers a dropped table within the Time Travel window.
- **LAG()** — A read-only window function that returns a value from a previous row in the same query result; it never changes data.
- **RESTORE TABLE** — A Delta command that rolls a table back to an earlier version by writing a new commit marked RESTORE.
- **VACUUM** — A Delta command that deletes unreferenced data files older than the retention period, which limits time travel.
- **UPDATE without WHERE** — The classic production mistake of changing every row, which the demo undid with RESTORE.
- **Idempotency** — The property that running an operation once or many times gives the same end result with no duplicates.
- **Idempotent** — The adjective for an operation, such as a keyed MERGE or checkpointed stream, that is safe to rerun.
- **CDC-style merge** — A MERGE that applies a change feed tagged insert/update/delete, using conditions like `WHEN MATCHED AND op = 'DELETE' THEN DELETE`.
- **AUTO CDC / APPLY CHANGES INTO** — The Lakeflow Declarative Pipelines feature that applies a CDC feed to a table automatically.
- **Change Data Feed** — A Delta table option that records row-level inserts, updates and deletes for downstream incremental processing.

## CDC vs. SCD
- **Change data capture (CDC)** — A set of techniques for recording every change to source data as it happens, used for replication and migrations.
- **Hot table** — A table still receiving writes from a live application while you migrate it.
- **Log-based CDC** — Capturing changes by reading the database's transaction log (binlog, WAL), the most reliable CDC method.
- **Debezium** — An open-source log-based CDC tool that streams database changes into Kafka.
- **AWS DMS** — AWS Database Migration Service, which migrates databases and can stream ongoing changes with CDC.
- **Timestamp-based CDC** — Polling for rows updated since the last run, which misses hard deletes.
- **Trigger-based CDC** — Using database triggers to write changes to an audit table, slowing down writes.
- **Slowly changing dimension (SCD)** — A method for storing the long-term history of dimension attributes in a warehouse.
- **SCD Type 0** — Keep the original attribute value and ignore changes.
- **SCD Type 1** — Overwrite the old value, keeping no history.
- **SCD Type 2** — Close the old row (valid_to, is_current = false) and insert a new current row for every change, keeping full history.
- **SCD Type 3** — Add a column holding the previous value, keeping one step of history.
- **valid_from / valid_to / is_current** — The SCD Type 2 columns that mark each row's effective period and which row is current.

## Auto Loader
- **Auto Loader** — Databricks' Structured Streaming source that incrementally ingests only new files from a folder.
- **cloudFiles** — The `format()` name that turns on Auto Loader in `spark.readStream`.
- **cloudFiles.format** — The Auto Loader option that sets the incoming file type, such as json or csv.
- **cloudFiles.schemaLocation** — The folder where Auto Loader stores the inferred schema and its changes.
- **cloudFiles.schemaEvolutionMode** — The Auto Loader setting (addNewColumns, rescue, failOnNewColumns, none) for handling new columns.
- **cloudFiles.useNotifications** — The Auto Loader option for file notification mode instead of directory listing on very large folders.
- **_rescued_data** — The column where Auto Loader puts values that don't fit the schema instead of dropping them.
- **UnknownFieldException** — The error that stops an Auto Loader stream once when a new column appears, before it restarts with the new schema.
- **multiLine** — The JSON reader option for files where one JSON object spans many lines.
- **recursiveFileLookup** — The reader option that also reads files in subfolders.
- **_metadata.file_path** — The hidden column giving each row's source file path, used for the source_file column.
- **NameError (undefined variable)** — The Python error from using a variable like source_path before defining it, fixed by running the defining cells first.
- **readStream** — The Spark API that creates a streaming DataFrame from a source.
- **writeStream** — The Spark API that writes a streaming DataFrame to a sink, batch after batch.
- **Streaming DataFrame** — A DataFrame whose rows keep arriving, processed as micro-batches.
- **toTable()** — The writeStream method that writes the stream into a named table.
- **awaitTermination()** — A call that blocks until the streaming query stops.
- **trigger(availableNow=True)** — A streaming trigger that processes all new data, commits progress and stops, for scheduled incremental batches.
- **trigger(processingTime)** — A streaming trigger that runs a micro-batch on a fixed interval indefinitely.
- **Checkpoint** — A folder recording a stream's processed files or offsets and committed batches so it can resume without loss or duplicates.
- **checkpointLocation** — The writeStream option naming the checkpoint folder, one per stream.
- **Exactly-once** — Each record affects the output exactly once, achieved by checkpoints plus a transactional sink like Delta.
- **Deduplication** — Removing repeated records by key, which checkpoints alone don't do when the same record arrives in two files.
- **Schema evolution** — Automatically handling added or removed columns in incoming data without breaking the pipeline.
- **Protobuf** — A schema-based binary format whose schema must be compiled before use.
- **Avro** — A schema-based binary format whose schema can change without a compile step.

## Lakeflow Jobs
- **Lakeflow Jobs** — Databricks' built-in orchestrator (formerly Workflows) that runs tasks in a dependency graph.
- **Jobs & Pipelines** — The Databricks sidebar page where you create Jobs and ETL pipelines.
- **Task** — One unit of work in a Job, such as a notebook, script, SQL query, pipeline or dbt run.
- **Notebook task** — A Job task that runs a workspace notebook on chosen compute, such as serverless.
- **Task dependency (Depends on)** — A link making one task wait for an upstream task, forming a DAG.
- **DAG (directed acyclic graph)** — The one-way chain of tasks and dependencies in a job.
- **Run if dependencies** — The Job setting (default All succeeded) that decides whether a task runs based on upstream results.
- **Upstream failed** — The status of a downstream task that was skipped because a task it depends on failed.
- **Retries** — A per-task setting that reruns a failed task a set number of times after a delay.
- **Repair run** — Rerunning only the failed tasks and those after them instead of the whole job.
- **Transient failure** — A temporary error, such as a timeout or throttling, that may succeed on retry.
- **Run now** — The button that triggers a Job immediately.
- **Job trigger** — What starts a job: a schedule, file arrival, table update or continuous mode.
- **ETL pipeline (Lakeflow Declarative Pipelines)** — A Databricks pipeline where you declare tables and the engine manages order, checkpoints and quality, with no Add task button.
- **Window function** — A function like ROW_NUMBER computed over a partition of rows, used in Gold to keep the latest snapshot per station per hour.
- **ROW_NUMBER() deduplication** — Numbering rows within each key and keeping row 1 to get one latest row per key.
- **Azure Data Factory (ADF)** — Azure's separate scheduler and copy service that can call Databricks notebooks or jobs.
- **Synapse Pipelines** — The ADF engine built into Azure Synapse.
- **ETL** — Transform data before loading it, still valid for simpler targets like Postgres and existing pipelines.
- **ELT** — Load raw data first and transform inside the platform, the preferred pattern for Bronze/Silver/Gold lakehouses.

## MLflow and Tabular ML
- **MLflow** — An open-source ML lifecycle platform, created by Databricks, for tracking runs, packaging and registering models, and serving them.
- **MLflow Tracking** — The MLflow component that logs each run's parameters, metrics and artifacts.
- **Experiment** — A named group of MLflow runs for one problem.
- **Run** — One training attempt logged in MLflow with its parameters, metrics and artifacts.
- **mlflow.start_run()** — The call that starts a new run so later log calls are recorded under it.
- **Parameter** — An input setting logged for a run, such as max_depth.
- **Metric** — A measured result logged for a run, such as accuracy or MAE.
- **Artifact** — A file saved with a run, such as the model, a plot or a feature list.
- **Model signature** — The recorded input columns and types and output type a model expects.
- **infer_signature** — The MLflow helper that builds a signature from sample inputs and predictions.
- **Integer columns warning** — An MLflow signature warning that integer columns can't hold missing values, fixed by casting to float.
- **mlflow.sklearn.log_model** — The call that saves a scikit-learn model as a run artifact.
- **Model flavor** — MLflow's per-library model format, such as sklearn or pytorch.
- **Model Registry** — A store of named, versioned models with aliases, living in Unity Catalog on Databricks.
- **databricks-uc registry URI** — The setting that makes MLflow register models in Unity Catalog.
- **Model serving** — Deploying a registered model as a REST endpoint for real-time predictions.
- **Batch predictions** — Scoring many rows at once, e.g. with `mlflow.pyfunc.spark_udf` on a Spark DataFrame.
- **mlflow server** — The command that runs a local MLflow tracking server and UI, by default on localhost:5000.
- **MLflow trace** — A record of each step an LLM or agent app took (calls, tool use, inputs, outputs, timings) for debugging.
- **Span** — One step inside an MLflow trace, such as a single LLM or tool call.
- **CrewAI** — An agentic AI framework where several AI agents with roles work and talk together.
- **Genie Code** — A Databricks AI assistant offered in notebooks for ML work.
- **MLOps** — Practices and infrastructure for training, deploying and monitoring ML models, using tools like MLflow.
- **Tabular ML** — Traditional machine learning on rows and columns, such as SQL tables or Spark DataFrames.
- **LLM (large language model)** — A model like ChatGPT or Claude that takes and returns natural language.
- **Traditional ML model** — A statistical model trained to predict a number or class from features.
- **Fraud detection pipeline** — A pipeline that scores card transactions in real time and flags suspicious ones for customer confirmation.
- **scikit-learn** — The standard Python library for traditional ML models.
- **PyTorch / TensorFlow** — Deep learning frameworks for building neural network models.
- **Features (X)** — The input columns a model learns from.
- **Target / label (y)** — The column a model predicts.
- **Train/test split** — Training on one part of the data and scoring on unseen data; time-based splits train on earlier data.
- **Regression** — Predicting a numeric value, which a random forest regressor also does.
- **Linear regression** — A model that fits a straight-line trend through the data.
- **Random forest** — An ensemble of decision trees trained on random samples, whose predictions are averaged.
- **One-hot encoder** — A transformer that turns a category into 0/1 columns, one per value.
- **ColumnTransformer / Pipeline** — scikit-learn tools that apply preprocessing to chosen columns and chain it with a model.
- **MAE (mean absolute error)** — The average size of prediction errors, in the target's units.
- **RMSE (root mean squared error)** — The square root of the average squared error, which penalizes large errors and is always at least the MAE.
- **Overfitting** — A model that fits training data so closely it performs badly on new data.
- **pandas DataFrame** — A single-machine in-memory table used by scikit-learn, unlike a distributed Spark DataFrame.
- **toPandas()** — The Spark method that collects a Spark DataFrame to the driver as a pandas DataFrame.
- **%pip install** — The notebook magic that installs a Python package into the notebook's environment.

## Unity Catalog
- **Unity Catalog** — Databricks' governance layer for permissions, lineage, auditing and discovery across workspaces.
- **Three-level namespace** — Unity Catalog's `catalog.schema.table` naming.
- **hive_metastore** — The legacy two-level Databricks metastore that Unity Catalog replaces.
- **Metastore** — The top-level Unity Catalog container, one per region, attached to workspaces.
- **Managed table** — A table whose storage location and lifecycle Unity Catalog controls.
- **External table** — A table whose data lives in your own storage path that Unity Catalog governs but doesn't own.
- **Volume** — A Unity Catalog object for governed files, addressed as `/Volumes/catalog/schema/volume/`.
- **Storage credential / external location** — Unity Catalog objects that let it reach your cloud storage through an identity.
- **GRANT** — The SQL command that gives a user or group a privilege such as SELECT on a securable object.
- **Lineage** — Automatic tracking of which jobs and notebooks read and wrote which tables and columns.
- **Row filter** — A function attached to a table that hides rows depending on who is querying.
- **Column mask** — A function attached to a column that masks its values depending on who is querying.
