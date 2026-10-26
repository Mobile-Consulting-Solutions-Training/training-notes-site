---
title: Training 7 - Spark Submit, Architecture & Execution
description: spark-submit arguments and deploy modes, Spark's driver/executor architecture, Catalyst/AQE, jobs/stages/tasks, narrow vs. wide transformations, lazy evaluation, data skew/salting, caching/broadcast joins, and the JVM.
sidebar:
  order: 7
---

Teacher: Evan Flint

Syllabus Day 8 (per file numbering) - actual coverage: `spark-submit` CLI arguments and Spark deployment configuration. Note: this continues the pacing drift already visible in `Training 6.md` (which itself covered content closer to the roadmap's Day 8 topic) - this session's content lines up with the roadmap's Day 9/10 territory ("Hive + Spark Intro" / "Spark Advanced") rather than its own nominal Day 8 slot.

---

# Spark Submit

## Video Resources

| Topic | Title | Channel | Link |
|---|---|---|---|
| AQE | Advancing Spark - Crazy Performance with Spark 3 Adaptive Query Execution | Advancing Analytics | https://www.youtube.com/watch?v=jlr8_RpAGuU&t=919s |
| Data Skew | Why Data Skew Will Ruin Your Spark Performance | Afaque Ahmad | https://www.youtube.com/watch?v=9Ss-_y7njKE |
| Salting | How Salting Can Reduce Data Skew By 99% | Afaque Ahmad | https://www.youtube.com/watch?v=rZGsc5y8AQk |
| Data Skew | Spark Data Skew Explained: Why One Task Becomes the Bottleneck | Under the Hood Data | https://www.youtube.com/watch?v=_UgFq0VK5YI |
| Coalesce/Repartition | Spark - Repartition Or Coalesce | Data Engineering | https://www.youtube.com/watch?v=ijD5zuEV8U8 |
| Broadcast Join | What is Broadcast Join in spark? \| Spark Optimization \| IN 3 MINUTES | Quick Tech Bits | https://www.youtube.com/watch?v=cFZPC9DYgOg |
| Broadcast Join | Joins in Databricks: Broadcast Join vs Shuffle Join Explained | Alberto Gaytan | https://www.youtube.com/watch?v=UIBQDj_vbTc |
| Broadcast Join | Your Spark Join Strategy is Wrong (Here's Why) | Chris Gambill \| Data Engineering Strategy | https://www.youtube.com/watch?v=7KafXl7N-CY |
| Cache/Persist | Cache, Persist & StorageLevels In Apache Spark | Afaque Ahmad | https://www.youtube.com/watch?v=FujwRYkBwM4 |
| Cache/Persist | Caching and Persisting Data for Performance in Azure Databricks | Advancing Analytics | https://www.youtube.com/watch?v=6MVppeGiftg |
| spark-submit + Airflow | How to Submit a PySpark Script to a Spark Cluster Using Airflow! | The Data and AI Guy | https://www.youtube.com/watch?v=ZerBdBHPusA |

---

Q. What is `spark-submit`, and how should its many arguments be learned?

A. (Teacher's definition) spark-submit accepts a large number of arguments. The most useful way to learn them is by category.

Expanded: `spark-submit` is the command-line tool used to launch a Spark application (Python, Scala, or Java) onto a cluster - it's the single entry point that bundles together where the job runs (`--master`), how much compute it gets (memory/cores/executors), what dependencies it needs (jars/files/packages), and any custom configuration (`--conf`). Rather than memorizing every flag individually, it's more useful to group them by what they control: core submission behavior, driver/executor resources, dependency distribution, generic `spark.*` configuration via `--conf`, cluster-manager-specific flags, and finally the application's own arguments. The categories below follow that grouping.

You can always see the exact arguments supported by the Spark version installed on a machine with:

```bash
spark-submit --help
```

---

## Core Arguments

| Argument | Purpose | Example |
|---|---|---|
| `--master` | Cluster manager / execution target | `--master yarn` |
| `--deploy-mode` | Where the driver runs: `client` or `cluster` | `--deploy-mode cluster` |
| `--class` | Main class for Java/Scala applications | `--class com.example.Main` |
| `--name` | Application name | `--name CustomerETL` |
| `--conf` | Set any Spark configuration property | `--conf spark.executor.memory=8g` |
| `--properties-file` | Load Spark properties from a file | `--properties-file spark.conf` |
| `--verbose` | Show detailed submission information | `--verbose` |

Expanded: these are the arguments that describe *how and where* the job is submitted, independent of the job's own logic. `--master` and `--deploy-mode` together decide the execution target and where the driver process lives (see the dedicated Deploy Mode section below); `--class` is only needed for compiled Java/Scala apps (a `.py` file doesn't need a main class); `--conf` is the escape hatch that exposes the much larger world of `spark.*` properties without needing a dedicated flag for each one.

---

## Driver and Executor Resources

| Argument | Purpose | Example |
|---|---|---|
| `--driver-memory` | Memory allocated to driver | `--driver-memory 4g` |
| `--driver-java-options` | Extra JVM options for driver | `--driver-java-options "-Xlog:gc"` |
| `--driver-library-path` | Extra native library path | `--driver-library-path /opt/lib` |
| `--driver-class-path` | Extra driver classpath | `--driver-class-path mylib.jar` |
| `--executor-memory` | Memory per executor | `--executor-memory 8g` |
| `--executor-cores` | CPU cores per executor | `--executor-cores 4` |
| `--total-executor-cores` | Total executor cores; mainly standalone/Mesos | `--total-executor-cores 20` |
| `--num-executors` | Number of executors; commonly YARN | `--num-executors 10` |

Expanded: these control the actual compute shape of the job. Driver settings size the coordinating process (which builds the DAG and collects results); executor settings size the worker processes that actually run tasks. `--num-executors` is YARN's way of saying "how many workers," while `--total-executor-cores` is the standalone/Mesos equivalent of the same idea expressed as a total core budget instead of a worker count - worth remembering that these two are largely interchangeable concepts across cluster managers, not two unrelated settings.

---

Q. What is `--driver-memory`?

A. (Teacher's definition) Driver memory is like executor memory, but it's for the driver application.

Expanded: same concept as `--executor-memory`, just applied to the single driver process instead of the (potentially many) executor processes - it's the RAM available to the process that builds the DAG, schedules tasks, and (importantly) collects results back from executors, e.g. via `.collect()`. Since there's only ever one driver per job (unlike executors, which can number in the dozens), sizing this is less about cluster-wide throughput and more about making sure the driver doesn't run out of memory when it has to hold a large collected result set or a very large execution plan in memory.

---

Q. What does `--num-executors` control?

A. (Teacher's definition) The number of executors which will be used in the job, distributed across the nodes.

Expanded: this is the total count of executor *processes* Spark will launch for the job - and per the Worker vs Executor section above, those executors get spread across the cluster's worker nodes, with a given worker commonly hosting several of them rather than just one.

---

Q. What does `--executor-memory` control?

A. (Teacher's definition) The amount of memory (RAM) which is allocated to each executor.

Expanded: this is a *per-executor* setting, not a per-worker or per-job total - each executor process gets this much RAM to hold cached data and run its assigned tasks. Since a worker often hosts multiple executors at once (per the cardinality point above), the actual RAM a single worker machine needs to support is roughly `(executors on that worker) x --executor-memory` - undersizing this per-executor value risks out-of-memory task failures, while oversizing it wastes RAM that could've gone to running more executors in parallel.

---

Q. What does `--executor-cores` control?

A. (Teacher's definition) The number of CPU cores that each of the executors is using to process its share of the data.

Expanded: like `--executor-memory`, this is sized *per executor*, not per worker - each executor process gets this many CPU cores to run its tasks in parallel (Spark runs one task per core concurrently within an executor). Together, `--num-executors`, `--executor-memory`, and `--executor-cores` are the three knobs that jointly define a job's total compute footprint across the cluster.

Example:

```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --name CustomerETL \
  --driver-memory 4g \
  --executor-memory 8g \
  --executor-cores 4 \
  --num-executors 10 \
  job.py
```

---

## Determining Executor Sizing (`--num-executors`, `--executor-cores`, `--executor-memory`)

Q. How do you determine the settings for cores per executor, `--num-executors`, and `--executor-memory`?

A. (Teacher's definition) First, take stock of the basics of the hardware:
- How many nodes do you have?
- How many CPU cores does each node's processor have?
- How much RAM does each node have?

Expanded: before picking numbers for these three settings, the starting point is always the physical ceiling of the cluster itself - you can't allocate more cores/RAM across all your executors than the hardware actually has. This is the first step of a sizing methodology (continues in this section as more is covered) that turns raw hardware specs (node count x cores/node x RAM/node) into concrete `--num-executors` / `--executor-cores` / `--executor-memory` values, generally leaving some cores/RAM per node reserved for the OS and (on YARN) the NodeManager/ApplicationMaster daemons rather than allocating 100% of a node's hardware to executors.

---

Q. In a standard situation with identical nodes, how do you calculate `--executor-cores`?

A. (Teacher's definition) In a standard situation, with identical nodes, the way that you calculate these numbers is to start with the number of CPU cores per node, then divide that by 5 - this will give you the number of cores per executor.

Expanded: the "5" here is itself the target `--executor-cores` value (a well-known Spark tuning rule of thumb, not arbitrary) - it caps each executor at around 5 concurrent tasks/threads, which is roughly the point past which HDFS client throughput and JVM garbage-collection behavior start to degrade if a single executor is given too many cores at once. Dividing a node's total cores *by* that fixed 5 doesn't recompute `--executor-cores` itself - it gives the **number of executors that fit on one node** (confirmed by the worked example below, where `36 / 5 = 7 executors`, not "7 cores per executor"). So the full picture is: `--executor-cores` = 5 (fixed starting point), and `executors per node` = `cores per node / 5`.

---

Q. Once you know the number of executors per node, how do you calculate `--executor-memory`?

A. (Teacher's definition) Once you have the number of executors for the node, you divide the amount of memory by the number of executors, and that will give you a figure for executor-memory.

Expanded: `--executor-memory` = `RAM per node / executors per node`. This is the same "divide the node's total resource by how many executors share the node" logic used for cores, just applied to RAM instead - each executor on a node gets an equal slice of that node's total memory.

---

Q. Worked example: how would you size executors for 10 nodes x 36 cores x 64 GB RAM?

A. (Teacher's definition) So the process is this for an average case (10 nodes, 36 cores per node, 64 GB memory per node): 36 / 5 = 7 executors, with a remainder of 1 core for system processes.

Expanded: `36 cores / 5 = 7.2`, rounded down to **7 executors per node** - the leftover fractional core (0.2, i.e. 1 whole core once you account for the rounding) is left unallocated to Spark and reserved for the node's own OS/system processes rather than assigned to an executor. This reserved-core pattern matches the general principle noted earlier in this section (leaving some hardware headroom for the OS/daemons rather than allocating 100% of a node to executors) - here it falls out naturally from the division/rounding rather than being a separate manual step.

A. (Teacher's definition) 64/7 = 9.14 - round that down to 9 for a number to pass to spark-submit, and leave the rest for the node's system processes.

Expanded: continuing the same worked example, `64 GB / 7 executors = 9.14 GB`, rounded down to **`--executor-memory 9g`**. Just like the cores calculation, the leftover fraction (0.14 x 7 executors ≈ 1 GB) is left unallocated to Spark and reserved for the node's OS/system processes rather than assigned to an executor - the same "round down, leave the remainder for the system" pattern applies to both cores and memory.

| Step | Calculation | Result |
|---|---|---|
| Cores per node | given | 36 |
| `--executor-cores` (fixed rule of thumb) | - | 5 |
| Executors per node | 36 / 5, rounded down | 7 |
| Cores reserved for OS/system | 36 - (7 x 5) | 1 |
| RAM per node | given | 64 GB |
| `--executor-memory` | 64 GB / 7, rounded down | 9g |
| RAM reserved for OS/system | 64 - (7 x 9) | ~1 GB |

For the full cluster (10 nodes x 7 executors/node), the teacher's numbers give `--num-executors 70 --executor-cores 5 --executor-memory 9g`.

Expanded (correction): the teacher's method is the right shape, but it leaves out two things, and with them the numbers above don't actually fit on the nodes.
1. **Memory overhead.** Each executor container on YARN/Kubernetes asks for `--executor-memory` **plus** `spark.executor.memoryOverhead`, which defaults to `max(384 MB, 10% of executor memory)`. 7 executors x (9 GB + ~0.9 GB) = ~69 GB, which is more than the 64 GB node has.
2. **The ApplicationMaster.** On YARN, one container is used by the ApplicationMaster (in cluster mode it also hosts the driver), so subtract one executor from the cluster total.

The standard version of the calculation:

| Step | Calculation | Result |
|---|---|---|
| Reserve per node for OS/daemons | 1 core + 1 GB | 35 cores, 63 GB usable |
| `--executor-cores` | rule of thumb | 5 |
| Executors per node | 35 / 5 | 7 |
| Memory per executor container | 63 GB / 7 | ~9 GB |
| Subtract ~10% memory overhead | 9 GB - ~0.9 GB | `--executor-memory` ~8g |
| `--num-executors` | 10 nodes x 7 - 1 (ApplicationMaster) | 69 |

Result: `--num-executors 69 --executor-cores 5 --executor-memory 8g`.

**Interview line:** "I reserve one core and about 1 GB per node for the OS, use about 5 cores per executor, divide the remaining memory by executors per node, take about 10% off for memory overhead, and subtract one executor for the YARN ApplicationMaster."

---

## Dependencies and Files

Q. Why does `spark-submit` need flags like `--jars` and `--packages` at all?

A. (Teacher's definition) Sometimes you need either jar files or other packages in order to run code.

Expanded: a Spark job's own logic often isn't self-contained - it may depend on third-party libraries (a JDBC driver, a cloud storage connector, a specific data format library) that aren't part of Spark's own bundled code and aren't already installed on the cluster's nodes. `--jars`/`--packages` (and PySpark's `--py-files`) exist to solve exactly that gap: they tell `spark-submit` to ship those extra dependencies out to the driver and every executor before the job starts, so the code that needs them can actually find them at runtime.

A. (Teacher's definition) For example, if you want to use Spark to process data written in XML format, or Avro, then you need external Java packages to do that, which are accessible either with the `--jars` flag or the `--packages` flag.

Expanded: Spark's built-in DataFrame reader only natively understands a certain set of formats out of the box (CSV, JSON, Parquet, ORC, plain text, etc.) - XML and Avro are **not** included in that built-in set, so reading/writing them requires an external connector library (e.g. `com.databricks:spark-xml` or `org.apache.spark:spark-avro`), supplied the same way any other JVM dependency is: either as a local JAR via `--jars`, or pulled automatically from Maven via `--packages`.

```bash
spark-submit \
  --packages org.apache.spark:spark-avro_2.12:3.5.0 \
  job.py
```

| Format | Built into Spark's DataFrame reader? | How to add support |
|---|---|---|
| CSV / JSON / Parquet / ORC | Yes | No extra dependency needed |
| Avro | No | `--packages org.apache.spark:spark-avro_2.12:<version>` |
| XML | No | `--packages com.databricks:spark-xml_2.12:<version>` (or `--jars` with a local copy) |

| Argument | Purpose | Example |
|---|---|---|
| `--jars` | Add JAR dependencies | `--jars postgresql.jar` |
| `--packages` | Download Maven dependencies | `--packages org.postgresql:postgresql:42.7.4` |
| `--exclude-packages` | Exclude conflicting Maven dependencies | `--exclude-packages group:artifact` |
| `--repositories` | Additional Maven repositories | `--repositories https://repo.example.com` |
| `--py-files` | Add Python `.py`, `.zip`, or `.egg` dependencies | `--py-files utils.zip` |
| `--files` | Distribute files to executors | `--files config.json` |
| `--archives` | Distribute and extract archives | `--archives environment.tar.gz#env` |

Expanded: this group is about getting code and data onto every executor, not just the driver's machine - Spark doesn't automatically ship anything beyond the main application file. For PySpark specifically, three of these matter most in practice:

```text
--py-files my_library.zip
--files config.yaml
--jars some_connector.jar
```

`--jars`/`--packages` solve the JVM-dependency problem (e.g. a JDBC driver like `postgresql.jar` needed even from PySpark, since the actual connection happens through the JVM); `--py-files` solves the Python-dependency problem; `--files`/`--archives` distribute arbitrary non-code assets (config files, Python environments) to every executor's working directory.

---

## Common Configuration Through `--conf`

Q. Why isn't there a dedicated `spark-submit` flag for every Spark setting?

A. (Teacher's definition) A huge amount of spark-submit configuration is actually passed through the generic `--conf` option. This means there isn't a separate spark-submit argument for every Spark setting. `--conf` gives you access to the much larger set of `spark.*` configuration properties.

Expanded: the named flags above (`--executor-memory`, `--num-executors`, etc.) are really just convenience shortcuts for the most commonly-used `spark.*` properties - `--conf` is the general-purpose mechanism underneath all of them, and it's how the vast majority of Spark's actual tuning surface (shuffle partitions, adaptive query execution, memory overhead, dynamic allocation, and hundreds of other properties) gets set at submit time.

```bash
spark-submit \
  --conf spark.sql.shuffle.partitions=400 \
  --conf spark.sql.adaptive.enabled=true \
  --conf spark.executor.memoryOverhead=2g \
  --conf spark.dynamicAllocation.enabled=true \
  job.py
```

| Property | Default | What it controls |
|---|---|---|
| `spark.sql.shuffle.partitions` | 200 | Number of partitions produced by every DataFrame/SQL shuffle (joins, `groupBy`). Too low = huge partitions that spill; too high = thousands of tiny tasks. With AQE on, Spark can coalesce small shuffle partitions after the fact |
| `spark.sql.adaptive.enabled` | `true` since Spark 3.2 | Turns on AQE (runtime re-planning: coalesce partitions, switch join strategy, split skewed join partitions) |
| `spark.executor.memoryOverhead` | `max(384 MB, 10% of executor memory)` | Extra non-heap memory per executor container (JVM overhead, Python workers, network buffers). Exceeding it gets the container killed by YARN/Kubernetes |
| `spark.dynamicAllocation.enabled` | `false` (on by default on EMR/Databricks) | Lets Spark add and remove executors based on pending tasks instead of a fixed `--num-executors` |

---

## Cluster-Manager-Specific Arguments

Q. Do all `spark-submit` arguments apply to every cluster manager?

A. (Teacher's definition) Some arguments only make sense with particular cluster managers.

Expanded: because `--master` can point at very different kinds of infrastructure (YARN, Spark Standalone, or Kubernetes), each cluster manager exposes its own extra flags/conventions layered on top of the core arguments above.

**YARN:**

| Argument | Purpose |
|---|---|
| `--queue` | YARN queue to submit the job into |
| `--num-executors` | Number of executors |
| `--principal` | Kerberos principal (secured clusters) |
| `--keytab` | Kerberos keytab file (secured clusters) |

```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --queue analytics \
  --num-executors 20 \
  --executor-cores 4 \
  --executor-memory 8g \
  job.py
```

**Spark Standalone:**

| Argument | Purpose |
|---|---|
| `--master spark://master:7077` | Points at a standalone Spark master |
| `--deploy-mode cluster` | Runs the driver on a cluster node |
| `--supervise` | Restarts the driver automatically if it fails |
| `--total-executor-cores` | Total core budget across executors |

Expanded: `--supervise` is standalone-specific and worth remembering on its own - it's the mechanism that makes a standalone-cluster driver resilient to failure (auto-restart), which is otherwise a concern handled differently (or automatically) under YARN/Kubernetes.

**Kubernetes:**

Kubernetes configuration is primarily supplied through `--conf`, using the many `spark.kubernetes.*` properties rather than dozens of dedicated command-line arguments:

```bash
spark-submit \
  --master k8s://https://my-k8s-api:6443 \
  --deploy-mode cluster \
  --name my-job \
  --conf spark.kubernetes.container.image=my-spark:latest \
  --conf spark.executor.instances=5 \
  local:///opt/spark/jobs/job.py
```

| Cluster Manager | How extra config is mostly supplied |
|---|---|
| YARN | Dedicated flags (`--queue`, `--num-executors`, `--principal`, `--keytab`) |
| Standalone | Dedicated flags (`--supervise`, `--total-executor-cores`) plus `--master spark://...` |
| Kubernetes | Almost entirely via `--conf spark.kubernetes.*` properties |

---

## Application Arguments

Q. How does `spark-submit` decide which arguments belong to it versus the application being run?

A. (Teacher's definition) Anything after the application file/JAR is passed to your application rather than interpreted by spark-submit. This distinction is important in interviews and troubleshooting.

Expanded: `spark-submit` parses flags up through the application file path (`job.py` or a `.jar`); everything positioned *after* that path is handed to the application's own argument parser untouched, not to Spark. This is a common trip-up point - if the ordering is wrong (an app flag placed before the job file), Spark will try to interpret it as its own argument and fail.

```bash
spark-submit \
  --master yarn \
  --executor-memory 8g \
  my_job.py \
  --input s3://bucket/input \
  --date 2026-09-21
```

| Argument | Belongs to |
|---|---|
| `--master`, `--executor-memory` | `spark-submit` |
| `--input`, `--date` | `my_job.py` (the application) |

---

## Deploy Mode: `client` vs `cluster`

Q. What are the options for `--deploy-mode`?

A. (Teacher's definition)

```text
spark-submit
--master yarn
--deploy-mode cluster
--queue analytics
--num-executors 20
--executor-cores 4
--executor-memory 8g
job.py
```

for deploy-mode: the options are: `client` and `cluster`.

Expanded: `--deploy-mode` controls **where the driver process runs**, not where the executors run (executors always run out on the cluster's worker nodes either way):

| Deploy Mode | Driver runs on | Typical use case |
|---|---|---|
| `client` | The machine you ran `spark-submit` from (e.g. your laptop, an edge/gateway node) | Interactive work, debugging, notebooks - you want to see driver logs/output directly in your terminal |
| `cluster` | A node inside the cluster itself, managed by the cluster manager | Production jobs - the driver isn't tied to your machine staying connected, so it survives you disconnecting |

The key practical consequence: in `client` mode, if your local machine/network connection drops, the driver dies and the job dies with it, since the driver was running locally the whole time. In `cluster` mode, the driver is just another process running inside the cluster (YARN/standalone/Kubernetes), so it's resilient to the submitting machine disconnecting - this is why production pipelines almost always use `--deploy-mode cluster`, while `client` is preferred for interactive/debugging sessions where you want immediate console feedback.

**Interview line:** "Deploy mode only decides where the driver runs: in client mode it runs on the machine I submitted from, which is good for notebooks and debugging; in cluster mode it runs inside the cluster, which is what production jobs use so they survive the submitting machine going away."

---

## Worker vs Executor

Q. What is a worker, in Spark?

A. (Teacher's definition) In Spark, a worker is a computer - it is the physical node on which the program is running, and it's part of the cluster.

Expanded: this draws a distinction that `Training 0.md`'s Driver/Executor coverage left implicit (it used "Worker/Executor" almost interchangeably) - a **worker** is the physical machine/node itself, while an **executor** (below) is the actual process that Spark launches *on* that worker to run tasks. This mirrors the same coordinator/many-hands shape noted back in `Training 3.md`'s Jenkins Controller/Agent comparison - there, "Agent" conflates machine-and-process the same way "worker" and "executor" can get conflated here, so it's worth keeping the two ideas separate.

---

Q. What is an executor, in Spark?

A. (Teacher's definition) An executor is a process, part of Spark's software, which runs on the nodes in the cluster.

Expanded: this confirms the distinction directly - an executor isn't the machine itself, it's a *process* (specifically, a JVM process that's part of Spark's own software) that Spark starts up on a worker node to actually execute tasks. A single worker node can potentially host one or more executor processes; the worker is the hardware/host, the executor is the running Spark process doing the work on it.

---

Q. Is it usually one executor per worker, or can a worker run more than one?

A. (Teacher's definition) In most Spark jobs, multiple executors will be running on one worker.

Expanded: this settles the cardinality question directly - it's not a 1:1 mapping. A single worker (physical/virtual machine) typically has multiple CPU cores and a large chunk of RAM, so rather than running just one large executor process, Spark commonly divides a worker's resources across several smaller executor processes running side-by-side on that same machine. This is exactly why `--executor-memory` and `--executor-cores` (from the Driver/Executor Resources table above) are sized *per executor*, not per worker - the total resources a worker contributes to a job is effectively `(executors on that worker) x (--executor-memory / --executor-cores)`, and getting that per-executor sizing right (not too big, not too small) is a core part of Spark cluster tuning.

---

Q. What was the older, "classic" terminology for this same coordinator/worker architecture?

A. (Teacher's definition) The standard terminology for the nodes in the cluster used to be that we have a master node and multiple worker nodes. That was the standard in Spark - the classic name for the architecture in which we have one node where the developer logs in and does the majority of the work, then that node controls all the other nodes in the cluster, was called the **master-slave architecture**.

Expanded: "master-slave" is the general historical name for a one-coordinator, many-workers cluster. The industry has broadly moved away from the term (replaced with pairings like primary/replica or leader/follower depending on the tool), but it's worth recognizing in older docs, legacy codebases, or interview questions.

Expanded (correction): in Spark specifically, the **Master** and the **driver** are two different things, so "master" does not map to "driver".
- In Spark Standalone mode, the **Master** is the **cluster manager**: a long-running daemon (`spark://host:7077`) that tracks the Workers and allocates cores/memory to applications. On YARN its role is played by the ResourceManager.
- The **driver** is a separate process, one per application, that runs your `main()`/SparkSession, builds the plan, and schedules tasks onto executors. It runs on the client machine (client mode) or on a worker (cluster mode).
- The node "where the developer logs in" is usually called an **edge node** or gateway node. It is where `spark-submit` is run, not the Master.

This matches the Anatomy of a Spark Application section below, where the Spark Master is listed as the cluster manager.

| Role | Spark Standalone name | YARN equivalent | What it does |
|---|---|---|---|
| Cluster manager ("master") | Master | ResourceManager | Allocates resources across all applications |
| Per-node agent ("slave") | Worker | NodeManager | Launches executor processes on its machine |
| Per-application coordinator | Driver | Driver (inside the ApplicationMaster in cluster mode) | Plans the job and schedules tasks |
| Per-application workers | Executors | Executors (YARN containers) | Run tasks and hold cached data |

| Term | What it actually is |
|---|---|
| Worker | The physical (or virtual) machine/node - part of the cluster's hardware |
| Executor | The process that runs on a worker, executes assigned tasks, and holds cached/in-memory data |
| Driver | The process (usually on a separate machine, or the client machine in `client` deploy mode) that coordinates the job and schedules tasks onto executors |

---

## What Happens When You Run `spark-submit` (a.k.a. "What Is the Architecture of Apache Spark?")

**Interview note (teacher's recommendation):** if either "What happens when you submit a Spark job with `spark-submit`?" or "What is the architecture of Apache Spark?" is asked, the answer below is the recommended one to give - the same five-step walkthrough answers both questions.

Q. When you submit a Spark job with `spark-submit`, what actually happens, end to end?

A. (Teacher's definition)
1. The driver application spins up, and the configuration and logic is read by the system.
2. The optimizer will create 2 plans - a logical plan and a physical plan.
3. The partitioned data is sent across the cluster to the various nodes, and is taken up by the various executors - the cluster manager is what manages this part of the process.
4. Each of the executors processes its share of the data.
5. When each executor finishes its work, it will return the data to the driver (through the cluster manager), and the output data will be re-assembled, then sent to the output location.

Expanded: this is the full end-to-end lifecycle of a Spark job, tying together nearly every concept covered so far in this file:

| Step | What happens | Ties back to |
|---|---|---|
| 1. Driver spins up | The driver process starts, reading the job's configuration (all the `spark-submit` flags/`--conf` settings above) and the application's own code/logic | Core Arguments, Deploy Mode sections above |
| 2. Optimizer builds logical + physical plans | Spark's Catalyst optimizer turns your DataFrame/SQL logic into a **logical plan** (what to do, in the abstract), then an optimized **physical plan** (the concrete execution strategy - e.g. which join algorithm, how to partition) | Builds on `Training 0.md`'s "Spark builds a DAG" coverage - the logical/physical plan pair is the more precise, two-stage version of that DAG-building step |
| 3. Cluster manager launches executors; driver sends tasks | The cluster manager (YARN/standalone/Kubernetes) launches the executor processes. The driver then sends tasks **directly** to the executors. Each task reads its own partition straight from storage (ideally on the same node - data locality) | Cluster-Manager-Specific Arguments section above |
| 4. Executors process their share | Each executor runs its assigned tasks on its partition(s) in parallel with the others, exchanging data with other executors during shuffles | Worker vs Executor section above |
| 5. Output is written / results returned | For a write, each executor writes its own partition directly to the output location (S3/HDFS/table). Only actions like `collect()`, `take()` or `count()` send results back to the driver, and executors send them directly, not through the cluster manager | Driver's role in the Driver/Executor split above |

Expanded (correction): steps 3 and 5 of the teacher's answer need two fixes before you give it in an interview.
1. **The cluster manager is not a data path.** It allocates resources and launches executors (and adds/removes them under dynamic allocation). After that, executors register with the driver and talk to it **directly**: the driver sends tasks, and executors send back task status, heartbeats, and results.
2. **Nothing is re-assembled on the driver for a write.** Each executor writes its own output files in parallel (that is why a Spark write produces many `part-*` files). Data only comes back to the driver for actions like `collect()`/`take()`, which is why `collect()` on a big dataset can crash the driver.

| Component | Talks to | About what |
|---|---|---|
| Driver -> cluster manager | At startup (and for dynamic allocation) | "I need N executors with X cores / Y GB" |
| Cluster manager -> worker nodes | At startup | Launch executor processes |
| Driver <-> executors | Whole job, directly | Tasks out; status, heartbeats, `collect()` results back |
| Executor <-> executor | During shuffles | Shuffle blocks |
| Executor -> storage | Whole job | Read input partitions, write output files |

**Interview line (corrected 5 steps):** "1) The driver starts and creates the SparkSession. 2) Catalyst turns my code into a logical plan, optimizes it, and picks a physical plan, which becomes a DAG of stages split at shuffles. 3) The driver asks the cluster manager for executors, and the cluster manager launches them. 4) The driver sends tasks, one per partition, directly to the executors, which read their partitions from storage, run in parallel, and shuffle between stages. 5) Executors write output directly to storage; only actions like `collect()` bring rows back to the driver."

### The Optimizer (Step 2, in detail)

Q. What optimizer does Spark use to build the logical/physical plans in step 2, and what's its job?

A. (Teacher's definition) There are multiple optimizers which you could use, the most common ones are the default optimizer and the Catalyst optimizer. These days, usually the Catalyst optimizer is what's preferred. Its job is to determine before the job is executed what the most efficient way of performing the job will be.

Expanded: the optimizer is the component responsible for taking your DataFrame/SQL code and figuring out, ahead of time, the fastest way to actually execute it - this is why step 2 in the execution flow above happens *before* any data actually moves across the cluster. **Catalyst** is Spark SQL's own optimizer and is the modern default/preferred choice - it's what actually performs the logical-plan -> optimized-logical-plan -> physical-plan pipeline referenced in step 2 above, applying rule-based and cost-based optimizations (e.g. predicate pushdown, reordering joins, picking a join strategy) before any executor starts running real tasks. This is also the direct mechanism behind Spark's **lazy evaluation**, already noted in `Training 0.md`'s ETL coverage - transformations don't run immediately precisely because Spark is waiting to hand the full chain of transformations to the optimizer first, rather than executing each one eagerly as it's written.

| Term | What it is |
|---|---|
| Optimizer (general) | The component that decides the most efficient execution strategy for a job, before it runs |
| Catalyst optimizer | Spark SQL's optimizer, and the default (and only) optimizer for DataFrames, Datasets and SQL - produces the logical and physical plans referenced in step 2 above |
| CBO (cost-based optimization) | Part of Catalyst; uses table/column statistics (`ANALYZE TABLE ... COMPUTE STATISTICS`) to pick join order and join strategy |
| AQE (Adaptive Query Execution) | Re-plans at runtime using real shuffle statistics (see below) |
| Tungsten | The execution engine underneath: whole-stage code generation and off-heap/binary memory management |

Expanded (correction): there is no separate "default optimizer" to choose between. Catalyst **is** the default optimizer for DataFrame/Dataset/SQL code, and plain RDD code has no optimizer at all (Spark runs RDD operations exactly as written). This is one reason DataFrames are usually faster than RDDs. The pieces worth naming in an interview are Catalyst, CBO, AQE, and Tungsten, as in the table above.

---

Q. What is a "predicate," in this context?

A. (Teacher's definition) Predicate - this is a reference to a field of formal logic which we don't need to super go into - but you just need to know that anything that removes data from the dataset can be considered a predicate - that includes the WHERE clause in SQL and the filter operation in Spark.

Expanded: rather than a strict formal-logic definition, the practical takeaway is simpler - a predicate is any condition that decides "keep this row or not," which in Spark/SQL terms means a `WHERE` clause or a `.filter()`/`.where()` call. This is the term that "predicate pushdown" (next) is named after.

---

Q. What is predicate pushdown, one of Catalyst's optimizations mentioned above?

A. (Teacher's definition) Predicate pushdown is the principle that we use operations that involve a predicate as early as possible in the execution. This enables us to remove any rows that don't need to be processed at the beginning of the job rather than at the point where they are referenced.

Expanded: without pushdown, you might write a filter *late* in your code (e.g. right before writing output), but Spark would still have to read, shuffle, and process every row of the full dataset through all the earlier steps before that filter finally discards the unwanted ones - wasted work on rows that were always going to be thrown away. Predicate pushdown is Catalyst rewriting the physical plan so that filter is applied as early as possible instead - ideally right at the data source read itself (many formats/sources, like Parquet or a JDBC database, can skip reading rows/blocks that don't match a filter, so pushing the predicate down to that level avoids even reading the unneeded data off disk). This directly reduces how much data has to flow through every later step, including any shuffles - fewer rows moving through the pipeline means less network/disk/compute cost everywhere downstream.

| Without predicate pushdown | With predicate pushdown |
|---|---|
| Filter is applied wherever it's written in the code (often late) | Catalyst moves the filter as early as possible - ideally to the data source read itself |
| Full dataset flows through every earlier step before being filtered | Unneeded rows/blocks are discarded (or never read at all) before later steps run |
| Wasted I/O, shuffle, and compute on rows that get thrown away anyway | Less data moving through the whole pipeline, cheaper shuffles |

Concretely, this is the shape predicate pushdown aims for:

```text
Read 1 TB
   ↓
Filter early
   ↓
Keep 50 GB
   ↓
Join / Group / Sort 50 GB
```

...rather than carrying the entire 1 TB through expensive operations (joins, shuffles, sorts) before finally filtering it down at the end.

---

Q. What is the logical plan, specifically?

A. (Teacher's definition) The logical plan is a high-level, formal plan that describes the operations that Spark will take in order to get the input data to be processed into the output data.

---

Q. What is the physical plan, specifically?

A. (Teacher's definition) The physical plan is the formal description of the low-level execution plan style steps that the computer will take to implement the logical plan.

Expanded: the two plans sit at different altitudes describing the *same* job. The **logical plan** answers "what needs to happen" (e.g. "filter these rows, then join these two datasets, then aggregate") without committing to *how* - it's an abstract description of the transformations, independent of the cluster's actual hardware. The **physical plan** answers "how will this actually run" - it takes that logical plan and turns it into concrete, low-level execution steps (which join algorithm to use, how data gets partitioned/shuffled, which operations can be combined into a single stage), tailored to the real cluster it's about to run on. This is the same logical -> physical progression already summarized in step 2 of the execution-flow table above, just broken out here in full detail.

---

Q. Does the optimizer only ever produce one logical plan and one physical plan?

A. (Teacher's definition) In most Spark jobs, the optimizer will create multiple logical plans and multiple physical plans, and based on what it knows about the cluster architecture, it will select the plan that it thinks is going to be the most efficient.

Expanded: this is the cost-based side of Catalyst's optimization process - rather than committing to the first valid plan it finds, Catalyst typically generates several *candidate* logical and physical plans (e.g. different join orderings, different join algorithms) and then picks whichever candidate it estimates will be cheapest to actually run, using what it knows about the data (statistics, size estimates) and the cluster (available executors/resources). This is why the same DataFrame code can execute differently - and with different performance - depending on the cluster it's submitted to, or as data volumes/statistics change over time.

| Plan | Answers | Altitude |
|---|---|---|
| Logical plan | *What* needs to happen to the data | High-level, abstract - independent of the cluster |
| Physical plan | *How* it will actually be executed | Low-level, concrete - tailored to the real cluster/hardware |
| Selection | Optimizer generates multiple candidates of each, picks the most efficient based on known data/cluster info | Cost-based optimization |

---

Q. What is a DAG, in the Spark context?

A. (Teacher's definition) Directed Acyclic Graph (DAG).

Expanded: in one sentence - the DAG is the graph of all the transformations in your job, with arrows showing which step feeds which and no loops; Spark's scheduler cuts it into stages at every shuffle and runs the stages in order. `Training 0.md` already briefly touched on this ("Spark builds this into a DAG (Directed Acyclic Graph) of steps"). A DAG is a graph of nodes connected by directed edges (arrows) with no cycles - you can never follow the arrows back to a node you already visited. In Spark, the DAG represents the chain of transformations (per the Narrow vs Wide Dependencies section below) as a graph of dependencies between RDDs/DataFrames - it's the structure the logical plan above is built as, before Catalyst turns it into a physical plan.

---

Q. Is the DAG concept specific to Spark?

A. (Teacher's definition) The DAG is a Spark concept, but it comes from mathematics, specifically graph theory, and is used in other applications besides Spark, notably Apache Airflow, and can be applied in many cases.

Expanded: this connects forward to `Training 26.md`'s upcoming Apache Airflow coverage - Airflow uses the exact same DAG concept to represent a *pipeline* of tasks/dependencies (rather than Spark's chain of data transformations), which is why Airflow's own building block is literally called a "DAG" too. Recognizing DAG as a general graph-theory concept, not a Spark-specific invention, makes it easier to transfer this mental model directly onto Airflow (and any other tool built around directed, cycle-free dependency graphs) later in the course.

---

Q. Why is it called a "directed" graph specifically?

A. (Teacher's definition) It's a directed graph because it contains circles and lines, and the lines represent a direction moving from one circle to the next - in technical terms these are called nodes and edges.

Expanded: "circles" = **nodes** (the individual steps/RDDs/DataFrames in the chain), "lines" = **edges** (the connections between them) - and what makes it *directed* specifically is that each edge/line has a direction (drawn as an arrow), representing "this step happens, then flows into that step," not just an undirected connection. The "acyclic" half of DAG (already covered above) is the separate guarantee that following those directed edges can never loop back to a node already visited - together, "directed" (edges have a one-way flow) and "acyclic" (no loops) are what make a DAG a valid representation of a data pipeline, where earlier steps must always complete before later ones that depend on them.

| Term | Meaning |
|---|---|
| Node | A single step/vertex in the graph (e.g. one RDD/DataFrame transformation) |
| Edge | A directed connection between two nodes, showing which step flows into which |
| Directed | Every edge has a one-way direction - not simply "connected," but "flows from A to B" |
| Acyclic | No path of edges ever loops back to a node already visited |

---

Q. Why is it called an "acyclic" graph specifically, in the Spark context?

A. (Teacher's definition) It's an acyclic graph because once you have moved from one stage to the next, it is against the rules to go back to the previous stage.

Expanded: this grounds the general graph-theory "acyclic" definition (no loops, above) in Spark's own terms - once execution has advanced from Stage 0 to Stage 1 (per the Jobs, Stages, and Tasks section above), there's no rule or mechanism for going backwards to re-run Stage 0 as part of that same DAG. Data flows strictly forward through the chain of transformations, stage by stage, which is exactly why the RDD lineage example earlier in this file only ever has arrows pointing forward (`RDD 1 → RDD 2 → RDD 3 → RDD 4`) and never back.

### Adaptive Query Execution (AQE)

Q. What was the big feature introduced in Spark 3.0 for improving query efficiency during execution?

A. (Teacher's definition) Adaptive Query Execution. AQE was the big feature in Spark 3.0. AQE is a system that will continuously work to improve the efficiency of the Spark job during execution.

---

Q. How does AQE actually work?

A. (Teacher's definition) The basic way that it works is that instead of just selecting one logical plan and one physical plan, AQE will develop new plans after the execution of each stage - so as soon as Spark's execution goes from one stage to the next, AQE will collect data about the actual observed performance of the executors. Then it will create new logical and physical plans in order to further improve efficiency. It will do this as many times as necessary in order to improve efficiency. It can also automatically change partition sizes in order to avoid data skew.

Expanded: this is the key limitation AQE fixes in the plain Catalyst flow described above - without AQE, the optimizer picks its "most efficient" logical/physical plan **once**, up front, based only on estimates (statistics, size guesses) before any data has actually moved. Real execution can reveal those estimates were wrong (e.g. a join turns out far more skewed than expected). AQE addresses this by re-running the planning step **mid-job**: after each stage completes (recall from `Training 0.md`, a stage is a unit of work bounded by shuffle boundaries), AQE looks at what the executors *actually* observed - real data sizes, real partition distributions - and re-optimizes the remaining logical/physical plan for the stages still to come, repeating this re-planning as many times as there are stage boundaries. One concrete capability this enables: automatically resizing/coalescing partitions mid-job to correct for **data skew** (some partitions being far larger than others, which otherwise leaves some executors idle while one struggles through an oversized partition).

This directly explains the `spark.sql.adaptive.enabled=true` setting already shown in the Common Configuration Through `--conf` section earlier in this file - that flag is what turns AQE on.

**AQE's three concrete capabilities (per today's class summary):**
- Dynamically **changes join strategies** mid-query (e.g. switching to a broadcast join - see Broadcast Variables and Broadcast Joins, below - if a table turns out smaller than originally estimated)
- **Coalesces unnecessarily small shuffle partitions** (avoiding the overhead of scheduling/running many tiny tasks)
- **Detects and mitigates skewed partitions** in sort-merge joins, by splitting an oversized partition into smaller tasks (see Data Skew, below - it does not fix skewed `groupBy` aggregations)

**Important scope clarification:** AQE does **not** maintain a learning history across separate job *runs* - it only responds to runtime information gathered *during the current execution* (per-stage statistics, as described above), not to what happened the last time this same job ran. Persisted table/column statistics can separately feed into Catalyst's cost-based optimizer (CBO) when constructing the *initial* plan, before AQE ever kicks in - but that's a distinct mechanism from AQE's own mid-job adaptation.

| Without AQE | With AQE |
|---|---|
| One logical + physical plan, chosen once, before execution, based on estimates | Plan is re-evaluated after every stage, based on actual observed executor performance |
| Skewed partitions stay as originally planned | Skewed sort-merge-join partitions can be split mid-job; small shuffle partitions are coalesced |
| Spark's original optimization model | Spark 3.0's major optimization feature (`spark.sql.adaptive.enabled=true`) |

---

## Jobs, Stages, and Tasks

Q. What are the levels of execution a Spark program is divided into?

A. (Teacher's definition) A Spark program is going to be divided into three levels of executions - jobs, stages, and tasks.

Expanded: this is the same three-level breakdown already introduced in `Training 0.md` ("How a job actually executes - Job -> Stages -> Tasks"), revisited here as its own dedicated topic rather than a side note - worth treating as the granularity hierarchy underneath everything else covered in this file's "What Happens When You Run `spark-submit`" section: the physical plan (from the Optimizer section above) is what actually gets carved up into jobs, then stages, then tasks at execution time.

A class slide ("Anatomy of a Spark Application") confirms the full hierarchy has one more level above Job:

| Level | Granularity | Triggered/bounded by |
|---|---|---|
| App(lication) | The whole submitted program | One `spark-submit` invocation - can contain multiple jobs |
| Job | A unit of work within the app | Triggered by an action (e.g. `.save()`, `.count()`) |
| Stage | A chunk of a job | Bounded by shuffle boundaries (a new stage starts wherever data must move across the network - see Narrow vs Wide Dependencies, below) |
| Task | The smallest unit of work | One task per data partition within a stage - tasks run in parallel across executors |

```text
App
├── Job
│   ├── Stage
│   │   ├── Task
│   │   └── Task
│   └── Stage
│       ├── Task
│       └── Task
└── Job
    └── Stage
        ├── Task
        └── Task
```

Tasks are ultimately what run *on* executors (per the Worker vs Executor section above) - the same executor can run tasks from different stages/jobs over its lifetime, it isn't dedicated to just one.

---

Q. What exactly is a task?

A. (Teacher's definition) A task is an individual data processing operation that Spark performs - all actual commands that you pass to spark are tasks.

Expanded: this reframes "task" from a purely structural definition (one-per-partition, per the table above) to a functional one - a task is the actual unit of *work being done*, corresponding to whatever command(s) you write in your Spark code. Every task falls into one of three categories, covered next.

---

## Narrow vs Wide Dependencies (Transformations) and Actions

Q. What are the three categories every Spark task falls into?

A. (Teacher's definition) All tasks fall into one of three categories: narrow transformations, wide transformations, and actions.

---

Q. What is a narrow transformation?

A. (Teacher's definition) Narrow transformations are data processing operations which do NOT shuffle the data.

---

Q. What is a wide transformation?

A. (Teacher's definition) Wide transformations are operations which shuffle the data.

---

Q. What is an action?

A. (Teacher's definition) Actions are operations which return something other than a new DataFrame or RDD.

Expanded: this is the authoritative three-way split underlying everything already covered about stages and shuffles in this file - **narrow** and **wide** are both *transformations* (lazy - per `Training 0.md`'s lazy-evaluation coverage, they just build up the DAG/logical plan without running yet), distinguished purely by whether they require a shuffle; **actions** are the separate category that actually triggers execution of the whole chain, and are recognizable specifically because they return something other than a new DataFrame/RDD (e.g. a count, a collected list, a write to disk) rather than another lazy DataFrame/RDD to keep chaining.

| Dependency type | What it means | Example transformations | Effect on stages |
|---|---|---|---|
| Narrow transformation | Does NOT shuffle the data - each input partition contributes to only one output partition | `map()`, `flatMap()`, `filter()` | Stays within the same stage - no shuffle required |
| Wide transformation | Shuffles the data - input partitions can contribute to *multiple* output partitions | `reduceByKey()`, `groupBy()`, `join()` | Forces a new stage boundary - a shuffle is required before the next step can run |
| Action | Returns something other than a new DataFrame/RDD (not a transformation at all) | `.count()`, `.collect()`, `.save()` | Triggers actual execution of the whole job (per Spark's lazy evaluation model) |

**Concrete example, from the class's RDD lineage diagram (a single Job, two Stages):**

```text
Job
├── Stage 0 (narrow dependencies - no shuffle)
│   RDD 1 --flatMap()--> RDD 2 --map()--> RDD 3
└── Stage 1 (starts after a wide dependency)
    RDD 3 --reduceByKey()--> RDD 4 --Action-->
```

`flatMap()` and `map()` are both narrow - each partition of RDD 1 maps cleanly to one partition of RDD 2, then RDD 3, with no cross-node data movement, so they all stay inside Stage 0. `reduceByKey()` is wide - to group all values sharing the same key together, data from *any* partition of RDD 3 might need to end up in *any* partition of RDD 4 (shown on the diagram as crossing lines between RDD 3 and RDD 4's partitions), which requires a shuffle across the network - and that shuffle is exactly what forces Stage 1 to begin. The whole thing only actually executes once an **Action** (e.g. `.collect()`, `.save()`) is called at the end, per Spark's lazy evaluation model (`Training 0.md`).

**Why this matters practically:** shuffles are the most expensive operation in Spark (data movement across the network, as already flagged in `Training 0.md`'s "Key Concepts" table) - recognizing which of your transformations are wide (and therefore trigger a shuffle/new stage) versus narrow is central to writing efficient Spark code and to reading a Spark execution plan/DAG when debugging performance.

### The Precise Distinction (Partition Dependencies)

Q. What is the precise distinction between a narrow transformation, a wide transformation, and an action?

A. (Teacher's definition) For teaching Spark, the key distinction is:
- **Narrow transformation** → each output partition depends on a small number - typically one - of input partitions; no shuffle is inherently required.
- **Wide transformation** → output partitions depend on multiple input partitions; normally introduces a shuffle/exchange.
- **Action** → causes Spark to actually execute the lazy DAG and return/write a result.

**One complication:** some operations are *conditionally* wide depending on the physical plan (from the Optimizer section above). A join is the classic example - a sort-merge join shuffles, while a broadcast join does not (covered in the Joins subsection below).

### Narrow Transformations - Reference Table

These generally operate independently within existing partitions - no data needs to cross the network.

| Operation | API | What it does |
|---|---|---|
| `map()` | RDD | One input element → one output element |
| `flatMap()` | RDD | One input → zero/many outputs |
| `mapPartitions()` | RDD | Transform an entire partition |
| `mapPartitionsWithIndex()` | RDD | Transform partition with partition index |
| `filter()` | RDD / DF | Remove rows/elements |
| `select()` | DataFrame | Select/project columns |
| `selectExpr()` | DataFrame | SQL-expression projection |
| `withColumn()` | DataFrame | Add/replace a column |
| `withColumns()` | DataFrame | Add/replace multiple columns |
| `drop()` | DataFrame | Remove columns |
| `withColumnRenamed()` | DataFrame | Rename column |
| `withColumnsRenamed()` | DataFrame | Rename multiple columns |
| `where()` | DataFrame | Filter rows |
| `alias()` | DataFrame | Assign alias |
| `cast()` | Column expression | Convert datatype |
| `when()`/`otherwise()` | Column expression | Conditional transformation |
| `union()` | RDD / DF | Combine datasets without deduplication |
| `unionAll()` | DataFrame | Alias of `union()` |
| `unionByName()` | DataFrame | Union using column names |
| `sample()` | RDD / DF | Random sampling |
| `coalesce()` | RDD / DF | Usually reduce partitions without full shuffle |
| `mapValues()` | Pair RDD | Transform values while preserving keys |
| `flatMapValues()` | Pair RDD | Flat-map values while preserving keys |
| `keys()` | Pair RDD | Extract keys |
| `values()` | Pair RDD | Extract values |
| `glom()` | RDD | Convert each partition into an array |
| `pipe()` | RDD | Send partition data through external process |
| `mapInPandas()` | DataFrame | Apply Python/Pandas processing by batches/partitions |
| `transform()` | DataFrame | Apply a function returning another DataFrame |

Typical examples:

```python
df.filter(col("salary") > 50000)
df.select("employee_id", "salary")
df.withColumn("annual_bonus", col("salary") * 0.10)
```

These can normally be pipelined together *within a single stage*, per the Lazy Evaluation section's "zero or more narrow transformations" rule:

```text
Partition 1 → filter → select → withColumn → output
Partition 2 → filter → select → withColumn → output
Partition 3 → filter → select → withColumn → output
```

No exchange of data between workers is inherently necessary.

### Wide Transformations

**Aggregation operations** - same keys must be brought together, which normally requires a shuffle:

| Operation | API | Why wide |
|---|---|---|
| `groupBy()` + aggregation | DF | Same keys must be brought together |
| `groupByKey()` | RDD | Same keys must be brought together |
| `reduceByKey()` | RDD | Key aggregation requires repartitioning |
| `aggregateByKey()` | RDD | Key aggregation |
| `combineByKey()` | RDD | Key aggregation |
| `foldByKey()` | RDD | Key aggregation |
| `cube()` | DF | Multidimensional aggregation |
| `rollup()` | DF | Hierarchical aggregation |
| `pivot()` | DF | Grouping/pivot aggregation |

*(Note: `countByKey()` is actually an **action**, not a transformation, despite involving aggregation - it belongs in the Actions tables below from an API/lazy-execution perspective.)*

```python
df.groupBy("department").avg("salary")
```

```text
Executor 1 ─┐
Executor 2 ─┼── SHUFFLE ──> department partitions
Executor 3 ─┤
Executor 4 ─┘
```

**Sorting operations** - global sorting requires Spark to redistribute records so partition ranges are correctly ordered:

| Operation | API |
|---|---|
| `sort()` | DataFrame |
| `orderBy()` | DataFrame |
| `sortBy()` | RDD |
| `sortByKey()` | Pair RDD |
| `repartitionByRange()` | DataFrame |

**Partitioning operations:**

| Operation | API | Behavior |
|---|---|---|
| `repartition()` | RDD / DF | Full redistribution |
| `repartitionByRange()` | DF | Redistributes by ranges |
| `partitionBy()` | Pair RDD | Redistributes according to partitioner |

**Important interview distinction:** `df.coalesce(4)` is usually **narrow** when reducing partitions (it merges existing partitions locally where possible, without a full shuffle), whereas `df.repartition(4)` is **wide**, because Spark deliberately redistributes the data across the cluster - both change partition count, but only one of them shuffles.

**In the teacher's own words:**

Q. What's the difference between `coalesce` and `repartition`?

A. (Teacher's definition) Coalesce is a method in Spark which can reduce the number of partitions by taking all of the partitions that have gone to a particular node, then combining them together into a single partition. So coalesce can only turn smaller partitions into larger partitions, and it does NOT guarantee that the partition sizes will be equal. Repartition is similar - in fact, at the low level, repartition first performs a coalesce operation, THEN it shuffles the data and divides it into the specified number of partitions.

Expanded: `coalesce()`'s mechanism specifically: it works *node-locally* - combining partitions that already live on the same node into fewer, larger partitions - which is exactly why it can avoid a full network shuffle, but also why it can only ever *decrease* partition count (you can't merge your way to more partitions than you started with), and why the resulting partitions can end up uneven in size (it's just grouping what's already there, not evenly redistributing).

Expanded (correction): `repartition()` does not run a coalesce step and *then* a shuffle as two separate steps. In the RDD API, `repartition(n)` is literally defined as `coalesce(n, shuffle = true)` - the same method with the shuffle switched on, so it is **one** full shuffle. Two more details:
- Only `repartition(n)` with no column spreads rows round-robin into roughly equal partitions. `repartition(n, "col")` hash-partitions by the column, so a hot key still produces one oversized partition (this is why salting exists - see Training 8).
- `coalesce(1)` (or any big reduction) is narrow, so Spark can fold it into the **previous** stage. That stage then runs with only 1 task, which can make the whole upstream computation single-threaded. If you need one output file from heavy work, `repartition(1)` keeps the upstream stage parallel and only the final write runs on one task.

| | `coalesce()` | `repartition()` |
|---|---|---|
| Can increase partition count? | No - can only reduce (DataFrame API) | Yes - can increase or decrease |
| Mechanism | Merges existing partitions (preferring ones on the same node) into fewer, larger ones | One full shuffle; it is `coalesce(n, shuffle = true)` |
| Equal partition sizes? | No | Roughly, for `repartition(n)` (round-robin); not guaranteed for `repartition(n, col)` (hash - hot keys stay together) |
| Shuffle? | Avoids a full shuffle (narrow) | Always shuffles (wide) |
| Gotcha | `coalesce(1)` can collapse the upstream stage to 1 task | Costs a full shuffle |

**Interview line:** "`coalesce` reduces partitions by merging existing ones without a shuffle, so it's cheap but can leave uneven partitions; `repartition` does a full shuffle, so it can increase or decrease the count and gives even partitions when you don't partition by a column. I use `coalesce` to cut down partitions before a write, and `repartition` when I need more parallelism or need to rebalance."

---

Q. Given that `repartition()` costs more compute than `coalesce()`, when is it worth choosing anyway?

A. (Teacher's definition) So repartition is going to be able to deliver even partition sizes, so while it is a more computationally expensive operation than coalesce, it's often necessary to pay the additional compute cost up front, because the problems you will have by operating on uneven partitions are worse down the road.

Expanded: this is the practical decision rule tying `coalesce()` vs `repartition()` directly back to the **Data Skew** section earlier in this file - uneven partitions are precisely what causes data skew (one executor stuck with an oversized partition while others idle), so choosing the cheaper `coalesce()` when partition sizes genuinely need to be balanced just defers that cost rather than avoiding it: you save on the shuffle now, but risk skew-driven slowdowns (or worse) throughout every downstream stage that has to work with those uneven partitions. `repartition()`'s upfront shuffle cost is a one-time, predictable expense; letting skew propagate downstream instead tends to cost more, less predictably, later in the job.

| Choice | Upfront cost | Downstream risk |
|---|---|---|
| `coalesce()` | Cheaper (avoids full shuffle) | Uneven partitions can cause data skew later in the job |
| `repartition()` | More expensive (always shuffles) | Even partitions with `repartition(n)`; `repartition(n, col)` can still be skewed by hot keys |

### Joins: Why "Join = Wide" Is an Oversimplification

Operations: `df.join()`, `rdd.join()`, `rdd.leftOuterJoin()`, `rdd.rightOuterJoin()`, `rdd.fullOuterJoin()`, `rdd.cogroup()`, `rdd.groupWith()`.

```python
orders.join(customers, "customer_id")
```

A typical **sort-merge join** requires:

```text
Orders                    Customers
   │                          │
   └──── shuffle by ID ───────┘
               │
         Sort-Merge Join
               │
             result
```

So this is wide. But:

```python
from pyspark.sql.functions import broadcast
orders.join(broadcast(customers), "customer_id")
```

can produce a **BroadcastHashJoin** - the small table is copied to the executors rather than both datasets being shuffled by key, avoiding the shuffle entirely.

Therefore, for DataFrames, it's more accurate to say: **a join can cause a shuffle, depending on the join strategy Spark chooses** (Catalyst's cost-based decision, per the Optimizer section above). Use `df.explain()` to see what Spark actually decided.

---

Q. What join strategies can Spark choose, and how do you force one?

A. Spark picks one of five physical join strategies based on table size, join type, and hints.

Expanded:

| Strategy | Shuffle? | When Spark picks it | Notes |
|---|---|---|---|
| Broadcast Hash Join | No (small side is broadcast) | Equi-join and one side is under `spark.sql.autoBroadcastJoinThreshold` (10 MB default), or a broadcast hint | Fastest; the small side must fit in driver and executor memory |
| Shuffle Hash Join | Yes, both sides | Equi-join, one side much smaller but too big to broadcast, and sort-merge is not preferred (or a `SHUFFLE_HASH` hint) | Builds a hash table per partition; no sort |
| Sort-Merge Join | Yes, both sides, plus a sort | Default for large-to-large equi-joins | Scales to any size because it can spill; AQE's skew-join handling applies here |
| Broadcast Nested Loop Join | No (one side broadcast) | Non-equi joins (`<`, `BETWEEN`, `LIKE`) with a small side | Compares every row pair; slow |
| Cartesian Product | Yes | Non-equi join or `crossJoin` with no small side | Rows = left x right; avoid |

Join hints (SQL and DataFrame):

```sql
SELECT /*+ BROADCAST(c) */ * FROM orders o JOIN customers c ON o.customer_id = c.customer_id;
-- other hints: MERGE (sort-merge), SHUFFLE_HASH, SHUFFLE_REPLICATE_NL
```

```python
orders.join(customers.hint("broadcast"), "customer_id")   # same as broadcast(customers)
orders.join(customers, "customer_id").explain()           # look for BroadcastHashJoin / SortMergeJoin
```

In `explain()` output, an `Exchange` node means a shuffle, and the join node name (`BroadcastHashJoin`, `SortMergeJoin`, `ShuffledHashJoin`) tells you which strategy was chosen. Broadcast joins and AQE come back in the Databricks material (Training 29); this section is the reference for them.

### Distinct / Set Operations

These frequently require shuffles, since Spark has to determine whether a duplicate/match exists in *another* partition:

| Operation | Typical behavior |
|---|---|
| `distinct()` | Wide |
| `dropDuplicates()` | Wide |
| `drop_duplicates()` | Wide |
| `intersection()` | Usually wide |
| `subtract()` | Usually wide |
| `exceptAll()` | Usually wide |
| `intersect()` | Usually wide |

```python
df.distinct()
```

Spark has to determine whether a duplicate exists in another partition, so records generally have to be redistributed.

### Window Functions

Many window operations result in exchanges and/or sorting:

```python
window = (
    Window
    .partitionBy("department")
    .orderBy(col("salary").desc())
)

df.withColumn("rank", rank().over(window))
```

Used with: `rank()`, `dense_rank()`, `row_number()`, `lag()`, `lead()`, `sum().over(...)`, `avg().over(...)`.

Spark generally has to bring rows for the same partition-by key (e.g. `department`) together and sort them - so although `withColumn()` is normally narrow (per the table above), a `withColumn()` containing a window expression can introduce an Exchange and sort. This illustrates why **physical plans matter more than simply memorizing method names**.

### Actions

**RDD actions:**

| Action | Result |
|---|---|
| `collect()` | Return entire RDD to driver |
| `count()` | Number of elements |
| `first()` | First element |
| `take(n)` | First n elements |
| `takeOrdered(n)` | First n according to ordering |
| `top(n)` | Largest n |
| `reduce()` | Reduce RDD to result |
| `fold()` | Aggregate using zero value |
| `aggregate()` | General aggregation |
| `treeReduce()` | Tree-based reduction |
| `treeAggregate()` | Tree-based aggregation |
| `foreach()` | Execute function for every element |
| `foreachPartition()` | Execute function per partition |
| `countByKey()` | Counts each key |
| `countByValue()` | Counts each value |
| `collectAsMap()` | Collect pair RDD as map |
| `lookup()` | Retrieve values for key |
| `isEmpty()` | Determine whether RDD is empty |
| `saveAsTextFile()` | Write text output |
| `saveAsSequenceFile()` | Write Hadoop SequenceFile |
| `saveAsObjectFile()` | Write serialized objects |

**DataFrame actions:**

| Action | Purpose |
|---|---|
| `show()` | Display rows |
| `collect()` | Return all rows to driver |
| `count()` | Count rows |
| `first()` | First row |
| `head()` | First row(s) |
| `take(n)` | Retrieve n rows |
| `tail(n)` | Retrieve final rows |
| `foreach()` | Run function against rows |
| `foreachPartition()` | Run function per partition |
| `toLocalIterator()` | Iterate through results locally |
| `isEmpty()` | Determine whether DataFrame is empty |

```python
df = spark.read.parquet("employees")
filtered = df.filter(col("salary") > 100000)
selected = filtered.select("name", "salary")
# Nothing necessarily executes yet.

selected.show()  # <- this is the action that triggers execution
```

**Writes are actions too:**

```python
df.write.parquet(...)
df.write.csv(...)
df.write.json(...)
df.write.orc(...)
df.write.format("delta").save(...)
df.write.saveAsTable(...)
df.write.insertInto(...)
df.write.jdbc(...)
```

```python
(
    df.write
      .mode("overwrite")
      .parquet("/output/employees")
)
```

This is effectively an action because Spark must execute the DAG to produce the files.

### Operations That Are Easy to Misclassify (Interview Table)

| Operation | Classification | Important caveat |
|---|---|---|
| `map()` | Narrow | RDD |
| `flatMap()` | Narrow | RDD |
| `filter()` | Narrow | RDD/DF |
| `select()` | Narrow | Unless expressions introduce something more complex |
| `withColumn()` | Usually narrow | Window expressions can cause shuffle/sort |
| `union()` | Narrow | Does not deduplicate |
| `coalesce()` | Usually narrow | Normally used to decrease partitions |
| `repartition()` | Wide | Forces shuffle |
| `groupBy()` + agg | Wide | Groups keys |
| `reduceByKey()` | Wide | Shuffle, but performs map-side combining |
| `groupByKey()` | Wide | Usually more expensive than `reduceByKey()` for aggregation |
| `distinct()` | Wide | Requires deduplication across partitions |
| `dropDuplicates()` | Wide | Generally requires exchange |
| `sort()` | Wide | Global ordering |
| `orderBy()` | Wide | Global ordering |
| `join()` | Depends | Join strategy matters |
| `crossJoin()` | Depends/expensive | Cartesian product |
| `Window.partitionBy()` | Usually wide | Exchange by window partition |
| `collect()` | Action | Dangerous for large data |
| `count()` | Action | Executes computation |
| `show()` | Action | Executes enough computation to obtain rows |
| `take()` | Action | Retrieves records |
| `write...` | Action | Executes DAG and writes result |
| `cache()` | Neither, in the simple sense | Marks dataset for caching; lazy |
| `persist()` | Neither, in the simple sense | Marks dataset for persistence; lazy |
| `unpersist()` | Storage-management operation | Removes cached blocks |

### The Most Useful Mental Model

Rather than memorizing every API call, ask:

**Does Spark need records from other partitions to calculate this result?**

```text
If no:  map, filter, select, withColumn       → NARROW
If yes: groupBy, distinct, repartition,
        global sort, many joins               → SHUFFLE → WIDE
```

**And if the operation asks Spark to produce an externally observable result:**

```text
show, collect, count, take, write             → ACTION
```

**Interview framing:** "wide vs. narrow" is fundamentally about partition dependencies and exchanges, not a rigid classification of method names - Catalyst/AQE (both covered above) can change the physical strategy, especially for joins. `df.explain()` is ultimately how you verify whether Spark has inserted an Exchange.

---

Q. What's the difference between `groupByKey()` and `reduceByKey()`?

A. Both are wide RDD transformations that group by key, but `reduceByKey()` combines values on the map side before the shuffle and `groupByKey()` does not.

Expanded: with `reduceByKey(_ + _)`, each executor first adds up the values for each key inside its own partitions (a **map-side combine**, like a MapReduce combiner), so only one partial result per key per partition crosses the network. With `groupByKey()`, every single value is shuffled, and all values for a key are collected into one in-memory list on one executor - more network traffic, and a hot key can run that executor out of memory. Use `reduceByKey`/`aggregateByKey` for aggregations; use `groupByKey` only when you really need every value. DataFrame `groupBy().agg()` already does partial aggregation automatically.

| | `groupByKey()` | `reduceByKey()` |
|---|---|---|
| Map-side combine | No | Yes |
| Data shuffled | Every value | One partial result per key per partition |
| Memory risk | All values for a key held at once | Low |
| Use for | Needing the full list of values | Sums, counts, max, any associative operation |

**Interview line:** "`reduceByKey` pre-aggregates on each partition before the shuffle, so it moves far less data; `groupByKey` shuffles every value and can OOM on a hot key, so I avoid it for aggregations."

---

Q. RDD vs DataFrame vs Dataset - what's the difference?

A. They are Spark's three APIs over the same engine; DataFrames and Datasets go through Catalyst, RDDs don't.

Expanded:

| | RDD | DataFrame | Dataset |
|---|---|---|---|
| What it is | Distributed collection of objects | Distributed table with named columns (`Dataset[Row]` in Scala) | Distributed collection of typed objects (`Dataset[Sale]`) |
| Optimized by Catalyst/Tungsten | No | Yes | Yes (lambdas are opaque to Catalyst) |
| Type safety | Compile-time (Scala/Java) | Runtime only (column names checked when the plan is analyzed) | Compile-time |
| Languages | Scala, Java, Python | Scala, Java, Python, R, SQL | Scala, Java only |
| Use when | Low-level control, unstructured data, legacy code | Default choice, especially in PySpark | Scala jobs that want typed domain objects (see Training 10) |

**Interview line:** "I default to DataFrames because Catalyst and Tungsten optimize them; Datasets add compile-time types in Scala; RDDs are the low-level API with no optimizer, so I only use them when I need that control."

---

## Lazy Evaluation

Q. Are all Spark operations lazily evaluated?

A. (Teacher's definition) All Spark operations are lazily evaluated.

Expanded (correction): only **transformations** are lazy. **Actions** (`count()`, `collect()`, `show()`, `write...`) are eager - calling one is exactly what makes Spark run the plan.

---

Q. What does lazy evaluation actually mean?

A. (Teacher's definition) Lazy evaluation is the principle that operations are not performed until the data is shuffled, and therefore taken from one stage to the next.

Expanded (correction): lazy evaluation means transformations (narrow **or** wide) are not executed until an **action** is called. A shuffle does not trigger execution. `df.groupBy("dept").count()` as a DataFrame transformation, or `rdd.reduceByKey(...)`, runs nothing on its own; it only adds a stage boundary to the plan. When an action is finally called, Spark hands the whole chain to the optimizer, builds the DAG, splits it into stages at the shuffles, and runs them. Benefits: Catalyst can optimize the full chain at once (predicate pushdown, column pruning, combining narrow steps into one stage), and nothing is computed that no action needs.

| Event | Triggers execution? |
|---|---|
| Narrow transformation (`filter`, `select`, `map`) | No |
| Wide transformation (`groupBy`, `join`, `repartition`) | No - marks a stage boundary in the plan |
| Action (`count`, `collect`, `show`, `write`) | Yes - submits a job |
| `cache()` / `persist()` | No - the data is cached the first time an action computes it |

Small exception worth knowing: a few calls run a job at definition time because Spark needs data to build the plan, e.g. `spark.read` with `inferSchema=True`, or `sortBy` on an RDD sampling the data for range boundaries.

**Interview line:** "Transformations are lazy - Spark just records them in a plan. Nothing runs until an action like `count`, `collect` or a write. Then Catalyst optimizes the whole chain, Spark splits it into stages at each shuffle, and runs the tasks."

---

Q. What is a stage, defined in terms of lazy evaluation and transformations?

A. (Teacher's definition) Stages are groups of tasks which are lazily evaluated. A stage will consist of zero or more narrow transformations, and at least one wide transformation or action.

Expanded: this is a more mechanical version of the lazy-evaluation idea already touched on briefly in `Training 0.md` ("Spark builds this into a DAG... and only actually runs it when an action... is triggered"). Put together with the Narrow vs Wide Dependencies section above, this gives a recipe for what a stage *is*: a run of narrow transformations (`map`, `filter`, `flatMap` - which can be pipelined together on one partition without moving data) that ends at a shuffle boundary (a wide transformation, where the next stage begins) or at the end of the job (the action). Stages describe **how** the work is divided up; **when** it runs is decided only by the action. Nothing executes on any executor until an action is called, and then all the stages of that job run in order.

| Stage composition rule | Meaning |
|---|---|
| Zero or more narrow transformations | Pipelined together inside one stage - no data movement between them |
| ...ending at a wide transformation or the action | A wide transformation closes the stage and starts a new one (shuffle boundary); the action ends the last stage. Only the action triggers execution |

Worked through the RDD lineage example above: `flatMap() -> map()` are the "zero or more narrow transformations" making up Stage 0, and `reduceByKey()` is the wide transformation that both closes Stage 0 and opens Stage 1 - matching this rule exactly. None of it runs until the final action.

---

## Data Skew

Q. How important is data skew as an interview topic?

A. (Teacher's definition) Data Skew - one of the most commonly talked about problems that can happen in a Spark program in interviews. It can also be referred to as Skewness.

---

Q. What is data skew, from the Spark execution perspective?

A. (Teacher's definition) Data skew (from the Spark execution perspective) is a situation where one of the executors needs to do more work than the other executors do - therefore, it's going to take a longer time than the other executors - therefore, the job as a whole is going to be delayed because of the one trailing executor.

Expanded: this is the practical cost of an uneven **shuffle** (per the Narrow vs Wide Dependencies section above) - when a wide transformation like `groupBy()`/`reduceByKey()`/a sort-merge `join()` redistributes data by key, some keys can be far more common than others (e.g. one `department` or `customer_id` has 10x the rows of the rest). Since each partition/task is tied to a set of keys, that means one executor ends up with a disproportionately large partition to process, while the other executors finish their (smaller, evenly-sized) partitions quickly and then sit idle. Because a Spark **job** only completes when *all* its tasks finish (per the Jobs, Stages, and Tasks section above), the entire job's total runtime is bottlenecked by that one slow, overloaded executor - adding more executors or more cluster resources doesn't fix this, since the problem isn't total capacity, it's an uneven *distribution* of the work.

This is the problem **AQE** (covered earlier in this file) targets - recall AQE "can also automatically change partition sizes in order to avoid data skew," re-planning partition boundaries mid-job based on actual shuffle statistics rather than the pre-execution estimate. Scope: AQE's skew handling (`spark.sql.adaptive.skewJoin.enabled`) splits oversized partitions in **sort-merge joins**; it does not fix a skewed `groupBy` aggregation.

---

Q. What's the root cause of data skew, put simply?

A. (Teacher's definition) Data skew is what happens when you don't partition your data properly.

Expanded: this is the root-cause framing behind the "one slow executor" symptom described above - skew isn't a bug or a random occurrence, it traces back to how the data ended up split into partitions in the first place. If partitioning is done in a way that happens to lump a disproportionate share of rows into one partition (most commonly: partitioning by a key whose values aren't evenly distributed in the real data, like a `customer_id` where one customer has far more orders than the rest), that partition becomes the oversized one an executor gets stuck processing. This is also why it's something you can proactively design around - e.g. choosing better partition keys, salting a skewed key to spread it across more partitions, or explicit `repartition()` calls - rather than purely something Spark has to react to after the fact via AQE.

| Aspect | Detail |
|---|---|
| Also called | Skewness |
| Root cause | Data not partitioned properly - a partition key whose real-world values aren't evenly distributed |
| Cause (mechanism) | Uneven key distribution during a shuffle (wide transformation) - some keys have far more rows than others |
| Symptom | One (or a few) executors take much longer than the rest; the others sit idle after finishing early |
| Effect | The whole job's total runtime is bottlenecked by the single slowest/most-overloaded executor |
| Why more resources don't fix it | The problem is distribution of work, not total cluster capacity |
| Spark's built-in mitigation | AQE (Adaptive Query Execution) can automatically split skewed partitions in sort-merge joins mid-job |
| How to spot it | Spark UI, Stages tab: one task's duration / shuffle-read size is far above the median (e.g. max 20 min vs median 30 s); that task often shows spill |

---

Q. How do you diagnose a slow or skewed job with `explain()` and the Spark UI?

A. Use `df.explain()` to read the plan before running, and the Spark UI to see what actually happened.

Expanded:

| Tool / tab | What to look at |
|---|---|
| `df.explain()` / `explain("formatted")` | `Exchange` nodes = shuffles; join type (`BroadcastHashJoin` vs `SortMergeJoin`); `PushedFilters` on the scan (predicate pushdown working); `AdaptiveSparkPlan` (AQE on) |
| Jobs tab | One job per action; which job is slow |
| Stages tab | Per-stage task metrics: compare **max vs median** task duration and shuffle read size (skew); "Spill (Memory/Disk)" columns (partitions too big for memory) |
| SQL / DataFrame tab | The executed physical plan with row counts per operator; the final plan after AQE changes |
| Storage tab | What is cached, at which storage level, and what fraction fits in memory |
| Executors tab | GC time, failed tasks, memory used per executor |

**Interview line ("Why is my Spark job slow?"):** "I open the Spark UI and find the slowest stage, then check for: skew (max task far above median), spill (partitions too big - raise shuffle partitions or memory), too many tiny tasks or small files (coalesce, compact), a sort-merge join that should be a broadcast, Python UDFs blocking Catalyst, and missing partition pruning or predicate pushdown on the read. Then I fix the biggest one and re-measure."

---

### Salting (Manual Skew Mitigation)

Q. What is salting, and is it still commonly used?

A. (Teacher's definition) Salting is a way to partition data which is somewhat outdated these days. AQE has pretty much completely taken the place of salting.

Expanded (correction): this is overstated. AQE handles most **join** skew automatically, by splitting oversized partitions in sort-merge joins. It does **not** fix a skewed `groupBy` aggregation, it can't split a single hot key in every case, and it only works on Spark 3.x with AQE enabled. Salting is still the standard manual fallback, and it is still a very common interview question.

---

Q. How does salting actually work?

A. (Teacher's definition) What salting is is that what we do is add a new column to our existing data, which contains multiple discrete values, a different one for each number of rows that we want for our partition.

Expanded: salting was the manual, proactive technique for the skew problem described above - instead of shuffling by the original skewed key alone (e.g. a `customer_id` with a disproportionate row count), you engineer a new "salt" column holding a small set of discrete values (e.g. a random number from 0-9), and shuffle/partition by the *combination* of the original key plus that salt value. This artificially splits what would have been one oversized partition (all rows for that one heavy key) into several smaller ones (one per salt value), spreading that key's rows across multiple executors instead of dumping them all on one. AQE (covered above) now handles much of this automatically for joins, but salting remains the manual fix when AQE doesn't apply (see the correction above).

---

Q. What are the concrete steps for applying salting?

A. (Teacher's definition) What you do is that you add a new column that has these distinct values, then you use the `repartition()` method to adjust the partition sizes based on the values of the salted key column. Then, after the partitioning is done, the salted key column is removed because it's no longer needed.

Expanded: the three steps are (1) add the synthetic salt column with its discrete values, (2) repartition by the original key plus the salt, and (3) drop the salt column when it is no longer needed.

Expanded (correction): `repartition(key, salt)` followed by dropping the salt does **not** fix skew on its own. The next wide operation (`groupBy("customer_id")` or `join(..., "customer_id")`) reshuffles by `customer_id` alone, and the hot key lands on one task again. The salt has to be part of the key **in the skewed operation itself**, and it can only be dropped after that operation. There are two real patterns (Training 8 covers the same caveat in detail):

**Pattern 1 - two-stage aggregation (skewed `groupBy`):**

```python
from pyspark.sql.functions import rand, col, sum as _sum

N = 10
salted = df.withColumn("salt", (rand() * N).cast("int"))

# Stage 1: partial aggregate per (key, salt) - the hot key is now spread over N tasks
partial = salted.groupBy("customer_id", "salt").agg(_sum("amount").alias("partial_amount"))

# Stage 2: combine the partials per real key - only N rows per key left to shuffle
result = partial.groupBy("customer_id").agg(_sum("partial_amount").alias("total_amount"))
```

**Pattern 2 - salted join (skewed join):**

```python
from pyspark.sql.functions import rand, explode, array, lit

N = 10
# Big, skewed side: random salt 0..N-1 on every row
orders_s = orders.withColumn("salt", (rand() * N).cast("int"))

# Small side: copy every row N times, once per salt value
customers_s = customers.withColumn("salt", explode(array(*[lit(i) for i in range(N)])))

# Join on (key, salt), then the salt can be dropped
joined = orders_s.join(customers_s, ["customer_id", "salt"]).drop("salt")
```

| Approach | How it works | Status |
|---|---|---|
| Two-stage aggregation | `groupBy(key, salt)` then `groupBy(key)` | Standard fix for skewed aggregations |
| Salted join | Random salt on the big side, small side exploded across all N salts, join on `(key, salt)` | Fix for skewed joins when AQE/broadcast isn't enough |
| AQE skew join | Automatically splits oversized sort-merge-join partitions at runtime | Default first line for join skew (Spark 3.x) |
| Broadcast the small side | No shuffle, so no skewed partition | Best option when one side is small |

**Interview line ("How do you handle data skew?"):** "First I confirm it in the Spark UI - one task much slower than the median. Then, in order: filter out nulls or junk hot keys, broadcast the small side if I can, make sure AQE skew-join is on, and if it's still skewed, salt the key - a two-stage aggregation for `groupBy`, or a salted join with the small side exploded across the salt values."

---

## Caching, Persist & Broadcast

Q. What is caching, in Spark?

A. (Teacher's definition) Caching - storing some frequently used data in memory so that it remains easily accessible during execution.

---

Q. What's a practical use case for caching?

A. (Teacher's definition) In Spark, a use case for caching might be that perhaps you are going to be doing a large number of joins between one table and a number of other tables - in that case, it may be advantageous to cache the one table, so that it can be accessed more easily.

Expanded: caching avoids redundant recomputation - by default (per Lazy Evaluation, above), Spark would otherwise recompute the same DataFrame's full transformation chain from scratch *every time* it's referenced by a new action or a new downstream operation. If one table is going to be joined against many other tables repeatedly, caching it means Spark computes it once and keeps the result readily available for every subsequent join, instead of re-reading and re-transforming it from the original source each time.

**Storage levels (the levels below actually belong to `persist()`, not `cache()` - see the cache vs. persist correction below):**

| Level | Meaning |
|---|---|
| Memory Only | Store data in memory only |
| Disk Only | Store data on disk only |
| Memory and Disk | Store in memory, spill to disk if it doesn't fit |
| Memory and Disk Serialized | Memory + disk, but data is serialized |
| Memory Only Serialized | Memory only, but data is serialized |

---

Q. What does "serialized" mean in this context, and why is it useful?

A. (Teacher's definition) Serialized means converting the data into a string of zeros and ones - this is useful in streaming.

Expanded: serialization converts in-memory objects into a compact byte representation - trading some CPU cost (to serialize/deserialize) for a smaller memory footprint.

Expanded (correction): serialized storage levels are not specifically a streaming feature. They are useful in **any** workload where cached data is too big for memory as plain objects: you spend CPU to deserialize on each read, and in return the cache takes much less space and creates less garbage-collection pressure. The streaming link is historical: the old DStream API stored received data with a serialized level (`MEMORY_AND_DISK_SER_2`) by default.

### Cache vs. Persist (Common Interview Question)

Q. What's the difference between `cache()` and `persist()`?

A. (Teacher's definition) It's actually PERSIST that has multiple levels, some of which involve only memory and others that involve disk only, and some combinations. Memory-only persist is equivalent to cache.

Expanded: the storage levels listed above (Memory Only, Disk Only, Memory and Disk, and their serialized variants) are `persist()`'s levels, configurable per call - `cache()` isn't a separate mechanism with its own levels, it's a shorthand for `persist()` with the default level.

Expanded (correction): "memory-only persist is equivalent to cache" is true for **RDDs only**. The default level depends on the API:

| API | `cache()` = | Default `persist()` level |
|---|---|---|
| RDD | `persist(StorageLevel.MEMORY_ONLY)` | `MEMORY_ONLY` - partitions that don't fit are recomputed from lineage |
| DataFrame / Dataset | `persist(StorageLevel.MEMORY_AND_DISK)` (PySpark 3.x shows it as `MEMORY_AND_DISK_DESER`) | `MEMORY_AND_DISK` - partitions that don't fit spill to local disk |

So `df.cache()` on a DataFrame already spills to disk; it is not memory-only. Both `cache()` and `persist()` are lazy: nothing is stored until the first action computes the data. Free it with `unpersist()`.

**Interview line:** "`cache()` is just `persist()` with the default storage level. For RDDs that's MEMORY_ONLY; for DataFrames it's MEMORY_AND_DISK. `persist()` lets me pick the level - for example DISK_ONLY or a serialized level when the data is big. Both are lazy and fill on the first action."

---

Q. Why would you use `persist()` (with a disk-involving level) instead of `cache()`?

A. (Teacher's definition) Disk only caching is equivalent to [using] persist. Persist stores frequently accessed data in the disk of every node rather than in memory. The reason one might use persist instead of cache would be if the table is too big to be efficiently cached in memory.

Expanded: this is the practical reason to reach for one of `persist()`'s disk-involving levels rather than plain `cache()`/Memory Only - if the dataset is too large to fit in the cluster's available RAM, a Memory Only cache either fails outright or forces Spark to recompute the uncached portion repeatedly (defeating the purpose of caching in the first place). A Disk Only or Memory and Disk level lets the data spill to each node's local disk instead, trading some read speed for reliability on datasets too big for memory.

Expanded (correction): "persist" does not mean "disk". `persist()` with no argument uses the same default as `cache()` (MEMORY_ONLY for RDDs, MEMORY_AND_DISK for DataFrames); it only uses disk-only storage when you pass `StorageLevel.DISK_ONLY`.

| | `cache()` | `persist()` |
|---|---|---|
| Storage levels | Only the default one | Any level you pass - Memory Only, Disk Only, Memory and Disk, serialized, replicated (`_2`) variants |
| Default | RDD: MEMORY_ONLY; DataFrame: MEMORY_AND_DISK | Same as `cache()` when called with no argument |
| When to prefer | Default level is fine | You need a specific level, e.g. `DISK_ONLY` for data much too big for memory |

**Caching vs checkpointing:** `cache`/`persist` keep the lineage (lost blocks are recomputed) and live only for the application. `checkpoint()` writes the data to reliable storage (HDFS/S3) and **cuts the lineage**, which is useful for very long lineages (iterative jobs) and is required for stateful streaming.

### Broadcast Variables and Broadcast Joins

Q. What is a broadcast variable?

A. (Teacher's definition) A broadcast variable is logically equivalent to a table that is cached in the memory of every single node in the cluster.

Expanded: this is the mechanism underneath the **BroadcastHashJoin** already introduced in the Joins subsection above - rather than shuffling a large table across the network to match keys with a small table, Spark instead copies ("broadcasts") the small table's full contents to every executor's memory once, so each executor can perform the join entirely locally against its own local copy. This is only practical for genuinely small tables (broadcasting a huge table to every node would cost far more memory/network than it saves), which is exactly why the Joins subsection framed it as Spark's alternative to a full sort-merge shuffle join for that specific case.

```python
df = spark.read.csv("my_file.csv")
broadcast_df = broadcast(df)
```

---

Q. What is a broadcast join, specifically, and why would you use one?

A. (Teacher's definition) Broadcast join - a join which will join a table that is not broadcast to a table which IS broadcast. The reason you might want to use a broadcast join is usually going to involve joining a very large table to a much smaller table.

---

Q. Why does this actually improve performance - what's the reasoning behind it?

A. (Teacher's definition) The reasoning behind it is that if you don't broadcast a table, then it will be distributed across the cluster. Therefore, if you broadcast *both* tables in the join, then the different nodes are going to need to ask each other for different parts of the data - this can tie up the local network and reduce the speed of processing. But when you broadcast the smaller table and distribute the larger table, what you have is a situation where the part of the larger table can be joined to the entire smaller table on each node. That means there is no need for any network requests - each part of the join can be performed entirely on the local system of each node, then the output table can be reassembled just like in normal Spark execution.

Expanded: this clarifies an easy-to-miss nuance - a broadcast join is asymmetric *by design*. The large table stays distributed across the cluster exactly as normal (each node holding its own partitions, per Spark's standard partitioning model), while only the small table gets copied in full to every node. That combination is what removes the network requests entirely: each node already has (a) its own local slice of the large table and (b) a full local copy of the small table, so the join for that slice can run entirely on local data - no node ever has to ask another node for a missing piece. This is also why broadcasting *both* tables wouldn't make sense here: the point isn't "avoid all data movement" in the abstract, it's specifically avoiding the *shuffle* that a sort-merge join would otherwise require to bring matching keys together across nodes - the large table doesn't need to move at all, only the small one does (once, up front, rather than repeatedly during a shuffle).

| Table role | What happens to it |
|---|---|
| Large table | Stays distributed across the cluster as normal - no shuffle, no movement |
| Small table | Broadcast - copied in full to every node's memory, once |
| Result | Each node joins its local slice of the large table against its full local copy of the small table - no network requests needed during the join itself |

| Term | What it is |
|---|---|
| Broadcast variable | A read-only copy of data sent to and cached in every executor's memory across the cluster |
| Broadcast join | A join between a large (non-broadcast, still-distributed) table and a small (broadcast) table - avoids a shuffle for the join entirely |
| When it's appropriate | The broadcast side must be small enough to comfortably fit in every executor's memory |

**Interview note (teacher's emphasis):** Broadcast joins are both good for efficiency and for interviews - they are one of the most commonly asked about Spark topics in interviews. Worth knowing cold alongside Data Skew (above) as one of the two heaviest-hitting Spark performance topics for interview prep.

---

## Anatomy of a Spark Application: Submission + HDFS Co-location

Q. What does the "Anatomy of a Spark Application" slide show?

A. How a cluster-mode submission, the Spark Master, workers/executors, and the HDFS layer fit together on the same machines.

Expanded (from the class slide "Anatomy of a Spark Application"): this slide ties the submission flow together with where the data physically lives, in a `--deploy-mode cluster` YARN-style setup:

1. A **Client** submits the application (`spark-submit`, `--deploy-mode cluster`).
2. The **Spark Master** (cluster manager) allocates resources - cores and memory - across the cluster for this application.
3. The **Driver** and **Executors** get launched onto **Spark Worker** nodes (per the Worker vs Executor section above - note the diagram shows multiple Executors per worker, confirming the cardinality point covered earlier).
4. Underneath, an **HDFS** layer stores the actual data: a **NameNode** tracks metadata while **DataNodes** hold the real blocks (matching `Training 0.md`'s HDFS coverage) - a large file (`/large/file`) is split into blocks (`A`, `B`, `C`, `D`) and each block is replicated with **replication factor 3** (`RF 3`) across different DataNodes, so no single DataNode failure loses any data.

**Key detail worth remembering - Spark/HDFS co-location:** the diagram marks one node as `DN + Spark`, meaning a single physical machine runs both an HDFS DataNode *and* a Spark Worker at the same time. This isn't incidental - co-locating Spark's compute (executors) on the same machines as HDFS's storage (DataNodes) is what enables **data locality**: Spark can schedule a task to run on the exact node that already holds the data block it needs, avoiding a network transfer entirely. This is a big part of why Hadoop/Spark clusters are traditionally deployed with compute and storage on the same hardware, rather than separated.

| Component | Role | Runs on |
|---|---|---|
| Client | Submits the application | Wherever `spark-submit` is run from |
| Spark Master | Allocates cluster resources (cores/memory) to the app | Dedicated master node |
| Driver | Coordinates the job (per Worker vs Executor, above) | A Spark Worker node (in `cluster` deploy mode) |
| Executors | Run tasks | Spark Worker nodes - multiple per worker |
| NameNode | Tracks HDFS metadata (block locations) | Dedicated master-role node |
| DataNode | Stores actual HDFS data blocks | Worker nodes - often co-located with Spark Workers (`DN + Spark`) |

---

## Interview-Level Reference Set

Q. Which `spark-submit` arguments are most important to know cold for interviews/troubleshooting?

A. (Teacher's definition) A good interview-level set to know cold is `--master`, `--deploy-mode`, `--class`, `--name`, `--conf`, `--driver-memory`, `--executor-memory`, `--executor-cores`, `--num-executors`, `--jars`, `--packages`, `--py-files`, `--files`, and `--archives`.

Expanded: this is effectively the union of the Core Arguments, Driver/Executor Resources, and Dependencies tables above - the flags that show up regardless of cluster manager, versus the cluster-manager-specific ones (`--queue`, `--supervise`, `spark.kubernetes.*`) which are more situational and worth recognizing but less critical to have memorized verbatim.

---

# The JVM (Java Virtual Machine)

Q. What capability does the JVM give us?

A. (Teacher's definition) The JVM gives us write once-run-anywhere capability.

Expanded: this is the JVM's core value proposition - code compiled for the JVM doesn't target a specific operating system or CPU architecture directly, so the same compiled artifact runs unmodified on Windows, Linux, or macOS, on any hardware, as long as a JVM is installed there. This is exactly why a JAR file (see the earlier "What is a JAR file" discussion in this session) is portable in the first place - it's compiled once into JVM bytecode, not into machine code for one specific OS/CPU, and it's also the underlying reason Spark clusters can mix heterogeneous machines and still run the same compiled application code on every node.

---

Q. How does the JVM actually execute code to achieve this?

A. (Teacher's definition) The way this is done is using the JVM to execute the code using a combination of compilation and interpretation.

Expanded: this is a two-stage process, not purely one or the other:

| Stage | What happens |
|---|---|
| 1. Compilation | Source code (Java, Scala, etc.) is compiled ahead of time into **bytecode** (`.class` files, bundled into a JAR) - a platform-independent intermediate format, not native machine code |
| 2. Interpretation (+ JIT compilation) | At runtime, the JVM interprets that bytecode instruction-by-instruction - and for code that runs frequently ("hot" code paths), the JVM's **Just-In-Time (JIT) compiler** additionally compiles those hot sections down into native machine code on the fly, so repeated execution gets faster over time |

This hybrid approach is what makes "write once, run anywhere" practical without sacrificing too much performance: the portable bytecode stays platform-independent, while JIT compilation claws back much of the speed a purely-interpreted language would otherwise lose. This is the same underlying execution model Scala and Spark's own JVM-based execution engine build on top of, which is why Scala/JAR-based Spark jobs and PySpark jobs (which still hand off to the JVM underneath for actual execution) both ultimately run through this same compile-then-interpret/JIT pipeline.

---

Q. What specifically does the compilation step (stage 1) produce?

A. (Teacher's definition) What happens is that the javac compiler will compile the code - but NOT to machine code. The compiled code is in a language similar to machine code which is called Java Bytecode.

Expanded: `javac` is the Java compiler itself, and this is the key distinction from a traditional compiled language like C - `javac` deliberately stops one level short of native machine code. **Java Bytecode** is a low-level, machine-code-*like* instruction set (hence the `.class` file extension), but it targets the JVM as an abstract machine rather than any real CPU/OS combination. It's this stopping point - compiling to bytecode instead of straight to machine code - that's the actual mechanism behind "write once, run anywhere": since every platform has its own JVM implementation able to run that same bytecode, the bytecode itself never needs to change per platform, only the JVM installed on each machine does.

| Term | What it is |
|---|---|
| `javac` | The Java compiler - turns `.java` source code into `.class` bytecode files |
| Java Bytecode | The compiled output - a machine-code-like instruction set, but targeting the JVM (an abstract machine), not a real CPU/OS |
| JVM | Interprets (and JIT-compiles) that bytecode into actual native machine code at runtime, per-platform |

---

Q. What is heap memory, in the context of the JVM?

A. (Teacher's definition) Heap memory is another concept in the JVM.

Expanded: in general JVM terms, the **heap** is the region of memory where the JVM allocates objects at runtime (as opposed to the stack, which holds method calls/local variables) and where garbage collection operates; this connects forward to `spark.executor.memoryOverhead` and executor memory tuning (touched on earlier in this file's `--executor-memory` coverage), since an executor's JVM heap sizing is a major factor in Spark out-of-memory errors and GC pauses.

**Executor memory model - on-heap vs off-heap (from the class slide):** a Worker can host multiple Executors (confirming the cardinality point from the Worker vs Executor section above), and each Executor has two distinct memory regions its Tasks read/write:

| Memory region | What it is | Managed by |
|---|---|---|
| On-heap memory | Standard JVM heap memory - where Spark objects normally live | The JVM's garbage collector - subject to GC pauses |
| Off-heap memory | Memory allocated outside the JVM heap | Managed by Spark itself directly, not the JVM's GC |

**Spark unified memory model (on-heap):** inside each executor's heap, Spark reserves ~300 MB, then splits the rest:

| Region | Size (defaults) | Used for |
|---|---|---|
| Unified memory | `spark.memory.fraction` = 0.6 of (heap - 300 MB) | Shared by **execution** memory (shuffles, joins, sorts, aggregations) and **storage** memory (cached data, broadcasts). Execution can evict cached blocks down to `spark.memory.storageFraction` (0.5) |
| User memory | The remaining 0.4 | Your own data structures, UDF objects, metadata |
| Overhead (outside the heap) | `spark.executor.memoryOverhead` = max(384 MB, 10%) | JVM internals, Python worker processes (PySpark), network buffers |

Common OOM / spill causes: a skewed partition, too few shuffle partitions (each one too big), `collect()` or a too-large broadcast (driver OOM), and PySpark UDFs exceeding the overhead (container killed by YARN with "exceeding memory limits" - raise `memoryOverhead`). When execution memory runs out, Spark **spills** to local disk instead of failing, which shows up as "Spill" in the Stages tab.

Each Executor's Tasks write to that executor's own **on-heap memory** as their primary working memory. The diagram also shows Tasks reaching out to a separate **off-heap memory** region - off-heap storage exists specifically to hold data (e.g. cached DataFrames) outside JVM heap management, which avoids garbage-collection overhead/pauses on that data (controlled via `spark.memory.offHeap.enabled`/`spark.memory.offHeap.size`). This is the practical payoff of the earlier JVM section's compilation/bytecode coverage - since Spark's executors are JVM processes, they inherit the JVM's GC behavior for on-heap memory by default, and off-heap memory is Spark's way of opting specific data out of that GC overhead when it would otherwise become a performance bottleneck.

---

## JVM Languages

Q. What is a "JVM language"?

A. (Teacher's definition) There is a family of languages called JVM languages - they are usually compatible with Java, and they use the JVM as their execution environment rather than developing their own. Scala is one of those languages.

Expanded: a JVM language is any programming language that compiles down to Java Bytecode and runs on the JVM, instead of building its own separate runtime/execution engine - it gets to reuse everything the JVM already provides (the bytecode format, the interpreter, JIT compilation, garbage collection, and "write once, run anywhere" portability) for free, rather than reinventing it. This is also why JVM languages are generally interoperable with Java and with each other - since they all compile to the same underlying bytecode, a Scala class can call Java code and vice versa, both running side-by-side on the same JVM instance.

| JVM Language | Notable for |
|---|---|
| Java | The original JVM language |
| Scala | Functional + object-oriented; the language Spark itself is written in |
| Kotlin | Modern, concise; common in Android development |
| Groovy | Scripting-oriented (used by Jenkinsfiles - see `Training 3.md`) |
| Clojure | Functional, Lisp-dialect JVM language |
| JRuby | Ruby implemented to run on the JVM |
| Jython | Python implemented to run on the JVM (distinct from PySpark, which runs CPython talking to the JVM via an interop layer rather than running Python code directly on the JVM) |

**Why this matters for Spark specifically:** Spark's core engine is written in Scala, which is precisely why Scala and Java (both JVM languages) can submit compiled JAR applications directly to `spark-submit` and run natively on the JVM Spark itself is built on - while PySpark instead runs Python code that talks to that same JVM engine underneath via an interop layer, rather than running Python directly *on* the JVM.

---

# Additional Notes (from class)

Additional material from class.

## Why isn't executor/hardware sizing decided automatically by Spark?

Q. If the optimizer already decides so much automatically (logical/physical plans, join strategy, etc.), why do you still have to manually calculate `--num-executors`/`--executor-memory`/`--executor-cores` yourself, rather than Spark just figuring out the hardware allocation too?

A. (Teacher's definition) "It's your responsibility as the programmer to write the spark submit command with the amount of hardware that you need already, because often what will happen in a professional environment... is that there are going to be multiple teams sharing the same cluster. If Spark decided the amount of hardware resources that it was going to use automatically, then that would mean that every time you run the Spark job it would use up either 100 percent or close to 100 percent of the entire cluster's resources, because there's no way for the software to know that it needs to reserve some compute for other teams. So that's why they've kept that as something that you have to decide as a human instead of just having Spark do it automatically. The logical plans and physical plans that the optimizer creates are going to be within the limitations that you have given it."

Expanded: this draws a sharp line between what Catalyst's optimizer *is* and *isn't* responsible for. The optimizer (per the Optimizer section above) freely decides the *strategy* for executing a job - join algorithms, predicate pushdown, partition planning - all without programmer input. But it never decides *how much of the cluster's total hardware* to claim, because on a real multi-tenant cluster (the teacher's JPMorgan Chase example in `Training 6.md`, where multiple teams shared one large cluster) nothing in Spark itself knows what other teams currently need. Auto-claiming resources would mean every job greedily grabs the whole cluster by default. This is why the executor-sizing math (cores/node ÷ 5, RAM/node ÷ executors-per-node, from the worked example above) is a human, `spark-submit`-time decision, not something the optimizer/AQE ever touches - AQE (also covered above) only ever adapts *within* the resource ceiling you already gave it, never expands past it.

---

## Salting vs. Hive Bucketing

Q. Is salting the same technique as bucketing in Hive?

A. (Teacher's definition) "The way that [salting] works is sort of analogous to the way that bucketing in Hive works, except that in Hive it's going to be based on a cryptographic hash, whereas with salting it is not necessarily going to be based on a hash."

Expanded: both techniques solve the same underlying problem - deliberately splitting data into a fixed number of evenly-sized buckets/partitions rather than letting natural key distribution decide - but they assign rows to buckets differently. Hive bucketing computes a cryptographic hash of the bucketing column and uses that hash (modulo the bucket count) to deterministically assign each row to the same bucket every time. Salting (per the Salting section above) instead just tacks on a random discrete value (e.g. `rand() * numSalts`, cast to int) as its own column and repartitions by that - there's no hashing involved, and the salt value carries no relationship to the row's actual content, it's purely there to spread rows evenly.

| | Hive Bucketing | Spark Salting |
|---|---|---|
| Assignment mechanism | Cryptographic hash of the bucketing column | Random discrete value, no hashing |
| Deterministic? | Yes - same row always hashes to the same bucket | No - salt value is randomly assigned each time |
| Where it lives | A property of how a Hive table is physically stored | A temporary column added, then dropped, during a Spark job |

Expanded (correction): Hive and Spark bucketing do **not** use a cryptographic hash (like SHA or MD5 - those would be needlessly slow). They use fast non-cryptographic hashes: Hive's hashCode-based function (Murmur3 for bucketing version 2 in Hive 3+), and Spark's Murmur3. The bucket is `hash(column) mod number_of_buckets`. Because Hive and Spark use different hash functions, Spark-written buckets are not compatible with Hive-written buckets. In the table above, read "cryptographic hash" as "deterministic hash".

---

## Broadcast Join Size Guideline

Q. Is there a concrete size threshold for what's safe to broadcast in a broadcast join?

A. (Teacher's definition) "You're only ever going to want to broadcast smaller tables, so generally the limit is considered to be about five gigabytes - that's of course going to change depending on how big the cluster that you're running is, but usually it's going to be a five gigabyte table or less that you might want to broadcast."

---

Q. How do you know how much memory a table will actually consume before deciding whether to broadcast it?

A. (Teacher's definition) "You can analyze how much data a table is going to consume... you just do that with a normal operation of checking the file size. If the file is five gigabytes, then when it's loaded into memory it's also going to be five gigabytes."

Expanded (correction): both numbers need fixing.

| Fact | Correct value |
|---|---|
| Automatic broadcast threshold | `spark.sql.autoBroadcastJoinThreshold` = **10 MB** by default. Spark only broadcasts automatically below this (AQE uses a similar runtime threshold) |
| Hard limit | A broadcast relation cannot exceed **8 GB**; Spark fails the query above that |
| Practical size | Tens to a few hundred MB. The table is collected to the **driver** first and then copied to **every executor**, so a 5 GB broadcast costs 5 GB+ on the driver and on each executor, and often causes OOM or timeouts |
| On-disk vs in-memory size | Not the same. Parquet/ORC are compressed and encoded, so the in-memory size is often **3-10x** the file size. Check Spark's estimate with `df.explain("cost")` or the SQL tab, not just the file size |

To broadcast something larger than 10 MB on purpose, use `broadcast(df)` or the `/*+ BROADCAST(t) */` hint (or raise the threshold), then confirm `BroadcastHashJoin` in `df.explain()`. Setting the threshold to `-1` disables automatic broadcasting.

**Interview line:** "Spark auto-broadcasts tables under 10 MB by default; I can force a bigger one with a broadcast hint, but it has to fit in driver and executor memory, the hard limit is 8 GB, and compressed Parquet gets several times bigger in memory."

Also worth noting the order of operations this implies: you decide what to broadcast *while writing the job's code* (based on the data itself), which happens independently of - and generally before - deciding the `spark-submit` executor memory/core settings covered earlier in this file.

---

## Repartitioning Carries No Data-Loss Risk

Q. When you repartition a DataFrame, is there any risk of losing data, or does it need to be backed up first?

A. (Teacher's definition) "There's no need to back up your data in repartitioning - when you partition the data, your output data is going to contain the exact same data as the input did, it's just that the data will be divided up differently. Spark will be equally able to read the data before it has been partitioned and after it has been partitioned."

Expanded: worth stating plainly since it's an easy thing to worry about - `repartition()`/`coalesce()` (covered in the Narrow vs Wide Dependencies section above) never drop or duplicate rows, they only change how the same complete dataset is physically split across partition boundaries. The teacher drew an explicit contrast here with repartitioning a hard drive (e.g. setting up a Windows/Linux dual-boot) - that's an unrelated, hardware-level operation (resizing disk partitions, cleaning up bad sectors) with real data-loss risk if done incorrectly; Spark's `repartition()` operates purely on data already loaded into a DataFrame/RDD, on disk in the sense of writing partition files, not on physical disk partitioning at all, so the two "repartition" concepts only share a name, not a mechanism or risk profile.

---

## Why the JVM Exists (Historical Motivation)

Q. Why does Java use a virtual machine at all, instead of compiling directly to machine code the way C/C++ do?

A. (Teacher's definition) "Before the 1990s when Java first came out... if you were working on serious applications then you were probably doing so in a language like C or C++... there is one little issue you can run into when you're trying to create production applications running on a large number of different customer machines: C and C++ applications are compiled to run on the specific processor they were written to run on. That creates a bit of an issue when you're trying to make an application commercially available, because what you'll wind up having to do is make a bunch of little adjustments and perhaps compile the code separately on a number of different machines just to guarantee that a customer can actually run it on their machine... One of the big features that the Java programming language had when it first came out was the write-once-run-anywhere feature. With Java, the Java Virtual Machine basically takes care of the compatibility issue for you, because there is a team at Oracle... that has some full-time dedicated people whose job is to ensure that the JVM is going to be compatible with any processor that you're likely to find on the market."

Expanded: this is the concrete historical problem the "write once, run anywhere" capability (already stated in the JVM section above) was actually invented to solve. Before the JVM, shipping a C/C++ application commercially meant either compiling separate builds per target processor architecture, or hiring engineers specifically to handle cross-platform compatibility - a real, costly burden for any software vendor. Java's answer was to centralize that burden: Oracle (Java's owner) maintains the JVM implementation for each platform, so any Java (or JVM-language) program compiles once to bytecode and Oracle's own JVM team - not the application developer - is responsible for making sure that bytecode runs correctly on whatever processor it ends up on (the teacher's concrete example: the same Java program, unmodified, runs identically on an x86 machine and on an Apple Silicon/ARM MacBook). This is the direct motivating story behind why `javac` deliberately stops at bytecode instead of compiling straight to machine code (per the "What specifically does the compilation step produce?" Q&A above).

---

## Predicate Logic's Historical Lineage (Optional Background)

Q. Where does the term "predicate" (as in predicate pushdown) actually come from?

A. (Teacher's definition, explicitly flagged as optional trivia) "Predicates are a reference to a kind of formal logic... that field is predicate logic, and predicate logic is one of the philosophical antecedents to SQL - there was a long philosophical tradition dating back to Aristotle of formal logic, and in the 20th century there was a guy by the name of Gottlob Frege, a German mathematician, who formalized [predicate logic]... the way predicate logic works was one of the intellectual underpinnings of logic programming, so things like Prolog - and logic programming is a direct ancestor of SQL." The teacher was explicit that "if you're not a data and philosophy enthusiast you don't necessarily need to know this" - it's background curiosity, not interview-relevant material, unlike the practical predicate pushdown mechanism itself (already covered in detail in the Optimizer section above).
