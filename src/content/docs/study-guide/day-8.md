---
title: Study Guide - Day 8
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 8: Spark Partitioning, Salting & Hive Setup"
sidebar:
  order: 80
---

Study Guide - Day 8 (source: notes/Training 8.md, notes/hive-spark-etl-walkthrough.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**repartition(n) vs Salting.** Salting is not for getting an exact row count per partition; it is a fix for data skew. Three different tools answer three different questions.

**repartition(n), No Key.** `df.repartition(10)` shuffles rows into 10 roughly equal partitions. Use it when you just want parallelism and don't need same-key rows together.

**repartition(n, key) Can Create Skew.** `df.repartition(10, "customer_id")` **hashes** the key, so every row with the same key lands in the same partition. If customer 100 has 70M of 100M rows, one partition gets ~73M. Raising `n` to 1000 doesn't help: one key always maps to one partition.

**Salting Splits the Hot Key.** Add a `salt` column with a few discrete values (0-4), then `df.repartition(10, "customer_id", "salt")`. Spark now hashes `(100, 0)`, `(100, 1)` ... so the hot key spreads across up to 5 partitions. The salt changes *what gets hashed*, not how partitioning works.

**The Distinction.** `repartition()` answers "how many buckets?" Salting answers "how do I stop one very common key from all going into the same bucket?" Salting only matters for key-based work (`groupBy`, `join`) with a dominant key.

**Salting Changes the Follow-Up.** `groupBy`: two-stage aggregation, first by `(key, salt)` then by key alone, to recombine partial results. `join`: salt the large skewed side and **duplicate** the small side's matching rows across every salt value so each salted partition can still match.

**Hive in Docker.** `docker pull apache/hive:standalone-metastore-nightly` only gets the metastore; the class ended up running full HiveServer2 from `apache/hive:4.0.1` as `hive-server`. The standalone metastore pattern lets many engines share one catalog without Hive's execution engine.

**Lesson Plan: Migration then ETL.** Part 1 **migration**: Postgres Bronze/Silver/Gold → exported files → Hive Bronze/Silver/Gold (no transformation). Part 2 **first real ETL**: messy `new_sales.csv` → Spark → Hive Bronze → clean/validate/dedupe → Silver → dimension lookups and surrogate keys → Gold `fact_sales`. Close by tracing one good `sale_id` through every layer and one bad record that only survives in Bronze, which shows why medallion architecture exists.

**Postgres Target Shape.** `bronze.sales` (raw), `silver.sales` (cleaned), and eight `gold` tables (six dimensions, `fact_payment`, `fact_sales`). The historical backfill was derived from already-clean Gold data, so Silver was a straight copy; `customer_id` stays `NULL` because the source never captured it (an honest gap, not a guess). The `product_id` column actually holds `product_number` values.

**Gotchas from the Hive Migration.**
1. **No Hive JDBC dialect in Spark.** Spark quotes identifiers with double quotes; Hive wants backticks, giving `COLUMN_NOT_DEFINED_IN_TABLE`. Pattern: read/transform with Spark, load with Hive's native `LOAD DATA LOCAL INPATH`.
2. **Default delimiter is `\001` (Ctrl-A).** Loading a comma CSV without `ROW FORMAT DELIMITED FIELDS TERMINATED BY ','` loads every column as `NULL` while `COUNT(*)` looks correct. A matching row count is not proof; spot-check values.
3. **Commas inside text.** Hive's delimited format has no quoted-field support, so commas in `product_description` shift columns. Use `\u0001`, which almost never appears in text.
4. **ANSI mode.** In Spark 4.x, `to_timestamp()` on bad input throws `CAST_INVALID_INPUT`. Use `try_to_timestamp()` to get `NULL` and reject the row later.
5. **Per-table delimiters.** A shared load helper that assumed one delimiter silently nulled the one table that used commas. Look up the format per table.

---

# Part 2: Cheat Sheet

## Three Partitioning Tools
- `repartition(n)` → N even partitions, no key · parallelism
- `repartition(n, key)` → same key together (hash) · skew if one key dominates · bigger `n` doesn't help
- `repartition(n, key, salt)` → hot key spread across salt values

## Salting Recipe
- `withColumn("salt", (rand()*k).cast("int"))` → `repartition(n, key, "salt")` → drop salt
- groupBy: aggregate `(key, salt)` then `key`
- join: salt big side, duplicate small side across all salt values

## Hive Setup
- `apache/hive:standalone-metastore-nightly` = metastore only · `apache/hive:4.0.1` = HiveServer2
- `docker pull` downloads only; `docker run` starts

## Medallion Migration + ETL
- Part 1: Postgres → files → Hive (copy, no logic)
- Part 2: CSV → Spark → Bronze → Silver (clean, dedupe) → Gold (lookups, surrogate keys)
- Trace a good record end to end and a bad one stuck in Bronze

## Gotchas
- Spark JDBC can't write Hive → `LOAD DATA LOCAL INPATH`
- Hive default delimiter `\001` · missing `ROW FORMAT` → all NULLs, correct count
- Commas in text break delimited loads → use `\u0001`
- Spark 4 ANSI mode → `try_to_timestamp()`
- Delimiter per table, not one for all

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: Is salting a way to get an exact number of rows per partition?
A: No. Salting is specifically a fix for data skew, where one key has far more rows than the others.

Q: What does repartition with no key do?
A: It shuffles the data into the number of partitions you ask for, spread roughly evenly. It's for parallelism when you don't need rows with the same key together.

Q: Why can repartition by a key create skew?
A: Spark hashes the key, so every row with the same key goes to the same partition. If one customer has 70 million rows, all of them land in one partition.

Q: Will increasing the number of partitions fix a skewed key?
A: No. One key value always hashes to one partition, no matter how many partitions there are.

Q: How does salting fix it?
A: You add a salt column with a few values and repartition by the key plus the salt. Spark hashes the combination, so the hot key's rows spread across several partitions instead of one.

Q: What's the one-sentence difference between repartition and salting?
A: Repartition decides how many buckets there are; salting stops one very common key from all being forced into the same bucket.

Q: What extra step does salting require for a groupBy?
A: A two-stage aggregation. First aggregate by key and salt, then aggregate those partial results again by the key alone to get the real totals.

Q: What extra step does salting require for a join?
A: You salt the large skewed side and duplicate the small side's matching rows for every salt value, so each salted partition still has rows to match.

Q: What's the difference between the two parts of the lesson plan?
A: Part 1 migrates an existing warehouse from Postgres to Hive with no transformation. Part 2 is the first real ETL pipeline, where messy new data is cleaned in Silver and modeled into Gold.

Q: Why trace a bad record that only survives in Bronze?
A: It shows why medallion architecture exists. Bronze keeps everything raw, so you can see exactly what was rejected and why, while Silver and Gold only hold clean data.

Q: Why couldn't Spark write to Hive over JDBC?
A: Spark has no JDBC dialect for Hive. It quotes column names with double quotes, Hive expects backticks, so the columns never match. The fix was to load with Hive's own LOAD DATA command.

Q: A Hive load reports the right row count but every column is NULL. What happened?
A: The table expected Hive's default Ctrl-A delimiter but the file was comma-separated. The row count matches, but no fields were split. Always spot-check actual values, not just counts.

Q: Why was a comma a bad delimiter for the product table?
A: Hive's delimited format just splits on the character and doesn't understand quotes, so commas inside product descriptions shifted every later column. Ctrl-A almost never appears in real text.

Q: Why did to_timestamp crash the pipeline?
A: Spark 4 runs in ANSI mode, so a bad cast throws an exception instead of returning NULL. try_to_timestamp returns NULL, so the row can be rejected later instead of killing the job.

Q: What was the lesson from the shared load helper bug?
A: When tables use different formats for historical reasons, the tooling has to look up the right format per table instead of assuming they're all the same.
