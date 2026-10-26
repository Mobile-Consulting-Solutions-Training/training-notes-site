---
title: "Training 22 - Warehouse Design and AWS Streaming"
description: "Warehouse design beyond dimensional modeling, then Kinesis Data Streams, Kinesis Firehose and MSK."
sidebar:
  order: 22
---

Teacher: Evan Flint

Syllabus Day 23 (per file numbering; Mon Oct 12) - topics: warehouse design beyond dimensional modeling (reading list), then AWS streaming: Kinesis Data Streams, Kinesis Firehose, MSK. More filled in as class goes.

---

# Data Warehouse Design (Beyond Dimensional Modeling)

Q. How do you decide what belongs in which tables, schemas, layers and storage structures?

A. (Teacher's definition) Evan posted an AI-generated reading list in answer to a student's question. The question it addresses: given business requirements, datasets and query patterns, how do we decide what belongs in which tables, schemas, layers and storage structures so the warehouse stays coherent, maintainable and performant? Kimball's *The Data Warehouse Toolkit* (already shared) covers facts, dimensions, star schemas and slowly changing dimensions, but not this broader architecture question.

Expanded: There's no single guide for this. Evan said he "can't point you to a single guide". It combines three disciplines, and the core idea is that **logical coherence and physical performance are separate design problems that have to be solved together.** Just before posting the list, Evan also noted that if many dimension tables get queried, a **snowflake schema** can be the more efficient design than a star schema. The goal is whatever design is most usable for the people querying it in production.

**Expanded (correction):** snowflaking normalizes dimensions into more tables, which *adds* joins, so it is rarely faster to query. Its benefits are less duplicated storage and easier maintenance of very large, deep dimension hierarchies. For query performance on columnar MPP warehouses, the star schema is the usual default (see `Training 5.md`).

| Discipline | Question it answers | Examples |
|---|---|---|
| **Logical data architecture** | How are entities and business meaning organized? | Entities, relationships, facts, dimensions, business domains, shared definitions |
| **Physical database design** | How is it stored so the workload runs fast? | Table structures, distribution, partitioning, clustering/sort keys, materialized views, indexing |
| **Enterprise data architecture** | Where are the boundaries between stages? | Ingestion vs transformation vs integration vs consumption; avoid duplicated or inconsistent business logic |

---

Q. What does a coherent layered architecture look like for the Citi Bike project?

A. (Teacher's definition, from the posted material)

| Layer | Purpose | Citi Bike contents |
|---|---|---|
| **Bronze** | Raw data | Station information, station status, trip events |
| **Silver** | Cleaned and standardized | Validated station records, typed timestamps, deduplicated events |
| **Gold** | Analytical warehouse | `dim_station`, `dim_date`, `fact_station_snapshot`, `fact_trip`; conformed dimensions, explicit grain, consistent metrics |
| **Serving** | Optimized query structures | Materialized aggregates, dashboard views, frequently requested KPIs |

Expanded: Picking a layer for each table is only part of the work; the design questions below matter more. This answers "how do I make Gold more than a copy of Silver?" Gold changes the **shape** (star schema, dimensions stored once). Serving changes the **grain** (aggregates at the level the business asks about, like `gold.agg_station_daily` = one row per station per day).

| Design question | Architectural principle |
|---|---|
| Should station names repeat in every snapshot? | Keep station attributes in a dimension; denormalize only when justified |
| Should we store every 5-minute observation? | Preserve the historical grain the business needs |
| Should dashboard queries scan every observation? | Consider a materialized hourly or daily aggregate |
| Should trips and station snapshots share dimensions? | Reuse **conformed dimensions** where the meaning matches |
| Should every analytical query get its own table? | No; avoid uncontrolled proliferation of specialized marts |
| Should we hand-set distribution and sort keys? | Start with engine recommendations and measured workloads, then override where justified |

---

Q. What exercise does the posted material suggest?

A. (Teacher's definition, from the posted material) Design a warehouse for five specified analytical queries, document the grain and relationships, then use `EXPLAIN` and query execution statistics to find where the physical design needs improvement.

Expanded: This forces the main lesson: a good warehouse isn't just a pile of correctly normalized or dimensional tables. It's an integrated model shaped by **business meaning**, **expected workloads**, and **how the database engine behaves**. Your Q1–Q5 Citi Bike queries are a ready-made starting point: turn on the **Explain** toggle in Query editor v2 and look for large scans or data redistribution (`DS_BCAST`, `DS_DIST`) in the plan.

---

## Reading List

Suggested order: **1 → 4/5 → 2**. Lifecycle Toolkit for organizing the system, the AWS Redshift guides for turning it into fast physical structures, DDIA for the engineering trade-offs underneath.

| # | Resource | Author / Source | Why read it | Free? |
|---|---|---|---|---|
| 1 | **The Data Warehouse Lifecycle Toolkit** (2nd ed., 2008) | Ralph Kimball et al. | **Best overall match.** Whole-warehouse architecture: coordinating data marts, gathering requirements, enterprise bus architecture, conformed dimensions, architecture planning, physical design | Official design templates free from Kimball Group; book is commercial |
| 2 | **Designing Data-Intensive Applications** (2017) | Martin Kleppmann | *Why* one architecture beats another: storage engines, indexes, batch, streaming, replication, partitioning. When to precompute, when to denormalize | Free companion study guide; book is commercial |
| 3 | **The Data Warehouse ETL Toolkit** (2004) | Ralph Kimball, Joe Caserta | Where processing should happen before analytical tables: staging, transformation placement, data quality, surrogate keys, incremental loading. Maps directly to Bronze/Silver/Gold | Commercial |
| 4 | **AWS Prescriptive Guidance: Query Best Practices for Amazon Redshift** | AWS | Most relevant to class right now: table design, query optimization, distribution, physical architecture | **Free official PDF** |
| 5 | **Amazon Redshift: Database Design and Performance Best Practices** | AWS docs | More technical: distribution styles, sort keys, materialized views, optimizing joins in a columnar MPP warehouse | **Free online** |
| 6 | **Kimball Group DW/BI Lifecycle Methodology** | Kimball Group | How requirements, technical architecture, dimensional modeling and deployment fit into one system | **Free online** |

---

# AWS Streaming

Q. What are the streaming services on AWS?

A. (Teacher's definition) Kinesis Data Streams is a serverless equivalent of Kafka. Kinesis Firehose is a message delivery system which takes the place of a consumer within a delivery pipeline.

Expanded: AWS has two routes for streaming. **MSK (Managed Streaming for Apache Kafka)** is literally Kafka on AWS: you provision a cluster, scale it as high as you want, and write producers and consumers exactly as you would for on-premises Kafka, with AWS handling more of the setup and recovery. **Kinesis** is *not* Kafka, just very similar. Producers and consumers are written slightly differently, but the concepts carry over.

| Kafka | Kinesis Data Streams |
|---|---|
| Producer → **broker** → consumer | Producer → **stream** → consumer |
| You see and manage the brokers | The stream does the broker's job "behind the veil"; you have limited control |
| You pay for the cluster | Provisioned: per **shard-hour** + PUT payload units. On-demand: per GB written/read + a per-stream hourly charge |
| Scale by adding brokers and partitions | Scale with **shards** (comes up in interviews) |

---

Q. What's the difference between Kinesis Data Streams and Kinesis Firehose?

A. (Teacher's definition, same as above) "Kinesis Firehose is a message delivery system which takes the place of a consumer within a delivery pipeline."

Expanded: **Data Streams** holds messages so that *your* consumer code can read and process them. **Firehose** *is* the consumer: you don't write one. You point Firehose at a destination (S3, Redshift, etc.) and it batches and delivers the messages for you.

| | Kinesis Data Streams | Kinesis Firehose |
|---|---|---|
| Role in the pipeline | The stream (like a Kafka broker/topic) | The consumer / delivery step |
| Who writes the consumer? | You | Nobody; Firehose replaces it |
| Typical destination | Your own app, Lambda, Flink | S3, Redshift, OpenSearch, etc. |
| Kafka analogy | Kafka broker | A Kafka Connect sink |
| Citi Bike example | Stream station-status events for real-time processing | Land the same events straight into S3 Bronze without writing a consumer |

---

Q. What are the producer and consumer options on the Kinesis console?

A. (Teacher's definition, posted by Evan) The AWS Kinesis console shows three producer options and three consumer options. These are different approaches to getting data into Kinesis Data Streams and processing it afterward. Not all six are equivalent technologies: some are libraries for writing your own applications, some are managed AWS services, and some are specialized tools. Kinesis transports events, while Flink or Spark processes streams, Firehose delivers them, and KCL helps custom consumers read them reliably.

Expanded: A **producer** is anything that sends records *into* a stream. A **consumer** reads records *out* and may transform, aggregate, analyze or deliver them. The key is knowing what *kind* of thing each option is.

**Producers**

| Option | What it is | Deployed on | Best for | Example | Limitation |
|---|---|---|---|---|---|
| **Kinesis Agent** | Standalone **Java app** installed on a server that watches log files and forwards new lines | EC2, on-prem Linux | Log collection, file-based ingestion | 20 Linux servers' app logs: install the agent, point it at the log folders, no custom code | Basic parsing only; not for complex logic; less flexible for cloud-native designs |
| **AWS SDK** | Programming libraries (Python = **boto3**, also Java, JS, .NET, Go) to call Kinesis from your own code | Lambda, ECS, EC2, on-prem, anywhere | Custom app events, APIs, IoT, integrations | Citi Bike Lambda sends station records. **Simplest option for our project** | You write and own all the logic |
| **Kinesis Producer Library (KPL)** | Optimized **producer library** for very high throughput | Your app (Java) | Huge volumes of small records | Bank with 100,000 transactions/sec: one SDK call per transaction is inefficient, so KPL aggregates and batches | Not a streaming platform, just a faster producer |

KPL's main features:
- **Aggregation:** packs many small records into fewer Kinesis records.
- **Batching:** sends groups instead of one request each.
- **Asynchronous:** the producer keeps working while sends happen.
- **Retries:** handles transient failures.
- **Metrics:** reports to CloudWatch.

**SDK producer example (boto3):**

```python
import boto3
import json

kinesis = boto3.client("kinesis", region_name="us-east-2")

record = {"station_id": "123", "num_bikes_available": 8}

kinesis.put_record(
    StreamName="citibike-stream",
    Data=json.dumps(record).encode("utf-8"),
    PartitionKey=record["station_id"],   # decides which shard the record lands on
)
```

The **PartitionKey** is hashed to pick the shard, so all records for one station go to the same shard and stay in order. It's the same idea as a Kafka message key choosing the partition.

**Consumers**

| Option | What it is | AWS runs it? | Best for | Example | Limitation |
|---|---|---|---|---|---|
| **Managed Apache Flink** | Fully managed real stream-processing engine (like Spark Structured Streaming in purpose); Java or SQL | Yes | Complex, low-latency, **stateful** analytics; fraud detection | Bank flags a customer with 5 transactions in different countries within 10 minutes: Flink keeps per-customer state and checks it continuously | More to learn; heavier than needed for simple jobs |
| **Amazon Data Firehose** | Fully managed **delivery** service into S3, Redshift, OpenSearch | Yes | Landing streams in data lakes/warehouses with minimal infrastructure | Kinesis → Firehose → convert to Parquet → **S3 Bronze** | Not a general compute engine; no complex state, no Spark |
| **Kinesis Client Library (KCL)** | Library for building **your own** consumers; handles the hard coordination | No (EC2, ECS, EKS) | Custom consumers where you control logic and infrastructure | 10 consumer instances on ECS share one stream; KCL assigns shards so they don't duplicate work | Coordination library, not a full processing framework |

- **Flink** supports: stateful processing, event-time windows and **watermarks**, continuous aggregations, stream joins, **exactly-once** state via checkpointing, complex event processing.
- **Firehose** supports: buffering/batching, **format conversion (JSON → Parquet)**, transforms via Lambda, **dynamic partitioning** in S3, compression, retries and failure handling.
- **KCL** handles: shard discovery and assignment, load balancing across workers, **checkpointing**, recovery when a worker fails, coordination through **DynamoDB lease tables**.

**Side-by-side**

| Technology | Primary purpose | AWS manages compute? | Custom processing |
|---|---|---|---|
| Kinesis Agent | Collect logs | No | Minimal |
| AWS SDK | Send custom events | Depends on hosting | Full producer logic |
| KPL | High-throughput producer | No | Producer-side logic |
| Managed Flink | Stream processing | Yes | Extensive, stateful |
| Data Firehose | Stream delivery | Yes | Limited transformations |
| KCL | Build custom consumers | No | Full custom consumer logic |

---

Q. Where do Spark Structured Streaming and Lambda fit, since they're not on the console page?

A. (Teacher's definition, posted by Evan) Spark Structured Streaming is another consumer option, even though it isn't shown on this console page. You can deploy Spark streaming applications on EMR or EMR Serverless and read Kinesis records using a compatible connector. These consumer approaches are alternatives, but they can also run simultaneously as independent applications against the same Kinesis stream.

Expanded: One stream can feed **many consumers at once**, each doing a different job. Same as multiple Kafka consumer groups reading one topic.

```
                          ┌─▶ Managed Flink ............ low-latency, stateful processing
                          ├─▶ Spark Structured Streaming (EMR) .. micro-batch processing
Producer ─▶ Kinesis ──────┼─▶ KCL application ......... custom consumer code
         Data Stream      ├─▶ Data Firehose ........... managed delivery to S3/Redshift
                          └─▶ Lambda (event source mapping) .. simple processing
```

**Recommended choices for the Citi Bike class:**

| Requirement | Recommended technology |
|---|---|
| Produce station-status events | AWS SDK (boto3) in Lambda |
| Simple stream processing | Lambda consumer with a Kinesis event source mapping |
| Demonstrate a full streaming engine | Managed Apache Flink |
| Deliver raw streaming records to S3 | Amazon Data Firehose |
| Demonstrate Spark streaming | EMR Serverless with Spark |
| Write processed data into RDS | Lambda or a custom consumer using database connections |

**Today's demo pipeline:** Citi Bike Lambda (producer) → **Kinesis Data Stream** → **Lambda consumer** → **RDS PostgreSQL**. Lambda isn't one of the three consumers on the console page, but it has native Kinesis integration and is much simpler than Flink, Spark or KCL. This is the "rare case" from earlier: good for a demo, but it doesn't show a full streaming framework. If that were the goal, the pick would be Managed Flink with a small Java/SQL app writing to RDS.

---

## MSK vs Kinesis

| | MSK | Kinesis Data Streams |
|---|---|---|
| What it is | Real Apache Kafka, managed by AWS | AWS's own Kafka-like service |
| Code | Standard Kafka producers/consumers | Kinesis-specific SDK calls |
| Control | High (cluster, brokers, configs) | Limited (shards) |
| Choose when | You already use Kafka, or need its ecosystem and control | You want serverless and minimal setup on AWS |

---

Q. How does Kinesis Data Streams scale, and what limits does a shard have?

A. A stream scales by adding **shards**. Each shard takes about 1 MB/s or 1,000 records/s of writes and serves 2 MB/s of reads.

**Expanded:**

| Topic | Detail |
|---|---|
| Write limit per shard | 1 MB/s or 1,000 records/s |
| Read limit per shard (shared) | 2 MB/s total, split across **all** standard consumers, and 5 `GetRecords` calls/s |
| **Enhanced fan-out (EFO)** | Each registered consumer gets its **own** 2 MB/s per shard, pushed over HTTP/2 (`SubscribeToShard`), with lower latency. Costs extra |
| Shard iterator types | `TRIM_HORIZON` (oldest kept record), `LATEST` (only new records), `AT_SEQUENCE_NUMBER` / `AFTER_SEQUENCE_NUMBER`, `AT_TIMESTAMP` |
| Resharding | **Split** a shard to add capacity, **merge** two to save cost (provisioned mode). On-demand mode does this automatically |
| Retention | 24 hours default, up to 365 days |
| Throttling | Exceeding a shard's limits returns `ProvisionedThroughputExceededException`; retry with exponential backoff (the SDK and KPL do this) |

**Hot shards:** the partition key is hashed to pick a shard, so a skewed key (one very busy station, or a constant key) sends most traffic to one shard and throttles it while others sit idle. Same problem as a hot Kafka partition (`Training 13.md`). Fixes: a higher-cardinality key, adding a random suffix (then aggregating downstream), or splitting the hot shard.

**Firehose delivery settings worth knowing:** **buffering hints** (flush when the buffer reaches a size, e.g. 64-128 MB for Parquet, or an interval, e.g. 60-300 s, whichever comes first) and an S3 **prefix** with dynamic partitioning, e.g. `bronze/station_status/!{partitionKeyFromQuery:station_id}/` or `year=!{timestamp:yyyy}/`. Bigger buffers mean fewer, larger files.

**Interview lines:**
- "Kinesis scales by shards: about 1 MB/s in and 2 MB/s out per shard. I size the shard count from peak throughput, or use on-demand mode if traffic is unpredictable."
- "Enhanced fan-out gives each consumer its own 2 MB/s per shard instead of sharing it, so I use it when several consumers read the same stream with low latency."
- "For a hot shard I fix the partition key first: more cardinality, or salting the key, and split the shard if needed. Producers retry throttling errors with backoff."

---

Q. What are the options for stream *processing* (transforming data in flight) on AWS?

A. (Teacher's definition) Streaming Processing Options on AWS:
1. Kinesis Firehose
2. Spark Structured Streaming consumer running an EMR cluster
3. Glue Streaming Consumer
4. Managed Streaming for Apache Flink
5. Lambda functions - ONLY A GOOD SOLUTION IN RARE CASES

Expanded: A stream (Kinesis Data Streams or MSK) only **moves** messages; something else has to **process** them. Evan's history with Firehose: it used to just deliver data, with no way to transform it, so for real transformations you had to write a Spark Structured Streaming job. Evan said Firehose now has a code execution environment where pandas or plain Python logic is fine. Precisely: Firehose itself runs no user code. Its **data transformation** feature invokes a **Lambda function you attach** on each buffered batch (up to about 6 MB per invocation, within the Lambda timeout), and that Lambda can use pandas. Firehose also has built-in JSON → Parquet/ORC conversion (using a Glue table schema) and dynamic partitioning, with no code. Either way, **don't put Spark code in Firehose**: it's serverless and **not distributed**. That's true of almost every serverless service. The exceptions are **Glue** and **EMR Serverless**, which were designed from the ground up to run distributed while still being serverless. MSK and Flink pair up: MSK (Kafka) is the streaming *pipeline*, but it doesn't do the stream *processing*, and Managed Flink handles that side.

| # | Option | What it is | Distributed? | Good for | Watch out for |
|---|---|---|---|---|---|
| 1 | **Kinesis Firehose** | Managed delivery into S3/Redshift/etc., with optional transform code | No | Simple "land the stream in storage" with light per-record cleanup | Not for Spark or heavy transforms |
| 2 | **Spark Structured Streaming on EMR** | Your own Spark streaming job on an EMR cluster (or EMR Serverless) | Yes | Heavy transforms, joins, windowed aggregations; full control | You manage the cluster and job; cost of always-on compute |
| 3 | **Glue Streaming** | Glue job (Spark Structured Streaming under the hood) reading the stream | Yes | Same Spark skills as your Glue batch job, serverless | Glue cost per DPU-hour while running continuously |
| 4 | **Managed Service for Apache Flink** | AWS-managed Flink (formerly *Kinesis Data Analytics*) | Yes | True record-by-record, low-latency stateful processing; pairs with MSK or Kinesis | New framework to learn (Flink, not Spark) |
| 5 | **Lambda** | Function triggered by batches of stream records | No | Demos and simple/light workloads | Not distributed, 15-min max runtime, no built-in state across invocations |

Citi Bike link: your Glue Bronze → Silver job is batch Spark. **Option 3** is the same code style turned into a continuously running streaming job.

---

Q. Why is Lambda only a good streaming consumer in rare cases?

A. (Teacher's definition) Lambda functions - ONLY A GOOD SOLUTION IN RARE CASES. One of those rare cases is simplicity for demonstration purposes, so we may write consumer code in Lambda for class demos. Lambda is not a good design for any kind of production application.

Expanded: Lambda is serverless and **not distributed**. You *can* package PySpark as a dependency (zip file on S3, like the dependency packaging shown in class) and it will run. But it will probably be **slower than plain pandas code**, because Spark's whole advantage is spreading work across many machines, and a Lambda is one small machine.

How Lambda actually reads a stream: through an **AWS event source mapping**. AWS collects records from the stream and invokes the Lambda only after a certain amount of data has arrived, passing it the whole **batch**. Evan's working metaphor (he said he wants more hands-on time to confirm it): it's like AWS doing the **micro-batching** you see in Spark Structured Streaming, but feeding the batches to a Lambda instead of a Spark job.

Why that matters, cost: at 1,500 messages per second, invoking Lambda once per message means 1,500 invocations per second. Even at a tiny fraction of a cent each, that adds up to real dollars per unit of time. Batching through the event source mapping keeps the invocation count down.

| | Lambda one call per message | Lambda via event source mapping | Spark Structured Streaming |
|---|---|---|---|
| Invocations at 1,500 msg/s | 1,500 per second | Far fewer (one per batch) | One continuously running job |
| Processing model | Per record | Micro-batch (AWS-managed) | Micro-batch (Spark-managed) |
| Distributed? | No | No | Yes |
| Use for | Never (per-record invocation) | Demos and light production workloads | Production, heavy transforms |

**Expanded (correction):** "not good for any production application" is overstated. Kinesis → Lambda through an event source mapping is a widely used production pattern for **light, per-record or small-batch work**: enrichment, routing, filtering, writing to DynamoDB. The mapping supports batch size and batching window, a **parallelization factor of up to 10 concurrent batches per shard**, bisect-batch-on-error, and on-failure destinations. Lambda is the wrong choice for **heavy, stateful or windowed** processing (joins, sessionization, large aggregations), where Flink or Spark Structured Streaming fits.

**Interview line:** "Lambda with an event source mapping is fine in production for light stateless processing of a stream. Once I need state, windows or heavy transforms, I move to Managed Flink or Spark Structured Streaming."

---

# AWS Databases

Q. What is RDS?

A. (Teacher's definition) RDS: Relational Database Service. RDS is a virtual database server. RDS is basically a database server where you can manage your data with any kind of SQL that you want.

You can use:
- MySQL
- Postgres
- MariaDB
- Oracle
- Microsoft SQL Server
- AWS Aurora - an AWS-designed SQL program, designed for speed

See `Training 18.md` ("RDS") for the main RDS entry (Multi-AZ, read replicas, RDS vs EC2, extraction patterns). This entry is a short recap.

Expanded: RDS is AWS running a normal relational database (PostgreSQL, MySQL, MariaDB, Oracle, SQL Server) for you on a virtual server. You pick the engine and the instance size, and AWS handles installing it, patching, backups, failover and storage. You still design the tables and write the SQL. It's an **OLTP** database: built for an application's many small reads and writes. It is not a warehouse for big analytical scans, which is what Redshift (OLAP) is for. **Aurora** is AWS's own cloud-built MySQL/PostgreSQL-compatible engine, offered through RDS.

| | RDS | Redshift |
|---|---|---|
| Workload | OLTP: app transactions, row lookups and updates | OLAP: analytics over millions/billions of rows |
| Storage | Row-oriented | Columnar |
| Scale | One server (plus read replicas) | MPP: many nodes/slices in parallel |
| In a pipeline | Often the **source** (the app's database) | The **destination** (the warehouse, Gold layer) |
| Self-managed equivalent | Postgres installed on your own server | — |

| Engine | Who makes it | Notes |
|---|---|---|
| **MySQL** | Oracle (open source) | Most common web-app database |
| **PostgreSQL** | Open source | Feature-rich; Redshift's SQL dialect descends from it |
| **MariaDB** | Open source fork of MySQL | Drop-in MySQL replacement |
| **Oracle** | Oracle | Commercial, enterprise; licensing costs |
| **Microsoft SQL Server** | Microsoft | Commercial, enterprise; common in Windows/.NET shops |
| **Aurora** | AWS | AWS-built, MySQL- or PostgreSQL-compatible, designed for speed: storage replicated across 3 AZs, faster failover; also has an Aurora Serverless option |

| You manage | AWS manages |
|---|---|
| Schema, tables, indexes, queries, users | Hardware, OS, DB install, patching |
| Picking engine, instance size, storage | Automated backups, point-in-time restore |
| Security groups / who can connect | Multi-AZ failover, storage scaling |

---

# Upcoming Projects (The Fun Stuff)

Q. What's on Evan's agenda after the syllabus material?

A. (Teacher's definition) The Fun Stuff:
1. Running a real time dashboard using Streamlit and AWS Fargate
2. An ML and Gen AI pipeline
   - 1a. Deployment of an ML app to Sagemaker and connecting that to the Redshift data and the Streamlit app
   - 1b. Deployment of a Gen AI powered app that uses a RAG pipeline
   - 1c. Management of the ML and Gen AI pipelines using MLFlow

Expanded: Together these build one connected system on top of the warehouse you already have. Redshift (Gold) is the data source; the ML model and the dashboard both read from it.

| Piece | What it is | Role in the project |
|---|---|---|
| **Streamlit** | Python library that turns a script into an interactive web app/dashboard, no front-end code | The real-time dashboard UI |
| **AWS Fargate** | Serverless containers: run a Docker container without managing servers (used with ECS or EKS) | Hosts the Streamlit app 24/7 |
| **SageMaker** | AWS's ML platform: train, deploy and host models as endpoints | Hosts the ML model that reads Redshift data and serves predictions to Streamlit |
| **Redshift** | Your warehouse (Gold layer) | The data everything reads from |
| **RAG pipeline** | Retrieval-Augmented Generation | Lets a Gen AI app answer questions about *your* data |
| **MLflow** | Open-source MLOps platform: experiment tracking, model registry, deployment | Manages the ML and Gen AI pipelines (see "Goal 1c: MLflow and MLOps" below) |

```
Kinesis / Lambda ──▶ S3 ──▶ Glue ──▶ Redshift (Gold)
                                       │
                         ┌─────────────┼──────────────┐
                         ▼             ▼              ▼
                 SageMaker model   Streamlit on    Gen AI app (RAG)
                  (predictions) ─▶   Fargate
```

---

Q. What is RAG?

A. (Teacher's definition) RAG basically is a pipeline that funnels specific data to a directory where an LLM can read it and then answer natural language questions based on it.

Expanded: **RAG = Retrieval-Augmented Generation.** An LLM only knows what it was trained on, so it doesn't know your company's or your Citi Bike data. RAG fixes that without retraining the model. When a question comes in, the pipeline **retrieves** the most relevant pieces of your data and adds them to the prompt. The LLM then **generates** an answer grounded in them.

| Step | What happens | Citi Bike example |
|---|---|---|
| 1. Ingest | Collect your documents/data | Station data, docs, reports |
| 2. Chunk | Split into small pieces | One chunk per station summary |
| 3. Embed | Turn each chunk into a vector (list of numbers capturing meaning) | Vector for "Centre St & Worth St, 114 of 120 bikes…" |
| 4. Store | Save vectors in a **vector database** | — |
| 5. Retrieve | Embed the question and find the closest chunks | "Which stations are usually empty?" → the most similar chunks |
| 6. Generate | LLM answers using those chunks as context | Natural-language answer citing your data |

---

Q. How is RAG different from a vector database?

A. (Teacher's definition) RAG is distinct but similar to Vector Databases, which are a specific kind of database that is formatted specifically for AI to read it rather than humans.

Expanded: They're related but not the same thing. **RAG is the pipeline (the process); a vector database is often the storage it uses** in steps 4–5 above. A vector database stores embeddings and is built to answer "which stored items are most *similar in meaning* to this one?" quickly. A normal SQL database answers exact matches like `WHERE station_id = '123'`.

| | RAG | Vector database |
|---|---|---|
| What it is | A pipeline / pattern | A kind of database |
| Job | Retrieve relevant data and feed it to an LLM to answer questions | Store embeddings and run similarity search |
| Relationship | Usually *uses* a vector DB for retrieval | One component *inside* a RAG pipeline |
| Examples | LangChain/LlamaIndex apps, Amazon Bedrock Knowledge Bases | pgvector (Postgres on RDS/Aurora), OpenSearch, Pinecone, Chroma |

**Interview line:** "RAG retrieves relevant chunks of my own data, usually by similarity search over embeddings in a vector database, and adds them to the LLM's prompt, so it can answer about private data without retraining. The data engineering work is the ingestion: chunking, embedding, metadata and keeping the index fresh."

These notes are the starting point for roadmap Day 39 (RAG & Vector Data Eng.); the local-AI and Bedrock follow-up is in `Training 25.md`.

---

# Class Walkthrough: Kinesis -> Glue Streaming -> Aurora

---

## Vector databases: what's actually in them

- A vector database is **unreadable to humans**: if you query it yourself, all you see is series of numbers.
- Those numbers come from passing natural language through a **tokenizer**, which converts words into numbers that carry meaning values inside the LLM.
- Evan's mental model: adding data to a vector database is "kind of like adding things directly to the ML model's training". The model runs its normal weights, then also uses the extra information you supplied, so it can answer questions a public model can't.
- **Example:** ask ChatGPT for a summary of new business from Bank of America's sales department over the last 3 months. It will either refuse (terms of service) or say it doesn't have that information and piece something together from the internet. It will **never** go into Bank of America's databases, because the bank blocks outside access, as it should. But a consultant working *for* Bank of America could put that data into a RAG pipeline / vector database, and the AI could then give a correct natural-language answer about it.
- **Interview tip:** "RAG pipelines and vector databases are 100% the AI subject that comes up most frequently in data engineering interviews."

> Precision note: technically RAG does **not** change the model's training or weights. The retrieved text is added to the *prompt* at question time. Two related but separate steps: **embeddings** (vectors from an embedding model) are what's stored and searched, and the **tokenizer** is what splits text into tokens. Evan's "adding to the training" is the intuition for the *effect*: the model can now answer about your private data.

---

## Goal 1c: MLflow and MLOps

Evan added a third goal to the Fun Stuff list: **1c. Management of the ML and Gen AI pipelines using MLflow.**

- **MLflow** is increasingly asked about in interviews: less than RAG, but there's an organizational push at his company to teach data engineers MLflow.
Q. What is MLOps?

A. (Teacher's definition, as said in class) Deployment and management of ML and AI pipelines, as described below.

- **MLOps** = deployment and management of ML and AI pipelines: delivering data from the regular database to those pipelines, training the models on that data, and letting the models get progressively better at answering questions about it. The "lower-level pipes" of how an ML model actually works.
- This is what's under the hood when you ask ChatGPT or Claude something: engineers deploy the website, connect it to the model, and make the model able to respond.
- **We do NOT do model development** (that's AI researchers). We assume the model is finished and available either through a **REST API** or as a **SafeTensors file** we deploy ourselves. The closest we come to editing a model is taking the SafeTensors file and deploying it in an environment we choose.

| | AI researchers | Data / ML engineers (us) |
|---|---|---|
| Work on | Building the model itself | Deploying, feeding and managing the model |
| Output | Model weights | Pipelines, endpoints, apps |
| Get the model via | They create it | REST API or SafeTensors file |

---

## After break: Q&A on Glue vs Spark

- **Q: Why list Spark (EMR) and Glue separately as streaming options?** Glue is Spark under the hood, but it's a **distinct service** with things unique to it:
  - **Serverless:** most cloud services that run Spark are *not* serverless, so Glue has a very particular architecture.
  - It *can* run native Spark code (shown last week), but it has its own conventions, the biggest being the **DynamicFrame**: a DataFrame without the rule that every row has the same columns.
  - **Why DynamicFrame exists:** Glue runs on the internet, the internet's main data format is **JSON**, and JSON often doesn't fit a neat DataFrame structure. Handling streaming JSON justified a new data structure that regular Spark doesn't have.
- **Same idea with Redshift vs PostgreSQL:** Redshift is heavily based on Postgres, so the SQL you know mostly works. But Postgres is **OLTP and row-based**; Redshift was redesigned to be **OLAP and columnar**, a huge architectural change. Same SQL flavor, not interchangeable.

| | Base technology | What was changed | Interchangeable? |
|---|---|---|---|
| **Glue** | Spark | Serverless architecture, DynamicFrame for messy JSON | No |
| **Redshift** | PostgreSQL | OLTP → OLAP, row-based → columnar | No |

(The batch version of this EMR vs Glue question, with the three-layer interview answer, is in `Training 20.md`. EMR architecture and Redshift distribution/sort keys are covered in `Training 18.md` and `Training 21.md`.)

---

## Plan for the rest of class

- **Live demo:** a different pipeline on the same Citi Bike data: **stream with Kinesis → land in RDS**, and maybe later also into the Bronze S3 bucket (the data lakehouse endpoint).
- **RDS is temporary:** "RDS is not cheap". If it needs approval from someone higher up at the company, Evan will stop and explain it theoretically instead.
- Then try to get the **Streamlit app working on Fargate**. All the AI pieces (MLflow, etc.) won't fit in today's time.
- **EventBridge restarted:** Evan re-enabled his EventBridge schedule (from now until **Friday at 7**) so the Lambda ingestion keeps running all week. Friday's analytical queries only had data from 4–5 PM Thursday and Friday, which isn't rich enough. By the end of the week there'll be real data to work with.

> For your homework: this is the same reason your Gold aggregates match Silver right now. More snapshots are needed before the grains separate.

---

## Kinesis console tour

The Kinesis console has three services in one UI:

| Service | Evan's summary |
|---|---|
| **Data Streams** | Where we build the substitute for Kafka |
| **Data Firehose** | Something like a Kafka consumer. Can't run Spark streaming code, but for a small pipeline that won't create consumer lag, it can run **pandas** code |
| **Managed Apache Flink** | What you'd use in a **real production** setting |

> Accuracy note: Firehose doesn't run pandas itself. It calls a Lambda function you attach for transformations, and that Lambda can use pandas (see "stream processing options" above).

- **Fraud detection example:** if a bank hired you to build fraud detection, Evan would recommend **Managed Flink over Spark Structured Streaming**, because Flink handles **each message individually**, which is what production fraud detection needs. Spark Structured Streaming works in micro-batches.

---

## Demo: creating the Kinesis data stream

1. Kinesis → **Create data stream**, named `citibike-station-stream`.
2. **Capacity mode:**
   - **On-demand:** pay for what you use; good when you *don't* keep the stream up all the time.
   - **Provisioned:** you set the shard count; good for a stream that's always up.
   - Evan started with on-demand, but the AI guide recommended **provisioned**, so he used that.
3. **Shards** are like **partitions in Kafka**: the stream is split into separate channels, and different consumers can read different shards, under our control.
4. **Per shard:** 1 MB/second and 1,000 records/second of write capacity. That's more than enough here. A big company stream would need more shards, and going very high may require asking AWS for a limit increase.
5. **Shard count** 1, **retention** default 24 hours (1 day), **max record size** 1,024 KB = 1 MB, same as Kafka's default. (1 MiB is the long-standing default; AWS announced in late 2025 that a stream's maximum record size can be raised to 10 MiB. Check the current Kinesis docs before quoting this in an interview.)
6. **Create.** It's active almost immediately because it's serverless.
7. The stream page lists **producers** and **consumers** (empty until something connects).
8. **Verified with the CLI:** first the command returned nothing because of a `--profile` mistake. Retrieving the stream's **ARN** proved it exists: no stream, no ARN.

| Kinesis term | Kafka equivalent |
|---|---|
| Stream | Topic (+ the broker that hosts it) |
| Shard | Partition |
| Retention (default 24 h) | Topic retention |
| Max record 1 MB | Default max message 1 MB |

**Producer and consumer options shown on the stream page** (Evan said to read about these at your leisure; we'll use the SDK because it's easiest; full write-up under *AWS Streaming → producer and consumer options*):

| Option | Side | What it is |
|---|---|---|
| **AWS SDK** (boto3 in Python) | Producer and consumer | Plain API calls like `put_record` / `get_records`. **What we'll use** |
| **Kinesis Producer Library (KPL)** | Producer | Specialized library for high-throughput producers (batching, retries) |
| **Kinesis Agent** | Producer | Standalone app that tails log files on a server and sends them to the stream |
| **Kinesis Client Library (KCL)** | Consumer | Library that handles shard assignment, checkpointing and scaling for consumers |
| **Data Firehose** | Consumer | Managed delivery to S3/Redshift/etc. |
| **Managed Apache Flink** | Consumer | Stream processing app |

---

## Demo: Lambda producer for Kinesis

- The AI guide said to **modify the existing ingestion Lambda** to also send to Kinesis.
- **Decision:** Evan did **not** modify it, because it's running on a schedule all week and editing it could interrupt the ingestion. Instead he **created a separate Lambda** (`lambda-kinesis`, Python 3.14 runtime, author from scratch) just for the Kinesis demo.
- **IAM again** ("Man, I hate authentication"):
  - Confusion: the roles he found while searching for Kinesis were all **Firehose** roles, but this is **Data Streams**. The permission belongs on the **Lambda's execution role**, not on the stream.
  - He added an **inline policy** with Kinesis permissions to the `citibike-lambda-role`.
  - The new Lambda auto-created its own role (he couldn't find the custom execution role option), so he edited **that** role's policy too. Watch for this: the role you added permissions to has to be the one the function actually uses. Same lesson as your 9:50 AM `AccessDenied` this morning.
- **Test:** ran the producer from the CLI and got `StatusCode 200`, executed version `$LATEST`. Green light for the Lambda.

---

## Demo: RDS + IAM for Glue

(RDS/Aurora cluster creation steps not shown. Evan already had the database **cluster identifier** from a command.)

- **Goal:** give the Glue role permission to connect to the RDS (Postgres) database.
- IAM → Roles → `AWSGlueServiceRole-citibike` → Add permissions → **Create inline policy** → JSON.
- Policy includes **`rds-db:connect`** plus Kinesis actions and access to the Citi Bike bucket.
- **Mistake caught:** he forgot to replace the placeholder **`cluster-resource-id`** in the policy with the real ID, fixed it and checked there were no other occurrences.
- **Error:** "Failed to create policy: policy name is required". Named it `rds-kinesis-policy`, and it was created.
- **Next step:** "modify the Spark script to use **IAM authentication**". Evan checked: the Lambda has no Spark code, so "Spark script" meant the **Glue** processing job (see below).

| Term | Meaning |
|---|---|
| **`rds-db:connect`** | IAM action that lets a role log into an RDS database with **IAM authentication** (a short-lived token instead of a stored password) |
| **Cluster resource ID** | RDS's internal ID for the cluster (looks like `cluster-ABC123...`), used in the `rds-db:connect` resource ARN. *Not* the cluster name |
| **IAM database authentication** | Connect to RDS using your IAM role, so no password is stored in code. Same idea as roles vs credentials in your Training 19 explanation |

---

## Demo: Glue streaming job Kinesis → RDS Postgres

- The AI guide wanted to **modify the existing Spark/Glue jobs**. Evan pushed back: *"I'd rather just create a new Glue streaming job and put the data directly into RDS with minimal processing to complete the demo pipeline."* Same instinct as the Lambda: don't touch working jobs, build a separate demo.
- **Job settings:** Glue 5.0, **Spark streaming job**, 2 × G.1X workers, **30-second batch window** (each micro-batch covers 30 s of stream data).
- Created a new table **`station_stream`** in Postgres (2 tables now; `SELECT *` showed the schema and 0 rows).
- Saved the script locally as `citibike_stream_demo.py` in a `citibike-kinesis` folder and **uploaded it to S3 with the CLI** (`.../scripts/glue/`).
- **IAM again:** added an inline policy to the Glue service role with the real cluster ID substituted.
- **Created the Glue job from the CLI** instead of the Visual ETL UI. The command used the existing Glue service role, Glue 5.0, and passed the **Kinesis stream and Aurora connection as job parameters**. "This is going to make it way, way, way easier."
- **Run order:** invoke the producer Lambda (StatusCode 200) → start the Glue job (got a **job run ID**) → check status (`RUNNING`) → tail CloudWatch logs → `SELECT` in Postgres.

> The database is **Aurora PostgreSQL** (an RDS engine), which is why the policy needed a *cluster* resource ID.

---

## Debugging the Glue streaming job: four errors

Evan's summary: *"I really feel like this class has been IAM focused rather than Kinesis and RDS focused... that is almost all of the greatest headaches that you get when you're trying to work with cloud technology."*

Q. How do you debug a failing Glue streaming job?

A. Confirm the producer and stream have data, then read the job's CloudWatch logs for the first real error (often IAM or schema), fix one thing at a time, stop old runs, and restart with a fresh checkpoint.

**Key signal:** in a Glue streaming job's logs, **"retrying micro batch processing"** means a batch is *failing*. A healthy job doesn't retry.

| # | Symptom in logs | Root cause | Fix |
|---|---|---|---|
| 1 | `Failed to connect` / `Connection refused` / `Unable to create executor`, then **`Not authorized`** | **IAM**: Glue couldn't create its S3 folder; the connection error was *caused by* an authorization error | `aws iam put-role-policy` from the CLI adding S3 access (a new inline policy, doesn't overwrite the others). Restarted: `RUNNING`, error message `null` (= good) |
| 2 | `Unresolved column` | The AI-generated script used **automatic JSON schema inference**, "a poor choice for a streaming demo where we already know the record structure" | Defined an explicit schema with `StructType` / `StructField` (`station_schema`) |
| 3 | `list index out of range` on `raw_column = df.columns[0]` | The DataFrame passed to `process_batch` had **zero columns**: the schema was defined but **never passed to the Kinesis reader** | Add `schema=station_schema` to the Glue Kinesis source; add a guard `if not df.columns: print(...); return` |
| 4 | Same error after "fixing" it | **Human copy/paste error** from many manual edits: the file had **two competing parsing implementations** | Asked the AI for a **complete replacement file** based on the current code; deployed it. **Worked** |

**Things worth remembering from the debugging:**

- **Check the producer first.** Evan's instinct was to confirm the Lambda was actually sending data:
  ```bash
  aws kinesis get-records --shard-iterator "$SHARD_ITERATOR" --limit 1 \
    --query 'Records[0].Data' --output text | base64 --decode
  ```
  That returned a valid JSON record, which proved the producer and stream were fine and the problem was on the **Glue side**.
- **Decode Base64 when reading from the CLI or Lambda.** Kinesis stores the raw bytes the producer sent. Base64 appears only because the **API/CLI JSON response** (and the Lambda event payload) encodes the binary `Data` blob for transport, so you decode it to read the JSON.
- **Trust your instincts over the AI.** Evan had noticed earlier that the schema wasn't referenced in the stream, but went ahead because it wasn't in the AI's instructions. That was bug #3. *"You very often do have to trust your instincts over what the AI says."*
- **Stop the old run before starting a new one**, or you'll read logs from the wrong run. At one point there were 3 failed runs plus 1 running.
- **Use a fresh checkpoint location** after changing a streaming job's schema/logic. The checkpoint remembers the old state.
- **Verify the upload:** compare the local file's **SHA** with the S3 object's (both started `7f81…` and ended `…72b03`) to prove S3 has the version you edited.

**Evan's tip for AI-assisted debugging:** when you've applied AI edits **manually** many times and errors keep coming, paste your *current* file back and ask for **a complete replacement file** rather than more edits. Your manual edits and the AI's intent may have drifted: a line not deleted, a line added twice. In the old days you'd comb through the script by hand, which doesn't work in a live demo. He doesn't recommend it for production code, and AI is "always a crapshoot", but it usually irons out human errors fast.

---

## Result: data flowing Kinesis → Glue → Postgres

`SELECT COUNT(*) FROM station_stream;` returned **2,519 rows**, the same station count as your Gold tables, i.e. one full snapshot.

```
Lambda (producer, boto3 put_record)
   │  Citi Bike station data (raw JSON bytes; Base64 only in API responses)
   ▼
Kinesis Data Stream (citibike-station-stream, 1 shard)
   │
   ▼
Glue 5.0 streaming job (Spark Structured Streaming, 30 s micro-batches)
   │  decode → apply station_schema → minimal processing
   ▼
Aurora PostgreSQL (RDS) table station_stream
```

- The script lives in S3; Glue runs it.
- The producer only ingests every couple of minutes, so the row count grows in steps.
- Evan: this would take **under an hour with on-prem Kafka + Postgres**, but *"it's the cloud: there are complications, there are permissions issues, and there are things that go wrong."*

---

## Student Q&A

- **"I don't think I have Glue access" (a student):** the **group** already grants Glue. The real error was that the **IAM role** (`citibike-lambda-role`) lacked permission to be assumed by Glue. Evan sent AI-generated policy instructions to apply the same way he applied policies all class. After the break the student confirmed it was resolved by using an approved role.
- **Glue job succeeds but Redshift table stays empty (Silver → Redshift):** Evan suggested tailing logs while the job runs:
  ```bash
  aws logs tail /aws-glue/jobs/output --follow
  ```
  **`tail` only shows *new* logs as they're written**, so start it *before* you run the job. It won't show anything for a job that already finished. (For a finished job, use `aws logs tail ... --since 1h` instead.)
- **Will we need more permissions for future homework?** **No new group permissions needed.** Everyone already has full access to **Glue, Kinesis and RDS** at the group level. If you hit a permissions error, it's the **policy on your IAM role**. You can't create IAM users, but you **can edit your roles' permission policies**. "It might feel like a game of whack-a-mole... but eventually it's going to work."

| Error says… | Look at | You can fix it? |
|---|---|---|
| *You* (`user/...`) not authorized | Group permissions | No: ask Evan |
| `assumed-role/<role>/...` not authorized | That role's policies (inline policy) | **Yes** |

---

## Cleanup: shut down what costs money

Evan asked AI for a final audit of what to stop overnight.

| Service | Shut down? | Why |
|---|---|---|
| **Glue streaming job** | **Yes: stop it** | A streaming job runs (and bills per DPU-hour) until you stop it |
| **Redshift Serverless** | Watch it | Bills for compute while running queries |
| **EMR / EC2** | Yes if any | Bill while running (none created today) |
| **Kinesis, S3, Lambda, EventBridge** | Generally no | Low or pay-per-use |

Steps: close the log tail → list the job runs → copy the run ID of the one that's `RUNNING` → stop it (`aws glue batch-stop-job-run --job-name <job> --job-run-ids <run-id>`).

> Also worth noting: a **provisioned** Kinesis stream bills per shard-hour and an **RDS/Aurora** instance bills per hour while running. Evan said RDS "is not cheap" earlier, so those are worth checking in your own account if you build this.

**Homework:** Evan gave "a basic homework assignment for how to implement this side of things" after cleanup. See `homework/assignment/Homework - Training 22 (Assignment).md`.
