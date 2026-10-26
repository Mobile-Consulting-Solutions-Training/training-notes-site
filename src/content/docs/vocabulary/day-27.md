---
title: Day 27 Vocabulary
description: Glossary of terms and definitions from the Training 27 notes.
sidebar:
  order: 27
---

Vocabulary — Study Guide Day 27

Source: notes/Training 27.md

## Class Admin and Project Updates
- **Incremental processing** — Loading only new or changed data on each run instead of reprocessing everything.
- **AccessDenied (AWS)** — The AWS error naming the action, principal and resource that a policy did not allow.
- **events:ListRules** — The read-only EventBridge permission to list rules, granted to a student to verify their pipeline.
- **CloudWatch Logs** — AWS's log service, where a Glue job's output can show why a run seems stuck.

## Getting into Azure
- **Azure portal** — The web console for Azure at portal.azure.com.
- **Microsoft Authenticator** — Microsoft's phone app for approving sign-ins and generating MFA codes.
- **Multi-factor authentication (MFA)** — Signing in with a second proof, such as an Authenticator approval, on top of a password.
- **Number matching** — An MFA method where you type the number shown on the sign-in screen into the Authenticator prompt.
- **Email one-time code** — A sign-in code sent by email, different from an Authenticator code.
- **QR code enrollment** — Adding an account to Microsoft Authenticator by scanning the code shown during setup.

## The AWS to Azure Service Map
- **Azure Virtual Machines** — Azure's cloud VMs, the equivalent of AWS EC2.
- **Azure Event Hubs** — Azure's managed event-streaming service, the equivalent of Kinesis, with a Kafka-compatible endpoint.
- **Event Hubs namespace** — The Event Hubs container that is roughly equivalent to a Kafka cluster.
- **Event hub** — One stream inside an Event Hubs namespace, roughly equivalent to a Kafka topic.
- **Azure Data Factory (ADF)** — Azure's managed service for orchestrating pipelines and doing basic, low-code ETL.
- **AWS Glue** — AWS's managed ETL service with visual jobs and workflows, the closest AWS match to ADF.
- **Cloud Data Fusion** — Google Cloud's visual data-integration service, a rough GCP parallel to ADF.
- **Cloud Composer** — Google Cloud's managed Apache Airflow service.
- **Apache NiFi** — An open-source tool for building data flows in a visual drag-and-drop UI.
- **Azure Databricks** — The Databricks data and AI platform integrated into Azure.
- **Azure Synapse Analytics** — Azure's service combining a SQL data warehouse, Spark pools and pipelines.
- **Power BI** — Microsoft's business-intelligence tool for reports, charts and dashboards.

## Azure Storage: Blob Storage and ADLS Gen2
- **Blob (Binary Large Object)** — A single chunk of data of any kind, stored as one object in Azure Blob Storage.
- **Azure Blob Storage** — Azure's general object storage, similar to S3, with a flat namespace by default.
- **Storage account** — The top-level Azure storage resource, with a globally unique name, region, redundancy and settings.
- **Container** — The top-level folder in a storage account, the equivalent of an S3 bucket.
- **File system (ADLS Gen2)** — The ADLS Gen2 API's name for a container.
- **Flat namespace** — Storage where "folders" are just slashes in object names, a facade over one level of objects.
- **ADLS Gen1** — The original Hadoop-compatible Azure Data Lake Store, retired in February 2024.
- **ADLS Gen2 (Azure Data Lake Storage Gen2)** — A general-purpose v2 storage account with hierarchical namespace enabled, used as the data lake.
- **Hierarchical namespace (HNS)** — Real directories in Azure storage, enabling atomic directory operations and folder-level ACLs.
- **HDFS-compatible** — Exposing an API (such as WebHDFS) that Hadoop and Spark can use like HDFS, without being HDFS.
- **Atomic directory rename** — Renaming a whole directory as one all-or-nothing metadata operation, which Spark uses to commit output.
- **POSIX ACLs** — File-system-style read/write/execute permissions on ADLS Gen2 folders and files.
- **wasbs://** — The URI scheme Spark uses for plain Blob Storage.
- **adl://** — The URI scheme that was used for ADLS Gen1.

## Identity: Entra ID, Managed Identities, Tenants and Subscriptions
- **Microsoft Entra ID** — Microsoft's cloud identity service (formerly Azure Active Directory) for users, groups, service principals and managed identities.
- **Azure Active Directory (Azure AD)** — The former name of Microsoft Entra ID.
- **Service principal** — An Entra ID identity used by an application or service rather than a person.
- **Azure RBAC** — Azure's role-based access control, which authorizes what an identity can do on which resources.
- **Role assignment** — Granting a role to a principal at a scope, the core unit of Azure RBAC.
- **Scope** — The level a role assignment applies to: subscription, resource group or a single resource.
- **Managed identity** — An Entra ID identity Azure creates for a resource, with credentials Azure manages, so no secrets are stored.
- **Workload identity federation** — Exchanging a token from one identity provider (such as Entra ID) for credentials in another system without long-lived keys.
- **AssumeRoleWithWebIdentity** — The AWS STS call that swaps an OIDC token, such as one for an Azure managed identity, for temporary AWS credentials.
- **Tenant** — An organization's Entra ID directory, holding its users and identities and one or more subscriptions.
- **Tenant ID** — The GUID that identifies a tenant, needed to sign in to the right directory.
- **Home tenant** — The tenant where a user account was originally created, which differs from the tenant a guest is invited into.
- **Subscription** — A billing and access container inside a tenant that holds resource groups and resources.
- **Guest account** — A user invited into another organization's tenant from their own home tenant.

## Databricks, Delta Lake and Open Table Formats
- **Apache Spark** — The open-source distributed data-processing engine created at UC Berkeley's AMPLab.
- **Databricks** — The company founded by Spark's creators, offering a managed lakehouse platform built around Spark.
- **Enterprise support model** — Turning an open-source project into a business by selling an enterprise edition and support.
- **Delta Lake** — An open-source storage layer and table format (now a Linux Foundation project) adding ACID transactions and versioning on top of Parquet files in your own storage.
- **Delta format** — The Delta Lake table format: Parquet data files plus a `_delta_log` transaction log.
- **Delta table** — A table stored in the Delta format.
- **_delta_log** — The folder of JSON commit files and Parquet checkpoints that records every change to a Delta table.
- **Delta Live Tables (DLT)** — Databricks' declarative pipeline framework, renamed Lakeflow Declarative Pipelines in 2025.
- **Lakeflow** — Databricks' umbrella brand for Lakeflow Connect, Lakeflow Jobs and Lakeflow Declarative Pipelines.
- **Lakeflow Declarative Pipelines** — The current name of DLT, for building ETL pipelines from declared tables and expectations.
- **Spark Declarative Pipelines** — The open-source version of the declarative pipeline framework contributed to Apache Spark.
- **Open table format (OTF)** — A table format that stores data (usually Parquet) plus metadata giving ACID transactions, schema evolution and time travel on object storage.
- **Apache Iceberg** — The vendor-neutral open table format created at Netflix, used by Snowflake, AWS, BigQuery and Trino.
- **Apache Hudi** — An open table format created at Uber, focused on upserts, rarely asked about in interviews.
- **Iceberg manifest** — An Avro metadata file in Iceberg listing data files and their statistics.
- **Parquet part files** — The individual `.snappy.parquet` files inside a Parquet or table-format directory.
- **UniForm** — A Databricks feature that lets a Delta table also be read as an Iceberg table.

## Unity Catalog and Databricks Workspaces
- **Unity Catalog (UC)** — Databricks' central governance layer for permissions, auditing and lineage across workspaces.
- **Data governance** — Controlling who can access which data, and tracking how it is used and where it came from.
- **Databricks workspace** — An isolated Databricks environment with its own notebooks, compute and settings.
- **Metastore** — The Unity Catalog top-level container, shared by all attached workspaces in a region.
- **Hive metastore (hive_metastore)** — The legacy per-workspace metastore, shown as a separate catalog for backward compatibility.
- **Data lineage** — A record of which tables and jobs produced which data, tracked automatically by Unity Catalog.
- **ELT** — Extract, Load, Transform: loading raw data first (Bronze) and transforming it inside the platform.
- **Dev environment** — Where engineers build and test new work without affecting the business.
- **UAT (User Acceptance Testing)** — The test environment where combined work is checked and business users confirm it meets their needs.
- **Production environment** — The environment running live business workloads, where failures are top priority.
- **Rollback** — Returning a system to a previous working version after a failed deployment.

## Azure Synapse
- **Dedicated SQL pool** — Synapse's provisioned MPP data warehouse, formerly Azure SQL Data Warehouse.
- **Serverless SQL pool** — Synapse's pay-per-query SQL engine for querying files in the data lake.
- **Apache Spark pool** — Spark compute provided inside Synapse.
- **Synapse Studio** — The web UI for building and running Synapse SQL, Spark and pipelines.
- **Data warehouse** — A relational, SQL-queried store of related tables designed for analytics and joins.
- **$lookup** — MongoDB's aggregation stage for left outer joins between collections.

## Microsoft Fabric and All-in-One Platforms
- **Microsoft Fabric** — Microsoft's SaaS all-in-one analytics platform on OneLake, generally available since November 2023.
- **OneLake** — Fabric's single tenant-wide data lake, built on ADLS Gen2 with Delta tables.
- **Copilot in Fabric** — Fabric's built-in AI assistant, running on OpenAI models through Azure OpenAI.
- **Azure OpenAI** — Azure's service for running OpenAI models under Microsoft's cloud.
- **Tableau** — A leading paid BI tool, with a free Tableau Public edition for public work.
- **Tableau Public** — The free edition of Tableau whose workbooks are published publicly.
- **Power BI Desktop** — The free Windows app for building Power BI reports locally; sharing needs a paid license.
- **AWS QuickSight** — AWS's business-intelligence service.
- **Streamlit** — A free Python library for building data apps and charts, used in class for BI.
- **Talend** — A commercial data-integration platform sold as an all-in-one pipeline tool.
- **Pentaho** — A commercial data-integration and analytics suite.
- **Informatica** — A commercial enterprise data-integration platform with its own proprietary tooling.
- **Palantir** — A data-analytics company selling all-in-one platforms to government and commercial customers.
- **Palantir Foundry** — Palantir's main commercial data platform for pipelines and analytics.
- **Palantir Gotham** — Palantir's platform for government and defense customers.
- **Palantir AIP** — Palantir's AI platform built on its data products.

## Azure CLI Setup and Login
- **Azure CLI (az)** — Microsoft's command-line tool for managing Azure resources.
- **WSL (Windows Subsystem for Linux)** — A Linux environment inside Windows, where the class could install the Azure CLI.
- **winget** — The Windows package manager, used to install the Azure CLI in PowerShell.
- **az login** — The CLI command that signs you in to Azure through a browser.
- **Device code login** — Signing in with `az login --use-device-code` by entering a printed code on a Microsoft web page.
- **az account show** — The CLI command showing the current tenant and default subscription.
- **az account set** — The CLI command that chooses which subscription commands run against.
- **az account clear** — The CLI command that removes all cached accounts so you can log in fresh.
- **Default subscription** — The subscription the CLI uses when none is given, marked `isDefault: true`.

## Demo: Creating an ADLS Gen2 Storage Account
- **Resource group** — A management and lifecycle container for related Azure resources, deleted with everything inside.
- **Virtual Network (VNet)** — Azure's private network, the actual equivalent of an AWS VPC.
- **Environment variable** — A shell variable such as `$RG` or `$STORAGE` reused across commands, lost when the terminal closes.
- **Region** — The Azure location where a resource runs, such as East US or East US 2.
- **Globally unique name** — A storage-account name (3–24 lowercase letters and numbers) that no other Azure account uses.
- **StorageV2 (general-purpose v2)** — The standard storage-account kind; it becomes ADLS Gen2 only when hierarchical namespace is enabled.
- **SKU** — The pricing and performance option for a resource, such as Standard_LRS.
- **LRS (Locally redundant storage)** — Three copies of data in one datacenter, the cheapest redundancy option.
- **ZRS (Zone-redundant storage)** — Copies of data spread across availability zones in one region.
- **GRS (Geo-redundant storage)** — LRS plus an extra copy in a paired region.
- **HTTPS only** — A storage setting that rejects unencrypted HTTP requests.
- **Allow blob public access** — A storage setting that, when false, blocks anonymous public containers.
- **Shared key access** — Using storage account keys for access; disabling it forces Entra ID authentication.
- **--auth-mode login** — A CLI flag that makes storage commands use your Entra ID sign-in instead of account keys.
- **AuthorizationFailed** — The Azure error returned when an identity lacks a role allowing the requested action.
- **Object ID** — An identity's unique ID in Entra ID, used when assigning roles.
- **Contributor role** — The Azure role that can create and manage resources but cannot grant roles to others.
- **Storage Blob Data Contributor** — The Azure role allowing reading, writing and deleting blob data.

## Demo: Container, Directories and a First Upload
- **az storage fs** — The Azure CLI command group for ADLS Gen2 file systems, directories and files.
- **Immutability policy** — A WORM (write once, read many) setting that blocks changing or deleting blobs for a period.
- **Legal hold** — A compliance flag that blocks deleting or changing blobs until it is removed.
- **Storage browser** — The portal page for browsing, viewing, uploading and downloading files in a storage account.
- **ABFS (Azure Blob File System)** — The Hadoop/Spark driver for ADLS Gen2; `abfss` is its TLS-secured form.
- **abfss:// path** — The ADLS Gen2 URI `abfss://<container>@<account>.dfs.core.windows.net/<path>` used by Spark.
- **dfs endpoint** — The `<account>.dfs.core.windows.net` Data Lake endpoint, as opposed to the `blob` endpoint.

## A Quick Tour of Databricks
- **Launch workspace** — The Azure portal button that opens a Databricks workspace.
- **Databricks Genie** — Databricks' AI/BI feature for asking natural-language questions grounded in the workspace's real data.
- **Databricks Assistant** — The AI helper built into Databricks notebooks and editors.
- **Databricks notebook** — A Jupyter-like web document of cells that runs Python, SQL, Scala or R on attached compute.
- **Serverless compute** — Databricks-managed compute a notebook can use without creating a cluster, which requires Unity Catalog.
- **spark (built-in variable)** — The SparkSession Databricks predefines in every notebook, so no builder code is needed.
- **SparkSession** — The entry point to Spark, built with `SparkSession.builder...getOrCreate()` outside Databricks.
- **createDataFrame()** — A Spark method that builds a DataFrame from local data and column names.
- **display()** — The Databricks function that shows a DataFrame as an interactive table.
- **Databricks cluster** — A Spark cluster (driver plus workers) running the Databricks Runtime, similar to an EMR cluster.
- **All-purpose compute** — A Databricks cluster for interactive notebook work.
- **Job cluster** — A Databricks cluster that starts for one job run and shuts down after.
- **Databricks Runtime** — The versioned Spark-based software image a Databricks cluster runs.
- **SQL warehouse** — Databricks compute for SQL queries and catalog browsing, which must be running to use them.
- **Information schema** — A built-in schema of metadata views describing a catalog's objects.
- **system catalog** — The Unity Catalog catalog of system tables such as audit and billing logs.
- **Jobs & Pipelines** — The Databricks area for orchestration jobs and ETL pipelines.
- **Lakeflow Jobs (Databricks Jobs)** — Databricks' orchestration for scheduling and chaining notebooks, SQL and pipelines as tasks.
- **Photon** — Databricks' proprietary C++ vectorized engine that speeds up SQL and DataFrame operations, falling back to Spark when needed.
- **Vectorized execution** — Processing data in batches of column values at a time for CPU efficiency.
- **DBU (Databricks Unit)** — Databricks' unit of compute usage for billing.
- **Snowflake** — A cloud data platform known for simple SQL warehousing, Databricks' main competitor.
- **dbt-databricks** — The dbt adapter for running dbt SQL models on Databricks, widely used.

## Homework and the Final Project
- **Pipeline proposal** — An original concept for a data pipeline on your own data source, the first project homework.
- **High concept** — A plain-language framing of the business question for a non-technical audience.
- **Research pitch** — A presentation framed around a question and its answer rather than developer details.
- **Ingestion stage** — The part of a pipeline that brings raw data in from the source.
- **Processing stage** — The part of a pipeline that cleans and transforms data.
- **Multi-layer data lakehouse** — A lakehouse organized into Bronze, Silver and Gold layers.
