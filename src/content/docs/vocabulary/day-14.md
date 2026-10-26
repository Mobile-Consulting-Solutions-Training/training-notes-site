---
title: Day 14 Vocabulary
description: Glossary of terms and definitions from the Training 14 notes.
sidebar:
  order: 14
---

Vocabulary — Study Guide Day 14

Source: notes/Training 14.md

## Kafka Cluster Setup (KRaft)
- **KRaft mode** — Kafka 3.3+ mode with no Zookeeper, where Kafka stores its own cluster metadata in a log on disk.
- **Formatting a Kafka cluster** — One-time step that writes the cluster ID and initial metadata into the broker's log directories before first start.
- **kafka-storage.sh random-uuid** — Generates a new unique cluster ID.
- **kafka-storage.sh format** — Formats KRaft storage with a cluster ID (`-t`) using a server config file (`-c`).
- **Cluster ID** — Unique identifier stamped into storage; every broker and controller in one cluster must share it.
- **--standalone** — Formats the node as a single-node controller quorum for a one-machine lab cluster.
- **server.properties** — Kafka broker configuration file.
- **log.dirs** — server.properties setting for where Kafka stores its data; defaults under `/tmp`, which is cleared on reboot.
- **metadata.log.dir** — server.properties setting for where KRaft metadata is stored.
- **meta.properties** — Storage file whose absence means the KRaft directory was never formatted or was wiped.
- **Reformatting** — Wiping and re-formatting KRaft storage, which deletes all topics and messages.

## Python Virtual Environments
- **Virtual environment (venv)** — A private folder of Python packages for one project, usually `.venv`, isolated from other projects and the system Python.
- **python3 -m venv .venv** — Creates a virtual environment.
- **source .venv/bin/activate** — Turns a venv on so `python` and `pip` use the project's copies.
- **deactivate** — Turns a venv off.
- **pip install** — Installs a package into the active environment.
- **pip freeze > requirements.txt** — Saves the exact installed package list.
- **pip install -r requirements.txt** — Rebuilds an environment from a requirements file.
- **requirements.txt** — File listing a project's Python dependencies, shared instead of the venv folder.
- **externally-managed-environment** — Ubuntu error blocking `pip install` into the system Python.
- **System Python** — The operating system's own Python installation, which OS tools depend on.
- **uv** — A fast Python package and environment manager.

## Virtual Machines and Containers
- **Virtual machine (VM)** — A complete computer simulated in software with its own virtual hardware and full OS kernel.
- **Hypervisor** — Software that divides real hardware among VMs, e.g. VirtualBox, VMware, KVM, Hyper-V or EC2's Nitro.
- **Kernel** — The core of an operating system that manages hardware and processes.
- **Container** — An isolated app plus its dependencies and filesystem that shares the host's kernel.
- **Userland** — The files and tools of an OS outside the kernel; a container has its own.
- **AWS EC2 instance** — A virtual machine in AWS.
- **Podman** — A container tool alternative to Docker.
- **venv vs. container vs. VM** — A venv isolates Python packages, a container isolates an application while sharing the host kernel, and a VM isolates an entire OS.

## Restarting a Pipeline
- **Startup order** — Storage and broker first, then producer, then consumer, then dashboard.
- **docker start** — Restarts an existing stopped container, keeping its data.
- **Restart policy** — Docker setting such as `--restart unless-stopped` that brings a container back after reboot.
- **kafka-topics.sh --list** — Lists a cluster's topics.
- **kafka-topics.sh --describe** — Shows a topic's partitions and their leaders.
- **--replication-factor** — Number of copies of each partition when creating a topic.
- **Framework launcher** — A program like `spark-submit` or `streamlit run` that must start certain Python apps instead of plain `python`.

## Debugging Kafka and Spark
- **UnknownTopicOrPartitionException** — Kafka error that the requested topic or partition does not exist on the server.
- **Stale checkpoint** — A checkpoint remembering partitions and offsets from an old or deleted cluster.
- **--from-beginning** — Console consumer option reading a topic from its first retained record.
- **--max-messages** — Console consumer option to stop after a number of messages.
- **subscribe** — Spark Kafka option meaning "this topic, discover its partitions".
- **assign** — Spark Kafka option naming exact partitions, skipping partition discovery.
- **useDeprecatedOffsetFetching** — Spark config switching to the older consumer-based Kafka offset reader.
- **AdminClient** — Kafka client API for administrative operations such as listing partitions.
- **awaitTermination()** — Keeps a streaming query running until it is stopped.
- **Traceback** — The error stack showing file paths and line numbers where an exception occurred.
- **--verbose** — spark-submit option printing detailed launch info, such as loaded JARs.
- **tee** — Command that shows output on screen and saves it to a file at the same time.
- **~/.ivy2 / ~/.m2** — Local caches where Spark and Maven store downloaded JARs.
- **Isolating layers** — Debugging by testing one pipeline component at a time and changing one thing at a time.

## Parquet File Sink
- **File sink** — Spark streaming sink writing each micro-batch as new files in a folder.
- **Parquet** — Columnar file format used here as the streaming output.
- **format("parquet")** — Sets a streaming write to output Parquet files.
- **option("path", ...)** — Output folder for a file sink.
- **pd.read_parquet** — pandas function reading a Parquet file or folder.
- **groupby().tail(1)** — pandas pattern getting the latest row per group.
- **Small files problem** — Many small output files accumulating over time from frequent micro-batches.

## Flink
- **Apache Flink** — Stream processing engine that processes records one at a time.
- **PyFlink (apache-flink)** — Flink's Python API plus a local runtime, installed with pip; it does not include the `flink` CLI.
- **Flink binary distribution** — The full Flink download providing the `flink` CLI, JobManager, TaskManager and web UI.
- **JobManager** — Flink's coordinator process.
- **TaskManager** — Flink's worker process that executes tasks.
- **start-cluster.sh / stop-cluster.sh** — Scripts that start and stop a local Flink cluster.
- **FLINK_HOME** — Environment variable pointing at the Flink install directory.
- **PATH** — Environment variable listing directories searched for commands.
- **jps** — Java tool listing running JVM processes.
- **Flink DataStream** — Flink's API for processing unbounded streams of records.
- **StreamExecutionEnvironment** — The entry point for a Flink streaming job, equivalent to SparkSession.
- **env.add_jars** — Adds connector JAR files to a PyFlink job.
- **set_parallelism** — Sets how many parallel instances Flink runs per operator.
- **KafkaSource** — Flink's Kafka source, configured with a builder.
- **set_group_id** — Sets the Kafka consumer group the Flink source uses.
- **KafkaOffsetsInitializer.latest()** — Starts reading from the newest offsets.
- **SimpleStringSchema** — Deserializer that reads Kafka values as plain strings.
- **from_source** — Creates a Flink stream from a source.
- **WatermarkStrategy.no_watermarks()** — Disables event-time watermarks.
- **Watermark** — A marker that tracks event-time progress for handling late or out-of-order data.
- **env.execute** — Submits and runs a Flink job, like starting a Spark query.
- **Types.STRING()** — Declares a Flink operator's output type as string.
- **MapFunction** — Flink class with a lifecycle: `open()` once at startup, `map()` once per record, `close()` once at shutdown.
- **RuntimeExecutionMode.STREAMING** — Flink mode for unbounded streams, versus BATCH mode.
- **Unbounded stream** — A data stream with no defined end.
- **Flink Kafka connector** — JAR letting Flink read and write Kafka, named `<connector version>-<Flink version>`.
- **Transitive dependency** — A library that another library needs, such as `kafka-clients` for the Flink Kafka connector.
- **NoClassDefFoundError** — Java error when a class needed at runtime is missing from the classpath.
- **Fat JAR (flink-sql-connector-kafka)** — A JAR bundling a library with its dependencies in one file.
- **Maven Central** — The main public repository of Java libraries.
- **Connector/version matrix** — The compatibility table of which connector versions work with which engine versions.
- **Python bridge bundling** — PyFlink sends records to a separate Python worker in bundles, so Python `map()` timestamps cluster together.
- **python.fn-execution.bundle.size / bundle.time** — PyFlink settings controlling records per bundle and maximum wait before sending a bundle.
- **PROCTIME()** — Flink SQL function for processing time computed inside the JVM.
- **wget -c** — Resumes a partially completed download.

## Market Data Demo
- **FastAPI** — Python framework that turns functions into web API endpoints.
- **@app.get** — FastAPI decorator mapping an HTTP GET path to a function.
- **uvicorn** — ASGI web server used to run a FastAPI app.
- **curl** — Command-line tool for making HTTP requests.
- **REST API** — A web API using HTTP methods on resource URLs.
- **Random walk** — Price simulation where each step adds a small random change.
- **random.gauss** — Python function returning a normally distributed random number.
- **Sequence number** — A unique, ordered event ID used to detect loss or reordering.
- **UTC ISO-8601 timestamp** — Standard timestamp string in UTC that compares correctly across machines and time zones.
- **Jitter** — Small random variation in delay.
- **Single partition** — One partition gives one total order but no parallelism.
- **Fixed-rate loop** — Producer loop that sleeps only for the remainder of each interval to hit a target rate.
- **time.perf_counter()** — High-precision timer for measuring elapsed time.
- **requests.Session()** — Reuses one HTTP connection across many requests.
- **raise_for_status()** — Raises an error if an HTTP response has an error status.
- **Ticks per second** — The rate of market events the producer sends.

## Spark Market Consumer
- **setLogLevel("ERROR")** — Reduces Spark console logging to errors only.
- **StructField** — One named, typed field in a Spark StructType schema.
- **LongType** — Spark 64-bit integer type.
- **kafka.bootstrap.servers** — Spark Kafka source option giving the broker address.
- **startingOffsets** — Spark Kafka option for where a new query starts reading, e.g. `latest`.
- **Kafka record timestamp** — Kafka's own timestamp column provided with key, value, partition and offset.
- **alias** — Renames a column.
- **withColumn** — Adds or replaces a DataFrame column.
- **data.*** — Expands a struct column into its individual fields.
- **isEmpty()** — Checks whether a DataFrame has no rows.
- **lit()** — Creates a constant-value column.
- **to_timestamp** — Converts a string to a timestamp.
- **unix_millis** — Converts a timestamp to milliseconds since 1970.
- **orderBy** — Sorts DataFrame rows.
- **collect()** — Pulls all rows to the driver; unsafe at large volume because it can exhaust driver memory.
- **asDict()** — Converts a Spark Row to a Python dictionary.
- **JSON Lines (JSONL)** — File format with one JSON object per line.
- **Line buffering (buffering=1)** — Flushes each line to disk immediately.
- **Timestamp chain** — Recording a timestamp at every pipeline stage to see where time is spent.
- **Processing latency** — Time from a record reaching Kafka to being processed.
- **End-to-end latency** — Total time from event creation to processed result.
- **Sawtooth latency pattern** — Latencies rising from about 0 to the trigger interval within each micro-batch, the visual proof of micro-batching.
- **Idempotent sink** — A sink where writing the same data twice gives the same result, e.g. an upsert keyed on sequence.
- **Upsert** — Insert a row or update it if the key already exists.

## Dashboard Lessons
- **Rolling window** — Showing only recent data so old records do not squash a live chart's axis.
- **Normalization** — Plotting percent change from a starting value so series on different scales are comparable.
- **Window anchoring** — Basing each engine's time window on its own newest timestamp.
- **--server.port** — Streamlit option to run a dashboard on a different port.
- **Expander** — Streamlit collapsible section of content.
- **Join on sequence** — Matching the same trade's records from both engines to compare them.
- **Simulated vs. measured timing** — The final Flink panel computed timestamps from a formula rather than measuring them, so it illustrates rather than proves the difference.

## Trading Latency Perspective
- **Latency-sensitive strategy** — A trading approach where delays mean acting on prices that have already changed.
- **Rolling average signal** — A simple BUY/SELL rule comparing price to its recent average.
- **Benchmark** — A controlled performance comparison; the class demo is explicitly not one.
