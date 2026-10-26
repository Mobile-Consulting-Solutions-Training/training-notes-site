---
title: Study Guide - Day 12
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 12: Streaming Data"
sidebar:
  order: 120
---

Study Guide - Day 12 (source: notes/Training 12.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Apache Kafka.** A distributed publish-subscribe event streaming platform. Producers write records to **topics**; topics split into **partitions** (ordered, append-only logs, each record with an **offset**) spread across **brokers**. Consumers in a **consumer group** share the partitions (one consumer per partition per group); separate groups each read the whole topic. Records stay after being read, so they can be replayed. Use it when data must move continuously, fan out to many systems, or decouple fast producers from slow consumers.

**Publish-Subscribe.** Producers publish without knowing who listens; consumers subscribe without knowing who produced. The broker sits between them. Almost every streaming platform uses this pattern.

**Kafka's Three Parts.** **Producer** (you write it): takes data from the source into the pipeline. **Broker** (pre-built, you configure it): runs on the cluster and stores/serves records. **Consumer** (you write it): reads from the broker, processes, writes to the final sink, tracking its own offset.

**The Broker Is Not a Database.** It stores data only so a failed or slow consumer can catch up later, and the data is stored serialized, so you can't query it like a table. Retention: Evan said 24 hours, but **Kafka's default is 7 days** (`log.retention.hours=168`, change per topic with `retention.ms`); **24 hours is Kinesis's default**.

**Topic.** A single data stream for a single use case, created on and stored by the broker.

**Running Kafka Locally.** `pip install kafka-python` for Python producers/consumers. Older Kafka: start ZooKeeper first (`zookeeper-server-start.sh`), then the broker (`kafka-server-start.sh`). Kafka 3.3+ can use **KRaft** instead of ZooKeeper. Test with `kafka-console-producer.sh` / `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test-topic`.

**Other Streaming Platforms.**
- **AWS MSK**: Kafka on AWS, managed; existing Kafka clients work unchanged.
- **AWS Kinesis**: AWS's own service, similar but not Kafka. **Shards** instead of partitions, AWS SDK API, 24-hour default retention (up to 365 days), On-Demand scaling.
- **Azure Event Hubs**: Azure's own service with partitions and a **Kafka-compatible endpoint**.
- **Google Pub/Sub**: topics and **subscriptions** (closer to a queue per consumer), auto-scaling, ordering and replay are add-ons.
- **AWS SQS**: simple queue; messages are deleted once processed, no replay, not for high volume.
- **RabbitMQ**: open-source broker (AMQP) for small-scale streaming; exchanges route messages to queues.
- **MQTT**: lightweight pub/sub protocol for IoT, hierarchical topics, QoS 0/1/2, retained messages and last will.

**Stream Processing Frameworks.** Transport tools move data; processing frameworks transform it as it arrives. **Spark Structured Streaming** = "micro-batch DataFrames": the stream is processed as small batches, each an ordinary DataFrame, so the batch API works unchanged. `spark.readStream` / `spark.writeStream`. Also listed: Apache Flink, AWS Glue Streaming, Google Cloud Dataflow.

**HTTP Methods.** GET retrieve, POST create, PUT update/replace, DELETE remove.

---

# Part 2: Cheat Sheet

## Kafka Model
- Producer → topic (partitions on brokers) → consumer group
- Partition = ordered log + offsets · one consumer per partition per group · groups independent
- Records persist → replay

## Three Parts
- Producer (you) · Broker (pre-built) · Consumer (you)

## Broker Storage
- Failure buffer, not a database · serialized
- Kafka default retention **7 days** · Kinesis **24 hours**

## Commands
- `pip install kafka-python`
- ZooKeeper then broker (old) · KRaft (3.3+)
- `kafka-console-producer.sh` / `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic t`

## Platform Comparison
- MSK = managed Kafka · Kinesis = shards, AWS API · Event Hubs = Kafka endpoint
- Pub/Sub = subscriptions · SQS = simple queue · RabbitMQ = small scale, AMQP · MQTT = IoT, QoS

## Processing
- Spark Structured Streaming = micro-batch DataFrames · `readStream` / `writeStream`
- Flink · Glue Streaming · Dataflow

## HTTP
- GET · POST · PUT · DELETE

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What is Kafka?
A: A distributed publish-subscribe streaming platform. Producers write records to topics, topics are split into partitions across brokers, and consumers read them at their own pace. Records aren't deleted when read, so they can be replayed.

Q: Why put Kafka between systems instead of connecting them directly?
A: Direct connections don't scale and a slow consumer can back up the producer. Kafka is a durable buffer in the middle, so systems can be added independently and a consumer that's down just resumes where it left off.

Q: What are Kafka's three main parts and who writes each?
A: The producer, which you write, brings data into the pipeline. The broker is pre-built software you only configure, and it stores and serves the data. The consumer, which you also write, reads from the broker, processes the data and writes it to the sink.

Q: What is the publish-subscribe pattern?
A: Producers publish messages without knowing who's listening, and consumers subscribe without knowing who produced them. The broker in the middle decouples them.

Q: Is the Kafka broker a database?
A: No. It only keeps data so a consumer that fails or falls behind can catch up, and the data is stored serialized, so you can't query it like a table.

Q: What's Kafka's default retention period?
A: Seven days, from log.retention.hours set to 168. It can be changed per topic. Twenty-four hours is the default for Kinesis.

Q: What is a topic?
A: A single data stream for a single use case, like order events. Topics are created on and stored by the brokers.

Q: How do consumer groups work?
A: Consumers in the same group split a topic's partitions, with each partition read by only one consumer in that group. A different group gets its own full copy of the stream.

Q: What did ZooKeeper do, and what replaced it?
A: ZooKeeper tracked brokers, partition leaders and config, so it had to start before the broker. Newer Kafka uses KRaft mode, where Kafka manages its own metadata.

Q: What's the difference between MSK and Kinesis?
A: MSK is actual Kafka managed by AWS, so Kafka clients work unchanged. Kinesis is AWS's own service with shards and its own API, so Kafka code has to be rewritten for it.

Q: What makes Event Hubs different from Kinesis for Kafka users?
A: Event Hubs has a Kafka-compatible endpoint, so existing Kafka clients can often connect just by changing the connection string.

Q: How is SQS different from Kafka?
A: SQS is a simple queue. Once a message is processed and deleted it's gone, so there's no replay or multiple consumer groups, and it isn't built for high volume.

Q: When would you use RabbitMQ or MQTT?
A: RabbitMQ for small-scale messaging with flexible routing. MQTT for IoT devices, because it's very lightweight and works on unreliable networks.

Q: What does "micro-batch DataFrames" mean for Spark Structured Streaming?
A: Spark processes the stream as a series of small batches, and each batch is a normal DataFrame, so the same DataFrame code you use for batch jobs works on streams.

Q: What's the difference between a streaming platform and a stream processing framework?
A: A platform like Kafka moves the data. A processing framework like Spark Structured Streaming or Flink reads the stream, transforms it, and writes the results out.

Q: Name the four standard HTTP methods.
A: GET retrieves data, POST creates it, PUT updates or replaces it, and DELETE removes it.
