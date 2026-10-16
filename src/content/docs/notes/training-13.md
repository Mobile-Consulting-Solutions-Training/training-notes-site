---
title: "Training 13 - Open Table Formats and NoSQL"
description: "Kafka limitations, Delta, Iceberg, Avro and Protobuf, NoSQL database types, and the Kafka to Spark to MongoDB class walkthrough."
---

Teacher: Evan Flint

Syllabus Day 14 (per file numbering) - topic: Open Table Formats (OTF) and schema-driven data formats.

# OTF and Schema-Driven Formats

Teacher's definition: "OTF and schema-driven formats:"

## Kafka Limitations

Teacher's definition: "Kafka limitations - message size limitation, maximum size of a message is 1MB."

Expanded: this is a size ceiling on a single Kafka record (the default `message.max.bytes`/`max.request.size` configuration), not on a topic's overall volume - Kafka happily handles unlimited total throughput/retention, but any one message has to fit under that 1MB default. This is worth having in mind as a motivation for today's OTF/schema-driven formats topic: Kafka (see `Training 12.md`) is built for a continuous stream of many small events, not for shipping large structured datasets whole - a single Parquet/Delta/Iceberg file, or even one Avro/Protobuf-encoded batch, can easily exceed 1MB, so bulk structured data generally moves via files in an object store (or a table format like Delta/Iceberg sitting on top of one) rather than being crammed through Kafka message-by-message.

## Delta

## Iceberg

Teacher's definition: "Similar to SQL tables or DataFrames - they are structured data formats" (applies to both Delta and Iceberg).

## Avro

Teacher's definition: "Similar to JSON format - it's a semistructured format."

## Protobuf

Teacher's definition: "It's own thing entirely."

---

# NoSQL Databases

## Types of NoSQL Database

Teacher's definition: "Types of NoSQL Database:"

| Type | Examples |
|---|---|
| Document | MongoDB, AWS DocumentDB |
| Column Family | DynamoDB, HBase, Cassandra |
| Graph | Neo4J, AWS Neptune |

Teacher's note: "AWS DocumentDB is also a Document type database."

## GSI (Global Secondary Index)

Teacher's definition: "GSI - Global Secondary Index (in DynamoDB)."

---

# Class Walkthrough: Teacher's ChatGPT Session (Sep 28–29)

Source: the ChatGPT conversation Evan worked through live in class ("Fix Spark Kafka Dependency", shared link). These notes summarize what came out of it. It is ChatGPT's explanation that the teacher used and presented, **not** the teacher's own verbatim definitions. The session ran across two days:
- **Sep 28 (end of Training 12):** getting Kafka 4.3.1 plus Spark working, and designing the Kafka homework and reading.
- **Sep 29 (this class):** message keys, Spark vs. Flink, MongoDB as a sink, MongoDB indexing, a Streamlit dashboard, and switching the demo to real weather data.

The end-of-class pipeline:

```text
Open-Meteo API ─► producer.py ─► Kafka (topic "weather", key = city)
                                        │
                                        ▼
                      consumer.py (Spark Structured Streaming, 5-sec micro-batches)
                                        │  parse JSON, °C → °F, keep key/partition/offset
                                        ▼
                         MongoDB (streaming_demo.weather)
                                        │
                                        ▼
                         dashboard.py (Streamlit, refresh every 2s)
```

---

## Kafka Message Keys

Expanded: a **message key** is an optional value attached to each Kafka record alongside the **value** (the payload). Kafka's producer hashes the key to pick a partition, so **every record with the same key goes to the same partition**. Kafka only guarantees order **within a partition**, so the key is how you get ordering for one entity (one vehicle, one customer, one city).

```text
"vehicle_123" ─► hash ─► Partition 2     (every time, while the partition count doesn't change)

P0: vehicle_827 → vehicle_827
P1: vehicle_456 → vehicle_456 → vehicle_992      ← different keys can share a partition
P2: vehicle_123 → vehicle_123 → vehicle_123      ← same key always lands together, in order
```

| | Key | Value |
|---|---|---|
| **Used by** | Kafka itself: partition choice, log compaction | Consumers: the application data |
| **Example** | `robot_827` | `{"machine_id": "robot_827", "temperature": 89.4}` |

- The same ID appearing in both the key and the value is normal; they serve different purposes.
- **No key** (`producer.send('test-topic', message)`) means records are spread across partitions with no per-entity ordering.
- **Log compaction:** a compacted topic keeps only the **latest value per key**, which is useful for "current state" topics (latest customer status, latest device configuration).
- **Choosing a key is an architecture decision.** Ask: *which events need to be processed together or in order?* For example `device_id` for IoT, `order_id` for orders, `account_id` for banking, `user_id` or `video_id` for streaming video, depending on the use case.
- **Hot partitions:** if one key produces a huge share of traffic, its partition gets overloaded even if the topic has 50 partitions. Consider how evenly the key's values are spread (**cardinality and distribution**), not just "pick the ID."

Sending a key in Python (`kafka-python`):

```python
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    key_serializer=lambda k: k.encode("utf-8"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)
producer.send("weather", key=city, value=message)
```

Keeping the key, partition and offset in Spark instead of discarding them:

```python
df.selectExpr("CAST(key AS STRING) AS kafka_key", "CAST(value AS STRING) AS value",
              "partition AS kafka_partition", "offset AS kafka_offset")
```

---

## Spark Structured Streaming vs. Flink

Expanded: Spark Structured Streaming is **micro-batch by default**: it collects the events that arrived during a time window and processes them together. Flink is a **record-at-a-time** engine: each event flows through the operators without waiting for a batch boundary. Flink is not literally instant (networking, buffering and serialization still add latency); it just never waits for a batch.

| | Spark Structured Streaming | Flink |
|---|---|---|
| Execution model | Micro-batches (streaming DataFrame abstraction on top) | Continuous, one record at a time |
| Visible behavior with `trigger(processingTime="5 seconds")` | Nothing, then about 20 events at once, then nothing… | Events appear one by one as they arrive |
| `processed_at` timestamps | Many events share the same batch time | Each event gets its own time, just after its event time |
| Strengths | Unified batch + streaming, huge ecosystem, fine for most data-engineering latency needs | Very low latency, advanced stateful processing, event time, timers |

The trigger that makes micro-batching visible:

```python
query = processed_df.writeStream.format("console").outputMode("append") \
    .trigger(processingTime="5 seconds").start()
```

**The lesson is not "Flink = fast, Spark = slow."** "Streaming" covers several latency models: batch (hours or days), micro-batch (seconds to sub-second) and record-at-a-time (very low latency). Choose based on the requirement. Daily production totals can wait a few seconds; a "machine overheating" alert may not be able to.

Planned Flink demo (not run in class, because time ran out): run Flink in Docker (a `jobmanager` plus a `taskmanager` via Docker Compose, web UI on port **8081**). Use **Flink SQL** to define the Kafka topic as a table (`'connector' = 'kafka'`, `'format' = 'json'`) and run a continuous `SELECT`. Inside a container, `localhost` means *the container itself*, so Flink reaches the host's Kafka at `host.docker.internal:9092` (on Linux this needs `extra_hosts: host.docker.internal:host-gateway`).

---

## MongoDB as the Spark Sink

Start MongoDB in Docker:

```bash
docker run -d --name mongodb -p 27017:27017 mongo:8.0.4
docker exec -it mongodb mongosh        # open the Mongo shell inside the container
```

The database and collection don't need to be created first; MongoDB creates them on the first write.

**`foreachBatch()`:** Spark hands each micro-batch to a Python function as a normal DataFrame, which is then written with the MongoDB connector. This makes the micro-batches visible ("Writing batch 0 to MongoDB", "Writing batch 1…"), and in `mongosh`, `countDocuments()` jumps in chunks every 5 seconds.

```python
def write_to_mongodb(batch_df, batch_id):
    print(f"Writing batch {batch_id} to MongoDB")
    batch_df.write.format("mongodb").mode("append") \
        .option("spark.mongodb.write.connection.uri", "mongodb://localhost:27017/") \
        .option("spark.mongodb.write.database", "streaming_demo") \
        .option("spark.mongodb.write.collection", "weather") \
        .save()

query = processed_df.writeStream.foreachBatch(write_to_mongodb) \
    .outputMode("append").trigger(processingTime="5 seconds") \
    .option("checkpointLocation", "/tmp/weather-mongodb-checkpoint").start()
```

**Spark now needs two connectors**, one per external system:

```bash
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1,org.mongodb.spark:mongo-spark-connector_2.13:10.5.0 \
  consumer.py
```

| Piece | What it is | Where it runs |
|---|---|---|
| Kafka server / MongoDB server | The actual services | Docker containers |
| `spark-sql-kafka-0-10` / `mongo-spark-connector` | **Spark connectors**: JAR libraries that teach Spark how to talk to each service | Downloaded into Spark by `--packages` |

A running server does not mean Spark can reach it. `Failed to find data source: mongodb` means the **connector** is missing, not the server.

**Processing layer vs. serving layer:** Spark *processes* the stream and MongoDB *serves* the results. The dashboard reads MongoDB, never Kafka or Spark directly; reading Kafka straight from the dashboard would bypass the processing layer.

---

## Querying MongoDB (mongosh)

```javascript
use streaming_demo
show collections
db.weather.find().pretty()
db.weather.countDocuments()
db.weather.find().sort({ processed_at: -1 }).limit(10)                               // newest 10
db.weather.find({}, { _id: 0, city: 1, temperature: 1, processed_at: 1 }).limit(10)  // projection: chosen fields only
```

---

## MongoDB Indexing

| Command | Purpose |
|---|---|
| `db.weather.getIndexes()` | List indexes. Every collection starts with the automatic `_id` index |
| `db.weather.createIndex({ processed_at: -1 })` | Single-field index, descending. Supports "latest N events" |
| `db.weather.createIndex({ city: 1, processed_at: -1 })` | **Compound index**. Supports "latest readings for one city" (filter + sort) |
| `db.jokes.createIndex({ joke: "text" })` | **Text index**, then search with `db.jokes.find({ $text: { $search: "computer" } })` |
| `.explain("executionStats")` | Shows how MongoDB ran the query |

Reading `explain()`:
- **`COLLSCAN`**: collection scan, where MongoDB reads every document (no usable index).
- **`IXSCAN`**: index scan, where MongoDB uses an index.
- Demo: run a query, `explain` it and see `COLLSCAN`; create the index, `explain` the same query and see `IXSCAN`.

Rules:
- **Indexes should follow query patterns**; don't index every field. The dashboard's constant "latest 100 events" query is exactly what `{ processed_at: -1 }` supports.
- **Indexes cost writes.** Every insert from the continuous Spark stream has to update the collection **and every index**, so extra indexes slow ingestion and use storage.

---

## Real-Time Dashboard with Streamlit

- Streamlit builds a web dashboard in pure Python (`pip install streamlit pymongo pandas`).
- **Run it with `streamlit run dashboard.py`**, not `python dashboard.py`. The flood of `missing ScriptRunContext! ... bare mode` warnings in class came from running it with plain `python`. It opens at `http://localhost:8501`.
- Auto-refresh: decorate the live section with `@st.fragment(run_every="2s")` so it re-queries MongoDB every 2 seconds. This is cleaner than an infinite `while True` + `time.sleep()` loop.
- Pattern: query MongoDB → `pd.DataFrame(records)` → `st.metric` tiles, `st.line_chart` / `st.bar_chart`, `st.dataframe` for a table of recent events.
- The first demo used Chuck Norris jokes (metrics: total events, average and longest joke length). Jokes make poor dashboard data, which led to switching to real weather data.

---

## Final Class Pipeline: Real Weather Data

**Producer:** polls Open-Meteo (free, no API key) every 15 seconds for 5 cities (Rio de Janeiro, New York, London, Tokyo, Sydney) and sends to topic `weather` with **key = city**. Fields: `city, latitude, longitude, temperature, feels_like, humidity, precipitation, cloud_cover, pressure, wind_speed, wind_direction, event_time`. Open-Meteo's "current" values come from 15-minute model data, so polling faster than every 10–15 seconds adds nothing.

**Consumer:** an explicit `StructType` schema (`DoubleType` for measurements, `IntegerType` for humidity, cloud cover and wind direction, `StringType` for city and time). It keeps `kafka_key / kafka_partition / kafka_offset` and adds `processed_at = current_timestamp()`. The transformation is `temperature_f = round(temperature * 9 / 5 + 32, 1)`. Output goes to `streaming_demo.weather` using `foreachBatch` and a 5-second trigger.

Creating the topic with 3 partitions, so the partition and offset data is more interesting:

```bash
bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic weather --partitions 3
```

**Dashboard:** metrics (Kafka events, cities, average temperature, average humidity), a current-weather table, temperature over time by city (`pivot_table` → `st.line_chart`), current humidity and wind speed bar charts, and a "Kafka Stream" table with key, partition and offset.

Keeping `partition` and `offset` all the way into MongoDB means the dashboard demonstrates **Kafka itself**, not just weather.

---

## Troubleshooting Log (errors hit live in class)

| Error | Cause | Fix |
|---|---|---|
| `Failed to find data source: kafka` | Spark-Kafka connector JAR not on Spark's classpath | `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_<scala>:<spark> consumer.py` |
| `NoSuchMethodError: scala.Predef$.wrapRefArray` | Connector built for the **wrong Scala version** (`_2.12` connector on a Scala 2.13 Spark) | Match both: `spark-sql-kafka-0-10_2.13:3.5.1` for Spark 3.5.1 / Scala 2.13. Check with `spark-submit --version` |
| `nc -vz localhost 9092` → Connection refused, although the broker log says it's listening | Port only open **inside** the container, not published to the host | Recreate the container with `-p 9092:9092`; check with `docker ps` / `docker port kafka` |
| `No readable meta.properties files found` | Kafka 4.x built from source (KRaft) with **unformatted storage** | `kafka-storage.sh random-uuid` → `kafka-storage.sh format --standalone -t <id> -c config/server.properties` (see `Training 14.md`) |
| `Socket server failed to bind to 0.0.0.0:9092: Address already in use` | The Docker Kafka container already held port 9092 | `docker stop kafka`; confirm the port is free with `sudo lsof -i :9092` |
| `bind: address already in use` on 27017 | Something already held MongoDB's port | Find the owner: `sudo ss -ltnp \| grep :27017` or `sudo lsof -nP -iTCP:27017 -sTCP:LISTEN`, then `ps -fp <PID>` |
| `MongoDB cannot start: Linux kernel versions 6.19 and newer has a known incompatibility` | Recent MongoDB builds refuse to run on kernel 6.19+ (SERVER-121912) | Pin an older image: class used `mongo:8.0.4`; the homework machine used `mongo:7.0` |
| `Conflict. The container name "/mongodb" is already in use` | The failed container still exists (stopped) | `docker rm mongodb`, then `docker run` again. `docker ps` only lists running containers; use `docker ps -a` |
| `[DATA_SOURCE_NOT_FOUND] Failed to find the data source: mongodb` | MongoDB **Spark connector** missing, even though MongoDB was running | Add `org.mongodb.spark:mongo-spark-connector_2.13:10.5.0` to `--packages` |
| `missing ScriptRunContext! ... bare mode` | Streamlit app started with `python` | `streamlit run dashboard.py` |

Other points from the troubleshooting:
- **The Spark connector version matches Spark, not the Kafka broker.** A Kafka 4.3.1 broker works fine with the Spark 3.5.1 connector; Spark supports brokers 0.10+.
- Provide the connector in **one** place: either `spark-submit --packages` or `.config("spark.jars.packages", ...)` in code, not both, or you can load two different versions.
- **Pin image versions** (`mongo:8.0.4`, `apache/kafka:4.3.1`) instead of `:latest`, so everyone's environment is reproducible and doesn't silently change.
- **Advertised listeners:** a client first connects to the bootstrap server, and Kafka then tells it which address to use (`advertised.listeners`). For apps on the host, advertise `PLAINTEXT://localhost:9092`. If Kafka advertises a Docker-internal name, the host can't resolve it.
- **Test the chain one layer at a time:** `nc -vz localhost 9092` → console producer to console consumer (`docker exec -it kafka /opt/kafka/bin/kafka-console-producer.sh ...`) → Python producer → Spark consumer. In a huge stack trace, look for the one meaningful line (for example `Address already in use`); the shutdown messages after it are normal cleanup.

---

## Kafka Concepts Reading (from the Sep 28 homework design)

The reading Evan had ChatGPT write alongside the "add `joke_length`" homework (see `homework/submission/alex_jackson_kafka_streaming_homework/`):

| Concept | Key idea |
|---|---|
| **Serialization** | Kafka only moves **bytes**. Producer: dict → JSON string → UTF-8 bytes. Consumer: bytes → `CAST(value AS STRING)` → `from_json()` → columns. Production systems often use Avro or Protobuf with a **Schema Registry** |
| **Partitions** | The unit of parallelism and scalability; ordering is guaranteed only **within** a partition |
| **Brokers and clusters** | A broker is one Kafka server; production clusters have several, and partitions are spread across them |
| **Replication** | Each partition is copied to several brokers (for example replication factor 3) for fault tolerance |
| **Leaders and followers** | Each partition has one **leader** that handles reads and writes; **followers** keep copies |
| **Leader election** | If a leader's broker dies, Kafka promotes an eligible follower to be the new leader |
| **Consumer groups** | Within a group, each partition goes to one consumer at a time (horizontal scaling); separate groups each read the whole topic independently |
| **Offsets** | A record's position in its partition; consumers track offsets to resume or replay. Spark tracks its progress with **checkpoints** |
| **Retention** | Kafka keeps records for a configured time or size even after they're read, so a crashed app can restart and catch up |
| **ZooKeeper vs. KRaft** | Old Kafka needed a separate ZooKeeper cluster for metadata (two systems to run). **KRaft** = Kafka manages its own metadata with a Raft-based controller quorum. Kafka 4.x is KRaft-only |
| **Rebalancing** | When consumers join or leave a group, partitions are reassigned; necessary, but frequent rebalances disrupt processing |
| **Delivery semantics** | **At-most-once** (may lose, no duplicates), **at-least-once** (no loss, possible duplicates), **exactly-once** (the effect happens once; needs coordination of producers, offsets, transactions and sinks) |
| **Consumer lag** | Latest offset minus the consumer's position. Growing lag is a key operational warning: check traffic, consumer speed, partition count, downstream slowness |

**Production example: car factory IoT.** Sensors (temperature, vibration, RPM…) → edge gateway on the factory floor (safety decisions stay local, in milliseconds) → secure WAN → Kafka in the cloud or data center (topics `machine-telemetry`, `robot-events`, `factory-alerts`, key = `machine_id`) → Spark or Flink → an alerting system for operators **and** a data lake for historical analytics and ML. Several independent consumers read the same topics.

**Production example: Netflix-style video.** Video bytes travel over nearby **CDNs**, *not* Kafka. Kafka carries **events about** viewing (play, pause, buffering, search), ingested **per region** (US, EU, South America, Asia). Consumers include operations (buffering spike alerts, in seconds), recommendations/ML (user-interest signals), business analytics (hours watched, plays per title → warehouse) and security. Kafka is the central event backbone, and producers don't need to know who consumes the events.
