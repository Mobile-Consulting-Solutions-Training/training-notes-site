---
title: Study Guide - Day 27
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 27: Getting into Azure"
sidebar:
  order: 270
---

Study Guide - Day 27 (source: notes/Training 27.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**The AWS → Azure Map.** S3 → Azure Storage (**ADLS Gen2**), IAM → **Entra ID** + Azure RBAC, EC2 → **Virtual Machines**, Kinesis → **Event Hubs**, Step Functions / Airflow → **Azure Data Factory (ADF)**, Glue / EMR → **Azure Databricks**, Redshift → **Synapse Analytics**, QuickSight → **Power BI**. It's a memory aid, not a one-to-one match: AWS IAM does identity and permissions, while Azure splits them into Entra ID (who you are) and RBAC (what you can do).

**Blob Storage vs ADLS Gen2.** A **blob** (Binary Large Object) is one object in a **container**, inside a **storage account** (≈ S3 object, bucket, account). Plain Blob Storage has a **flat namespace**: folders are a facade over long keys with slashes. **ADLS Gen2** is a general-purpose v2 storage account with the **hierarchical namespace** turned on (`--hns true`): real directories, **atomic directory rename** (one metadata operation instead of copy + delete per file, which matters because Spark commits by renaming a temp folder) and POSIX-style **ACLs**. Gen1 was HDFS-compatible and was **retired in February 2024**. Evan's rule: on your profile, always say **ADLS Gen2**, never "Blob Storage."

**Identity.** **Microsoft Entra ID** (formerly Azure AD) holds users, groups, service principals and **managed identities**, and handles sign-in and MFA (number matching in Microsoft Authenticator). **Azure RBAC** authorizes: a **role assignment** = principal + role + scope. The **tenant** is the organization's Entra directory; **subscriptions** inside it are billing and access containers; **resource groups** hold resources. A **managed identity** is an identity Azure creates for a resource, with credentials Azure manages, so no secrets in code; it can even reach AWS through workload identity federation.

**Other Services.** **Event Hubs** = managed Kafka (namespace ≈ cluster, event hub ≈ topic; Kafka clients use the Kafka endpoint on port 9093 with SASL_SSL). **ADF** = orchestration plus basic low-code ETL with a drag-and-drop canvas; closest AWS match is Glue. **Synapse** = SQL warehouse (dedicated and serverless SQL pools) + Spark pools + pipelines in one studio; many teams now prefer Databricks or Fabric.

**Databricks and Delta.** Databricks was founded (2013) by the creators of Spark (UC Berkeley AMPLab). Spark alone processes but doesn't store, so Databricks added **Delta Lake**: an open-source **table format** (Parquet + a `_delta_log` transaction log) over your own ADLS/S3, now a Linux Foundation project. **DLT** was renamed **Lakeflow Declarative Pipelines**; Lakeflow is the umbrella brand. About 30-40% of interviews Evan sees involve Databricks.

**Open Table Formats.** **Delta** (Databricks, `_delta_log/`), **Iceberg** (Netflix, `metadata/` with Avro manifests; vendor-neutral, used by Snowflake, AWS, BigQuery, Trino) and **Hudi** (Uber, `.hoodie/`; just know it exists). All three are open source. Each is Parquet data plus metadata that tracks files per version, which gives **ACID**, schema evolution and **time travel** on object storage.

**Unity Catalog and Environments.** **Unity Catalog (UC)** is the governance layer for Databricks: one **metastore** per region shared by many workspaces, with central `GRANT`s, auditing and **lineage**. It shares data and permissions across workspaces, not clusters (compute stays in one workspace). `hive_metastore` is the legacy per-workspace catalog. **Serverless compute requires UC.** A **workspace** is an isolated Databricks environment. Production projects use **dev**, **UAT** (User Acceptance Testing) and **prod** environments.

**Fabric and BI.** **Microsoft Fabric** (GA November 2023) is a SaaS all-in-one platform on **OneLake** (built on ADLS Gen2, Delta format): Data Factory, Spark, warehouse, real-time, data science and Power BI with **Copilot**. It doesn't include Databricks. All-in-one enterprise tools: Talend, Pentaho, Informatica, **Palantir** (Foundry). For BI, learn **Power BI** (free Desktop) or **Tableau** (free Tableau Public).

**The Demo.** Azure CLI install (`curl ... | sudo bash` on WSL, `winget` on Windows), `az login` (`--tenant`, `--use-device-code`), `az account show`. Variables for student ID, resource group (`rg-adls-<name>`), region, a globally unique lowercase storage name, container. `az group create`, then `az storage account create --kind StorageV2 --hns true --allow-shared-key-access false` (so every data command needs `--auth-mode login`). `az storage fs create` for the `bronze` container, `fs directory create` for `customers/raw`, `fs file upload/list/download`. Path for Spark: `abfss://<container>@<account>.dfs.core.windows.net/<path>`. Errors: wrong tenant, MFA token expired, **AuthorizationFailed** until Evan granted **Contributor**, and an empty `$STORAGE` variable.

**Databricks Tour.** Genie (AI over Unity Catalog metadata), serverless notebooks, **`spark` is predefined** (no SparkSession needed), Catalog, Jobs & Pipelines (Lakeflow Jobs + ETL pipelines), Compute. **Photon** = Databricks' C++ vectorized engine for SQL/DataFrame operators, falling back to Spark for the rest. Databricks (more control, Python/SQL, your storage) vs **Snowflake** (simpler, SQL-first, managed storage).

**Final Project.** Your own data source and an original pipeline on AWS or Azure, Bronze/Silver/Gold lakehouse, pitched to non-technical management: high concept first, then ingestion, processing, storage and analytics. Five to 10 minutes.

---

# Part 2: Cheat Sheet

## AWS → Azure
- S3 → ADLS Gen2 · IAM → Entra ID + RBAC · EC2 → VMs · Kinesis → Event Hubs
- Step Functions → ADF · Glue/EMR → Databricks · Redshift → Synapse · QuickSight → Power BI

## Storage
- Storage account → container → blob · flat namespace (facade folders) vs hierarchical namespace (real dirs)
- ADLS Gen2 = StorageV2 + `--hns true` · atomic rename · POSIX ACLs · Gen1 retired Feb 2024
- Paths: `wasbs://` (Blob) · `abfss://<container>@<account>.dfs.core.windows.net/` (Gen2)
- Redundancy: LRS · ZRS · GRS · GZRS · name: lowercase, 3-24 chars, globally unique

## Identity
- Entra ID = authentication · RBAC = authorization (principal + role + scope)
- Tenant (directory) → subscription (billing) → resource group (lifecycle) → resource
- Contributor (create/manage, can't grant) · Storage Blob Data Contributor (data access)
- Managed identity = no secrets in code · `AuthorizationFailed` = Azure's AccessDenied

## Databricks
- Delta Lake = open table format (Parquet + `_delta_log`) · DLT → Lakeflow Declarative Pipelines
- OTFs: Delta (Databricks) · Iceberg (vendor-neutral) · Hudi (rarely asked)
- Unity Catalog: one metastore per region, shared permissions/lineage, not shared clusters
- Serverless needs UC · `hive_metastore` = legacy · `spark` predefined · Photon = C++ engine
- Clusters: all-purpose · job · serverless · environments: dev / UAT / prod

## Platforms
- Synapse = SQL pools + Spark pools + pipelines · Fabric = SaaS on OneLake + Power BI + Copilot
- Databricks (control) vs Snowflake (simplicity) · dbt-databricks is common

## CLI
- `az login --tenant <id>` · `az account show` / `set --subscription`
- `az group create` · `az storage account create ... --hns true`
- `az storage fs create` / `fs directory create` / `fs file upload` (all `--auth-mode login`)

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What's the difference between Azure Blob Storage and ADLS Gen2?
A: ADLS Gen2 is Blob Storage with a hierarchical namespace turned on. That gives real directories, atomic directory renames and folder-level ACLs, so it's the storage you use for a data lake.

Q: What is a hierarchical namespace?
A: Real directories in object storage. A folder is an actual object in the file system, so renaming or deleting it is one metadata operation instead of copying or deleting every file under it.

Q: Why does atomic rename matter for Spark?
A: Spark commits its output by writing to a temporary folder and renaming it to the final folder. On flat storage that's thousands of copies and deletes and not atomic, so a crash can leave a half-moved result.

Q: How do you create an ADLS Gen2 account?
A: Create a general-purpose v2 storage account with hierarchical namespace enabled, using `--kind StorageV2 --hns true` in the CLI or the checkbox on the Advanced tab in the portal.

Q: Should you write "Azure Blob Storage" on your profile?
A: No. Always say ADLS Gen2. Saying Blob Storage makes it sound like you didn't use a real data lake.

Q: What is the ADLS Gen2 path format for Spark?
A: abfss, colon slash slash, container at storage account dot dfs dot core dot windows dot net, then the path. The extra s means TLS, and it uses the dfs endpoint, not blob.

Q: What is Microsoft Entra ID?
A: Microsoft's cloud identity service, formerly Azure Active Directory. It holds users, groups, service principals and managed identities, and handles sign-in and MFA.

Q: What's the difference between Entra ID and Azure RBAC?
A: Entra ID authenticates who you are. RBAC authorizes what you can do: a role assignment gives a principal a role at a scope, like Contributor on a subscription.

Q: What's the difference between a tenant and a subscription?
A: The tenant is the organization's Entra ID directory with all its users. A subscription is a billing and access container inside the tenant that holds resource groups and resources. A tenant can have many subscriptions.

Q: What is a resource group?
A: A management and lifecycle container for related resources. You can set permissions on it, see its costs, and delete it to delete everything inside. It's not a network like a VPC; Azure's VPC is a VNet.

Q: What is a managed identity?
A: An Entra ID identity that Azure creates for a resource, like a data factory or VM, with credentials Azure manages. Your code never stores a password or key.

Q: What do Kinesis, EC2, Step Functions and Redshift map to in Azure?
A: Event Hubs, Virtual Machines, Azure Data Factory and Synapse Analytics.

Q: What is Azure Event Hubs?
A: A managed event streaming service, basically Kafka in the cloud. A namespace is like a Kafka cluster and an event hub is like a topic, and Kafka clients can connect to it directly.

Q: What is Azure Data Factory?
A: Azure's orchestration tool that also does basic low-code ETL with a drag-and-drop pipeline canvas. It's used for the jobs you'd do with Step Functions or Airflow on AWS.

Q: What is Delta Lake?
A: An open-source table format and storage layer created by Databricks. Data stays in your own cloud storage as Parquet files plus a _delta_log transaction log, which adds ACID transactions and time travel.

Q: What are the three open table formats?
A: Delta Lake, Apache Iceberg and Apache Hudi. Delta is native to Databricks, Iceberg is the vendor-neutral one used by Snowflake, AWS and BigQuery, and Hudi is rarely asked about.

Q: What does Unity Catalog do?
A: It's the governance layer for Databricks. One metastore per region is shared by many workspaces, with central permissions, auditing and lineage on catalogs, schemas and tables.

Q: Does Unity Catalog let workspaces share clusters?
A: No. Compute still belongs to one workspace. What's shared is the metastore, so every attached workspace sees the same tables and permissions without copying data.

Q: What are dev, UAT and prod?
A: Separate environments. Dev is where engineers build, UAT is User Acceptance Testing where the combined work is tested before release, and prod runs the live business.

Q: What is Photon?
A: Databricks' vectorized query engine written in C++. It speeds up SQL and DataFrame operations like scans, joins and aggregations, and falls back to normal Spark for anything it doesn't support.

Q: Do you need to create a SparkSession in a Databricks notebook?
A: No. The `spark` variable is already defined in every Databricks notebook.

Q: Can you use serverless compute with Unity Catalog?
A: Yes. In fact serverless compute requires Unity Catalog.

Q: What is Microsoft Fabric?
A: Microsoft's SaaS all-in-one analytics platform built on OneLake. It packages Data Factory, Spark, a warehouse, real-time analytics and Power BI with Copilot. It doesn't include Databricks.

Q: Databricks or Snowflake, what's the difference?
A: Databricks started as a Spark lakehouse platform: more control, Python and SQL, your own storage. Snowflake started as a cloud SQL warehouse: simpler, with less control and managed storage.

Q: What does AuthorizationFailed mean in Azure?
A: Your identity has no role that allows the action. The message names the object ID, the action and the scope, which is what an admin needs to grant a role like Contributor.

Q: What should a final-project presentation cover?
A: A high-concept business question for non-technical management, then the pipeline: ingestion, processing, Bronze/Silver/Gold storage and the analytics that answer the question, using your own data source.
