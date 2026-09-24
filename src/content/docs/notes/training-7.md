---
title: Training 7 - Spark Submit, Architecture & Execution
description: spark-submit arguments and deploy modes, Spark's driver/executor architecture, Catalyst/AQE, jobs/stages/tasks, narrow vs. wide transformations, lazy evaluation, data skew/salting, caching/broadcast joins, and the JVM.
---

Teacher: Evan Flint

Syllabus Day 8 (per file numbering) - actual coverage: `spark-submit` CLI arguments and Spark deployment configuration. Note: this continues the pacing drift already visible in `Training 6.md` (which itself covered content closer to the roadmap's Day 8 topic) - this session's content lines up with the roadmap's Day 9/10 territory ("Hive + Spark Intro" / "Spark Advanced") rather than its own nominal Day 8 slot.

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

Q. What is `--driver-memory`?

A. (Teacher's definition) Driver memory is like executor memory, but it's for the driver application.

Expanded: same concept as `--executor-memory`, just applied to the single driver process instead of the (potentially many) executor processes - it's the RAM available to the process that builds the DAG, schedules tasks, and (importantly) collects results back from executors, e.g. via `.collect()`. Since there's only ever one driver per job (unlike executors, which can number in the dozens), sizing this is less about cluster-wide throughput and more about making sure the driver doesn't run out of memory when it has to hold a large collected result set or a very large execution plan in memory.

Q. What does `--num-executors` control?

A. (Teacher's definition) The number of executors which will be used in the job, distributed across the nodes.

Expanded: this is the total count of executor *processes* Spark will launch for the job - and per the Worker vs Executor section above, those executors get spread across the cluster's worker nodes, with a given worker commonly hosting several of them rather than just one.

Q. What does `--executor-memory` control?

A. (Teacher's definition) The amount of memory (RAM) which is allocated to each executor.

Expanded: this is a *per-executor* setting, not a per-worker or per-job total - each executor process gets this much RAM to hold cached data and run its assigned tasks. Since a worker often hosts multiple executors at once (per the cardinality point above), the actual RAM a single worker machine needs to support is roughly `(executors on that worker) x --executor-memory` - undersizing this per-executor value risks out-of-memory task failures, while oversizing it wastes RAM that could've gone to running more executors in parallel.

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

Q. In a standard situation with identical nodes, how do you calculate `--executor-cores`?

A. (Teacher's definition) In a standard situation, with identical nodes, the way that you calculate these numbers is to start with the number of CPU cores per node, then divide that by 5 - this will give you the number of cores per executor.

Expanded: the "5" here is itself the target `--executor-cores` value (a well-known Spark tuning rule of thumb, not arbitrary) - it caps each executor at around 5 concurrent tasks/threads, which is roughly the point past which HDFS client throughput and JVM garbage-collection behavior start to degrade if a single executor is given too many cores at once. Dividing a node's total cores *by* that fixed 5 doesn't recompute `--executor-cores` itself - it gives the **number of executors that fit on one node** (confirmed by the worked example below, where `36 / 5 = 7 executors`, not "7 cores per executor"). So the full picture is: `--executor-cores` = 5 (fixed starting point), and `executors per node` = `cores per node / 5`.

Q. Once you know the number of executors per node, how do you calculate `--executor-memory`?

A. (Teacher's definition) Once you have the number of executors for the node, you divide the amount of memory by the number of executors, and that will give you a figure for executor-memory.

Expanded: `--executor-memory` = `RAM per node / executors per node`. This is the same "divide the node's total resource by how many executors share the node" logic used for cores, just applied to RAM instead - each executor on a node gets an equal slice of that node's total memory.

**Worked example - an average case (10 nodes, 36 cores/node, 64 GB RAM/node):**

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

For the full cluster (10 nodes x 7 executors/node), this would give `--num-executors 70 --executor-cores 5 --executor-memory 9g` as the resulting `spark-submit` settings for this average-case hardware profile.

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

---

## Worker vs Executor

Q. What is a worker, in Spark?

A. (Teacher's definition) In Spark, a worker is a computer - it is the physical node on which the program is running, and it's part of the cluster.

Expanded: this draws a distinction that `Training 0.md`'s Driver/Executor coverage left implicit (it used "Worker/Executor" almost interchangeably) - a **worker** is the physical machine/node itself, while an **executor** (below) is the actual process that Spark launches *on* that worker to run tasks. This mirrors the same coordinator/many-hands shape noted back in `Training 3.md`'s Jenkins Controller/Agent comparison - there, "Agent" conflates machine-and-process the same way "worker" and "executor" can get conflated here, so it's worth keeping the two ideas separate.

Q. What is an executor, in Spark?

A. (Teacher's definition) An executor is a process, part of Spark's software, which runs on the nodes in the cluster.

Expanded: this confirms the distinction directly - an executor isn't the machine itself, it's a *process* (specifically, a JVM process that's part of Spark's own software) that Spark starts up on a worker node to actually execute tasks. A single worker node can potentially host one or more executor processes; the worker is the hardware/host, the executor is the running Spark process doing the work on it.

Q. Is it usually one executor per worker, or can a worker run more than one?

A. (Teacher's definition) In most Spark jobs, multiple executors will be running on one worker.

Expanded: this settles the cardinality question directly - it's not a 1:1 mapping. A single worker (physical/virtual machine) typically has multiple CPU cores and a large chunk of RAM, so rather than running just one large executor process, Spark commonly divides a worker's resources across several smaller executor processes running side-by-side on that same machine. This is exactly why `--executor-memory` and `--executor-cores` (from the Driver/Executor Resources table above) are sized *per executor*, not per worker - the total resources a worker contributes to a job is effectively `(executors on that worker) x (--executor-memory / --executor-cores)`, and getting that per-executor sizing right (not too big, not too small) is a core part of Spark cluster tuning.

Q. What was the older, "classic" terminology for this same coordinator/worker architecture?

A. (Teacher's definition) The standard terminology for the nodes in the cluster used to be that we have a master node and multiple worker nodes. That was the standard in Spark - the classic name for the architecture in which we have one node where the developer logs in and does the majority of the work, then that node controls all the other nodes in the cluster, was called the **master-slave architecture**.

Expanded: this is the historical name for the exact same shape already covered in `Training 0.md`'s "Master/Worker (Driver/Executor)" table entry - "master" maps to today's driver (the node the developer effectively works through, coordinating everything), and "slave" maps to today's worker nodes. The industry has broadly moved away from "master-slave" terminology (replaced with pairings like driver/executor, primary/replica, or leader/follower depending on the tool), but it's worth recognizing "master-slave" if it comes up in older docs, legacy codebases, or interview questions, since it describes the identical coordinator-and-many-workers architecture just under an older name.

| Era/Term | Coordinator | Workers |
|---|---|---|
| Classic ("master-slave") | Master node | Worker nodes (slaves) |
| Modern Spark terminology | Driver | Worker nodes, each running executor processes |

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
| 3. Cluster manager distributes data to executors | The cluster manager (YARN/standalone/Kubernetes) allocates the executors and hands each one its assigned partition(s) of data to work on | Cluster-Manager-Specific Arguments section above |
| 4. Executors process their share | Each executor runs its assigned tasks on its partition(s) in parallel with the others | Worker vs Executor section above |
| 5. Results return to the driver and get written out | Executors send their results back to the driver (routed through the cluster manager, not directly), the driver re-assembles the full output, and writes it to the final output location | Driver's role in the Driver/Executor split above |

**Worth noting:** step 5's detail that results are returned *through the cluster manager* rather than executors talking to the driver directly reinforces why the cluster manager isn't just a one-time resource allocator at job start - it stays involved as the coordination layer for the whole job's lifetime, not only at launch.

### The Optimizer (Step 2, in detail)

Q. What optimizer does Spark use to build the logical/physical plans in step 2, and what's its job?

A. (Teacher's definition) There are multiple optimizers which you could use, the most common ones are the default optimizer and the Catalyst optimizer. These days, usually the Catalyst optimizer is what's preferred. Its job is to determine before the job is executed what the most efficient way of performing the job will be.

Expanded: the optimizer is the component responsible for taking your DataFrame/SQL code and figuring out, ahead of time, the fastest way to actually execute it - this is why step 2 in the execution flow above happens *before* any data actually moves across the cluster. **Catalyst** is Spark SQL's own optimizer and is the modern default/preferred choice - it's what actually performs the logical-plan -> optimized-logical-plan -> physical-plan pipeline referenced in step 2 above, applying rule-based and cost-based optimizations (e.g. predicate pushdown, reordering joins, picking a join strategy) before any executor starts running real tasks. This is also the direct mechanism behind Spark's **lazy evaluation**, already noted in `Training 0.md`'s ETL coverage - transformations don't run immediately precisely because Spark is waiting to hand the full chain of transformations to the optimizer first, rather than executing each one eagerly as it's written.

| Term | What it is |
|---|---|
| Optimizer (general) | The component that decides the most efficient execution strategy for a job, before it runs |
| Catalyst optimizer | Spark SQL's modern, preferred optimizer - produces the logical and physical plans referenced in step 2 above |
| "Default optimizer" | Older/alternative optimizer path, generally superseded by Catalyst in modern Spark |

Q. What is a "predicate," in this context?

A. (Teacher's definition) Predicate - this is a reference to a field of formal logic which we don't need to super go into - but you just need to know that anything that removes data from the dataset can be considered a predicate - that includes the WHERE clause in SQL and the filter operation in Spark.

Expanded: rather than a strict formal-logic definition, the practical takeaway is simpler - a predicate is any condition that decides "keep this row or not," which in Spark/SQL terms means a `WHERE` clause or a `.filter()`/`.where()` call. This is the term that "predicate pushdown" (next) is named after.

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

Q. What is the logical plan, specifically?

A. (Teacher's definition) The logical plan is a high-level, formal plan that describes the operations that Spark will take in order to get the input data to be processed into the output data.

Q. What is the physical plan, specifically?

A. (Teacher's definition) The physical plan is the formal description of the low-level execution plan style steps that the computer will take to implement the logical plan.

Expanded: the two plans sit at different altitudes describing the *same* job. The **logical plan** answers "what needs to happen" (e.g. "filter these rows, then join these two datasets, then aggregate") without committing to *how* - it's an abstract description of the transformations, independent of the cluster's actual hardware. The **physical plan** answers "how will this actually run" - it takes that logical plan and turns it into concrete, low-level execution steps (which join algorithm to use, how data gets partitioned/shuffled, which operations can be combined into a single stage), tailored to the real cluster it's about to run on. This is the same logical -> physical progression already summarized in step 2 of the execution-flow table above, just broken out here in full detail.

Q. Does the optimizer only ever produce one logical plan and one physical plan?

A. (Teacher's definition) In most Spark jobs, the optimizer will create multiple logical plans and multiple physical plans, and based on what it knows about the cluster architecture, it will select the plan that it thinks is going to be the most efficient.

Expanded: this is the cost-based side of Catalyst's optimization process - rather than committing to the first valid plan it finds, Catalyst typically generates several *candidate* logical and physical plans (e.g. different join orderings, different join algorithms) and then picks whichever candidate it estimates will be cheapest to actually run, using what it knows about the data (statistics, size estimates) and the cluster (available executors/resources). This is why the same DataFrame code can execute differently - and with different performance - depending on the cluster it's submitted to, or as data volumes/statistics change over time.

| Plan | Answers | Altitude |
|---|---|---|
| Logical plan | *What* needs to happen to the data | High-level, abstract - independent of the cluster |
| Physical plan | *How* it will actually be executed | Low-level, concrete - tailored to the real cluster/hardware |
| Selection | Optimizer generates multiple candidates of each, picks the most efficient based on known data/cluster info | Cost-based optimization |

Q. What is a DAG, in the Spark context?

A. (Teacher's definition) Directed Acyclic Graph (DAG).

Expanded: `Training 0.md` already briefly touched on this ("Spark builds this into a DAG (Directed Acyclic Graph) of steps"). A DAG is a graph of nodes connected by directed edges (arrows) with no cycles - you can never follow the arrows back to a node you already visited. In Spark, the DAG represents the chain of transformations (per the Narrow vs Wide Dependencies section below) as a graph of dependencies between RDDs/DataFrames - it's the structure the logical plan above is built as, before Catalyst turns it into a physical plan.

Q. Is the DAG concept specific to Spark?

A. (Teacher's definition) The DAG is a Spark concept, but it comes from mathematics, specifically graph theory, and is used in other applications besides Spark, notably Apache Airflow, and can be applied in many cases.

Expanded: this connects forward to `Training 26.md`'s upcoming Apache Airflow coverage - Airflow uses the exact same DAG concept to represent a *pipeline* of tasks/dependencies (rather than Spark's chain of data transformations), which is why Airflow's own building block is literally called a "DAG" too. Recognizing DAG as a general graph-theory concept, not a Spark-specific invention, makes it easier to transfer this mental model directly onto Airflow (and any other tool built around directed, cycle-free dependency graphs) later in the course.

Q. Why is it called a "directed" graph specifically?

A. (Teacher's definition) It's a directed graph because it contains circles and lines, and the lines represent a direction moving from one circle to the next - in technical terms these are called nodes and edges.

Expanded: "circles" = **nodes** (the individual steps/RDDs/DataFrames in the chain), "lines" = **edges** (the connections between them) - and what makes it *directed* specifically is that each edge/line has a direction (drawn as an arrow), representing "this step happens, then flows into that step," not just an undirected connection. The "acyclic" half of DAG (already covered above) is the separate guarantee that following those directed edges can never loop back to a node already visited - together, "directed" (edges have a one-way flow) and "acyclic" (no loops) are what make a DAG a valid representation of a data pipeline, where earlier steps must always complete before later ones that depend on them.

| Term | Meaning |
|---|---|
| Node | A single step/vertex in the graph (e.g. one RDD/DataFrame transformation) |
| Edge | A directed connection between two nodes, showing which step flows into which |
| Directed | Every edge has a one-way direction - not simply "connected," but "flows from A to B" |
| Acyclic | No path of edges ever loops back to a node already visited |

Q. Why is it called an "acyclic" graph specifically, in the Spark context?

A. (Teacher's definition) It's an acyclic graph because once you have moved from one stage to the next, it is against the rules to go back to the previous stage.

Expanded: this grounds the general graph-theory "acyclic" definition (no loops, above) in Spark's own terms - once execution has advanced from Stage 0 to Stage 1 (per the Jobs, Stages, and Tasks section above), there's no rule or mechanism for going backwards to re-run Stage 0 as part of that same DAG. Data flows strictly forward through the chain of transformations, stage by stage, which is exactly why the RDD lineage example earlier in this file only ever has arrows pointing forward (`RDD 1 → RDD 2 → RDD 3 → RDD 4`) and never back.

### Adaptive Query Execution (AQE)

Q. What was the big feature introduced in Spark 3.0 for improving query efficiency during execution?

A. (Teacher's definition) Adaptive Query Execution. AQE was the big feature in Spark 3.0. AQE is a system that will continuously work to improve the efficiency of the Spark job during execution.

Q. How does AQE actually work?

A. (Teacher's definition) The basic way that it works is that instead of just selecting one logical plan and one physical plan, AQE will develop new plans after the execution of each stage - so as soon as Spark's execution goes from one stage to the next, AQE will collect data about the actual observed performance of the executors. Then it will create new logical and physical plans in order to further improve efficiency. It will do this as many times as necessary in order to improve efficiency. It can also automatically change partition sizes in order to avoid data skew.

Expanded: this is the key limitation AQE fixes in the plain Catalyst flow described above - without AQE, the optimizer picks its "most efficient" logical/physical plan **once**, up front, based only on estimates (statistics, size guesses) before any data has actually moved. Real execution can reveal those estimates were wrong (e.g. a join turns out far more skewed than expected). AQE addresses this by re-running the planning step **mid-job**: after each stage completes (recall from `Training 0.md`, a stage is a unit of work bounded by shuffle boundaries), AQE looks at what the executors *actually* observed - real data sizes, real partition distributions - and re-optimizes the remaining logical/physical plan for the stages still to come, repeating this re-planning as many times as there are stage boundaries. One concrete capability this enables: automatically resizing/coalescing partitions mid-job to correct for **data skew** (some partitions being far larger than others, which otherwise leaves some executors idle while one struggles through an oversized partition).

This directly explains the `spark.sql.adaptive.enabled=true` setting already shown in the Common Configuration Through `--conf` section earlier in this file - that flag is what turns AQE on.

**AQE's three concrete capabilities (per today's class summary):**
- Dynamically **changes join strategies** mid-query (e.g. switching to a broadcast join - see Broadcast Variables and Broadcast Joins, below - if a table turns out smaller than originally estimated)
- **Coalesces unnecessarily small shuffle partitions** (avoiding the overhead of scheduling/running many tiny tasks)
- **Detects and mitigates skewed partitions** (the data skew point already covered above)

**Important scope clarification:** AQE does **not** maintain a learning history across separate job *runs* - it only responds to runtime information gathered *during the current execution* (per-stage statistics, as described above), not to what happened the last time this same job ran. Persisted table/column statistics can separately feed into Catalyst's cost-based optimizer (CBO) when constructing the *initial* plan, before AQE ever kicks in - but that's a distinct mechanism from AQE's own mid-job adaptation.

| Without AQE | With AQE |
|---|---|
| One logical + physical plan, chosen once, before execution, based on estimates | Plan is re-evaluated after every stage, based on actual observed executor performance |
| Skewed partitions stay as originally planned | Partition sizes can be automatically adjusted mid-job to reduce skew |
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

Q. What exactly is a task?

A. (Teacher's definition) A task is an individual data processing operation that Spark performs - all actual commands that you pass to spark are tasks.

Expanded: this reframes "task" from a purely structural definition (one-per-partition, per the table above) to a functional one - a task is the actual unit of *work being done*, corresponding to whatever command(s) you write in your Spark code. Every task falls into one of three categories, covered next.

---

## Narrow vs Wide Dependencies (Transformations) and Actions

Q. What are the three categories every Spark task falls into?

A. (Teacher's definition) All tasks fall into one of three categories: narrow transformations, wide transformations, and actions.

Q. What is a narrow transformation?

A. (Teacher's definition) Narrow transformations are data processing operations which do NOT shuffle the data.

Q. What is a wide transformation?

A. (Teacher's definition) Wide transformations are operations which shuffle the data.

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

Expanded: this adds two important details beyond the "narrow vs wide" summary above. First, `coalesce()`'s mechanism specifically: it works *node-locally* - combining partitions that already live on the same node into fewer, larger partitions - which is exactly why it can avoid a full network shuffle, but also why it can only ever *decrease* partition count (you can't merge your way to more partitions than you started with), and why the resulting partitions can end up uneven in size (it's just grouping what's already there, not evenly redistributing). Second, `repartition()` isn't a totally separate operation from `coalesce()` - under the hood, it actually runs a coalesce step first, and *then* performs a full shuffle to redivide the data into the requested number of partitions, which is what lets it both increase *or* decrease partition count and guarantee more even sizing (unlike plain `coalesce()`).

| | `coalesce()` | `repartition()` |
|---|---|---|
| Can increase partition count? | No - can only reduce | Yes - can increase or decrease |
| Mechanism | Combines partitions already on the same node into fewer, larger ones | Internally coalesces first, then shuffles and redivides into the requested count |
| Guarantees equal partition sizes? | No | Yes (post-shuffle redistribution) |
| Shuffle? | Avoids a full shuffle (mostly narrow) | Always shuffles (wide) |

Q. Given that `repartition()` costs more compute than `coalesce()`, when is it worth choosing anyway?

A. (Teacher's definition) So repartition is going to be able to deliver even partition sizes, so while it is a more computationally expensive operation than coalesce, it's often necessary to pay the additional compute cost up front, because the problems you will have by operating on uneven partitions are worse down the road.

Expanded: this is the practical decision rule tying `coalesce()` vs `repartition()` directly back to the **Data Skew** section earlier in this file - uneven partitions are precisely what causes data skew (one executor stuck with an oversized partition while others idle), so choosing the cheaper `coalesce()` when partition sizes genuinely need to be balanced just defers that cost rather than avoiding it: you save on the shuffle now, but risk skew-driven slowdowns (or worse) throughout every downstream stage that has to work with those uneven partitions. `repartition()`'s upfront shuffle cost is a one-time, predictable expense; letting skew propagate downstream instead tends to cost more, less predictably, later in the job.

| Choice | Upfront cost | Downstream risk |
|---|---|---|
| `coalesce()` | Cheaper (avoids full shuffle) | Uneven partitions can cause data skew later in the job |
| `repartition()` | More expensive (always shuffles) | Even partitions - skew risk from partitioning itself is avoided |

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

## Lazy Evaluation

Q. Are all Spark operations lazily evaluated?

A. (Teacher's definition) All Spark operations are lazily evaluated.

Q. What does lazy evaluation actually mean?

A. (Teacher's definition) Lazy evaluation is the principle that operations are not performed until the data is shuffled, and therefore taken from one stage to the next.

Q. What is a stage, defined in terms of lazy evaluation and transformations?

A. (Teacher's definition) Stages are groups of tasks which are lazily evaluated. A stage will consist of zero or more narrow transformations, and at least one wide transformation or action.

Expanded: this is a more precise, mechanical restatement of the lazy-evaluation idea already touched on briefly in `Training 0.md` ("Spark builds this into a DAG... and only actually runs it when an action... is triggered"). Put together with the Narrow vs Wide Dependencies section above, this gives a formal recipe for what a stage actually *is*: a stage accumulates zero or more narrow transformations (`map`, `filter`, `flatMap` - none of which need to move data, so nothing has to execute yet) and always ends with either a wide transformation (a shuffle boundary, forcing the next stage to begin) or an action (which triggers real execution of the whole accumulated chain). Nothing actually runs - no tasks execute on any executor - until one of those two triggering events happens; narrow transformations are only ever building up the logical/physical plan (from the Optimizer section above), never executing on their own.

| Stage composition rule | Meaning |
|---|---|
| Zero or more narrow transformations | Can chain freely - `map`, `filter`, `flatMap`, etc. - without triggering execution or a new stage |
| ...followed by exactly one wide transformation or action | Where the stage actually ends - a wide transformation starts a *new* stage (shuffle boundary), an action triggers execution of the whole job so far |

Worked through the RDD lineage example above: `flatMap() -> map()` are the "zero or more narrow transformations" making up Stage 0, and `reduceByKey()` is the wide transformation that both closes Stage 0 and opens Stage 1 - matching this rule exactly.

---

## Data Skew

Q. How important is data skew as an interview topic?

A. (Teacher's definition) Data Skew - one of the most commonly talked about problems that can happen in a Spark program in interviews. It can also be referred to as Skewness.

Q. What is data skew, from the Spark execution perspective?

A. (Teacher's definition) Data skew (from the Spark execution perspective) is a situation where one of the executors needs to do more work than the other executors do - therefore, it's going to take a longer time than the other executors - therefore, the job as a whole is going to be delayed because of the one trailing executor.

Expanded: this is the practical cost of an uneven **shuffle** (per the Narrow vs Wide Dependencies section above) - when a wide transformation like `groupBy()`/`reduceByKey()`/a sort-merge `join()` redistributes data by key, some keys can be far more common than others (e.g. one `department` or `customer_id` has 10x the rows of the rest). Since each partition/task is tied to a set of keys, that means one executor ends up with a disproportionately large partition to process, while the other executors finish their (smaller, evenly-sized) partitions quickly and then sit idle. Because a Spark **job** only completes when *all* its tasks finish (per the Jobs, Stages, and Tasks section above), the entire job's total runtime is bottlenecked by that one slow, overloaded executor - adding more executors or more cluster resources doesn't fix this, since the problem isn't total capacity, it's an uneven *distribution* of the work.

This is exactly the problem **AQE** (covered earlier in this file) directly targets - recall AQE "can also automatically change partition sizes in order to avoid data skew," re-planning partition boundaries mid-job based on actually-observed executor performance rather than the pre-execution estimate that caused the imbalance in the first place.

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
| Spark's built-in mitigation | AQE (Adaptive Query Execution) can automatically resize/split skewed partitions mid-job |

### Salting (Legacy Skew Mitigation)

Q. What is salting, and is it still commonly used?

A. (Teacher's definition) Salting is a way to partition data which is somewhat outdated these days. AQE has pretty much completely taken the place of salting.

Q. How does salting actually work?

A. (Teacher's definition) What salting is is that what we do is add a new column to our existing data, which contains multiple discrete values, a different one for each number of rows that we want for our partition.

Expanded: salting was the manual, proactive technique for the skew problem described above - instead of shuffling by the original skewed key alone (e.g. a `customer_id` with a disproportionate row count), you engineer a new "salt" column holding a small set of discrete values (e.g. a random number from 0-9), and shuffle/partition by the *combination* of the original key plus that salt value. This artificially splits what would have been one oversized partition (all rows for that one heavy key) into several smaller ones (one per salt value), spreading that key's rows across multiple executors instead of dumping them all on one. It's listed here as **legacy** specifically because AQE (covered above) now handles this same rebalancing automatically and dynamically, based on real observed data at runtime, removing the need to manually engineer a salt column ahead of time - which is why the root-cause section above lists salting as one of the *older* proactive fixes, now largely superseded by AQE's reactive approach.

Q. What are the concrete steps for applying salting?

A. (Teacher's definition) What you do is that you add a new column that has these distinct values, then you use the `repartition()` method to adjust the partition sizes based on the values of the salted key column. Then, after the partitioning is done, the salted key column is removed because it's no longer needed.

Expanded: three steps, matching what was just introduced above - (1) add the synthetic salt column with its discrete values, (2) call `repartition()` (a **wide transformation**, per the Narrow vs Wide Dependencies section above - it's what actually forces the shuffle/redistribution) using the combined original-key-plus-salt as the partitioning key, then (3) drop the salt column once partitioning has already happened, since it was only ever a temporary tool to influence *how* the shuffle spread the data - it carries no meaning in the actual dataset and would just be dead weight in the final output.

```python
# 1. Add a salt column with discrete values
salted = df.withColumn("salt", (rand() * 10).cast("int"))

# 2. Repartition using the original key + salt
salted = salted.repartition("customer_id", "salt")

# 3. Drop the salt column - no longer needed after partitioning
result = salted.drop("salt")
```

| Approach | How it works | Status |
|---|---|---|
| Salting | Add a synthetic salt column → `repartition()` by (original key + salt) → drop the salt column once partitioning is done | Legacy - largely superseded |
| AQE | Automatically detects and re-splits skewed partitions mid-job, based on real observed performance | Modern default |

---

## Caching, Persist & Broadcast

Q. What is caching, in Spark?

A. (Teacher's definition) Caching - storing some frequently used data in memory so that it remains easily accessible during execution.

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

Q. What does "serialized" mean in this context, and why is it useful?

A. (Teacher's definition) Serialized means converting the data into a string of zeros and ones - this is useful in streaming.

Expanded: serialization converts in-memory objects into a compact byte representation - trading some CPU cost (to serialize/deserialize) for a smaller memory footprint, which matters most in streaming workloads where data is continuously flowing through and memory pressure is a constant concern rather than a one-time job cost.

### Cache vs. Persist (Common Interview Question)

Q. What's the difference between `cache()` and `persist()`?

A. (Teacher's definition) It's actually PERSIST that has multiple levels, some of which involve only memory and others that involve disk only, and some combinations. Memory-only persist is equivalent to cache.

Expanded: this is the corrected, accurate version of the relationship - worth flagging explicitly since it's easy to mix up (and the teacher raised it specifically as a common interview trap). The five storage levels listed above (Memory Only, Disk Only, Memory and Disk, and their serialized variants) are `persist()`'s levels, configurable per call - `cache()` isn't a separate mechanism with its own levels, it's simply a shorthand for `persist()` using the Memory Only level. So `df.cache()` and `df.persist(StorageLevel.MEMORY_ONLY)` do the same thing; `persist()` is the more general, configurable operation underneath.

Q. Why would you use `persist()` (with a disk-involving level) instead of `cache()`?

A. (Teacher's definition) Disk only caching is equivalent to [using] persist. Persist stores frequently accessed data in the disk of every node rather than in memory. The reason one might use persist instead of cache would be if the table is too big to be efficiently cached in memory.

Expanded: this is the practical reason to reach for one of `persist()`'s disk-involving levels rather than plain `cache()`/Memory Only - if the dataset is too large to fit in the cluster's available RAM, a Memory Only cache either fails outright or forces Spark to recompute the uncached portion repeatedly (defeating the purpose of caching in the first place). A Disk Only or Memory and Disk level lets the data spill to each node's local disk instead, trading some read speed for reliability on datasets too big for memory.

| | `cache()` | `persist()` |
|---|---|---|
| Storage levels | Only one - Memory Only | Configurable - Memory Only, Disk Only, Memory and Disk, and serialized variants |
| Relationship | Shorthand for `persist(MEMORY_ONLY)` | The general, underlying operation |
| When to prefer | Data comfortably fits in memory | Data too large to efficiently fit in memory - use a disk-involving level instead |

### Broadcast Variables and Broadcast Joins

Q. What is a broadcast variable?

A. (Teacher's definition) A broadcast variable is logically equivalent to a table that is cached in the memory of every single node in the cluster.

Expanded: this is the mechanism underneath the **BroadcastHashJoin** already introduced in the Joins subsection above - rather than shuffling a large table across the network to match keys with a small table, Spark instead copies ("broadcasts") the small table's full contents to every executor's memory once, so each executor can perform the join entirely locally against its own local copy. This is only practical for genuinely small tables (broadcasting a huge table to every node would cost far more memory/network than it saves), which is exactly why the Joins subsection framed it as Spark's alternative to a full sort-merge shuffle join for that specific case.

```python
df = spark.read.csv("my_file.csv")
broadcast_df = broadcast(df)
```

Q. What is a broadcast join, specifically, and why would you use one?

A. (Teacher's definition) Broadcast join - a join which will join a table that is not broadcast to a table which IS broadcast. The reason you might want to use a broadcast join is usually going to involve joining a very large table to a much smaller table.

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

Q. How does the JVM actually execute code to achieve this?

A. (Teacher's definition) The way this is done is using the JVM to execute the code using a combination of compilation and interpretation.

Expanded: this is a two-stage process, not purely one or the other:

| Stage | What happens |
|---|---|
| 1. Compilation | Source code (Java, Scala, etc.) is compiled ahead of time into **bytecode** (`.class` files, bundled into a JAR) - a platform-independent intermediate format, not native machine code |
| 2. Interpretation (+ JIT compilation) | At runtime, the JVM interprets that bytecode instruction-by-instruction - and for code that runs frequently ("hot" code paths), the JVM's **Just-In-Time (JIT) compiler** additionally compiles those hot sections down into native machine code on the fly, so repeated execution gets faster over time |

This hybrid approach is what makes "write once, run anywhere" practical without sacrificing too much performance: the portable bytecode stays platform-independent, while JIT compilation claws back much of the speed a purely-interpreted language would otherwise lose. This is the same underlying execution model Scala and Spark's own JVM-based execution engine build on top of, which is why Scala/JAR-based Spark jobs and PySpark jobs (which still hand off to the JVM underneath for actual execution) both ultimately run through this same compile-then-interpret/JIT pipeline.

Q. What specifically does the compilation step (stage 1) produce?

A. (Teacher's definition) What happens is that the javac compiler will compile the code - but NOT to machine code. The compiled code is in a language similar to machine code which is called Java Bytecode.

Expanded: `javac` is the Java compiler itself, and this is the key distinction from a traditional compiled language like C - `javac` deliberately stops one level short of native machine code. **Java Bytecode** is a low-level, machine-code-*like* instruction set (hence the `.class` file extension), but it targets the JVM as an abstract machine rather than any real CPU/OS combination. It's this stopping point - compiling to bytecode instead of straight to machine code - that's the actual mechanism behind "write once, run anywhere": since every platform has its own JVM implementation able to run that same bytecode, the bytecode itself never needs to change per platform, only the JVM installed on each machine does.

| Term | What it is |
|---|---|
| `javac` | The Java compiler - turns `.java` source code into `.class` bytecode files |
| Java Bytecode | The compiled output - a machine-code-like instruction set, but targeting the JVM (an abstract machine), not a real CPU/OS |
| JVM | Interprets (and JIT-compiles) that bytecode into actual native machine code at runtime, per-platform |

Q. What is heap memory, in the context of the JVM?

A. (Teacher's definition) Heap memory is another concept in the JVM.

Expanded: in general JVM terms, the **heap** is the region of memory where the JVM allocates objects at runtime (as opposed to the stack, which holds method calls/local variables) and where garbage collection operates; this connects forward to `spark.executor.memoryOverhead` and executor memory tuning (touched on earlier in this file's `--executor-memory` coverage), since an executor's JVM heap sizing is a major factor in Spark out-of-memory errors and GC pauses.

**Executor memory model - on-heap vs off-heap (from the class slide):** a Worker can host multiple Executors (confirming the cardinality point from the Worker vs Executor section above), and each Executor has two distinct memory regions its Tasks read/write:

| Memory region | What it is | Managed by |
|---|---|---|
| On-heap memory | Standard JVM heap memory - where Spark objects normally live | The JVM's garbage collector - subject to GC pauses |
| Off-heap memory | Memory allocated outside the JVM heap | Managed by Spark itself directly, not the JVM's GC |

Each Executor's Tasks write to that executor's own **on-heap memory** as their primary working memory. The diagram also shows Tasks reaching out to a separate **off-heap memory** region - off-heap storage exists specifically to hold data (e.g. cached DataFrames) outside JVM heap management, which avoids garbage-collection overhead/pauses on that data (controlled via `spark.memory.offHeap.enabled`/`spark.memory.offHeap.size`). This is the practical payoff of the earlier JVM section's compilation/bytecode coverage - since Spark's executors are JVM processes, they inherit the JVM's GC behavior for on-heap memory by default, and off-heap memory is Spark's way of opting specific data out of that GC overhead when it would otherwise become a performance bottleneck.

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
