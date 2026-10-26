---
title: Study Guide - Day 11
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 11: Postgres to Hive with Scala Spark"
sidebar:
  order: 110
---

Study Guide - Day 11 (source: notes/Training 11.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**The Teacher's Finished Job.** A Scala Spark app that reads all ten warehouse tables from Postgres over JDBC (`spark.read.jdbc(url, table, properties)`, password from `sys.env("PG_PASSWORD")`) and writes each one into Hive with `df.write.mode("overwrite").saveAsTable("gold.dim_customer")`. It uses **native Spark-Hive metastore integration**: `.config("hive.metastore.uris", "thrift://localhost:9083")` plus `.enableHiveSupport()`. No CSV export, `docker cp` or `LOAD DATA` bridge as in Training 8.

**Silent-Failure Risk.** If the metastore URI doesn't reach a real metastore, `enableHiveSupport()` can quietly create a local Derby `metastore_db` and `spark-warehouse` folder and look successful. Always check the real tables from another client (beeline) after running.

**Why It First Failed: Broken Pipe.** The first `saveAsTable` threw `TTransportException ... Broken pipe`. Inside the `hive-server` container only HiveServer2 was running (ports 10000/10002); nothing listened on 9083, and the metastore was embedded Derby. Docker accepted the TCP connection on the mapped port, so Spark didn't fail at startup, but the first real Thrift call broke. Embedded Derby allows only one JVM, so the fix was a re-architecture, not a config line.

**The Rebuild.** Snapshot with `docker commit`; create a `hive_metastore` database in Postgres; add the Postgres JDBC driver to `/opt/hive/lib`; point `hive-site.xml` at it (`javax.jdo.option.ConnectionURL` via `host.docker.internal`, because the default bridge network has no container-name DNS); `schematool -dbType postgres -initSchema` (83 tables); start `hive --service metastore` as a second process listening on 9083.

**Remaining Errors, in Order.** (1) `SCHEMA_NOT_FOUND`: `saveAsTable` doesn't create databases, so add `CREATE DATABASE IF NOT EXISTS bronze/silver/gold`. (2) `... is not a directory or unable to create one`: Spark's default warehouse dir was a Mac path, stored in the metastore, and the metastore server tried to `mkdir` it inside the container. Client and server must agree on what a path means, which is why real Hive sits on HDFS or S3. Fix: bind-mount a shared folder at the **same absolute path** on both sides and set `spark.sql.warehouse.dir` explicitly. (3) Stale `hiveserver2.pid` captured by `docker commit` made the new container think HiveServer2 was already running; remove the pidfile and restore the entrypoint.

**Result.** All 10 `saveAsTable` calls succeeded; beeline independently showed the databases, 8 Gold tables and 122 rows in `dim_customer`. Native integration works once the metastore has a real backend and a shared filesystem.

**generate_sales.py.** Teacher's Python script that inserts batches of 5 fake sales into `bronze.sales` with psycopg2. It finds the highest `T###` ID with a regex-filtered `MAX(CAST(SUBSTRING(...)))`, continues the sequence, randomizes customer, product, quantity, a ±10% price and a date within 30 days, commits, then re-selects the inserted IDs to verify. Meant to be re-run to simulate new data arriving.

---

# Part 2: Cheat Sheet

## Native Spark → Hive
- `.config("hive.metastore.uris", "thrift://localhost:9083")` · `.enableHiveSupport()`
- `spark.read.jdbc(url, table, props)` → `df.write.mode("overwrite").saveAsTable("db.table")`
- Secrets from env vars: `sys.env("PG_PASSWORD")`
- Verify with beeline; a clean exit can be a local Derby fallback

## Debugging Path
- Broken pipe → nothing listening on 9083 (HiveServer2 only, embedded Derby)
- Fix: Postgres-backed metastore · driver in `/opt/hive/lib` · `hive-site.xml` · `schematool -initSchema` · `hive --service metastore`
- `SCHEMA_NOT_FOUND` → `CREATE DATABASE IF NOT EXISTS`
- "not a directory" → shared bind mount at same path + `spark.sql.warehouse.dir`
- Stale PID file after `docker commit` → delete it, restore entrypoint

## Docker Notes
- `docker commit` = snapshot before risky changes (also captures pidfiles, entrypoint overrides)
- Default bridge network: no name DNS → `host.docker.internal`
- Background process in a container: `docker exec -d`

## generate_sales.py
- Next ID: `MAX(CAST(SUBSTRING(transaction_id FROM 2) AS INTEGER))` where `~ '^T[0-9]+$'`
- Insert 5 random rows · commit · verify with `= ANY(%s)`

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What does the teacher's finished Scala job do?
A: It reads the bronze, silver and gold tables from Postgres over JDBC and writes each one straight into Hive with saveAsTable, using Spark's native Hive metastore integration instead of exporting CSVs and running LOAD DATA.

Q: What two settings turn on Spark's Hive integration?
A: The hive.metastore.uris config pointing at the metastore's Thrift address, and enableHiveSupport on the SparkSession builder.

Q: Why should you check Hive with beeline after the job finishes?
A: If Spark can't reach a real metastore, it can fall back to a local embedded Derby metastore and local warehouse folder. The job looks successful, but nothing reached the real Hive.

Q: Why did the first write fail with a broken pipe?
A: Nothing in the container was actually listening on port 9083. Only HiveServer2 was running, with an embedded Derby metastore. Docker accepted the connection on the mapped port, but the first real Thrift call broke.

Q: Why wasn't starting a metastore process enough at first?
A: Embedded Derby only lets one JVM hold the database, so a second process would conflict. The metastore needed a real shared backend database, which became Postgres.

Q: What did schematool do?
A: It initialized the Hive metastore schema in the new Postgres database, creating the tables the metastore needs to store its metadata.

Q: Why use host.docker.internal instead of the Postgres container's name?
A: The containers were on Docker's default bridge network, which doesn't resolve container names. host.docker.internal routes from a container back to the host, where Postgres's port is published.

Q: Why did the "not a directory" error happen?
A: Spark stored a Mac file path as the database location, and the metastore server inside the container tried to create that path on its own Linux filesystem, where it didn't exist. Spark and the metastore have to agree on what a storage path means.

Q: How was the storage path problem fixed?
A: By bind-mounting a shared folder into the container at the exact same absolute path as on the Mac, and setting spark.sql.warehouse.dir to it explicitly.

Q: Why do real Hive deployments use HDFS or S3?
A: So the metastore and every client see the same storage. A path stored in the metastore has to resolve to the same files for everyone.

Q: What's a gotcha with docker commit?
A: It captures everything, including stale files like a PID file and any entrypoint override. That made the new container think HiveServer2 was already running until the PID file was removed.

Q: What does generate_sales.py do?
A: It finds the highest existing transaction ID in bronze.sales, then inserts a batch of five random sales continuing that sequence and prints them back to verify. Running it repeatedly simulates new data arriving in Bronze.
