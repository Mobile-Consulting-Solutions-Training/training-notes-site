---
title: Day 28 Vocabulary
description: Glossary of terms and definitions from the Training 28 notes.
sidebar:
  order: 28
---

Vocabulary — Study Guide Day 28

Source: notes/Training 28.md

## Class Admin and Project Updates
- **Kaggle** — A website with a large free collection of public datasets (free account required), recommended for finding project data.
- **MovieLens** — A classic public movie-ratings dataset, available in several sizes such as 32 million ratings.
- **NYC taxi trip records** — A large public dataset of New York City taxi trips, suggested as a big dataset that complements Citi Bike.
- **Small-files problem** — The slowdown caused by writing data as huge numbers of tiny files, fixed by repartitioning into fewer, larger files.
- **Repartition** — Changing the number of partitions in a Spark DataFrame (for example before a write) to control how many output files are produced.
- **Target file size** — The recommended size for Parquet/Delta data files, roughly 128 MB to 1 GB each.
- **Multi-cloud architecture** — A pipeline that uses more than one cloud provider, such as S3 on AWS feeding ADLS and Databricks on Azure.
- **Workspace** — A container for one service's assets, such as a Databricks, Synapse, Log Analytics or Fabric workspace, not an Azure-wide concept.

## The Azure Pipeline Plan
- **ADLS Gen2 (Azure Data Lake Storage Gen2)** — Azure's data-lake storage: a storage account with hierarchical namespace, organized into containers and folders.
- **Azure Data Factory (ADF)** — Azure's managed service for building pipelines that move and orchestrate data between systems.
- **Azure Databricks** — The Databricks data and AI platform running on Azure, used here to transform data with Spark notebooks.
- **Container** — The top-level folder in an Azure storage account, the equivalent of an S3 bucket.

## Azure Data Factory
- **Activity** — One step in an ADF pipeline, such as copying data or running a notebook.
- **Copy activity (Copy data)** — The basic ADF activity that copies data from a source dataset to a sink dataset, optionally converting format but not transforming it.
- **Source** — The dataset a Copy activity reads from.
- **Sink** — ADF's term for the destination dataset a Copy activity writes to.
- **Data Flow** — An ADF activity type for visually designed transformations, run on Spark behind the scenes.
- **Control flow activity** — An ADF activity that adds logic, such as ForEach, If Condition, Wait or Execute Pipeline.
- **Pipeline** — A logical group of ADF activities that runs as a unit.
- **Linked service** — The connection and authentication details ADF uses to reach an external system, like a connection string.
- **Dataset** — A named pointer to specific data (folder, file, format) inside a linked service.
- **Integration runtime (IR)** — The compute that runs ADF activities and moves the data.
- **AutoResolveIntegrationRuntime** — ADF's default managed Azure integration runtime, which picks a region automatically.
- **Azure IR** — The fully managed cloud integration runtime used for cloud-to-cloud copies.
- **Self-hosted IR** — Integration-runtime software you install on your own machine to reach on-prem or private-network data.
- **Azure-SSIS IR** — An integration runtime for running existing SQL Server Integration Services packages in ADF.
- **Trigger** — What starts an ADF pipeline run: a schedule, tumbling window, storage event or manual start.
- **Schedule trigger** — An ADF trigger that runs a pipeline at set times.
- **Tumbling window trigger** — An ADF trigger that runs a pipeline for fixed, back-to-back time windows.
- **Storage event trigger** — An ADF trigger that fires when blobs arrive in Azure Blob/ADLS Gen2, not in S3.
- **ADF Studio** — The web UI for Data Factory, with Home, Author, Monitor and Manage sections.
- **Author (ADF)** — The ADF Studio section where you build pipelines, datasets and data flows.
- **Manage (ADF)** — The ADF Studio section for linked services, integration runtimes, triggers and Git settings.
- **Monitor (ADF)** — The ADF Studio section showing pipeline and activity runs and their status.
- **Publish all** — The ADF Studio button that saves draft changes to the live factory; unpublished resources can't be used elsewhere.
- **Debug run** — Running the current draft of an ADF pipeline for testing, without publishing or a trigger.
- **Validate** — The ADF check that reports configuration errors in a pipeline before running it.
- **Binary format** — An ADF dataset format that copies file bytes as-is without parsing them.
- **Preserve hierarchy** — A Copy activity setting that keeps the source folder structure in the destination.
- **Recursively** — A source setting that makes a Copy activity include files in all subfolders.
- **Microsoft Fabric** — Microsoft's newer all-in-one analytics platform, which ADF Studio promotes as an upgrade.
- **DMS (Database Migration Service)** — The service (on AWS, Azure and GCP) for migrating whole databases to a new database with little or no transformation.
- **AzCopy** — Microsoft's command-line tool for bulk copying files into and out of Azure Storage.
- **Azure Data Box** — Physical storage devices Microsoft ships to you for offline transfer of very large datasets.
- **AWS DataSync** — The AWS service for bulk transfers of files and objects between storage systems.

## AWS Access for ADF
- **Dedicated IAM user** — An IAM user created for one purpose, such as ADF reading S3, so admin credentials are never exposed.
- **AmazonS3ReadOnlyAccess** — The AWS managed policy that grants read-only access to S3.
- **Inline policy** — An IAM policy written directly on one user or role rather than as a reusable managed policy.
- **s3:ListBucket** — The permission to list objects in a bucket, granted on the bucket ARN.
- **s3:GetBucketLocation** — The permission to look up which region a bucket is in, granted on the bucket ARN.
- **s3:GetObject** — The permission to read objects, granted on the object ARN ending in `/*`.
- **Access key** — A long-lived AWS credential pair (access key ID + secret) that should be stored in a vault and rotated, never posted publicly.
- **Azure Key Vault** — Azure's service for storing secrets, keys and certificates that other services can reference.
- **Temporary credentials** — Short-lived AWS credentials (from STS or role assumption) that AWS recommends over long-lived access keys.
- **Broken pipe error** — A harmless shell message when output is piped to a command like `head` that closes early.
- **Eventually consistent (IAM)** — AWS IAM changes usually apply within seconds but can take a short time to propagate.

## Azure Identity and RBAC
- **Managed identity** — An identity Azure creates and manages for a resource so it can authenticate to other Azure services without stored keys.
- **System-assigned managed identity** — A managed identity tied to one resource's lifecycle, deleted when the resource is deleted.
- **Microsoft Entra ID** — Azure's identity service for users, groups and service principals.
- **Access control (IAM)** — The blade on an Azure resource where you view and add role assignments.
- **Role assignment** — Granting a role to an identity at a scope, the core of Azure RBAC.
- **Azure RBAC** — Azure's role-based access control system for granting permissions on resources.
- **Storage Blob Data Contributor** — The Azure role that allows reading, writing and deleting blob data in a storage account.
- **Control plane** — Management of the resource itself (create, configure, delete), governed by roles like Contributor and Owner.
- **Data plane** — Access to the data inside a resource, such as blobs, governed by roles like Storage Blob Data Contributor.
- **RBAC propagation delay** — The few minutes it can take an Azure role assignment to take effect after it's created.
- **Scope** — The level a role assignment applies to: subscription, resource group or a single resource.
- **Least privilege** — Granting only the permissions needed, at the narrowest scope.
- **403 Forbidden** — The HTTP status returned when an identity is authenticated but not authorized for the operation.
- **User Access Administrator** — An Azure role that allows managing role assignments, which students did not have.
- **Principal ID** — The object ID of an identity (such as a managed identity) used when creating role assignments.
- **Azure CLI extension** — An add-on package for `az` commands, such as the one needed for `az datafactory`.

## Azure Databricks Setup
- **Databricks workspace** — The Databricks environment where notebooks, compute, jobs and catalogs live.
- **Launch workspace** — The Azure portal button that opens the Databricks workspace UI.
- **Premium tier** — The Azure Databricks pricing tier required for Unity Catalog.
- **Serverless compute** — Databricks-managed compute that a notebook can attach to without creating a cluster.
- **Unity Catalog (UC)** — Databricks' governance layer for permissions, auditing and lineage on data and the storage behind it.
- **Metastore** — The top-level Unity Catalog container that holds catalogs for a region's workspaces.
- **Three-level namespace** — Unity Catalog's `catalog.schema.table` naming.
- **Workspace catalog** — The catalog automatically created with a new UC-enabled workspace, named after the workspace.
- **Catalog Explorer** — The Databricks UI for browsing catalogs, schemas, tables, volumes and their schemas, history and permissions.
- **Access Connector for Azure Databricks** — An Azure resource whose only purpose is to own a managed identity that Databricks uses to reach storage.
- **Storage credential** — A Unity Catalog object recording the identity (such as an Access Connector) used to authenticate to cloud storage.
- **External location** — A Unity Catalog object pairing a cloud storage path with a storage credential and controlling who may use it.
- **Force create** — Creating an external location even though its file-permission check didn't pass.
- **File events** — An optional external-location feature that tracks new files; skipped in class to get past a verification error.
- **External volume** — A Unity Catalog volume over files that stay in your own external storage location.
- **Managed volume** — A Unity Catalog volume whose files live in Unity Catalog's managed storage.
- **Databricks account** — The level above workspaces that holds identities, the metastore and all workspaces.
- **Workspace user** — An account identity that has been assigned to a specific workspace and can open it.

## Databricks Notebooks and Reading Data
- **Databricks notebook** — A web document of cells that runs Python, SQL, Scala, R or Markdown on attached compute.
- **Magic command** — A cell prefix such as `%sql`, `%python` or `%md` that sets that cell's language.
- **dbutils** — The Databricks utilities object, used here for `dbutils.fs.ls` to list files.
- **display()** — The Databricks function that shows a DataFrame as an interactive table that can be turned into a chart.
- **Volume path** — A path of the form `/Volumes/<catalog>/<schema>/<volume>/` for reading files through Unity Catalog.
- **abfss://** — The URI scheme for reading ADLS Gen2 directly, as `abfss://<container>@<account>.dfs.core.windows.net/`.
- **DBFS** — The Databricks File System; the `dbfs:` prefix on a volume path is optional.
- **multiLine option** — A Spark JSON option for files where one JSON document spans many lines.
- **recursiveFileLookup** — A Spark read option that reads files in all subfolders.
- **_metadata.file_path** — A hidden Spark column giving the source file of each row.
- **printSchema()** — A DataFrame method that prints column names, types and nesting.
- **Nested JSON** — JSON with objects and arrays inside objects, read by Spark as struct and array columns.
- **Struct / array column** — Spark column types that hold nested records and lists, valid in a DataFrame.
- **Schema (Unity Catalog)** — A container inside a catalog that holds tables, views and volumes, also called a database.
- **NameError** — The Python error raised when a cell uses a variable that an earlier, unrun cell was supposed to define.

## Bronze, Silver and Gold
- **Medallion architecture** — Layering data as Bronze (raw), Silver (cleaned and validated) and Gold (business aggregates).
- **Bronze layer** — Raw or minimally processed data plus load metadata such as source file and ingestion time.
- **Silver layer** — Cleaned, typed, validated and deduplicated data.
- **Gold layer** — Business-level aggregated tables ready for analytics, BI and AI.
- **Flatten** — Turning nested JSON into flat, top-level columns so it can be queried with SQL.
- **explode()** — A Spark function that turns each element of an array column into its own row.
- **struct.*** — Selecting all fields of a struct column so each becomes a top-level column.
- **Ingestion timestamp** — A column recording when a row was loaded, added with `current_timestamp()`.
- **Delta Lake** — An open table format that adds a transaction log, ACID transactions, schema enforcement and version history on top of Parquet files.
- **Delta table** — A table stored as Parquet data files plus a `_delta_log` transaction log.
- **_delta_log** — The folder of JSON commit files that records every change to a Delta table.
- **ACID transactions** — Guarantees (atomic, consistent, isolated, durable) that each write fully succeeds or fully fails.
- **Schema enforcement** — Delta's rejection of writes whose columns or types don't match the table.
- **overwriteSchema** — A Delta write option that allows an overwrite to change the table's columns or types.
- **mode("overwrite")** — A write mode that replaces a table's data in a full reload.
- **saveAsTable()** — A DataFrame write that registers the output as a named table in the catalog.
- **Managed table** — A Unity Catalog table whose files live in managed storage and are deleted with the table.
- **cast()** — Converting a column to another data type, which renames it unless you add an alias.
- **alias()** — Giving a column a name, used after a cast to keep the original name.
- **LongType (BIGINT)** — Spark's 64-bit integer type, not a string type.
- **from_unixtime()** — A Spark function converting epoch seconds to a timestamp string.
- **to_timestamp()** — A Spark function converting a string to a true `TIMESTAMP` column.
- **Epoch time** — A timestamp counted as seconds (or milliseconds) since Jan 1, 1970 UTC.
- **dropDuplicates()** — A Spark method that keeps one row per unique combination of the listed columns.
- **Data validation** — Filtering out bad rows, such as null station IDs or negative bike counts.
- **legacy_id** — The GBFS field holding a station's old numeric ID alongside its UUID-style `station_id`.
- **UNION ALL** — A SQL operator that stacks the results of two queries, used to compare layer row counts.
- **DESCRIBE HISTORY** — A Delta SQL command listing a table's versions and the operation that made each.
- **Table version** — A numbered snapshot of a Delta table created by each write, starting at version 0.
- **Time travel** — Querying an earlier version of a Delta table, as in `VERSION AS OF 0`.
- **CREATE OR REPLACE TABLE AS SELECT (CRTAS)** — SQL that rebuilds a table from a query, how Delta logs an overwrite `saveAsTable`.
- **dbt table materialization** — dbt's way of building a model as a table, using CREATE OR REPLACE TABLE AS SELECT.
- **DESCRIBE DETAIL** — A Delta SQL command that shows a table's storage location, size and file count.
- **date_trunc()** — A Spark function that rounds a timestamp down to a unit such as the hour.
- **groupBy / agg** — Grouping rows by a key and computing aggregates like sum, average and count.
- **countDistinct()** — An aggregate counting unique values, used for stations reporting.
- **Window function** — A calculation across a set of related rows (a window) without collapsing them.
- **Window.partitionBy().orderBy()** — Defining a window's groups and its ordering within each group.
- **row_number()** — A window function numbering rows 1, 2, 3 within each partition.
- **Latest record per key** — Keeping `row_number() = 1` over a window ordered by timestamp descending.
- **Stations reporting** — The number of distinct stations with a snapshot in a given hour.
- **Station capacity** — A station's total docks, roughly equal to bikes available plus docks available.

## Databricks Visualizations and Interviews
- **Databricks visualization** — A chart added to a `display()` result with the + button, such as a line chart.
- **Apache Spark** — The open-source distributed data-processing engine.
- **Databricks** — A managed platform around Spark that adds notebooks, Delta Lake, Unity Catalog, jobs and serverless compute.
- **Photon** — Databricks' optimized native query engine for faster Spark SQL and DataFrame work.
- **Lakeflow** — Databricks' jobs and declarative pipelines product, the next step after notebook pipelines.
- **MERGE** — A Delta command that updates matching rows and inserts new ones, useful for a latest-status table.
- **Auto Loader** — Databricks' incremental file ingestion that reads only new files.
