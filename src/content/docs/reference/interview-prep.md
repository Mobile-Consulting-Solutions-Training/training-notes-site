---
title: Interview Prep
description: Start here for interviews - the traps to unlearn, how data engineering interviews run, the question bank by topic, and every day's interview-ready answers.
sidebar:
  order: 11
---

Everything on the site that's aimed at interviews, in one place. Work through it in this order: the traps below, then the question bank for the stack the job uses, then [Flashcards](/training-notes-site/reference/flashcards/) out loud.

## How the interviews run

From class (Trainings 29 and 30):

| Stage | What happens | How to prepare |
|---|---|---|
| Screening | Often automated or AI-led; basic fit and background | Have a 60-second summary of your profile ready |
| Round 1 | Quiz-style technical questions: Spark, SQL, Python, cloud services | The question bank below and the flashcards |
| Rounds 2 and 3 | A technical person asks about your **last project**: what you built, the problems, the fixes. This round usually decides the job | Real problem-and-fix stories. Rebuild your profile project small so you can describe it naturally |
| Live coding | Usually basic Python or SQL | The [code library](/training-notes-site/reference/code-python/) and the SQL window-function patterns |

| Advice | Why |
|---|---|
| Have opinions about tools ("Databricks vs Snowflake") | It shows hands-on experience |
| Keep the story simple (Occam's razor) | Anything you mention is fair game for follow-ups |
| Know your tables at a high level | You won't be asked table names, but you need a mental model of how they relate |
| Security questions usually mean **data governance** | Masking, roles and permissions (Unity Catalog, policy tags) |
| One bad interview doesn't end anything | Treat each one as practice for the next |

## Traps to unlearn

The class answers that are most likely to be wrong in an interview. Each is explained in full in the question bank.

These are the corrections most likely to come up in an interview. Each one is explained under its question below.

| Topic | Raw answer says | Correct answer |
|---|---|---|
| Spark task scheduling | The cluster manager sends tasks to executors | The **driver** schedules tasks. The cluster manager only allocates resources |
| Lazy evaluation | Runs at "a shuffle or action" | Only an **action** triggers execution |
| Client vs cluster mode | Client mode = laptop testing | Deploy mode = **where the driver runs**. Laptop testing is **local mode** |
| Broadcast join size | Under 5 GB | Default auto threshold **10 MB**, hard cap 8 GB, practical tens to hundreds of MB |
| Shuffle | Changes the order of rows | **Redistributes data across partitions** over the network, writing shuffle files |
| Skew fix in AQE | Dynamic Partition Pruning | **Skew join optimization**. DPP is a different feature |
| Salting | Fixed values every x rows | **Random** suffix 0..N-1 on the hot key, then a two-stage aggregation or exploded join |
| RDD resilience | Resumes a failed job on rerun | Lineage **recomputes lost partitions during the job**. Resuming needs checkpointing |
| Kafka consumer group | One consumer reads one partition | **Each partition goes to one consumer per group**; a consumer can read many |
| Kafka replication default | 3 | Broker default is **1**; 3 is the production recommendation |
| Kafka leaders | One leader node for the cluster | Leaders are **per partition**, chosen by the **controller** from the ISR |
| ZooKeeper | KRaft is optional | **Kafka 4.0 removed ZooKeeper**; KRaft only |
| Secondary NameNode | A backup that can take over | Only **checkpoints**. Failover is the **Standby NameNode** (HA) |
| Small file problem | Each file fills a 128 MB block | Files use real size on disk; the cost is **NameNode memory** and one task per file |
| Spark vs MapReduce | Spark never touches disk | Spark still uses disk for shuffles and spills; it avoids **HDFS writes between stages** |
| GIL | Multithreading isn't allowed | Threads are allowed; only **one thread runs Python bytecode at a time** |
| multiprocessing | Runs across a cluster | Separate processes **on one machine**. Clusters need Spark, Dask or Ray |
| SQS | Not scalable | Scales to very high throughput; the difference is **queue vs replayable log** |
| Redshift Spectrum | Uses your cluster's compute | Runs on a **separate AWS-managed fleet**, billed per TB scanned |
| Cassandra ring | Each node linked to two neighbors | A **token ring from consistent hashing**; any node talks to any node |

## Question bank

The full question bank, with the class answer, a corrected expanded answer, and a short answer to say out loud:

- [Big Data](/training-notes-site/reference/interview-big-data/)
- [Programming and SQL](/training-notes-site/reference/interview-programming/)
- [Cloud and DevOps](/training-notes-site/reference/interview-cloud-devops/)
- [Platforms and Behavioral](/training-notes-site/reference/interview-platforms-behavioral/)

## Interview-ready answers by day

The one-line answers at the end of each day's notes.

### [Training 24](/training-notes-site/notes/training-24/)

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

### [Training 27](/training-notes-site/notes/training-27/)

| Question | Your one-line answer |
|---|---|
| Blob Storage vs ADLS Gen2? | ADLS Gen2 is Blob Storage with a hierarchical namespace: real directories, atomic renames and POSIX ACLs, so it's the data-lake choice |
| What is a hierarchical namespace? | Real directories in object storage, so directory operations are single metadata operations instead of copying every object |
| Why does atomic rename matter for Spark? | Spark commits output by renaming a temp folder; on flat storage that's thousands of copy+deletes and not atomic |
| How do you make a storage account ADLS Gen2? | Create a StorageV2 account with hierarchical namespace enabled (`--hns true` or the Advanced-tab checkbox) |
| What is the ADLS Gen2 path format? | `abfss://<container>@<account>.dfs.core.windows.net/<path>` |
| What is Entra ID? | Microsoft's cloud identity service (formerly Azure AD) for users, groups, service principals and managed identities |
| Entra ID vs Azure RBAC? | Entra ID authenticates who you are; RBAC role assignments (principal + role + scope) authorize what you can do |
| Tenant vs subscription? | A tenant is the organization's Entra ID directory; subscriptions inside it are billing and access containers for resources |
| What is a resource group? | A management and lifecycle container for related resources; delete it and everything inside goes too (not a network like a VPC) |
| What is a managed identity? | An Entra identity Azure creates for a resource, with credentials Azure manages, so no secrets in code |
| AWS → Azure: Kinesis, EC2, Step Functions, Redshift? | Event Hubs, Virtual Machines, Data Factory, Synapse |
| What are the open table formats? | Delta Lake, Apache Iceberg and Apache Hudi: Parquet data plus a metadata/transaction log that adds ACID, schema evolution and time travel |
| Delta vs Iceberg? | Delta is Databricks' native format (`_delta_log`); Iceberg is the vendor-neutral format used by Snowflake, AWS, BigQuery and Trino |
| What does Unity Catalog do? | Central governance for Databricks: one metastore shared across workspaces with permissions, auditing and lineage on catalogs, schemas, tables and volumes |
| Dev, UAT, prod? | Separate environments for development, user acceptance testing, and live business workloads |
| What is Photon? | Databricks' C++ vectorized engine that speeds up SQL and DataFrame operations, falling back to Spark for unsupported operators |
| Do you need a SparkSession in Databricks? | No, `spark` is predefined in every notebook |
| Synapse vs Databricks? | Synapse combines SQL warehouse, Spark pools and pipelines; many teams now use Databricks (or Fabric) for Spark and lakehouse work |
| What is Microsoft Fabric? | Microsoft's SaaS all-in-one analytics platform on OneLake: Data Factory, Spark, warehouse, real-time and Power BI with Copilot |

### [Training 28](/training-notes-site/notes/training-28/)

| Question | Your one-line answer |
|---|---|
| What is a Copy activity in ADF? | The basic ADF activity that copies data from a source dataset to a sink dataset, optionally converting format, with no real transformation |
| Linked service vs dataset? | A linked service is the connection and authentication to a system; a dataset points to specific data (path, file, format) inside it |
| What is an integration runtime? | The compute that runs ADF activities and moves the data: Azure IR (managed), self-hosted IR (on-prem/private networks), or Azure-SSIS IR |
| Why a managed identity for ADLS? | Azure manages the identity's credentials, so no keys are stored; you just grant it an RBAC role like Storage Blob Data Contributor |
| Why did the connection fail right after granting the role? | Azure RBAC role assignments take a few minutes to propagate |
| ADF or DMS for a migration? | DMS (Database Migration Service) for moving whole databases with little or no transformation; ADF for pipelines and moderate data copies; AzCopy / Data Box for bulk files |
| How does Databricks reach ADLS under Unity Catalog? | Access Connector (managed identity) → Storage Blob Data role → storage credential → external location → external volume or tables |
| External vs managed volume? | External: files stay in your ADLS path governed by UC; managed: files live in UC's managed storage |
| What does `explode` do? | Turns each element of an array column into its own row; `struct.*` then turns struct fields into columns |
| Bronze, Silver, Gold? | Raw data plus load metadata; cleaned, typed, deduplicated data; business-level aggregates |
| What does Delta add over plain Parquet/JSON? | ACID transactions, schema enforcement, a transaction log with version history (time travel), MERGE/UPDATE/DELETE |
| How do you keep the latest row per key? | `row_number()` over a window partitioned by the key, ordered by timestamp desc, then filter `rn = 1` |
| Databricks vs Spark? | Spark is the open-source engine; Databricks is a managed platform around it with notebooks, Delta, Unity Catalog, jobs and serverless compute |
| Is Azure Databricks different from Databricks on AWS? | The notebook and Spark code are the same; only the cloud integration and authorization setup differ |

### [Training 29](/training-notes-site/notes/training-29/)

| Question | Your one-line answer |
|---|---|
| Explain the Delta transaction log | JSON commits plus Parquet checkpoints in `_delta_log`; readers see only committed versions, which gives ACID and time travel |
| OPTIMIZE vs Z-ORDER vs liquid clustering | Compaction; co-location on filter columns; incremental, changeable clustering that replaces partitioning + Z-ORDER |
| VACUUM risk | Deletes unreferenced files older than 7 days by default, so time travel past that breaks |
| Delta MERGE / SCD2 | MERGE on the business key; for SCD2, close the current row and insert the new version in one MERGE |
| Schema enforcement vs evolution | Mismatched writes are rejected by default; `mergeSchema` / autoMerge adds new columns on purpose |
| Auto Loader vs COPY INTO | Both incremental; Auto Loader streams, scales to millions of files and evolves schema |
| What is Lakeflow? | Databricks' umbrella for Connect (ingestion), Declarative Pipelines (formerly DLT) and Jobs (orchestration) |
| Table vs view vs materialized view | Table stores data; view stores only a query; materialized view stores the query's results until refreshed |

### [Training 30](/training-notes-site/notes/training-30/)

| Question | Your one-line answer |
|---|---|
| What is Delta MERGE? | An upsert: match source rows to the target on a key, then update, insert or delete in one atomic commit |
| What is time travel? | Querying a table as it was at an earlier version or timestamp (`VERSION AS OF` / `TIMESTAMP AS OF`), using the Delta log. Delta, Iceberg and Hudi all support it |
| How far back can Delta time travel go? | As long as the log and data files exist: history 30 days and files 7 days after VACUUM by default, configurable. Snowflake caps at 90 days |
| RESTORE vs. MERGE vs. VACUUM? | RESTORE rolls back to an old version (as a new commit); MERGE upserts new data; VACUUM deletes unreferenced old files and limits time travel |
| What is idempotency? | Running an operation once or many times gives the same result, with no duplicates. Needed for pipelines that can rerun (MERGE, checkpoints, partition overwrite) |
| CDC vs. SCD? | CDC captures every change from a source as it happens (replication, migrations). SCD stores long-term history of dimension attributes in the warehouse. CDC often feeds an SCD Type 2 MERGE |
| What is SCD Type 2? | Each change closes the old row (`valid_to`, `is_current = false`) and inserts a new current row, keeping full history |
| What does Auto Loader solve? | Incremental file ingestion: `cloudFiles` picks up only new files in a folder, tracks them in a checkpoint, and handles schema inference and evolution |
| Why checkpoints? | They record what was processed, so a restart resumes without loss or reloading, giving exactly-once with a Delta sink |
| What does `availableNow=True` do? | Processes all new data, commits progress and stops: incremental batch on a schedule |
| What is a Lakeflow Job? | Databricks' orchestrator: tasks (notebooks, pipelines, SQL…) in a DAG with dependencies, schedules, retries and alerts |
| What if an upstream task fails? | With "All succeeded", downstream tasks don't run (upstream failed). Fix and use repair run to rerun only failed tasks |
| Databricks Jobs vs. ADF? | Two different schedulers. Jobs run inside Databricks; ADF orchestrates many Azure services and can call Databricks |
| Is ETL outdated? | No. ELT is preferred for lakehouses; ETL still fits simpler targets like Postgres and existing pipelines that work |
| What is MLflow? | Open-source ML lifecycle platform (made by Databricks): tracking experiments and runs, model packaging, a versioned registry and serving |
| Experiment vs. run; param vs. metric vs. artifact? | An experiment groups runs; a run is one training attempt. Params are inputs, metrics are measured results, artifacts are saved files like the model |
| What is the Model Registry? | A versioned, governed store of named models (in Unity Catalog on Databricks) used to promote and serve models |
| What are MLflow traces? | Step-by-step records of an LLM/agent app's calls (inputs, outputs, tool calls, timings) for debugging why it answered what it did |
| What's a data engineer's role in MLOps? | Build the data pipelines and features, prepare training data, deploy and run the infrastructure; data scientists build the model |
| What is Unity Catalog? | Databricks' governance layer: `catalog.schema.table`, GRANTs, lineage, auditing, row filters and column masks |

### [Training 31](/training-notes-site/notes/training-31/)

| Question | Your one-line answer |
|---|---|
| What is MPP? | Massively parallel processing: a shared-nothing architecture where data is spread across nodes, each node processes its slice in parallel, and a leader combines results. It's what Redshift, Snowflake, Synapse and Databricks use |
| What's the Azure equivalent of Redshift? | Azure Synapse (dedicated SQL pool for provisioned MPP; serverless SQL pool is closer to Athena / Spectrum) |
| Serverless vs dedicated SQL pool? | Serverless: query files in ADLS, pay per TB processed, nothing to manage. Dedicated: a provisioned MPP warehouse, billed per hour, must be paused |
| How do you keep serverless query costs down? | Parquet, select only the columns you need, partition pruning, smaller Gold tables (CETAS), and a cost-control limit |
| Why convert JSON to Parquet before the warehouse? | SQL engines want flat, typed columns. Parquet is columnar and compressed, so queries are simpler, faster and cheaper |
| What's a VPS? | A virtual private server, a VM in the cloud (like EC2) from any provider |
| GDPR / CCPA? | EU and California data-privacy laws. They affect where personal data is stored and how it's handled (data residency) |
| How do you pick an analytics platform? | Start from the business need, data size, budget and existing infrastructure. "The best platform is the one that provides what the business needs in the way the business needs it" |
| What is MinIO / DuckDB / Iceberg? | MinIO: S3-compatible on-prem object storage. DuckDB: in-process OLAP SQL engine. Iceberg: an open table format (ACID, snapshots) that needs a catalog |
