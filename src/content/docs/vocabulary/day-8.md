---
title: Day 8 Vocabulary
description: Glossary of terms and definitions from the Training 8 notes.
sidebar:
  order: 8
---

Vocabulary — Study Guide Day 8

Source: notes/Training 8.md

## Repartitioning and Salting
- **repartition(n)** — Shuffles data into n partitions spread reasonably evenly, with no key, giving parallelism.
- **repartition(n, key)** — Hash-partitions data by a key so all rows with the same key land in the same partition.
- **Hash partitioning** — Assigning rows to partitions by hashing a key, guaranteeing same-key rows co-locate.
- **Parallelism** — Splitting work across more tasks/executors so it runs at the same time.
- **Hot key** — A single key value holding a huge share of the rows, which hash partitioning forces into one partition.
- **Data skew** — Uneven partition sizes caused by uneven key distribution; adding more partitions does not fix a hot key.
- **Salting** — Not a way to get an exact row count per partition, but a technique specifically for data skew that splits a hot key across partitions.
- **Salt column** — An added column of discrete values combined with the key, so the combination `(key, salt)` is hashed instead of the key alone.
- **repartition(n, key, salt)** — Partitioning on key plus salt so a dominant key spreads across several partitions.
- **Two-stage aggregation** — For a salted `groupBy()`: aggregate by `(key, salt)` first, then re-aggregate by the original key.
- **Salted join** — Salt the large skewed side and duplicate the small side's matching rows across every salt value.
- **groupBy()** — Key-based aggregation that needs same-key rows together.
- **join()** — Key-based combination of two tables that needs matching keys together.

## Hive in Docker
- **docker pull** — Downloads an image from Docker Hub without running a container.
- **docker run** — Creates and starts a container from an image.
- **docker images** — Lists the images stored locally.
- **Docker Hub** — Public registry from which Docker images are pulled.
- **Hive Standalone Metastore** — Running only the Hive Metastore catalog as its own service, without Hive's query engine.
- **Hive Metastore** — Hive's catalog service that tracks table schemas and file locations.
- **HiveServer2** — Hive's full query-execution server, which the standalone metastore image does not include.
- **apache/hive** — Official Apache Hive Docker image (e.g. tag `4.0.1` for full Hive).

## Medallion Migration and ETL
- **Medallion Architecture** — Organizing data into Bronze (raw), Silver (cleaned) and Gold (dimensional) layers.
- **Bronze layer** — Raw incoming data stored unfixed.
- **Silver layer** — Cleaned and validated version of Bronze data.
- **Gold layer** — Dimensional (fact and dimension) tables ready for analysis.
- **Migration** — Moving already-correct data from one system to another with no transformation logic.
- **ETL pipeline** — A pipeline that extracts new data and transforms it (clean, validate, model) as it moves into the target.
- **Fact table** — Table of measurable events, such as `fact_sales` or `fact_payment`.
- **Dimension table** — Table of descriptive attributes, such as `dim_customer` or `dim_date`.
- **Surrogate key** — A system-generated key used in dimension tables in place of a business key.
- **Business key** — The natural identifier from the source data, such as `product_number`.
- **Dimension lookup** — Joining incoming facts to dimension tables to get their keys.
- **Foreign key** — A column referencing another table's primary key, linking the two.
- **Primary key** — Column that uniquely identifies each row in a table.
- **Backfill** — Loading historical data into a new table or pipeline.
- **ALTER TABLE ... SET SCHEMA** — PostgreSQL command moving a table into a different schema.
- **CREATE SCHEMA IF NOT EXISTS** — Creates a schema only if it doesn't already exist.
- **ROW_NUMBER() OVER** — Window function assigning a sequential number to each row in a given order.
- **CREATE TABLE ... AS SELECT** — Creates a new table populated by a query's results.
- **\COPY** — psql command exporting or importing table data to or from a client-side file such as CSV.
- **LOAD DATA LOCAL INPATH** — Hive's native bulk-load command for loading a local file into a table.
- **Row-count validation** — Comparing row counts between source and target to check a migration, which alone is not sufficient evidence.
- **Deduplication** — Removing duplicate records, a Silver-layer cleaning step (e.g. `dropDuplicates`).

## Spark and Hive Gotchas
- **JDBC (Java Database Connectivity)** — Java API Spark uses to read from and write to databases.
- **JDBC dialect** — Spark's identifier-quoting and type-mapping rules for a specific database; Hive has none, so plain JDBC writes to Hive fail.
- **spark.read.format("jdbc")** — Reads a database table into Spark via JDBC.
- **df.write.format("jdbc")** — Writes a DataFrame to a database via JDBC.
- **COLUMN_NOT_DEFINED_IN_TABLE** — Spark error caused by Hive's backtick quoting not matching Spark's double-quote quoting.
- **Backticks** — Hive's quoting character for identifiers, unlike ANSI SQL double quotes.
- **ROW FORMAT DELIMITED FIELDS TERMINATED BY** — Hive table clause setting the field delimiter; without it a comma CSV silently loads as all NULLs.
- **\001 / \u0001 (Ctrl-A)** — Hive's default field delimiter, chosen because it essentially never appears in real text.
- **Field delimiter** — The character separating columns in a delimited file.
- **Quoted-field support** — CSV-parser ability to treat commas inside quotes as data; Hive's delimited format lacks it.
- **ANSI SQL mode** — Spark mode (default in recent versions) where invalid casts throw errors instead of returning NULL.
- **to_timestamp()** — Spark function parsing a string to a timestamp; throws on bad input under ANSI mode.
- **try_to_timestamp()** — Spark function that returns NULL instead of throwing on unparseable timestamps.
- **CAST_INVALID_INPUT** — Spark error raised when a value can't be cast under ANSI mode.
