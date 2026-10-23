---
title: "Training 12 - Streaming Data"
description: "Message brokers and streaming services (Kafka, MSK, Kinesis, Event Hubs, Pub/Sub, SQS, RabbitMQ, MQTT) and stream processing frameworks (Spark Structured Streaming, Flink, Glue Streaming, Dataflow)."
sidebar:
  order: 12
---

Teacher: Evan Flint

Syllabus Day 13 (per file numbering) - topic: Streaming Data.

# Streaming Data

## Apache Kafka

**Definition and purpose:**

| | |
|---|---|
| **What** | A distributed, publish-subscribe event streaming platform. Producers write records to named **topics**; topics are split into **partitions** for parallelism; consumers (in **consumer groups**) read those records, independently and at their own pace. Records aren't deleted on read - they persist for a configurable retention period, so multiple consumers can replay the same data. |
| **When** | Whenever data needs to move continuously, in near-real-time, from one or more producers to one or more consumers - as opposed to a nightly batch job. Common triggers: an app needs to react to events as they happen (fraud detection, monitoring/alerting), multiple downstream systems need the same data feed (fan-out) without each hitting the source system directly, or a pipeline needs to decouple fast producers from slower consumers. |
| **Why** | Point-to-point integrations (System A calls System B directly) don't scale past a handful of systems - every new consumer means another direct connection, and a slow/down consumer can back up the producer. Kafka sits in the middle as a durable, replayable buffer: producers and consumers never talk to each other directly, systems can be added/removed independently, and a consumer that's down or slow just resumes later from where it left off instead of losing data or blocking the producer. |
| **How** | A Kafka **cluster** is made of **brokers** (servers that store the data). Producers publish records to a **topic**; each topic is divided into **partitions**, spread across brokers for scalability, each partition an ordered, append-only log. Records within a partition keep a strict order and are assigned an offset; consumers track their own offset per partition so they can resume exactly where they left off. Consumers in the same **consumer group** split the partitions between them (each partition read by only one consumer in the group at a time), while separate consumer groups can each independently read the whole topic. |

**Publish-subscribe pattern**

Teacher's definition: "Kafka, and practically ALL other streaming platforms, operate on the publish-subscribe algorithm."

Expanded: producers **publish** records without needing to know who (if anyone) is listening; consumers **subscribe** to a topic to receive records without needing to know who produced them. Neither side talks to the other directly - the broker is the intermediary - which is the same decoupling property described in the "Why" row above, and it's the shared pattern across virtually every platform covered today (Kafka, MSK, Kinesis, Event Hubs, Pub/Sub, RabbitMQ, MQTT), not just Kafka specifically.

**Kafka's 3 major parts** (teacher's definition): "Kafka has 3 major parts to it: Producer, Broker, Consumer."

Teacher's definitions of each:

- **Producer** - "the application which you write as a developer, which takes the data from its source and ingests it into the streaming pipeline."
- **Broker** - "the application running on the cluster - you DO NOT write the broker, it's already written - you just manage it and configure it."
- **Consumer** - "the application which gets data from the broker, processes it, and puts it into the final output sink." "We as developers write the consumer as well."

| Part | Who writes it | Role |
|---|---|---|
| **Producer** | You (the developer) | Takes data from its source and ingests it into the streaming pipeline. |
| **Broker** | Nobody - pre-built, you configure/manage it | Runs on the cluster; stores records and serves them to consumers. A cluster is made of multiple brokers, each holding a subset of each topic's partitions. |
| **Consumer** | You (the developer) | Gets data from the broker, processes it, and writes it into the final output sink. Tracks its own offset so it can resume where it left off. |

**The broker's storage is NOT a database**

Teacher's definition: "One of the functions of the broker is to store data that's being streamed - HOWEVER it is ABSOLUTELY NOT A DATABASE." "Data on the broker is ONLY SAVED in case there is a failure on the consumer side, so that the data that can't be consumed right now can be stored and then consumed later." "The default amount of time that data is stored on the broker is 24 hours." "The reason that you can't fetch the data being stored on a Kafka cluster is because that data is serialized."

Expanded: the broker's storage exists purely as a durability/failure-recovery buffer between producer and consumer - not a general-purpose place to query or persist data long-term. Two concrete reasons it can't be used like a database:

- **Retention is temporary by default** - data sits on the broker for 24 hours by default, not indefinitely, specifically so a consumer that's down or behind can catch up.
- **The data is serialized** - records are stored in their serialized (encoded, e.g. binary/Avro/etc.) form, not as directly queryable rows/columns, so you can't just "fetch" or query it the way you would a database table - a consumer has to deserialize it using the appropriate schema/format to make sense of it.

**Topic**

Teacher's definition: "A topic is a single data stream for a single use case." "Topics are created on the broker, and that's where they're located."

Expanded: A topic is the named channel a producer publishes to and a consumer subscribes to - scoped to one specific use case/data stream (e.g. a topic for order events, a separate topic for click events), rather than one topic carrying every kind of data. Topics live on the broker - creating a topic is a broker-side operation, and the broker is what physically stores the topic's data (split across its partitions).

**Hands-on: `kafka-python`**

```bash
pip install kafka-python
```

The Python library used to write Kafka producers/consumers (the two applications developers actually write, per the Producer/Broker/Consumer breakdown above).

**Hands-on: starting Kafka locally (older versions)**

```bash
./bin/zookeeper-server-start.sh ./config/zookeeper.properties
```
^ the command to start a Zookeeper server in older versions of Kafka.

```bash
./bin/kafka-server-start.sh ./config/server.properties
```
^ the command to start the Kafka broker in older versions.

Expanded: Zookeeper was Kafka's separate coordination service in older versions - tracking which brokers are alive, partition leadership, and topic config - which is why it has to be started first, as its own process, before the broker (the broker registers with Zookeeper on startup). Newer Kafka versions (3.3+) replace this with **KRaft mode**, where Kafka manages its own metadata internally and no separate Zookeeper process is needed.

**Hands-on: console producer/consumer**

```bash
./bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic test-topic
```
^ the command to start the console producer, assuming a locally running broker and a topic called `test-topic`.

```bash
./bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test-topic
```
^ same for the console consumer.

Expanded: these are Kafka's own built-in CLI tools - no code required - for manually testing a topic. The producer reads lines typed into the terminal and publishes each one as a record; the consumer prints out records as they arrive on the topic. `--bootstrap-server` is the broker's host:port the client connects to first, to discover the rest of the cluster.

---

## AWS MSK (Managed Streaming for Apache Kafka)

Teacher's definition: "AWS MSK (Managed Streaming for Apache Kafka) - basically just Kafka on AWS."

Expanded: MSK is AWS's managed offering for running Apache Kafka - it's the same Kafka (same producers/consumers/topics/partitions/brokers model above, same client APIs), but AWS handles provisioning, patching, broker replacement, and scaling the underlying cluster instead of self-hosting Kafka on your own EC2 instances/servers. The tradeoff is the standard managed-service one: less operational overhead (no manually standing up ZooKeeper/brokers, applying security patches, or handling broker failures yourself) in exchange for less low-level control and AWS-specific cost/configuration constraints.

---

## AWS Kinesis

Teacher's definition: "AWS Kinesis - similar to Kafka, but not the same."

Expanded: Kinesis is AWS's own, natively-built streaming service - not Kafka under the hood, unlike MSK. It plays the same basic role (durable, ordered, replayable stream of records that producers write to and consumers read from), but with its own terminology and a different underlying model:

| | Kafka (and MSK) | Kinesis |
|---|---|---|
| Unit of parallelism | Partition | Shard |
| Client protocol | Kafka's own binary protocol | AWS SDK / REST API |
| Retention | Configurable, commonly days-weeks (or indefinite), independent of throughput | Default 24 hours, extendable (up to 365 days), historically tied more directly to shard count/throughput |
| Scaling | Add partitions/brokers (self-hosted) or resize the MSK cluster | Add/split shards, or use On-Demand mode for automatic scaling |
| Ecosystem | Broad, open-source, portable across clouds/on-prem | AWS-native, integrates tightly with other AWS services (Lambda, Firehose, etc.) |

Because Kinesis isn't Kafka, existing Kafka producer/consumer code doesn't just work against it as-is - it needs to be written against the Kinesis API (or adapted via a compatibility layer), whereas MSK is a drop-in target for existing Kafka clients.

---

## Azure Event Hubs

Teacher's definition: "Azure Event Hubs - similar to Kafka, but not the same."

Expanded: Microsoft's equivalent to Kinesis - a natively-built Azure streaming service, not Kafka itself, that plays the same role (durable, ordered, replayable event stream). Its unit of parallelism is the **partition** (same term as Kafka, though the underlying implementation is Azure's own), and it's tightly integrated with the rest of the Azure ecosystem (Azure Functions, Stream Analytics, etc.), the same way Kinesis is tightly coupled to the AWS ecosystem. Notably, Event Hubs also ships a **Kafka-compatible endpoint** - existing Kafka producer/consumer clients can often point at Event Hubs with just a connection-string change, without rewriting to a separate native API - which is a meaningfully different compatibility story than Kinesis's fully separate API.

---

## Google Cloud Pub/Sub

Teacher's definition: "Google Cloud Pub/Sub - similar, not the same."

Expanded: GCP's native messaging/streaming service - again, not Kafka under the hood. The bigger conceptual difference from Kafka/Kinesis/Event Hubs: Pub/Sub is push-and-pull messaging built around **topics and subscriptions** rather than partition-ordered logs as the primary mental model - a **subscription** is a durable, independent "view" onto a topic (closer to a queue per consumer than a shared partitioned log), and ordering/replay have historically been secondary features layered on top (ordering keys, seek-to-timestamp) rather than the core primitive the way partition offsets are in Kafka. It scales automatically without the user managing partition/shard counts directly, which trades some of Kafka's fine-grained parallelism control for operational simplicity.

---

## AWS SQS (Simple Queue Service)

Teacher's definition: "AWS SQS - Simple Queue Service." / "SQS is technically a streaming framework, but it's simple, and it's not designed for high volume."

Expanded: Unlike Kinesis/Event Hubs/Pub/Sub, SQS is queue-shaped rather than log-shaped - a message is delivered to a consumer, and once processed and explicitly deleted (acknowledged), it's gone, so there's no replay and no multiple independent consumer groups each reading the same full history the way Kafka's partitioned log supports. But per the teacher, that doesn't put it in a different category from streaming - it's still a streaming framework, just a simple one, and specifically not built for high-throughput/high-volume workloads the way Kafka/Kinesis/Event Hubs/Pub/Sub are. It fits point-to-point work-distribution (a pool of workers pulling tasks off a shared queue) at modest volume, rather than high-volume fan-out.

---

## RabbitMQ

Teacher's definition: "RabbitMQ - the streaming framework that you should use for small-scale streaming."

Expanded: An open-source message broker (not tied to any one cloud provider, unlike SQS/Kinesis/Event Hubs/Pub/Sub), traditionally built around the **AMQP** protocol. Like SQS, it's queue-shaped rather than a partitioned replayable log - messages get routed through **exchanges** to **queues** and are acknowledged/removed once consumed - but RabbitMQ adds more flexible routing logic than SQS (direct, topic, fanout, and header exchange types controlling exactly which queue(s) a message lands in). Per the teacher's framing, it sits in the same "simple, small-scale" tier as SQS rather than the high-volume tier occupied by Kafka/Kinesis/Event Hubs/Pub/Sub.

---

## MQTT

Teacher's definition: "MQTT - the streaming framework for IoT devices."

Expanded: A lightweight publish-subscribe messaging protocol purpose-built for constrained devices and unreliable/low-bandwidth networks - the defining use case being IoT (sensors, embedded devices) rather than server-to-server data pipelines. Clients publish to and subscribe against **topics** (organized hierarchically, e.g. `home/livingroom/temperature`) through a central **broker**. Its design priorities reflect the IoT use case specifically: a very small protocol/message overhead (important for low-power/low-bandwidth devices), configurable delivery guarantees via **QoS levels** (0 = at most once, 1 = at least once, 2 = exactly once), and a **retained message**/**last will and testament** mechanism so a device's most recent state (or its disconnect notification) is available even to subscribers that connect later.

---

# Streaming Processing Frameworks

The systems above (Kafka, MSK, Kinesis, Event Hubs, Pub/Sub, SQS, RabbitMQ, MQTT) move/transport streaming data. The frameworks below actually process it - reading from a stream, running transformations/aggregations, and writing results out - as data arrives, rather than in a scheduled batch job.

## Spark Structured Streaming

Teacher's definition: "Micro-batch DataFrames."

Expanded: Spark Structured Streaming doesn't process records one at a time as they arrive - it processes the stream as a series of small, discrete **micro-batches**, each one loaded into a regular Spark **DataFrame**. That's why the same DataFrame API/transformations already used for batch Spark jobs (filter, join, groupBy, etc.) work unchanged against a stream - each micro-batch is just an ordinary DataFrame under the hood, run through the same query, repeatedly, as new data keeps arriving.

**Core API:** `spark.readStream` / `spark.writeStream`

Expanded: the streaming counterparts to the ordinary `spark.read`/`.write` batch API - `readStream` builds a streaming DataFrame from a continuously-arriving source (e.g. a Kafka topic) instead of a one-time static read, and `writeStream` continuously writes each micro-batch's results out to a sink, instead of writing once and stopping.

## Apache Flink

## AWS Glue Streaming

## Google Cloud Dataflow

---

# HTTP Fundamentals

**Standard HTTP request types:**

| Method | Purpose |
|---|---|
| **GET** | Retrieve data. |
| **POST** | Create new data. |
| **PUT** | Update/replace existing data. |
| **DELETE** | Remove data. |

