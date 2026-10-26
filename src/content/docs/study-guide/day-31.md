---
title: Study Guide - Day 31
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 31: Azure Synapse Analytics and Databricks Bronze to Silver"
sidebar:
  order: 310
---

Study Guide - Day 31 (source: notes/Training 31.md, notes/azure-synapse-citibike-walkthrough.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Class Admin.** Student AWS permissions were revoked over cloud spending; requests now go through the company admin. Stop anything you don't need. A student's GCP tip: $300 free credit, set a **budget alert** and forecast alerts, test locally first. Profile narratives were "a very good foundation".

**Evan's Small-Business Analytics Design.** Problem: video stats spread across five social sites, plus store sales to join later. Lesson: "The best analytics platform is not necessarily the most functional and not necessarily the cheapest. It is the one that provides what the business needs in the way the business needs it." He rejected Microsoft Fabric because he already owns a 5-node on-prem cluster. Pipeline: one batch ingestion job per source → **MinIO** Bronze → incremental Silver → Gold in **Iceberg** tables tracked by **Lakekeeper** → **DuckDB** → Streamlit. Some APIs (X) cost a lot, so available data depends on budget.

**On-Prem Building Blocks.** **VPS** = virtual private server, an EC2-like computer in the cloud from any provider. **MinIO** = locally hosted object storage that speaks the S3 API (like hosting ADLS yourself); with Iceberg it replaces the old HDFS + Hive route. **DuckDB** = an in-process OLAP SQL engine (the SQLite of analytics), columnar and fast on one machine, reads Parquet/CSV/JSON directly; alone it's just an engine. **Iceberg** adds the table layer (schema, snapshots, ACID, time travel). The **catalog** (Lakekeeper, Glue, Unity) points to each table's current metadata file and makes commits atomic; the Iceberg **REST catalog** API lets any engine share the same tables.

**Azure Synapse.** "Basically the Azure equivalent of Redshift." An analytics workspace with a **serverless SQL pool** (query ADLS files with T-SQL, ~Athena), a **dedicated SQL pool** (provisioned MPP warehouse, ~provisioned Redshift), **Spark pools**, **Pipelines** (ADF inside) and **Synapse Studio**. Considered the older way vs Databricks, and Microsoft steers new work to Fabric, but still used.

**Serverless vs Dedicated.** Serverless: nothing to provision, data stays in ADLS, billed **per TB processed** (~$5/TB), no materialized views, low risk. Dedicated: you pick a DWU size, data loaded into the pool, billed per hour even idle (pause it), supports materialized views, high risk for class. Billing counts bytes read, not stored, so querying 1 GB a thousand times ≈ 1 TB ≈ $5. Keep it cheap: Parquet, select only needed columns, partition pruning, aggregated tables, a cost-control processing limit.

**MPP (interview question).** Massively Parallel Processing: an architectural system, not a query engine. A shared-nothing setup where data is spread across **nodes**, each processes its slice in parallel, and a leader combines the results; scale by adding nodes; moving data between nodes is expensive. Redshift, Snowflake, Databricks and Synapse all use it. Be able to define it without looking it up.

**Creating the Workspace.** Same resource group, leave the managed resource group blank, primary storage = existing ADLS account with a new `synapse` container. East US failed: "not accepting the creation of new Azure SQL database servers" (regional capacity/subscription restriction), so it was redeployed in Brazil South. Data in East US with a warehouse in Brazil is bad for production: **latency and egress cost**, and **data residency** laws: **GDPR** (EU), **CCPA/CPRA** (California, often applied nationwide), **LGPD** (Brazil).

**Synapse Studio.** Hubs: Home, **Data** (linked ADLS), **Develop** (SQL scripts, notebooks), Integrate (pipelines), Monitor, **Manage** (pools, cost control). Smoke test: `SELECT @@VERSION, DB_NAME(), GETUTCDATE()`.

**Why JSON Didn't Work.** Synapse's SQL engine is OLAP and wants structured data. `FORMAT = 'JSON'` isn't supported in serverless `OPENROWSET`. The "stored procedures cannot be stored in master" error was misleading: queries were running in **`master`**, where you can't create objects, so `CREATE DATABASE citibike_analytics; USE citibike_analytics;` first. JSON can be read as one text column (`FORMAT = 'CSV'` with `0x0b` terminators) and parsed with `OPENJSON`, but the production answer is to **flatten once into Silver Parquet**.

**Databricks: Bronze JSON → Silver Parquet.** Read Bronze, `printSchema` (nested `data → stations → element`), `explode` + `select`/`cast`/`alias` to flatten, validate (not null, counts ≥ 0, like DLT expectations or Great Expectations), `dropDuplicates`, add `snapshot_date`, compare counts (Silver had ~8,000 fewer rows), `coalesce(4).write.parquet` (a few medium files, avoiding small files), read back to verify.

**Querying Silver in Synapse.** `OPENROWSET(BULK '<path>/*.parquet', FORMAT = 'PARQUET')` reads files as a table without loading them. Analytics: top stations by average bikes; network totals per snapshot, which revealed an **anomaly** (one snapshot with 1 station vs ~2,518), the kind of thing a Gold completeness check should catch.

**Views in Synapse Serverless.** `CREATE OR ALTER VIEW` is **saved in the database** and survives logout (Evan said session-scoped; that's a correction), but stores no data, so each query re-scans and is billed again. Serverless has **no materialized views**; use **CETAS** (`CREATE EXTERNAL TABLE AS SELECT`) to write results as new Parquet, effectively a Gold table.

**Event Hubs.** Azure's managed event streaming; speaks the **Kafka protocol** on port 9093, so existing Kafka code works by changing config: `bootstrap.servers = <namespace>.servicebus.windows.net:9093`, `SASL_SSL`, `PLAIN`, username `$ConnectionString`, password = connection string (a secret). Namespace ≈ cluster, event hub ≈ topic, partition ≈ partition.

---

# Part 2: Cheat Sheet

## Platform Choice
- Business need + data size + budget + existing infra, not popularity

## On-Prem Stack
- VPS = cloud VM anywhere · MinIO = S3-API object storage · DuckDB = in-process OLAP engine
- Iceberg = table format · catalog (Lakekeeper REST / Glue / Unity) = current metadata + atomic commits

## Synapse
- Serverless SQL pool (~Athena, per TB processed) · Dedicated SQL pool (~Redshift, per hour, pause)
- Spark pools · Pipelines (ADF) · Studio hubs: Data, Develop, Integrate, Monitor, Manage
- Cost: Parquet, few columns, partitions, CETAS, processing limit

## MPP
- Shared-nothing nodes · split query · parallel slices · leader combines · data movement is costly

## Regions and Law
- Keep data and warehouse together (latency, egress) · GDPR · CCPA/CPRA · LGPD
- Region refuses SQL servers → capacity/quota, pick another region

## Gotchas
- `FORMAT='JSON'` unsupported · `master` → `CREATE DATABASE` + `USE`
- JSON workaround: CSV + `0x0b` + `OPENJSON` · better: flatten to Parquet

## Silver Notebook
- explode → select/cast/alias → filters → dropDuplicates → compare counts → `coalesce(4).write.parquet`

## Views
- Serverless view: saved, no data, re-scans · no materialized views · CETAS writes Parquet

## Event Hubs
- Kafka protocol, port 9093 · SASL_SSL + PLAIN · `$ConnectionString` · namespace / event hub / partition

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: How do you choose an analytics platform?
A: Start from what the business needs, the data size, the budget and the infrastructure you already have. The best platform isn't the most functional or the cheapest, it's the one that gives the business what it needs the way it needs it.

Q: What is a VPS?
A: A virtual private server: a computer in the cloud, like an EC2 instance, from any provider.

Q: What is MinIO?
A: Object storage you host yourself that speaks the S3 API, so tools that read S3 can read it by changing the endpoint. With Iceberg it replaces the older HDFS and Hive setup.

Q: What is DuckDB?
A: An in-process OLAP SQL engine, a library or single binary with no server. It's columnar and very fast on one machine and can query Parquet, CSV and JSON files directly.

Q: Why does Iceberg need a catalog?
A: Every write creates a new metadata file, so something has to hold the single answer to which metadata file is current for each table and make commits atomic. That's the catalog, like Lakekeeper, Glue or Unity.

Q: What is Azure Synapse?
A: Azure's analytics workspace and basically its equivalent of Redshift, combining serverless and dedicated SQL pools, Spark pools and pipelines in one studio.

Q: What's the difference between a serverless and a dedicated SQL pool?
A: The serverless pool queries files in ADLS in place, needs no provisioning and bills per terabyte processed. The dedicated pool is a provisioned MPP warehouse that bills per hour while running, even idle, so you have to pause it.

Q: How is Synapse serverless billed?
A: By data processed, not stored. A 1 GB dataset queried a thousand times counts as about a terabyte processed.

Q: How do you keep serverless query costs down?
A: Query Parquet, select only the columns you need, filter on partitions, keep smaller aggregated tables with CETAS, and set a processing limit.

Q: Define MPP.
A: Massively parallel processing, a shared-nothing architecture. Data is spread across many nodes, each with its own CPU, memory and storage. A leader splits the query, every node works on its slice in parallel, and the leader combines the results. Redshift, Snowflake, Synapse and Databricks all use it.

Q: Why is it bad to keep data in one region and the warehouse in another?
A: Every query moves data a long way, which is slow and incurs data transfer charges. And crossing borders raises data residency issues under laws like GDPR.

Q: What are GDPR, CCPA and LGPD?
A: Data privacy laws: GDPR in the EU, CCPA and CPRA in California, and LGPD in Brazil. They govern how and where personal data is stored and handled.

Q: Why did the Synapse workspace fail to deploy in East US?
A: The region wasn't accepting new Azure SQL servers for that subscription, a capacity or quota restriction. Deploying in another region fixed it.

Q: Why did queries fail with an error about the master database?
A: Serverless pools start in the master system database, where you can't create your own objects. You create a database and USE it first.

Q: Can Synapse serverless read JSON?
A: Not with a JSON format option. You can read each file as one text column and parse it with OPENJSON, but the better answer is to flatten it once into Silver Parquet.

Q: Why convert JSON to Parquet before querying with SQL?
A: SQL engines need flat, typed columns at one level. Parquet is structured, columnar and compressed, so queries are simpler, faster and cheaper.

Q: Why use coalesce(4) when writing Silver?
A: To write a few medium files instead of many tiny ones, which avoids the small files problem and speeds up Synapse queries.

Q: Does a view in Synapse serverless disappear when you log out?
A: No, it's saved in the database. But it stores no data, so every query re-scans the files and is billed again.

Q: How do you persist query results in Synapse serverless?
A: With CETAS, create external table as select, which writes the results as new Parquet files. Materialized views only exist in dedicated pools.

Q: How do you point a Kafka producer at Event Hubs?
A: Change the configuration, not the code: bootstrap servers to the namespace on port 9093, SASL_SSL with PLAIN, the username literally $ConnectionString, and the connection string as the password, kept as a secret.

Q: The network-total query showed one snapshot with only one station. What should a pipeline do about that?
A: Add a completeness check in Gold that flags any snapshot with far fewer stations than normal, since it points to a partial file or bad timestamp.
