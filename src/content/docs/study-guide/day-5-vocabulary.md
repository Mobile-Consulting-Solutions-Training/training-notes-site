---
title: Day 5 Vocabulary
description: Glossary of terms and definitions from the Training 5 study guide.
---

Vocabulary — Study Guide Day 5

## Analytical Databases
- **Hive** — Old Hadoop-stack SQL warehouse; considered outdated on-prem analytical database.
- **DuckDB** — Local, embeddable analytical database, usually paired with an Open Table Format like Iceberg.
- **Redshift** — AWS's cloud analytical database.
- **Azure Synapse Analytics / Databricks Delta Lake** — Azure's cloud analytical database options.
- **BigQuery** — GCP's cloud analytical database.
- **Snowflake** — An independent analytical database company that still runs on top of AWS/Azure/GCP infrastructure rather than owning its own data centers.
- **Databricks / Delta Lake** — Has no purpose-built analytical database of its own; Delta Lake + Delta Format is architecturally "engine (Spark) + open table format + object storage," the same pattern as a local DuckDB + Iceberg setup, just at cloud scale.

## OLAP / OLTP
- **OLAP (Online Analytical Processing)** — Scanning, joining, and aggregating large historical data volumes to answer analytical questions.
- **OLTP (Online Transaction Processing)** — Fast, narrow, single-row reads/writes for live applications.

## Dimensional Schemas
- **Kimball methodology** — Dimensional modeling approach (Ralph Kimball); builds a warehouse bottom-up as business-process-oriented star schemas.
- **Inmon methodology** — Competing approach; builds top-down with one normalized enterprise model first, with departmental marts derived afterward.
- **Star Schema** — Basic denormalized dimensional model; one fact table with every dimension attached directly via Foreign Key, one join hop each.
- **Snowflake Schema** — Normalized extension of a star schema; some dimensions split into sub-dimensions connected to other dimension tables rather than the fact table directly, trading query simplicity for reduced redundancy.
- **Galaxy Schema (fact constellation)** — Multiple stars/snowflakes sharing dimensions; not a term to bring up in an interview.
- **Fact Table** — Central table holding "elementary facts" (measurable events, e.g. quantity/price/revenue) plus Foreign Keys to every dimension.
- **Dimension Table** — Table holding descriptive/contextual attributes about the events in a fact table; a dimensional schema always has at least one fact table and multiple dimension tables.

## Database Normalization
- **Edgar F. Codd** — Invented the relational model and formalized normalization/normal forms.
- **1NF (First Normal Form)** — Every cell holds exactly one value.
- **2NF (Second Normal Form)** — Every table has a Primary Key (fuller definition: no partial dependency on part of a composite key).
- **3NF (Third Normal Form)** — Removes transitive dependencies (a non-key column depending on another non-key column instead of directly on the Primary Key).
- **Normalization trade-off** — More normalization means more, narrower tables and faster single-table queries, but more joins once data must be pulled from many tables — why OLAP warehouses favor denormalization (star schemas) instead.

## Data Visualization
- **Matplotlib** — Low-level Python visualization library; full control and full responsibility.
- **Seaborn** — Higher-level Python visualization library, Pandas-integrated, with modern-looking defaults.
- **Plotly** — A Seaborn competitor Python visualization library.
- **BI tools** — Dedicated business-intelligence platforms: Power BI, Tableau, AWS QuickSight, Looker.

## Data Lakehouse vs Data Warehouse
- **Data Warehouse** — Schema-on-write, structured tables, SQL-only workload (e.g. Redshift, Snowflake, BigQuery, Synapse).
- **Data Lakehouse** — Schema-on-read files (Parquet/Delta/Iceberg) in cheap object storage, with the table format adding ACID/schema enforcement/time travel; supports SQL and Spark/ML on the same files (e.g. Databricks).

## Medallion Architecture
- **Bronze** — Raw dumping ground layer, few or no rules applied.
- **Silver** — Intermediate layer; common format applied across bronze sources.
- **Gold** — Business-ready layer, often (not always) star/snowflake shaped, directly answering analytical questions.

## Object Store
- **Object Store** — Storage system based on buckets; each bucket has its own internal file-like structure, and an account can hold many independent buckets.
- **AWS S3** — Cloud object store on AWS.
- **Azure Data Lake Storage (ADLS)** — Cloud object store on Azure; never call it "Azure Blob Storage" — Blob Storage is the flat layer underneath, while ADLS Gen2 adds the hierarchical namespace.
- **MinIO / Apache Ozone** — On-prem object store examples.

## Surrogate Keys & SCD
- **Surrogate Key** — A warehouse-generated artificial ID (not the source system's business key); enables multiple historical versions of the same entity, avoids cross-source key collisions, and is always a fast single-column integer join.
- **SCD (Slowly Changing Dimensions)** — A framework for handling dimension changes over time.
- **SCD Type 0** — Per this class: don't record the change, just overwrite (note: many textbooks instead define Type 0 as "never changes at all," and define "overwrite, no history" as Type 1 — worth clarifying which convention is being tested).
- **SCD Type 1** — Overwrite in place, no history kept.
- **SCD Type 2** — Insert a new row (new surrogate key) and mark the old one as no longer current, preserving full history.

## The "Taylor Swift Problem" (Fan-Out)
- **Push / fan-out-on-write** — Copy data to every destination immediately; fast reads, expensive/bursty writes (e.g. ETL, materialized views, CDC streaming).
- **Pull / fan-out-on-read** — Store data once, compute on demand; cheap writes, expensive reads (e.g. ELT, plain views, batch polling). Same underlying trade-off as data skew / hot-key problems in Spark joins and Kafka partitions.
