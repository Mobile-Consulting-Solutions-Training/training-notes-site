---
title: Study Guide - Day 22
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 22: Warehouse Design and AWS Streaming"
sidebar:
  order: 220
---

Study Guide - Day 22 (source: notes/Training 22.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Warehouse Design Beyond Dimensional Modeling.** Deciding what goes in which tables, schemas and layers combines three disciplines: **logical data architecture** (entities, facts, dimensions, shared definitions), **physical database design** (distribution, partitioning, sort keys, materialized views, indexes) and **enterprise data architecture** (boundaries between ingestion, transformation and consumption). Logical coherence and physical performance are separate problems solved together. A snowflake schema can be more efficient when many dimensions are queried.

**Citi Bike Layers.** Bronze (raw), Silver (cleaned, typed, deduplicated), Gold (`dim_station`, `dim_date`, `fact_station_snapshot`; conformed dimensions, explicit grain), **Serving** (materialized aggregates, dashboard views, KPIs). Gold changes the **shape**; Serving changes the **grain**. Principles: attributes in dimensions, keep the needed historical grain, aggregate for dashboards, reuse **conformed dimensions**, avoid mart sprawl, start from engine defaults and measure. Exercise: design for five queries and check `EXPLAIN` for big scans or redistribution (`DS_BCAST`, `DS_DIST`). Reading: Kimball's *Lifecycle Toolkit*, AWS Redshift best practices, Kleppmann's *DDIA*.

**AWS Streaming.** **MSK** = real Kafka on AWS. **Kinesis Data Streams** = a serverless equivalent of Kafka: producer → stream → consumer; scale with **shards** (like partitions); pay per throughput. **Kinesis Firehose** = a message delivery system that takes the place of the consumer, delivering to S3, Redshift or OpenSearch (like a Kafka Connect sink).

**Producers and Consumers.** Producers: **Kinesis Agent** (Java app tailing log files), **AWS SDK** (boto3 `put_record`, simplest), **KPL** (high-throughput aggregation, batching, retries). Consumers: **Managed Apache Flink** (stateful, low latency, fraud detection), **Data Firehose** (managed delivery, JSON → Parquet, dynamic partitioning), **KCL** (library for custom consumers; shard assignment and checkpointing via DynamoDB lease tables). Also Spark Structured Streaming on EMR and Lambda. One stream can feed many consumers at once. The **PartitionKey** is hashed to choose the shard, keeping one station's records in order.

**Stream Processing Options on AWS.** (1) Kinesis Firehose (light Python/pandas transforms, not distributed, no Spark); (2) Spark Structured Streaming on EMR; (3) Glue Streaming; (4) Managed Flink (pairs with MSK or Kinesis); (5) Lambda, **only good in rare cases** like demos. Almost every serverless service is not distributed; Glue and EMR Serverless are the exceptions. Lambda reads streams through an **event source mapping** that batches records, which keeps invocation counts (and cost) down.

**RDS.** A virtual database server with MySQL, Postgres, MariaDB, Oracle, SQL Server or **Aurora** (AWS-built, MySQL/Postgres-compatible, designed for speed). OLTP and row-based: usually the pipeline **source**; Redshift (OLAP, columnar) is the destination.

**Upcoming Projects.** Streamlit dashboard on **AWS Fargate** (serverless containers); SageMaker ML app reading Redshift; a Gen AI app using **RAG**; managing ML/Gen AI pipelines with **MLflow** (MLOps). Data engineers deploy and feed models (via REST API or SafeTensors), they don't build them.

**RAG vs Vector Database.** **RAG** (Retrieval-Augmented Generation) = a pipeline that funnels your data to where an LLM can read it and answer questions: ingest → chunk → embed → store → retrieve → generate. It adds context to the prompt; it doesn't retrain the model. A **vector database** stores embeddings for similarity search and is unreadable to humans; it's usually a component inside RAG (pgvector, OpenSearch, Pinecone, Chroma). RAG is the AI topic that comes up most in DE interviews.

**Glue vs Spark, Redshift vs Postgres.** Glue is Spark made serverless with the **DynamicFrame** for messy JSON. Redshift is Postgres-flavored SQL redesigned as OLAP and columnar. Similar syntax, not interchangeable.

**Demo: Kinesis → Glue Streaming → Aurora Postgres.** Created `citibike-station-stream` (provisioned, 1 shard = 1 MB/s and 1,000 records/s writes, 24-hour retention, 1 MB max record). Built a **separate** producer Lambda instead of editing the working one. IAM permissions go on the **execution role** the function actually uses. Glue role got `rds-db:connect` (IAM database auth with the **cluster resource ID**). Glue 5.0 streaming job, 2 × G.1X, 30-second windows, created from the CLI. Four errors: (1) "Not authorized" hidden behind connection errors → add S3 access; (2) `Unresolved column` from schema inference → explicit `StructType`; (3) zero columns because the schema wasn't passed to the reader; (4) copy-paste drift → ask the AI for a complete replacement file. Result: 2,519 rows. Lessons: "retrying micro batch" means failing; check the producer with `get-records` (records are **Base64**); trust your instincts over the AI; stop old runs; new checkpoint after logic changes; verify uploads by SHA; start `aws logs tail --follow` before the job. `user/...` not authorized → ask Evan; `assumed-role/...` not authorized → fix the role's policy. Stop streaming Glue jobs when done.

---

# Part 2: Cheat Sheet

## Warehouse Design
- Logical · physical · enterprise architecture
- Bronze → Silver → Gold (shape) → Serving (grain)
- Conformed dimensions · explicit grain · measure with `EXPLAIN`

## Kinesis vs Kafka
- Stream = topic + broker · shard = partition · 24 h retention · 1 MB max record
- 1 shard: 1 MB/s, 1,000 rec/s write · on-demand vs provisioned
- MSK = real Kafka · Kinesis = Kafka-like, SDK calls

## Producers / Consumers
- Producers: Agent (logs) · SDK/boto3 (`put_record`, PartitionKey) · KPL (high volume)
- Consumers: Managed Flink · Firehose · KCL · Spark on EMR · Lambda
- Firehose = the consumer, delivers to S3/Redshift

## Processing Options
- Firehose · Spark on EMR · Glue Streaming · Managed Flink · Lambda (rare)
- Distributed: EMR, Glue, Flink · not: Firehose, Lambda

## RDS
- MySQL, Postgres, MariaDB, Oracle, SQL Server, Aurora · OLTP source

## AI Vocabulary
- RAG: ingest → chunk → embed → store → retrieve → generate
- Vector DB = embeddings + similarity search · MLflow = MLOps · Fargate = serverless containers

## Debugging Cloud Pipelines
- "Retrying micro batch" = failing · connection errors can hide auth errors
- `get-records | base64 --decode` · explicit schema · new checkpoint · stop old runs
- `user/` denied → admin · `assumed-role/` denied → fix role policy

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What three disciplines go into designing a warehouse beyond dimensional modeling?
A: Logical data architecture, which is how entities and business meaning are organized; physical database design, which is how data is stored for performance; and enterprise data architecture, which sets the boundaries between ingestion, transformation and consumption.

Q: How is Gold different from Silver, and Serving different from Gold?
A: Gold changes the shape, into a star schema with dimensions stored once. Serving changes the grain, with aggregates at the level the business asks about, like one row per station per day.

Q: What is a conformed dimension?
A: A dimension shared across fact tables where the meaning matches, like one date or station dimension used by both trips and snapshots.

Q: What is Kinesis Data Streams?
A: A serverless equivalent of Kafka. Producers write to a stream, consumers read from it, and it scales with shards instead of brokers and partitions.

Q: What's the difference between Kinesis Data Streams and Firehose?
A: Data Streams holds the messages for your own consumer code to process. Firehose is the consumer: you point it at a destination like S3 or Redshift and it delivers the data without you writing a consumer.

Q: What's the difference between MSK and Kinesis?
A: MSK is real Apache Kafka managed by AWS, so you use standard Kafka code and get more control. Kinesis is AWS's own Kafka-like service with its own SDK calls and less control, but it's serverless with minimal setup.

Q: What's a shard?
A: Kinesis's unit of capacity, like a Kafka partition. Each shard handles about 1 MB per second or 1,000 records per second of writes.

Q: What does the partition key do in a Kinesis put_record call?
A: It's hashed to choose the shard, so all records with the same key, like one station, go to the same shard and stay in order.

Q: When would you use the Kinesis Producer Library instead of the SDK?
A: For very high volumes of small records, like 100,000 transactions a second. KPL aggregates, batches and retries records instead of making one API call per record.

Q: What does the Kinesis Client Library do?
A: It helps you build your own consumers by handling shard assignment, load balancing across workers, checkpointing and recovery, coordinated through DynamoDB lease tables.

Q: What are the stream processing options on AWS?
A: Kinesis Firehose, Spark Structured Streaming on EMR, Glue Streaming, Managed Flink, and Lambda, which is only good in rare cases like demos.

Q: Why is Lambda rarely a good streaming consumer?
A: It's not distributed, has a 15-minute limit and keeps no state between invocations. It's fine for demos and light workloads, but not production.

Q: Why would you choose Managed Flink for fraud detection?
A: Flink processes each message individually with low latency and keeps per-customer state, which fraud detection needs. Spark Structured Streaming works in micro-batches.

Q: What is RAG?
A: Retrieval-Augmented Generation. A pipeline retrieves the most relevant pieces of your own data and adds them to the LLM's prompt, so it can answer questions about data it was never trained on.

Q: How is RAG different from a vector database?
A: RAG is the pipeline. A vector database is a kind of storage that holds embeddings and finds the most similar ones, and it's usually one component inside a RAG pipeline.

Q: Does RAG retrain the model?
A: No. The retrieved text is added to the prompt at question time. The model's weights don't change.

Q: Why is Glue not interchangeable with plain Spark?
A: Glue is serverless and has its own DynamicFrame, built for messy JSON where rows don't all have the same columns. It can run Spark code, but it's a distinct service.

Q: The Glue streaming job log says "retrying micro batch processing". What does that mean?
A: A batch is failing. A healthy streaming job doesn't retry, so look for the real error underneath.

Q: How do you check that a Kinesis producer is actually sending data?
A: Get a shard iterator, call get-records and decode the data from Base64. If you see valid JSON, the producer and stream are fine and the problem is downstream.

Q: An error says assumed-role something is not authorized. Who fixes it?
A: You can. It's the policy on your IAM role, so add the missing permission there. If it says your user is not authorized, that's group permissions and you need an admin.

Q: What should you shut down after a streaming demo?
A: The Glue streaming job, because it bills per DPU-hour until stopped. Also check anything that bills per hour, like a provisioned Kinesis stream or an RDS instance.
