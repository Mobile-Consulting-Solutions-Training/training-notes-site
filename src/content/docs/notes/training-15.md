---
title: "Training 15 - Cloud Platforms and Snowflake"
description: "Unified data platforms, AWS/Azure/GCP object storage and VMs, EBS, and Snowflake features: Cortex Code, Workspaces, Semantic Views and virtual warehouses."
sidebar:
  order: 15
---

Teacher: Evan Flint

Syllabus Day 16 (per file numbering) - topic: Cloud data platforms, cloud storage and compute (preparation for Snowflake).

The roadmap's topic for this day, **Spark Structured Streaming** (output modes, triggers, windows, watermarks, state, checkpoints, exactly-once), is covered in `Training 14.md` ("Spark Structured Streaming: Core Concepts"), next to the streaming labs.

# Unified Data Platform

Q. What is a unified data platform?

Expanded: a **unified data platform** handles a company's whole data lifecycle (ingestion, storage, processing, analytics, machine learning and governance) in one place, on one shared copy of the data, instead of a chain of separate tools that each keep their own copy.

The fragmented version is what we've built so far in class: Postgres → Spark ETL → Hive → Kafka → Spark/Flink → MongoDB / Parquet → Streamlit. Every arrow is a separate system with its own storage, security, schema and copies, which leads to data silos, integration overhead (connectors, version mismatches, ports, permissions), inconsistent governance and slower insight.

| Capability | Meaning |
|---|---|
| Single storage layer | Data stored once, often in open formats (Parquet, Delta, Iceberg), read by every workload |
| Batch + streaming together | The same tables receive nightly loads and real-time streams |
| Multiple workloads | SQL analytics, data engineering, data science and ML on the same data |
| Unified governance | One catalog, one set of permissions, lineage and auditing |
| Separation of storage and compute | Processing scales independently of storage |

| Platform | How it unifies |
|---|---|
| Databricks ("Lakehouse") | Spark + Delta Lake + Unity Catalog; lake and warehouse in one, ML built in |
| Snowflake ("AI Data Cloud") | One warehouse for SQL, semi-structured data, Snowpark (Python), streaming (Snowpipe Streaming), Iceberg tables |
| Microsoft Fabric | OneLake storage shared by Data Factory, Spark, warehouse and Power BI |
| Google BigQuery / AWS | BigQuery + Dataplex; S3 + Glue + Redshift + Lake Formation |

Why it matters: one source of truth, less data movement (lower cost, fresher data), a simpler architecture, easier governance and compliance, and data that's ready for ML/AI. Trade-offs: vendor lock-in (reduced by open table formats), usage-based costs that can grow quickly, and less fine-grained control than running each tool yourself.

---

# Cloud Providers: AWS, Azure, GCP

Q. Who are the main cloud providers, and how do their data services map to each other?

A. (Teacher's list) "AWS / Azure / GCP"

Expanded: the three big public cloud providers. They offer the same building blocks under different names; Snowflake and Databricks run on all three (a Snowflake account is created in one of them, and its storage lives in that cloud).

| | AWS | Azure | GCP |
|---|---|---|---|
| Position | #1, largest and oldest | #2, strong with Microsoft enterprises | #3, strong in analytics and AI |
| Object storage | S3 | Blob Storage / ADLS Gen2 | Cloud Storage (GCS) |
| Data warehouse | Redshift | Synapse / Fabric Warehouse | BigQuery (serverless) |
| Spark / big data | EMR, Glue | HDInsight, Synapse Spark, Databricks | Dataproc |
| Streaming | MSK (Kafka), Kinesis | Event Hubs (Kafka-compatible) | Pub/Sub |
| Stream processing | Managed Flink | Stream Analytics | Dataflow (Apache Beam) |
| ETL / orchestration | Glue, Step Functions, MWAA (Airflow) | Data Factory | Cloud Composer (Airflow) |
| Catalog / governance | Glue Data Catalog, Lake Formation | Purview | Dataplex |
| NoSQL | DynamoDB, DocumentDB | Cosmos DB | Firestore, Bigtable |
| Virtual machines | EC2 | Azure Virtual Machines | Compute Engine |

---

# Object Storage

Q. What is object storage, and why is data engineering built on it?

A. (Teacher's definitions) "Object stores are there to be easier to store long term, persistent data on a cloud service." "Object stores are all serverless." "Object stores store their data in bucket and the buckets contain either a actual filesystem or simulated filesystem."

Teacher's clarification: "The buckets contain either an actual simulated file system (in ADLS) OR they contain a simulated file system - it looks and feels like one when you are using it, but it is in fact just an abstraction that is created by the system (AWS S3)."

(In context, the ADLS case is the **actual** file system: real directories via the hierarchical namespace. The S3 case is the **simulated** one: folders are an abstraction built from object-key prefixes.)

---

Q. What is the difference between a flat and a hierarchical namespace?

**Actual vs. simulated filesystem:**

| | Simulated filesystem (flat namespace) | Actual filesystem (hierarchical namespace) |
|---|---|---|
| How it works | The bucket is one flat list of objects. "Folders" are just the `/`-separated prefixes in each key (`bronze/sales/part-0001.parquet`), which tools *display* as folders | The bucket has **real directories** stored as their own entries, like a disk |
| Empty folder | Doesn't really exist (consoles fake one with a zero-byte placeholder object) | Exists |
| Rename or move a folder | Copy every object to the new prefix, then delete the old ones: slow, and not atomic | One metadata change: instant and all-or-nothing |
| Listing a folder | Filter all keys by prefix | Read the directory |
| Folder permissions | Not native (policies match on prefixes) | POSIX-style ACLs on directories |
| Examples | S3 (standard buckets), Azure Blob Storage, GCS (default) | **ADLS Gen2** (hierarchical namespace enabled), GCS with hierarchical namespace, S3 **directory buckets** (S3 Express One Zone) |

Why it matters: Spark, Hive and Delta write to temporary folders and rename them into place when a job commits. On a simulated filesystem that rename is a slow copy, and a crash halfway leaves partial data, which is why analytics-focused storage (ADLS Gen2) offers a real filesystem, and why table formats like Delta and Iceberg avoid relying on renames by tracking which files belong to each table version in a transaction log.

**Interview line (renames on S3):** "S3 has no real directories, so renaming a folder means copying and deleting every object: slow and not atomic. That breaks Spark's classic write-to-temp-then-rename commit, which is why we use the S3A committers, or table formats like Delta and Iceberg that commit by writing a log entry instead of renaming files."

Expanded: object storage keeps data as **objects** in a flat container called a **bucket**. Each object has a **key** (its unique name, e.g. `market-lake/event_date=2026-09-30/event_hour=21/part-0001.parquet`), the **data** itself, and **metadata**. The `/` in a key is just part of the name; tools display prefixes as folders, which is why Hive-style partition paths work the same way in a bucket as on a local disk.

- **Long-term, persistent data:** cheap per GB, practically unlimited, extremely durable (S3 is designed for 99.999999999%, "11 nines"), with cold tiers for rarely read data. Objects can't be edited in place; you replace the whole object, so it suits write-once data: data-lake files, backups, logs, archives.
- **Serverless:** you never provision, size or patch a server. Create a bucket, read and write over an HTTP API, and pay per GB stored plus requests. There are servers underneath, but they're the provider's problem.

| | Object storage | File storage | Block storage |
|---|---|---|---|
| Organized as | Flat bucket of objects with keys | Folder tree | Raw fixed-size blocks |
| Accessed via | HTTP API (`s3://...`) | File system (NFS, SMB, local disk) | Attached disk under an OS or database |
| Examples | S3, Azure Blob/ADLS, GCS | Laptop disk, AWS EFS | AWS EBS, a VM's disk |
| Scale | Practically unlimited | Limited by the server | One disk at a time |
| Cost | Cheapest | Medium | Highest |
| Edit in place | No | Yes | Yes |
| Best for | Data lakes, backups, media, ML data | Shared documents | Databases, operating systems |

Why data engineering is built on it: cheap storage for years of raw (Bronze) data, durability, **separation of storage and compute** (data stays in the bucket while Spark, Flink, Snowflake or Hive read it), and open formats any tool can read. Delta Lake and Iceberg add transactions, schema evolution and time travel *on top of* object storage. MinIO is an open-source, S3-compatible object store that runs in Docker for practice.

## AWS S3, Azure Blob Storage, Azure Data Lake Storage (ADLS)

| | AWS S3 | Azure Blob Storage | ADLS Gen2 |
|---|---|---|---|
| What it is | AWS's object storage | Azure's general-purpose object storage | Blob Storage with the **hierarchical namespace** enabled, tuned for analytics |
| Container | Bucket | Container (in a storage account) | File system / container (in a storage account) |
| Folders | Flat | Flat | Real directories |
| Rename a folder | Copy every object, then delete | Copy and delete | Atomic, instant (one metadata change) |
| Permissions | IAM, bucket policies | Azure RBAC, SAS tokens | RBAC + POSIX-style ACLs on folders and files |
| Address | `s3://bucket/path` | `https://account.blob.core.windows.net/container/path` | `abfss://container@account.dfs.core.windows.net/path` |
| Tiers | Standard, Infrequent Access, Glacier | Hot, Cool, Cold, Archive | Same as Blob |

**ADLS Gen2 = Blob Storage + hierarchical namespace.** It's one service: tick "Enable hierarchical namespace" when creating the storage account. It matters because Spark and Hive jobs constantly create, rename and delete folders (e.g. write to a temporary folder, then rename it into place on commit). On flat storage that rename copies every file; with real directories it's one instant, all-or-nothing operation. Gen1 was an older, retired service.

## Google Cloud Storage (GCS)

| | GCS |
|---|---|
| Container | Bucket (globally unique name) |
| Address | `gs://bucket/path` |
| Structure | Flat, with an optional hierarchical namespace (real folders, atomic renames) |
| Storage classes | Standard → Nearline (~monthly) → Coldline (~quarterly) → Archive (yearly) |
| Location | Region, dual-region or multi-region |
| Permissions | IAM (uniform bucket-level access recommended), signed URLs |

Used as GCP's data-lake layer: BigQuery loads from it or queries it in place (external tables), Dataproc reads `gs://` paths instead of HDFS, Dataflow writes output there.

| | AWS | Azure | GCP |
|---|---|---|---|
| Service | S3 | Blob / ADLS Gen2 | GCS |
| Spark path | `s3a://` | `abfss://` | `gs://` |
| Snowflake stage URL | `s3://` | `azure://` | `gcs://` |

---

# Remote Instances (Cloud Virtual Machines)

Q. What is a remote instance?

A. (Teacher's definition) "Remote Instance = Virtual Machine hosted on the cloud"

Teacher's examples: "AWS EC2", "Azure Virtual Machines", "Google App Engine"

Expanded: you rent a computer in the provider's data center, choose its CPU, memory, disk and OS, and connect remotely (usually SSH). Each cloud VM runs its **own kernel** (see the VM vs. container comparison in `Training 14.md`).

Note: Google's VM service is **Compute Engine**. **App Engine** is a different kind of service, a **platform (PaaS)**: you upload code and Google runs and scales it, with no server to manage. Its equivalents are AWS Elastic Beanstalk and Azure App Service.

| | AWS EC2 | Azure Virtual Machines | Google Compute Engine | Google App Engine |
|---|---|---|---|---|
| Type | VM (IaaS) | VM (IaaS) | VM (IaaS) | Platform (PaaS) |
| You manage | OS, patches, software, scaling | Same | Same | Only your code |
| Sizes | Instance types (`t3.micro`, `m5.xlarge`) | VM sizes (`B2s`, `D4s_v5`) | Machine types (`e2-medium`) | Scales automatically |
| Connect | SSH / key pair | SSH / RDP | SSH (browser or `gcloud`) | No server to log in to |

| Model | You manage | Provider manages | Examples |
|---|---|---|---|
| IaaS (Infrastructure as a Service) | OS, runtime, software, app | Hardware, network, virtualization | EC2, Azure VMs, Compute Engine |
| PaaS (Platform as a Service) | Code and data | Everything else | App Engine, Elastic Beanstalk, Azure App Service |
| SaaS (Software as a Service) | Nothing, just use it | Everything | Snowflake, Gmail, Salesforce |

Why data engineers use them: running your own tools (Kafka, Spark, Airflow, Postgres) off your laptop, renting big machines on demand, keeping streaming jobs running 24/7, and managed services (EMR, Dataproc, MSK) run on fleets of VMs underneath.

---

# EBS (AWS Elastic Block Store)

Q. What is EBS, and how does it compare with S3 and EFS?

A. (Teacher's definition) "EBS - AWS Elastic Block Store - basically persistent storage that can be attached to an EC2 instance"

Expanded: EBS is **block storage**: the virtual hard drive of a cloud VM. The instance sees a raw disk, formats it with a file system and mounts it.

- **Persistent:** data survives stopping or restarting the instance; volumes can be detached and reattached. Unlike **instance store**, a temporary disk inside the host that is wiped when the instance stops.
- **Volume** = one EBS disk. The root (OS) drive is an EBS volume; extra volumes can be attached for data.
- **One Availability Zone:** a volume attaches only to instances in the same AZ, usually one at a time (some `io2` volumes support multi-attach).
- **Snapshots:** point-in-time backups stored in S3 behind the scenes; used to restore, copy to another AZ or region, or create new volumes.
- Can be resized or change type while attached.

| Volume type | Kind | Use for |
|---|---|---|
| gp3 | General Purpose SSD (default) | OS drives, dev servers, small databases |
| io2 / io1 | Provisioned IOPS SSD | Busy databases needing guaranteed I/O |
| st1 | Throughput-optimized HDD | Large sequential reads: logs, Kafka data |
| sc1 | Cold HDD | Rarely accessed data |

| | EBS | S3 | EFS |
|---|---|---|---|
| Type | Block (a disk) | Object (a bucket) | File (shared network drive) |
| Attached to | One EC2 instance, same AZ | Nothing; HTTP from anywhere | Many instances at once |
| Needs a server | Yes | No (serverless) | No |
| Billing | Per GB provisioned | Per GB stored + requests | Per GB stored |
| Best for | OS drives, databases, Kafka broker logs | Data lakes, backups, Parquet | Shared files across servers |

Equivalents: Azure Managed Disks, GCP Persistent Disk. Data engineering use: self-managed databases and Kafka brokers on EC2 keep their data on EBS (they need in-place updates); analytical data (Parquet, the lake) goes in S3. Same idea as the Docker `mongo-data` volume in the Training 13 homework, which kept MongoDB's data when the container restarted.

---

# Snowflake Cortex Code (CoCo) in Snowsight

Link shared in class: https://docs.snowflake.com/en/user-guide/cortex-code/cortex-code-snowsight

Expanded: **Cortex Code ("CoCo")** is Snowflake's AI assistant built into **Snowsight** (Snowflake's web UI). The docs describe it as providing "an agentic experience across several functional areas within Snowsight", "designed to assist data analysts, engineers, and administrators with tasks such as SQL development, data exploration, and account management." *Agentic* means it can carry out multi-step tasks (write a query, run it, check results, fix errors), not just answer questions. Status: **generally available**.

**Where it is:** the **CoCo icon in the lower-right corner** of Snowsight opens a chat panel on the right side. It works in **SQL Workspaces** (the main place), **Notebooks** in Workspaces, **dbt Projects** on Snowflake, and chats can start from the Snowsight home page.

| Area | What it can do |
|---|---|
| SQL development | Generate and modify queries, explain code, suggest optimizations, inline suggestions while typing, find and fix errors; changes are shown as a **diff** to review before applying |
| Data discovery | Natural-language search for tables and schemas, metadata and **lineage** exploration; type **`@`** to add database objects as context |
| Administration | Governance and security questions, **cost analysis** and warehouse optimization, role and privilege discovery |
| Notebooks and dbt | Create notebooks and cells (SQL, Python, Markdown), scaffold and document dbt projects |
| Semantic models | Works with Cortex Analyst semantic models |

Example prompts from the docs:
- "Write a query for top 10 customers by revenue and a 7-day moving average"
- "Find all tables that have PII in them"
- "Which 5 service types are using the most credits?"
- "Build me a notebook for a customer churn prediction use case"

**Access requirements:**
- Database role **`SNOWFLAKE.COPILOT_USER`** (required), plus **either** `SNOWFLAKE.CORTEX_USER` **or** `SNOWFLAKE.CORTEX_AGENT_USER`. The agent role is the least-privilege option: it grants the Cortex Agents API without other Cortex features.
- Cross-region inference must be enabled; **trial accounts need a credit card added** to turn on AI features.
- If the account previously opted out of the old Snowflake Copilot, CoCo is disabled too.

**Models:** choose a specific LLM (Claude, GPT, Gemini, Grok) or **Auto** (Snowflake picks), **Auto Intelligent** (capability first) or **Auto Efficient** (cost first). Some models allow Low/Medium/High reasoning effort.

**Customizing:** "skills" (custom instructions/workflows in `.snowflake/cortex/skills` in a workspace) and an **`AGENTS.md`** file for persistent project instructions.

**Security:** CoCo runs inside the account's existing authentication and **RBAC** (role-based access control): it can only see and do what your role allows, and doesn't store credentials. It always starts with your **default role**, even if a worksheet uses a different one; switching roles has to be asked for explicitly.

**Limitations:** suggestions "can occasionally be incorrect or not match your intent", so review the diff before applying. Usage counts as AI-feature consumption (credits) under Snowflake's AI terms.

| | Legacy Copilot | CoCo (Cortex Code) | Snowflake CoWork |
|---|---|---|---|
| Purpose | Limited SQL and UI help | Development and operational workflows (agentic) | Natural-language insights and recommendations for business users |

---

# Workspaces

Q. What is a workspace in Snowflake and Databricks?

A. (Teacher's definition) "A workspace in Snowflake and Databricks is a virtual location within your Snowflake or Databricks environment where you can hold resources, which are isolated from all other resources on the platfor[m]." "So basically, workspaces allow you to have projects which are isolated from each other."

Expanded: a workspace is a **container for a project**: its code, files and settings live together and are kept separate from other projects on the same platform, so teams and projects don't interfere with each other. The word means slightly different things on the two platforms:

| | Snowflake Workspace | Databricks Workspace |
|---|---|---|
| What it is | A **file-based development environment** in Snowsight: an in-browser IDE for organizing project files | The **top-level environment** for a team or organization: everything you work with in Databricks lives in one |
| What it holds | SQL files, Python files, notebooks, dbt projects, YAML/Markdown, organized in folders | Notebooks, files, repos (Git folders), jobs/workflows, clusters/compute, dashboards, libraries |
| Isolation | Personal workspaces (private) vs. shared / Git-connected ones; access governed by Snowflake roles | Each workspace has its own users, permissions, compute and URL; companies often use separate workspaces for **dev / test / prod** |
| Data | Data stays in databases/schemas/tables (shared across the account); the workspace holds the **code** that works on it | Data is governed by **Unity Catalog**, which can be shared across workspaces |
| Git | Connect a Git repository: pull, commit, push | Git folders (Repos) |
| AI assistant | Cortex Code (CoCo) | Databricks Assistant |

**Snowflake detail:** Workspaces replace the older **Worksheets** (single SQL tabs) with a file/folder structure like VS Code. Each file runs with a chosen **role** and **warehouse** (the compute that executes it). CoCo works inside workspaces and can use workspace-specific "skills" (`.snowflake/cortex/skills/`) and `AGENTS.md` instructions.

**Why isolation matters:** one team's experiments can't break another team's production code; access can be granted per project (least privilege); and environments like dev/test/prod stay separate, the same idea as the CI/CD environments from earlier trainings.

**Vocabulary:** *Workspace*: an isolated virtual location in a platform such as Snowflake or Databricks that holds a project's resources (code, notebooks, files, settings) separately from other projects.

---

# Semantic Views

Q. What is a semantic view?

Expanded: a **semantic view** is a Snowflake schema-level object that stores the **business meaning** of data next to the tables: which tables relate to each other, what business terms mean, and how metrics are calculated. Humans, BI tools and AI (Cortex Analyst, CoCo) can then ask questions in business terms and get **consistent answers**.

**Problem it solves:** raw tables have technical names (`fact_sales.qty * fact_sales.unit_price`, `dim_customer.cust_seg_cd`). Without a shared definition, every analyst, dashboard or AI tool works out the joins and formulas itself, and they often get **different numbers** for the same question. A semantic view defines "revenue" and "region" **once**, in the database.

| Part | Meaning | Example (Training 5 star schema) |
|---|---|---|
| Logical tables | The tables involved | `fact_sales`, `dim_customer`, `dim_product`, `dim_date` |
| Relationships | How they join | `fact_sales.customer_id → dim_customer.id` |
| Facts | Row-level numeric values | `quantity`, `unit_price` |
| Dimensions | Attributes to group or filter by | `customer.region`, `product.category`, `date.month` |
| Metrics | Business calculations (aggregations) | `total_revenue = SUM(quantity * unit_price)`, `order_count` |
| Synonyms / comments | Plain-language names for AI | "sales", "turnover" → `total_revenue` |

```sql
CREATE SEMANTIC VIEW sales_analysis
  TABLES (
    sales     AS gold.fact_sales   PRIMARY KEY (sale_id),
    customers AS gold.dim_customer PRIMARY KEY (id)
  )
  RELATIONSHIPS (
    sales (customer_id) REFERENCES customers
  )
  FACTS (
    sales.line_amount AS quantity * unit_price
  )
  DIMENSIONS (
    customers.region AS region
  )
  METRICS (
    sales.total_revenue AS SUM(sales.line_amount)
  );
```

Querying: request dimensions and metrics, and Snowflake generates the joins and aggregation:

```sql
SELECT * FROM SEMANTIC_VIEW(
  sales_analysis
  DIMENSIONS customers.region
  METRICS sales.total_revenue
);
```

| | Regular view | Semantic view |
|---|---|---|
| Stores | One fixed SQL query | Definitions: tables, joins, dimensions, metrics |
| Output | Always the same result shape | Any combination of dimensions and metrics requested |
| Used by | SQL users | SQL users, BI tools, AI (Cortex Analyst, CoCo) |
| Purpose | Reuse a query | One shared business vocabulary |

Why it matters:
- **One definition of each metric:** "revenue" means the same thing everywhere (the single source of truth from the Unified Data Platform section).
- **Better AI answers:** Cortex Analyst converts plain English to SQL far more accurately when joins and metric definitions are explicit, which is why CoCo works with semantic models.
- **Built on the Gold layer:** sits on top of a star schema (facts and dimensions), like `gold.fact_sales` / `gold.dim_*` from Training 5.

The general concept is a **semantic layer**; other examples are dbt's Semantic Layer, Looker's LookML and Power BI semantic models.

**Vocabulary:** *Semantic view*: a Snowflake object defining business entities, relationships, dimensions and metrics over physical tables, so people, BI tools and AI query consistent business concepts instead of re-deriving joins and formulas.

---

# Snowflake Data Processing (Compute and Processing Features)

Expanded: Snowflake processes data on compute that is **separate from storage**, either **virtual warehouses** you size and start, or **serverless** compute that Snowflake manages for you, and offers several ways to transform data without moving it out.

## Virtual Warehouses: the Main Processing Engine

| Type | Use for |
|---|---|
| Standard warehouse | SQL queries, `COPY INTO` loads, transformations, BI dashboards |
| Snowpark-optimized warehouse | Memory-heavy Python/Java/Scala work: ML training, large in-memory operations |
| Multi-cluster warehouse | Many concurrent users: automatically adds clusters when queries start queuing |

Sizes X-Small → 6X-Large, each size roughly doubling power and credit cost. Warehouses **auto-suspend** when idle (no charge) and **auto-resume** when a query arrives.

## Processing Features Inside Snowflake

| Feature | What it does | Compare to |
|---|---|---|
| SQL | Transformations with `INSERT ... SELECT`, `MERGE`, `CREATE TABLE AS` | Postgres / Hive SQL |
| **Snowpark** | DataFrame API in Python, Java or Scala that runs inside Snowflake's compute; data never leaves | PySpark: `session.table("sales").filter(...).group_by(...)` |
| UDFs / stored procedures | Custom functions and procedures in SQL, Python, Java, JavaScript or Scala | Spark UDFs |
| **Streams** | Track changes (inserts, updates, deletes) on a table: change data capture | Kafka offsets: "what's new since I last read?" |
| **Tasks** | Scheduled SQL/procedure runs, chainable into pipelines (DAGs) | cron / Airflow |
| **Dynamic Tables** (detail: `Training 16.md`) | Declare the result as a query plus a freshness target (`TARGET_LAG = '5 minutes'`); Snowflake keeps it updated incrementally | A Spark Structured Streaming job written as SQL |
| **Snowpipe / Snowpipe Streaming** | Serverless continuous loading of files / rows | The `?` in Kafka → Spark/Flink → Parquet → ? → Snowflake |
| Snowpark Container Services | Run Docker containers (apps, ML models, APIs) on Snowflake-managed compute | Docker, inside Snowflake |
| Cortex AI functions | LLM functions in SQL (`AI_COMPLETE`, sentiment, summarize, translate), Cortex Analyst | AI inside the database |

## Serverless Compute

Snowpipe, serverless Tasks, Dynamic Table refreshes and automatic clustering run on **Snowflake-managed compute**: no warehouse to size or start, billed per use. Same "serverless" idea as object storage.

## Mapping to the Class Pipeline

```text
Kafka → Spark/Flink → Parquet → [Snowpipe] → raw table
                                                │  Stream (what's new?)
                                                ▼
                                   Task or Dynamic Table (SQL / Snowpark)
                                                │
                                   Gold tables → Semantic View → BI / CoCo
```

Inside Snowflake, **Streams + Tasks** or **Dynamic Tables** can run the Bronze → Silver → Gold transformations previously done with Spark, without moving the data out.

## "Data Processor" in the Legal Sense

Under privacy laws such as GDPR, the **data controller** decides why and how personal data is used (the company using Snowflake), and the **data processor** handles it on the controller's behalf (Snowflake). Cloud providers sign **data processing agreements (DPAs)** on that basis.

**Interview one-liner:** Snowflake processes data on virtual warehouses (standard, Snowpark-optimized, multi-cluster) and serverless compute; you transform it with SQL, Snowpark DataFrames, UDFs, Streams and Tasks, or Dynamic Tables, and load it with Snowpipe, all inside Snowflake with storage separate from compute.

---

# Snowpark

Q. What is Snowpark?

A. (Teacher's definition) "Snowpark - Snowflake's code execution environment, in which it is possible to use a Spark job"

Expanded: **Snowpark** lets you write data processing code in **Python, Java or Scala** (not just SQL) that runs **inside Snowflake**, on Snowflake's virtual warehouses, next to the data. The data never has to be pulled out to a separate Spark cluster.

- **Snowpark DataFrame API:** looks and feels like PySpark. Operations are **lazy** (nothing runs until an action like `.collect()` or `.show()`), and Snowflake translates them into SQL that runs on the warehouse:

```python
from snowflake.snowpark.functions import col, sum as sum_

sales = session.table("gold.fact_sales")
result = (sales.filter(col("quantity") > 0)
               .group_by("product_id")
               .agg(sum_(col("quantity") * col("unit_price")).alias("revenue")))
result.show()   # executes now, inside Snowflake
```

- **Running Spark jobs:** **Snowpark Connect for Apache Spark** lets existing **PySpark** code run against Snowflake with minimal changes, with Snowflake's engine executing it instead of a Spark cluster. That's what the teacher means by being able to use a Spark job.
- **Beyond DataFrames:** Python/Java/Scala **UDFs** and **stored procedures**, ML training on **Snowpark-optimized warehouses**, and Snowpark Container Services for Docker workloads.

| | PySpark (on a Spark cluster) | Snowpark |
|---|---|---|
| Where code runs | Your Spark cluster (local, EMR, Dataproc, Databricks) | Snowflake virtual warehouses |
| Data location | Read in from files or databases, then written back | Stays in Snowflake tables |
| Cluster to manage | Yes (executors, memory, versions, connectors) | No: pick a warehouse size |
| API | `spark.read...`, DataFrames, lazy evaluation | `session.table(...)`, DataFrames, lazy evaluation |
| Connector headaches from class (`--packages`, Scala versions) | Yes | No |

**Interview nuance:** Snowpark **DataFrame** operations are pushed down: compiled to SQL and run by Snowflake's engine, so they are as fast as SQL. Snowpark **Python UDFs and stored procedures** instead run row or batch logic in a sandboxed Python runtime on the warehouse, which is more flexible but slower; prefer DataFrame operations where possible. Snowflake architecture and warehouses: `Training 16.md`.

---

# dbt (data build tool)

Q. What is dbt?

A. (Teacher's definition) "DBT - the major ELT tool that we use with Snowflake"

Expanded: **dbt** handles the **T (Transform)** in **ELT**: data is first **E**xtracted and **L**oaded raw into the warehouse (Snowpipe, `COPY INTO`), then **dbt transforms it inside the warehouse** using SQL. dbt doesn't move data and has no compute of its own: it turns your SQL into the right `CREATE TABLE / VIEW` statements and runs them on Snowflake's warehouses.

| | ETL | ELT |
|---|---|---|
| Order | Extract → Transform (outside) → Load | Extract → Load (raw) → Transform (inside the warehouse) |
| Transform runs on | A separate engine (Spark job, Python script) | The warehouse's own compute (Snowflake) |
| Example from class | Postgres → Spark (HiveSparkETL) → Hive | Kafka → Parquet → Snowpipe → raw table → **dbt** → Gold |
| Why ELT now | Older warehouses were expensive or slow | Cloud warehouses scale compute cheaply; raw data is kept for reprocessing |

How dbt works:
- A **model** is a `.sql` file containing one `SELECT`. dbt **materializes** it as a view, table, incremental table or ephemeral CTE.
- **`ref()`** links models together, so dbt knows the build order and draws the **lineage DAG** automatically:

```sql
-- models/silver/silver_sales.sql
SELECT sale_id, customer_id, product_id, quantity, unit_price,
       quantity * unit_price AS line_amount
FROM {{ ref('bronze_sales') }}
WHERE sale_id IS NOT NULL
```

- **Jinja** templating (`{{ ... }}`) adds variables, loops and reusable macros to SQL.
- **Tests** (`unique`, `not_null`, `relationships`, `accepted_values`) check data quality on every run. For example, a `unique` test on `sale_id` would have caught the Training 11 duplicate problem automatically.
- **Incremental models** process only new rows (`is_incremental()`), the same idea as the anti-join dedup in `HiveSparkETL.scala`.
- **Docs:** `dbt docs generate` builds a browsable data catalog with the lineage graph.
- Commands: `dbt run` (build models), `dbt test`, `dbt build` (run + test), `dbt docs generate`.

| Flavor | What it is |
|---|---|
| dbt Core | Free, open-source command-line tool |
| dbt Cloud | Hosted version: web IDE, scheduler, CI |
| dbt Projects on Snowflake | Run dbt natively inside Snowflake (in Workspaces; CoCo can scaffold projects) |

Why it's the standard with Snowflake: transformations are plain SQL under **version control** (Git), with tests, documentation and lineage. It brings software-engineering practice (CI/CD, code review, environments) to the Bronze → Silver → Gold layers.

This is a short intro; the hands-on dbt + Snowflake class (models, `ref`/`source`, tests, materializations) is in `Training 17.md`.

## Installing dbt (class follow-along)

Class command: `pip install dbt-core dbt-postgres dbt-snowflake`

- **`dbt-core`** is the dbt engine itself; **adapters** (`dbt-postgres`, `dbt-snowflake`, also `dbt-databricks`, `dbt-bigquery`, …) teach it how to talk to each warehouse. Install one adapter per platform you connect to.
- On this Ubuntu machine the command fails with **`externally-managed-environment`** (PEP 668: Ubuntu blocks `pip install` into the system Python, as with PyFlink in `Training 14.md`). dbt also doesn't support Python 3.14 yet.
- Fix used: a dedicated Python 3.12 virtual environment at `~/MCS/BigData/dbt-practice/.venv` (dbt-core 1.12.5, dbt-snowflake 1.12.1, dbt-postgres 1.11.0):

```bash
cd ~/MCS/BigData/dbt-practice
source .venv/bin/activate      # (.venv) appears in the prompt
dbt --version                  # confirm core + adapters
pip install <anything else>    # pip works inside the venv
```

---

# Using Snowflake from the Command Line

Expanded: yes, Snowflake can be used entirely from a terminal, not just the Snowsight web UI.

| Tool | Command | Status | Use for |
|---|---|---|---|
| **Snowflake CLI** | `snow` | Current, recommended | Run SQL, manage objects, deploy Snowpark/Streamlit apps, notebooks and dbt projects, upload files to stages |
| **SnowSQL** | `snowsql` | Older, being replaced by Snowflake CLI | Interactive SQL shell (like `psql`), `PUT` files to stages |
| dbt (`dbt-snowflake`) | `dbt run`, `dbt test` | Installed in `dbt-practice/.venv` | Run transformations against Snowflake |
| Python connector / Snowpark | `snowflake-connector-python`, `snowflake-snowpark-python` | Libraries, not CLIs | Scripts and Python jobs |

```bash
pip install snowflake-cli          # inside a venv (e.g. dbt-practice)
snow connection add                # one-time: account identifier, user, auth, role, warehouse
snow connection test
snow sql -q "SELECT CURRENT_VERSION();"
snow sql -f load_market_ticks.sql
snow stage copy ./market-lake @market_stage --recursive   # upload local files to an internal stage
snow object list warehouse         # also: database, schema, table, ...
```

- Connection settings live in `~/.snowflake/config.toml` / `connections.toml`.
- Pipeline connection: uploading local files (e.g. the Parquet written to `/tmp/market-lake/` in Training 14) to an **internal stage** with `snow stage copy` or SnowSQL `PUT` is the step before `COPY INTO` loads them into a table. CI/CD pipelines use the CLI to deploy Snowflake code.

## Installing Snowflake CLI (class instructions, via ChatGPT)

Teacher-shared instructions (from ChatGPT), for **Windows / PowerShell**, using **pipx**:

```powershell
python --version                  # or: py --version  (the py launcher is more reliable on Windows)
py -m pip install --user pipx
py -m pipx ensurepath
# CLOSE AND REOPEN POWERSHELL (so the PATH change takes effect)
pipx --version
pipx install snowflake-cli
snow --version
snow connection add
snow connection list
snow sql -q "SELECT CURRENT_VERSION(), CURRENT_REGION();"
```

- **pipx** installs a Python **command-line application** into its own private virtual environment and puts just its command (`snow`) on your PATH. You get the tool without polluting your main Python, and without activating a venv every time.
- If `pipx` is "not recognized": it's installed but its folder isn't on PATH. `py -m pipx --version` confirms it; run `py -m pipx ensurepath` and **restart the terminal**, or bypass it with `py -m pipx install snowflake-cli`.
- `pipx install snowflake-cli` is an officially documented, cross-platform installation method.

| | pip (inside a venv) | pipx / `uv tool install` |
|---|---|---|
| Installs | **Libraries** for a project (pyspark, pandas, dbt adapters) | **Standalone command-line apps** (`snow`, `dbt`, `black`) |
| Activate first? | Yes (`source .venv/bin/activate`) | No: the command is on PATH everywhere |
| Isolation | One venv per project | One private venv per app, created automatically |

**This machine (Ubuntu):** the equivalent of pipx without `sudo` is `uv tool install --python 3.12 snowflake-cli`, which installed **Snowflake CLI 3.28.0** with `snow` in `~/.local/bin` (already on PATH), so `snow` works in any terminal. (With apt instead: `sudo apt install pipx`, then `pipx ensurepath` and `pipx install snowflake-cli`.)

**Real example of why pipx matters (happened in class):** running `pip install snowflake-cli` *inside* the dbt virtual environment **broke dbt**. snowflake-cli 3.28.0 pins older versions of shared libraries, so pip downgraded `click` 8.5 → 8.1.8 and `protobuf` 6.33 → 5.29, and printed:

```text
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. ...
dbt-core 1.12.5 requires click<9.0,>=8.3.0, but you have click 8.1.8 which is incompatible.
dbt-core 1.12.5 requires protobuf<8.0,>=6.0, but you have protobuf 5.29.6 which is incompatible.
```

Note that pip still says "Successfully installed": **a red `dependency conflicts` block after an install means something else in that environment may now be broken**, even though the install itself succeeded. Fix: uninstall the CLI from the venv (`pip uninstall snowflake-cli`), restore the downgraded packages (`pip install "click>=8.3,<9" "protobuf>=6,<7"`), confirm with **`pip check`** ("No broken requirements found"), and keep `snow` in its own isolated install (pipx / `uv tool install`). Rule: **apps → pipx; project libraries → the project's venv.**
