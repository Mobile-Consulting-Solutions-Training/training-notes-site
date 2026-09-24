---
title: Study Guide - Combined (Days 0-5)
description: "Condensed cross-day overview spanning Training 0 through Training 5, for quick verbal review across the whole bootcamp so far"
---

Study Guide - Combined Overview, Days 0-5 (sources: notes/Training 0.md through Training 5.md)

> Condensed cross-day overview for quick verbal review, covering Day 0 through Day 5 per the teacher's note that quiz content could come from any of these days.
> For deep flashcard-style verbal practice on Day 5 specifically (SQL/Data Warehousing - the most recent, densest material), see [Study Guide - Day 5](/training-notes-site/study-guide/day-5/).
> Day 1 and Day 2 also have their own full three-part guides ([Study Guide - Day 1](/training-notes-site/study-guide/day-1/), [Study Guide - Day 2](/training-notes-site/study-guide/day-2/)) with additional flashcards not repeated here.

---

## Table of Contents
- [Day 0: Data Engineering Fundamentals](#day-0-data-engineering-fundamentals)
- [Day 1: Linux & Shell Scripting](#day-1-linux--shell-scripting)
- [Day 2: Python + Pandas](#day-2-python--pandas)
- [Day 3: Git Workflow & CI/CD Pipeline Basics](#day-3-git-workflow--cicd-pipeline-basics)
- [Day 4: SQL Fundamentals + Data Warehousing Foundations](#day-4-sql-fundamentals--data-warehousing-foundations)
- [Day 5: SQL Providers, Dimensional Modeling, Normalization, Lakehouses](#day-5-sql-providers-dimensional-modeling-normalization-lakehouses)
- [Cross-Day Threads Worth Noticing](#cross-day-threads-worth-noticing)

---

# Day 0: Data Engineering Fundamentals

### Hardware Basics
- **ROM** = non-volatile, read-only, firmware/boot. **RAM** = volatile, fast, active working data.
- "Memory" in DE usage = RAM. "Disk" = persistent storage (SSD/HDD).
- **In-memory computing**: processing in RAM instead of touching disk every step - why Spark is ~10-100x faster than MapReduce (which wrote intermediate results to disk between every step).
- Running out of RAM causes spilling to disk (slower) or OOM errors.
- **CPU** = general-purpose processor. **GPU** = specialized for matrix multiplication (graphics = pixel matrices; ML = layers of numeric matrix math) - irrelevant for everyday Spark work, critical for AI/ML.
- **x86** = complex instruction set, more power/cooling. **ARM** = simpler/power-efficient, dominant in mobile and increasingly in data centers.

### Distributed Systems
- Multiple machines working together toward a common goal - for scale, fault tolerance, and parallelism.
- Key concepts: partitioning/sharding, replication, cluster, master/worker (driver/executor), shuffle (expensive network data movement).
- **CAP theorem**: a distributed system can only fully guarantee 2 of Consistency / Availability / Partition-tolerance.
- **Compute cluster** = at least 3 networked computers on a LAN/router working on the same task.
  - Contrast: a **peer-to-peer network** (BitTorrent, SETI) works over the raw internet instead, and is less secure.
- Cluster machines communicate via SSH over local IPs; a switch adds more local IP capacity; internet access is optional for the cluster's router.

### HDFS
- Hadoop Distributed File System - splits files into **blocks** (default 128MB), **replicates** each (default 3x) across DataNodes for fault tolerance.
- A **NameNode** tracks metadata (which blocks live where).
- Write-once, read-many; poor for small files or low-latency random access.
- Increasingly replaced by cloud object storage (S3) in modern stacks.

### Processing Engines
- Separates the "compute" layer from the "storage" layer (HDFS/S3/lake).
- **Batch**: Spark, Hadoop MapReduce
- **Stream**: Flink, Kafka Streams, Spark Structured Streaming
- **Query/SQL engines**: Presto/Trino, Hive, Athena
- **Unified** (batch + streaming): Spark, Flink, Beam

### Apache Spark
- Distributed processing engine, in-memory (vs. MapReduce's disk-heavy model).
- **Architecture**: Driver (builds the DAG, schedules tasks) -> Cluster Manager (allocates nodes: YARN/Kubernetes/Mesos) -> Executors (run tasks in parallel, cache in-memory).
- **Execution flow**: Job (triggered by an action like `.save()`/`.count()`) -> Stages (split at shuffle boundaries like `groupBy`/`join`) -> Tasks (one per partition, run in parallel).
- **DataFrame** (structured, Catalyst-optimized) built on top of **RDD** (original core structure).
- **Lazy evaluation**: transformations build a DAG but don't run until an action triggers it.

### Hive
- An old OLAP data warehouse on top of Hadoop/HDFS - HiveQL translated into MapReduce (historically slow).
- **Hive Metastore** (table metadata catalog) concept still widely used under modern systems.
- Now largely superseded by faster engines (Spark SQL, Presto/Trino, cloud warehouses) for the actual processing.

### OLTP vs OLAP
*(Foundational distinction reused constantly in later days.)*
- **OLTP**: day-to-day app transactions, many small fast reads/writes, highly normalized, ACID guarantees. Examples: MySQL, Postgres, Mongo.
- **OLAP**: historical analysis, fewer/larger/complex queries, denormalized/star-schema, columnar storage. Examples: Hive, Snowflake, BigQuery, Redshift.
- This split is the real-world reason **ETL/ELT pipelines exist** - you don't run heavy analytics directly on the live OLTP database.

### Data Lake / Warehouse / Lakehouse
- **Warehouse**: structured, schema-on-write, more expensive storage but fast/cheap to query. (Hive, Snowflake, BigQuery, Redshift)
- **Data Lake**: raw, schema-on-read, any format, cheap storage but more compute to query well. (S3, ADLS, raw HDFS)
- **Lakehouse**: raw data + warehouse-like structure via a table format layer - cheap storage + fast queries. (Databricks/Delta Lake, Iceberg, Hudi)
- **Data Mart**: a smaller, focused subset of a warehouse for one team.

### Medallion Architecture
*(First introduced here, elaborated further in Day 5.)*
- **Bronze** (raw dumping ground, no rules) -> [Transform job] -> **Silver** (cleaned/combined) -> [Transform job] -> **Gold** (business-ready) -> BI/Reports/ML.
- A transform job sits between every layer pair - that's literally where ETL/ELT's "Transform" step lives.

### File Formats
- **Row-based** (CSV, JSON, Avro) - good for ingest/Bronze.
- **Columnar** (Parquet, ORC) - good for analytical queries, Silver/Gold/warehouses (read only needed columns).
- **Open Table Formats (OTF)**: Iceberg, Delta, Hudi - sit on top of Parquet/ORC, add ACID transactions, schema evolution, time travel.
  - Iceberg = open-source standard.
  - Delta = Databricks-proprietary (use only when working in Databricks).
  - Hudi = lowest priority, just know it exists.

### Data Lifecycle & ETL/ELT
- **Lifecycle**: Ingestion -> Transformation -> Storage -> Analysis/Consumption -> Archival/Deletion.
- **ETL** (Extract-Transform-Load): transform happens before loading (in a separate engine like Spark) - good when data must be cleaned/masked before storage (compliance/PII), or the destination can't transform at scale.
- **ELT** (Extract-Load-Transform): raw data loads first, transforms inside the destination warehouse itself (common with dbt) - the modern cloud default when the warehouse is powerful/cheap enough.

### Batch vs Streaming
- **Batch**: data arrives on a schedule (e.g. 8am daily), processed by a scheduler (Airflow, cron) + batch engine (Spark).
- **Streaming**: data generated continuously in real time, needs two separate specialized systems:
  - Move it: **Kafka** (a "pipe," minimal processing itself)
  - Process it: **Flink** (true record-by-record, lowest latency) or **Spark Structured Streaming** (micro-batch, ~1 second windows processed as tiny batch jobs - a middle ground)
- **Kafka concepts**: topic, producer, consumer (fully decoupled from each other), partition, broker, retention (messages persist so consumers can replay).
- **Kafka alternatives** (lower volume, simpler): RabbitMQ, MQTT, AWS SQS.
- **Managed cloud Kafka alternatives**: AWS Kinesis (pay-per-message, no cluster to manage), AWS MSK (managed real Kafka), Azure Event Hubs, GCP Pub/Sub.

### Idempotency & Error Handling
- **Idempotent** = running a process multiple times doesn't accumulate duplicate results (unless designed to).
  - Concrete example: an idempotent "add `_1` suffix" operation checks if the suffix already exists before adding it again; a non-idempotent one keeps stacking `_1_1_1...` on every re-run.
  - Achieved via: UPSERT/MERGE (not blind INSERT), deduplication on a unique ID, full-partition overwrites, tracked offsets/checkpoints.
- **Error handling strategies**: retries (with backoff), idempotency (makes retries safe), dead-letter queues (DLQ, for repeatedly-failing records), checkpointing, schema/data-quality validation (dbt tests, Great Expectations), quarantining bad records instead of failing the whole batch, alerting.
- **Python**: `try`/`except SpecificError`/`except Exception`/`finally` - catch specific exceptions first, `Exception` only as the final fallback. Fault isolation: one bad file/record shouldn't kill an entire multi-file job.

### The Data Engineer Role
- **CI/CD tools to know**: Jenkins, AWS CodeCommit/CodePipeline, Azure DevOps, GitLab CI, Travis CI, GitHub Actions.
- A lot of the actual job is operational/admin, not just building pipelines:
  - Access management
  - Cluster/infra management
  - Pipeline monitoring/alerting/on-call
  - Cost optimization
  - Data governance/compliance (PII masking, GDPR/HIPAA)
  - Documentation
  - Schema/metadata management
  - Backup/DR
  - Security
  - Vendor management
  - Stakeholder communication

### CI/CD - The Three Environments, and Why It Exists
- **Development** -> **Testing/QA** -> **Production**.
- CI = linting/tests/quality checks on a PR. CD = getting validated code into production with minimal user disruption.
- Before CI/CD, deploying meant taking the whole system down at a low-traffic time.
- CI/CD (from "extreme programming") lets code reload in production without downtime.
- A **canary deployment** (roll out to a small subset first) is an optional extra safety layer, not a CI/CD requirement itself.

### Quick Hits
- **Is MongoDB a data lake?** No - it requires JSON-formatted data (a format constraint). A true data lake needs no format constraint at all (a regular filesystem, or an object store like S3/ADLS).
- **What makes data "Big Data"?** Not a fixed size threshold - the point where a single machine can no longer process it efficiently. 1,000-line CSV: no. Gigabytes: borderline. Terabytes: yes. Petabytes: definitely.
- **Three ways data gets used in an org**: (1) Visualization/dashboards, (2) Machine learning (DE preps the data/infra, DS builds the model), (3) Enhancing LLMs via RAG (feeding an org's private data into an LLM's retrieval system).
- **AI's effect on the data space**: pre-AI, data scientists were mostly statisticians making charts - now shifted toward model training and RAG pipelines. Agentic AI hasn't penetrated DE much yet (data is too economically critical to hand to an unsupervised agent).
- **Git Flow** (expanded fully in Day 3): `main` (stable) / `develop` (branch-off point) / `feature/*` (merged back via PR) / `release/*`.

---

# Day 1: Linux & Shell Scripting

### Unix/Linux Background
- Unix (Bell Labs, 1969, proprietary) -> GNU (Stallman, 1983, free tools, no kernel) -> Linux kernel (Torvalds, 1991) -> GNU/Linux, a complete free OS.
- Free + open source is why Linux dominates data centers over licensed Unix/Windows.
- **Three distro families**: Debian (`.deb`/APT - Ubuntu, Mint), Enterprise Linux (`.rpm` - RHEL, Fedora, CentOS), Arch (Pacman, full control).
- Android runs the Linux kernel but is **not** a GNU/Linux distro (different userspace).
- `pyenv` manages multiple Python versions per machine; skip Anaconda's bloat.

### Filesystem & Permissions
- Core commands: `ls`, `pwd`, `cd`, `cat`, `nano`, `rm -rf` (no undo).
- Standard dirs: `/bin`, `/home`, `/usr`, `/etc`, `/var`, `/opt`, `/tmp`.
- `chmod` numeric (r=4/w=2/x=1, e.g. `644`) or symbolic (`u+x`).
- Owner/root can always override permissions.
- `sudo` access is gated by group membership deliberately, to limit blast radius.

### grep / awk / sed & Regex
- One regex language, different tools.
- `grep -E`/`-o`/`-i` searches text.
- `awk -F,` parses columnar data (`$1`, `$2`...).
- `sed 's/old/new/'` previews, `sed -i` edits in place.
- Python's `re.search`/`findall`/`sub`, named groups `(?P<name>...)`.

### Processes & Cron
- `ps aux`, `&` backgrounds, `nohup` survives disconnect, `kill <PID>`.
- `crontab -e`: 5 fields (minute hour day month weekday, `*` = every) - same syntax Airflow uses later in the course.

### Shell Scripts & systemd
- `#!/bin/bash` shebang + `chmod +x` before `./script.sh` runs.
- `systemctl status/start/stop/enable <service>`, `journalctl <service>` for logs.

---

# Day 2: Python + Pandas

### Python Fundamentals
- Interpreted, no build step (vs. compiled C/C++/Rust/Go, or hybrid Java bytecode+JVM).
- Dynamically typed - type hints aren't enforced without `mypy`/`pyright`.
- Packages from PyPI only (watch typosquatting).
- **GIL**: only one thread runs Python bytecode at a time - threading helps I/O-bound work only, `multiprocessing` needed for CPU-bound work. This is why Spark's real parallelism happens at the JVM/process level, not Python threads.
- `if __name__ == "__main__":` guards direct-execution-only code.

### Control Flow & Functions
- `for`/`while`, `def name(a, b=default, *args, **kwargs)`.
- `map`/`filter`/`reduce` vs. the now-preferred list comprehensions.
- `True`/`False` are case-sensitive (capital only).
- `if`/`elif`/`else` - first match wins.
- `==` (value) vs `is` (identity).

### Exceptions & Logging
- `try`/`except`/`else`/`finally` - `finally` always runs.
- A *caught* exception does not halt the script, only an uncaught one does.
- Specific exceptions must be caught before generic `Exception`.
- `logging` preferred over `print()` - filterable by severity.

### Pandas
- Vectorized, column-oriented (`df["salary"] * 1.05` operates on the whole column at once).
- `pd.read_csv` (extract), boolean indexing `df[condition]` (filter).
- `.groupby().agg()/.mean()` (aggregate, collapses rows) vs `.groupby().transform()`/`.rank()` (broadcasts back onto every row, no collapsing).
- `.merge()` (join), `.sort_values([...], ascending=[...])`.
- Series (one column) vs DataFrame (full table) - `.to_frame()` converts.
- `pd.cut()` bins numeric data into labeled categories (low-exclusive/high-inclusive edges by default).
- `.unstack()` reshapes long->wide; `observed=True` avoids phantom category groups.

---

# Day 3: Git Workflow & CI/CD Pipeline Basics

### Git Hosting Platforms
- **GitHub** (Microsoft, largest community, GitHub Actions)
- **GitLab** (GitLab Inc., CI/CD built-in natively, best self-hosted/all-in-one)
- **Bitbucket** (Atlassian, deep Jira/Confluence integration)
- Git itself works identically regardless of host - these just add remote storage, PR workflows, CI/CD, and access control on top.

### Branching & Worktrees
- **Git Flow**: `main` (stable/deployable), `develop` (integration branch), `feature/*` (branched from develop), `release/*` (final testing before a release), `hotfix/*` (urgent fix from `main`, merged into both `main` and `develop`).
- `git switch -c` (create+switch, newer syntax) vs `git checkout -b` (older).
- `git worktree add -b <branch> <path>` checks out multiple branches into separate directories *simultaneously*, sharing the same underlying repo/history - useful for an urgent hotfix without disturbing unfinished feature work.

### Commits & PRs
- `git add` stages (middle step before commit); commit messages: short present-tense summary + optional "why" explanation.
- A PR is a hosting-platform feature, not a Git concept - a mandatory checkpoint for CI + human review before code reaches a shared branch.
- **Merge strategies**: merge commit (full history), squash and merge (one commit per PR), rebase and merge (linear history, no merge commit).

### Merge Conflicts & Code Review
- Conflict markers: `<<<<<<< HEAD` / `=======` / `>>>>>>> branch-name` - edit to the desired final result, delete all three markers, then `git add`+`git commit`.
- Code review checks: correctness, readability, test coverage, security, scope.
- Review states: Approve / Request Changes / Comment.

### Repository Discipline & Releases
- `.gitignore` doesn't untrack already-tracked files - needs `git rm --cached`.
- Never commit secrets (still recoverable from history even if deleted later).
- Protected branches enforce the "PR mandatory" rule (without it, anyone can push straight to `main`).
- Branch prefixes: `feature/`, `bugfix/`, `hotfix/`, `chore/`, `docs/`.
- Git tags mark releases (`git tag -a v1.2.0 -m "..."`, must be pushed explicitly).
- **SemVer**: `MAJOR.MINOR.PATCH` - MAJOR=breaking, MINOR=new backward-compatible feature, PATCH=bug fix only.

### CI/CD Pipeline Stages
*(In order, cheap/fast checks before expensive/slow ones.)*
- Checkout -> Build -> Lint -> Unit Test -> Integration Test -> Security Scan -> Artifact Creation.
- `pytest` (function-based, `assert`) vs `unittest` (class-based, `self.assertEqual`) - both rely on `test_*.py` naming for auto-discovery.

### Jenkins
- **Controller** (schedules/coordinates) + **Agents** (actually run the work) - mirrors the Spark Driver/Executor pattern.
- `Jenkinsfile` (Groovy, checked into the repo) defines the pipeline as code.
- Declarative (structured template) vs Scripted (full Groovy flexibility) syntax.
- Triggers: Webhook (fastest, push-based), Poll SCM (periodic check, same cron syntax as Day 1), Scheduled, Manual.

### Docker Hub
- Registry for images (like GitHub, but for containers).
- `docker login` -> `docker build -t user/repo:tag .` -> `docker push`.
- `docker pull` + `docker run` anywhere reproduces the exact environment.
- Alternatives: GitHub Container Registry, AWS ECR, Google Artifact Registry.

---

# Day 4: SQL Fundamentals + Data Warehousing Foundations

### PostgreSQL Peer Authentication (Local Dev Setup)
- Match Linux username, Postgres role, and Postgres database name so plain `psql` (no flags) just works.
- Postgres's `peer` auth checks the OS username against a matching role name.
- Three separate namespaces (Linux user, Postgres role, Postgres database) - nothing forces them to share a name, but naming them the same is a dev convenience.
- `docker run --name X -e POSTGRES_USER=X -e POSTGRES_PASSWORD=... -e POSTGRES_DB=X -p 5432:5432 -d postgres:16` replicates this in a container.

### Primary Keys / Foreign Keys
- **PK**: uniquely identifies a row (never NULL, always unique, usually auto-indexed).
- **FK**: in one table references another table's PK, enabling `JOIN`s and enforcing referential integrity (can't insert an FK value with no matching PK; can't delete a still-referenced PK row without `ON DELETE CASCADE`/`SET NULL`).
- Composite key = PK spanning multiple columns.

### SQL Data Types
- `INTEGER`/`SMALLINT`/`BIGINT` (whole numbers), `SERIAL`/`BIGSERIAL` (auto-increment)
- `DECIMAL(p,s)`/`NUMERIC` (exact - always use for money), `FLOAT`/`REAL` (approximate, never for money)
- `CHAR(n)` (fixed, rare) vs `VARCHAR(n)` (variable, common) vs `TEXT` (unbounded)
- `DATE`/`TIME`/`TIMESTAMP`/`TIMESTAMPTZ` (prefer TZ-aware for cross-timezone data), `BOOLEAN`
- Every column nullable by default except PKs.

### Core SQL Syntax
- `INSERT INTO t VALUES (...), (...);` for multi-row inserts.
- String/date literals need single quotes (`'text'`), never double quotes (those are for identifiers).
- Missing semicolon leaves `psql` waiting (`=#` -> `-#` prompt) and swallows the next line as a continuation.
- `GROUP BY` requires every non-aggregated `SELECT` column to also be in the `GROUP BY` list.
- `WHERE` filters rows before grouping; `HAVING` filters after aggregation.
- Subqueries (nested, one-off) vs CTEs (`WITH x AS (...)`, named/reusable, better for chained logic) vs window functions (`<agg>() OVER (PARTITION BY ... ORDER BY ...)` - one row *per original row*, no collapsing, unlike `GROUP BY`).
- `RANK()` (gaps after ties) vs `DENSE_RANK()` (no gaps) vs `ROW_NUMBER()` (always unique) - the classic "Nth highest per group" question requires a CTE/subquery wrapper since `WHERE` can't see a window function's own output column in the same query level.

### Indexing & Query Plans
- `EXPLAIN ANALYZE` shows the real execution plan + timing.
- `Seq Scan` (reads every row) vs `Index Scan` (traverses a B-tree, jumps to matches).
- The planner is cost-based - an index existing doesn't guarantee it's used (small tables often favor Seq Scan anyway).
- Composite index `(col_a, col_b)` favors queries filtering on `col_a` first; column order matters.
- Indexes cost disk space and slow every `INSERT`/`UPDATE`/`DELETE` - index only columns frequently used to filter/join/sort.

### Data Warehousing Basics
- OLTP ("what's happening now," normalized) vs OLAP ("what happened over time," denormalized).
- **Star schema**: one `fact_sales` (measurable events: quantity/price/revenue + FKs) surrounded by `dim_customer`/`dim_product`/`dim_date` (descriptive attributes, denormalized/flattened).
- Simple ETL pattern: extract via `pd.read_sql`, transform via Pandas, load via `to_sql`.
- At huge scale, a single Postgres server hits real limits:
  - **Redshift**: columnar storage (read only the columns a query needs, compresses well)
  - **Snowflake**: separates storage from compute (scale each independently, suspend unused compute)
  - **Databricks**: popularized the lakehouse (object storage + Delta/open table format + Spark, for SQL *and* ML on the same files)

---

# Day 5: SQL Providers, Dimensional Modeling, Normalization, Lakehouses

*(Full flashcard set for this day: [Study Guide - Day 5](/training-notes-site/study-guide/day-5/))*

### Analytical DB Landscape
- **On-prem**: Hive (old Hadoop warehouse), DuckDB (local, pairs with an OTF like Iceberg).
- **Cloud**: Redshift (AWS), Synapse/Delta Lake (Azure), BigQuery (GCP), Snowflake (independent, still runs atop AWS/Azure/GCP).
- OLAP = Online Analytical Processing; OLTP = Online Transaction Processing.

### Dimensional Modeling
- **Ralph Kimball** = star-schema/business-process-first methodology (vs. Inmon's top-down normalized-enterprise-model-first).
- **Star Schema**: basic denormalized model - every dimension one FK-hop from the fact table.
- **Snowflake Schema**: normalized extension - some dimensions connect to *other dimensions* instead of the fact table directly (more joins, less redundancy).
- **Galaxy/fact-constellation Schema**: multiple stars/snowflakes sharing dimensions (skip this term in interviews).
- **Fact table**: central table of "elementary facts" (measures). **Dimension table**: descriptive context.
- A schema always has >=1 fact table and multiple dimensions.

### Normalization
- **Edgar F. Codd** = relational model + normal forms.
- **1NF**: one value per cell.
- **2NF**: has a Primary Key (fuller: no partial dependency on part of a composite key).
- **3NF**: no transitive dependencies (non-key depending on another non-key instead of the PK directly).
- More normalized = more/narrower tables, faster single-table reads, but more joins once data spans many tables - the exact reason OLAP warehouses denormalize (star schemas) instead.

### Visualization Stack
- Matplotlib (low-level) < Seaborn (higher-level, Pandas-native) ~ Plotly (Seaborn competitor).
- BI tools: Power BI, Tableau, AWS QuickSight, Looker.
- Python-to-Postgres-to-chart stack: `pandas` + `sqlalchemy` + `psycopg2-binary` + `seaborn`/`matplotlib`.

### Lakehouse vs Warehouse
- **Warehouse**: schema-on-write, structured, SQL-only.
- **Lakehouse**: schema-on-read files (Parquet/Delta/Iceberg) in object storage + table format adds ACID/schema enforcement/time travel - supports SQL *and* Spark/ML on the same files.

### Medallion Architecture (Recap)
- **Bronze** (raw dump, few rules) -> **Silver** (cleaned/conformed, common format) -> **Gold** (business-ready, often but not always star/snowflake shaped).

### Object Store
- Buckets = top-level containers with their own internal structure.
- Layout: Bronze/Silver/Gold as three buckets, OR Bronze/Silver as buckets + Gold in a dedicated SQL warehouse.
- **Cloud**: S3, Azure Data Lake Storage/ADLS (never say "Azure Blob Storage" - that's the flat layer underneath; ADLS Gen2 adds the hierarchical namespace), GCS.
- **On-prem**: MinIO, Apache Ozone.

### Surrogate Keys & SCD
- **Surrogate key**: warehouse-generated artificial ID (not the source business key) - enables multiple historical versions of an entity, avoids cross-source key collisions, fast single-column joins.
- **SCD** = Slowly Changing Dimensions.
  - Type 0 (per class): overwrite, no history. *(Note: most textbooks flip this - Type 0 usually means "never changes at all," and "overwrite, no history" is usually Type 1 - worth clarifying which convention is being tested.)*
  - Type 1: overwrite in place, no history.
  - Type 2: insert a new row + new surrogate key, mark the old row not-current - full history preserved.

### Fan-Out ("Taylor Swift Problem")
- **Push/fan-out-on-write** (copy to every destination immediately - fast reads, expensive bursty writes) = ETL, materialized views, CDC streaming.
- **Pull/fan-out-on-read** (compute on demand - cheap writes, expensive reads) = ELT, plain views, batch polling.
- Same underlying trade-off as data skew/hot-key problems in Spark joins and Kafka partitions.

---

# Cross-Day Threads Worth Noticing

| Thread | Where it connects |
|---|---|
| ETL vs ELT | Introduced Day 0, expanded Day 4 - same push-vs-pull trade-off as fan-out-on-write vs fan-out-on-read (Day 5) and materialized vs plain views |
| PK/FK | Day 4 - underlies fact/dimension table relationships (Day 5) and referential integrity generally |
| Normalization vs denormalization | Codd/1NF-3NF (Day 5) vs star schema (Day 0/4/5) are explicit opposites - OLTP favors one, OLAP the other; the OLTP/OLAP split (Day 0) is the reason ETL/ELT pipelines exist |
| "One coordinator, many workers" shape | Spark's Driver/Executor (Day 0) = Jenkins' Controller/Agent (Day 3) - recurs across distributed tooling |
| Medallion Architecture | Introduced Day 0 (Bronze/Silver/Gold, transform-job-between-layers) - elaborated Day 5 (Object Store bucket layout, lakehouse tie-in) |
| Cron syntax | Day 1 - reused directly by Jenkins' Poll SCM trigger (Day 3) and Apache Airflow (later in the course) |
| Git Flow branch types | Introduced Day 0 (`main`/`develop`/`feature`/`release`) - full commands/worktrees/merge-strategy treatment in Day 3 |
| Three CI/CD environments | Dev/Test-QA/Production (Day 0) map directly onto the CI/CD pipeline stages (Checkout->Build->Lint->Test->Security Scan->Artifact, Day 3) |
| Idempotency | Day 0 (UPSERT/MERGE, checkpointing, DLQ) - same reliability concern behind SCD Type 2's append-only history design (Day 5) |
| Data quality vigilance | The exact same mislabeled-column bug (`orderdetails.product_category` actually holding quantity data) showed up independently in both the class's own database *and* Evan's separate ChatGPT-assisted lesson prep (Day 5's Worked Example) - never trust a column name without verifying its actual contents |
