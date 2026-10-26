---
title: Day 12 Vocabulary
description: Glossary of terms and definitions from the Training 12 notes.
sidebar:
  order: 12
---

Vocabulary — Study Guide Day 12

Source: notes/Training 12.md

## Streaming Concepts
- **Streaming data** — Data that moves continuously in near-real time from producers to consumers, as opposed to a scheduled batch job.
- **Batch processing** — Processing data in scheduled chunks, such as a nightly job.
- **Publish-subscribe (pub/sub)** — The pattern practically all streaming platforms use: producers publish without knowing the listeners and consumers subscribe without knowing the sources.
- **Decoupling** — Producers and consumers never talk directly, so systems can be added, removed or slowed independently.
- **Fan-out** — Several downstream systems receiving the same data feed.
- **Point-to-point integration** — Systems calling each other directly, which does not scale past a few systems.
- **Sink** — The final output destination where processed data is written.
- **Serialization** — Encoding records into a format such as binary or Avro for storage or transfer.
- **Deserialization** — Decoding serialized records back into usable data with the right schema.

## Apache Kafka
- **Apache Kafka** — A distributed publish-subscribe event streaming platform with three major parts: producer, broker and consumer.
- **Producer** — The application you write that takes data from its source and ingests it into the streaming pipeline.
- **Broker** — The pre-built application running on the cluster that you configure and manage, which stores records and serves them to consumers.
- **Consumer** — The application you write that gets data from the broker, processes it and puts it into the final output sink.
- **Kafka cluster** — A group of brokers that together store a topic's partitions.
- **Topic** — A single data stream for a single use case, created on and stored by the broker.
- **Partition** — A subdivision of a topic, an ordered append-only log spread across brokers for parallelism.
- **Offset** — The sequential position of a record within a partition, tracked by consumers so they can resume.
- **Consumer group** — Consumers that split a topic's partitions between them, each partition read by one member at a time.
- **Append-only log** — A storage structure where records are only added to the end, never modified.
- **Retention period** — How long records stay on the broker; Kafka's default is 7 days (`log.retention.hours=168`), while Kinesis defaults to 24 hours.
- **Replay** — Re-reading records that are still retained, possible because reading does not delete them.
- **Broker storage is not a database** — Data is kept only temporarily and serialized, purely so a failed consumer can catch up later.
- **kafka-python** — Python library for writing Kafka producers and consumers.
- **Zookeeper** — Kafka's separate coordination service in older versions, tracking brokers, partition leadership and topic config.
- **zookeeper-server-start.sh** — Script that starts Zookeeper in older Kafka versions.
- **kafka-server-start.sh** — Script that starts the Kafka broker.
- **KRaft mode** — Kafka 3.3+ mode where Kafka manages its own metadata without Zookeeper.
- **kafka-console-producer.sh** — Built-in CLI that publishes each typed line as a record to a topic.
- **kafka-console-consumer.sh** — Built-in CLI that prints records as they arrive on a topic.
- **--bootstrap-server** — The broker host:port a client connects to first to discover the cluster, e.g. `localhost:9092`.
- **Port 9092** — Kafka broker's default port.

## Cloud and Other Streaming Platforms
- **AWS MSK (Managed Streaming for Apache Kafka)** — Basically just Kafka on AWS, with AWS managing provisioning, patching and scaling.
- **Managed service** — A cloud service where the provider runs the infrastructure, trading control for less operational work.
- **AWS Kinesis** — AWS's native streaming service, similar to Kafka but not the same, using its own API.
- **Shard** — Kinesis's unit of parallelism, equivalent to a Kafka partition.
- **On-Demand mode** — Kinesis capacity mode that scales shards automatically.
- **Azure Event Hubs** — Azure's native streaming service, similar to Kafka but not the same, with a Kafka-compatible endpoint.
- **Kafka-compatible endpoint** — An interface letting existing Kafka clients connect to a non-Kafka service with only a connection change.
- **Google Cloud Pub/Sub** — GCP's native messaging and streaming service, built around topics and subscriptions; similar, not the same.
- **Subscription (Pub/Sub)** — A durable, independent view onto a topic, closer to a queue per consumer.
- **AWS SQS (Simple Queue Service)** — A simple queue-shaped streaming framework not designed for high volume; messages are deleted once processed.
- **Queue** — A structure where each message is delivered to one consumer and removed after acknowledgment, with no replay.
- **Acknowledgment (ack)** — A consumer confirming a message was processed so it can be removed.
- **RabbitMQ** — Open-source message broker the teacher recommends for small-scale streaming.
- **AMQP (Advanced Message Queuing Protocol)** — The messaging protocol RabbitMQ is traditionally built around.
- **Exchange** — RabbitMQ component that routes messages to queues by type: direct, topic, fanout or headers.
- **MQTT** — Lightweight publish-subscribe protocol, the streaming framework for IoT devices.
- **IoT (Internet of Things)** — Networked sensors and embedded devices.
- **QoS levels (Quality of Service)** — MQTT delivery guarantees: 0 at most once, 1 at least once, 2 exactly once.
- **Retained message** — MQTT feature keeping a topic's last message for subscribers who connect later.
- **Last will and testament** — MQTT message the broker publishes when a device disconnects unexpectedly.

## Stream Processing Frameworks
- **Stream processing framework** — A system that reads a stream, transforms or aggregates it and writes results as data arrives.
- **Spark Structured Streaming** — Spark's streaming engine, described by the teacher as micro-batch DataFrames.
- **Micro-batch** — A small discrete chunk of streaming data processed as an ordinary DataFrame.
- **spark.readStream** — Builds a streaming DataFrame from a continuously arriving source such as a Kafka topic.
- **writeStream** — Continuously writes each micro-batch's results to a sink.
- **Apache Flink** — Open-source stream processing framework.
- **AWS Glue Streaming** — AWS Glue's streaming ETL capability.
- **Google Cloud Dataflow** — GCP's managed stream and batch processing service.

## HTTP Fundamentals
- **HTTP (Hypertext Transfer Protocol)** — The request-response protocol used by the web and APIs.
- **GET** — HTTP method to retrieve data.
- **POST** — HTTP method to create new data.
- **PUT** — HTTP method to update or replace existing data.
- **DELETE** — HTTP method to remove data.
