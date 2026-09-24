---
title: Combined (Days 1-5) Vocabulary
description: Consolidated glossary of terms and definitions spanning Training 0 through Training 5.
---

Vocabulary — Study Guide Combined (Days 0-5)

# Day 0: Data Engineering Fundamentals

## Hardware Basics
- **ROM** — Non-volatile, read-only memory, used for firmware/boot.
- **RAM** — Volatile, fast memory for active working data.
- **In-memory computing** — Processing in RAM instead of touching disk every step; why Spark is ~10-100x faster than MapReduce.
- **Spilling** — Falling back to disk when RAM runs out.
- **CPU** — General-purpose processor.
- **GPU** — Specialized for matrix multiplication (graphics/pixel matrices, ML/numeric matrix math); irrelevant for everyday Spark work, critical for AI/ML.
- **x86** — Complex instruction set architecture, more power/cooling required.
- **ARM** — Simpler, power-efficient architecture, dominant in mobile and increasingly in data centers.

## Distributed Systems
- **CAP theorem** — A distributed system can only fully guarantee 2 of Consistency / Availability / Partition-tolerance.
- **Compute cluster** — At least 3 networked computers on a LAN/router working on the same task.
- **Peer-to-peer network** — Works over the raw internet instead of a LAN (e.g. BitTorrent, SETI); less secure than a compute cluster.
- **Shuffle** — Expensive network data movement between nodes in a distributed system.

## HDFS
- **HDFS (Hadoop Distributed File System)** — Splits files into blocks (default 128MB), replicates each (default 3x) across DataNodes for fault tolerance.
- **NameNode** — Tracks HDFS metadata (which blocks live where).
- **Write-once, read-many** — HDFS's access pattern; poor for small files or low-latency random access.

## Processing Engines
- **Batch engines** — Spark, Hadoop MapReduce.
- **Stream engines** — Flink, Kafka Streams, Spark Structured Streaming.
- **Query/SQL engines** — Presto/Trino, Hive, Athena.
- **Unified engines** — Spark, Flink, Beam (handle both batch and streaming).

## Apache Spark
- **Driver** — Builds the DAG and schedules tasks.
- **Cluster Manager** — Allocates nodes (YARN/Kubernetes/Mesos).
- **Executors** — Run tasks in parallel, cache data in-memory.
- **Job** — Triggered by an action like `.save()`/`.count()`.
- **Stages** — Job subdivisions, split at shuffle boundaries (e.g. `groupBy`/`join`).
- **Tasks** — Stage subdivisions, one per partition, run in parallel.
- **DataFrame** — Structured, Catalyst-optimized data structure built on top of RDD.
- **RDD** — Spark's original core data structure.
- **Lazy evaluation** — Transformations build a DAG but don't execute until an action triggers it.

## Hive
- **Hive** — An old OLAP data warehouse on top of Hadoop/HDFS; HiveQL historically translated into (slow) MapReduce jobs.
- **Hive Metastore** — Table metadata catalog concept, still widely used under modern systems.

## OLTP vs OLAP
- **OLTP (Online Transaction Processing)** — Day-to-day app transactions: many small, fast reads/writes, highly normalized, ACID guarantees (e.g. MySQL, Postgres, Mongo).
- **OLAP (Online Analytical Processing)** — Historical analysis: fewer, larger, complex queries, denormalized/star-schema, columnar storage (e.g. Hive, Snowflake, BigQuery, Redshift).

## Data Lake / Warehouse / Lakehouse
- **Data Warehouse** — Structured, schema-on-write; more expensive storage but fast/cheap to query.
- **Data Lake** — Raw, schema-on-read, any format; cheap storage but more compute to query well.
- **Data Lakehouse** — Raw data plus warehouse-like structure via a table format layer; cheap storage with fast queries.
- **Data Mart** — A smaller, focused subset of a warehouse for one team.

## Medallion Architecture
- **Bronze** — Raw dumping ground layer, no rules.
- **Silver** — Cleaned/combined layer.
- **Gold** — Business-ready layer.
- A transform job sits between every layer pair — where ETL/ELT's "Transform" step lives.

## File Formats
- **Row-based formats** — CSV, JSON, Avro; good for ingest/Bronze.
- **Columnar formats** — Parquet, ORC; good for analytical queries (Silver/Gold/warehouses), since only needed columns are read.
- **Open Table Formats (OTF)** — Iceberg, Delta, Hudi; sit on top of Parquet/ORC, add ACID transactions, schema evolution, and time travel. Iceberg = open-source standard; Delta = Databricks-proprietary; Hudi = lowest priority.

## Data Lifecycle & ETL/ELT
- **Data Lifecycle** — Ingestion -> Transformation -> Storage -> Analysis/Consumption -> Archival/Deletion.
- **ETL (Extract-Transform-Load)** — Transform happens before loading, in a separate engine (e.g. Spark); good when data must be cleaned/masked before storage.
- **ELT (Extract-Load-Transform)** — Raw data loads first, transforms happen inside the destination warehouse itself (common with dbt); the modern cloud default.

## Batch vs Streaming
- **Batch** — Data arrives on a schedule, processed by a scheduler (Airflow, cron) plus a batch engine (Spark).
- **Streaming** — Data generated continuously in real time; needs a tool to move it (Kafka) and a tool to process it (Flink or Spark Structured Streaming).
- **Kafka topic/producer/consumer/partition/broker/retention** — Core Kafka concepts: producer writes, consumer reads (fully decoupled from each other), partitions split a topic, brokers store/serve, retention keeps messages so consumers can replay.
- **Kafka alternatives** — RabbitMQ, MQTT, AWS SQS (lower volume, simpler).
- **Managed cloud Kafka alternatives** — AWS Kinesis, AWS MSK, Azure Event Hubs, GCP Pub/Sub.

## Idempotency & Error Handling
- **Idempotent** — Running a process multiple times doesn't accumulate duplicate results (unless designed to); achieved via UPSERT/MERGE, deduplication on a unique ID, full-partition overwrites, or tracked offsets/checkpoints.
- **Dead-letter queue (DLQ)** — Where repeatedly-failing records get routed instead of failing the whole batch.
- **Fault isolation** — Design principle that one bad file/record shouldn't kill an entire multi-file job.

## The Data Engineer Role
- **CI/CD tools** — Jenkins, AWS CodeCommit/CodePipeline, Azure DevOps, GitLab CI, Travis CI, GitHub Actions.
- **Canary deployment** — Rolling out a change to a small subset first, as an optional extra safety layer (not a CI/CD requirement itself).

## Quick Hits
- **"Big Data"** — Not a fixed size threshold; the point where a single machine can no longer process the data efficiently.
- **RAG (Retrieval-Augmented Generation)** — Feeding an organization's private data into an LLM's retrieval system to enhance its answers.

---

# Day 1: Linux & Shell Scripting

## Unix/Linux Background
- **Unix -> GNU -> Linux kernel -> GNU/Linux** — Historical chain: Unix (Bell Labs, 1969, proprietary) -> GNU (Stallman, 1983, free tools, no kernel) -> Linux kernel (Torvalds, 1991) -> combined into GNU/Linux, a complete free OS.
- **Debian family** — `.deb`/APT-based distros (Ubuntu, Mint).
- **Enterprise Linux family** — `.rpm`-based distros (RHEL, Fedora, CentOS).
- **Arch family** — Pacman-based, full user control.
- **pyenv** — Manages multiple Python versions per machine.

## Filesystem & Permissions
- **`chmod`** — Changes file permissions; numeric (r=4/w=2/x=1, e.g. `644`) or symbolic (`u+x`) notation.
- **`sudo`** — Gated by group membership deliberately, to limit blast radius.

## grep / awk / sed & Regex
- **`grep`** — Searches text for pattern matches.
- **`awk`** — Parses columnar data by field (`$1`, `$2`, ...).
- **`sed`** — Search-and-replace on text; previews by default, `-i` edits in place.

## Processes & Cron
- **`nohup`** — Runs a command so it survives terminal disconnect.
- **cron** — Linux job scheduler; 5-field syntax (minute hour day month weekday, `*` = every) — the same syntax Airflow uses later in the course.

## Shell Scripts & systemd
- **Shebang** — `#!/bin/bash`-style first line of a script identifying its interpreter.
- **`systemctl`** — Manages system services (status/start/stop/enable).
- **`journalctl`** — Views a service's logs.

---

# Day 2: Python + Pandas

## Python Fundamentals
- **Interpreted language** — Runs with no build step (vs. compiled C/C++/Rust/Go, or hybrid Java bytecode+JVM).
- **Dynamically typed** — Types aren't enforced at runtime without external tools like `mypy`/`pyright`.
- **PyPI** — Official Python package source; watch for typosquatting.
- **GIL (Global Interpreter Lock)** — Only one thread runs Python bytecode at a time; threading helps I/O-bound work only, `multiprocessing` needed for CPU-bound work.

## Control Flow & Functions
- **`map`/`filter`/`reduce`** — Higher-order functions, now generally superseded by list comprehensions for readability.
- **`==` vs `is`** — Value equality vs. object identity.

## Exceptions & Logging
- **`finally`** — Block that always runs regardless of exception outcome.
- **`logging`** — Preferred over `print()` in production; filterable by severity.

## Pandas
- **Vectorization** — Operating on an entire column at once (e.g. `df["salary"] * 1.05`) instead of row-by-row looping.
- **Boolean indexing** — `df[condition]` filters rows.
- **`.groupby().agg()`** — Aggregates and collapses rows to one per group.
- **`.groupby().transform()` / `.rank()`** — Broadcasts a result back onto every row, without collapsing.
- **`.merge()`** — Joins two DataFrames.
- **Series vs. DataFrame** — One column with no column names vs. a full table with named columns; `.to_frame()` converts Series -> DataFrame.
- **`pd.cut()`** — Bins numeric data into labeled categories (low-exclusive/high-inclusive edges by default).
- **`.unstack()`** — Reshapes long format to wide format.
- **`observed=True`** — Avoids phantom category groups in a `groupby()` over categorical data.

---

# Day 3: Git Workflow & CI/CD Pipeline Basics

## Git Hosting Platforms
- **GitHub** — Microsoft-owned, largest developer community, GitHub Actions for CI/CD.
- **GitLab** — GitLab Inc., CI/CD built in natively.
- **Bitbucket** — Atlassian-owned, deep Jira/Confluence integration.

## Branching & Worktrees
- **Git Flow** — Branching model: `main` (stable/deployable), `develop` (integration branch), `feature/*` (branched from develop), `release/*` (final testing before release), `hotfix/*` (urgent fix from `main`, merged into both `main` and `develop`).
- **`git worktree add`** — Checks out multiple branches into separate directories simultaneously, sharing the same underlying repo/history.

## Commits & PRs
- **Pull Request (PR)** — A hosting-platform feature (not a Git concept itself); a mandatory checkpoint for CI + human review before code reaches a shared branch.
- **Merge commit** — Merge strategy preserving full history.
- **Squash and merge** — Merge strategy collapsing a PR into one commit.
- **Rebase and merge** — Merge strategy producing linear history with no merge commit.

## Merge Conflicts & Code Review
- **Conflict markers** — `<<<<<<< HEAD` / `=======` / `>>>>>>> branch-name`, marking the two competing versions of a conflicting section.
- **Review states** — Approve / Request Changes / Comment.

## Repository Discipline & Releases
- **`.gitignore`** — Prevents new files from being tracked; does not untrack files already tracked (needs `git rm --cached` for that).
- **Protected branches** — Enforce the "PR mandatory" rule on a branch.
- **Git tags** — Mark releases (e.g. `git tag -a v1.2.0`); must be pushed explicitly.
- **SemVer (Semantic Versioning)** — `MAJOR.MINOR.PATCH` numbering: MAJOR=breaking change, MINOR=new backward-compatible feature, PATCH=bug fix only.

## CI/CD Pipeline Stages
- **Pipeline stage order** — Checkout -> Build -> Lint -> Unit Test -> Integration Test -> Security Scan -> Artifact Creation (cheap/fast checks before expensive/slow ones).
- **`pytest`** — Function-based Python testing tool using `assert`.
- **`unittest`** — Class-based Python testing tool using `self.assertEqual`.

## Jenkins
- **Controller** — Schedules/coordinates Jenkins jobs (mirrors Spark's Driver).
- **Agents** — Actually run the work (mirrors Spark's Executors).
- **Jenkinsfile** — Groovy file, checked into the repo, defining the pipeline as code.
- **Declarative vs. Scripted syntax** — Structured template vs. full Groovy flexibility.
- **Pipeline triggers** — Webhook (fastest, push-based), Poll SCM (periodic check, same cron syntax as Day 1), Scheduled, Manual.

## Docker Hub
- **Docker Hub** — Registry for container images (like GitHub, but for containers).
- **`docker build` / `docker push` / `docker pull`** — Build an image, push it to a registry, and pull it to reproduce the exact environment anywhere.

---

# Day 4: SQL Fundamentals + Data Warehousing Foundations

## PostgreSQL Peer Authentication
- **Peer authentication** — Postgres auth mode that checks the OS username against a matching role name.

## Primary Keys / Foreign Keys
- **Primary Key (PK)** — Uniquely identifies a row; never NULL, always unique, usually auto-indexed.
- **Foreign Key (FK)** — References another table's PK, enabling `JOIN`s and enforcing referential integrity.
- **Composite key** — A PK spanning multiple columns.

## SQL Data Types
- **`DECIMAL`/`NUMERIC`** — Exact numeric types; always use for money.
- **`FLOAT`/`REAL`** — Approximate numeric types; never use for money.
- **`VARCHAR(n)` vs `TEXT`** — Variable-length bounded string vs. unbounded string.
- **`TIMESTAMPTZ`** — Timezone-aware timestamp; preferred for cross-timezone data.

## Core SQL Syntax
- **`GROUP BY`** — Requires every non-aggregated `SELECT` column to also appear in the `GROUP BY` list.
- **`WHERE` vs `HAVING`** — `WHERE` filters rows before grouping; `HAVING` filters after aggregation.
- **CTE (Common Table Expression)** — `WITH x AS (...)` — a named, reusable subquery, better for chained logic than a nested subquery.
- **Window function** — `<agg>() OVER (PARTITION BY ... ORDER BY ...)`; produces one row per original row, unlike `GROUP BY`'s collapsing behavior.
- **`RANK()` / `DENSE_RANK()` / `ROW_NUMBER()`** — Ranking functions: `RANK()` leaves gaps after ties, `DENSE_RANK()` doesn't, `ROW_NUMBER()` is always unique.

## Indexing & Query Plans
- **`EXPLAIN ANALYZE`** — Shows a query's real execution plan and timing.
- **Seq Scan** — Reads every row in a table.
- **Index Scan** — Traverses a B-tree index, jumping directly to matches.
- **Composite index** — An index on multiple columns `(col_a, col_b)`; favors queries filtering on `col_a` first.

## Data Warehousing Basics
- **Star schema** — One fact table (e.g. `fact_sales`) surrounded by dimension tables (e.g. `dim_customer`, `dim_product`, `dim_date`).
- **Redshift** — Columnar-storage cloud warehouse (AWS); reads only needed columns, compresses well.
- **Snowflake** — Warehouse that separates storage from compute, so each can scale independently.
- **Databricks** — Popularized the lakehouse pattern (object storage + Delta/open table format + Spark).

---

# Day 5: SQL Providers, Dimensional Modeling, Normalization, Lakehouses

*(See `Study Guide - Day 5 (Vocabulary).md` for the full, non-duplicated term list for this day.)*

## Quick Reference (terms specific to this combined overview's phrasing)
- **Analytical DB landscape** — On-prem: Hive, DuckDB. Cloud: Redshift (AWS), Synapse/Delta Lake (Azure), BigQuery (GCP), Snowflake (independent).
- **Kimball vs. Inmon** — Star-schema/business-process-first methodology vs. top-down normalized-enterprise-model-first methodology.
- **Codd's normal forms (1NF/2NF/3NF)** — Progressive rules eliminating data redundancy; more normalization trades faster single-table reads for more cross-table joins.
- **Surrogate key** — Warehouse-generated artificial ID, not the source system's business key.
- **SCD (Slowly Changing Dimensions)** — Type 1 overwrites with no history; Type 2 inserts a new row + surrogate key, preserving full history.
- **Fan-out (push vs. pull)** — Push/fan-out-on-write (fast reads, expensive writes) vs. pull/fan-out-on-read (cheap writes, expensive reads) — same trade-off as data skew/hot-key problems in Spark joins and Kafka partitions.

---

# Cross-Day Threads Worth Noticing
- **ETL vs ELT** — The same push-vs-pull trade-off recurs as fan-out-on-write vs. fan-out-on-read (Day 5) and materialized vs. plain views.
- **"One coordinator, many workers" shape** — Spark's Driver/Executor (Day 0) mirrors Jenkins' Controller/Agent (Day 3); recurs across distributed tooling generally.
- **Cron syntax** — Introduced Day 1, reused directly by Jenkins' Poll SCM trigger (Day 3) and Apache Airflow (later in the course).
