---
title: "Training 12 Homework"
description: "Homework assignment for Training 12: Streaming Data."
sidebar:
  order: 12
---

:::note
The assignment prompt as given in class. Related notes: [Training 12](/training-notes-site/notes/training-12/).
:::

I'd make this a small coding extension plus architecture/concepts reading, rather than turning the homework into another environment-setup exercise. The coding task should prove they understand the producer → Kafka → Spark flow they just built.

## Homework: Kafka and Spark Structured Streaming

### Part 1 — Extend the Streaming Application

You now have a working streaming pipeline:

REST API → Python Producer → Kafka → Spark Structured Streaming → Console

Your assignment is to make a small modification to the existing application without changing its overall architecture.

#### Task

Modify the producer so that every Kafka message contains a third field called `joke_length`.

The producer currently sends messages like:

```json
{
  "joke": "Chuck Norris can divide by zero.",
  "time": 1790628000
}
```

Change it so that it sends:

```json
{
  "joke": "Chuck Norris can divide by zero.",
  "time": 1790628000,
  "joke_length": 32
}
```

`joke_length` should be calculated from the length of the joke returned by the API. Do not hard-code it.

Then modify the Spark consumer so that it:

- Reads the new field from Kafka.
- Adds `joke_length` to the Spark schema.
- Displays all three fields.
- Only displays jokes whose `joke_length` is greater than 100 characters.

The final output should therefore contain:

```
joke | time | joke_length
```

but jokes of 100 characters or fewer should not appear.

#### Requirements

You should not need to change the Kafka container or create a different topic.

Start Kafka with:

```bash
docker run -d \
  --name kafka \
  -p 9092:9092 \
  apache/kafka:4.3.1
```

Run the Spark application using:

```bash
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1 \
  consumer.py
```

Submit your modified `producer.py` and `consumer.py`.

### Part 2 — Kafka Concepts

You do not need to implement these concepts for this homework, but you should understand what they mean and be prepared to discuss them.

#### 1. Serialization and Deserialization

Kafka ultimately transports bytes.

Our Python producer starts with a Python dictionary:

```python
message = {
    "joke": res["value"],
    "time": ts
}
```

The serializer:

```python
value_serializer=lambda v: json.dumps(v).encode("utf-8")
```

performs roughly:

```
Python dictionary
       ↓
JSON string
       ↓
UTF-8 bytes
       ↓
Kafka
```

The Spark consumer reverses the process:

```
Kafka bytes
       ↓
CAST(value AS STRING)
       ↓
JSON string
       ↓
from_json()
       ↓
Spark columns
```

Production Kafka applications may use JSON, Avro, Protobuf or other serialization formats.

Avro and Protobuf are particularly common when organizations want strongly controlled schemas and compatibility between producers and consumers.

A related production concept is a Schema Registry, which provides centralized management of message schemas and schema versions.

#### 2. Topics and Partitions

A Kafka topic is divided into one or more partitions.

For example:

```
vehicle-telemetry

Partition 0: A → D → G → J
Partition 1: B → E → H → K
Partition 2: C → F → I → L
```

Partitions are important because they provide Kafka with a major mechanism for parallelism and scalability.

Instead of one broker and one consumer processing every message sequentially, different partitions can be distributed across brokers and consumers.

Kafka guarantees ordering within a partition, not across an entire multi-partition topic.

#### 3. Message Keys and Partitioning

A producer can assign a key to a Kafka record.

For example:

```
key = vehicle_123
value = engine telemetry
```

Kafka can use the key to determine the partition.

This allows messages with the same key to consistently reach the same partition.

For example:

```
Partition 0:
vehicle_123 → vehicle_123 → vehicle_123

Partition 1:
vehicle_456 → vehicle_456 → vehicle_456
```

This is useful when ordering matters for an individual entity.

Examples include:

- vehicle ID
- customer ID
- account ID
- device ID
- order ID
- movie/video ID

You should understand why randomly distributing all records is sometimes undesirable.

#### 4. Brokers and Kafka Clusters

A broker is a Kafka server.

The Docker container used in class gives us a single Kafka broker:

```
Computer
   │
   └── Docker
         │
         └── Kafka Broker
                │
                └── test-topic
```

A production cluster normally contains multiple brokers:

```
                 Kafka Cluster

       Broker 1      Broker 2      Broker 3
          │             │             │
       P0 leader     P1 leader     P2 leader
       P1 replica    P2 replica    P0 replica
```

Partitions can therefore be distributed and replicated across machines.

#### 5. Replication

Production Kafka clusters generally should not have only one copy of important data.

Suppose:

```
Topic: factory-sensors
Partition: 0
Replication factor: 3
```

Kafka could store it as:

```
Broker 1: Partition 0 — LEADER
Broker 2: Partition 0 — FOLLOWER
Broker 3: Partition 0 — FOLLOWER
```

The replicas provide fault tolerance.

If a broker fails, Kafka can continue operating using another replica, subject to the cluster's configuration and replica state.

#### 6. Leaders and Followers

For each partition, one replica acts as the leader.

Clients interact with the appropriate partition leader for reads/writes, while follower replicas keep copies of the partition.

Conceptually:

```
Producer
    │
    ▼
Broker 1
P0 LEADER
    │
    ├──────────► Broker 2
    │             P0 FOLLOWER
    │
    └──────────► Broker 3
                  P0 FOLLOWER
```

If Broker 1 fails, Kafka can elect an eligible replica as the new leader.

This is called leader election.

#### 7. Consumer Groups

Production systems often need more than one consumer process.

Consumers can belong to a consumer group.

Kafka distributes partitions among consumers within that group.

For example:

```
Topic
P0 ─────────► Consumer A
P1 ─────────► Consumer B
P2 ─────────► Consumer C

           Consumer Group
```

Within one consumer group, a partition is assigned to one consumer at a time.

This allows applications to scale horizontally.

A second consumer group can independently consume the same topic.

For example:

```
                 factory-sensors
                 /             \
                /               \
       Consumer Group A      Consumer Group B
       Spark Analytics       Alert Service
```

Both applications receive the data independently.

#### 8. Offsets

Every record within a Kafka partition has an offset.

Conceptually:

```
Partition 0

Offset 0 → message A
Offset 1 → message B
Offset 2 → message C
Offset 3 → message D
```

Offsets allow consumers to track their position.

This is one reason Kafka is different from simply sending a network message from application A directly to application B.

The data remains in Kafka according to the topic's retention configuration, and consumers can process or potentially replay records.

Spark Structured Streaming also maintains information about its streaming progress through checkpointing.

#### 9. Retention

Kafka is not merely a temporary message relay.

Topics have retention policies determining how long records are retained or how much storage they may consume.

For example, a company might retain raw telemetry for several days even though its streaming application normally processes each event within seconds.

This allows scenarios such as:

```
Kafka retains events
       ↓
Spark application fails
       ↓
Application restarted
       ↓
Processing continues/replays as appropriate
```

#### 10. ZooKeeper vs. KRaft

Older Kafka architectures depended on Apache ZooKeeper.

ZooKeeper was a separate distributed coordination system used by Kafka for important cluster metadata and coordination responsibilities.

Conceptually:

```
        ZooKeeper Cluster
              │
              │ coordination/metadata
              ▼
         Kafka Cluster
      /       |        \
 Broker 1  Broker 2  Broker 3
```

This meant Kafka administrators effectively had two distributed systems to operate.

Modern Kafka uses KRaft — Kafka Raft metadata mode.

Kafka now manages cluster metadata through Kafka's own controller quorum rather than requiring an external ZooKeeper cluster.

Conceptually:

```
        KRaft Controllers
          /     |     \
        C1      C2     C3
               │
               ▼
          Kafka Brokers
        /      |       \
       B1      B2       B3
```

KRaft uses a consensus protocol based on Raft principles so the controllers can maintain an agreed-upon view of cluster metadata.

The Kafka 4.x generation is KRaft-based; ZooKeeper mode is no longer part of the Kafka 4.x architecture.

You should understand:

ZooKeeper architecture

- Kafka + separate ZooKeeper system

versus:

KRaft architecture

- Kafka manages its own metadata quorum

#### 11. Rebalancing

Suppose a consumer group has:

```
3 partitions
3 consumers
```

Kafka might assign:

```
P0 → Consumer A
P1 → Consumer B
P2 → Consumer C
```

If Consumer B dies, Kafka needs to redistribute the work:

```
P0 → Consumer A
P1 → Consumer A
P2 → Consumer C
```

This process is called a rebalance.

Rebalances are necessary for fault tolerance and scaling, but excessive rebalancing can disrupt processing and hurt performance.

#### 12. Delivery Semantics

Streaming engineers should recognize these terms:

**At-most-once**

A message is processed zero or one times. Losing a message is possible, but duplicate processing is avoided.

**At-least-once**

Messages should not be lost, but processing a message more than once is possible.

**Exactly-once**

The system attempts to ensure that the effect of processing each event occurs exactly once.

Exactly-once processing is considerably more complicated than simply saying, "Kafka doesn't send duplicate messages." It involves the interaction between producers, Kafka, consumers, offsets, transactions, and downstream systems.

#### 13. Backpressure and Consumer Lag

Imagine Kafka receives:

```
100,000 events/sec
```

but consumers can process only:

```
70,000 events/sec
```

Kafka continues receiving records while the consumers fall behind.

The difference between the latest available offsets and the consumer's processed position is generally described as consumer lag.

Growing lag is one of the most important operational signals in a production Kafka environment.

A Kafka engineer should immediately ask:

- Is incoming traffic unusually high?
- Are consumers slow?
- Do we have enough partitions?
- Do we need additional consumers?
- Is downstream processing slow?
- Is there a network or storage bottleneck?

### Production Example 1 — Automobile Factory IoT

Imagine an automobile manufacturer with factories in Michigan, Mexico and Germany.

Each factory contains thousands of machines.

Sensors monitor:

- temperature
- vibration
- pressure
- voltage
- motor RPM
- robot position
- error codes

A sensor might generate:

```json
{
  "machine_id": "robot-187",
  "factory": "mexico-02",
  "temperature": 81.7,
  "vibration": 4.2,
  "timestamp": "2026-09-28T20:30:00Z"
}
```

#### Physical architecture

```
MEXICO FACTORY FLOOR
─────────────────────────────────

Robot/Sensor
     │
     ▼
Industrial Gateway / Edge Computer
     │
     │ factory network
     ▼
Local ingestion service
     │
     │ secure WAN/cloud connection
     ▼

CLOUD / DATA CENTER
─────────────────────────────────

Kafka Cluster
     │
     ├── machine-telemetry
     ├── robot-events
     └── factory-alerts
              │
              ▼
       Streaming Processing
       Spark / Flink / similar
          /           \
         /             \
        ▼               ▼
 Alerting System     Data Lake
        │               │
        ▼               ▼
Factory operators   Historical analytics
```

#### Why have edge infrastructure?

A robot cannot necessarily depend on a cloud data center thousands of kilometers away for millisecond-level safety decisions.

Immediate machine control may therefore occur locally:

```
Sensor → PLC/edge controller → immediate action
```

while telemetry is simultaneously sent upstream:

```
Sensor
   ↓
Gateway
   ↓
Kafka
   ↓
Streaming analytics
   ↓
Long-term storage
```

Kafka might partition telemetry using:

```
machine_id
```

as the key.

That keeps events for an individual machine ordered within its partition.

Spark could then perform operations such as:

- filter abnormal temperatures
- calculate rolling averages
- detect unusual vibration
- aggregate production statistics
- enrich machine IDs with equipment metadata

An alerting consumer might need events immediately.

A data-lake consumer might persist everything for later analytics and machine-learning workloads.

The same Kafka topics can therefore support several independent consumers.

### Production Example 2 — Global Video Streaming Service

Now imagine a service similar to Netflix.

This problem is geographically very different.

Users are distributed around the world:

- New York
- São Paulo
- London
- Mumbai
- Tokyo
- Sydney

A user presses Play.

The actual video does not normally travel through Kafka.

Video content is delivered through geographically distributed content-delivery infrastructure.

Kafka instead transports events about what is happening.

For example:

```json
{
  "user_id": "98217",
  "video_id": "movie-551",
  "event": "play",
  "device": "smart_tv",
  "country": "BR",
  "timestamp": "2026-09-28T20:30:00Z"
}
```

A few seconds later:

```json
{
  "user_id": "98217",
  "video_id": "movie-551",
  "event": "buffering",
  "duration_ms": 1800
}
```

#### Physical/geographic architecture

```
USER IN BRAZIL
────────────────────────

Smart TV / Phone
       │
       ├──────────────► Nearby CDN
       │                 │
       │                 └── VIDEO DATA
       │
       └──────────────► Application/API infrastructure
                              │
                              └── EVENT DATA
                                     │
                                     ▼

REGIONAL/CLOUD INFRASTRUCTURE
────────────────────────────────

Event ingestion
      │
      ▼
Kafka
      │
      ├── playback-events
      ├── search-events
      ├── device-events
      └── quality-events
              │
              ▼
       Stream Processing
        /      |       \
       /       |        \
      ▼        ▼         ▼
Monitoring  Analytics  Recommendations
      │        │         │
      ▼        ▼         ▼
 Alerts    Data Lake   Feature Store/
                      ML Systems
```

A global company may operate Kafka and ingestion infrastructure in multiple geographic regions rather than sending every event directly across the planet to one Kafka cluster.

For example:

```
North America ──► US regional ingestion
Europe        ──► EU regional ingestion
South America ──► Brazil/South America ingestion
Asia          ──► Asian regional ingestion
```

Regional data can then be aggregated or replicated according to the organization's architecture and regulatory requirements.

#### Different consumers want different things

An operations system might consume:

```
quality-events
```

to detect:

```
Buffering suddenly increased 300% in Brazil
```

A recommendation system might consume:

```
play
pause
finish
search
thumbs-up
```

events to update user-interest signals.

A business analytics pipeline might aggregate:

- plays per title
- hours watched
- active users
- device distribution
- regional viewing patterns

and write the results into a warehouse.

A security pipeline might independently examine authentication and device events.

Kafka therefore acts as a central event backbone:

```
                    Kafka
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Operations   Analytics      ML
          │           │           │
       seconds      minutes    seconds/minutes
```

The producer does not need to know how all these systems work.

It simply publishes a well-defined event.

### What You Should Know After This Exercise

You should be able to explain the following architecture without looking at the code:

```
Producer
   │
   │ serialize
   ▼
Kafka Topic
   │
   ├── Partition 0 ── Leader + replicas
   ├── Partition 1 ── Leader + replicas
   └── Partition 2 ── Leader + replicas
             │
             │ offsets
             ▼
       Consumer Group
             │
             ▼
      Spark Streaming
             │
       deserialize
             │
             ▼
        Transformations
             │
             ▼
           Sink
```

You should also be able to explain:

1. Why Kafka uses partitions.
2. What determines which partition receives a record.
3. Why message keys matter.
4. What serialization and deserialization mean.
5. Why production clusters replicate partitions.
6. What partition leaders and followers do.
7. What happens when a leader fails.
8. What consumer groups accomplish.
9. What an offset represents.
10. Why consumer lag matters.
11. What happens during a consumer-group rebalance.
12. Why Kafka retains messages after they have been consumed.
13. The difference between at-most-once, at-least-once and exactly-once processing.
14. Why Kafka moved from ZooKeeper to KRaft.
15. Where Kafka fits into a larger real-time data architecture.

---

Instructor note: I deliberately kept the coding portion small. Adding a field forces them to touch serialization on the producer, schema/deserialization on Spark, and a Spark transformation, so it tests whether they understand the pipeline without making the homework mostly debugging.
