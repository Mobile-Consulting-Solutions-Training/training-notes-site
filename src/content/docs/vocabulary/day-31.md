---
title: Day 31 Vocabulary
description: Glossary of terms and definitions from the Training 31 notes.
sidebar:
  order: 31
---

Vocabulary — Study Guide Day 31

Source: notes/Training 31.md
Note: Event Hubs section is a preview; it will be expanded later.

## Class Admin and Cloud Costs
- **AccessDenied** — The error returned when an identity lacks permission for an action, here likely caused by the org-wide permission removal.
- **GCP free trial** — Google Cloud's sign-up offer of $300 in credit for new accounts.
- **Budget alert** — A cloud billing setting that emails you when spend reaches a threshold.
- **Spend forecast** — A cloud billing estimate of future spend that can trigger an alert before the threshold is actually hit.

## Small-Business Analytics On-Prem
- **Multi-source analytics** — Combining several sources with different APIs and permissions into one model that feeds one dashboard.
- **On-prem (on-premises)** — Running on hardware you own rather than in a cloud provider.
- **Control node** — The cluster machine used to manage and coordinate the other nodes.
- **Worker node** — A cluster machine that does the actual processing work.
- **Batch ingestion job** — A periodic job that pulls a batch of data from a source and writes it to the Bronze layer.
- **Medallion architecture (Bronze / Silver / Gold)** — Layering data as raw (Bronze), cleaned and validated (Silver) and aggregated business-ready (Gold).
- **VPS (Virtual Private Server)** — A computer in the cloud, like an EC2 instance but from any provider, hooked up to DNS to host a website.
- **DNS (Domain Name System)** — The system that maps domain names to server IP addresses.
- **Cloudflare** — A DNS and web infrastructure provider used to register and route a domain.
- **MinIO** — Locally hosted object storage, in the style of S3 or ADLS, that speaks the S3 API.
- **S3 API** — Amazon S3's object storage interface, which MinIO implements so S3 tools work by changing the endpoint URL.
- **Object storage** — Storage of files as objects in buckets, the modern replacement for HDFS in a data lake.
- **HDFS (Hadoop Distributed File System)** — Hadoop's distributed file storage spread across DataNodes, now considered somewhat outdated.
- **Hive Metastore** — The Hive service that stores table metadata for files in HDFS.
- **DuckDB** — An OLAP SQL query engine that runs in-process on a local machine with no server or cloud hosting.
- **OLAP (Online Analytical Processing)** — Analytical querying such as aggregations and `GROUP BY` over large datasets.
- **In-process database** — A database that runs as a library inside your program rather than as a separate server.
- **Columnar / vectorized execution** — Processing data column by column in batches, which makes aggregations fast.
- **Apache Iceberg** — An open table format that adds schema, snapshots, ACID commits, time travel and partition evolution on top of data files.
- **Open table format** — A specification for managing a set of data files as a versioned table independent of any one engine.
- **ACID commit** — An atomic, consistent, isolated and durable write, so concurrent writers can't corrupt each other's changes.
- **Snapshot (Iceberg)** — A saved version of a table's state after a write.
- **Time travel** — Querying a table as it was at an earlier snapshot.
- **Partition evolution** — Changing a table's partitioning scheme without rewriting the existing data.
- **Catalog (Iceberg)** — The service that points to each table's current metadata file and makes commits atomic.
- **Lakekeeper** — An open-source, user-friendly Apache Iceberg REST catalog that can also handle access control.
- **Iceberg REST catalog** — Iceberg's standard HTTP API for catalogs, letting any engine share the same tables without a special connector.
- **Metadata files (Iceberg)** — Files holding a table's schema, partitions and list of snapshots, with a new one created on every write.
- **Glue Data Catalog** — The AWS metadata catalog, playing the role Lakekeeper plays on-prem.
- **Unity Catalog** — The Databricks catalog, playing the role Lakekeeper plays on-prem.
- **Trino** — A distributed SQL query engine that can read Iceberg tables.
- **Streamlit** — A Python framework for building web dashboards, used here to read Gold data.
- **Microsoft Fabric** — Microsoft's all-in-one cloud analytics platform that it now steers new projects toward.

## Azure Synapse Analytics
- **Azure Synapse Analytics** — Azure's analytics workspace combining SQL warehousing, Spark and pipelines; essentially the Azure equivalent of Redshift.
- **Serverless SQL pool** — Synapse's built-in, nothing-to-provision engine that queries files in ADLS with T-SQL and bills per TB processed.
- **Dedicated SQL pool** — Synapse's provisioned MPP cluster warehouse (formerly Azure SQL Data Warehouse), billed per hour while running.
- **DWU (Data Warehouse Units)** — The size setting that determines a dedicated SQL pool's compute.
- **Pause (dedicated pool)** — Stopping a dedicated SQL pool so it stops incurring compute charges.
- **Apache Spark pool** — Synapse's managed Spark for running notebooks.
- **Synapse Pipelines** — Azure Data Factory built into Synapse.
- **Synapse Studio** — The web UI for all Synapse features.
- **T-SQL (Transact-SQL)** — Microsoft's SQL dialect used by Synapse SQL pools.
- **Per TB processed billing** — Charging by the bytes your queries read (about $5/TB in serverless), not by the bytes stored.
- **Serverless SQL processing limit (cost control)** — A Synapse setting that caps daily, weekly and monthly TB processed to cap spend.
- **Partition pruning** — Filtering on partition folders so whole folders are skipped and less data is scanned.
- **MPP (Massively Parallel Processing)** — A shared-nothing architecture where data and queries are split across many nodes that process their slices in parallel, used by all modern cloud warehouses.
- **Node** — One machine in a cluster, the preferred term over "server" in cluster talk.
- **Shared-nothing architecture** — A design where each node has its own CPU, memory and storage.
- **Leader node** — The MPP node that splits a query into pieces and combines the partial results.
- **Distribution key** — The column that decides which node each row lives on, which matters because moving data between nodes is expensive.
- **Supercomputer** — The top-end extreme of a very large MPP cluster.
- **Managed resource group** — A resource group Azure creates and fills itself for a service's internal resources; leave it blank.
- **Primary storage (Synapse)** — The ADLS Gen2 account and container a Synapse workspace uses for its own files.
- **ADLS Gen2 (Azure Data Lake Storage Gen2)** — Azure's data lake storage, used as the lake and as Synapse's primary storage.
- **File system (container)** — A top-level folder in an ADLS Gen2 account, such as `bronze` or `synapse`.
- **Regional capacity restriction** — An Azure region or subscription refusing new resources (here new SQL servers), fixed by choosing another region or requesting quota.
- **Quota** — A subscription limit on how many resources of a type can be created.
- **Latency** — The delay added when data must travel a long physical distance.
- **Egress** — Data transferred out of a region, which is billed.
- **Data residency / sovereignty** — Laws governing which country certain data, especially personal data, may be stored or processed in.
- **GDPR (General Data Protection Regulation)** — The EU's strict personal-data law covering consent, the right to be forgotten and moving data out of the EU.
- **CCPA / CPRA (California Consumer Privacy Act / California Privacy Rights Act)** — California's data-privacy law, the strictest in the US, which most companies apply nationwide.
- **LGPD (Lei Geral de Proteção de Dados)** — Brazil's GDPR-style data-protection law.
- **Data hub (Synapse Studio)** — The hub for browsing linked storage and workspace databases.
- **Develop hub** — The Synapse Studio hub for SQL scripts, notebooks and data flows.
- **Integrate hub** — The Synapse Studio hub for pipelines.
- **Monitor hub** — The Synapse Studio hub showing run history for pipelines, SQL requests and Spark.
- **Manage hub** — The Synapse Studio hub for SQL pools, Spark pools, linked services, access control and cost control.
- **Linked storage / linked service** — A connection that lets Synapse reach external storage or services such as the ADLS account.
- **Smoke test** — A minimal query or check proving a system can run anything at all.
- **`@@VERSION` / `DB_NAME()` / `GETUTCDATE()`** — T-SQL functions returning the SQL version, current database and current UTC time.
- **`master` database** — The system database every serverless pool starts in, where you can't create your own objects.
- **CREATE DATABASE / USE** — Creating your own database and switching to it, the habit needed before creating views or other objects.
- **OPENROWSET(BULK ...)** — A T-SQL function that reads files in the lake as if they were a table, without loading or copying them.
- **FORMAT option (OPENROWSET)** — The file-type setting for OPENROWSET; serverless supports `PARQUET`, `DELTA` and `CSV` but not `JSON`.
- **JSON_VALUE / JSON_QUERY** — T-SQL functions extracting a scalar value or an object/array from a JSON string.
- **OPENJSON** — A T-SQL table-valued function that parses a JSON string into rows and columns.
- **CROSS APPLY** — A T-SQL join that runs a table-valued function such as OPENJSON for each row.
- **0x0b terminator trick** — Reading each JSON file as one big CSV text column using terminators that never occur, then parsing it with JSON functions.
- **Semi-structured data** — Nested data like JSON that must be flattened to top-level columns to work in SQL.
- **Structured data** — Data in flat rows and columns with a fixed schema, as SQL engines and Parquet require.
- **Parquet** — A columnar, compressed, schema-carrying file format that SQL engines read natively and cheaply.
- **View** — A saved query that stores no data and re-scans its source on every read; in Synapse serverless it is saved in the database and is not session-scoped.
- **CREATE OR ALTER VIEW** — T-SQL that creates a view, or replaces it if it already exists.
- **dbo** — The default schema in a SQL Server–family database.
- **Materialized view** — A view that stores its results; not supported in serverless SQL pools, only in dedicated pools and Databricks.
- **External table** — A table definition that points at files in the lake without storing data itself.
- **CETAS (CREATE EXTERNAL TABLE AS SELECT)** — Synapse serverless syntax that writes a query's result as new Parquet files in ADLS, effectively a Gold table.
- **External data source / external file format** — Synapse objects defining where external files live and how they are formatted, required before CETAS.
- **Completeness check** — A Gold-layer check flagging data, such as a snapshot with far fewer stations than normal, that falls below an expected threshold.
- **Data anomaly** — An unexpected value or pattern in data that should be investigated.

## Databricks: Bronze JSON to Silver Parquet
- **Flattening** — Pulling nested fields up to top-level columns so every row has the same schema level.
- **printSchema** — A Spark method that prints a DataFrame's (possibly nested) schema.
- **explode** — A Spark function that turns each element of an array into its own row.
- **cast / alias** — Spark column methods that change a column's data type and rename it.
- **from_unixtime / to_timestamp / to_date** — Spark functions converting epoch seconds to a timestamp string, a timestamp, and a date.
- **Validation filters** — Filters like `IS NOT NULL` and counts `>= 0` that drop invalid rows, similar to DLT expectations.
- **Great Expectations** — An open-source Python data-validation framework.
- **dropDuplicates** — A Spark method removing duplicate rows based on the given columns.
- **coalesce** — A Spark method reducing the number of partitions, and so output files, without a full shuffle.
- **Small-files problem** — Many tiny files slowing queries down, avoided by writing fewer medium-sized files.
- **write.mode("overwrite")** — A Spark write mode that replaces existing data at the target path.
- **abfss://** — The URI scheme for securely accessing ADLS Gen2 from Spark.
- **GBFS (General Bikeshare Feed Specification)** — The JSON feed standard the Citi Bike data comes from.
- **ADF (Azure Data Factory)** — Azure's data integration service, used to copy Bronze data from S3 into ADLS.

## Event Hubs (Preview)
- **Azure Event Hubs** — Azure's managed event-streaming service, comparable to Kinesis Data Streams, that works with Kafka syntax by changing the endpoint.
- **Kafka protocol (port 9093)** — Event Hubs' Kafka-compatible endpoint that existing Kafka producers and consumers can connect to.
- **Kafka producer / consumer** — Client programs that write events to and read events from a stream.
- **bootstrap.servers** — The Kafka setting naming the broker endpoint, set to the Event Hubs namespace host on port 9093.
- **SASL_SSL** — The Kafka security protocol of SASL authentication over an encrypted TLS connection, required by Event Hubs.
- **SASL PLAIN** — The SASL mechanism using a username and password, with Event Hubs username `$ConnectionString`.
- **Connection string** — The namespace credential used as the Kafka password, a secret that belongs in Key Vault or a secret scope.
- **Key Vault** — Azure's service for storing secrets, keys and certificates.
- **Namespace (Event Hubs)** — The Event Hubs container, equivalent to a Kafka cluster.
- **Event hub** — One stream inside a namespace, equivalent to a Kafka topic or a Kinesis stream.
- **Partition** — An ordered subdivision of a stream for parallelism, equivalent to a Kinesis shard.
- **Consumer group** — A named group of readers that tracks its own position in the stream.
- **Offset / sequence number** — The position of an event within a partition.
- **Kinesis Data Streams** — The AWS managed streaming service equivalent to Event Hubs.
