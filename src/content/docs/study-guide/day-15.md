---
title: Study Guide - Day 15
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 15: Cloud Platforms and Snowflake"
sidebar:
  order: 150
---

Study Guide - Day 15 (source: notes/Training 15.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Unified Data Platform.** Handles ingestion, storage, processing, analytics, ML and governance in one place on one shared copy of the data, instead of a chain of tools that each keep a copy (the Postgres → Spark → Hive → Kafka → MongoDB chain from class). Features: single storage layer in open formats, batch and streaming together, many workloads, unified governance, storage separate from compute. Examples: Databricks (Lakehouse, Unity Catalog), Snowflake (AI Data Cloud), Microsoft Fabric (OneLake), BigQuery, AWS. Trade-offs: lock-in, usage costs, less control.

**AWS, Azure, GCP.** Same building blocks, different names. Object storage: S3 / Blob & ADLS Gen2 / GCS. Warehouse: Redshift / Synapse & Fabric / BigQuery. Spark: EMR & Glue / HDInsight & Databricks / Dataproc. Streaming: MSK & Kinesis / Event Hubs / Pub/Sub. Orchestration: Glue, Step Functions, MWAA / Data Factory / Cloud Composer. Catalog: Glue Data Catalog & Lake Formation / Purview / Dataplex. VMs: EC2 / Azure VMs / Compute Engine.

**Object Storage.** For long-term persistent data; **serverless**; data lives as objects in **buckets** with a key, data and metadata. Buckets have either a **simulated filesystem** (S3: folders are just key prefixes) or an **actual filesystem** (ADLS Gen2 with hierarchical namespace: real directories). Renaming a folder on flat storage copies every object (slow, not atomic); on a real filesystem it's one atomic metadata change, which matters because Spark/Hive commit by renaming. Delta/Iceberg avoid relying on renames with a transaction log. Cheap, ~unlimited, 11 nines durability, no editing in place. Object vs file vs block storage.

**S3, Blob, ADLS Gen2, GCS.** ADLS Gen2 = Blob Storage + hierarchical namespace, with POSIX-style ACLs. GCS has storage classes Standard → Nearline → Coldline → Archive. Spark paths: `s3a://`, `abfss://`, `gs://`.

**Remote Instances.** A VM hosted in the cloud: EC2, Azure Virtual Machines, Google **Compute Engine**. (Evan listed App Engine, but that's PaaS: upload code, Google runs it.) IaaS = you manage OS and up; PaaS = you manage code; SaaS = you just use it (Snowflake).

**EBS.** Elastic Block Store: persistent block storage attached to an EC2 instance, the VM's virtual hard drive. Survives stops (unlike instance store), lives in one Availability Zone, backed up with **snapshots**. Types: gp3 (default SSD), io2 (provisioned IOPS), st1 (throughput HDD), sc1 (cold). EBS for OS drives, databases and Kafka logs; S3 for the lake; EFS for shared files.

**Cortex Code (CoCo).** Snowflake's agentic AI assistant in Snowsight (lower-right icon): writes, explains and fixes SQL (shown as a diff), discovers data and lineage (`@` to add objects), answers cost and governance questions, builds notebooks and dbt projects. Needs `SNOWFLAKE.COPILOT_USER` plus `CORTEX_USER` or `CORTEX_AGENT_USER`; trials need a credit card. Runs under your RBAC, starting with your **default role**. Review suggestions; usage costs credits.

**Workspaces.** An isolated virtual location in Snowflake or Databricks that holds a project's resources separately from others. Snowflake Workspace = in-browser file-based IDE (SQL, Python, notebooks, dbt; Git; replaces Worksheets; each file runs with a role and warehouse). Databricks Workspace = the top-level environment (notebooks, jobs, clusters, repos), often one each for dev/test/prod; data governed by Unity Catalog.

**Semantic Views.** A Snowflake object that stores business meaning next to the tables: logical tables, relationships, facts, dimensions, metrics, synonyms. Query with `SEMANTIC_VIEW(... DIMENSIONS ... METRICS ...)` and Snowflake writes the joins. Gives one definition of each metric and better AI answers (Cortex Analyst). Built on the Gold star schema. The general idea is a semantic layer (dbt Semantic Layer, LookML, Power BI).

**Snowflake Processing.** Compute separate from storage: **virtual warehouses** (standard, Snowpark-optimized, multi-cluster; X-Small → 6X-Large, each size doubles; auto-suspend/resume) or serverless compute. Features: SQL (`MERGE`, CTAS), Snowpark, UDFs/procedures, **Streams** (change data capture), **Tasks** (scheduled SQL, DAGs), **Dynamic Tables** (query + `TARGET_LAG`), Snowpipe / Snowpipe Streaming, Container Services, Cortex AI functions. Legal sense: the company is the data controller, Snowflake the data processor.

**Snowpark.** Snowflake's code execution environment: Python/Java/Scala DataFrames that run on Snowflake warehouses next to the data, lazily, translated to SQL. **Snowpark Connect for Apache Spark** runs existing PySpark against Snowflake. No cluster or connector headaches.

**dbt.** The main ELT tool with Snowflake: the **T** inside the warehouse. A **model** is a `.sql` SELECT materialized as a view, table, incremental table or ephemeral CTE; `ref()` builds the dependency DAG; Jinja templating; tests (`unique`, `not_null`, `relationships`, `accepted_values`); incremental models; `dbt docs generate`. Commands: `dbt run`, `dbt test`, `dbt build`. dbt Core (CLI), dbt Cloud, dbt Projects on Snowflake. Install `dbt-core` plus one **adapter** per platform, inside a venv (Python 3.12 here).

**Snowflake from the Command Line.** Snowflake CLI `snow` (current), SnowSQL (older). `snow connection add/test`, `snow sql -q/-f`, `snow stage copy` to an internal stage before `COPY INTO`. Install command-line **apps** with **pipx** or `uv tool install`, not into a project venv: installing snowflake-cli inside the dbt venv downgraded `click` and `protobuf` and broke dbt. A red dependency-conflict block means something may be broken even though pip said "Successfully installed"; check with `pip check`.

---

# Part 2: Cheat Sheet

## Platforms
- Unified platform = one copy of data for every workload · Databricks · Snowflake · Fabric
- AWS / Azure / GCP: S3 / ADLS / GCS · Redshift / Synapse / BigQuery · EMR / HDInsight / Dataproc

## Storage
- Object (bucket, HTTP, cheapest) · File (folder tree) · Block (disk, EBS)
- S3 = simulated folders · ADLS Gen2 = real directories, atomic rename
- `s3a://` · `abfss://` · `gs://`
- EBS: persistent, one AZ, snapshots, gp3 default

## Compute Models
- IaaS (EC2, Compute Engine) · PaaS (App Engine, Beanstalk) · SaaS (Snowflake)

## Snowflake UI and AI
- CoCo: agentic, diffs, `@` objects · roles COPILOT_USER + CORTEX_(AGENT_)USER · default role
- Workspaces: isolated projects · Snowflake IDE vs Databricks top-level env
- Semantic view: tables, relationships, facts, dimensions, metrics → `SEMANTIC_VIEW(...)`

## Snowflake Processing
- Warehouses: standard, Snowpark-optimized, multi-cluster · sizes double · auto-suspend
- Streams (CDC) · Tasks (schedule) · Dynamic Tables (`TARGET_LAG`) · Snowpipe
- Snowpark: lazy DataFrames inside Snowflake · Snowpark Connect for PySpark

## dbt
- ELT "T" · model = SELECT · `ref()` → DAG · Jinja · tests · incremental
- `dbt run` / `test` / `build` / `docs generate` · core + adapter in a venv

## CLI Tools
- `snow connection add` · `snow sql -q` · `snow stage copy`
- Apps → pipx / `uv tool install` · libraries → project venv · `pip check`

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What is a unified data platform?
A: A platform that handles ingestion, storage, processing, analytics, ML and governance on one shared copy of the data, instead of a chain of separate tools that each keep their own copy. Databricks and Snowflake are examples.

Q: What are the trade-offs of a unified platform?
A: Vendor lock-in, usage-based costs that can grow quickly, and less low-level control than running each tool yourself. Open table formats reduce the lock-in.

Q: What's the object storage service on each major cloud?
A: S3 on AWS, Blob Storage and ADLS Gen2 on Azure, and Cloud Storage on GCP.

Q: What does it mean that object storage is serverless?
A: You never provision or manage a server. You create a bucket, read and write over an HTTP API, and pay for what you store and the requests you make.

Q: What's the difference between a simulated and an actual filesystem in a bucket?
A: In S3, folders are just prefixes in object keys, so they're simulated. ADLS Gen2 with the hierarchical namespace has real directories, so renaming a folder is one instant, atomic operation instead of copying every object.

Q: Why does atomic rename matter for Spark?
A: Spark and Hive write to a temporary folder and rename it into place on commit. On flat storage that rename is a slow copy, and a crash halfway leaves partial data.

Q: What's the difference between object, file and block storage?
A: Object storage is a flat bucket accessed over HTTP, cheap and practically unlimited. File storage is a folder tree like a network drive. Block storage is a raw disk attached to a server, like EBS, used for operating systems and databases.

Q: What is EBS?
A: Elastic Block Store, persistent block storage attached to an EC2 instance, like its hard drive. It survives restarts, lives in one Availability Zone, and is backed up with snapshots.

Q: When do you use EBS versus S3?
A: EBS for things that need a disk with in-place updates, like an OS drive, a database or Kafka broker logs. S3 for data lake files, backups and Parquet.

Q: What's the difference between IaaS, PaaS and SaaS?
A: With IaaS, like EC2, you rent a machine and manage the OS and software. With PaaS, like App Engine, you only upload code. With SaaS, like Snowflake, you just use the product.

Q: What is Cortex Code?
A: Snowflake's agentic AI assistant in Snowsight. It writes and fixes SQL, explores data and lineage, answers cost and governance questions, and builds notebooks and dbt projects, all within your role's permissions.

Q: What is a workspace in Snowflake or Databricks?
A: An isolated virtual location that holds a project's resources, like code, notebooks and files, separately from other projects, so teams and environments don't interfere with each other.

Q: What is a semantic view?
A: A Snowflake object that defines the business meaning of data: which tables join, what the dimensions are, and how metrics like revenue are calculated. Everyone, including BI tools and AI, then gets the same answer for the same question.

Q: What types of virtual warehouse does Snowflake have?
A: Standard for normal SQL and loading, Snowpark-optimized for memory-heavy Python or ML work, and multi-cluster for many concurrent users. Each size up roughly doubles power and cost, and they auto-suspend when idle.

Q: What are Streams and Tasks in Snowflake?
A: A Stream tracks changes on a table, like change data capture. A Task runs SQL on a schedule and can be chained into a pipeline. Together they can run Bronze to Silver to Gold inside Snowflake.

Q: What is Snowpark?
A: Snowflake's code execution environment. You write DataFrame code in Python, Java or Scala, and it runs on Snowflake's warehouses next to the data instead of on a separate Spark cluster.

Q: What does dbt do?
A: It's the transform step in ELT. You write SQL SELECT models, and dbt builds them as tables or views inside the warehouse in the right order, with tests, documentation and lineage.

Q: What does ref do in dbt?
A: It references another model, which tells dbt the build order and lets it draw the lineage graph automatically.

Q: Why install the Snowflake CLI with pipx instead of into the dbt venv?
A: Installing it into the dbt venv downgraded shared libraries and broke dbt. pipx gives a command-line app its own private environment. Apps go in pipx, project libraries go in the project's venv.

Q: pip says "Successfully installed" but prints a dependency conflict block. What does that mean?
A: The install worked, but another package in that environment may now be broken. Run pip check and fix the conflicting versions.
