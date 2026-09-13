---
title: Study Guide - Day 0
description: Quick summary, cheat sheet, and flashcards for Training 0
---

Study Guide - Day 0 (source: notes/Training 0.md)

# Part 1: Quick Summary

**Hardware.** RAM is fast, volatile, working memory; disk (SSD/HDD) is slower, non-volatile, long-term storage. ROM is non-volatile, read-only, used for firmware. In data engineering, "memory" and "disk" specifically mean RAM and persistent storage - in-memory processing (like Spark) avoids constant disk I/O, which is why it's fast, but running out of RAM causes OOM errors or slower disk spilling.

**Distributed Systems & Infrastructure.** A distributed system spreads storage/processing across multiple connected machines (a compute cluster) for scale, fault tolerance, and parallelism - at the cost of complexity and the CAP theorem tradeoff (pick 2 of Consistency/Availability/Partition tolerance). HDFS is the classic distributed storage layer (blocks + replication). Processing engines (the compute layer, separate from storage) come in batch (Spark, MapReduce), stream (Flink, Kafka Streams), query (Hive, Presto), and unified (Spark, Flink) flavors. Spark is the dominant in-memory batch/unified engine; Hive is the SQL-on-Hadoop OLAP warehouse layer. OLTP (transactional, e.g. MySQL) vs OLAP (analytical, e.g. Hive/Snowflake) is a core distinction - you don't run analytics on an OLTP database, which is why ETL/ELT pipelines exist. Data Lakes (raw, cheap, schema-on-read) vs Data Warehouses (structured, schema-on-write) vs Data Lakehouses (best of both, via Open Table Formats) are the three storage destination options. The Medallion Architecture (Bronze -> Silver -> Gold) is the standard way to organize a data lake, with a transformation job between each layer. File formats split into row-based (CSV/JSON/Avro, good for Bronze) and columnar (Parquet/ORC, good for Silver/Gold analytics). Open Table Formats (Iceberg = open standard, Delta = Databricks-proprietary, Hudi = low priority) sit on top of Parquet/ORC to add ACID transactions and time travel.

**Data Engineering Concepts.** The Data Lifecycle (Ingestion -> Transformation -> Storage -> Analysis -> Archival) is the umbrella process. ETL (transform before load) and ELT (transform after load, inside the warehouse) are the two pipeline patterns - ELT is now more common in cloud-native stacks, but ETL isn't obsolete. Batch processing (scheduled, periodic chunks) vs Streaming (continuous, real-time) is a key architectural choice - streaming needs a tool to move data (Kafka) AND a tool to process it (Flink for true real-time, or Spark Structured Streaming for micro-batch/near-real-time). Idempotency (safe to re-run without duplicating data) and error handling (retries, DLQs, checkpointing, quarantining bad records) are core reliability principles - Python implements this with try/except/finally, catching specific exceptions before a general fallback.

**The Data Engineer Role.** CI/CD tools (Jenkins, GitHub Actions, GitLab CI, Azure DevOps, AWS CodePipeline, Travis CI) automate testing/deploying pipeline code. A lot of the actual job is operational/admin work: access management, cluster management, monitoring/alerting, cost optimization, governance/compliance, documentation, schema management, backups, security, vendor management, and stakeholder communication - not just building pipelines.

---

# Part 2: Cheat Sheet

## Hardware
- **RAM**: fast, volatile, expensive, small. **Disk**: slow, non-volatile, cheap, large. **ROM**: non-volatile, read-only, firmware/boot.
- In-memory computing = process in RAM instead of disk each step -> why Spark beats MapReduce.
- OOM = out-of-memory error. Spilling = falling back to disk when RAM runs out.

## Distributed Systems & Infrastructure
- **Distributed system**: multiple connected machines working toward a common goal. Pros: scale, fault tolerance, parallelism. Cons: complexity, latency, consistency tradeoffs.
- **Compute cluster**: >=3 computers on a LAN/router, working together. Roles: Master/Driver (assigns work), Worker/Executor (does work), Cluster Manager (allocates resources - YARN/Kubernetes/Mesos).
- **CAP Theorem**: pick 2 of Consistency, Availability, Partition tolerance. Real tradeoff is usually C vs A.
- **HDFS**: distributed file system. Blocks (128MB default) + Replication (3x default). NameNode = metadata/master. DataNode = actual data/worker. Bad for small files/low-latency access.
- **Processing engines** (compute layer, separate from storage): Batch (Spark, MapReduce) / Stream (Flink, Kafka Streams) / Query (Hive, Presto/Trino) / Unified (Spark, Flink, Beam).
- **Apache Spark**: in-memory, 10-100x faster than MapReduce. Driver builds DAG -> Cluster Manager allocates -> Executors run tasks. Job -> Stages (split at shuffles) -> Tasks (one per partition). RDD = original data structure; DataFrame = higher-level, optimized. Modules: Core, SQL, Structured Streaming, MLlib, GraphX.
- **Hive**: old SQL-on-Hadoop OLAP data warehouse. HiveQL -> jobs on cluster. Hive Metastore = table metadata catalog concept, still used today.
- **OLTP** (MySQL/Postgres): small fast transactions, normalized, ACID, real-time. **OLAP** (Hive/Snowflake/BigQuery): large complex analytical queries, denormalized/star-schema, batch-updated.
- **Data Warehouse** (structured, schema-on-write) vs **Data Lake** (raw, schema-on-read, cheap) vs **Data Lakehouse** (both, via OTF). Data Mart = warehouse subset for one team.
- **Medallion Architecture**: Bronze (raw dumping ground) -> [T] -> Silver (cleaned/combined) -> [T] -> Gold (business-ready). T = transformation jobs between every layer.
- **File formats**: Row-based (CSV, JSON, Avro) = good for Bronze/writing. Columnar (Parquet, ORC) = good for Silver/Gold/analytics.
- **Open Table Formats (OTF)**: sit on Parquet/ORC, add ACID + time travel via internal data+metadata folder structure. Iceberg (open standard, most common) > Delta (Databricks-only) > Hudi (just know it exists).

## Data Engineering Concepts
- **Data Lifecycle**: Ingestion -> Transformation -> Storage -> Analysis/Consumption -> Archival/Deletion.
- **ETL**: Extract -> Transform -> Load (transform before loading). **ELT**: Extract -> Load -> Transform (transform inside the destination). ELT is the modern cloud default; ETL still used for compliance/PII filtering before storage.
- **Batch processing**: scheduled, periodic (e.g. daily 8am 150GB file). Uses a scheduler (Airflow) + batch engine (Spark).
- **Streaming**: real-time, continuous. Needs 2 tools: moving data (Kafka) + processing it (Flink or Spark Structured Streaming).
- **Apache Kafka**: for >1,000 msgs/sec without loss. Producer (writes) -> Broker (stores/serves, forms cluster) -> Consumer (reads). Topics, partitions, retention. Alternatives (lower throughput): RabbitMQ, MQTT, AWS SQS.
- **Micro-batch** (Spark Structured Streaming): process ~1 second windows continuously, near-real-time. **True streaming** (Flink): process each record individually, true real-time (milliseconds).
- **Idempotency**: re-running a process doesn't create duplicates unless intentional. Achieved via UPSERT/MERGE, dedup on event ID, overwrite partitions, track offsets/checkpoints.
- **Error handling**: retries, DLQ (dead-letter queue), checkpointing, data quality validation, quarantine bad records, alerting, delivery guarantees (at-most/at-least/exactly-once).
- **Python try/except**: catch specific exceptions first, `except Exception` as final fallback, `finally` always runs. Use `logging` not `print()` in production; route bad records to a DLQ/quarantine.

## The Data Engineer Role
- **CI/CD tools**: Jenkins, GitHub Actions, GitLab CI, Azure DevOps, AWS CodeCommit/CodePipeline, Travis CI - automate test/build/deploy of pipeline code.
- **Admin work**: access management, cluster/infra management, monitoring/alerting, cost optimization, governance/compliance, documentation, schema/metadata management, backup/DR, security, vendor management, stakeholder communication.

---

# Part 3: Flashcards

Q: What's the difference between RAM and Disk?

A: RAM = fast, volatile, expensive, small (active working data). Disk = slow, non-volatile, cheap, large (long-term storage).

--- 
Q: What is a distributed system?

A: Multiple connected machines working together toward a common goal - for scale, fault tolerance, and parallelism.

--- 
Q: What is the CAP theorem?

A: A distributed system can only fully guarantee 2 of: Consistency, Availability, Partition tolerance.

--- 
Q: What is a compute cluster?

A: At least 3 computers connected via LAN/router, configured to work together on the same task.

--- 
Q: What are the 3 roles in a compute cluster?

A: Master/Driver (assigns work), Worker/Executor (does work), Cluster Manager (allocates resources).

--- 
Q: What is HDFS?

A: Hadoop Distributed File System - splits files into replicated blocks (128MB, 3x replication) across a cluster. NameNode = metadata; DataNode = data.

--- 
Q: What are the 4 categories of processing engines?

A: Batch, Stream, Query/SQL, Unified.

--- 
Q: What is Apache Spark?

A: An in-memory distributed processing engine - Extract from HDFS/S3, Transform via DAG, Load into a warehouse. 10-100x faster than MapReduce.

--- 
Q: What's the Job -> Stages -> Tasks hierarchy in Spark?

A: Job = triggered by an action. Stages = split at shuffle boundaries. Tasks = one per partition, run in parallel.

--- 
Q: What is Hive?

A: An old SQL-on-Hadoop data warehouse (OLAP/analytical database) - HiveQL gets translated into jobs on the cluster.

--- 
Q: OLTP vs OLAP?

A: OLTP = fast small transactions, normalized, real app databases (MySQL). OLAP = large analytical queries, denormalized, warehouses (Hive/Snowflake).

--- 
Q: Why can't you run analytics directly on an OLTP database?

A: It would slow down/lock the live application - this is why ETL/ELT pipelines extract data into a separate OLAP warehouse.

--- 
Q: Data Warehouse vs Data Lake vs Data Lakehouse?

A: Warehouse = structured, schema-on-write. Lake = raw, schema-on-read, cheap. Lakehouse = both, via Open Table Formats.

--- 
Q: What is the Medallion Architecture?

A: Bronze (raw dump) -> Silver (cleaned/combined) -> Gold (business-ready), with a transformation job between each layer.

--- 
Q: Row-based vs Columnar file formats?

A: Row-based (CSV/JSON/Avro) = good for fast writes/Bronze. Columnar (Parquet/ORC) = good for analytical reads/Silver/Gold.

--- 
Q: What are Open Table Formats (OTF)?

A: A layer on top of Parquet/ORC files adding ACID transactions, schema evolution, and time travel via combined data+metadata folder structure.

--- 
Q: Name the 3 major OTFs and their status.

A: Iceberg (open source standard, most common), Delta (Databricks-proprietary), Hudi (low priority, just know it exists).

--- 
Q: What is the Data Lifecycle?

A: Ingestion -> Transformation -> Storage -> Analysis/Consumption -> Archival/Deletion.

--- 
Q: ETL vs ELT?

A: ETL = Extract, Transform, then Load (transform before loading). ELT = Extract, Load, then Transform (transform inside the destination).

--- 
Q: Is ETL legacy?

A: No - still widely used, especially for compliance/PII filtering before storage. ELT is the more common modern cloud default, not a full replacement.

--- 
Q: Batch vs Streaming?

A: Batch = scheduled, periodic chunks (minutes/hours latency OK). Streaming = continuous, real-time (seconds or less).

--- 
Q: What two tools does streaming require?

A: One to move the data (e.g. Kafka) and one to process it (e.g. Flink or Spark Structured Streaming).

--- 
Q: What is Apache Kafka built for?

A: Streaming more than 1,000 messages/second without losing messages.

--- 
Q: What are Kafka's Producer, Broker, Consumer?

A: Producer writes messages -> Broker (Kafka cluster) stores/serves them -> Consumer reads them. Fully decoupled.

--- 
Q: Name 3 simpler alternatives to Kafka.

A: RabbitMQ, MQTT, AWS SQS - not designed for high message volume like Kafka.

--- 
Q: What is micro-batch processing, and what uses it?

A: Collecting ~1 second of data and processing it continuously in tiny batches. Spark Structured Streaming uses this.

--- 
Q: What is Apache Flink?

A: A true real-time streaming engine - processes each record individually as it arrives (millisecond latency), vs Spark's micro-batch approach.

--- 
Q: What is idempotency?

A: A process that, when run multiple times, doesn't accumulate/duplicate results unless specifically designed to.

--- 
Q: Name 4 ways to make a process idempotent.

A: UPSERT/MERGE instead of INSERT, dedup on event ID, overwrite partitions instead of appending, track offsets/checkpoints.

--- 
Q: What is a dead-letter queue (DLQ)?

A: Where records that repeatedly fail processing get routed, instead of blocking/crashing the whole pipeline.

--- 
Q: In Python, what's the order exceptions should be caught in?

A: Specific exceptions first, `except Exception` as the final fallback, `finally` for cleanup that always runs.

--- 
Q: Name 3 CI/CD tools.

A: Jenkins, GitHub Actions, GitLab CI (also: Azure DevOps, AWS CodePipeline, Travis CI).

--- 
Q: Name 3 admin tasks a data engineer might do beyond building pipelines.

A: Access management, cost optimization, monitoring/alerting (also: governance/compliance, documentation, on-call).
--- 