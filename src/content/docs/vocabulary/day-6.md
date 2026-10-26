---
title: Day 6 Vocabulary
description: Glossary of terms and definitions from the Training 6 notes.
sidebar:
  order: 6
---

Vocabulary — Study Guide Day 6

Source: notes/Training 6.md

## Distributed Systems Fundamentals
- **HPC (High Performance Computing)** — Using clusters of many machines working together to get computing power far beyond a single machine.
- **Distributed system** — A system whose work and data are spread across many networked machines (nodes) that cooperate as one.
- **Node** — One individual machine in a cluster or distributed system.
- **Cluster** — A group of nodes pooling compute and storage to work as a single system.
- **Fault tolerance** — A system's ability to keep working when individual nodes fail; more important as clusters grow, since each added node raises the chance some node is failing at any given time.
- **Cluster manager** — Software, installed on every node, that tracks which nodes are alive, coordinates them, and keeps shared cluster state consistent.
- **Consensus algorithm** — A protocol that lets independent nodes agree on one shared value (such as who the leader is) even when some nodes are slow or crash.
- **RAFT** — A consensus algorithm many cluster managers are built on, including Kafka's KRaft.
- **ZAB (ZooKeeper Atomic Broadcast)** — The consensus algorithm Zookeeper is built on.
- **Leader election** — The process by which a cluster's nodes choose (or re-choose after a failure) a single coordinator node.
- **Split-brain** — A failure scenario where two nodes both believe they are the leader at once, which consensus algorithms prevent.
- **Hadoop YARN** — The Hadoop ecosystem's cluster/resource manager.
- **KRaft** — Apache Kafka's built-in cluster manager, based on RAFT, replacing Kafka's older Zookeeper dependency.
- **Zookeeper** — A coordination service used by many distributed systems, built on ZAB.
- **Kubernetes** — A container orchestrator whose control plane performs cluster-manager-style coordination in some cases.
- **etcd** — The Raft-based key-value store Kubernetes' control plane uses to keep cluster state consistent.
- **Heartbeat** — A periodic message one node sends to another, followed by a confirmation sent back to the originator.
- **Down node** — A node the cluster manager considers failed because it did not respond to a heartbeat.
- **Self-healing** — Automatic adjustment some cluster managers perform to keep operating when a node goes down; administrators are always notified regardless.

## Hadoop
- **Hadoop** — An open-source big data stack made of three core components: HDFS (storage), YARN (resource management) and MapReduce (processing).
- **YARN (Yet Another Resource Negotiator)** — One of the three components of a Hadoop cluster; schedules and allocates compute resources across the cluster.
- **HDFS (Hadoop Distributed File System)** — A distributed file system and the primary place data is stored in most Hadoop clusters; it is not a database.
- **MapReduce** — Hadoop's original distributed processing engine, which performs some operations in memory and others on disk.
- **hdfs dfs -put** — Command that copies a file from the local system into HDFS.
- **hdfs dfs** — Command prefix used in a normal Linux terminal to send storage commands (e.g. `-put`, `-get`, `-ls`, `-mkdir`) to HDFS.
- **Replication** — Storing the same data multiple times in multiple locations.
- **Replication factor** — The number of copies kept of each block; Hadoop's standard is 3, so you can lose two copies and still have one.
- **NameNode** — HDFS's metadata/coordinator component that tracks where blocks live and can trigger re-replication.
- **Block** — A fixed-size chunk a file is split into for storage and replication in HDFS.
- **HDFS block size** — Default chunk size for HDFS blocks: 128 MB for a while, 256 MB today, editable in the Hadoop config.
- **Small File Problem** — Storing many small files on Hadoop wastes storage (metadata per file) and slows processing (one task per tiny file).
- **Compaction** — Combining many small files into fewer, larger files to avoid the Small File Problem.

## CAP Theorem
- **CAP Theorem** — A distributed system can fully guarantee only two of Consistency, Availability and Partition Tolerance at once.
- **Consistency (C)** — Every node returns the same, most up-to-date data for a read.
- **Availability (A)** — Every request gets a non-error response, even if the data may not be the latest.
- **Partition Tolerance (P)** — The system keeps working when network communication breaks between nodes.
- **Network partition** — A break in communication where some nodes cannot talk to others.
- **CP system** — Chooses consistency over availability during a partition, refusing or delaying requests rather than returning stale data; HDFS is usually classified as CP (one active NameNode is the source of truth).
- **AP system** — Chooses availability over consistency during a partition, answering requests even if some data is stale.
- **Strong consistency** — All replicas reflect a change at the same instant; HDFS does not guarantee this.
- **Eventual consistency** — All replicas become consistent after a change, but not at the exact same instant.

## Processing Performance
- **I/O (Input/Output)** — Reading data in and writing data out.
- **Disk I/O** — Reads and writes against physical disk rather than RAM, much slower than memory access.
- **In-memory processing** — Keeping data in RAM across processing steps instead of round-tripping to disk, as Spark does.
- **Less work, not faster work** — Optimization principle that most optimizations avoid work entirely rather than doing the same work faster.
- **Full table scan** — Reading every row of a table because nothing lets the engine skip irrelevant data.

## Scalability
- **Scalability** — How big you can make a process.
- **Vertical scalability (scale up)** — Improving one system's components (CPU, RAM, disk) so it can handle more.
- **Horizontal scalability (scale out)** — Creating multiple identical systems that work together.

## Hive and Metastores
- **Hive** — The OLAP data warehouse framework for Hadoop systems.
- **OLAP (Online Analytical Processing)** — Analytical, read-heavy querying over large data, as in a data warehouse.
- **HiveQL (Hive SQL)** — Hive's SQL query language, which works basically as a wrapper for MapReduce.
- **Metastore** — A system designed to store metadata such as schemas (column names, data types), indexes and partitions, not the data itself.
- **Metadata** — Data that describes other data, such as schema and file location.
- **Hive Metastore** — Hive's metadata catalog; the only part of Hive that is still modern and is reused by newer engines.
- **AWS Glue Data Catalog** — Amazon's managed metastore, compatible with the Hive Metastore API.
- **Schema on Read** — Storing raw data without enforcing a schema and applying the schema at query time via a metastore.
- **Schema on Write** — Defining and enforcing a schema before data can be loaded, as in a traditional RDBMS or warehouse.
- **Internal (managed) table** — A Hive table where Hive owns both metadata and data; dropping it deletes both.
- **External table** — A Hive table where Hive owns only the metadata; dropping it deletes only the metadata and the data stays.
- **DROP TABLE** — SQL command removing a table; its effect on the data depends on internal vs. external.
- **Partitioning** — Physically subdividing a table's rows into separate sub-files on disk, grouped by a column's value.
- **Partition pruning** — Skipping partitions that a query's filter rules out, so only relevant files are read.
- **Bucketing** — Subdividing a table by applying a hash to a chosen value so rows land in a fixed number of buckets.
- **Hash function** — An algorithm that turns any string input (a cell, column or row) into a fixed output used to assign buckets.
- **Cardinality** — The number of distinct values in a column; high-cardinality columns suit bucketing over partitioning.

## File Compression and Storage Formats
- **Snappy** — A file compression format emphasizing speed of compression and decompression over compression ratio.
- **gzip** — A heavier compression format that shrinks files more but costs more CPU.
- **Compression codec** — An algorithm applied on top of a storage format to shrink file size.
- **ORC (Optimized Row Columnar)** — Hive's default file format; columnar, partitionable, distributable and compressible.
- **Parquet** — A columnar file format sharing ORC's properties, common across Spark and lakehouses.
- **Columnar format** — Stores data column by column so queries can read only the columns they need.
- **Row-based format** — Stores whole records together, suited to processing one record at a time.
- **Avro** — Basically a compressed JSON file with a flexible schema; row-based and good for streaming.
- **Avro schema** — The schema stored with Avro data, which facilitates schema evolution.
- **Batch processing** — Processing large accumulated volumes of data at once; Parquet and ORC suit it.
- **Streaming** — Processing records or events as they arrive; JSON and Avro suit it.
- **Schema evolution** — Handling a schema that changes over time (fields added, removed, renamed); not "schema evaluation."
- **Protobuf (Protocol Buffers)** — Google's binary row-based serialization format, with schemas in `.proto` files, supporting schema evolution.
- **Iceberg** — An open table format that handles schema evolution at the table level.
- **Delta (Delta Lake)** — Databricks' open table format providing table-level schema evolution and enforcement.
- **Open table format** — A table layer over data files (Parquet, ORC, Avro) that tracks schema and table changes.

## Spark Introduction
- **Spark** — The dominant distributed data processing engine that replaced MapReduce by doing processing in memory; a processor, not a storage system.
- **repartition** — Spark method that changes the number of partitions; used to turn 1 MB partitions into 10 GB ones in the teacher's archival fix.
- **coalesce** — Spark method more commonly expected for reducing partition count.
- **RDD (Resilient Distributed Dataset)** — Spark 1.0's original data structure, basically a large distributed list or array of values.
- **DataFrame** — Spark 2.0's table-like data structure modeled on Pandas DataFrames, at distributed scale.
- **Spark SQL** — Spark's DataFrame/SQL module, the underlying basis of most data processing technologies today.
- **AWS Glue** — AWS's managed processing service, described as a special-syntax version of Spark.
- **Google Cloud Dataproc** — Google Cloud processing service used with Apache Beam syntax.
- **Apache Beam** — A syntax/API layer for data processing, not an engine itself, with Spark-based backends.
- **Databricks** — Cloud platform founded by original Spark developers, originally "Spark plus a data warehouse" in one service.
- **Object store** — Cloud storage such as S3, ADLS or GCS where the provider handles replication and the Small File Problem largely disappears.
- **ETL (Extract, Transform, Load)** — Transforming data before loading it; Spark's original purpose.
- **ELT (Extract, Load, Transform)** — Loading raw data first and transforming it in the target; dominant only in the last few years and how Spark is used in Databricks today.
- **BI tools (Business Intelligence)** — Reporting tools such as Tableau and Power BI that query the warehouse.

## Weekend Project Tools
- **Docker Compose** — Tool that defines and runs multi-container setups (e.g. PostgreSQL plus a Python app) from a `docker-compose.yml` file.
- **Dockerfile** — File of instructions for building a Docker image, used to containerize the Python pipeline.
- **Persistent volume** — Docker storage that keeps database data across container restarts.
- **requirements.txt** — File listing the Python packages a project needs.
- **run_pipeline.sh** — Bash script that starts the Docker environment and runs the Python pipeline.
- **PostgreSQL** — Open-source relational database used to store processed transactions and run SQL analytics.
- **GROUP BY** — SQL clause grouping rows so aggregates are computed per group (e.g. per category).
- **SUM()** — SQL aggregate function that totals a column.
- **ORDER BY** — SQL clause sorting query results.
