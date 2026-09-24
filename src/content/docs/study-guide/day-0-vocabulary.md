---
title: Day 0 Vocabulary
description: Glossary of terms and definitions from the Training 0 study guide.
---

Vocabulary — Study Guide Day 0

## Hardware
- **RAM** — Fast, volatile, expensive, small-capacity memory used for active working data.
- **Disk** — Slow, non-volatile, cheap, large-capacity storage (SSD/HDD) used for long-term data.
- **ROM** — Non-volatile, read-only memory used for firmware/boot.
- **In-memory computing** — Processing data in RAM instead of disk at each step; why Spark beats MapReduce.
- **OOM (Out-Of-Memory)** — An error caused by running out of available RAM.
- **Spilling** — Falling back to disk when RAM runs out.

## Distributed Systems & Infrastructure
- **Distributed system** — Multiple connected machines working toward a common goal; gains scale, fault tolerance, and parallelism at the cost of complexity, latency, and consistency tradeoffs.
- **Compute cluster** — At least 3 computers connected via LAN/router, configured to work together on the same task.
- **Master/Driver** — The cluster role that assigns work.
- **Worker/Executor** — The cluster role that does the assigned work.
- **Cluster Manager** — Allocates resources across the cluster (e.g. YARN, Kubernetes, Mesos).
- **CAP Theorem** — A distributed system can only fully guarantee 2 of: Consistency, Availability, Partition tolerance; the real-world tradeoff is usually Consistency vs. Availability.
- **HDFS (Hadoop Distributed File System)** — Distributed storage layer that splits files into replicated blocks (128MB default, 3x replication default) across a cluster; poor for small files or low-latency access.
- **NameNode** — HDFS's metadata/master node.
- **DataNode** — HDFS's actual-data/worker node.
- **Processing engines** — The compute layer, separate from storage; comes in Batch (Spark, MapReduce), Stream (Flink, Kafka Streams), Query (Hive, Presto/Trino), and Unified (Spark, Flink, Beam) flavors.
- **Apache Spark** — In-memory distributed processing engine, 10-100x faster than MapReduce; Driver builds a DAG, Cluster Manager allocates resources, Executors run tasks.
- **Job** — A unit of Spark work triggered by an action.
- **Stages** — Spark job subdivisions, split at shuffle boundaries.
- **Tasks** — Spark stage subdivisions, one per partition, run in parallel.
- **RDD** — Spark's original, lower-level data structure.
- **DataFrame** — Spark's higher-level, optimized data structure.
- **Hive** — Old SQL-on-Hadoop OLAP data warehouse; HiveQL gets translated into jobs run on the cluster.
- **Hive Metastore** — Table metadata catalog concept, still widely used today.
- **OLTP** — Online Transaction Processing: small, fast, normalized, real-time transactions (e.g. MySQL, Postgres).
- **OLAP** — Online Analytical Processing: large, complex, denormalized/star-schema, batch-updated analytical queries (e.g. Hive, Snowflake, BigQuery).
- **Data Warehouse** — Structured, schema-on-write storage destination.
- **Data Lake** — Raw, schema-on-read, cheap storage destination.
- **Data Lakehouse** — Combines warehouse and lake characteristics via Open Table Formats.
- **Data Mart** — A subset of a data warehouse scoped to one team.
- **Medallion Architecture** — Bronze (raw dumping ground) -> Silver (cleaned/combined) -> Gold (business-ready), with a transformation job between every layer.
- **Row-based file formats** — CSV, JSON, Avro; good for fast writes and Bronze-layer storage.
- **Columnar file formats** — Parquet, ORC; good for analytical reads and Silver/Gold-layer storage.
- **Open Table Formats (OTF)** — A layer on top of Parquet/ORC files that adds ACID transactions, schema evolution, and time travel via a combined data+metadata folder structure.
- **Iceberg** — Open-standard Open Table Format; the most common choice.
- **Delta** — Databricks-proprietary Open Table Format.
- **Hudi** — Lower-priority Open Table Format; worth knowing it exists.

## Data Engineering Concepts
- **Data Lifecycle** — Ingestion -> Transformation -> Storage -> Analysis/Consumption -> Archival/Deletion.
- **ETL** — Extract, Transform, Load: transform data before loading it into the destination.
- **ELT** — Extract, Load, Transform: transform data after loading it, inside the destination; the modern cloud-native default, though ETL is still used (e.g. for compliance/PII filtering before storage).
- **Batch processing** — Scheduled, periodic processing of data chunks; uses a scheduler (e.g. Airflow) plus a batch engine (e.g. Spark).
- **Streaming** — Continuous, real-time processing; requires one tool to move data (e.g. Kafka) and one to process it (e.g. Flink or Spark Structured Streaming).
- **Apache Kafka** — Streaming platform built for handling over 1,000 messages/second without loss.
- **Producer** — Writes messages into Kafka.
- **Broker** — Stores/serves messages; brokers form the Kafka cluster.
- **Consumer** — Reads messages from Kafka.
- **RabbitMQ / MQTT / AWS SQS** — Simpler messaging alternatives to Kafka, not designed for Kafka's message volume.
- **Micro-batch** — Collecting ~1 second of data and processing it continuously in small batches (used by Spark Structured Streaming); near-real-time.
- **True streaming** — Processing each record individually as it arrives, at millisecond latency (used by Apache Flink).
- **Idempotency** — A process that, when run multiple times, doesn't accumulate or duplicate results unless intentionally designed to.
- **UPSERT/MERGE** — Update-or-insert operation used to keep re-runs idempotent instead of duplicating via plain INSERT.
- **Dead-letter queue (DLQ)** — Where records that repeatedly fail processing get routed, instead of blocking/crashing the whole pipeline.
- **Checkpointing** — Tracking offsets/progress so a process can safely resume without reprocessing or losing data.
- **try/except/finally (Python)** — Error-handling pattern: catch specific exceptions first, `except Exception` as the final fallback, `finally` for cleanup that always runs.

## The Data Engineer Role
- **CI/CD tools** — Automate testing/building/deploying pipeline code; examples: Jenkins, GitHub Actions, GitLab CI, Azure DevOps, AWS CodePipeline, Travis CI.
- **Admin/operational work** — The non-pipeline-building side of the role: access management, cluster/infra management, monitoring/alerting, cost optimization, governance/compliance, documentation, schema/metadata management, backup/DR, security, vendor management, stakeholder communication.
