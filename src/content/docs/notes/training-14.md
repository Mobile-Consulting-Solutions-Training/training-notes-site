---
title: "Training 14 - Kafka Cluster Setup & Spark Streaming"
description: "Kafka KRaft cluster setup, the teacher's ChatGPT class walkthrough, and a market-data demo measuring Spark micro-batch latency."
---

Teacher: Evan Flint

Syllabus Day 15 (per file numbering) - topic: MongoDB + Spark Streaming (per `Course Roadmap.md`).

# Kafka Cluster Setup (KRaft)

## Formatting a Kafka Cluster

Teacher's definition: "to format a kafka cluster:"

```bash
bin/kafka-storage.sh format \
  --standalone \
  -t "$KAFKA_CLUSTER_ID" \
  -c config/server.properties
```

Teacher's note: "before the above, get a new cluster id:"

```bash
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
echo $KAFKA_CLUSTER_ID
```

Expanded: this is the one-time setup for a Kafka broker running in **KRaft mode**, the newer Kafka (3.3+) mode with no Zookeeper (see `Training 12.md`, "starting Kafka locally (older versions)"). Without Zookeeper, Kafka stores its own cluster metadata in a log on disk, and that storage directory has to be **formatted** before the broker's first start, much like formatting a new drive before using it.

| Step | Command | What it does |
|---|---|---|
| 1. Generate a cluster ID | `bin/kafka-storage.sh random-uuid` | Creates a unique ID for this cluster. Saving it in `KAFKA_CLUSTER_ID` lets the next command use it |
| 2. Format storage | `bin/kafka-storage.sh format ...` | Writes the cluster ID and initial metadata into the log directories listed in `server.properties` |
| 3. Start the broker | `bin/kafka-server-start.sh config/server.properties` | Starts Kafka normally, with no separate Zookeeper process first |

| Flag | Meaning |
|---|---|
| `-t` / `--cluster-id` | The cluster ID to stamp into storage. Every broker and controller in one cluster must be formatted with the **same** ID |
| `-c` / `--config` | The server config file, which says where the log directories are (`log.dirs`) and what role the node plays |
| `--standalone` | Formats this node as a single-node controller quorum, the simplest setup for a one-machine dev or lab cluster |

Things to watch for:
- Formatting only needs to happen **once**. Running it again on a directory that is already formatted fails, which protects existing data. Wiping the log directory and reformatting deletes every topic and message.
- If the broker won't start and complains about a missing `meta.properties` or an unformatted directory, this step was skipped.
- `echo $KAFKA_CLUSTER_ID` is just a check that the variable was set. If it prints nothing, the `format` command gets an empty ID and fails.
- The Docker image used in the Training 13 homework (`apache/kafka`) runs these steps automatically when the container starts, which is why they weren't needed there.

---

# Agent Generated Notes

Not from the teacher. Added from questions asked during class while setting up PyFlink with `pip install apache-flink`.

## Virtual Environments (Python)

Expanded: a **virtual environment** (venv) is a private folder of Python packages for one project, usually named `.venv`. Each project gets its own Python interpreter link and its own installed packages, so projects can't conflict with each other or break the Python that the operating system itself depends on.

Analogy: the computer is a kitchen. Without virtual environments, every recipe shares one pantry: one recipe needs an old brand of flour, another needs the new one, and they fight over the same shelf. A virtual environment gives each recipe its own lunchbox with exactly the ingredients it needs.

**Why it matters on this machine (Ubuntu 26.04):**

| Environment | Python | Contents | Why it's separate |
|---|---|---|---|
| `homework/submission/alex_jackson_streaming_homework/.venv` | 3.12 | Spark 3.5, kafka-python, pymongo, streamlit | Spark 3.5 doesn't support Python 3.14 |
| `flink-practice/.venv` | 3.12 | PyFlink 2.3 (`apache-flink`) | PyFlink supports only Python 3.9-3.12 |
| System Python (no venv) | 3.14 | Ubuntu's own tools | Ubuntu blocks `pip install` here (`externally-managed-environment` error) so nothing breaks the OS |

**Commands:**

| Command | What it does |
|---|---|
| `python3 -m venv .venv` | Creates a virtual environment in a folder called `.venv` (needs `sudo apt install python3-venv` once on Ubuntu) |
| `source .venv/bin/activate` | Turns it on: `(.venv)` appears in the prompt, and `python`/`pip` now mean this project's copies |
| `pip install <package>` | Installs into **this** environment only |
| `pip freeze > requirements.txt` | Saves the exact package list so others can rebuild the environment |
| `pip install -r requirements.txt` | Rebuilds an environment from that list |
| `deactivate` | Turns it off and goes back to the system Python |

**Rules of thumb:**
- Activate before running `pip install` or running code. Forgetting this is the usual cause of `No module named ...` and `externally-managed-environment` errors.
- PyFlink specifically starts its worker processes with the command `python`, which only exists while a venv is active. Without it, jobs fail with `Cannot run program "python"`.
- Never commit, copy or submit the `.venv` folder. It's large and tied to one machine. Share `requirements.txt` instead.

## Virtual Machines

Expanded: a **virtual machine** (VM) is a complete computer simulated in software: its own virtual CPU, memory, disk and a **full operating system**, running on top of the real machine. A program called a **hypervisor** (VirtualBox, VMware, KVM, Hyper-V, or AWS EC2's Nitro) divides the real hardware among the VMs. Each VM boots its own OS kernel, so a Windows VM can run on a Linux host, and a crash inside a VM doesn't affect the host.

In data engineering, VMs are everywhere even when you don't see them: every **AWS EC2 instance** is a VM, and Spark or Kafka clusters in the cloud usually run on fleets of VMs.

## Virtual Environment vs. Container vs. Virtual Machine

Despite the shared word "virtual," a virtual environment and a virtual machine isolate completely different things. Docker containers (used for Kafka and MongoDB in the Training 13 homework) sit between them.

| | Virtual Environment (venv) | Container (Docker) | Virtual Machine |
|---|---|---|---|
| **What it isolates** | Python packages only | An app plus all its dependencies, libraries and filesystem | An entire computer: OS, kernel, virtual hardware |
| **Has its own OS?** | No, it uses the machine's OS and Python | Partly: its own Linux userland (files and tools), but it **shares the host's kernel** | Yes, a full OS with its own kernel |
| **Size** | Megabytes | Tens to hundreds of MB | Gigabytes |
| **Startup time** | Instant | Seconds | Tens of seconds to minutes |
| **Isolation strength** | Weakest: just separate package folders | Medium: separate processes, network and filesystem | Strongest: separate kernel and virtual hardware |
| **Can run a different OS?** | No | Only Linux-based on a Linux host (Mac and Windows run a hidden Linux VM underneath) | Yes, for example Windows on Linux |
| **Tool** | `python3 -m venv`, `uv` | Docker, Podman | VirtualBox, VMware, KVM, Hyper-V, cloud (EC2) |
| **Example from this course** | `.venv` for the Spark and Flink work | `kafka` and `mongodb` containers in the streaming homework; the Ubuntu container from `Training 1.md` | AWS EC2 instances |

**A real example of the difference:** in the Training 13 homework, MongoDB 8.0 refused to start inside Docker because the **host's** Linux kernel (7.0) had a known incompatibility (SERVER-121912). Containers share the host kernel, so containerizing MongoDB didn't protect it. A VM runs its own kernel, so it would not have hit that problem; a venv isolates nothing at the OS level at all.

**How they stack in practice:** they're often layered. A cloud **VM** (EC2) runs Docker, Docker runs **containers** (Kafka, Spark), and a Python app inside a container may still use a **venv** for its packages.

**Interview one-liner:** a venv isolates *Python packages*, a container isolates an *application and its dependencies* while sharing the host kernel, and a VM isolates an *entire operating system* on virtual hardware.

---

# Class Walkthrough: Teacher's ChatGPT Session (Sep 30)

Source: the continuation of the same ChatGPT conversation Evan used live in class (link shared; the Sep 28–29 portion is summarized in `Training 13.md`). These are ChatGPT's explanations that the teacher worked through, **not** the teacher's own verbatim definitions. The session ended with the Training 13 homework being generated (Sep 29, 16:56); this class picked up after Evan's machine restarted.

Today's arc:
1. Bring yesterday's Kafka → Spark → MongoDB → Streamlit pipeline back after a reboot.
2. Kafka wouldn't start → reformat KRaft storage.
3. The Spark consumer kept failing with `UnknownTopicOrPartitionException` → drop MongoDB, write **Parquet** files instead.
4. Build a **parallel Flink pipeline** from the same Kafka topic, with a second dashboard, to compare micro-batch and record-at-a-time processing.
5. Work through Flink setup problems (no `flink` command, missing connector JARs, version matrix).

---

## Restarting a Pipeline After a Reboot

Expanded: after a restart, nothing comes back automatically unless it was set up to. The order to bring things back is **storage and broker first, then producer, then consumer, then dashboard**:

| Order | Component | Command | Check |
|---|---|---|---|
| 1 | MongoDB (Docker) | `docker start mongodb`. Reuse the stopped container instead of `docker run`, which keeps its data | `docker ps -a \| grep mongo`, `nc -vz localhost 27017` |
| 2 | Kafka (local KRaft build) | `bin/kafka-server-start.sh config/server.properties` | `nc -vz localhost 9092`, `bin/kafka-topics.sh --bootstrap-server localhost:9092 --list` |
| 3 | Producer | `python weather_producer.py` | Records printing |
| 4 | Spark consumer | `spark-submit --packages <kafka>,<mongo> weather_consumer.py` | "Writing Spark batch N…" |
| 5 | Dashboard | `streamlit run weather_dashboard.py` | `http://localhost:8501` |

- `docker ps` shows only **running** containers; `docker ps -a` shows stopped ones too. A container with no **restart policy** stays stopped after a reboot (`docker run --restart unless-stopped ...` would bring it back automatically).
- `docker start mongodb` failing with `address already in use` means the container is stopped **and** something else holds port 27017. `nc` succeeding only proves *something* is listening, not that it's your container. Identify it with `sudo lsof -nP -iTCP:27017 -sTCP:LISTEN`.
- **Kafka lost its KRaft metadata after the reboot** (`No readable meta.properties files found`). The fix is the storage-format commands from the top of these notes. **Reformatting deletes all topics**, so the topic had to be recreated:

```bash
bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic weather --partitions 3 --replication-factor 1
bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic weather   # every partition needs a valid Leader
```

Likely reason the metadata vanished: the default `log.dirs` in Kafka's `server.properties` is under `/tmp`, which Ubuntu clears on reboot. Check with `grep -E '^(log.dirs|metadata.log.dir)' config/server.properties` and point it at a permanent directory for anything you want to keep. (This is my inference; the class chat didn't confirm it.)

---

## `python` vs. `spark-submit`

The first error after the restart, `Failed to find data source: kafka`, came from running the consumer with `python weather_consumer.py`. Plain `python` starts PySpark **without** the connector JARs; `spark-submit --packages ...` downloads and loads them. It's the same lesson as `streamlit run` vs. `python` for dashboards: **some Python programs must be started by their framework's launcher.**

(An alternative is to put `.config("spark.jars.packages", "...")` in the `SparkSession.builder`, which lets plain `python` work. The streaming homework's `consumer.py` does this.)

---

## The `UnknownTopicOrPartitionException` Debugging Session

Error: `org.apache.kafka.common.errors.UnknownTopicOrPartitionException: This server does not host this topic-partition.`, thrown from Spark's `KafkaOffsetReaderAdmin` / `SubscribeStrategy.retrieveAllPartitions` while starting the stream.

What was tried, in order:

| Attempt | Idea | Result |
|---|---|---|
| Recreate the `weather` topic | Reformatting deleted the old topics | Topic existed with a healthy leader; same error |
| `rm -rf /tmp/weather-mongodb-checkpoint` | A **stale checkpoint** remembers partitions and offsets from the old, deleted cluster | Same error (with a new query ID, so the checkpoint wasn't the cause) |
| Check `advertised.listeners` | A reboot can change the IP/hostname Kafka advertises | Fine: `PLAINTEXT://localhost:9092` |
| `kafka-console-consumer.sh --topic weather --from-beginning --max-messages 5` | Test Kafka without Spark | **Worked**, so Kafka was healthy |
| `.config("spark.sql.streaming.kafka.useDeprecatedOffsetFetching", "true")` | Use the older consumer-based offset reader instead of the AdminClient one | Same error |
| `.option("assign", '{"weather":[0]}')` instead of `subscribe` | Name the exact partitions so Spark skips partition discovery | Same error |
| Minimal `kafka_test.py` (Kafka → console, only the Kafka package) | Remove MongoDB, schema and transformations to isolate the problem | **Worked** |

**Probable root cause (my analysis, not stated in class):** every failing traceback pointed to `/home/evan/Work/kafka-producer-example/consumer.py`, **line 37** `query.awaitTermination()`. That's the old ~37-line Chuck Norris consumer, which subscribes to `test-topic`, not the new `weather_consumer.py`. Reformatting Kafka deleted `test-topic`, and asking Spark for a topic that doesn't exist raises exactly `UnknownTopicOrPartitionException`. ChatGPT noticed the filename once ("your traceback says `consumer.py`") but dropped it. The fresh `kafka_test.py` subscribing to `weather` worked right away, which fits this explanation. **Lesson: read the file path and line number in the traceback, and confirm you're running the file you think you are** (`grep -n subscribe *.py`).

Useful commands from the session:
- `subscribe` vs. `assign`: `subscribe` = "this topic, discover its partitions"; `assign` = "exactly these partitions" (`'{"weather":[0]}'`).
- `spark-submit --packages ... --verbose app.py 2>&1 | tee /tmp/spark-kafka.log` then `grep -Ei 'kafka-clients|spark-sql-kafka' /tmp/spark-kafka.log` shows which JAR versions were actually loaded.
- `find /opt/spark/jars ~/.ivy2 ~/.m2 -name 'kafka-clients*.jar'` finds stray or duplicate Kafka JARs.
- Debugging method: **isolate layers** (console consumer → minimal Spark test → full job) and **change one thing at a time**. Remove failed experiments (like the unused config flag) so they don't pile up.

---

## Workaround: Spark → Parquet → Streamlit (no MongoDB)

Expanded: Spark's built-in **file sink** writes each micro-batch as new Parquet files in a folder, and the dashboard reads that folder. No database is needed, and it still shows a real-time pipeline:

```text
Open-Meteo → Kafka → Spark Structured Streaming → /tmp/weather-stream/*.parquet → Streamlit
```

```python
query = processed_df.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("path", "/tmp/weather-stream") \
    .option("checkpointLocation", "/tmp/weather-stream-checkpoint") \
    .trigger(processingTime="5 seconds") \
    .start()
```

```bash
rm -rf /tmp/weather-stream /tmp/weather-stream-checkpoint     # start clean
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1 consumer.py   # only the Kafka connector now
```

Dashboard side: `pd.read_parquet("/tmp/weather-stream")` reads the whole folder. Wrap it in `try/except`, because Spark may be halfway through writing a file. The rest of the dashboard (metrics, latest reading per city with `groupby("city").tail(1)`, temperature pivot chart, humidity and wind bar charts, Kafka key/partition/offset table) is unchanged.

| Sink | Pros | Cons |
|---|---|---|
| **Parquet files** (file sink) | Built in, needs only the Kafka connector, exactly-once with a checkpoint | Many small files over time; the dashboard re-reads everything on each refresh |
| **MongoDB** (`foreachBatch` + connector) | Indexed queries, a proper serving layer | Extra connector and a database to run |

---

## Parallel Demo: Spark vs. Flink on the Same Kafka Topic

```text
                        ┌─► Spark Structured Streaming (5-sec micro-batches) → Parquet → Streamlit :8501
Open-Meteo → Kafka ─────┤
   (topic "weather")    └─► Flink DataStream (record-at-a-time)              → JSONL   → Streamlit :8502
```

- Both read the **same topic independently**. Each consumer tracks its own offsets (Flink uses consumer group `flink-weather-dashboard`), so neither affects the other.
- The second dashboard runs on another port: `streamlit run flink_weather_dashboard.py --server.port 8502`.
- Spark visibly updates in bursts every 5 seconds; Flink updates per record. The point is the **processing model**, not "Flink is faster."

PyFlink job (`flink_weather_consumer.py`):

```python
env = StreamExecutionEnvironment.get_execution_environment()
env.add_jars("file:///home/<user>/flink-jars/flink-connector-kafka-5.0.0-2.1.jar",
             "file:///home/<user>/flink-jars/kafka-clients-4.1.0.jar")
env.set_parallelism(1)

source = KafkaSource.builder() \
    .set_bootstrap_servers("localhost:9092").set_topics("weather") \
    .set_group_id("flink-weather-dashboard") \
    .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
    .set_value_only_deserializer(SimpleStringSchema()).build()

stream = env.from_source(source, WatermarkStrategy.no_watermarks(), "Kafka Weather Source")

def transform_weather(value):
    record = json.loads(value)
    if record.get("temperature") is not None:
        record["temperature_f"] = round(record["temperature"] * 9 / 5 + 32, 1)
    record["processed_by"] = "flink"
    with open("/tmp/flink-weather.jsonl", "a") as f:   # demo-only sink
        f.write(json.dumps(record) + "\n")
    return json.dumps(record)

stream.map(transform_weather, output_type=Types.STRING()).print()
env.execute("Flink Real-Time Weather ETL")
```

| Piece | PySpark equivalent |
|---|---|
| `StreamExecutionEnvironment` | `SparkSession` |
| `KafkaSource.builder()...build()` + `env.from_source(...)` | `spark.readStream.format("kafka")...load()` |
| `stream.map(fn)`, run once per record | DataFrame transformations, run per micro-batch |
| `env.execute("name")` | `query.start()` + `awaitTermination()` |
| `WatermarkStrategy.no_watermarks()` | (no event-time watermarks; not needed for this demo) |

Writing to a file inside `map()` is a **teaching shortcut only**. Production Flink uses a proper sink with checkpointing for exactly-once output.

---

## Flink Setup Lessons

**1. `pip install apache-flink` does not give you the `flink` command.** It installs **PyFlink** (the Python API plus a local runtime) into a Python environment. Running `source ~/.bashrc` won't create a CLI that was never installed. You don't need `flink --version` to run PyFlink: `python flink_job.py` runs a local job.

| | `pip install apache-flink` (PyFlink) | Flink binary distribution (`flink-2.1.0-bin-scala_2.12.tgz`) |
|---|---|---|
| What you get | Python API to write jobs; runs them locally | `flink` CLI, **JobManager**, **TaskManager**, Web UI, config, logs |
| Start | `python job.py` | `$FLINK_HOME/bin/start-cluster.sh` (stop: `stop-cluster.sh`) |
| Web UI | none | `http://localhost:8081`: running jobs, job graph, operators, metrics, checkpoints, logs |
| Check | `pip show apache-flink` | `flink --version`, `jps` (lists the JVM processes) |

Full-install steps from class: download and extract to `~/flink`, then add `export FLINK_HOME="$HOME/flink"` and `export PATH="$FLINK_HOME/bin:$PATH"` to `~/.bashrc`. Put connector JARs in `$FLINK_HOME/lib/` and restart the cluster to make them available.

**2. Install PyFlink in its own virtual environment.** Installing it into Evan's main Python downgraded `apache-beam`, `pyarrow`, `numpy` and `dill` and broke other packages (sagemaker, airflow, chromadb…). The fix was an isolated venv:

```bash
python -m venv ~/venvs/flink-demo
source ~/venvs/flink-demo/bin/activate
pip install apache-flink==2.1.0
```

(See the "Virtual Environments" section above. This was a real example of why they matter.)

**3. Flink does not include external connectors; you supply the JARs.** Two errors in a row, each one layer deeper:

| Error | Meaning | Fix |
|---|---|---|
| `TypeError: Could not found the Java class 'org.apache.flink.connector.kafka.source.KafkaSource.builder'` | The **Flink Kafka connector** JAR is missing | Download `flink-connector-kafka-5.0.0-2.1.jar` from Maven Central; `env.add_jars("file:///...")` |
| `NoClassDefFoundError: org/apache/kafka/clients/consumer/OffsetResetStrategy` | Connector found, but its **transitive dependency** `kafka-clients` is missing (the ~418 KB connector JAR doesn't bundle it) | Also download `kafka-clients-4.1.0.jar` (the version the connector's Maven metadata requires) and add it to `add_jars` |

Don't keep downloading JARs blindly. If a third `NoClassDefFoundError` appears, inspect the connector's Maven dependency tree, or use the **`flink-sql-connector-kafka`** "fat" JAR, which bundles `kafka-clients` in one file.

**4. Check the connector/version matrix before choosing a version.** At the time of class, **Flink 2.3 had no released Kafka connector**, so the demo moved to **Flink 2.1** + `flink-connector-kafka 5.0.0-2.1`. Connector versions are named `<connector version>-<Flink version>`.

This is the same lesson as Spark: the connector must match the **engine's** version (Spark 3.5.1 / Scala 2.13 → `spark-sql-kafka-0-10_2.13:3.5.1`), not the Kafka broker's version.

> Note for this machine: `flink-practice/.venv` has **PyFlink 2.3.0** (installed during class). To follow the Kafka demo, it would need `pip install apache-flink==2.1.0` plus the two JARs above.

---

## Troubleshooting Log (Sep 30)

| Error | Cause | Fix |
|---|---|---|
| `No readable meta.properties files found` (after a reboot) | KRaft storage directory emptied, probably `/tmp` being cleared | `kafka-storage.sh random-uuid` → `format --standalone` → start; recreate topics |
| `docker start mongodb` → `bind: address already in use` | Another process holds 27017 | `sudo lsof -nP -iTCP:27017 -sTCP:LISTEN` → identify it before deleting anything |
| `Conflict. The container name "/mongodb" is already in use` | A stopped container with that name exists | `docker start mongodb` (keeps its data) or `docker rm mongodb` first |
| `Failed to find data source: kafka` | Consumer started with `python` instead of `spark-submit --packages` | Use `spark-submit --packages ...` (or `spark.jars.packages` in code) |
| `UnknownTopicOrPartitionException` | Most likely running the old `consumer.py` (subscribes to the now-deleted `test-topic`) | Run the right file; confirm the topic name with `grep -n subscribe *.py` |
| `Command 'flink' not found` | PyFlink doesn't install the CLI | Run jobs with `python`, or install the Flink binary distribution |
| pip dependency conflicts after `pip install apache-flink` | Installed into a shared Python environment | A dedicated venv for Flink |
| `Could not found the Java class ...KafkaSource.builder` | Flink Kafka connector JAR missing | `env.add_jars("file:///.../flink-connector-kafka-5.0.0-2.1.jar")` |
| `NoClassDefFoundError: .../OffsetResetStrategy` | `kafka-clients` JAR missing | Add `kafka-clients-4.1.0.jar` too |

---

# Market Data Demo: Measuring Micro-Batch Latency

Teacher-shared code (Evan Flint, pasted in class). The indentation was lost in the paste and has been restored here. Goal: replace the slow weather feed (Open-Meteo only updates every 15 minutes) with a **fast synthetic stock-tick feed** and **measure** how long each record waits in Spark's micro-batches, instead of just describing it.

```text
FastAPI /tick  ─►  producer (adds kafka_ts)  ─►  Kafka topic market_ticks  ─►  Spark (2-sec micro-batches)  ─►  /tmp/spark-market.jsonl  ─►  dashboard
 exchange_ts        api_ts / kafka_ts                kafka_broker_ts               processed_ts
```

## 1. Synthetic Market Data API (FastAPI)

```python
import random
import time
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(title="Synthetic Market Data API")

prices = {
    "AAPL": 225.00,
    "MSFT": 430.00,
    "NVDA": 185.00,
    "AMZN": 220.00,
    "GOOG": 195.00,
    "META": 710.00
}

sequence = 0

def timestamp():
    return datetime.now(timezone.utc).isoformat()

@app.get("/tick")
def get_tick():

    global sequence

    sequence += 1

    symbol = random.choice(list(prices))

    # Random-walk price movement
    change = random.gauss(0, 0.04)

    prices[symbol] = max(
        1,
        prices[symbol] + change
    )

    # Simulate a small amount of exchange/network jitter
    network_delay_ms = random.randint(1, 8)

    exchange_ts = timestamp()

    time.sleep(network_delay_ms / 1000)

    return {
        "sequence": sequence,
        "symbol": symbol,
        "price": round(prices[symbol], 2),
        "size": random.choice([
            100, 100, 100,
            200, 500, 1000
        ]),
        "side": random.choice([
            "BUY",
            "SELL"
        ]),
        "exchange_ts": exchange_ts,
        "api_ts": timestamp(),
        "simulated_network_ms": network_delay_ms
    }
```

Expanded:
- **FastAPI** turns a Python function into a web API: `@app.get("/tick")` means an HTTP GET to `/tick` runs `get_tick()` and returns its dict as JSON. Run it with a server such as `uvicorn market_api:app --port 8000` (the file name and port are whatever you choose), then `curl http://localhost:8000/tick`.
- **Random walk:** each tick nudges one stock's price by `random.gauss(0, 0.04)`, a small normally-distributed change averaging 0 with a standard deviation of 4 cents, so prices drift realistically instead of jumping randomly. `max(1, ...)` keeps prices from going below $1.
- **`sequence`** is a global counter that increments on every tick, giving each event a unique, ordered ID. It's how you check that nothing was lost or reordered downstream, and how the Spark output shows which ticks landed in which batch.
- **`size`** is weighted by repetition: 100 appears three times in the list, so half of all trades are 100 shares.
- **Two timestamps with a simulated delay between them:** `exchange_ts` (when the "exchange" created the trade) → a 1–8 ms `time.sleep` (fake network jitter) → `api_ts` (when the API returned it). `simulated_network_ms` records the delay so it can be checked against the timestamps.
- All timestamps are **UTC ISO-8601** strings (`datetime.now(timezone.utc).isoformat()`), so they compare correctly across machines and time zones.

## 2. Kafka Topic

```bash
bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic market_ticks \
  --partitions 1 \
  --replication-factor 1
```

**One partition** means **one total order** for every tick: Kafka only guarantees ordering within a partition, so a single partition keeps `sequence` strictly in order end to end. The trade-off is no parallelism, which is fine for a demo. A real market feed would use several partitions keyed by `symbol`, keeping order per stock (see "Kafka Message Keys" in `Training 13.md`).

(The producer script that polls `/tick` and sends to Kafka wasn't in the pasted code. It came later in the ChatGPT session; see "The Producer: Pacing to a Target Rate" below. It adds a **`kafka_ts`** field just before `producer.send(...)`, which the Spark schema expects.)

## 3. Spark Consumer: `market_consumer_spark.py`

```python
import json
import os
import time
from datetime import datetime, timezone

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    to_timestamp,
    current_timestamp,
    lit,
    unix_millis
)
from pyspark.sql.types import (
    StructType,
    StructField,
    LongType,
    StringType,
    DoubleType,
    IntegerType
)

# ============================================================
# Configuration
# ============================================================

KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC = "market_ticks"

OUTPUT_FILE = "/tmp/spark-market.jsonl"
CHECKPOINT_DIR = "/tmp/spark-market-checkpoint"

# Deliberately large enough that students can SEE microbatches.
TRIGGER_INTERVAL = "2 seconds"

# ============================================================
# Spark
# ============================================================

spark = (
    SparkSession.builder
    .master("local[*]")
    .appName("Spark Market Streaming Demo")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

# ============================================================
# Input schema
# ============================================================

schema = StructType([
    StructField("sequence", LongType(), True),
    StructField("symbol", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("size", IntegerType(), True),
    StructField("side", StringType(), True),

    StructField("exchange_ts", StringType(), True),
    StructField("api_ts", StringType(), True),
    StructField("kafka_ts", StringType(), True),

    StructField("simulated_network_ms", IntegerType(), True)
])

# ============================================================
# Kafka source
# ============================================================

raw = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
    .option("subscribe", KAFKA_TOPIC)
    .option("startingOffsets", "latest")
    .load()
)

# ============================================================
# Parse Kafka JSON
# ============================================================

ticks = (
    raw
    .select(
        col("partition").alias("kafka_partition"),
        col("offset").alias("kafka_offset"),
        col("timestamp").alias("kafka_broker_ts"),
        col("value").cast("string").alias("json")
    )
    .withColumn("data", from_json(col("json"), schema))
    .select(
        "kafka_partition",
        "kafka_offset",
        "kafka_broker_ts",
        "data.*"
    )
)

# ============================================================
# Microbatch processing
# ============================================================

def process_batch(batch_df, batch_id):

    if batch_df.isEmpty():
        return

    # --------------------------------------------------------
    # ONE timestamp is deliberately assigned to this batch.
    #
    # This makes the microbatch behavior obvious in the
    # dashboard: many records will acquire approximately the
    # same processing timestamp.
    # --------------------------------------------------------

    batch_processed_ts = datetime.now(timezone.utc)

    processed = (
        batch_df
        .withColumn("processed_ts", lit(batch_processed_ts))
        .withColumn("engine", lit("spark"))
        .withColumn("batch_id", lit(int(batch_id)))
        .withColumn("exchange_timestamp", to_timestamp("exchange_ts"))
        .withColumn("kafka_timestamp", to_timestamp("kafka_ts"))
        .withColumn(
            "processing_latency_ms",
            unix_millis(col("processed_ts"))
            - unix_millis(col("kafka_timestamp"))
        )
        .withColumn(
            "end_to_end_latency_ms",
            unix_millis(col("processed_ts"))
            - unix_millis(col("exchange_timestamp"))
        )
    )

    # Sort only for human-readable demo output.
    rows = (
        processed
        .orderBy("sequence")
        .collect()
    )

    # --------------------------------------------------------
    # Append this microbatch to the dashboard feed
    # --------------------------------------------------------

    with open(OUTPUT_FILE, "a", buffering=1) as f:

        for row in rows:

            record = row.asDict()

            # Convert Spark/Python datetime objects to strings.
            for field in [
                "kafka_broker_ts",
                "processed_ts",
                "exchange_timestamp",
                "kafka_timestamp"
            ]:
                if record.get(field) is not None:
                    record[field] = record[field].isoformat()

            f.write(json.dumps(record, default=str) + "\n")

    count = len(rows)

    if count:

        first_sequence = rows[0]["sequence"]
        last_sequence = rows[-1]["sequence"]

        print(
            f"\n"
            f"SPARK MICRO-BATCH {batch_id}\n"
            f"Records: {count}\n"
            f"Sequence: {first_sequence} -> {last_sequence}\n"
            f"Processed: {batch_processed_ts.isoformat()}\n"
        )

# ============================================================
# Start streaming
# ============================================================

print()
print("=" * 60)
print("SPARK STRUCTURED STREAMING")
print("=" * 60)
print()
print(f"Kafka topic: {KAFKA_TOPIC}")
print(f"Trigger: {TRIGGER_INTERVAL}")
print(f"Output: {OUTPUT_FILE}")
print()
print("Watch for groups of records appearing every 2 seconds.")
print()

query = (
    ticks.writeStream
    .foreachBatch(process_batch)
    .option("checkpointLocation", CHECKPOINT_DIR)
    .trigger(processingTime=TRIGGER_INTERVAL)
    .start()
)

query.awaitTermination()
```

Run it the same way as the weather consumer (it needs only the Kafka connector):

```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1 market_consumer_spark.py
```

## What's New in This Code

**The timestamp chain.** Each record collects a timestamp at every stage, so you can see exactly where the time goes:

| Timestamp | Set by | Meaning |
|---|---|---|
| `exchange_ts` | API | The trade happened |
| `api_ts` | API | The API returned it (after the simulated 1–8 ms network delay) |
| `kafka_ts` | Producer | The producer sent it to Kafka |
| `kafka_broker_ts` | **Kafka itself** | Kafka's own record `timestamp` column, which the Kafka source always provides alongside key, value, partition and offset |
| `processed_ts` | Spark | The micro-batch that picked it up was processed |

| Latency column | Formula | What it shows |
|---|---|---|
| `processing_latency_ms` | `processed_ts − kafka_ts` | How long the record waited in Kafka and Spark. **Mostly the wait for the next 2-second trigger** |
| `end_to_end_latency_ms` | `processed_ts − exchange_ts` | Total time from trade to processed result |

`unix_millis(timestamp)` converts a timestamp to milliseconds since 1970, so subtracting two of them gives a difference in milliseconds.

**One `processed_ts` per batch, on purpose.** `datetime.now()` is called **once** per micro-batch in the Python driver and stamped onto every row with `lit()`. With ticks arriving continuously and a 2-second trigger, a record that arrives just after a batch starts waits almost 2 seconds, and one that arrives just before waits only a few milliseconds. Latencies therefore form a **sawtooth pattern from ~0 to ~2000 ms**, and every record in a batch shares one `processed_ts`. That's the visual proof of micro-batching. A record-at-a-time engine like Flink would show roughly constant, low latency per record.

(Built-in `current_timestamp()`, used in the weather consumer, also evaluates **once per micro-batch** in Structured Streaming, so it would show the same effect. The explicit Python timestamp just makes the point obvious and also works for the printed log.)

**`foreachBatch` with a custom Python sink.** Here `foreachBatch` isn't only a connector workaround; it runs **arbitrary Python per batch**: check `batch_df.isEmpty()` to skip empty batches, add batch-level columns (`batch_id`, `engine`), then write JSON Lines to a file the dashboard reads. The console log shows the batch structure directly:

```text
SPARK MICRO-BATCH 12
Records: 38
Sequence: 1041 -> 1078
Processed: 2026-09-30T19:42:10.004+00:00
```

**Demo-only choices (fine for class, not for production):**
- `.collect()` pulls the whole batch to the driver. That's OK for a few dozen ticks every 2 seconds, but at production volume it would run the driver out of memory; you'd write with a distributed sink instead.
- `orderBy("sequence")` is only there for readable output.
- Appending to a local file isn't exactly-once: if the job restarts, a batch can be written twice. A production sink would be idempotent (for example, an upsert keyed on `sequence`).
- `open(..., buffering=1)` is **line-buffered**, so each record is flushed to disk right away and the dashboard sees it immediately.
- `json.dumps(record, default=str)` turns any remaining non-JSON types (like datetimes) into strings instead of crashing.
- `import os`, `import time` and `current_timestamp` are imported but unused.

---

# Market Data Lab: Spark vs. Flink on One Dashboard (ChatGPT session, Sep 30, 3:07–3:51 PM)

Continuation of the teacher's ChatGPT session (same shared link, re-shared after class). These are ChatGPT's explanations and code that Evan worked through, **not** Evan's own definitions. Goal, in Evan's words to ChatGPT: *"simulate a high-speed stock trading application - we want the data to come in many times per second, and to be processed by each of our data processing systems using their respective engines, and the dashboards should be able to reflect the difference in processing things individually … vs processing them in microbatches"*. The weather feed (updates every 15 min) was too slow to show the difference.

```text
                Synthetic Market REST API (FastAPI, /tick)
                          ~50 ticks/sec
                               │
                               ▼
                    Kafka: market_ticks (1 partition)
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
     Spark Structured Streaming        Flink DataStream (PyFlink)
        2-second micro-batches         record-at-a-time map()
                 │                           │
     /tmp/spark-market.jsonl         /tmp/flink-market.jsonl
                 └─────────────┬─────────────┘
                               ▼
               ONE Streamlit dashboard (market_dashboard.py, port 8503)
```

## Flink Binary: Scala 2.12 Is Fine

Evan tried to download `flink-2.1.0-bin-scala_2.13.tgz` to match his Scala 2.13 system and got a **404**: there is **no official Flink 2.1 build for Scala 2.13**. The system's Scala version doesn't matter here:

- A **Flink distribution bundles its own Scala libraries**; it never uses the system `scala` command. Spark 3.5.1 (Scala 2.13) and Flink 2.1.0 (Scala 2.12) coexist fine on one machine.
- Scala versions **do** matter for **libraries loaded into an engine**. `spark-sql-kafka-0-10_2.12` inside a Scala 2.13 Spark breaks with `NoSuchMethodError`, because the `_2.12` suffix means the JAR was compiled against Scala 2.12. For Flink, match the **connector** to the Flink version (`5.0.0-2.1`), not to the system Scala.
- PyFlink jobs are written in Python, so no Scala code is compiled.
- `wget -c <url>` **resumes** a partial download. Evan had 455 of 539 MB when he pressed Ctrl+C.

## The Producer: Pacing to a Target Rate

```python
import json
import time
from datetime import datetime, timezone

import requests
from kafka import KafkaProducer

API = "http://localhost:8000/tick"
TICKS_PER_SECOND = 50
INTERVAL = 1 / TICKS_PER_SECOND

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    key_serializer=lambda k: k.encode("utf-8"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

session = requests.Session()

def timestamp():
    return datetime.now(timezone.utc).isoformat()

print(f"Producing approximately {TICKS_PER_SECOND} market ticks/sec")

while True:
    start = time.perf_counter()
    try:
        response = session.get(API, timeout=1)
        response.raise_for_status()
        tick = response.json()
        tick["kafka_ts"] = timestamp()
        producer.send("market_ticks", key=tick["symbol"], value=tick)
    except Exception as e:
        print(f"Producer error: {e}")

    elapsed = time.perf_counter() - start
    sleep_time = INTERVAL - elapsed
    if sleep_time > 0:
        time.sleep(sleep_time)
```

- **Fixed-rate loop:** measure how long the work took (`time.perf_counter()`, a high-precision timer) and sleep only for the rest of the 20 ms interval. A plain `sleep(0.02)` would run slower than 50/sec, because the HTTP call takes time too.
- **`requests.Session()`** reuses one HTTP connection instead of opening a new one per tick, which matters at 50 calls/sec.
- `kafka_ts` is stamped just before `send()`; it's the "arrived at Kafka" time the consumers measure latency from.
- 50/sec = 3,000/min = 180,000/hour. ChatGPT suggested raising it to ~100/sec to make Spark's bursts bigger (~200 records per 2-second batch).

## The Flink Consumer: `flink_market_consumer.py` (first version)

The Spark consumer is the one already in these notes (`market_consumer_spark.py`, called `spark_market_consumer.py` in the session). The Flink counterpart writes **each event individually**:

```python
class ProcessMarketTick(MapFunction):

    def open(self, runtime_context):
        # Runs once when the operator starts: open the output file.
        self.output = open(OUTPUT_FILE, "a", buffering=1)
        self.counter = 0

    def map(self, value):
        # Runs once PER EVENT.
        processed_time = timestamp()
        tick = json.loads(value)
        kafka_time = parse_timestamp(tick.get("kafka_ts"))
        exchange_time = parse_timestamp(tick.get("exchange_ts"))

        processing_latency_ms = round((processed_time - kafka_time).total_seconds() * 1000, 3)
        end_to_end_latency_ms = round((processed_time - exchange_time).total_seconds() * 1000, 3)

        tick["processed_ts"] = processed_time.isoformat()
        tick["engine"] = "flink"
        tick["batch_id"] = None          # no micro-batches in Flink
        tick["processing_latency_ms"] = processing_latency_ms
        tick["end_to_end_latency_ms"] = end_to_end_latency_ms

        self.output.write(json.dumps(tick) + "\n")
        self.output.flush()
        self.counter += 1
        if self.counter % 100 == 0:       # don't print every event
            print(f"FLINK processed {self.counter} events | seq={tick.get('sequence')} | latency={processing_latency_ms} ms")
        return json.dumps(tick)

    def close(self):
        # Runs once when the operator shuts down.
        if self.output:
            self.output.close()

env = StreamExecutionEnvironment.get_execution_environment()
env.set_runtime_mode(RuntimeExecutionMode.STREAMING)
env.set_parallelism(1)
env.add_jars(FLINK_KAFKA_JAR, KAFKA_CLIENT_JAR)   # connector 5.0.0-2.1 + kafka-clients 4.1.0

source = KafkaSource.builder() \
    .set_bootstrap_servers("localhost:9092").set_topics("market_ticks") \
    .set_group_id("flink-market-demo") \
    .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
    .set_value_only_deserializer(SimpleStringSchema()).build()

stream = env.from_source(source, WatermarkStrategy.no_watermarks(), "Market Kafka Source")
stream.map(ProcessMarketTick(), output_type=Types.STRING()).print()
env.execute("Flink Market Streaming Demo")
```

New ideas compared with the weather Flink job:
- **A `MapFunction` class with a lifecycle:** `open()` runs once at startup (set up resources such as files or connections), `map()` runs once per record, and `close()` runs once at shutdown. That's better than reopening the file for every record, as the weather version did.
- `set_runtime_mode(RuntimeExecutionMode.STREAMING)` makes it explicit that this is an unbounded stream (Flink can also run jobs in BATCH mode).
- `batch_id = None` for Flink versus `0, 1, 2…` for Spark. That one column shows the difference in the output tables.
- Spark and Flink use **different consumer groups** (Spark tracks its own offsets in its checkpoint; Flink uses `flink-market-demo`), so both receive **every** tick independently.
- Both outputs share one schema (`sequence, symbol, price, …, processed_ts, engine, batch_id, processing_latency_ms`), so one dashboard can read both files and **join them on `sequence`**: the *same trade* through two engines.

## The Dashboard: Four Iterations and What Each Taught

Evan asked for **one** Streamlit dashboard reading both JSONL files. It took several full rewrites:

| Iteration | Problem Evan saw | Diagnosis | Change |
|---|---|---|---|
| 1. Scatter plot, sequence vs. `processed_ts` | "The visuals are not obvious". He expected a live price chart | The JSONL files held **~3 hours of old events**, so the x-axis spanned hours and current activity was a sliver | Chart only a **recent window** (last 30 s) |
| 2. Live price chart on top | Six stocks at $185–$710 look **flat** on one y-axis | Absolute prices on one axis hide small moves | **Normalize**: plot % change from the start of the window (`price / first_price − 1) × 100`), so every stock starts at 0% |
| 3. 10-second "processing monitor", events per 100 ms bucket | Spark's panel **blank** ("Spark active time buckets: 0%") | Both engines' windows were anchored to **Flink's newest timestamp**; Spark's latest batch was older, so it fell outside the window | Anchor each engine's window to **its own** newest `processed_ts` |
| 4. Per-engine windows | "Now they look identical - there should be a difference!!!!" | Both files really had ~100 records sharing one `processed_ts` every ~2 s. **The dashboard was correct; the Flink data was bunched** | See next section |

Lessons:
- **When a chart looks wrong, check the data before the chart code.** Iteration 4 proved the visualization was faithfully showing what the consumers wrote.
- Live dashboards need **rolling windows**; old data squashes the axis.
- Put different-scale series on one chart by **normalizing** them.
- The dashboard refreshed every **250 ms** (`@st.fragment(run_every="250ms")`) and read only the last 15,000 lines of each file, to stay fast.
- Evan wanted complete replacement files ("I'm not trying to teach how to do the nuances of streamlit"). Streamlit reloads a changed file automatically, so nothing else had to restart.

## Why Flink Looked Micro-Batched, and the Final "Fix"

**Cause (ChatGPT's explanation):** in PyFlink, a Python `map()` doesn't run inside Flink's Java engine. Flink's JVM sends records to a separate **Python worker process in bundles** and the results come back in bundles. So `datetime.now()` inside `map()` records when the Python worker received the *bundle*, and ~100 records got nearly the same timestamp. That's an artifact of the **Python bridge**, not of Flink's streaming model.

**ChatGPT's replacement Flink consumer** stopped measuring: it sets Flink's `processed_ts` to the record's **Kafka timestamp plus a fixed, simulated 5 ms** (`simulated_processing_ms = 5`). ChatGPT called this an "educational representation." The dashboard then showed a smooth Flink line against Spark's 2-second spikes.

> **Critical note (my analysis, not from class):** after that change the comparison is no longer an experiment. Spark's timing is *measured* (its real `foreachBatch` boundary); Flink's is *computed from a formula* that guarantees a smooth line. The chart shows the idea correctly, since Flink is designed for record-at-a-time processing, but it doesn't prove it from this pipeline's data. If this comes up in class, that's a fair point to raise.
>
> A way to test the real behavior: PyFlink's bundling is configurable, with `python.fn-execution.bundle.size` (records per bundle) and `python.fn-execution.bundle.time` (max milliseconds before a bundle is sent). Setting them very low (for example size 1, time 1 ms) should make the Python `map()` see records nearly one at a time, trading throughput for latency. The class didn't try this; it's untested here.
>
> ```python
> from pyflink.common import Configuration
> config = Configuration()
> config.set_string("python.fn-execution.bundle.size", "1")
> config.set_string("python.fn-execution.bundle.time", "1")
> env = StreamExecutionEnvironment.get_execution_environment(config)
> ```
>
> Other honest alternatives: timestamp inside the **JVM** (for example Flink SQL with `PROCTIME()`, whose operators don't cross into Python), or label the Flink panel "simulated" on the dashboard.

## Quant Perspective (from the dashboard's explainer text)

The dashboard included an expander, "Why does latency matter to a trading system?":
- `exchange_ts` → `kafka_ts` represents exchange, network, serialization and transport delay before the pipeline sees the event.
- After Kafka, the engine's processing model adds more delay: Flink reacts per event; Spark with a 2-second trigger makes the **oldest record in a batch wait almost the full 2 seconds** while the newest barely waits.
- For a latency-sensitive strategy, the price may have **already changed again** before an older event is processed. ChatGPT's suggested extension: have each engine compute a simple signal (price above or below its rolling average → SELL/BUY) and show that, for a moment, **Spark and Flink "believe" different prices** despite reading the same Kafka stream.
- ChatGPT's own caveats: this exaggerates effects to make them visible at human scale. Real trading systems don't put a REST API or Streamlit in the tick path, and it's **not a benchmark** of either engine. **"Flink = fast, Spark = slow" is the wrong lesson**; Spark can use much shorter triggers, and Flink has its own buffering.

## Running It (class setup: five terminals)

| Terminal | Command |
|---|---|
| 1. API | `uvicorn market_api:app --host 127.0.0.1 --port 8000` (interactive docs: `http://localhost:8000/docs`) |
| 2. Producer | `python market_producer.py` |
| 3. Spark | `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1 spark_market_consumer.py` |
| 4. Flink | `source ~/venvs/flink-demo/bin/activate && python flink_market_consumer.py` |
| 5. Dashboard | `streamlit run market_dashboard.py --server.port 8503` |

Clear old output first (`rm -f /tmp/spark-market.jsonl /tmp/flink-market.jsonl; rm -rf /tmp/spark-market-checkpoint`), because old records caused the "squashed chart" problem.
