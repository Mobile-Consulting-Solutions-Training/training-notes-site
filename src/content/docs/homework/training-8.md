---
title: "Training 8 Homework"
description: "Homework assignment for Training 8: Spark Partitioning, Salting & Hive Setup."
sidebar:
  order: 8
---

:::note
The assignment prompt as given in class. Related notes: [Training 8](/training-notes-site/notes/training-8/).
:::

## Homework Assignment: Postgres → Hive Migration via PySpark

**Note: reconstructed, not verbatim.** Unlike the other homework files in this folder, this one was not given as a single formally-issued prompt. It grew out of an in-class, article-driven build session (Evan shared a planning doc proposing the class "explicitly demonstrate both Medallion Architecture and ETL" using the existing `bronze.sales` / `silver.sales` / `gold.*` schema) and was completed hands-on rather than assigned as a discrete take-home task. This file reconstructs the assignment's shape from what was actually built (`hive-spark-etl/DEMO.md` and the two delivered scripts) and from [Training 8 notes](/training-notes-site/notes/training-8/)'s own framing. If this doesn't match what was actually asked, let me know and I'll correct it.

**Objective:** Move data from the Postgres warehouse (`<your-name>` container, database `warehouse_practice`) into Hive (`hive-server` container), using PySpark for the read/transform side and demonstrating the Medallion Architecture (Bronze/Silver/Gold) end to end across two different systems rather than just within Postgres.

### Task

Using the existing `bronze.sales`, `silver.sales`, and `gold.*` (dim/fact) tables already built in Postgres:

1. Set up a working `hive-server` container (Apache Hive) alongside the existing `<your-name>` Postgres container.
2. Write a PySpark script (`postgres_to_hive.py`) that reads each Postgres table via Spark's JDBC data source and loads it into a matching Hive table.
3. Since Spark has no built-in JDBC dialect for Hive (a direct `df.write.format("jdbc")` to Hive doesn't work), figure out and implement a working load path instead - Hive's native `LOAD DATA` statement was the approach actually used, driven from the Spark script rather than a direct Spark-to-Hive JDBC write.
4. Handle whatever data-formatting issues come up when moving from Postgres's types/delimiters into Hive's (e.g. Hive's default `\u0001` row delimiter vs. plain CSV, timestamp parsing under Spark's ANSI SQL mode).
5. Write a second script (`migrate_remaining_to_hive.py`) to finish migrating whatever tables the first pass didn't yet cover, so every Bronze/Silver/Gold table that exists in Postgres also exists in Hive.
6. Document the whole process - versions used, prerequisites, the reasoning behind the `LOAD DATA` approach instead of a direct JDBC write, and a troubleshooting section for issues actually hit along the way.

**Verification:** confirm the migrated data is actually queryable in Hive (e.g. via `beeline`), not just that the Spark job exited without an error.

### Deliverables

- `postgres_to_hive.py` and `migrate_remaining_to_hive.py` (the working PySpark migration scripts)
- A walkthrough document (`DEMO.md`) covering setup, the scripts' logic, and troubleshooting
