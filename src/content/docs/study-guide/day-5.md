---
title: Study Guide - Day 5
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 5: SQL providers, dimensional modeling, normalization, and lakehouses"
---

Study Guide - Day 5 (source: notes/Training 5.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Analytical Databases (On-Prem vs Cloud).** On-prem options: Hive (old Hadoop-stack warehouse, outdated), DuckDB (local embeddable analytical DB, usually paired with an Open Table Format like Iceberg). Cloud options: Redshift (AWS), Azure Synapse Analytics or Databricks Delta Lake (Azure), BigQuery (GCP), and Snowflake - an independent company that still has to run on top of AWS/Azure/GCP rather than owning its own infrastructure. Databricks has no purpose-built analytical database of its own - Delta Lake + Delta Format is architecturally the same "engine + open table format + object storage" pattern as a local DuckDB + Iceberg setup, just at cloud scale.

**OLAP vs OLTP.** OLAP = Online Analytical Processing - scanning/joining/aggregating large historical volumes to answer analytical questions. OLTP = Online Transaction Processing - fast, narrow, single-row reads/writes for live applications. Every system in the Analytical Databases list exists to make OLAP fast.

**Dimensional Schemas.** Ralph Kimball pioneered dimensional modeling (star-schema-based warehouses, business-process-oriented) vs. the competing Inmon methodology (single normalized enterprise model first). **Star Schema** = the basic denormalized model - one fact table, dimensions attach directly via FK, one join hop each. **Snowflake Schema** = a normalized extension - some dimensions split into sub-dimensions connected to *other dimension tables* rather than the fact table directly, trading query simplicity for reduced redundancy. **Galaxy Schema** (fact constellation) = multiple stars/snowflakes sharing dimensions - don't bring this term up in an interview. **Fact Table** = the central table holding "elementary facts" (measurable events, e.g. quantity/price/revenue) plus FKs to every dimension. **Dimension Table** = descriptive/contextual attributes about those events; a dimensional schema always has >=1 fact table and multiple dimension tables.

**Database Normalization.** Edgar F. Codd invented the relational model and formalized normalization/normal forms. **1NF**: every cell holds exactly one value. **2NF**: every table has a Primary Key (fuller version: no partial dependency on part of a composite key). **3NF**: remove transitive dependencies (a non-key column depending on another non-key column instead of directly on the PK). General pattern: more normalization = more, narrower tables = faster single-table queries, but more joins once data must be pulled from many tables - which is exactly why OLAP warehouses favor denormalization (star schemas) instead.

**Data Visualization.** Connects to OLAP warehouses because warehouses are optimized to do the math that produces visualization-ready results. Python libraries: Matplotlib (low-level, full control/responsibility), Seaborn (higher-level, Pandas-integrated, modern-looking defaults by default), Plotly (a Seaborn competitor). BI tools: Power BI, Tableau, AWS QuickSight, Looker. Hands-on stack: `pandas` + `sqlalchemy` + `psycopg2-binary` + `seaborn` + `matplotlib`.

**Data Lakehouse vs Data Warehouse.** Warehouse = schema-on-write, structured tables, SQL-only workload (Redshift/Snowflake/BigQuery/Synapse). Lakehouse = schema-on-read files (Parquet/Delta/Iceberg) in cheap object storage, with the table format adding ACID/schema enforcement/time travel - supports SQL *and* Spark/ML on the same files (Databricks).

**Medallion Architecture.** Bronze = raw dumping ground, few/no rules. Silver = intermediate, common format applied across bronze sources. Gold = business-ready, often (not always) star/snowflake shaped - directly answers analytical questions.

**Object Store.** Storage system based on buckets - each bucket has its own internal file-like structure, and an account can hold many independent buckets. Common lakehouse layout: bronze/silver/gold buckets, OR bronze/silver buckets + gold living in a dedicated SQL warehouse instead. Cloud examples: AWS S3, Azure Data Lake Storage/ADLS (never say "Azure Blob Storage" for this - Blob Storage is the flat layer underneath; ADLS Gen2 adds the hierarchical namespace). On-prem examples: MinIO, Apache Ozone.

**Surrogate Keys & SCD.** A surrogate key is a warehouse-generated artificial ID (not the source system's business key) - enables multiple historical "versions" of the same entity, avoids cross-source key collisions, and is always a fast single-column integer join. SCD = Slowly Changing Dimensions. Type 0 (per class) = don't record the change, just overwrite (note: most textbooks define this the opposite way - Type 0 = never changes at all, and define "just overwrite, no history" as Type 1 - worth clarifying which convention is being tested). Type 1 = overwrite in place, no history. Type 2 = insert a new row (new surrogate key) and mark the old one as no longer current, preserving full history.

**The "Taylor Swift Problem" (Fan-Out).** Push/fan-out-on-write = copy data to every destination immediately (fast reads, expensive/bursty writes) = ETL, materialized views, CDC streaming. Pull/fan-out-on-read = store once, compute on demand (cheap writes, expensive reads) = ELT, plain views, batch polling. Same underlying trade-off as data skew / hot-key problems in Spark joins and Kafka partitions.

---

# Part 2: Cheat Sheet

## Analytical Databases
- On-prem: **Hive** (old Hadoop SQL warehouse), **DuckDB** (local, pairs with an OTF like Iceberg)
- Cloud: **Redshift** (AWS), **Synapse/Delta Lake** (Azure), **BigQuery** (GCP), **Snowflake** (independent, runs on top of AWS/Azure/GCP)
- Databricks = no purpose-built DB; Delta Lake + Delta Format = engine (Spark) + open table format (Delta) + object storage = same pattern as DuckDB + Iceberg, just cloud-scale

## OLAP / OLTP
- **OLAP** = Online Analytical Processing (scan/aggregate history)
- **OLTP** = Online Transaction Processing (fast single-row app reads/writes)

## Dimensional Schemas
- **Kimball** = star-schema, business-process-first. **Inmon** = normalized enterprise model first, marts derived after.
- **Star** = denormalized, all dims -> FK -> fact directly, fewest joins
- **Snowflake** = normalized extension, some dims -> FK -> other dims (not the fact)
- **Galaxy/fact constellation** = multiple stars/snowflakes sharing dims (don't say this in interviews)
- **Fact table** = elementary facts (measures) + FKs out to dims
- **Dimension table** = descriptive context; always >=1 fact + multiple dims per schema

## Normalization
- Codd = relational model + normal forms
- **1NF**: one value per cell
- **2NF**: has a PK (full def: no partial dependency on part of a composite key)
- **3NF**: no transitive dependencies (non-key -> non-key -> PK chain)
- More normalized = more/narrower tables = faster single-table reads, more joins across tables -> why warehouses denormalize (star schema)

## Data Visualization
- Python: **Matplotlib** (low-level) < **Seaborn** (higher-level, Pandas-friendly) ~ **Plotly** (Seaborn competitor)
- BI tools: **Power BI**, **Tableau**, **AWS QuickSight**, **Looker**
- Stack: `pandas` + `sqlalchemy` + `psycopg2-binary` + `seaborn` + `matplotlib`

## Lakehouse vs Warehouse
- Warehouse: schema-on-write, structured, SQL-only
- Lakehouse: schema-on-read files + table format (Delta/Iceberg) = ACID/time-travel + SQL AND Spark/ML on the same files

## Medallion Architecture
- **Bronze** = raw dump, few/no rules
- **Silver** = cleaned/conformed, common format
- **Gold** = business-ready (often, not always, star/snowflake)

## Object Store
- Buckets = top-level containers, each with its own internal structure
- Layout: bronze/silver/gold buckets, OR bronze/silver buckets + gold in a SQL warehouse
- Cloud: **S3**, **ADLS** (NOT "Azure Blob Storage"), **GCS**
- On-prem: **MinIO**, **Apache Ozone**

## Surrogate Keys & SCD
- Surrogate key = warehouse-generated artificial ID, not the source business key -> enables history, avoids key collisions, fast single-column joins
- **SCD Type 0** (per class) = overwrite, no history (double-check vs. textbook "never changes" definition)
- **SCD Type 1** = overwrite, no history
- **SCD Type 2** = new row + surrogate key, old row marked not-current, full history preserved

## Fan-Out ("Taylor Swift Problem")
- **Push/fan-out-on-write** = ETL, materialized views, CDC streaming -> fast reads, expensive writes
- **Pull/fan-out-on-read** = ELT, plain views, batch polling -> cheap writes, expensive reads
- Same trade-off underlies data skew / hot-key problems (Spark join skew, Kafka partition hotspots)

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What's the difference between an on-premises and a cloud analytical database, and name one of each?
A: On-premises means you install and run it yourself - for example DuckDB. Cloud means a managed service billed by usage - for example Redshift on AWS.

Q: Does Databricks have its own purpose-built analytical database?
A: No - it uses Delta Lake, which is really a Spark compute engine plus the Delta open table format sitting on object storage, the same architectural pattern as running DuckDB against Iceberg files, just at cloud scale.

Q: Why is Snowflake's position among cloud analytical databases a bit unusual?
A: Unlike Redshift or BigQuery, which are native services of their own cloud, Snowflake is an independent company that still has to run on top of AWS, Azure, or GCP's infrastructure rather than owning its own data centers.

Q: What does OLAP stand for, and how is it different from OLTP?
A: Online Analytical Processing - built for scanning and aggregating large volumes of historical data. OLTP, Online Transaction Processing, is built for fast, narrow, single-row reads and writes for live applications.

Q: Who is Ralph Kimball, and what methodology is he known for?
A: A data warehousing pioneer who developed dimensional modeling - building a warehouse as business-process-oriented star schemas designed to be intuitive for analysts to query directly.

Q: What's the difference between the Kimball and Inmon approaches?
A: Kimball builds bottom-up as star schemas per business process. Inmon builds top-down - one normalized enterprise-wide model first, with departmental marts derived from it afterward.

Q: What is a Star Schema?
A: The basic denormalized dimensional model - one fact table in the center, with every dimension table connected to it directly by a single Foreign Key, giving the fewest possible joins per query.

Q: What is a Snowflake Schema, and how is it different from a Star Schema?
A: A normalized extension of the star schema - some dimension tables are split into sub-dimensions that connect to other dimension tables instead of connecting directly to the fact table, which reduces redundancy but requires more joins.

Q: What is a Galaxy Schema, and should you bring it up in an interview?
A: Also called a fact constellation - a warehouse with multiple star or snowflake schemas, often sharing dimensions. It's not really a deliberate design pattern interviewers test for, so it's better left unmentioned in an interview.

Q: What is a Fact Table?
A: The central table of a warehouse, holding elementary facts - the measurable numeric values from a business event - plus a Foreign Key out to every dimension describing that event.

Q: What is a Dimension Table?
A: A table holding descriptive, contextual attributes about the events in a fact table - answering the who/what/where/when around each fact.

Q: How many fact and dimension tables does a dimensional schema need?
A: At least one fact table, and always multiple dimension tables.

Q: Who is Edgar F. Codd, and why does he matter for normalization?
A: He invented the relational model for databases and later formalized normalization and the normal forms as a way to systematically eliminate data redundancy and inconsistency.

Q: What does 1st Normal Form require?
A: Every cell in a table must contain exactly one value - no multiple values crammed into a single column.

Q: What does 2nd Normal Form require?
A: Every table must have a Primary Key uniquely identifying its rows; more precisely, every non-key column must depend on the entire (possibly composite) key, not just part of it.

Q: What does 3rd Normal Form require?
A: Removing transitive dependencies - a non-key column shouldn't depend on another non-key column, only on the Primary Key directly.

Q: What's the overall trade-off as a database becomes more normalized?
A: More tables, each with less data, which speeds up queries that stay within one or two tables - but once you need data from many different tables, you need more joins, which is why analytical warehouses often denormalize instead.

Q: How do data visualization tools relate to OLAP warehouses?
A: They're commonly connected to OLAP warehouses because those warehouses are optimized to do the aggregations and math that produce the clean result sets visualization tools need to render.

Q: Name the three Python data visualization libraries covered, and describe each in one phrase.
A: Matplotlib - low-level, full control and full responsibility. Seaborn - higher-level, works directly with Pandas, modern-looking defaults. Plotly - a competitor to Seaborn.

Q: Name four dedicated BI tools covered in class.
A: Microsoft Power BI, Tableau, AWS QuickSight, and Looker.

Q: What's the difference between a Data Warehouse and a Data Lakehouse?
A: A warehouse is schema-on-write - structured tables, transformed before load, SQL-only. A lakehouse is schema-on-read files like Parquet or Delta sitting in cheap object storage, with an open table format adding ACID transactions and schema enforcement, supporting SQL analytics and Spark/ML on the exact same files.

Q: What are the three layers of Medallion Architecture, and what does each contain?
A: Bronze - raw data, essentially a dumping ground with few rules. Silver - cleaned, conformed tables built from Bronze into a common format. Gold - business-ready data for answering analytical questions, often but not always shaped as a star or snowflake schema.

Q: What is an Object Store?
A: A storage system built around buckets - each bucket has its own internal file-like structure, and an account can have many independent buckets.

Q: What are two common ways to lay out Bronze/Silver/Gold inside an object store?
A: Either three buckets - bronze, silver, and gold - or bronze and silver buckets with the gold layer instead living in a dedicated SQL data warehouse platform.

Q: Name the three cloud object stores and two on-premises object stores covered.
A: Cloud: AWS S3, Azure Data Lake Storage (ADLS), and Google Cloud Storage. On-premises: MinIO and Apache Ozone.

Q: What's the correct term for Azure's object store used in a lakehouse, and what should you avoid calling it?
A: Azure Data Lake Storage, or ADLS - avoid calling it "Azure Blob Storage," since Blob Storage is the flat layer underneath; ADLS Gen2 adds the hierarchical namespace that makes it lakehouse-suitable.

Q: What is a Surrogate Key, and why use one instead of the source system's own key?
A: An artificial, warehouse-generated identifier assigned to each dimension row instead of using the source system's business key - it allows the same business entity to have multiple historical versions, avoids key collisions across source systems, and is always a fast single-column integer to join on.

Q: What does SCD stand for?
A: Slowly Changing Dimensions.

Q: What's the difference between SCD Type 1 and Type 2?
A: Type 1 overwrites the old value in place with no history kept. Type 2 inserts a brand new row with its own surrogate key for the changed entity, keeping the old row intact and marking it as no longer current, preserving full history.

Q: What is the "Taylor Swift problem," and what are the two approaches to it?
A: The social-media celebrity fan-out problem - push (fan-out-on-write), which copies a post into every follower's feed immediately for fast reads but expensive bursty writes, and pull (fan-out-on-read), which stores the post once and computes the feed on demand, which is cheap to write but more expensive to read.

Q: How does the fan-out push/pull trade-off apply to a data engineering job?
A: It's the same trade-off as ETL vs ELT, materialized views vs plain views, and CDC streaming vs batch polling - push optimizes read speed at the cost of write amplification, and pull optimizes write cost at the cost of read latency, and recognizing which side a given pipeline needs is the actual skill.
