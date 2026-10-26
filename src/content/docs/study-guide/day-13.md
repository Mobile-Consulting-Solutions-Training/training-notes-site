---
title: Study Guide - Day 13
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 13: Open Table Formats and NoSQL"
sidebar:
  order: 130
---

Study Guide - Day 13 (source: notes/Training 13.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Kafka's Message Size Limit.** A single Kafka message is limited to **1 MB** by default (`message.max.bytes`). Kafka is for many small events; bulk structured data moves as files in object storage or table formats.

**OTF and Schema-Driven Formats.** **Delta** and **Iceberg** = open table formats, structured like SQL tables or DataFrames. **Avro** = semi-structured, like JSON. **Protobuf** = "its own thing entirely" (Google's binary format with `.proto` schemas).

**NoSQL Types.** Document: MongoDB, AWS DocumentDB. Column family: DynamoDB, HBase, Cassandra. Graph: Neo4j, AWS Neptune. **GSI** = Global Secondary Index in DynamoDB.

**Class Pipeline.** Open-Meteo API → `producer.py` → Kafka topic `weather` (key = city, 3 partitions) → `consumer.py` (Spark Structured Streaming, 5-second micro-batches, parse JSON, °C → °F, keep key/partition/offset) → MongoDB `streaming_demo.weather` → Streamlit dashboard refreshing every 2 seconds.

**Message Keys.** Kafka hashes the key to pick a partition, so the same key always lands in the same partition, and order is only guaranteed within a partition. The key is for Kafka (partitioning, log compaction); the value is the data. No key = spread with no per-entity order. **Log compaction** keeps only the latest value per key. Choosing a key is an architecture decision: what must be processed together or in order? Watch for **hot partitions** from uneven keys.

**Spark Structured Streaming vs Flink.** Spark is micro-batch: with `trigger(processingTime="5 seconds")` events arrive in bursts and share a batch time. Flink processes one record at a time with very low latency and strong stateful/event-time features. Pick by the latency requirement, not "Flink fast, Spark slow." In Docker, Flink reaches host Kafka at `host.docker.internal:9092`.

**MongoDB as a Sink.** `docker run -d --name mongodb -p 27017:27017 mongo:8.0.4`; database and collection are created on first write. `foreachBatch(fn)` hands each micro-batch to a function as a normal DataFrame, written with the MongoDB connector, with a `checkpointLocation`. Spark needs **two connectors** via `--packages` (Kafka and MongoDB). A running server doesn't mean Spark has the connector. Spark processes; MongoDB serves; the dashboard reads MongoDB only.

**Querying and Indexing MongoDB.** `use db`, `show collections`, `find()`, `countDocuments()`, `sort({processed_at: -1}).limit(10)`, projections. Indexes: single field `{processed_at: -1}`, compound `{city: 1, processed_at: -1}`, text. `explain("executionStats")`: `COLLSCAN` (reads everything) vs `IXSCAN` (uses an index). Index for query patterns; every index slows streaming writes.

**Streamlit.** Python web dashboards. Run with `streamlit run dashboard.py` (plain `python` causes "missing ScriptRunContext" warnings), opens on port 8501. `@st.fragment(run_every="2s")` auto-refreshes. Query → DataFrame → `st.metric`, charts, `st.dataframe`.

**Troubleshooting Lessons.** `Failed to find data source: kafka/mongodb` = missing connector. `NoSuchMethodError ... wrapRefArray` = Scala version mismatch (`_2.12` vs `_2.13`). Connection refused = port not published (`-p 9092:9092`). `No readable meta.properties` = format KRaft storage. "Address already in use" = find the owner with `lsof`/`ss`. MongoDB fails on kernel 6.19+, so pin an older image. Connector version matches Spark, not the broker. Provide connectors in one place. Pin image versions. `advertised.listeners` must be resolvable by the client. Test one layer at a time.

**Kafka Concepts Reading.** Serialization (Kafka moves bytes; Avro/Protobuf with a Schema Registry in production). Partitions = unit of parallelism. Replication across brokers; each partition has a **leader** and **followers**; **leader election** on failure. Consumer groups, offsets (Spark uses checkpoints), retention. Kafka 4.x is KRaft-only. **Rebalancing** when consumers join/leave. Delivery: at-most-once, at-least-once, exactly-once. **Consumer lag** = latest offset minus consumer position; growing lag is a warning.

**Production Examples.** Car factory: sensors → edge gateway (local safety decisions) → Kafka (key = machine_id) → Spark/Flink → alerts and data lake. Netflix: video bytes go over CDNs; Kafka carries events about viewing to operations, recommendations, analytics and security.

---

# Part 2: Cheat Sheet

## Formats and Limits
- Kafka message max 1 MB · Delta/Iceberg = table formats · Avro ≈ JSON · Protobuf = own thing

## NoSQL
- Document (MongoDB, DocumentDB) · Column family (DynamoDB, HBase, Cassandra) · Graph (Neo4j, Neptune) · GSI

## Keys
- Same key → same partition → ordered · key for Kafka, value for app · compaction keeps latest per key
- Pick by "what must stay in order" · avoid hot partitions

## Spark vs Flink
- Micro-batch bursts vs record-at-a-time · choose by latency need

## Spark → MongoDB
- `foreachBatch(fn)` + `checkpointLocation` · two `--packages` connectors
- Spark processes, MongoDB serves, dashboard reads MongoDB

## MongoDB
- `find`, `countDocuments`, `sort`, `limit`, projection
- `createIndex` single / compound / text · `COLLSCAN` vs `IXSCAN` · indexes cost writes

## Streamlit
- `streamlit run app.py` · port 8501 · `@st.fragment(run_every="2s")`

## Troubleshooting
- Missing data source → connector · `_2.12` vs `_2.13` → Scala mismatch
- Refused → publish port · port in use → `lsof -i :port`
- Connector matches Spark version · pin images · `advertised.listeners` · test layer by layer

## Kafka Concepts
- Replication · leader/followers · leader election · rebalancing
- At-most / at-least / exactly-once · consumer lag

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What is Kafka's default message size limit and what does it imply?
A: One megabyte per message. Kafka is built for many small events, so large datasets move as files in object storage or table formats rather than through Kafka.

Q: What are the three types of NoSQL database from class, with examples?
A: Document databases like MongoDB and DocumentDB, column family databases like DynamoDB, HBase and Cassandra, and graph databases like Neo4j and Neptune.

Q: What does a Kafka message key do?
A: Kafka hashes it to choose the partition, so all records with the same key go to the same partition and stay in order. The value is the actual data.

Q: How do you choose a good message key?
A: Ask which events must be processed together or in order, like device ID for IoT or account ID for banking, and make sure the key's values are spread evenly so one partition doesn't get overloaded.

Q: What is log compaction?
A: A topic setting that keeps only the latest value for each key, useful for current-state data like the latest status of each customer.

Q: How is Flink different from Spark Structured Streaming?
A: Spark processes the stream in micro-batches, so events arrive in bursts. Flink processes each record as it arrives, giving lower latency and richer stateful processing. Which is better depends on the latency requirement.

Q: What does foreachBatch do?
A: It gives you each micro-batch as a normal DataFrame inside a function, so you can write it with any batch writer, like the MongoDB connector.

Q: MongoDB is running but Spark says it can't find the data source mongodb. Why?
A: The MongoDB Spark connector isn't loaded. The server running doesn't mean Spark knows how to talk to it; you add the connector with --packages.

Q: What's the difference between the processing layer and the serving layer?
A: Spark processes the stream, and MongoDB serves the results. The dashboard reads from MongoDB, never directly from Kafka or Spark.

Q: What do COLLSCAN and IXSCAN mean in a MongoDB explain?
A: COLLSCAN means MongoDB read every document because no index helped. IXSCAN means it used an index.

Q: How should you decide which MongoDB indexes to create?
A: Follow the query patterns, like an index on processed_at descending for "latest 100 events". Don't index everything, because every index slows down the constant streaming inserts.

Q: Why did the Streamlit dashboard print ScriptRunContext warnings?
A: It was started with python instead of streamlit run. Streamlit apps have to be launched with streamlit run.

Q: What causes NoSuchMethodError wrapRefArray with the Kafka connector?
A: A Scala version mismatch, like a connector built for Scala 2.12 on a Spark built with Scala 2.13. The connector's Scala and Spark versions must match Spark.

Q: Should the Spark Kafka connector version match the Kafka broker?
A: No, it matches the Spark version. A new Kafka broker works with the connector for your Spark version.

Q: What are advertised listeners?
A: The address Kafka tells clients to use after they first connect. If it advertises a Docker-internal name, apps on the host can't resolve it, so for host apps it should be localhost:9092.

Q: What are leaders and followers in Kafka?
A: Each partition has one leader broker that handles reads and writes and follower brokers that keep copies. If the leader dies, a follower is elected leader.

Q: Explain the three delivery semantics.
A: At-most-once may lose messages but never duplicates. At-least-once never loses but may duplicate. Exactly-once means the effect happens once, which requires coordinating producers, offsets and sinks.

Q: What is consumer lag and why watch it?
A: The difference between the latest offset and where the consumer is. Growing lag means the consumer can't keep up, from more traffic, a slow consumer or a slow sink.

Q: In a Netflix-style system, does the video go through Kafka?
A: No. Video bytes go through CDNs. Kafka carries events about viewing, like play, pause and buffering, to many independent consumers.
