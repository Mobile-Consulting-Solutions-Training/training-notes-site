---
title: Study Guide - Day 7
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 7: Spark Submit, Architecture & Execution"
sidebar:
  order: 70
---

Study Guide - Day 7 (source: notes/Training 7.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**spark-submit.** The command that launches a Spark application onto a cluster. Learn its arguments by category: core (`--master`, `--deploy-mode`, `--class`, `--name`, `--conf`), driver/executor resources, dependencies, `--conf` properties, cluster-manager-specific flags, and application arguments. `spark-submit --help` lists them.

**Driver and Executor Resources.** `--driver-memory` = RAM for the driver (matters when collecting results). `--num-executors` = how many executors (YARN). `--executor-memory` = RAM per executor. `--executor-cores` = CPU cores per executor (one task per core). `--total-executor-cores` = standalone equivalent as a total budget.

**Executor Sizing Method.** Start from the hardware: nodes, cores per node, RAM per node. Use 5 cores per executor. Executors per node = cores ÷ 5 (round down). Executor memory = RAM ÷ executors per node (round down). Leftovers go to the OS. Worked example (10 nodes, 36 cores, 64 GB): 7 executors per node, 9g each → `--num-executors 70 --executor-cores 5 --executor-memory 9g`. Spark doesn't choose this itself because clusters are shared between teams; the optimizer works within the limits you give it.

**Dependencies.** Spark only ships the main file. `--jars` (local JARs), `--packages` (from Maven), `--py-files` (Python code), `--files` (config), `--archives` (environments). XML and Avro aren't built into Spark's reader and need packages. A JDBC driver is needed even from PySpark.

**--conf, Cluster Managers, App Arguments.** Most Spark settings are `spark.*` properties set with `--conf` (shuffle partitions, AQE, memory overhead, dynamic allocation). YARN adds `--queue`, `--principal`, `--keytab`; Standalone uses `spark://host:7077`, `--supervise` (auto-restart the driver); Kubernetes uses `--conf spark.kubernetes.*`. Anything after the application file goes to your application, not to spark-submit.

**Deploy Mode.** Controls where the **driver** runs. `client` = on the submitting machine (interactive, debugging; dies if you disconnect). `cluster` = on a cluster node (production).

**Worker, Executor, Driver.** A **worker** is a machine (node). An **executor** is a JVM process on a worker that runs tasks; usually several per worker. The **driver** coordinates the job. Older name for this shape: master-slave architecture.

**What Happens on spark-submit (also "Spark's architecture").** (1) Driver starts and reads config and logic; (2) optimizer builds a logical and a physical plan; (3) cluster manager distributes partitioned data to executors; (4) executors process their share; (5) results return to the driver through the cluster manager, are reassembled and written out.

**Catalyst Optimizer.** Decides the most efficient execution before the job runs. A **predicate** is anything that removes data (`WHERE`, `filter`). **Predicate pushdown** applies filters as early as possible, ideally at the source read. **Logical plan** = what to do (abstract); **physical plan** = how it runs on this cluster. Catalyst builds several candidates and picks the cheapest. Lazy evaluation exists so the whole chain can be optimized first.

**DAG.** Directed Acyclic Graph: nodes (steps) and directed edges, no loops. From graph theory; also used by Airflow. Acyclic in Spark: once you move to the next stage, you never go back.

**Adaptive Query Execution (AQE).** Spark 3.0's big feature (`spark.sql.adaptive.enabled=true`). After each stage it uses real runtime statistics to re-plan the rest of the job: switches join strategies (e.g. to broadcast), coalesces tiny shuffle partitions, splits skewed partitions. It doesn't learn across separate runs.

**Jobs, Stages, Tasks.** App (one spark-submit) → jobs (one per action) → stages (bounded by shuffles) → tasks (one per partition, the actual work). A stage = zero or more narrow transformations plus one wide transformation or action.

**Narrow, Wide, Actions.** Narrow = no shuffle; each output partition depends on one input partition (`map`, `filter`, `select`, `withColumn`, `union`, usually `coalesce`). Wide = shuffle; output depends on many input partitions (`groupBy`, `reduceByKey`, `distinct`, `orderBy`, `repartition`, window functions). Joins depend on strategy: sort-merge shuffles, broadcast doesn't. Actions return something other than a DataFrame/RDD and trigger execution (`show`, `collect`, `count`, `take`, writes). `cache`/`persist` are lazy markers. Mental model: does Spark need rows from other partitions? Verify with `df.explain()`.

**coalesce vs repartition.** `coalesce` combines partitions already on the same node: only reduces, no full shuffle, sizes can be uneven. `repartition` coalesces then shuffles: can increase or decrease, even sizes, always wide. Paying for `repartition` up front often beats the skew problems uneven partitions cause later. Repartitioning never loses data.

**Data Skew.** One executor has much more work than the others, so the whole job waits on it. Root cause: data not partitioned properly (uneven key distribution). More hardware doesn't fix it. Fixes: AQE (modern), better keys, `repartition`, **salting** (legacy): add a random salt column, `repartition(key, salt)`, drop the salt. Salting is like Hive bucketing, but random instead of hash-based.

**Cache, Persist, Broadcast.** **Cache** keeps frequently used data in memory (e.g. one table joined to many). `cache()` = `persist(MEMORY_ONLY)`; `persist()` has levels: memory only, disk only, memory and disk, and serialized variants. Use a disk level when data is too big for memory. **Broadcast variable** = a small table cached in every executor. **Broadcast join** = large table stays distributed, small table is copied to every node, so each node joins locally with no shuffle. Rule of thumb: broadcast tables of about 5 GB or less (file size ≈ memory size). One of the most asked Spark interview topics, with data skew.

**HDFS Co-location.** A node often runs both a DataNode and a Spark worker, so tasks can run where their data block already lives (**data locality**).

**The JVM.** Write once, run anywhere. `javac` compiles to **bytecode**, not machine code; the JVM interprets it and **JIT**-compiles hot code to native code. Invented because C/C++ needed separate builds per processor. **Heap** = where objects live and garbage collection runs; Spark can also use **off-heap** memory to avoid GC pauses. **JVM languages** (Java, Scala, Kotlin, Groovy, Clojure) compile to bytecode. Spark is written in Scala; PySpark talks to the JVM through an interop layer.

---

# Part 2: Cheat Sheet

## Must-Know Flags
- `--master` · `--deploy-mode` · `--class` · `--name` · `--conf`
- `--driver-memory` · `--executor-memory` · `--executor-cores` · `--num-executors`
- `--jars` · `--packages` · `--py-files` · `--files` · `--archives`
- YARN: `--queue`, `--principal`, `--keytab` · Standalone: `--supervise` · K8s: `--conf spark.kubernetes.*`
- Args after the app file → your app

## Sizing (identical nodes)
- `--executor-cores 5` · executors/node = cores ÷ 5 ↓ · memory = RAM ÷ executors/node ↓
- 10 × (36 cores, 64 GB) → 70 executors × 5 cores × 9g

## Deploy Mode
- `client` = driver on your machine (interactive) · `cluster` = driver in cluster (production)

## Architecture
- Worker = machine · Executor = JVM process (many per worker) · Driver = coordinator
- 5 steps: driver starts → plans → distribute → process → return + write

## Optimizer
- Catalyst · predicate pushdown (filter early) · logical (what) vs physical (how) · picks cheapest
- AQE (Spark 3.0): re-plans per stage · join switch · coalesce partitions · fix skew · not across runs

## Execution Hierarchy
- App → Job (per action) → Stage (per shuffle) → Task (per partition)
- Stage = narrow* + one wide or action

## Narrow / Wide / Action
- Narrow: `map`, `filter`, `select`, `withColumn`, `union`, `coalesce`
- Wide: `groupBy`, `reduceByKey`, `distinct`, `orderBy`, `repartition`, windows
- Depends: `join` (sort-merge vs broadcast) · Actions: `show`, `collect`, `count`, `take`, `write`
- `cache`/`persist` = lazy markers · check `df.explain()`

## Partitions and Skew
- `coalesce` ↓ only, local, uneven · `repartition` ↑↓, shuffle, even
- Skew = one slow executor · fix with AQE, keys, repartition, salting (legacy)

## Caching and Broadcast
- `cache()` = `persist(MEMORY_ONLY)` · persist levels incl. disk + serialized
- Broadcast join: small table (≤ ~5 GB) to every node, big table stays put, no shuffle

## JVM
- `javac` → bytecode → JVM interprets + JIT · heap (GC) vs off-heap
- JVM languages: Java, Scala, Kotlin, Groovy, Clojure

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What is spark-submit?
A: The command-line tool that launches a Spark application onto a cluster. Its flags say where it runs, how much compute it gets, what dependencies to ship and any Spark configuration.

Q: What's the difference between executor memory, executor cores and number of executors?
A: Executor memory is the RAM each executor gets, executor cores is how many tasks each executor runs at once, and number of executors is how many executor processes the job launches across the cluster.

Q: How do you size executors for 10 nodes with 36 cores and 64 GB each?
A: Use 5 cores per executor, so 36 divided by 5 gives 7 executors per node with a core left for the OS. 64 GB divided by 7 is about 9, so 9g each. Across 10 nodes that's 70 executors, 5 cores, 9g.

Q: Why doesn't Spark figure out the hardware allocation automatically?
A: Clusters are usually shared between teams. If Spark sized itself, every job would take nearly the whole cluster. You set the limits, and the optimizer works within them.

Q: When do you need --jars or --packages?
A: When your code needs a library that isn't part of Spark, like a JDBC driver or the Avro or XML readers. --jars ships a local JAR; --packages downloads it from Maven.

Q: How does spark-submit know which arguments belong to your program?
A: Everything after the application file is passed to your application. Flags before it belong to spark-submit.

Q: What's the difference between client and cluster deploy mode?
A: It's about where the driver runs. In client mode it runs on the machine you submitted from, which is good for debugging but dies if you disconnect. In cluster mode it runs inside the cluster, which is what production uses.

Q: What's the difference between a worker and an executor?
A: A worker is a machine in the cluster. An executor is a process Spark runs on that machine to do the work, and a worker usually runs several executors.

Q: What happens when you submit a Spark job?
A: The driver starts and reads the configuration and code. The optimizer builds a logical and physical plan. The cluster manager sends partitioned data to the executors, each executor processes its share, and the results come back to the driver to be assembled and written to the output.

Q: What is predicate pushdown?
A: Applying filters as early as possible, ideally while reading the source, so rows that will be thrown away never go through joins, shuffles or sorts.

Q: What's the difference between the logical plan and the physical plan?
A: The logical plan describes what has to happen to the data. The physical plan describes how it will actually run on this cluster, like which join algorithm to use. The optimizer builds several candidates and picks the cheapest.

Q: What is a DAG and why is it acyclic in Spark?
A: A directed acyclic graph: steps connected by one-way arrows with no loops. In Spark, once execution moves to the next stage it can't go back to a previous one. Airflow uses the same idea for pipelines.

Q: What does Adaptive Query Execution do?
A: Introduced in Spark 3.0, it re-optimizes the plan after each stage using real runtime statistics. It can switch to a broadcast join, coalesce tiny shuffle partitions and split skewed ones. It doesn't learn across separate runs.

Q: Explain jobs, stages and tasks.
A: An action triggers a job. The job is split into stages at shuffle boundaries. Each stage runs as tasks, one per partition, in parallel on executors.

Q: What's the difference between a narrow and a wide transformation?
A: A narrow transformation like map or filter works within each partition with no shuffle. A wide transformation like groupBy or distinct needs rows from other partitions, so it shuffles data and starts a new stage.

Q: Is a join narrow or wide?
A: It depends on the strategy. A sort-merge join shuffles both sides, so it's wide. A broadcast join copies the small table to every executor and doesn't shuffle. You check with explain.

Q: What is an action?
A: An operation that returns something other than a DataFrame or RDD, like count, collect, show or a write. Actions trigger execution of the lazy chain.

Q: What is lazy evaluation?
A: Transformations aren't run when you write them. Spark builds up the plan and only executes when it reaches a shuffle boundary or an action, which lets the optimizer see the whole chain first.

Q: What's the difference between coalesce and repartition?
A: Coalesce merges partitions already on the same node, so it avoids a full shuffle but can only reduce the count and sizes can be uneven. Repartition shuffles, can increase or decrease the count, and gives even sizes.

Q: When is repartition worth its extra cost?
A: When you need even partitions. Uneven partitions cause skew in every later stage, which usually costs more than the one upfront shuffle.

Q: What is data skew?
A: One executor gets far more data than the others, so the whole job waits on it while the rest sit idle. It comes from data that isn't partitioned evenly, and adding hardware doesn't fix it.

Q: How do you fix data skew?
A: Today AQE handles a lot of it automatically. You can also choose a better partition key, repartition, or use salting, which adds a random column, repartitions by key plus salt, and then drops the salt.

Q: What's the difference between cache and persist?
A: Cache is just persist with the memory-only level. Persist lets you choose levels like disk only or memory and disk, which you'd use when the data is too big for memory.

Q: What is a broadcast join and when do you use it?
A: You join a large table to a small one by copying the small table to every node. The large table stays distributed, so each node joins its slice locally with no shuffle. It's for small tables, about 5 GB or less.

Q: What does "write once, run anywhere" mean for the JVM?
A: Java compiles to bytecode instead of machine code, and each platform's JVM runs that bytecode, interpreting it and JIT-compiling hot paths. The same JAR runs on any machine with a JVM.

Q: What's the difference between on-heap and off-heap memory in an executor?
A: On-heap is normal JVM memory managed by the garbage collector, so it can pause. Off-heap is managed by Spark directly outside the JVM heap, which avoids GC overhead for things like cached data.
