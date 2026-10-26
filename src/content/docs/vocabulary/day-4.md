---
title: Day 4 Vocabulary
description: Glossary of terms and definitions from the Training 4 study guide.
sidebar:
  order: 4
---

Vocabulary — Study Guide Day 4

## PostgreSQL Setup
- **psql** — PostgreSQL's command-line client.
- **Peer authentication** — Local login method where Postgres trusts the OS username, with no password.
- **Role** — PostgreSQL's login and permissions identity, created with `CREATE USER` / `createuser`.
- **CREATEDB** — Role attribute allowing a user to create databases.
- **SUPERUSER** — Role attribute that bypasses all permission checks; avoid for normal work.
- **Schema** — A named namespace inside a database that groups tables, e.g. `warehouse`.

## Keys
- **Primary key (PK)** — Column(s) uniquely identifying each row; never NULL.
- **Foreign key (FK)** — Column referencing another table's primary key.
- **Referential integrity** — Rule that FK values must exist in the parent table.
- **ON DELETE CASCADE** — FK option deleting child rows when the parent is deleted.
- **Composite key** — A primary key made of more than one column.

## Data Types
- **INTEGER / SMALLINT / BIGINT** — Whole-number types with increasing range.
- **SERIAL / BIGSERIAL** — Postgres auto-incrementing integer types.
- **DECIMAL(p,s) / NUMERIC** — Exact decimal; `p` total digits, `s` after the decimal. Use for money.
- **FLOAT / DOUBLE PRECISION** — Approximate floating-point numbers.
- **CHAR(n)** — Fixed-length string padded with spaces.
- **VARCHAR(n)** — Variable-length string up to `n` characters.
- **TEXT** — Variable-length string with no practical limit.
- **DATE / TIME** — Calendar date only / time of day only.
- **TIMESTAMP** — Date and time with no time zone.
- **TIMESTAMPTZ** — Date and time stored as UTC and shown in the session's time zone.
- **BOOLEAN** — TRUE, FALSE or NULL.
- **NOT NULL** — Constraint forbidding empty values.
- **AUTO_INCREMENT** — MySQL's equivalent of SERIAL.

## Querying
- **INSERT INTO ... VALUES** — Adds one or more rows.
- **SELECT ... WHERE** — Returns chosen columns for rows matching a condition.
- **Identifier** — A table or column name; double-quoted in Postgres when needed.
- **GROUP BY** — Collapses rows sharing a value into one row per group.
- **Aggregate function** — `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.
- **HAVING** — Filters groups after aggregation.
- **INNER JOIN / LEFT JOIN** — Join keeping only matches / keeping all left-side rows.
- **Subquery** — A query nested inside another query.
- **CTE (Common Table Expression)** — A named temporary result set defined with `WITH ... AS`.
- **Window function** — An aggregate computed per row over a partition, with `OVER (...)`.
- **PARTITION BY** — Splits rows into groups for a window function.
- **RANK()** — Ranking where ties share a rank and gaps follow.
- **DENSE_RANK()** — Ranking where ties share a rank with no gaps.
- **ROW_NUMBER()** — Unique sequential number per row, ignoring ties.

## Indexing
- **Index** — Separate ordered structure mapping column values to rows for fast lookup.
- **B-tree** — PostgreSQL's default index structure.
- **Composite index** — An index on more than one column; the leading column matters.
- **EXPLAIN** — Shows the query planner's chosen plan without running it.
- **EXPLAIN ANALYZE** — Runs the query and reports the plan with real timings.
- **Query planner / optimizer** — Chooses the cheapest estimated execution plan.
- **Seq Scan** — Reading every row of a table.
- **Index Scan** — Using an index to find matching rows.
- **generate_series** — Postgres function producing a series of numbers, used to build test tables.

## Data Warehousing
- **Data warehouse** — A database designed for analysis of historical data.
- **Application database** — A database that runs the day-to-day app.
- **OLTP** — Online transaction processing: fast, narrow reads and writes.
- **OLAP** — Online analytical processing: large scans and aggregations.
- **ETL / ELT** — Extract-transform-load / extract-load-transform pipelines feeding a warehouse.
- **BI (business intelligence)** — Tools like Power BI and Tableau that visualize warehouse data.
- **Star schema** — A central fact table joined to surrounding dimension tables.
- **Fact table** — Table of measurable events: IDs plus numbers like quantity and revenue.
- **Dimension table** — Table of descriptive attributes about the facts.
- **dim_date** — Date dimension with year, quarter, month and day-of-week columns.

## Analytical Platforms
- **Amazon Redshift** — AWS's distributed, columnar cloud data warehouse.
- **Row-oriented storage** — Each full row stored together; suits OLTP.
- **Columnar storage** — Each column stored together; suits analytics and compresses well.
- **Snowflake** — Cloud data platform with storage separated from compute.
- **Virtual warehouse** — An independent Snowflake compute cluster that can scale or suspend.
- **Databricks** — Lakehouse platform built around Apache Spark.
- **Lakehouse** — Warehouse-style analytics directly on data in object storage.
- **Delta Lake** — Table format on object storage used by Databricks.
- **Parquet** — Columnar file format for analytics.
- **Object storage** — Cheap cloud file storage: S3, ADLS, GCS.
