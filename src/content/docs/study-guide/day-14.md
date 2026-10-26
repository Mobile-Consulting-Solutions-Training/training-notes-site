---
title: Study Guide - Day 14
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 14: Kafka Cluster Setup & Spark Streaming"
sidebar:
  order: 140
---

Study Guide - Day 14 (source: notes/Training 14.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Formatting a KRaft Cluster.** KRaft mode (Kafka 3.3+, no ZooKeeper) stores metadata in a log on disk that must be formatted once before the first start: `KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"` → `bin/kafka-storage.sh format --standalone -t "$KAFKA_CLUSTER_ID" -c config/server.properties` → `kafka-server-start.sh`. Every node in a cluster uses the same ID. `--standalone` = single-node controller quorum. Reformatting wipes all topics. `No readable meta.properties` = storage not formatted. The `apache/kafka` Docker image does this automatically.

**Virtual Environment vs Container vs VM.** A **venv** isolates Python packages only (`python3 -m venv .venv`, `source .venv/bin/activate`, `pip freeze > requirements.txt`, `deactivate`); Ubuntu blocks system `pip install` (`externally-managed-environment`). A **container** isolates an app and its dependencies but **shares the host kernel**. A **VM** runs a full OS with its own kernel on a hypervisor (EC2 instances are VMs). The MongoDB kernel-6.19 bug hit inside Docker because containers share the host kernel. They often stack: VM → Docker → container → venv. Never commit `.venv`; share `requirements.txt`.

**Restarting After a Reboot.** Bring things back in order: storage/broker, producer, consumer, dashboard. `docker start` a stopped container to keep its data; `docker ps -a` shows stopped ones; use `--restart unless-stopped` to survive reboots. Kafka lost its KRaft metadata (likely because `log.dirs` defaults to `/tmp`), so storage had to be reformatted and topics recreated.

**python vs spark-submit.** Running the consumer with `python` gave `Failed to find data source: kafka` because the connector JARs weren't loaded. Use `spark-submit --packages ...` or set `spark.jars.packages` in code. Some programs must start through their framework's launcher (`spark-submit`, `streamlit run`).

**The UnknownTopicOrPartitionException Hunt.** Tried recreating the topic, deleting the checkpoint, checking advertised listeners, a console consumer (worked), deprecated offset fetching, `assign` instead of `subscribe`, then a minimal test (worked). Probable real cause: the traceback pointed to the **old `consumer.py`**, which subscribed to the deleted `test-topic`. Lesson: read the file path and line in the traceback, isolate layers, change one thing at a time.

**Parquet Sink Workaround.** Spark's file sink writes each micro-batch as Parquet (`format("parquet")`, `path`, `checkpointLocation`); the dashboard reads the folder with `pd.read_parquet`. Built in and exactly-once with a checkpoint, but creates many small files.

**Spark vs Flink, Same Topic.** Both consume `weather` independently with their own offsets (separate consumer groups); two dashboards on ports 8501 and 8502. PyFlink: `StreamExecutionEnvironment` ≈ `SparkSession`, `KafkaSource.builder()` + `env.from_source` ≈ `readStream`, `stream.map(fn)` per record, `env.execute()` ≈ `start()`.

**Flink Setup Lessons.** `pip install apache-flink` installs PyFlink only, not the `flink` CLI, JobManager, TaskManager or web UI (port 8081), which come from the binary distribution. Install PyFlink in its own venv (it broke Evan's other packages). Flink doesn't bundle connectors: add `flink-connector-kafka-5.0.0-2.1.jar` **and** its dependency `kafka-clients-4.1.0.jar`, or use the fat `flink-sql-connector-kafka` JAR. Check the version matrix: Flink 2.3 had no Kafka connector, so the class used 2.1. Connectors match the **engine** version. The Flink distribution bundles its own Scala, so Scala 2.12 Flink is fine next to Scala 2.13 Spark.

**Market Data Demo.** A FastAPI `/tick` endpoint returns random-walk stock ticks with a `sequence` number and timestamps; a paced producer sends ~50/sec to a **one-partition** topic `market_ticks` (one total order). Spark (2-second trigger) and Flink both write JSONL for one Streamlit dashboard joined on `sequence`.

**Measuring Latency.** Timestamp chain: `exchange_ts` → `api_ts` → `kafka_ts` → `kafka_broker_ts` → `processed_ts`. `processing_latency_ms = processed − kafka`; `end_to_end_latency_ms = processed − exchange` (via `unix_millis`). Spark stamps one `processed_ts` per batch, so latency forms a **sawtooth from ~0 to ~2000 ms**: the visible proof of micro-batching. Demo-only shortcuts: `.collect()` to the driver, appending to a local file (not exactly-once).

**Why Flink Also Looked Batched.** PyFlink sends records to a Python worker in **bundles**, so timestamps taken in Python `map()` cluster. ChatGPT's fix simulated Flink's timing (Kafka time + 5 ms), which illustrates the idea but is no longer a measurement. Honest options: tune `python.fn-execution.bundle.size/time`, timestamp in the JVM (Flink SQL `PROCTIME()`), or label the panel simulated. Dashboard lessons: check the data before the chart, use rolling windows, normalize different-scale series. Wrong lesson: "Flink fast, Spark slow."

---

# Part 2: Cheat Sheet

## KRaft Format
- `random-uuid` → `format --standalone -t $ID -c server.properties` → start
- Once only · reformat = data loss · same ID for all nodes · watch `log.dirs` in `/tmp`

## venv / Container / VM
- venv = packages · container = app + deps, shared kernel · VM = full OS + kernel
- `python3 -m venv .venv` · `source .venv/bin/activate` · `pip freeze > requirements.txt`

## Restart Order
- Storage/broker → producer → consumer → dashboard
- `docker start` (keeps data) · `docker ps -a` · `--restart unless-stopped`

## Launchers
- `spark-submit --packages` (or `spark.jars.packages`) · `streamlit run`

## Debugging Method
- Read traceback path + line · isolate layers · one change at a time · remove failed experiments
- `subscribe` (discover partitions) vs `assign` (exact partitions)

## Sinks
- Parquet file sink: built in, exactly-once w/ checkpoint, small files
- MongoDB via `foreachBatch`: indexed serving layer, extra connector

## Flink
- PyFlink ≠ Flink CLI · own venv · connector + `kafka-clients` JARs (or fat JAR)
- Connector `<ver>-<flink>` matches engine · web UI 8081
- `MapFunction`: `open` once, `map` per record, `close` once

## Latency Demo
- Timestamps: exchange → api → kafka → broker → processed
- Spark sawtooth 0–2000 ms · PyFlink bundles distort Python timestamps

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: Why do you have to format storage before starting Kafka in KRaft mode?
A: Without ZooKeeper, Kafka keeps its own cluster metadata in a log on disk. That directory has to be stamped with a cluster ID and initial metadata once before the first start.

Q: What happens if you reformat Kafka storage?
A: Every topic and message in it is deleted, so you have to recreate the topics. That's why formatting is a one-time step.

Q: What's the difference between a virtual environment, a container and a virtual machine?
A: A venv isolates only Python packages. A container isolates an application and its dependencies but shares the host's kernel. A VM runs a whole operating system with its own kernel on virtual hardware.

Q: Why didn't running MongoDB in Docker avoid the kernel bug?
A: Containers share the host's kernel, so a kernel incompatibility affects them too. Only a VM, with its own kernel, would have avoided it.

Q: Why shouldn't you commit a .venv folder?
A: It's large and tied to one machine. Share requirements.txt instead so others can rebuild the environment.

Q: In what order do you restart a streaming pipeline after a reboot?
A: Storage and the broker first, then the producer, then the consumer, then the dashboard.

Q: Why did the consumer fail with "Failed to find data source: kafka"?
A: It was started with plain python, which doesn't load the connector JARs. Running it with spark-submit and --packages, or setting spark.jars.packages in the code, fixes it.

Q: What was the most likely cause of the UnknownTopicOrPartitionException?
A: The traceback pointed to the old consumer file, which subscribed to a topic deleted by the reformat. The lesson is to read the file path and line number in the traceback and check you're running the file you think you are.

Q: How do you debug a multi-layer pipeline?
A: Isolate the layers. Test Kafka alone with the console consumer, then a minimal Spark job, then the full job, and change one thing at a time.

Q: What's the difference between subscribe and assign in the Spark Kafka source?
A: Subscribe names a topic and lets Spark discover its partitions. Assign names exactly which partitions to read.

Q: What are the pros and cons of writing a stream to Parquet files?
A: It's built in, needs only the Kafka connector and is exactly-once with a checkpoint. But it creates many small files and the dashboard has to re-read them.

Q: Does pip install apache-flink give you the flink command?
A: No. It installs PyFlink, the Python API with a local runtime. The CLI, JobManager, TaskManager and web UI come from the Flink binary distribution.

Q: Why did Flink need two JARs to read from Kafka?
A: The Flink Kafka connector doesn't bundle its dependency, kafka-clients. You add both, or use the fat SQL connector JAR that includes it.

Q: Does Flink's Scala version need to match your system's Scala?
A: No. A Flink distribution bundles its own Scala libraries. Scala versions only matter for libraries you load into an engine, like a Spark connector.

Q: How did the market demo prove Spark micro-batches?
A: Spark stamped one processed time per batch, so latencies formed a sawtooth from near zero to about two seconds, and every record in a batch shared one timestamp.

Q: Why did the Flink output also look batched?
A: PyFlink runs Python functions in a separate worker that receives records in bundles, so timestamps taken in Python cluster. It's an artifact of the Python bridge, not Flink's streaming model.

Q: What's wrong with simulating Flink's processing time in the dashboard?
A: Then the comparison isn't a measurement anymore. Spark's timing is real, but Flink's is computed from a formula that guarantees a smooth line.

Q: What does a MapFunction's open, map and close do in Flink?
A: Open runs once at startup to set up resources like files or connections, map runs once per record, and close runs once at shutdown to clean up.

Q: Why use one Kafka partition for the market demo?
A: Kafka only guarantees order within a partition, so one partition keeps every tick in sequence order. A real feed would use several partitions keyed by symbol.
