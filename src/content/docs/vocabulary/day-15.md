---
title: Day 15 Vocabulary
description: Glossary of terms and definitions from the Training 15 notes.
sidebar:
  order: 15
---

Vocabulary — Study Guide Day 15

Source: notes/Training 15.md

## Unified Data Platforms
- **Unified data platform** — A platform that handles the whole data lifecycle (ingestion, storage, processing, analytics, ML, governance) in one place on one shared copy of the data.
- **Data silo** — Data trapped in one system with its own storage, security and schema, cut off from other tools.
- **Single storage layer** — Data stored once, often in open formats, and read by every workload.
- **Unified governance** — One catalog, one set of permissions, lineage and auditing across all workloads.
- **Separation of storage and compute** — Architecture where processing scales independently of where the data is stored.
- **Vendor lock-in** — Dependence on one vendor's platform that makes switching costly; reduced by open table formats.
- **Databricks Lakehouse** — Databricks' unified platform combining Spark, Delta Lake and Unity Catalog so the lake and warehouse are one.
- **Unity Catalog** — Databricks' governance catalog, shareable across workspaces.
- **Snowflake AI Data Cloud** — Snowflake's unified platform for SQL, semi-structured data, Snowpark, streaming and Iceberg tables.
- **Microsoft Fabric** — Microsoft's unified platform where Data Factory, Spark, warehouse and Power BI share OneLake storage.
- **OneLake** — The single shared storage layer of Microsoft Fabric.
- **Lake Formation** — AWS service for data-lake governance and permissions.
- **Dataplex** — GCP's data catalog and governance service.

## Cloud Providers
- **AWS (Amazon Web Services)** — The largest and oldest public cloud provider.
- **Azure** — Microsoft's public cloud, strong with Microsoft enterprises.
- **GCP (Google Cloud Platform)** — Google's public cloud, strong in analytics and AI.
- **Redshift** — AWS's data warehouse.
- **Synapse** — Azure's analytics/data warehouse service.
- **BigQuery** — GCP's serverless data warehouse.
- **EMR (Elastic MapReduce)** — AWS's managed Spark/big-data cluster service.
- **AWS Glue** — AWS's serverless ETL service and data catalog.
- **HDInsight** — Azure's managed Hadoop/Spark service.
- **Dataproc** — GCP's managed Spark/Hadoop service.
- **MSK (Managed Streaming for Kafka)** — AWS's managed Apache Kafka service.
- **Kinesis** — AWS's native streaming service.
- **Event Hubs** — Azure's Kafka-compatible streaming service.
- **Pub/Sub** — GCP's messaging/streaming service.
- **Dataflow** — GCP's stream/batch processing service based on Apache Beam.
- **Step Functions** — AWS's workflow orchestration service.
- **MWAA (Managed Workflows for Apache Airflow)** — AWS's managed Airflow service.
- **Data Factory** — Azure's ETL and orchestration service.
- **Cloud Composer** — GCP's managed Airflow service.
- **Purview** — Azure's data catalog and governance service.
- **DynamoDB** — AWS's managed NoSQL key-value database.
- **Cosmos DB** — Azure's managed multi-model NoSQL database.

## Object Storage
- **Object storage** — Serverless cloud storage that keeps long-term, persistent data as objects in buckets, accessed over an HTTP API.
- **Bucket** — The container that holds objects in object storage.
- **Object** — A stored item made of a key, the data itself and metadata.
- **Key** — An object's unique name, whose `/`-separated prefixes tools display as folders.
- **Metadata** — Descriptive information stored alongside an object's data.
- **Serverless** — A service where you never provision, size or patch servers and pay per use.
- **Simulated filesystem (flat namespace)** — A bucket that is one flat list of objects, with "folders" being only an abstraction built from key prefixes, as in S3.
- **Actual filesystem (hierarchical namespace)** — Storage with real directories stored as their own entries, enabling instant atomic renames, as in ADLS Gen2.
- **Atomic rename** — A folder rename done as one all-or-nothing metadata change.
- **POSIX-style ACLs** — File-system-style access control lists on directories and files.
- **11 nines (99.999999999%)** — S3's designed durability level.
- **Cold tier** — Cheaper storage class for rarely read data.
- **File storage** — Storage organized as a folder tree accessed through a file system (NFS, SMB, local disk).
- **Block storage** — Storage as raw fixed-size blocks attached as a disk under an OS or database.
- **MinIO** — An open-source, S3-compatible object store that runs in Docker.
- **AWS S3 (Simple Storage Service)** — AWS's object storage service, with a flat namespace and `s3://` addresses.
- **S3 directory bucket (S3 Express One Zone)** — An S3 bucket type with a real hierarchical namespace.
- **Glacier** — S3's archive storage tier.
- **Bucket policy** — A resource policy attached to an S3 bucket controlling access.
- **Azure Blob Storage** — Azure's general-purpose flat object storage.
- **Storage account** — The Azure resource that holds Blob/ADLS containers.
- **Container (Azure)** — Azure's equivalent of a bucket inside a storage account.
- **SAS token (Shared Access Signature)** — An Azure token granting limited, time-bound access to storage.
- **Azure RBAC** — Azure's role-based access control.
- **ADLS Gen2 (Azure Data Lake Storage Gen2)** — Azure Blob Storage with the hierarchical namespace enabled, tuned for analytics.
- **Hierarchical namespace** — The storage-account setting that gives ADLS Gen2 real directories.
- **abfss://** — The URI scheme Spark uses to address ADLS Gen2 paths.
- **GCS (Google Cloud Storage)** — GCP's object storage, addressed with `gs://`.
- **Storage classes (GCS)** — Standard, Nearline, Coldline and Archive tiers priced by how often data is read.
- **Uniform bucket-level access** — Recommended GCS setting where IAM alone controls bucket access.
- **Signed URL** — A time-limited URL granting access to a private object.
- **External table** — A table definition that queries files in object storage in place.
- **s3a://** — The URI scheme Spark uses to read S3.

## Remote Instances and Service Models
- **Remote instance** — A virtual machine hosted on the cloud.
- **Virtual machine (VM)** — A rented virtual computer with its own kernel, CPU, memory, disk and OS.
- **AWS EC2 (Elastic Compute Cloud)** — AWS's virtual machine service.
- **Azure Virtual Machines** — Azure's virtual machine service.
- **Google Compute Engine** — GCP's virtual machine service.
- **Google App Engine** — GCP's PaaS where you upload code and Google runs and scales it.
- **Elastic Beanstalk** — AWS's PaaS, equivalent to App Engine.
- **Azure App Service** — Azure's PaaS, equivalent to App Engine.
- **Instance type** — A named VM size such as `t3.micro`.
- **SSH (Secure Shell)** — Encrypted protocol for logging in to a remote machine.
- **Key pair** — Public/private key used to SSH into an EC2 instance.
- **RDP (Remote Desktop Protocol)** — Protocol for graphical remote login, mainly to Windows VMs.
- **IaaS (Infrastructure as a Service)** — Cloud model where you manage the OS and software and the provider manages hardware and virtualization.
- **PaaS (Platform as a Service)** — Cloud model where you manage only code and data.
- **SaaS (Software as a Service)** — Cloud model where you just use the software and the provider manages everything.

## EBS and Disk Storage
- **EBS (Elastic Block Store)** — Persistent block storage that can be attached to an EC2 instance.
- **Volume** — One EBS disk.
- **Instance store** — A temporary disk inside the host that is wiped when the instance stops.
- **Availability Zone (AZ)** — An isolated data center location within a region; an EBS volume attaches only within its AZ.
- **Multi-attach** — Ability of some `io2` volumes to attach to more than one instance.
- **EBS snapshot** — A point-in-time backup of a volume, stored in S3 behind the scenes.
- **gp3** — General Purpose SSD, the default EBS volume type.
- **io2 / io1** — Provisioned IOPS SSD volumes for busy databases.
- **IOPS (Input/Output Operations Per Second)** — A measure of disk I/O performance.
- **st1** — Throughput-optimized HDD for large sequential reads.
- **sc1** — Cold HDD for rarely accessed data.
- **EFS (Elastic File System)** — AWS's shared network file storage, mountable by many instances.
- **Azure Managed Disks** — Azure's equivalent of EBS.
- **GCP Persistent Disk** — GCP's equivalent of EBS.

## Snowflake Cortex Code and Workspaces
- **Snowsight** — Snowflake's web UI.
- **Cortex Code (CoCo)** — Snowflake's agentic AI assistant built into Snowsight for SQL development, data exploration and account management.
- **Agentic** — Able to carry out multi-step tasks, not just answer questions.
- **Diff** — A view of proposed code changes to review before applying.
- **Lineage** — The record of where data comes from and how it flows between objects.
- **SNOWFLAKE.COPILOT_USER** — Database role required to use CoCo.
- **SNOWFLAKE.CORTEX_USER** — Database role granting Cortex AI features.
- **SNOWFLAKE.CORTEX_AGENT_USER** — Least-privilege database role granting the Cortex Agents API.
- **Cross-region inference** — Setting allowing AI requests to be processed in another region; required for CoCo.
- **Snowflake Copilot** — Snowflake's older, limited SQL assistant replaced by CoCo.
- **Snowflake CoWork** — Snowflake's natural-language insights tool for business users.
- **AGENTS.md** — File holding persistent project instructions for CoCo.
- **Skills (CoCo)** — Custom instructions/workflows stored in `.snowflake/cortex/skills`.
- **RBAC (Role-Based Access Control)** — Access control where permissions are granted to roles; CoCo can only do what your role allows.
- **Default role** — The role a Snowflake user starts with, which CoCo always uses unless asked to switch.
- **Workspace** — An isolated virtual location in Snowflake or Databricks that holds a project's resources separately from other projects.
- **Snowflake Workspace** — A file-based in-browser IDE in Snowsight for SQL, Python, notebooks and dbt files.
- **Databricks Workspace** — The top-level Databricks environment with its own users, permissions, compute and URL.
- **Worksheets** — Snowflake's older single-tab SQL editors, replaced by Workspaces.
- **Git folders (Repos)** — Databricks' Git-connected folders.
- **Databricks Assistant** — Databricks' built-in AI assistant.

## Semantic Views
- **Semantic view** — A Snowflake object defining business entities, relationships, dimensions and metrics over physical tables so everyone queries consistent business concepts.
- **Logical tables** — The tables a semantic view involves.
- **Relationships** — How a semantic view's tables join.
- **Facts** — Row-level numeric values in a semantic view.
- **Dimensions** — Attributes used to group or filter.
- **Metrics** — Business calculations defined as aggregations.
- **Synonyms** — Plain-language alternative names that help AI map questions to metrics.
- **SEMANTIC_VIEW()** — Query function that requests dimensions and metrics from a semantic view, with Snowflake generating the joins.
- **Cortex Analyst** — Snowflake's AI that converts plain-English questions into SQL using semantic models.
- **Semantic layer** — The general concept of a shared business vocabulary over data, e.g. dbt Semantic Layer, LookML, Power BI semantic models.
- **Star schema** — Fact table surrounded by dimension tables, the base a semantic view sits on.
- **Single source of truth** — One authoritative definition or copy of data used everywhere.

## Snowflake Data Processing
- **Virtual warehouse** — Snowflake's sized, startable compute cluster that runs queries, separate from storage.
- **Standard warehouse** — Warehouse type for SQL queries, loads, transformations and BI.
- **Snowpark-optimized warehouse** — Memory-heavy warehouse type for Python/Java/Scala and ML work.
- **Multi-cluster warehouse** — Warehouse that automatically adds clusters when queries start queuing.
- **Credit** — Snowflake's unit of compute billing.
- **Auto-suspend / auto-resume** — Warehouse stops when idle (no charge) and restarts when a query arrives.
- **COPY INTO** — Snowflake command that bulk-loads staged files into a table.
- **MERGE** — SQL command that inserts, updates or deletes rows based on a match condition.
- **UDF (User-Defined Function)** — A custom function written in SQL, Python, Java, JavaScript or Scala.
- **Stored procedure** — A saved program of SQL/procedural logic that can be called.
- **Streams** — Snowflake objects that track inserts, updates and deletes on a table (change data capture).
- **CDC (Change Data Capture)** — Tracking and delivering row-level changes from a source.
- **Tasks** — Scheduled SQL/procedure runs that can be chained into DAGs.
- **DAG (Directed Acyclic Graph)** — A dependency graph of steps with no cycles.
- **Dynamic Tables** — Tables declared as a query plus freshness target (`TARGET_LAG`) that Snowflake keeps updated incrementally.
- **TARGET_LAG** — The maximum staleness allowed for a dynamic table.
- **Snowpipe** — Snowflake's serverless continuous file loading.
- **Snowpipe Streaming** — Snowflake's serverless row-level streaming ingestion.
- **Snowpark Container Services** — Running Docker containers on Snowflake-managed compute.
- **Cortex AI functions** — LLM functions callable in SQL, such as `AI_COMPLETE`, sentiment, summarize and translate.
- **Serverless compute (Snowflake)** — Snowflake-managed compute for Snowpipe, serverless Tasks, Dynamic Table refreshes and clustering, billed per use.
- **Automatic clustering** — Serverless Snowflake service that keeps table data organized by a clustering key.
- **Data controller** — Under GDPR, the party deciding why and how personal data is used.
- **Data processor** — Under GDPR, the party handling personal data on the controller's behalf.
- **GDPR (General Data Protection Regulation)** — EU privacy law governing personal data.
- **DPA (Data Processing Agreement)** — Contract between a data controller and processor.

## Snowpark
- **Snowpark** — Snowflake's code execution environment for Python, Java or Scala that runs inside Snowflake next to the data.
- **Snowpark DataFrame API** — PySpark-like DataFrame API that Snowflake translates into SQL.
- **Lazy evaluation** — Operations are only planned until an action like `.collect()` or `.show()` runs them.
- **session.table()** — Snowpark call returning a DataFrame for a table.
- **Snowpark Connect for Apache Spark** — Lets existing PySpark code run on Snowflake's engine with minimal changes.

## dbt
- **dbt (data build tool)** — The major ELT tool used with Snowflake, handling the Transform step in SQL inside the warehouse.
- **ETL (Extract, Transform, Load)** — Transforming data on a separate engine before loading it.
- **ELT (Extract, Load, Transform)** — Loading raw data first, then transforming it inside the warehouse.
- **Model (dbt)** — A `.sql` file containing one `SELECT` that dbt builds.
- **Materialization** — How dbt builds a model: view, table, incremental or ephemeral.
- **Ephemeral model** — A dbt model inlined as a CTE rather than built as an object.
- **ref()** — dbt function linking models so dbt knows build order and lineage.
- **Lineage DAG** — The dependency graph of models dbt draws automatically.
- **Jinja** — Templating language (`{{ ... }}`) adding variables, loops and macros to dbt SQL.
- **Macro** — A reusable Jinja function in dbt.
- **dbt tests** — Data-quality checks such as `unique`, `not_null`, `relationships` and `accepted_values`.
- **Incremental model** — A dbt model that processes only new rows using `is_incremental()`.
- **dbt run** — Builds the models.
- **dbt test** — Runs the data tests.
- **dbt build** — Runs models and tests together.
- **dbt docs generate** — Builds a browsable data catalog with the lineage graph.
- **dbt Core** — Free, open-source dbt command-line tool.
- **dbt Cloud** — Hosted dbt with web IDE, scheduler and CI.
- **dbt Projects on Snowflake** — Running dbt natively inside Snowflake Workspaces.
- **Adapter (dbt)** — Plugin such as `dbt-snowflake` or `dbt-postgres` that lets dbt talk to a specific warehouse.
- **externally-managed-environment** — pip error from PEP 668 when installing into a system-managed Python.
- **PEP 668** — Python standard letting OS distributions block `pip install` into the system Python.
- **Virtual environment (venv)** — An isolated Python environment for a project's libraries.

## Snowflake Command Line
- **Snowflake CLI (`snow`)** — Current, recommended Snowflake command-line tool for SQL, objects, deployments and stage uploads.
- **SnowSQL** — Older interactive Snowflake SQL shell being replaced by Snowflake CLI.
- **snow connection add** — One-time command that saves account, user, auth, role and warehouse settings.
- **snow sql** — Runs SQL from `-q` text or a `-f` file.
- **snow stage copy** — Uploads local files to a stage.
- **PUT** — SnowSQL command that uploads local files to a stage.
- **Internal stage** — Snowflake-managed storage location for files before `COPY INTO`.
- **config.toml / connections.toml** — Files under `~/.snowflake/` holding CLI connection settings.
- **snowflake-connector-python** — Python library for connecting to Snowflake from scripts.
- **pipx** — Installs a Python command-line app into its own private venv and puts its command on PATH.
- **uv tool install** — uv's equivalent of pipx for installing command-line apps.
- **PATH** — Environment variable listing directories the shell searches for commands.
- **ensurepath** — pipx command that adds its app folder to PATH.
- **Dependency conflict** — When installing one package downgrades shared libraries another package needs, breaking it.
- **pip check** — Verifies installed packages have compatible requirements.
