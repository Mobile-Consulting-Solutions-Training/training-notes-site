---
title: Day 22 Vocabulary
description: Glossary of terms and definitions from the Training 22 notes.
sidebar:
  order: 22
---

Vocabulary — Study Guide Day 22

Source: notes/Training 22.md

## Warehouse Design
- **Logical data architecture** — How entities, relationships, facts, dimensions and business definitions are organized, independent of storage.
- **Physical database design** — How data is stored for performance: table structures, distribution, partitioning, sort keys, materialized views and indexing.
- **Enterprise data architecture** — Setting clear boundaries between ingestion, transformation, integration and consumption so business logic isn't duplicated.
- **Snowflake schema** — A dimensional model whose dimensions are normalized into sub-tables; can be more efficient than a star when many dimension tables are queried.
- **Star schema** — A central fact table joined directly to denormalized dimension tables.
- **Bronze layer** — Raw data exactly as ingested.
- **Silver layer** — Cleaned, typed, validated and deduplicated data.
- **Gold layer** — The analytical warehouse layer with dimensions, facts, explicit grain and consistent metrics; it changes the shape of the data.
- **Serving layer** — Query-optimized structures such as materialized aggregates and dashboard views; it changes the grain of the data.
- **Grain** — What one row of a table represents, e.g. one station per day.
- **Conformed dimension** — A dimension shared by multiple fact tables where its meaning is the same.
- **Data mart** — A subject-specific subset of the warehouse; avoid uncontrolled proliferation of specialized marts.
- **Materialized view / aggregate** — A precomputed, stored query result that dashboards read instead of scanning every observation.
- **Denormalization** — Repeating attributes across rows to avoid joins; done only when justified.
- **EXPLAIN** — Shows a query's execution plan so you can spot large scans or data redistribution.
- **DS_BCAST / DS_DIST** — Redshift plan labels meaning data is broadcast or redistributed across nodes, a sign the physical design needs work.
- **Enterprise bus architecture** — Kimball's approach of coordinating data marts through shared conformed dimensions.
- **Surrogate key** — A system-generated key used in place of a natural business key in a dimension.
- **Incremental loading** — Loading only new or changed data instead of reloading everything.
- **MPP (Massively Parallel Processing)** — An architecture where many nodes/slices process a query in parallel, as in Redshift.

## AWS Streaming
- **Kinesis Data Streams** — A serverless AWS equivalent of Kafka that holds messages for your own consumers to read.
- **Kinesis Firehose (Amazon Data Firehose)** — A managed message delivery system that takes the place of a consumer, batching and delivering stream records to destinations like S3 or Redshift.
- **MSK (Managed Streaming for Apache Kafka)** — Real Apache Kafka run as a managed cluster on AWS.
- **Stream** — The Kinesis object that does a Kafka broker/topic's job behind the scenes.
- **Shard** — A Kinesis unit of capacity and ordering, equivalent to a Kafka partition; each handles 1 MB/s and 1,000 records/s of writes.
- **Producer** — Anything that sends records into a stream.
- **Consumer** — Anything that reads records out of a stream and may process or deliver them.
- **Kinesis Agent** — A standalone Java app installed on a server that tails log files and forwards new lines to a stream.
- **AWS SDK** — Programming libraries for calling AWS services from your own code; the simplest Kinesis producer option for the class.
- **boto3** — The AWS SDK for Python.
- **KPL (Kinesis Producer Library)** — An optimized producer library for very high throughput that aggregates, batches, sends asynchronously and retries.
- **KCL (Kinesis Client Library)** — A library for building your own consumers that handles shard assignment, load balancing, checkpointing and worker recovery.
- **DynamoDB lease table** — The table KCL uses to coordinate which worker owns which shard.
- **Managed Service for Apache Flink** — AWS-managed Flink (formerly Kinesis Data Analytics) for low-latency, stateful, record-by-record stream processing.
- **Apache Flink** — A stream-processing engine that handles each message individually, suited to production use cases like fraud detection.
- **Stateful processing** — Stream processing that remembers information across records, e.g. per-customer transaction history.
- **Watermark** — A marker of event-time progress used to decide when windows can close despite late data.
- **Exactly-once** — A guarantee that each record affects the result exactly one time, achieved in Flink via checkpointing.
- **Checkpointing** — Periodically saving a stream processor's progress and state so it can recover; use a fresh checkpoint location after changing a job's schema or logic.
- **Dynamic partitioning** — Firehose feature that writes records into S3 folders based on values in the data.
- **Format conversion** — Firehose feature that converts records, e.g. JSON to Parquet, before delivery.
- **put_record** — boto3 Kinesis call that writes one record to a stream.
- **get_records** — Kinesis API call that reads records from a shard using a shard iterator.
- **Shard iterator** — A pointer to a position in a shard from which `get-records` reads.
- **PartitionKey** — A value hashed to choose a record's shard, keeping records with the same key in order on one shard.
- **Spark Structured Streaming** — Spark's streaming engine that processes data in micro-batches; can run on EMR or EMR Serverless as a Kinesis consumer.
- **Micro-batch** — Processing a stream as a series of small batches rather than record by record.
- **Glue Streaming** — A continuously running Glue job using Spark Structured Streaming to read a stream; serverless and distributed.
- **EMR Serverless** — A serverless way to run distributed Spark jobs on AWS.
- **Event source mapping** — AWS feature that collects stream records and invokes a Lambda with a whole batch instead of once per message.
- **Lambda consumer** — A Lambda reading a stream; only good in rare cases like demos because it isn't distributed and has a 15-minute max runtime.
- **Distributed** — Spreading work across many machines; most serverless services are not, except Glue and EMR Serverless.
- **Kafka Connect sink** — A Kafka component that delivers topic data to an external system, the Kafka analogue of Firehose.
- **Consumer group** — In Kafka, a set of consumers reading a topic together; many groups can read one topic independently, as many consumers can read one Kinesis stream.
- **Capacity mode** — Kinesis setting choosing on-demand or provisioned capacity.
- **On-demand mode** — Kinesis capacity mode where you pay for what you use; good for streams not kept up all the time.
- **Provisioned mode** — Kinesis capacity mode where you set the shard count and pay per shard-hour; good for always-on streams.
- **Retention period** — How long a stream keeps records; Kinesis defaults to 24 hours.
- **Max record size** — The largest single record allowed, 1 MB in Kinesis, same as Kafka's default.
- **Base64** — The encoding Kinesis uses for record data, which must be decoded to read the JSON.
- **Consumer lag** — How far a consumer falls behind the newest records in a stream.

## AWS Databases
- **RDS (Relational Database Service)** — A virtual database server where AWS runs a relational engine (MySQL, Postgres, MariaDB, Oracle, SQL Server, Aurora) and handles patching, backups and failover.
- **Aurora** — AWS's own MySQL- and PostgreSQL-compatible engine designed for speed, with storage replicated across 3 AZs.
- **Aurora Serverless** — An Aurora option that scales capacity automatically.
- **MySQL** — The most common open-source web-app relational database.
- **PostgreSQL** — A feature-rich open-source relational database from which Redshift's SQL dialect descends.
- **MariaDB** — An open-source fork of MySQL usable as a drop-in replacement.
- **Oracle** — A commercial enterprise relational database with licensing costs.
- **Microsoft SQL Server** — Microsoft's commercial enterprise relational database.
- **OLTP (Online Transaction Processing)** — Workloads of many small application reads and writes, served by row-oriented databases like RDS.
- **OLAP (Online Analytical Processing)** — Analytical workloads scanning millions or billions of rows, served by columnar warehouses like Redshift.
- **Row-oriented storage** — Storing each row's values together, suited to OLTP.
- **Columnar storage** — Storing each column's values together, suited to OLAP scans.
- **Read replica** — A read-only copy of a database used to scale reads.
- **Multi-AZ failover** — Automatic switch to a standby database in another Availability Zone if the primary fails.
- **Point-in-time restore** — Restoring a database to its state at a specific past moment from automated backups.

## ML and Gen AI Projects
- **Streamlit** — A Python library that turns a script into an interactive web app or dashboard without front-end code.
- **AWS Fargate** — Serverless containers that run Docker containers without managing servers, used with ECS or EKS.
- **SageMaker** — AWS's ML platform to train, deploy and host models as endpoints.
- **RAG (Retrieval-Augmented Generation)** — A pipeline that funnels specific data to where an LLM can read it, retrieving relevant pieces into the prompt so it answers natural-language questions about your data without retraining.
- **Vector database** — A database formatted for AI rather than humans that stores embeddings and runs similarity search; often the storage inside a RAG pipeline.
- **Embedding** — A vector of numbers capturing a chunk of text's meaning, produced by an embedding model and stored in a vector database.
- **Chunking** — Splitting documents into small pieces before embedding them.
- **Similarity search** — Finding stored items closest in meaning to a query vector.
- **Tokenizer** — The component that splits text into tokens (numbers) an LLM processes.
- **LLM (Large Language Model)** — A model trained on large text corpora that generates natural-language answers.
- **pgvector** — A PostgreSQL extension that adds vector storage and similarity search.
- **MLflow** — An open-source MLOps platform for experiment tracking, model registry and deployment.
- **MLOps** — Deployment and management of ML and AI pipelines: feeding data to models, training and serving them.
- **REST API** — A web interface through which a finished model can be called.
- **SafeTensors** — A file format for model weights that can be deployed in an environment you choose.

## Glue, IAM and Debugging
- **DynamicFrame** — Glue's data structure, a DataFrame without the rule that every row has the same columns, built for messy JSON.
- **Inline policy** — A permission policy embedded directly in one IAM role.
- **Execution role** — The IAM role a Lambda or Glue job runs as; permissions must be added to the role the function actually uses.
- **rds-db:connect** — IAM action that lets a role log into an RDS database with IAM authentication.
- **IAM database authentication** — Connecting to RDS with an IAM role and a short-lived token instead of a stored password.
- **Cluster resource ID** — RDS's internal cluster ID used in the `rds-db:connect` resource ARN, not the cluster name.
- **put-role-policy** — CLI command that adds an inline policy to a role without overwriting others.
- **G.1X worker** — A standard Glue worker type.
- **DPU (Data Processing Unit)** — Glue's billing unit of compute; streaming jobs bill per DPU-hour until stopped.
- **Batch window** — In a Glue streaming job, how much stream time each micro-batch covers (30 seconds in the demo).
- **Schema inference** — Automatically guessing a schema from data; a poor choice when the record structure is already known.
- **StructType / StructField** — PySpark classes for defining an explicit schema.
- **Job run ID** — The identifier of one execution of a Glue job, used to check status or stop it.
- **aws logs tail** — CLI command that streams CloudWatch logs; `--follow` shows only new logs, `--since` shows past ones.
- **batch-stop-job-run** — Glue CLI command that stops running job runs.
- **SHA (checksum)** — A hash of a file's contents used to verify the S3 copy matches the local file.
- **EventBridge schedule** — A rule that triggers a target such as a Lambda on a recurring schedule.
- **ARN (Amazon Resource Name)** — A unique identifier for an AWS resource; retrieving one proves the resource exists.
- **StatusCode 200** — The success response from invoking a Lambda.
- **$LATEST** — The Lambda version alias for the most recent unpublished code.
