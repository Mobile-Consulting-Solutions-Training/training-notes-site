---
title: Day 13 Vocabulary
description: Glossary of terms and definitions from the Training 13 notes.
sidebar:
  order: 13
---

Vocabulary — Study Guide Day 13

Source: notes/Training 13.md

## OTF and Schema-Driven Formats
- **OTF (Open Table Format)** — A table layer such as Delta or Iceberg that adds table structure on top of data files in an object store.
- **Schema-driven format** — A data format whose records follow a defined schema, such as Avro or Protobuf.
- **Kafka message size limit** — Kafka's default maximum size of a single message is 1MB, so bulk structured data moves as files instead.
- **message.max.bytes / max.request.size** — Kafka broker and producer settings controlling the maximum message size.
- **Delta (Delta Lake)** — An open table format; a structured data format similar to SQL tables or DataFrames.
- **Iceberg (Apache Iceberg)** — An open table format; a structured data format similar to SQL tables or DataFrames.
- **Avro** — A semi-structured, schema-based serialization format similar to JSON.
- **Protobuf (Protocol Buffers)** — A schema-based binary serialization format that is its own thing entirely.
- **Parquet** — A columnar file format for structured data.
- **Object store** — File storage such as S3 where bulk data files live.

## NoSQL Databases
- **NoSQL database** — A non-relational database that does not use fixed relational tables.
- **Document database** — NoSQL type storing JSON-like documents, e.g. MongoDB and AWS DocumentDB.
- **Column family database** — NoSQL type storing data in column families, e.g. DynamoDB, HBase and Cassandra.
- **Graph database** — NoSQL type storing nodes and relationships, e.g. Neo4J and AWS Neptune.
- **MongoDB** — A document NoSQL database.
- **AWS DocumentDB** — AWS's document-type database.
- **DynamoDB** — AWS's managed NoSQL key-value and column family database.
- **HBase** — Hadoop's column family NoSQL database.
- **Cassandra** — Distributed column family NoSQL database.
- **Neo4J** — A graph database.
- **AWS Neptune** — AWS's managed graph database.
- **GSI (Global Secondary Index)** — A DynamoDB index that lets you query on attributes other than the table's primary key.

## Kafka Message Keys
- **Message key** — Optional value on a Kafka record that is hashed to choose its partition, so the same key always goes to the same partition.
- **Message value** — The payload of a Kafka record, the application data consumers use.
- **Partition ordering** — Kafka only guarantees order within a partition, so a key gives per-entity ordering.
- **Log compaction** — Topic setting that keeps only the latest value per key, useful for current-state topics.
- **Hot partition** — A partition overloaded because one key produces a large share of traffic.
- **Cardinality and distribution** — How many distinct key values exist and how evenly traffic spreads across them.
- **KafkaProducer** — kafka-python class that sends records to Kafka.
- **key_serializer / value_serializer** — Producer functions that convert keys and values to bytes.
- **producer.send** — Sends a record, optionally with a key, to a topic.
- **selectExpr** — Spark method selecting columns using SQL expressions, e.g. casting Kafka key and value to strings.

## Spark Structured Streaming vs. Flink
- **Micro-batch** — Spark's default streaming model of collecting events over a time window and processing them together.
- **Record-at-a-time** — Flink's streaming model where each event flows through operators without waiting for a batch.
- **trigger(processingTime=...)** — Sets how often Spark Structured Streaming runs a micro-batch, e.g. every 5 seconds.
- **outputMode("append")** — Streaming output mode that writes only new rows.
- **format("console")** — Streaming sink that prints results to the terminal.
- **Latency models** — Batch (hours or days), micro-batch (seconds to sub-second) and record-at-a-time (very low latency).
- **Event time** — The time an event actually happened, as opposed to when it was processed.
- **processed_at** — Timestamp column recording when Spark processed a record.
- **Stateful processing** — Stream processing that remembers information across events.
- **Apache Flink** — Open-source record-at-a-time stream processing engine with very low latency.
- **Flink SQL** — Flink's SQL interface, which can define a Kafka topic as a table and run continuous queries.
- **JobManager / TaskManager** — Flink's coordinator process and worker process.
- **Port 8081** — Flink web UI's default port.
- **Docker Compose** — Tool that defines and runs multi-container setups from one file.
- **host.docker.internal** — Hostname a container uses to reach services on the host machine.

## MongoDB as a Sink
- **mongosh** — MongoDB's interactive shell.
- **Port 27017** — MongoDB's default port.
- **Collection** — A MongoDB group of documents, like a table; created automatically on first write.
- **Document** — A single JSON-like record in MongoDB.
- **foreachBatch()** — Spark streaming method that passes each micro-batch to a function as a normal DataFrame.
- **checkpointLocation** — Directory where Spark Structured Streaming saves progress so it can resume after restart.
- **Checkpoint** — Saved record of streaming progress, including offsets processed.
- **Spark connector** — A JAR library that teaches Spark how to talk to an external system such as Kafka or MongoDB.
- **spark-sql-kafka-0-10** — Spark's Kafka connector package.
- **mongo-spark-connector** — MongoDB's Spark connector package.
- **spark-submit** — Command that launches a Spark application.
- **--packages** — spark-submit option that downloads connector dependencies by Maven coordinates.
- **spark.jars.packages** — Config equivalent of `--packages`, set in code; use only one of the two.
- **Processing layer** — The layer that transforms the stream, here Spark.
- **Serving layer** — The layer that stores results for consumers such as dashboards, here MongoDB.

## Querying and Indexing MongoDB
- **use** — mongosh command that switches to a database.
- **show collections** — Lists a database's collections.
- **find()** — Queries documents in a collection.
- **pretty()** — Formats query output for readability.
- **countDocuments()** — Returns the number of documents in a collection.
- **sort / limit** — Order results and cap how many are returned.
- **Projection** — Selecting only certain fields in a query result.
- **_id index** — The automatic index every MongoDB collection starts with.
- **getIndexes()** — Lists a collection's indexes.
- **createIndex** — Creates an index on one or more fields.
- **Single-field index** — Index on one field, ascending (1) or descending (-1).
- **Compound index** — Index on multiple fields supporting filter-plus-sort queries.
- **Text index** — Index supporting word search with `$text` and `$search`.
- **explain("executionStats")** — Shows how MongoDB executed a query.
- **COLLSCAN** — Collection scan, reading every document because no usable index exists.
- **IXSCAN** — Index scan, using an index to find documents.
- **Index write cost** — Every insert must update each index, so extra indexes slow ingestion and use storage.

## Streamlit Dashboard
- **Streamlit** — Python library for building web dashboards.
- **streamlit run** — The correct way to launch a Streamlit app; running with plain `python` causes bare-mode warnings.
- **Port 8501** — Streamlit's default local port.
- **@st.fragment(run_every=...)** — Decorator that re-runs a section of the app on an interval for auto-refresh.
- **st.metric** — Displays a single KPI tile.
- **st.line_chart / st.bar_chart** — Display line and bar charts.
- **st.dataframe** — Displays a table.
- **pymongo** — Python driver for MongoDB.
- **pandas** — Python data analysis library providing DataFrames.
- **pivot_table** — pandas function reshaping data, e.g. one column per city.

## Weather Pipeline
- **Open-Meteo API** — Free weather API with no key, used as the producer's data source.
- **API (Application Programming Interface)** — An interface programs use to request data or services from another system.
- **StructType** — Spark class defining an explicit schema of typed fields.
- **DoubleType / IntegerType / StringType** — Spark field types for decimals, integers and text.
- **current_timestamp()** — Spark function returning the current time.
- **from_json()** — Spark function parsing a JSON string column into structured columns.
- **kafka-topics.sh --create** — Creates a Kafka topic, with options such as `--partitions`.

## Troubleshooting
- **Classpath** — The set of locations where the JVM looks for classes and JARs.
- **Failed to find data source** — Spark error meaning the connector for that source is missing, not the server.
- **NoSuchMethodError: scala.Predef$.wrapRefArray** — Error from a connector built for the wrong Scala version.
- **Scala version suffix (_2.12 / _2.13)** — Part of an artifact name that must match Spark's Scala version.
- **spark-submit --version** — Shows the Spark and Scala versions installed.
- **nc -vz** — Netcat check of whether a host port is open.
- **Publishing a port (-p)** — Docker option making a container port reachable from the host.
- **docker ps / docker ps -a** — List running containers, or all containers including stopped ones.
- **docker port** — Shows a container's port mappings.
- **docker rm** — Removes a container.
- **meta.properties** — Kafka storage metadata file required in KRaft mode.
- **kafka-storage.sh** — Tool that generates a cluster ID (`random-uuid`) and formats KRaft storage (`format`).
- **Address already in use** — Error when another process already holds the port.
- **lsof / ss** — Linux tools that show which process is using a port.
- **ps -fp** — Shows details for a given process ID.
- **Image pinning** — Using a specific image version tag instead of `:latest` for reproducibility.
- **advertised.listeners** — Kafka setting for the address the broker tells clients to use after bootstrap.
- **PLAINTEXT** — Unencrypted Kafka listener protocol.
- **Layer-by-layer testing** — Verifying a pipeline one component at a time, from port check to Spark consumer.

## Kafka Concepts
- **Serialization (Kafka)** — Kafka only moves bytes, so producers encode data and consumers decode it.
- **Schema Registry** — Service storing Avro or Protobuf schemas so producers and consumers agree on format.
- **Replication** — Copying each partition to several brokers for fault tolerance.
- **Replication factor** — The number of copies of each partition.
- **Leader** — The partition replica that handles reads and writes.
- **Follower** — A partition replica that keeps a copy of the leader's data.
- **Leader election** — Promoting an eligible follower when a leader's broker dies.
- **Rebalancing** — Reassigning partitions when consumers join or leave a group.
- **At-most-once** — Delivery that may lose messages but never duplicates.
- **At-least-once** — Delivery with no loss but possible duplicates.
- **Exactly-once** — Delivery where the effect happens once, requiring coordinated producers, offsets, transactions and sinks.
- **Consumer lag** — Latest offset minus the consumer's position; growing lag is a key warning sign.
- **KRaft** — Kafka managing its own metadata with a Raft-based controller quorum; Kafka 4.x is KRaft-only.
- **Controller quorum** — The group of Kafka nodes that manage cluster metadata in KRaft.
- **Edge gateway** — Device near sensors that makes local, millisecond decisions before forwarding data.
- **WAN (Wide Area Network)** — A network spanning large distances, connecting sites to the cloud or data center.
- **Data lake** — Storage for large volumes of raw and historical data for analytics and ML.
- **CDN (Content Delivery Network)** — Distributed servers that deliver content such as video from nearby locations.
- **Event backbone** — Kafka's role as the central channel that many independent producers and consumers share.
