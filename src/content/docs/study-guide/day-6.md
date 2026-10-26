---
title: Study Guide - Day 6
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 6: Distributed Systems & HDFS"
sidebar:
  order: 60
---

Study Guide - Day 6 (source: notes/Training 6.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**HPC and Fault Tolerance.** HPC (High Performance Computing) = many machines working together for more power than one machine can give. Every node you add raises the chance that *some* node is failing at any moment, so at scale failure is routine. Distributed systems are built to detect and recover from failure automatically (replication, leader re-election).

**Cluster Managers.** Keep nodes coordinated: track which are alive, elect a leader, keep shared state consistent. Built on **consensus algorithms** like **RAFT** and **ZAB**, which prevent split-brain (two leaders). Examples: Hadoop **YARN**, **KRaft** (Kafka, RAFT-based, replaced ZooKeeper), **ZooKeeper** (ZAB), **Kubernetes** (etcd, Raft-based). An instance runs on every node.

**Heartbeats.** A heartbeat is a message from one node to another plus a confirmation back. If no confirmation comes, the node is considered down. Some cluster managers then self-heal automatically (re-elect, reschedule, re-replicate); in **all** cases the administrator is notified.

**Hadoop's Three Components.** **HDFS** (storage), **YARN** (Yet Another Resource Negotiator: resource and cluster management), **MapReduce** (processing). Spark later replaced MapReduce but often still runs on YARN and HDFS.

**HDFS.** Hadoop Distributed File System: the main storage in a Hadoop cluster. It is a **file system, not a database** (no tables, schema or SQL). Used from a normal Linux terminal: `hdfs dfs -put`, `-get`, `-ls`, `-mkdir`. Files are split into **blocks** (64 MB → 128 MB → 256 MB today; configurable). **Replication** = storing the same data in several places; default factor **3**, so you can lose two copies.

**CAP Theorem.** Consistency (every node returns the latest data), Availability (every request gets a response), Partition tolerance (keeps working when the network splits). You can only guarantee two. Partitions will happen, so the real choice is **CP** (refuse rather than return stale data, e.g. finance) or **AP** (always answer, maybe stale, e.g. social feeds). Evan said HDFS chose availability, but the standard answer is **HDFS is CP**: one active NameNode is the source of truth, and if it's down the file system stops rather than serve inconsistent data.

**MapReduce and Disk I/O.** I/O = input/output. MapReduce does some work in memory and some on disk, writing intermediate results to disk between stages. Spark keeps intermediate data in memory and is roughly 100x faster. **Optimization principle:** most optimizations aren't doing work faster, they're doing less work (Spark skips the disk round-trips; partitions let a query skip most rows).

**Small File Problem.** Many files much smaller than the block size waste metadata (each file needs a NameNode entry) and slow processing (roughly one task per file, so task overhead dominates). Fix: compact into fewer, larger files. Evan's JPMorgan story: 1 MB partitions caused archival jobs to fail; `repartition` to 10 GB partitions cleared a backlog in two weeks. Largely a non-issue on cloud object stores.

**Scalability.** How big can you make a process? **Vertical** (scale up) = improve one machine; hits a hard ceiling. **Horizontal** (scale out) = many identical machines working together; higher ceiling, but needs all the distributed-systems machinery.

**Hive.** The OLAP data warehouse framework for Hadoop: a SQL layer on HDFS + YARN + MapReduce (or Spark). **HiveQL** is a wrapper for MapReduce, so it inherits MapReduce's slowness. A **metastore** stores metadata (schemas, column types, partitions, file locations), never the data. The **Hive Metastore** is the only still-modern part of Hive; Spark, Trino and Athena use it. **AWS Glue Data Catalog** is another metastore (Hive-compatible). Metastores enable **schema on read** (apply the schema at query time) vs **schema on write** (define before loading, as in an RDBMS).

**Managed vs External Tables (interview question).** Drop a managed (internal) table → lose data **and** metadata. Drop an external table → lose **only** metadata; files stay.

**Partitioning vs Bucketing.** Partitioning physically splits a table into sub-files/folders by a column's value (date, region), enabling **partition pruning**. Bucketing assigns rows to a fixed number of buckets by **hashing** a column; good for high-cardinality columns like `customer_id` and for joins. The hash input can be one cell, a column or a row, converted to a string.

**Compression and File Formats.** **Snappy** = compression codec focused on speed, not ratio (gzip compresses more, uses more CPU). **ORC** (Optimized Row Columnar) = Hive's default; columnar, partitionable, distributable, compressible, like **Parquet** (the broader Spark/lakehouse default). **Avro** = row-based, "a compressed JSON with a flexible schema"; its schema enables **schema evolution** (not "schema evaluation"). Parquet/ORC for batch, JSON/Avro for streaming. Schema evolution also via Protobuf (records) and Iceberg/Delta (tables).

**Spark Intro.** Every modern data processing system is Spark or based on it (Glue, Dataproc via Beam, Databricks). Took over because of in-memory speed and the **DataFrame API** (Spark 2.0, Spark SQL), which replaced raw **RDDs**. **Spark is a processor, not storage**: it always reads from and writes to something else (HDFS, S3, Hive). Spark started as ETL; ELT came later and is now dominant in Databricks.

---

# Part 2: Cheat Sheet

## Distributed Basics
- More nodes → more failures · failure is routine at scale
- Cluster manager: liveness, leader election, shared state · RAFT / ZAB consensus
- YARN · KRaft (RAFT, Kafka) · ZooKeeper (ZAB) · Kubernetes (etcd)
- Heartbeat: send → confirm · no reply = down · self-heal sometimes, admin alert always

## Hadoop
- HDFS (storage) · YARN (resources) · MapReduce (processing)
- HDFS = file system, not DB · `hdfs dfs -put/-get/-ls/-mkdir`
- Blocks 64 → 128 → 256 MB (configurable) · replication factor 3

## CAP
- C consistency · A availability · P partition tolerance → pick 2
- Real choice CP vs AP · HDFS = CP (single NameNode source of truth)

## Performance
- I/O = input/output · MapReduce writes intermediate data to disk; Spark keeps it in memory (~100x)
- Optimize by doing less work: skip transfers, prune partitions
- Small files → metadata bloat + task overhead → compact (`repartition`/`coalesce`)

## Scaling
- Vertical = bigger box (ceiling) · Horizontal = more boxes (complexity)

## Hive
- OLAP warehouse on Hadoop · HiveQL → MapReduce jobs
- Metastore = metadata only · Hive Metastore still modern · Glue Data Catalog compatible
- Schema on read (lake) vs schema on write (RDBMS)
- Managed drop = data + metadata · External drop = metadata only

## Partition vs Bucket
- Partition: by value, variable count, pruning, low-cardinality columns
- Bucket: by hash, fixed count, even spread, high-cardinality columns

## Formats
- Snappy = fast codec · gzip = smaller, slower
- ORC (Hive default) / Parquet = columnar → batch
- Avro / JSON = row-based → streaming · Avro schema → schema evolution
- Schema evolution: Avro, Protobuf (records) · Iceberg, Delta (tables)

## Spark
- Processor, never storage · RDD (1.0) → DataFrame / Spark SQL (2.0)
- Glue, Dataproc (Beam), Databricks are all Spark-based · ETL first, ELT later

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: Why does fault tolerance matter more as a cluster grows?
A: Each node you add is another thing that can fail, so the chance that some node is down at any moment keeps rising. In a big cluster, failure is a normal everyday event the system has to handle on its own.

Q: What does a cluster manager do?
A: It keeps the nodes coordinated. It tracks which nodes are alive, elects a leader, and keeps shared state consistent even when nodes fail. Examples are YARN, KRaft, ZooKeeper and Kubernetes.

Q: What are RAFT and ZAB?
A: Consensus algorithms. They let a group of nodes agree on one value, like who the leader is, even when some nodes are slow or crash, which prevents two nodes from both thinking they're leader.

Q: How does a cluster know a node is down?
A: Through heartbeats. Each node's cluster manager sends a message and waits for a confirmation. If the confirmation doesn't come back in time, that node is considered down.

Q: What happens after a node is marked down?
A: Some cluster managers recover automatically, for example by electing a new leader or re-replicating data. In every case, an administrator gets notified so a person can find the root cause.

Q: What are the three components of a Hadoop cluster?
A: HDFS for storage, YARN for resource management, and MapReduce for processing.

Q: Is HDFS a database?
A: No, it's a distributed file system. It stores files as replicated blocks but has no tables, schema or SQL. Things like Hive are built on top of it.

Q: What's the default HDFS replication factor and why?
A: Three. You can lose two copies and still have the data, which balances safety against the storage cost of extra copies.

Q: What's the current default HDFS block size?
A: 256 MB today, after 64 and then 128 MB in earlier versions. It's configurable in the Hadoop config.

Q: Explain the CAP theorem.
A: A distributed system can only guarantee two of consistency, availability and partition tolerance. Since network partitions will happen, the real choice is between consistency, refusing requests rather than returning stale data, and availability, always answering even if the data might be stale.

Q: Is HDFS CP or AP?
A: CP. One active NameNode holds all the metadata, so there's a single source of truth, and if it's unavailable the file system stops instead of returning inconsistent data. Replication is for fault tolerance.

Q: Why is Spark faster than MapReduce?
A: MapReduce writes intermediate results to disk between stages. Spark keeps them in memory, so a whole set of data transfers simply never happens. It's less work, not the same work done faster.

Q: What's the small file problem?
A: Lots of files much smaller than the block size. Each file still needs metadata, which bloats the NameNode, and each file becomes its own task, so scheduling overhead outweighs the actual work. The fix is compacting into fewer, larger files.

Q: What's the difference between vertical and horizontal scaling?
A: Vertical means making one machine bigger, which eventually hits a ceiling. Horizontal means adding more identical machines that work together, which scales further but needs fault tolerance and coordination.

Q: What is Hive and why is it considered slow?
A: Hive is the OLAP warehouse framework for Hadoop. It gives files in HDFS a SQL interface, but HiveQL is translated into MapReduce jobs, so it inherits MapReduce's disk-heavy performance.

Q: What is a metastore?
A: A system that stores metadata about data, like table schemas, column types, partitions and file locations, but not the data itself. The Hive Metastore and AWS Glue Data Catalog are examples.

Q: Why is the Hive Metastore still used when Hive itself is outdated?
A: Because it became a standard catalog. Spark, Trino and Athena all use it to find table schemas and file locations without ever running a MapReduce job.

Q: What's the difference between schema on read and schema on write?
A: Schema on write means the schema is defined before data loads, like a relational database. Schema on read means raw files land as they are and a metastore applies the schema at query time, like a data lake.

Q: What happens when you drop a managed table versus an external table in Hive?
A: Dropping a managed table deletes both the metadata and the data. Dropping an external table deletes only the metadata, and the files stay where they are.

Q: What's the difference between partitioning and bucketing?
A: Partitioning splits a table into separate folders by a column's value, like date, so queries can skip partitions. Bucketing hashes a column into a fixed number of buckets, which works for high-cardinality columns like customer ID and helps joins.

Q: What is Snappy?
A: A compression codec built for fast compression and decompression rather than the smallest file size. It's the common default with Parquet and ORC because processing speed usually matters more than storage.

Q: When do you use Parquet or ORC versus Avro or JSON?
A: Parquet and ORC are columnar, so they're best for batch analytics that read a few columns across many rows. Avro and JSON are row-based, which fits streaming, where records arrive one at a time.

Q: What advantage does Avro's schema give you?
A: Schema evolution. Fields can be added or changed over time without breaking consumers. And it's schema evolution, not schema evaluation.

Q: Does Spark store data?
A: No. Spark is only a processing engine. It always reads from and writes to separate storage like HDFS, S3 or Hive tables.

Q: What two things made Spark take over?
A: Speed from in-memory processing, and the DataFrame API in Spark 2.0, which gave a Pandas-like interface at distributed scale through Spark SQL.
