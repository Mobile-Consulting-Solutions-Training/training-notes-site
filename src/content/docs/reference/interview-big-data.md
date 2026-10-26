---
title: "Interview Questions: Big Data"
description: "Interview questions with the class answer, a corrected expanded answer and a short answer to say out loud: Spark, Kafka, Hadoop, Clusters, Hive, HBase, Cassandra, MongoDB, Data Lakes, Warehouses, and Lakehouses, Data Formats, Elastic Stack."
sidebar:
  order: 12
---

Each question has three parts: **A. (Class answer)**, the answer from the class question bank as given; **Expanded**, a corrected and fuller explanation (starting with **Correction:** when the class answer was wrong); and **Say it out loud**, a short answer for the interview itself. Start with the [traps to unlearn](/training-notes-site/reference/interview-prep/#traps-to-unlearn).

## Spark


**Q. Describe the architecture of Spark**

**A. (Class answer)**

Sparks architecture involves 3 major components, the driver, the executors, and the cluster manager.

The driver, also called the driver application, is the application that we write when developing Spark jobs.

The executors are JVM processes the run on Sparks worker nodes. The number of them on each node will depend on the requirements of the job. Their function is to process the data in parallel.

The cluster manager is the component that organizes the other components. It makes decisions about which tasks to send to which executors and how many resources to provide to which part of the cluster. If we are running Spark on a Hadoop system, we use YARN as the cluster manager, but we can use Sparks standalone cluster manager when doing testing, and we can also use Kubernetes for the cluster manager if working on a Kubernetes system.

(Note: do not mention Mesos, nobody uses it)

**Expanded:**

**Correction:** The cluster manager does **not** decide which tasks go to which executors. The **driver** does that: its DAGScheduler splits the job into stages and its TaskScheduler sends each task to an executor, preferring executors that already hold the data. The cluster manager only **allocates resources**: it launches executor processes (containers or pods) when the driver asks for them. Also, Spark's standalone manager is a real multi-node cluster manager that can run in production. It is not just for testing. Testing on a laptop is **local mode** (`--master local[*]`), which uses no cluster manager at all.

| Component | Where it runs | What it does |
|---|---|---|
| Driver | The submitting machine (client mode) or a container inside the cluster (cluster mode) | Runs your `main` program, creates the SparkSession, builds and optimizes the plan, splits it into stages and tasks, schedules the tasks, collects results, serves the Spark UI (port 4040) |
| Executors | JVM processes on worker nodes | Run tasks in parallel (one task per core at a time), cache data, write shuffle files, read inputs and write outputs |
| Cluster manager | Its own service (YARN ResourceManager, Kubernetes API server, standalone master) | Grants CPU and memory, starts and restarts executor containers |

The teacher's advice to skip Mesos is sound: Mesos support was deprecated in Spark 3.2.

See [Training 7 notes](/training-notes-site/notes/training-7/) ("What Happens When You Run `spark-submit`" and "Worker vs Executor").

**Say it out loud:** "A Spark application has a driver, executors and a cluster manager. The driver turns my code into an optimized plan of stages and tasks and schedules those tasks. The executors are JVM processes on the worker nodes that run the tasks in parallel. The cluster manager, such as YARN or Kubernetes, only hands out the CPU and memory for those executors."

---

**Q. Difference between RDD and DF**

**A. (Class answer)**

RDDs are the most basic data structure in Spark, which behave like arrays in other programming languages.

DataFrames are the most common data structure used in Spark today, and they resemble SQL tables. They have rows, columns, and a schema.

DataFrames are actually an abstraction over RDDs, so they act as syntactic sugar. Spark's engine interprets them as RDDs for the purposes of data processing.

**Expanded:**

**Correction:** A DataFrame is more than syntactic sugar over an RDD. It has a **schema**, so Spark's **Catalyst optimizer** can rewrite the query (push filters down, prune columns, pick a join strategy) and the **Tungsten** engine can store rows in a compact binary format and generate code for them. The final physical plan does run as RDD operations internally, but a DataFrame job is usually much faster than the same logic written by hand with RDDs. This is also why PySpark DataFrame code runs about as fast as Scala: the plan executes in the JVM.

| | RDD | DataFrame |
|---|---|---|
| What it is | Immutable, partitioned, distributed collection of objects | Distributed table of rows with named, typed columns |
| Schema | None (Spark sees opaque objects) | Yes |
| Optimization | None. Spark runs your functions exactly as written | Catalyst optimizer + Tungsten code generation |
| API | Functional: `map`, `filter`, `reduceByKey` | SQL-like: `select`, `where`, `groupBy`, or plain SQL |
| When to use | Low-level control, unstructured data, legacy code | Almost everything today |

An RDD is closer to a distributed list than an array: you can't index into it by position.

**Say it out loud:** "An RDD is Spark's low-level distributed collection with no schema, so Spark can't optimize it. A DataFrame adds a schema, which lets the Catalyst optimizer and Tungsten engine optimize the whole query, so DataFrames are the default choice and usually faster."

---

**Q. Transformation vs Action**

**A. (Class answer)**

Transformations and actions are both categories of tasks in Spark's processing engine.

A transformation is any task that accepts an RDD and returns a modified RDD. Examples include map and filter.

An action is any task that accepts an RDD and returns something other than an RDD. Examples include collect and count.

**Expanded:** Transformations are **lazy**: they return a new RDD or DataFrame and only add a step to the plan (`map`, `filter`, `select`, `withColumn`, `join`, `groupBy`). Actions **trigger execution**. They either return a result to the driver (`count`, `collect`, `take`, `show`, `first`) or write data out (`write.parquet(...)`, `saveAsTextFile`, `foreach`). Each action starts at least one **job**.

Terminology note: in Spark, "task" has a specific meaning (one unit of work on one partition, see the jobs/stages/tasks question below), so it is clearer to call transformations and actions *operations*.

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Narrow vs Wide Dependencies (Transformations) and Actions").

**Say it out loud:** "Transformations like `filter` or `join` are lazy and just build up the plan. An action like `count`, `collect` or a `write` is what makes Spark actually run a job."

---

**Q. Narrow transformation vs Wide transformation**

**A. (Class answer)**

A narrow transformation is any kind of transformation which does not shuffle the data, and therefore does not constitute the end of a stage or job. Examples include map and filter.

A wide transformation is any kind of transformation which shuffles the data, and therefore constitutes a shift from one stage to the next. Examples include reduceByKey, groupByKey, and join.

**Expanded:** The precise definition is about **partition dependencies**:

| | Narrow | Wide |
|---|---|---|
| Each output partition depends on | One input partition | Many input partitions |
| Shuffle? | No | Yes |
| Stage boundary? | No, many narrow steps are pipelined in one stage | Yes, a new stage starts after the shuffle |
| Examples | `map`, `filter`, `select`, `withColumn`, `union`, `coalesce` | `groupBy`/`groupByKey`, `reduceByKey`, `distinct`, `orderBy`, `repartition`, most joins |

A join is wide only when both sides must be shuffled. A **broadcast join** avoids the shuffle of the large side. A wide transformation ends a **stage**, not a job. Only an action creates a job.

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Narrow vs Wide Dependencies" and the "Joins" section that follows it).

**Say it out loud:** "In a narrow transformation each output partition comes from one input partition, so there's no shuffle and Spark can pipeline it inside one stage. In a wide transformation like `groupBy` or a join, an output partition needs data from many partitions, so Spark shuffles and starts a new stage."

---

**Q. What is lazy evaluation**

**A. (Class answer)**

Lazy evaluation is the principle in Spark tasks are not executed until a shuffle or action is performed. This allows Spark's optimizer to find potential ways of executing the same series of tasks in a more efficient way.

**Expanded:**

**Correction:** Only an **action** triggers execution. A shuffle does not. A shuffle is just a stage boundary in the plan, and a chain of transformations that includes several shuffles still does nothing until an action is called.

Because Spark waits, it sees the whole chain of transformations before running anything. The optimizer can then combine steps, push filters down to the data source, read only the needed columns, and skip work whose result is never used.

```python
df = spark.read.parquet("s3://bucket/sales/")   # nothing runs yet
big = df.filter("amount > 100").select("id")    # still nothing
big.count()                                     # action: now Spark plans and runs a job
```

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Lazy Evaluation").

**Say it out loud:** "Lazy evaluation means transformations only build a plan, and nothing runs until an action like `count` or `write`. That lets Spark optimize the whole pipeline at once, for example by pushing filters down and reading only the columns it needs."

---

**Q. What happens when you submit a spark job**

**A. (Class answer)**

NOTE: The answer to this question is similar to a general question about Spark's architecture and should be treated as such.

When a Spark job is submitted with spark-submit, the first thing that happens is that the driver application is run. The tasks to be performed are gathered and sent to Spark's optimizer, which constructs a logical plan and a physical plan in for executing them in the most efficient way possible.

After the plans have been selected, the job is sent to Spark's cluster manager, which divides the data among the executors running on the worker nodes and provisions resources according to the parameters specified in the spark-submit command and/or the Spark config.

The executors then begin processing the data in parallel. When they are finished, they return the data to the cluster manager, which directs them to the output location specified in the driver.

**Expanded:**

**Correction:** Executors do not return data to the cluster manager, and the cluster manager does not direct output. Executors report task status (and small results) **directly to the driver**, and they **write output files themselves**, straight to HDFS or S3. Also, the plan is not "sent to the cluster manager". The driver schedules the tasks itself. The cluster manager only provides the executors.

The real sequence:

1. `spark-submit` starts the **driver**: on your machine in client mode, or in a container in the cluster in cluster mode.
2. The driver creates the SparkSession and asks the **cluster manager** for executors, using the resources you requested (`--num-executors`, `--executor-memory`, etc.).
3. The cluster manager starts the **executors** on worker nodes, and they register with the driver.
4. Your code runs. Transformations only build a logical plan. When an **action** is reached, Catalyst optimizes the plan into a physical plan.
5. The driver's DAGScheduler splits the plan into **stages** at shuffle boundaries. The TaskScheduler creates one **task per partition** and sends tasks to executors, preferring data locality.
6. Executors run the tasks, exchange shuffle data with each other, and report back to the driver. Output is written directly from the executors to storage.
7. When the application ends, the driver stops and the cluster manager releases the resources.

See [Training 7 notes](/training-notes-site/notes/training-7/) ("What Happens When You Run `spark-submit`").

**Say it out loud:** "spark-submit starts the driver, which asks the cluster manager like YARN for executors. When my code hits an action, the driver optimizes the plan, breaks it into stages at the shuffles and sends one task per partition to the executors. The executors run the tasks, report back to the driver, and write the output straight to HDFS or S3."

---

**Q. Client mode vs cluster mode**

**A. (Class answer)**

Client mode is a setting in Spark which is used for small-scale experimentation and testing, and is what should be used when developing Spark jobs on a laptop.

Cluster mode is for executing distributed processing jobs on a compute cluster. It is what should be used when executing a Spark job for practical data processing.

**Expanded:**

**Correction:** This answer mixes up **client mode** with **local mode**. `--deploy-mode` only decides **where the driver runs**. Both client and cluster mode use a real cluster. Running on a laptop for testing is local mode (`--master local[*]`).

| Mode | Set with | Where the driver runs | Typical use |
|---|---|---|---|
| Local | `--master local[*]` | Inside one JVM on your machine, together with the executor threads | Development and unit tests on a laptop |
| Client | `--deploy-mode client` (the default) | On the machine that ran `spark-submit` (an edge node, a notebook) | Interactive work: `spark-shell`, notebooks, debugging, where you want to see output directly |
| Cluster | `--deploy-mode cluster` | In a container on a cluster node | Production jobs. The job survives if your laptop or SSH session disconnects, and the driver is close to the executors |

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Deploy Mode: `client` vs `cluster`").

**Say it out loud:** "Deploy mode is about where the driver runs. In client mode it runs on the machine I submit from, which is handy for interactive work. In cluster mode it runs inside the cluster, which is what you want in production. Testing on a laptop is a different thing, local mode."

---

**Q. Difference between a DF and a DS**

**A. (Class answer)**

DataFrames and DataSets are similar Spark APIs, but which have a few critical differences.

They both look like SQL tables, but DataSets have the additional feature of ensuring type safety at compile time. For this reason, DataSets are only available in Spark Scala, as Python is not a compiled language and therefore doesn't have compile time. Type safety at compile time gives us as developers the ability to catch type errors more quickly because is there is an issue with data types, the compilation will fail and force us to go back and fix any issues before we compile the code.

Note - type safety means the 100% assurance that a piece of data will be of the type that we expect. This is usually enforced by statically typed languages (such as Java), meaning languages that force the developer to explicitly specify data types. The alternative is dynamically typed languages (such as Python) where data types are determined during the program's execution based on context. Dynamically typed languages cannot be said to be type safe, as there is a small chance that the program will interpret a piece of data as one type when it was intended to be another.

**Expanded:**

**Correction:** Datasets are available in **Scala and Java** (both compiled JVM languages), not only Scala. Python and R have only DataFrames. In Scala, a DataFrame is literally `Dataset[Row]`, an untyped Dataset. Small precision on the note: "type safety" and "static typing" are not the same thing. Python is dynamically typed but still strongly typed (it won't silently add a string to an int). What a Dataset adds is **compile-time** checking of column names and types.

| | DataFrame | Dataset |
|---|---|---|
| Type | `Dataset[Row]` (generic rows) | `Dataset[T]` for a case class `T` |
| Column/type errors caught | At runtime (analysis) | At compile time (for typed operations like `.map(_.age)`) |
| Languages | Scala, Java, Python, R | Scala, Java |
| Performance | Fully optimized by Catalyst | Same optimizer, but lambdas over objects need encoding/decoding and are opaque to Catalyst |

```scala
case class Person(name: String, age: Int)
val ds = df.as[Person]          // needs import spark.implicits._
ds.filter(_.age > 30)           // a typo in .age fails at compile time
```

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Worked Example (Teacher's Code): `case class` + `Dataset[Person]`").

**Say it out loud:** "A Dataset is a typed DataFrame: a `Dataset` of a case class, so column and type mistakes are caught at compile time. A DataFrame is `Dataset[Row]` with checks at runtime. Datasets exist only in Scala and Java, so in PySpark you always use DataFrames."

---

**Q. Difference between a Pandas DF and a Spark DF**

**A. (Class answer)**

Pandas was where the concept of the DataFrame originated, and the idea was incorporated into Spark at a later time.

The major difference between them is that Pandas is not a distributed processing framework, so data processing can only ever be performed on one machine, never on a cluster. Spark dataframes, on the other hand, are processed in a distributed way on a compute cluster, making them more suitable for processing extremely large datasets.

They also have different APIs, meaning different commands that are used to perform the same operation.

**Expanded:**

**Correction:** The DataFrame idea did not originate in pandas. It came from the S and **R** languages (R's `data.frame`). Pandas (2008) brought it to Python, and Spark added DataFrames in version 1.3 (2015).

| | pandas DataFrame | Spark DataFrame |
|---|---|---|
| Runs on | One machine, data must fit in RAM | A cluster, data partitioned across executors |
| Execution | Eager: each line runs immediately | Lazy: runs when an action is called |
| Mutability | Mutable (you can assign into it) | Immutable (each transformation returns a new DataFrame) |
| Index | Has a row index | No row index or row order guarantee |
| Good for | Small to medium data, quick analysis | Large data, distributed ETL |

Bridges between them: `df.toPandas()` (collects everything to the driver, so be careful), pandas UDFs, and the **pandas API on Spark** (`pyspark.pandas`, formerly the Koalas project).

**Say it out loud:** "pandas runs eagerly on one machine and the data has to fit in memory. A Spark DataFrame is distributed across a cluster, immutable and lazily evaluated, so it scales to data far bigger than one machine. The APIs look similar but are different."

---

**Q. Coalesce vs repartition**

**A. (Class answer)**

Coalesce and repartition are both ways of changing the sizes of the partitions in your data.

Coalesce will take the partitions that are present on each node of the cluster and combine them together, resulting in larger sized partitions. This is in line with the meaning of the English word coalesce, which means to bring things together into a larger whole (eg, military forces can coalesce when smaller units come together to form a larger fighting force). It is only capable of creating larger partitions, never smaller ones, and it does not guarantee that the output partitions will be equally sized. This is useful when we want larger partitions and do not need for the partitions to be of equal size.

Repartition is similar, and under the hood the first thing that repartition does is perform a coalesce operation. However, after performing it, it will also do a full shuffle of the data. This means that repartition is able to give us more control over the size of the output partitions, meaning that they can be either larger or smaller than the input partitions. It guarantees equally sized output partitions as well. Because it can guarantee equally sized output partitions, it is one of the best methods for preventing the problem of data skewness.

**Expanded:**

**Correction:** `repartition(n)` does not "first perform a coalesce and then a shuffle". In the RDD API it is defined as `coalesce(n, shuffle = true)`: **one full shuffle**. A round-robin `repartition(n)` gives roughly even partitions, but `repartition(col)` hash-partitions by that column, so every row of a hot key still lands in the **same partition**. Repartition therefore does **not** fix key skew. Salting or AQE skew join handles that.

| | `coalesce(n)` | `repartition(n)` / `repartition(n, col)` |
|---|---|---|
| Direction | Only reduces the number of partitions | Increases or reduces |
| Shuffle | No full shuffle: merges existing partitions, mostly on the same executor | Full shuffle |
| Output sizes | Can be uneven | Round-robin: roughly even. By column: grouped by key (can be skewed) |
| Cost | Cheap | Expensive |
| Typical use | Reduce the number of output files before a write | Increase parallelism, or co-locate rows by key before a join or partitioned write |

One gotcha: because coalesce avoids a shuffle, `coalesce(1)` can reduce the parallelism of the whole preceding stage, not just the write.

See [Training 7 notes](/training-notes-site/notes/training-7/) and [Training 8 notes](/training-notes-site/notes/training-8/) ("`repartition()` vs. Salting: What Each One Actually Controls").

**Say it out loud:** "Coalesce only reduces the partition count and merges partitions without a full shuffle, so it's cheap but sizes can be uneven. I use it to cut the number of output files. Repartition does a full shuffle and can go up or down. Round-robin gives even sizes, but repartitioning by a skewed key doesn't fix skew, for that I'd use salting or AQE."

---

**Q. What's a shuffle?**

**A. (Class answer)**

A shuffle is an operation that changes the order of the rows in a dataset.

Transformations that do not shuffle the data are called narrow transformations, and multiple of them can be performed in one stage.

Transformations that do shuffle the data are called wide transformations, and executing one of them will transition the spark job from one stage to the next stage.

A classic example of an operation that shuffles the data is a GroupBy, which needs to change the order of the rows by definition because it is arranging similar rows to be next to each other. Another example is when we perform a repartition, which shuffles the data in order to get evenly sized partitions as output.

Shuffling the data is computationally expensive, meaning that it requires a lot of compute power and time to perform. Therefore, to optimize a Spark job, we need to make sure that we are only shuffling the data when it is absolutely necessary to do so.

**Expanded:**

**Correction:** A shuffle is not "changing the order of rows". A shuffle **redistributes data across partitions**, usually across the network between executors, so that all rows with the same key end up in the same partition. Each map-side task writes its output to local disk as shuffle files, partitioned by key, and the next stage's tasks fetch the pieces they need. Sorting may happen as part of it, but redistribution is the point.

Why it is expensive: disk writes, network transfer, serialization, and a stage boundary where all upstream tasks must finish. Ways to reduce shuffles: broadcast joins, filtering and selecting columns early, pre-aggregating (`reduceByKey` instead of `groupByKey` in RDDs), bucketing tables on the join key, and letting AQE coalesce shuffle partitions. `spark.sql.shuffle.partitions` (default 200) sets how many partitions a DataFrame shuffle produces.

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Wide Transformations").

**Say it out loud:** "A shuffle redistributes data across partitions over the network so that rows with the same key end up together, like for a `groupBy` or join. It's expensive because it writes shuffle files to disk, moves data over the network and forces a stage boundary, so I try to minimize it, for example with broadcast joins and early filtering."

---

**Q. What is the DAG?**

**A. (Class answer)**

The term DAG stands for Directed Acyclic Graph, a concept in graph theory (a branch of mathematics) that represents an operation where we move from one step of an operation to another in ordered way, with no ability to go backwards. In the graph, the circles are called nodes and the lines are called edges.

In Spark, the concept of the DAG is used the execution engine in order to plan the execution of the entire program. Collections of transformations are grouped into nodes in the DAG, and a wide transformation represents a transition from one node to the next.

Note: when the term "node" is used above, it DOES NOT REFER TO A NODE IN THE CLUSTER.

**Expanded:** A DAG is a graph of steps connected by one-way edges with no cycles. In Spark, the driver builds a DAG of your transformations (each RDD or operation depends on its parents). When an action runs, the **DAGScheduler** cuts that graph into **stages** at shuffle boundaries. The Spark UI's DAG visualization shows each stage as a box with its operations inside.

Small precision on the teacher's wording: the boxes that "move from one to the next at a wide transformation" are **stages**. The DAG's individual nodes are the operations or RDDs.

The DAG is also what makes lineage possible: if a partition is lost, Spark walks back through the DAG to recompute it.

See [Training 17 notes](/training-notes-site/notes/training-17/) (the section on what "DAG" means in dbt vs Spark vs Airflow).

**Say it out loud:** "The DAG is the directed acyclic graph of transformations Spark builds from my code. When an action runs, the DAG scheduler splits it into stages at each shuffle, and the same graph is the lineage Spark uses to recompute lost partitions."

---

**Q. What is a logical plan vs a physical plan?**

**A. (Class answer)**

Both of them are plans for how to execute a data processing job as efficiently as possible.

A logical plan is a high-level representation of what is happening to the data during processing, which aligns with the way we as programmers think about the data operations.

A physical plan is a low-level representation of the operations that the computer will perform in order to implement the logical plan. There are optimizations that can be made at this stage which could not be made from the perspective of logical data operations.

The most efficient plans are selected by the optimizer and submitted to the cluster manager, which uses them to orchestrate the operations to be performed on the cluster.

**Expanded:**

**Correction:** The selected physical plan is not submitted to the cluster manager. It stays in the **driver**, which turns it into stages and tasks and schedules them on the executors itself.

Catalyst works in these steps (you can see them with `df.explain(True)`):

| Step | What happens |
|---|---|
| Parsed (unresolved) logical plan | Your DataFrame code or SQL as a tree of operations |
| Analyzed logical plan | Table and column names resolved against the catalog, types checked |
| Optimized logical plan | Rule-based rewrites: predicate pushdown, column pruning, constant folding, combining filters |
| Physical plan(s) | Concrete algorithms chosen, for example broadcast hash join vs sort-merge join, with cost-based choices |
| Code generation | Whole-stage codegen turns the chosen plan into compact JVM bytecode |

With AQE on, the physical plan can still change at runtime at each stage boundary.

See [Training 7 notes](/training-notes-site/notes/training-7/) ("The Optimizer (Step 2, in detail)").

**Say it out loud:** "The logical plan describes what I want, like filter, join and aggregate, and Catalyst optimizes it with rules such as predicate pushdown. The physical plan describes how to do it, for example a broadcast hash join instead of a sort-merge join. I can see both with `explain(True)`."

---

**Q. How is a Spark application divided into jobs, stages, and tasks?**

**A. (Class answer)**

Tasks are individual operations that represent any narrow transformation, wide transformation, or action.

Tasks are grouped into stages, which are divided from each other by wide transformations, which shuffle the data and cause the DAG to move from one stage to the next.

If the program contains more than one action, there are said to be multiple jobs. Jobs are divided from each other by the execution of an action, which results in an output value that is not an RDD.

**Expanded:**

**Correction:** A task is not "an individual operation". A **task** is the unit of work sent to one executor core: it runs **all of a stage's operations on one partition**. So a stage over 200 partitions has 200 tasks. Transformations and actions are operations. Tasks are their execution, one per partition.

| Unit | Created by | Count |
|---|---|---|
| Application | One `spark-submit` / one SparkSession | 1 |
| Job | Each **action** (`count`, `write`, `collect`) | One per action (some operations like schema inference can add extra jobs) |
| Stage | Splitting a job at each **shuffle** boundary | Number of shuffles + 1 |
| Task | One per **partition** in a stage | Equals the stage's partition count |

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Jobs, Stages, and Tasks").

**Say it out loud:** "Each action creates a job. The job is split into stages wherever there's a shuffle, and each stage runs as one task per partition. The task is the actual unit of work on an executor core."

---

**Q. What is a driver?**

**A. (Class answer)**

The driver application is the program that we write when we are developing a Spark job. It contains the logic that the program will execute when it is submitted.

**Expanded:** The driver is the process that runs your `main` program. It creates the SparkSession, builds and optimizes the plan, splits jobs into stages and tasks, schedules tasks on executors, keeps track of which executor has which cached data and shuffle output, receives results from actions like `collect`, and hosts the Spark UI. If the driver dies, the whole application dies. Driver memory problems usually come from `collect()`, `toPandas()` or very large broadcast tables.

**Say it out loud:** "The driver is the process running my main program. It plans the work, schedules tasks on the executors and collects results, so if the driver fails the whole application fails."

---

**Q. What is an executor?**

**A. (Class answer)**

An executor is a JVM process that is part of Spark. It is a software process which serves to perform processing tasks.

Note: AN EXECUTOR AND A NODE ARE NOT THE SAME THING!!!!!!!

Executors are software processes which run on nodes, which are physical machines. There will usually be multiple executors running on a single node. The number of executors running on each node can be specified either in the config section of the part of the program that defines your SparkSession, or in the spark-submit command.

**Expanded:** An executor is a JVM process launched for one Spark application on a worker node. It has a fixed number of cores (`--executor-cores`), so it can run that many tasks at once as threads, and a fixed heap (`--executor-memory`) split between execution memory (shuffles, joins, sorts) and storage memory (cache). It also stores shuffle files and cached partitions. A node can host several executors, and in YARN or Kubernetes each executor runs in a container or pod. With dynamic allocation, Spark can add and remove executors as the workload changes.

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Worker vs Executor").

**Say it out loud:** "An executor is a JVM process on a worker node that runs tasks in parallel, one per core, and holds cached data and shuffle files. It's a process, not a machine: one node can run several executors."

---

**Q. What are some common spark-submit parameters?**

**A. (Class answer)**

- num-executors: specifies how many executors we want to run on our cluster
- executor-cores: specifies the number of CPU cores assigned to each executor
- executor-memory: specifies the amount of RAM assigned to each executor
- driver-memory: specifies the amount of RAM assigned to the driver application
- jars: specifies any additional code that will be provided to the Spark execution using a jar file (for example, you need jar files to work with XML or Avro files in Spark)
- py-files: specifies any additional code that will be provided to the Spark execution using Python files, which will be zipped in order to pass them to our application
- class: If your Spark application is written in Scala, you have to specify which class is the main one, which you do using the class parameter
- master: specifies either the master node or the cluster manager that you will be using for your application (for example, when running Spark on a Hadoop cluster, master will most likely be set to YARN)
- deploy-mode: specifies whether we are running the application in client mode or cluster mode

**Expanded:** The teacher's list is accurate. A few more worth knowing: `--conf key=value` (any Spark setting, such as `spark.sql.shuffle.partitions`), `--packages` (pull Maven dependencies by coordinate, for example the Kafka connector), `--files` (ship config files to executors), `--name`, `--driver-cores`, and `--py-files` for zipped Python modules.

```bash
spark-submit \
  --master yarn --deploy-mode cluster \
  --num-executors 10 --executor-cores 4 --executor-memory 8g \
  --driver-memory 4g \
  --conf spark.sql.shuffle.partitions=400 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  my_job.py s3://bucket/input s3://bucket/output
```

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Core Arguments" through "Application Arguments").

**Say it out loud:** "The ones I use most are `--master` and `--deploy-mode`, the resource settings `--num-executors`, `--executor-cores`, `--executor-memory` and `--driver-memory`, `--conf` for Spark settings, and `--jars`, `--packages` or `--py-files` for dependencies."

---

**Q. What is data skew? How do you fix it?**

**A. (Class answer)**

Data skew, also called data skewness, is a problem that occurs in distributed data processing in which the partition sizes are uneven, and so the executor which receives the largest partition will take a larger amount of time than the rest, and therefore will take more time than the rest, which causes the job to take longer than it should.

If the extra data that the one executor has were instead spread across the cluster, the processing would be more efficient and the job would take less time. So, the solution to this problem will involve doing this. There are three methods for solving this problem:

1. Use a simple repartition operation, which will resize the partitions to approximately equal sizes.
2. Use salting, which involves creating a new column with specific values added to every x number of rows, which we then use to repartition the data in order to have finer control over the size of our partitions.
3. If using Spark 3.0 or later, turn on adaptive query execution. One of the optimizations included with AQE is called Dynamic Partition Pruning, or DPP, which can automatically detect unevenly sized partitions and resize them without additional input from the programmer. This is the most modern solution.

**Expanded:**

**Correction:** Three fixes in this answer need correcting:
- The AQE feature that handles skew is **skew join optimization** (`spark.sql.adaptive.skewJoin.enabled`). **Dynamic Partition Pruning is a different feature**: it skips reading partitions of a partitioned table based on a join filter (described correctly in the DPP question below).
- A plain `repartition(n)` evens out partition sizes, but if the skew comes from one hot **key** in a join or `groupBy`, the shuffle sends all of that key's rows to one partition again. Repartition doesn't fix key skew.
- Salting does not add "values to every x number of rows". It adds a **random** suffix (0 to N-1) to the hot key so its rows spread over N partitions (see the salting question below).

Skew is usually **key skew**: one key (often `NULL`, or one huge customer) has far more rows than the rest, so one task runs far longer than the others. You spot it in the Spark UI when one task's duration or shuffle-read size is far above the median.

| Fix | When it fits |
|---|---|
| AQE skew join (on by default with AQE in Spark 3.2+) | Skewed sort-merge joins: Spark splits the oversized partition into smaller pieces at runtime |
| Broadcast join | One side is small, so no shuffle is needed |
| Salting | Hot keys in joins or aggregations that AQE doesn't handle |
| Handle the hot key separately | Filter out `NULL` keys or process the one huge key on its own path, then union |
| `repartition(n)` (no key) | Uneven input files or partitions, not key skew |

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Data Skew" and "Salting (Manual Skew Mitigation)") and [Training 8 notes](/training-notes-site/notes/training-8/).

**Say it out loud:** "Data skew is when one partition, usually one hot key, has far more data than the rest, so one task holds up the whole stage. I'd first check the Spark UI, then turn on AQE skew join handling, use a broadcast join if one side is small, or salt the hot key. A plain repartition helps uneven files but not a hot key."

---

**Q. What is a cluster manager? Which ones have you used?**

**A. (Class answer)**

A cluster manager is a program which organizes and orchestrates Spark jobs, particularly when run on a cluster. There are 3 major options for cluster managers to use:

1. YARN - this is what we use when running Spark on a Hadoop cluster. It is a part of core Hadoop and also serves as Hadoop's load balancer and as a tool for administering the Hadoop cluster.
2. Spark's built in cluster manager: this is when we use when running Spark in client mode on a laptop for testing. It is simple to use, but it is not robust enough for use in production.
3. Kubernetes: If running Spark on a Kubernetes cluster, Kubernetes itself can be used as Spark's cluster manager.

DO NOT MENTION APACHE MESOS. In over five years of doing interviews, I have never once heard an interviewer mention this technology.

**Expanded:**

**Correction:** Spark's built-in **standalone** cluster manager is a real multi-node cluster manager. You start a master and workers on several machines, and it is used in production (it also supports high availability with ZooKeeper). The laptop case the teacher describes is **local mode**, which uses no cluster manager. Also, the cluster manager doesn't schedule Spark's tasks; the driver does. The cluster manager allocates resources.

| Cluster manager | Used when |
|---|---|
| YARN | Spark on Hadoop: on-prem Hadoop clusters, Amazon EMR, Dataproc |
| Kubernetes | Spark on a Kubernetes cluster (EKS, AKS, GKE). Executors run as pods |
| Standalone | A simple dedicated Spark cluster without Hadoop or Kubernetes |
| (Local mode, not a cluster manager) | One machine, for development and tests |

YARN is Hadoop's resource manager, not really a "load balancer": its ResourceManager allocates containers across the cluster, and a NodeManager on each node runs them.

See [Training 6 notes](/training-notes-site/notes/training-6/) ("Cluster Manager").

**Say it out loud:** "A cluster manager allocates CPU and memory to applications and starts their executors. I've used YARN, for example on EMR, and I know Spark can also run on Kubernetes or its own standalone manager. On a laptop you just use local mode."

---

**Q. Difference between SparkContext and SparkSession**

**A. (Class answer)**

SparkContext was the original point of entry for Spark applications. From within a SparkContext, we gain access to the RDD API. It has been obsolete for this purpose since the release of Spark 2.0, but a SparkContext can still be created within a SparkSession if we want to work directly with RDDs in a modern Spark project.

SparkSession is the point of entry for all modern Spark projects. It is part of Spark SQL, which was introduced in Spark version 2.0. It gives us access to the DataFrame API.

**Expanded:**

**Correction:** SparkContext is not obsolete. Every classic SparkSession still contains one (`spark.sparkContext`), and it is still what connects the driver to the cluster and gives you the RDD API, broadcast variables and accumulators. Also, Spark SQL was not introduced in Spark 2.0. It existed from Spark 1.0 (through `SQLContext` and `HiveContext`). What Spark 2.0 introduced was **SparkSession**, a single entry point that replaced SQLContext, HiveContext and (for most uses) StreamingContext.

| | SparkContext | SparkSession |
|---|---|---|
| Introduced | Spark 1.0 | Spark 2.0 |
| Gives you | RDDs, broadcast variables, accumulators, cluster connection | DataFrames, Datasets, SQL, catalog, Structured Streaming |
| How you get it | `spark.sparkContext` | `SparkSession.builder...getOrCreate()` |

One newer exception: with **Spark Connect** (Spark 3.4+), a thin client talks to a remote Spark server and has no SparkContext or RDD API on the client side.

**Say it out loud:** "SparkContext was the original entry point, for RDDs and the cluster connection. Since Spark 2.0 we use SparkSession, which unifies SQL, DataFrames and Hive support, and it still wraps a SparkContext that I can reach with `spark.sparkContext` if I need RDDs."

---

**Q. How do deal with an out of memory error in Spark?**

**A. (Class answer)**

This is an open-ended question with many possible answers. Some of the best are as follows:

1. If your cluster has more hardware resources available, you can try giving the job more resources. This is the simplest solution, but it is not always possible due to hardware constraints and the possibility of other teams needing access to the same resources.
2. Optimize the code to use memory as efficiently as possible. Eliminate any unnecessary processing steps, avoid shuffling the data whenever possible, and make sure that your partitions are evenly sized.
3. If the above two strategies do not work, you can scale the cluster to have more hardware resources. On the cloud this is simple to do, but carries a cost. On an on premises cluster this is much more complicated, and will likely involve a long process of discussions with stakeholders and business decisions to spend more money on the cluster. This is a last resort, and highly impractical for most situations.

**Expanded:** First work out **where** it happened, because the fixes differ:

| Where | Typical cause | Fixes |
|---|---|---|
| Driver | `collect()`, `toPandas()`, broadcasting a table that is too large, too many tiny tasks to track | Don't collect big data (write it out, or use `take`/`limit`), lower the broadcast threshold, increase `--driver-memory` |
| Executor | Partitions too large, skew, big joins or aggregations, caching too much | More partitions (`spark.sql.shuffle.partitions`, `repartition`), fix skew, filter and select columns earlier, use `MEMORY_AND_DISK` or unpersist caches, avoid RDD `groupByKey` |
| Executor container killed by YARN/Kubernetes | Off-heap memory (Python workers, network buffers) above the container limit | Increase `spark.executor.memoryOverhead` |

Only after that, add resources (`--executor-memory`) or scale the cluster. The teacher's order (tune the code before buying hardware) is right.

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Driver and Executor Resources" and "Determining Executor Sizing").

**Say it out loud:** "I'd first check whether it's the driver or an executor. Driver OOMs usually come from `collect` or a large broadcast. Executor OOMs usually come from oversized or skewed partitions, so I'd increase the partition count, fix skew and drop unneeded columns early, and raise memory or memory overhead only after that."

---

**Q. How do you detect duplicate rows?**

**A. (Class answer)**

This can be achieved by performing a groupby operation combined with a count, then filtering the data to only include rows where the value of the count column is greater than 1.

**Expanded:** The teacher's method is correct. In code:

```python
from pyspark.sql import functions as F, Window

# find duplicates on the business key
dups = df.groupBy("order_id").count().filter("count > 1")

# remove exact duplicates, or duplicates on chosen columns
clean = df.dropDuplicates(["order_id"])

# keep only the latest version of each key
w = Window.partitionBy("order_id").orderBy(F.col("updated_at").desc())
latest = df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")
```

The `row_number` pattern is the one interviewers like, because `dropDuplicates` keeps an arbitrary row while the window lets you choose which one survives. In SQL it is the same `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` pattern.

See [Training 4 notes](/training-notes-site/notes/training-4/) ("Nth-Highest-Per-Group: RANK / DENSE_RANK / ROW_NUMBER").

**Say it out loud:** "I group by the key columns, count, and filter for count greater than one. To remove them I use `dropDuplicates`, or a `row_number` window ordered by timestamp when I need to keep the latest record."

---

**Q. When would you use a broadcast join?**

**A. (Class answer)**

Broadcast joins are useful in a situation where a join needs to be performed between two tables, one of which is much smaller than the other. The definition of what constitutes a "small" table is one that is less than 5 GB, although if your cluster has an unusually high amount of memory it could potentially be larger.

The join is performed by broadcasting the smaller table to all of the worker nodes, where it is stored in the RAM of each node. Then, the larger table is distributed among the nodes, as normal in Spark. On each node, the partition of the larger table is joined to the entire smaller table. When the partitions are reassembled, the output is logically the same as if the join had been performed in the normal way, but the process will be much more efficient.

The efficiency comes from the fact that the smaller table is stored locally, so nodes have no need to communicate with each other in order to perform the join. This prevents unnecessary traffic on the LAN that connects the cluster nodes together, and saves time that would be wasted in the nodes finding the data that need to be sent to each other.

**Expanded:**

**Correction:** A "small" table is not "less than 5 GB". Spark's automatic broadcast threshold (`spark.sql.autoBroadcastJoinThreshold`) defaults to **10 MB**. You can raise it or force a broadcast with the `broadcast()` hint, but there is a **hard limit of 8 GB** per broadcast table, and in practice broadcast tables are tens to a few hundred MB. The whole table is collected on the driver and copied into every **executor's** memory (not just every node), so a multi-GB broadcast usually causes out-of-memory errors.

```python
from pyspark.sql.functions import broadcast
result = facts.join(broadcast(dim_store), "store_id")
```

Why it is faster: the large table is not shuffled at all. Each executor joins its own partitions of the large table against its local copy of the small one. One restriction: in an outer join, Spark can only broadcast the side whose unmatched rows are *not* kept (for a left outer join, the right side).

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Broadcast Variables and Broadcast Joins" and "Broadcast Join Size Guideline").

**Say it out loud:** "When one side of the join is small, like a dimension table, I broadcast it so every executor gets a full copy and the big table never has to be shuffled. Spark does this automatically under 10 MB by default, and I can force it with the `broadcast()` hint for tables up to a few hundred MB."

---

**Q. What is a broadcast variable?**

**A. (Class answer)**

A broadcast variable is one where the data it stores is sent to the worker nodes in the cluster, to be stored on the local memory of each node. This makes them more easily accessible when performing complex tasks, or when the data will be used frequently.

Broadcast variables are typically used to store DataFrames or RDDs.

**Expanded:**

**Correction:** Broadcast variables are not "typically used to store DataFrames or RDDs". You can't broadcast an RDD or DataFrame as a variable. A broadcast variable holds a **small, read-only value created on the driver**, such as a lookup dictionary, a set of IDs or model parameters. Spark sends it **once per executor** (instead of once per task inside every closure) and caches it there. Broadcasting a DataFrame is done with a broadcast **join** hint instead.

```python
lookup = spark.sparkContext.broadcast({"US": "United States", "CA": "Canada"})
rdd.map(lambda r: lookup.value.get(r.country))
```

Its counterpart is the **accumulator**: a variable that tasks can only add to and the driver reads (for example, a counter of bad records).

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Broadcast Variables and Broadcast Joins").

**Say it out loud:** "A broadcast variable is a small read-only value, like a lookup dictionary, that Spark ships once to each executor and caches, instead of sending it with every task. For joining against a small DataFrame I'd use a broadcast join instead."

---

**Q. Spark Streaming vs Structured Streaming**

**A. (Class answer)**

Spark Streaming is the original streaming processing API for Spark, common before the release of Spark 2.0. It processes the data using the RDD API, specifically by using something called a forEachRDD loop. This works similarly to other loops in programming, but the data that it is looping over is a continuous stream which is divided into small chunks called micro-batches. A micro-batch is an RDD that is populated with whichever data is streamed into it during a time window, the length of which you specify in the program. When the time window closes, the accumulated data is then processed as a batch in the same way that Spark does batch processing. When the processing is finished, Spark moves on to the next batch, then the next, and so on for as long as the program continues to run. This method is called "near-real-time processing" and is approximately as efficient as programs that process streaming data in true real time.

Spark Structured Streaming is the modern way to process streaming data, using the DataFrame API. Instead of a loop, we use something called ReadStreams and WriteStreams. In this method, we declare our DataFrame similarly to how we would in a batch job, but define it as a ReadStream or WriteStream. A ReadStream will continuously read micro-batches of data into the input DataFrame, which will then be processed using the same code that would be used to process an equivalent batch DataFrame. The final DataFrame in the process will be declared as a WriteStream, which is configured to save the processed data to its output location.

**Expanded:**

**Correction:** Two points need fixing:
- Spark Streaming (DStreams) is not built on a `foreachRDD` loop. A DStream **is** a sequence of RDDs, one per batch interval, and you transform it with operations like `map` and `reduceByKeyAndWindow`. `foreachRDD` is only one *output* operation for writing results.
- Micro-batching is not "approximately as efficient as true real time". It adds latency of roughly the batch interval, typically seconds. That is near-real-time. Engines like Flink that process each event as it arrives get lower latency.

| | Spark Streaming (DStreams) | Structured Streaming |
|---|---|---|
| API | RDD-based DStreams | DataFrame/Dataset and SQL |
| Model | Sequence of RDD micro-batches | An unbounded table that new rows keep appending to |
| Optimizer | None | Catalyst |
| Event time + late data | Limited | Built in: event-time windows and watermarks |
| Guarantees | At-least-once by default | Exactly-once with a replayable source, checkpointing and an idempotent or transactional sink |
| Status | Legacy (deprecated as of Spark 3.4) | The current API |

In code, `spark.readStream` returns a reader and `df.writeStream` a writer. They are methods, not separate "ReadStream/WriteStream" object types. Structured Streaming also uses micro-batches by default (an experimental continuous mode exists).

See [Training 14 notes](/training-notes-site/notes/training-14/) ("Spark Structured Streaming: Core Concepts") and [Training 12 notes](/training-notes-site/notes/training-12/) ("Spark Structured Streaming").

**Say it out loud:** "The old Spark Streaming API used DStreams, which are sequences of RDD micro-batches, and it's now legacy. Structured Streaming treats the stream as an unbounded DataFrame, so I write the same code as for batch, and it adds event-time windows, watermarks and exactly-once output through checkpointing. Both are micro-batch, so latency is in seconds rather than true per-event streaming."

---

**Q. What is key salting?**

**A. (Class answer)**

Key salting is a process for preventing data skewness. It is performed by creating a new DataFrame column which is populated with specific values, which change every x number of rows (defined by you as the programmer). This allows us to specify an exact number of rows that will go into each output partition. We then use repartition to partition the dataframe on the salted column, which will result in evenly sized output partitions.

**Expanded:**

**Correction:** Salting does not let you "specify an exact number of rows per partition", and the salt does not change "every x rows". Salting appends a **random** number from 0 to N-1 to a **hot key**, so that key's rows are spread across N partitions instead of one. The follow-up operation must then be adapted:
- **Aggregation:** aggregate twice: first by `(key, salt)`, then combine those partial results by `key`.
- **Join:** salt the big, skewed side randomly, and **explode** the small side so each of its rows appears once for every salt value, then join on `(key, salt)`.

```python
from pyspark.sql import functions as F
N = 8
big = big.withColumn("salt", (F.rand() * N).cast("int"))
small = small.withColumn("salt", F.explode(F.array([F.lit(i) for i in range(N)])))
joined = big.join(small, ["key", "salt"]).drop("salt")
```

See [Training 8 notes](/training-notes-site/notes/training-8/) ("Salting Artificially Splits the Hot Key" and "Caveat: Salting Changes How the Follow-Up Operation Must Work") and [Training 7 notes](/training-notes-site/notes/training-7/) ("Salting (Manual Skew Mitigation)").

**Say it out loud:** "Salting fixes key skew by appending a random number from 0 to N-1 to the hot key, so its rows spread over N partitions. For an aggregation I then aggregate twice, by key and salt and then by key. For a join I replicate the small side once per salt value."

---

**Q. What is Adaptive Query Execution?**

**A. (Class answer)**

Adaptive Query Execution, abbreviated to AQE, is the flagship feature of Spark 3.0. It contains a large number of optimizations which operate under the hood, without needing any input from the programmer other than to activate the features in the config section of the SparkSession. The optimizations include:

1. Dynamically switching join strategies in order to increase join efficiency.
2. Dynamically coalescing shuffle partitions, which allows us to avoid creating too many small partitions, or too few large partitions.
3. Skew join optimization, which prevents data skew by detecting uneven partition sizes during shuffle operations and resizes the data to make the partitions even.

There are others, the list is too extensive to include here.

**Expanded:** The teacher's answer is correct. AQE re-optimizes the query **at runtime**, at each stage boundary, using the actual statistics from completed shuffles instead of estimates. It was introduced in Spark 3.0 and has been **on by default since Spark 3.2** (`spark.sql.adaptive.enabled=true`).

| AQE feature | What it does |
|---|---|
| Coalescing shuffle partitions | Merges many tiny shuffle partitions into fewer reasonably sized ones |
| Switching join strategy | Changes a sort-merge join to a broadcast hash join if one side turns out to be small |
| Skew join optimization | Splits an oversized partition in a sort-merge join into smaller tasks |
| Local shuffle reader | Reads shuffle output locally after switching to a broadcast join, saving network transfer |

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Adaptive Query Execution (AQE)").

**Say it out loud:** "AQE lets Spark re-optimize a query while it runs, using real shuffle statistics. It coalesces small shuffle partitions, switches to a broadcast join when a side turns out small, and splits skewed partitions. It's on by default since Spark 3.2."

---

**Q. What is Dynamic Partition Pruning?**

**A. (Class answer)**

Dynamic Partition Pruning is another new feature in Spark 3.0 which dynamically decides which partitions to read when executing a spark application, excluding any that are unnecessary. This improves the overall efficiency of the program by reducing the resources needed.

**Expanded:** The teacher's answer is correct. A concrete example makes it interview-ready: a large `sales` fact table is partitioned by `date_key`, and you join it to `dim_date` with a filter `WHERE d.year = 2024`. Static pruning can't help, because the filter is on the dimension, not on `sales`. With DPP, Spark first evaluates the filtered dimension, then uses the resulting `date_key` values to **skip reading every non-matching partition** of `sales` at runtime. It is on by default in Spark 3.0+ (`spark.sql.optimizer.dynamicPartitionPruning.enabled`). It is a separate feature from AQE, and it only helps when the large table is partitioned on the join key.

**Say it out loud:** "Dynamic partition pruning lets Spark use a filter on a dimension table to skip partitions of a big partitioned fact table at runtime. For example, filtering dates to 2024 means only the 2024 partitions of the sales table are read."

---

**Q. Why are UDFs less efficient in Pyspark than Spark Scala?**

**A. (Class answer)**

UDFs, or User Defined Functions, are written by the programmer of a Spark application when a task is not able to be completed by Spark's built-in functions. They are written as normal functions, then registered as UDFs by a separate line of code. They are generally not optimized to the standard of Spark's built-in functions, so even when they are executed in Scala they are considered inefficient and should be avoided if not absolutely necessary.

In Python they are less efficient because of Python's nature as a programming language. UDFs are executed in the language they are written in, which means that while Pyspark is ordinarily a wrapper for Scala code, there is no equivalent Scala code in the Spark's codebase for a UDF and so Python must be used.

Python is significantly slower to execute than Scala is. This is because of Python's nature as an interpreted language. Interpreted languages are less efficient than compiled languages because the machine code used to execute the program's commands must be decided in real time during the execution of the program, rather than beforehand as we have in compiled languages.

Because Scala is a compiled language (like all JVM languages), this work is done before the execution begins, which allows the computer's resources to be entirely used in the execution of the code. This results in much faster processing speeds than are possible with any interpreted language.

**Expanded:**

**Correction:** The main cost is not that "Python is interpreted". A regular Python UDF forces Spark to **serialize every row out of the JVM, send it to a separate Python worker process, run your function row by row, and serialize the result back**. That data movement is the main cost. Also, **any** UDF, in Scala or Python, is a black box to Catalyst, so filters can't be pushed through it and no code generation happens inside it.

| Option | Speed | Why |
|---|---|---|
| Built-in functions (`pyspark.sql.functions`, SQL) | Fastest | Run inside the JVM, fully optimized |
| Scala UDF | Fast-ish | Runs in the JVM, but opaque to the optimizer |
| **Pandas (vectorized) UDF** | Much better than plain Python UDFs | Uses **Apache Arrow** to move whole column batches, and your function works on pandas Series |
| Plain Python UDF | Slowest | Row-by-row serialization between the JVM and Python |

```python
import pandas as pd
from pyspark.sql.functions import pandas_udf

@pandas_udf("double")
def to_celsius(f: pd.Series) -> pd.Series:
    return (f - 32) * 5 / 9
```

Note that ordinary PySpark DataFrame code without UDFs runs about as fast as Scala, because only the plan is built in Python.

See [Training 2 notes](/training-notes-site/notes/training-2/) (PySpark speed note) and [Training 7 notes](/training-notes-site/notes/training-7/).

**Say it out loud:** "A Python UDF makes Spark ship every row from the JVM to a Python worker and back, row by row, and Catalyst can't optimize inside it. I try built-in functions first, and if I really need custom Python I use a pandas UDF, which moves data in Arrow batches and is much faster."

---

**Q. What does the collect function do?**

**A. (Class answer)**

The collect function will take an RDD and convert it to an ordinary list in whichever programming language you are using to write your Spark job.

**Expanded:** `collect()` is an action that brings **every row** of a DataFrame or RDD back to the **driver** as a local collection: a Python list of `Row` objects in PySpark, an `Array` in Scala. Use it only on small results. Safer alternatives: `show()` or `take(n)` to look at data, `limit(n).collect()`, `toLocalIterator()` to stream rows one partition at a time, or simply write the result to storage.

**Say it out loud:** "`collect` is an action that pulls all the rows back to the driver as a local list, so I only use it on small results and use `take`, `show` or a write otherwise."

---

**Q. Difference between a job, a stage, and a task**

**A. (Class answer)**

A job is the largest unit of work in Spark, a stage is in the middle, and a task is the smallest.

A task in an individual operation performed by Spark. It can be a narrow transformation, a wide transformation, or an action.

A stage combines one or more transformations together, often multiple narrow transformation and exactly one wide transformation or action. A stage ends when a wide transformation is executed, which shuffles the data and moves the job to the next stage. The job ends when an action is performed and our result is something other than an RDD.

**Expanded:**

**Correction:** As in the jobs/stages/tasks question above: a **task** is not "an individual operation". It is one partition's worth of a stage's work, running on one executor core. A stage usually contains several narrow transformations and ends at a shuffle (or at the final output). It doesn't contain "exactly one wide transformation".

| | Job | Stage | Task |
|---|---|---|---|
| Triggered by | An action | A shuffle boundary within a job | One partition within a stage |
| Contains | One or more stages | A pipeline of narrow operations | The stage's operations applied to one partition |
| Runs on | The whole cluster | Many executors in parallel | One executor core |

See [Training 7 notes](/training-notes-site/notes/training-7/) ("Jobs, Stages, and Tasks").

**Say it out loud:** "A job is everything triggered by one action. It's split into stages at shuffle boundaries, and each stage runs as many tasks as it has partitions. The task is the smallest unit and runs on one core."

---

**Q. In what situation would it be a bad idea to use collect?**

**A. (Class answer)**

Using collect is a bad idea when the RDD you are collecting is larger than the amount of memory that you have available in your master node. Because collect converts the RDD to a programming language object, it loses its distributed nature and becomes available only on one computer. In order to work on it, that computer must store the RDD in memory. If the RDD is bigger than the available memory, this will produce an out of memory error and the Spark job will fail.

**Expanded:**

**Correction:** `collect()` pulls the data into the **driver**, not a "master node". The driver may run on an edge node, your laptop or a container in the cluster (cluster mode), and its memory is set by `--driver-memory` (and limited further by `spark.driver.maxResultSize`, default 1 GB).

Collect is a bad idea whenever the result is large. The query may succeed on the executors and then crash the driver with an out-of-memory error, and even if it fits, you lose all parallelism, because everything after that runs on one machine. Write large results to storage instead, or use `take`, `limit` or aggregates.

**Say it out loud:** "Collect pulls all the data into the driver's memory, so it's a bad idea on anything large: the driver can run out of memory and I lose all parallelism. For big results I write to storage, and for inspection I use `take` or `show`."

---

**Q. What makes an RDD resilient?**

**A. (Class answer)**

RDDs are resilient due to something called RDD lineage. Lineage is the tracking of progress through the Spark DAG for the application. Because of this, if a Spark job fails, it is able to pick up more or less where it left off before failure when executed again.

This is in line with the meaning of the English word "resilient", which means able to persevere even when encountered with challenges or pain.

**Expanded:**

**Correction:** Lineage does not let a failed job "pick up where it left off when executed again". Lineage means each RDD records the transformations that built it from its parents. If an executor or node dies **during** a job, Spark uses that recipe to **recompute only the lost partitions** and the job continues. If the whole application fails and you rerun it, it starts from the beginning unless you saved progress yourself. Saving progress is what **checkpointing** does: it writes data to reliable storage and cuts the lineage. Structured Streaming checkpoints offsets and state so a restarted query resumes.

| Mechanism | Protects against |
|---|---|
| Lineage (recompute) | Losing executors or partitions during a running job |
| Shuffle files kept on disk | Rerunning whole upstream stages after a downstream task fails |
| Checkpointing | Very long lineages, and resuming a streaming query after restart |
| Task retries (`spark.task.maxFailures`, default 4) | Transient task failures |

**Say it out loud:** "RDDs are resilient because of lineage: each RDD knows how it was built from its parents, so if an executor dies Spark recomputes just the lost partitions during the same job. Resuming after the whole application fails needs checkpointing."

---


## Kafka


**Q. What is a producer?**

**A. (Class answer)**

A producer is a program in Kafka which accesses data from one or more sources and ingests them into a Kafka topic. Optionally, the data can be processed before ingestion.

**Expanded:** A producer is a **client application** (it runs outside the brokers) that publishes records to a topic. Each record has a key, a value, optional headers and a timestamp. Key points interviewers look for:
- **Partitioning:** with a key, the producer hashes it to choose the partition, so all records with the same key go to the same partition and stay in order. Without a key, records are spread across partitions.
- **Durability setting `acks`:** `0` (don't wait), `1` (the leader wrote it), `all` (all in-sync replicas have it).
- **Idempotence:** `enable.idempotence=true` (the default since Kafka 3.0) stops retries from creating duplicates.
- **Batching and compression** (`linger.ms`, `batch.size`, `compression.type`) for throughput.

See [Training 13 notes](/training-notes-site/notes/training-13/) ("Kafka Message Keys" and "Kafka Reliability (interview core)").

**Say it out loud:** "A producer is a client that publishes records to a Kafka topic. The record key decides the partition, so the same key always lands in the same partition in order, and I'd use `acks=all` with idempotence turned on for reliable delivery."

---

**Q. What is a consumer?**

**A. (Class answer)**

A consumer is a program in Kafka which receives data from a topic, optionally processes it, and puts it into a storage location.

**Expanded:** A consumer is a client application that **pulls** records from one or more topics by calling `poll()` in a loop. It tracks its position in each partition with **offsets** and commits them (to Kafka's internal `__consumer_offsets` topic), so it can resume after a restart. Reading does not delete anything: other consumer groups can read the same data independently. Whether it then writes to storage is up to your code (Spark, Kafka Connect sinks and Flink are common consumers).

**Say it out loud:** "A consumer is a client that polls records from topic partitions, tracks how far it has read with committed offsets, and usually writes the processed data somewhere. Consuming doesn't delete the messages, so other groups can read them too."

---

**Q. What is a broker?**

**A. (Class answer)**

A broker is a process that is running on each node in a Kafka cluster. It is responsible for administration of the Kafka cluster, as well as for containing topics and storing data within them.

**Expanded:** A broker is a Kafka server process. It stores partition logs on disk, serves produce and fetch requests for the partitions it **leads**, and copies data for the partitions it **follows**. Precision on "administration": cluster-wide management (tracking brokers, assigning partition leaders) is the job of the **controller**: one elected broker in ZooKeeper mode, or a small quorum of controller nodes in KRaft mode. A production cluster typically has at least three brokers.

**Say it out loud:** "A broker is a Kafka server that stores topic partitions on disk and handles reads and writes for them. A cluster has several brokers, and one controller, a broker or a KRaft controller quorum, manages metadata and leader election."

---

**Q. What is a consumer group?**

**A. (Class answer)**

A consumer group is a number of consumers which work together to ingest data from a partitioned topic. One consumer can ingest data from one partition.

**Expanded:**

**Correction:** The rule is the other way round. **Each partition is read by at most one consumer within a group**, and one consumer can read **many** partitions. With 6 partitions and 3 consumers, each consumer gets 2 partitions. With 6 partitions and 8 consumers, 2 consumers sit idle. So the partition count is the maximum parallelism of a group.

Different groups are independent: each group gets its own copy of the full stream and its own committed offsets. When a consumer joins or leaves, the group **rebalances**, reassigning partitions.

| Partitions | Consumers in one group | Result |
|---|---|---|
| 6 | 1 | One consumer reads all 6 |
| 6 | 3 | 2 partitions each |
| 6 | 6 | 1 each (maximum parallelism) |
| 6 | 8 | 6 busy, 2 idle |

See [Training 12 notes](/training-notes-site/notes/training-12/) ("How do partitioning, replication and consumer groups work in Kafka?").

**Say it out loud:** "A consumer group is a set of consumers sharing the work of reading a topic. Each partition goes to exactly one consumer in the group, but one consumer can read several partitions, so the number of partitions caps how many consumers can be useful."

---

**Q. What is the role of Zookeeper in Kafka?**

**A. (Class answer)**

Zookeeper acts as the cluster manager in Kafka. It must be run before the broker can be run. It is an implementation of the ZAB consensus algorithm.

In more recent versions of Kafka, there is the option to alter Kafka's configuration to use a different cluster manager called KRaft, which is an implementation of the RAFT algorithm and is built into Kafka, making Zookeeper unnecessary.

**Expanded:**

**Correction:** ZooKeeper was a **coordination and metadata service** for Kafka (broker membership, topic configuration, controller election). It is not a cluster manager in the YARN sense, since it doesn't allocate resources. More importantly, the "option" of KRaft is now the only option: KRaft became production-ready in Kafka 3.3, ZooKeeper mode was deprecated in 3.5, and **Kafka 4.0 (2025) removed ZooKeeper entirely**. In KRaft mode, a quorum of Kafka controller nodes stores the metadata in an internal log replicated with the Raft protocol. That simplifies operations (one system to run) and supports far more partitions.

| | ZooKeeper mode | KRaft mode |
|---|---|---|
| Metadata stored in | External ZooKeeper ensemble | Internal `__cluster_metadata` log on controller nodes |
| Consensus | ZAB (ZooKeeper Atomic Broadcast) | Raft |
| Status | Removed in Kafka 4.0 | Default and only mode going forward |

See [Training 14 notes](/training-notes-site/notes/training-14/) ("Kafka Cluster Setup (KRaft)").

**Say it out loud:** "ZooKeeper used to store Kafka's cluster metadata and elect the controller. Kafka has replaced it with KRaft, a built-in Raft-based controller quorum, and since Kafka 4.0 ZooKeeper is gone, so new clusters are all KRaft."

---

**Q. What are the 4 major Kafka APIs?**

**A. (Class answer)**

1. Producer API - for writing producers
2. Consumer API - for writing consumers
3. Connect API - for making it simpler to connect Kafka to different data sources
4. Streams API - for building scalable applications that have Kafka integrated into them

**Expanded:**

**Correction:** Kafka's documentation lists **five** core APIs. The fifth is the **Admin API**, for managing topics, brokers, ACLs and configs from code.

| API | Used for |
|---|---|
| Producer | Publishing records |
| Consumer | Reading records |
| Streams | A Java/Scala **library** for stream processing apps that read from topics, transform (including stateful joins and windows) and write back to topics, with exactly-once support |
| Connect | A framework of reusable **source** connectors (database, files into Kafka) and **sink** connectors (Kafka into S3, Elasticsearch, a warehouse) with no custom code |
| Admin | Creating topics, changing configs, inspecting the cluster |

**Say it out loud:** "Kafka has the Producer and Consumer APIs, the Streams API for building stream-processing apps, the Connect API for ready-made source and sink connectors, and an Admin API for managing topics and configs."

---

**Q. What is an offset?**

**A. (Class answer)**

An offset is an integer that is attached to each message that is streamed through Kafka. Each one is unique, and they are sequential. They represent the order in which messages were streamed, so that if they arrive out of order they can be reassembled in the order in which they were streamed. It also helps to identify if a message is missing.

**Expanded:**

**Correction:** Offsets are unique and sequential **within a partition**, not across the topic. Partition 0 and partition 1 both have an offset 42. Ordering is guaranteed **only within a partition**. Offsets aren't used to "reassemble" out-of-order messages; within a partition messages are never out of order. What offsets are for:
- **Tracking progress:** a consumer group commits the next offset it will read, per partition, so it can resume after a restart.
- **Replay:** you can reset a group to an earlier offset (or a timestamp) to reprocess data.
- Spotting gaps is not reliable: offsets can skip numbers (for example with transactions or compacted topics).

See [Training 12 notes](/training-notes-site/notes/training-12/) and [Training 13 notes](/training-notes-site/notes/training-13/) ("Kafka Reliability (interview core)").

**Say it out loud:** "An offset is a record's sequential position within one partition. Consumers commit offsets to remember where they stopped, which lets them resume or replay. Ordering is only guaranteed within a partition."

---

**Q. What is replication?**

**A. (Class answer)**

Replication is the copying of partitions of data in a topic across the cluster. The default replication factor is 3. This helps to ensure fault tolerance.

**Expanded:**

**Correction:** Kafka's broker default `default.replication.factor` is **1**, meaning no copies. **3 is the recommended production setting**, and managed services such as Amazon MSK set 3 by default on three-AZ clusters. The "3" the teacher remembers is also HDFS's default replication.

How it works: each partition has one **leader** replica and some **follower** replicas on other brokers. Followers copy from the leader. Paired with `acks=all` and `min.insync.replicas=2`, a replication factor of 3 means a write is confirmed only once at least two brokers have it, so losing one broker loses no data.

See [Training 12 notes](/training-notes-site/notes/training-12/) and [Training 13 notes](/training-notes-site/notes/training-13/) ("Kafka Reliability (interview core)").

**Say it out loud:** "Replication keeps copies of each partition on several brokers: one leader and followers. The broker default is actually 1, so in production we set a replication factor of 3 with `min.insync.replicas` of 2 and `acks=all` so a single broker failure loses nothing."

---

**Q. What is a topic?**

**A. (Class answer)**

A topic is an element of Kafka which streams and stores messages. The producer sends messages to the topic, where they are stored, partitioned, and replicated. The consumer receives messages from the topic.

**Expanded:** A topic is a named stream of records, stored as an **append-only log** split into partitions that are spread and replicated across brokers. Unlike a queue, reading a message does **not** remove it. Records stay until the retention limit (time or size) is reached, so any number of consumer groups can read the same topic at their own pace. Topics can also be **compacted** (`cleanup.policy=compact`), keeping only the latest value per key.

**Say it out loud:** "A topic is a named, append-only log of records, split into partitions and replicated across brokers. Consumers read it without removing anything, and data is kept until the retention period expires."

---

**Q. What is the default retention period for data stored in a Kafka topic?**

**A. (Class answer)**

7 days. This can be changed in the Kafka configuration.

The reason why it is only 7 days is because Kafka is not a database. Streaming data is retained for the purpose of being received at a later time by a consumer which was not able to receive it when it was first streamed.

**Expanded:** The teacher's answer is correct: `log.retention.hours=168`, which is 7 days. It can be overridden per topic with `retention.ms`. There is also size-based retention (`retention.bytes`, unlimited by default), and compacted topics that keep the latest value per key indefinitely. Retention deletes whole **log segments**, so data can live a little past the limit.

**Say it out loud:** "Seven days by default, configurable per topic with `retention.ms` or by size. Kafka is a buffer you can replay from, not the long-term store, so data lands in S3 or a warehouse for long-term keeping."

---

**Q. What is a partition?**

**A. (Class answer)**

A partition is a sub-section of a topic, which contained a defined amount of messages that have been streamed. Each partition can be replicated across the nodes of the cluster.

**Expanded:**

**Correction:** A partition doesn't hold "a defined amount of messages". It is an **ordered, append-only log** that keeps growing as records arrive (stored on disk as segment files and trimmed only by retention). Partitions are the unit of:
- **Parallelism:** each partition can be read by one consumer per group, and different partitions are spread across brokers.
- **Ordering:** order is guaranteed within a partition only.
- **Replication:** each partition is replicated separately, with its own leader.

The partition count can be increased later but not reduced, and increasing it changes which partition a key maps to.

**Say it out loud:** "A partition is an ordered, append-only log that is part of a topic. Partitions are how Kafka scales, since each one can be on a different broker and read by a different consumer, and ordering is guaranteed only within a partition."

---

**Q. What is an in sync replica?**

**A. (Class answer)**

An in sync replica is node in the cluster which stores the exact same messages as the leader. Only in sync replicas are able to be candidates in a leader election.

**Expanded:**

**Correction:** An in-sync replica is a **replica** (a copy of one partition on some broker), not a node. And it doesn't need to have "the exact same messages" at every instant. It is a follower that is **caught up** with the leader within `replica.lag.time.max.ms` (30 seconds by default). The leader itself is always in the ISR.

Why it matters: with `acks=all`, the leader confirms a write only after all current ISR members have it, and `min.insync.replicas` sets how many must be in the ISR for writes to be accepted. By default (`unclean.leader.election.enable=false`), only ISR members can become leader, which prevents data loss.

See [Training 13 notes](/training-notes-site/notes/training-13/) ("Kafka Reliability (interview core)").

**Say it out loud:** "The ISR is the set of replicas of a partition that are caught up with the leader. With `acks=all`, a write is confirmed only when every ISR member has it, and only an in-sync replica can be promoted to leader, so committed data isn't lost."

---

**Q. What is leader election?**

**A. (Class answer)**

A leader election is the process of replacing the leader when it fails. What happens is that as soon as the cluster management program (Zookeeper or KRaft) detects that the leader has failed, messages are sent to the other nodes to declare that a new leader is needed. The in sync replicas in the cluster declare that they are candidates to be the new leader. This is followed by a process of confirmation by the other nodes, called voting. If an in sync replica gains more than 50% of votes from nodes in the cluster, it becomes the new leader. Typically, the first in sync replica to declare itself a candidate will be the new leader, but there are edge cases where it can lose the election and a different node will win.

**Expanded:**

**Correction:** Kafka's partition leader election is not a vote among replicas, and there is no ">50% of votes" step. The **controller** (the active KRaft controller, or the controller broker in ZooKeeper mode) notices that a broker has failed and, for each partition that broker led, **picks a new leader from the ISR**, normally the first live replica in the partition's assigned replica list. It then publishes the new leadership to the brokers, and clients update their metadata and reconnect. Leaders are **per partition**, so one broker failure triggers many small elections.

The majority voting the teacher describes does exist, but in a different place: **KRaft controllers** elect the active controller among themselves using Raft, which requires a majority.

See [Training 13 notes](/training-notes-site/notes/training-13/) ("Kafka Reliability (interview core)").

**Say it out loud:** "When a broker fails, the controller picks a new leader for each partition that broker led, choosing from the in-sync replicas so no committed data is lost. Clients then refresh their metadata and switch to the new leader. Majority voting only happens among the KRaft controllers themselves."

---

**Q. What is a leader?**

**A. (Class answer)**

The leader is Kafka's equivalent of a master node. It is the node which is responsible for communication with processes that function outside of the cluster, such as producers and consumers, therefore it is this node which actually streams the data.

**Expanded:**

**Correction:** Leadership is **per partition**, not per cluster. There is no single "master" broker that streams all the data. Each partition has one leader replica, and leaders are spread across brokers, so **every broker is the leader for some partitions and a follower for others**. Producers write to, and by default consumers read from, the leader of each partition they use. (Since Kafka 2.4, consumers can optionally read from a nearby follower.)

**Say it out loud:** "A leader is the replica of a partition that handles its reads and writes. It's per partition, so every broker leads some partitions and follows others, which spreads the load across the cluster."

---

**Q. What is a follower?**

**A. (Class answer)**

Followers are all of the nodes in the Kafka cluster which are not the leader. Each is running a broker, and each is helping to replicate and store parts of the data on the cluster.

**Expanded:**

**Correction:** Like leaders, followers are **per partition**. A follower is a replica that copies (fetches) the partition's data from its leader. A follower that keeps up is part of the ISR and can be promoted if the leader fails. The same broker is a follower for some partitions and the leader for others.

**Say it out loud:** "A follower is a replica of a partition that copies data from that partition's leader so it can take over if the leader fails. Each broker is a follower for some partitions and a leader for others."

---

**Q. What is serialization**

**A. (Class answer)**

Serialization is the process of converting a text format or other type of format to a bytes-like format. This is for the purposes of transmitting the data over a network, which is much easier and faster to do with bytes-like data.

De-serialization is the process of converting bytes-like format back to its original format.

When writing Kafka code in Scala or Java, the serializer must be explicitly declared in the producer, and a deserializer must be explicitly declared in the consumer. In Python, this is taken care of under the hood.

**Expanded:**

**Correction:** In Python it is **not** taken care of under the hood. Kafka itself only stores bytes. With `kafka-python` you must either pass bytes or set a `value_serializer` (and `key_serializer`) on the producer, and a matching `value_deserializer` on the consumer:

```python
import json
from kafka import KafkaProducer
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    key_serializer=lambda k: k.encode("utf-8"),
)
producer.send("weather", key="nyc", value={"temp": 21})
```

Serialization turns an in-memory object into bytes for the network or disk, and deserialization turns them back. Common formats: JSON (readable, no enforced schema), **Avro** and **Protobuf** (compact, with schemas, usually used with a **Schema Registry** so producers and consumers agree on the schema and can evolve it safely).

See [Training 13 notes](/training-notes-site/notes/training-13/) ("Avro" and "Protobuf").

**Say it out loud:** "Kafka only stores bytes, so producers serialize keys and values and consumers deserialize them. In Python that means setting a `value_serializer`, for example `json.dumps` then encode. In production we often use Avro or Protobuf with a schema registry."

---

**Q. What is the max size of a Kafka message**

**A. (Class answer)**

1 MB. For this reason, Kafka is not suitable as a migration tool, but rather is a streaming data tool designed to handle large numbers of small messages.

**Expanded:** The teacher's answer is right as the **default**: the broker setting `message.max.bytes` is about 1 MB (1,048,588 bytes). It is configurable, but raising it also requires changing the producer's `max.request.size` and the consumer's fetch sizes, and big messages hurt throughput and memory. The usual pattern for large payloads is the **claim-check** pattern: store the file in S3 and send a small message with its location.

**Say it out loud:** "About 1 MB by default, configurable on the broker, producer and consumer. Kafka is built for lots of small messages, so for large files I'd put the file in S3 and send a pointer through Kafka."

---


## Hadoop


**Q. What is the architecture of Hadoop?**

**A. (Class answer)**

The most important parts of Hadoop's architecture are HDFS, MapReduce, and YARN.

HDFS is the Hadoop Distributed File System. As it's name suggests, it is a file system, not a database. The files stored in HDFS are distributed across the cluster with a default replication factor of 3. This means that as many as two nodes containing the data can fail, but if one remains, then the data remains available to end users.

MapReduce is the original data processing framework for Hadoop. It processes data using mappers and reducers. These are written in a programming language such as Java, Scala, or Python. Processing is distributed across the nodes in the cluster. MapReduce was revolutionary for its ability to process huge amounts of data, but is no longer in common use. It has been replaced by Spark and other similar technologies. It was deprecated in 2022.

YARN is the cluster manager for Hadoop. From the perspective of the user, YARN is used to administer the cluster and ensure that all of the nodes are visible and functioning properly. It also acts as a load balancer, ensuring that each node gets the correct allocation of work and resources. It consists of the ResourceManager and the NodeManager. The ResourceManager is what allocates resources across the cluster. The NodeManager is the process running on each node which identifies that node to YARN and allows it to be controlled.

**Expanded:**

**Correction:** MapReduce was **not deprecated in 2022**. It is still part of Apache Hadoop 3.x and is still maintained. It is simply rarely chosen for new work, because Spark, Tez and other engines replaced it for most workloads.

| Layer | Component | Role |
|---|---|---|
| Storage | **HDFS**: NameNode (metadata) + DataNodes (blocks) | Distributed file system, files split into 128 MB blocks, each replicated 3 times by default |
| Resources | **YARN**: ResourceManager + NodeManagers | Allocates CPU and memory containers to applications across the cluster |
| Processing | **MapReduce** (or Spark, Tez, Hive on top) | Batch processing using map and reduce phases |
| Shared | Hadoop Common | Shared libraries and utilities |

With replication factor 3, a block survives the loss of two of the three nodes holding it, as the teacher says.

See [Training 6 notes](/training-notes-site/notes/training-6/) ("Hadoop Cluster Components", "HDFS" and "HDFS Components (NameNode, DataNode, HA)").

**Say it out loud:** "Hadoop has three main parts: HDFS for distributed storage, with a NameNode for metadata and DataNodes holding replicated blocks, YARN for resource management, and MapReduce for processing. Today Spark usually replaces MapReduce, but it typically still runs on YARN and HDFS or S3."

---

**Q. What is a NameNode?**

**A. (Class answer)**

The NameNode is effectively the master node in the master-slave architecture of Hadoop. It is the node that the user logs in to, and from which the user controls processes on the rest of the cluster.

**Expanded:**

**Correction:** The NameNode is not "the node the user logs in to". It is the **HDFS metadata master**. It keeps the file system namespace (directories, file names, permissions) and the map of which DataNodes hold each block, all in memory. Clients ask the NameNode *where* blocks are, then read and write the data **directly with the DataNodes**. Users log in to an **edge (gateway) node**, which has the client tools installed but isn't a master.

The NameNode persists its state as an **fsimage** (a snapshot) plus an **edit log** (changes since the snapshot). Without high availability it is a single point of failure.

See [Training 6 notes](/training-notes-site/notes/training-6/) ("HDFS Components (NameNode, DataNode, HA)").

**Say it out loud:** "The NameNode is HDFS's master: it holds all the metadata, the directory tree and which DataNodes hold each block. Clients get block locations from it and then read and write data directly with the DataNodes. Users usually work from an edge node, not the NameNode."

---

**Q. What is a DataNode?**

**A. (Class answer)**

Datanodes are the slave nodes in Hadoop's master-slave architecture. Each DataNode performs its part of distributed storage on HDFS and distributed processing on MapReduce or whichever processing framework is used.

**Expanded:**

**Correction:** Precision on processing: the **DataNode** is the HDFS daemon that stores blocks and serves reads and writes, and it sends heartbeats and block reports to the NameNode. Processing is not done by the DataNode itself but by **YARN containers launched by a NodeManager**, which usually runs on the same worker machine. That co-location is what lets processing run close to the data (data locality).

**Say it out loud:** "A DataNode is the HDFS worker daemon that stores the blocks and reports to the NameNode. The processing on the same machine is done by YARN's NodeManager containers, which is how Hadoop moves compute to the data."

---

**Q. What is a secondary NameNode?**

**A. (Class answer)**

For the purposes of fault-tolerance, the idea of the secondary NameNode was introduced in Hadoop version 2.0. The secondary NameNode acts as a backup NameNode in case the main one fails, and can take over as the main NameNode in that case.

**Expanded:**

**Correction:** This is a classic interview trap. The Secondary NameNode is **not a backup and cannot take over** when the NameNode fails. It only does **checkpointing**: it periodically downloads the fsimage and edit log, merges them into a new fsimage and sends it back, so the edit log doesn't grow forever and restarts are faster. It also existed already in Hadoop 1, not introduced in 2.0.

What Hadoop 2.0 introduced is **NameNode High Availability**: an **Active** and a **Standby NameNode**. The standby stays in sync by reading the edit log from a set of **JournalNodes**, and **ZooKeeper** (with the ZKFailoverController) detects failure and promotes the standby automatically. In an HA setup the standby also does the checkpointing, so no Secondary NameNode is needed.

| | Secondary NameNode | Standby NameNode (HA) |
|---|---|---|
| Purpose | Checkpoint: merge edit log into fsimage | Hot standby for failover |
| Can take over? | No | Yes, automatically |
| Since | Hadoop 1 | Hadoop 2 |

See [Training 6 notes](/training-notes-site/notes/training-6/) ("HDFS Components (NameNode, DataNode, HA)").

**Say it out loud:** "Despite the name, the Secondary NameNode isn't a backup. It just checkpoints by merging the edit log into the fsimage. Failover comes from NameNode high availability, where a Standby NameNode stays in sync through JournalNodes and ZooKeeper promotes it if the active one fails."

---

**Q. What is master-slave architecture?**

**A. (Class answer)**

Master-slave architecture describes a distributed system that consists of multiple nodes (at least 3) that are connected together, and only one of which serves as a control center for the user. The node which the user logs into is called the master node, and the nodes which are controlled by the master are called the slaves.

Because the term master-slave has controversial political implications, some systems replace the name with master-worker or leader-follower. All of those terms refer to the same system architecture.

**Expanded:**

**Correction:** The master is not defined as "the node the user logs into", and there's no minimum of three nodes. In master-worker (leader-follower) architecture, one node or process **coordinates** (keeps metadata, assigns work, tracks health) and the others **do the work**. Users and clients often work from a separate edge node or just talk to the master over the network. Examples: NameNode/DataNodes, YARN ResourceManager/NodeManagers, Spark driver/executors. The weakness is the master as a single point of failure, which is why HA standbys exist. The contrast is **peer-to-peer** (for example Cassandra), where all nodes are equal.

**Say it out loud:** "In master-worker architecture one node coordinates, holding the metadata and assigning work, and the workers do the storage or processing, like HDFS's NameNode and DataNodes. Its weak point is the master, so production systems add a standby. The alternative is peer-to-peer, like Cassandra."

---

**Q. What is Cloudera?**

**A. (Class answer)**

Cloudera is the largest company offering Hadoop as a paid service, giving customers access to cloud-hosted Hadoop instances and an extended suite of software in addition to core Hadoop, including Hue, Impala, and Kudu.

**Expanded:**

**Correction:** Cloudera's main business is not "cloud-hosted Hadoop instances". Cloudera sells an enterprise **data platform** built on Hadoop-ecosystem projects: originally CDH, today **Cloudera Data Platform (CDP)**, which runs **on-premises (Private Cloud) and on AWS, Azure and GCP (Public Cloud)**. It adds management tools (Cloudera Manager), security and governance, and projects Cloudera created or led, such as Impala (SQL engine), Kudu (storage engine) and Hue (web UI). After merging with Hortonworks it is the main remaining Hadoop vendor.

**Say it out loud:** "Cloudera is the main enterprise Hadoop vendor. Its Cloudera Data Platform packages HDFS, Hive, Spark, Impala and so on with management and security tools, and it runs both on-prem and in the cloud."

---

**Q. What is the difference between Cloudera and Hortonworks**

**A. (Class answer)**

Cloudera and Hortonworks were once the two major Enterprise Hadoop companies until Cloudera purchased Hortonworks in 2019. Today Hortonworks is offered as a service by Cloudera but is de-emphasized in favor of their main product.

Hortonworks offers several additions to core Hadoop, including Ambari, Ranger, and a suite of other tools.

**Expanded:**

**Correction:** Today Hortonworks isn't offered as a separate service. The two companies merged in **January 2019**, and Hortonworks Data Platform (HDP) and Cloudera's CDH were both phased out and replaced by the combined **Cloudera Data Platform (CDP)**. Older HDP versions are end-of-life (verify the exact dates if asked).

| | Cloudera (CDH) | Hortonworks (HDP) |
|---|---|---|
| Approach | Open-source core plus proprietary management (Cloudera Manager) | Positioned as 100% open source |
| Signature tools | Cloudera Manager, Impala, Hue, Kudu | Ambari (cluster management), Ranger (security), Atlas (governance) |
| Today | Merged into CDP (2019) | Merged into CDP (2019) |

**Say it out loud:** "They were the two big Hadoop distribution vendors. Hortonworks pushed fully open-source tools like Ambari and Ranger, Cloudera had Cloudera Manager and Impala. They merged in 2019 and both products were replaced by Cloudera Data Platform."

---

**Q. What is the default Hadoop block size?**

**A. (Class answer)**

128 MB

**Expanded:** The teacher's answer is correct: 128 MB in Hadoop 2 and 3 (it was 64 MB in Hadoop 1), set by `dfs.blocksize`. Large blocks keep the NameNode's metadata small and make big sequential reads efficient. A block is a maximum size, not a fixed allocation (see the small file question below).

See [Training 6 notes](/training-notes-site/notes/training-6/) ("HDFS Blocks").

**Say it out loud:** "128 MB in Hadoop 2 and later, configurable with `dfs.blocksize`. Large blocks keep the NameNode's metadata small and favor big sequential reads."

---

**Q. What is the small file problem?**

**A. (Class answer)**

The small file problem is an issue that is caused by saving a large number of small files on HDFS. Because the Hadoop block size is 128 MB, any file that is smaller than that will occupy an entire block, which leads to inefficient storage. It also negatively affects data processing times, so a job done on a large number of small files will be slower than a properly partitioned dataset.

**Expanded:**

**Correction:** A small file does **not** occupy an entire 128 MB block on disk. A 1 MB file uses about 1 MB (times the replication factor). The real costs are:
- **NameNode memory:** every file, directory and block is an object in the NameNode's RAM, roughly 150 bytes each. Millions of tiny files can exhaust the NameNode even when the disks are mostly empty.
- **Processing overhead:** Spark, Hive and MapReduce usually create at least one task (split) per file, so many tiny files mean many tiny tasks, with scheduling and file-open overhead dominating. On S3 the same issue shows up as slow listing and per-request overhead.

Fixes: compact small files (Spark `coalesce`/`repartition` before writing, Hive `CONCATENATE`, Delta `OPTIMIZE`), batch streaming writes into larger files, and don't over-partition tables. Aim for files of roughly 128 MB to 1 GB.

See [Training 6 notes](/training-notes-site/notes/training-6/) ("The Small File Problem" and "The Small File Problem in Practice").

**Say it out loud:** "The small file problem isn't wasted disk, since a small file only uses its real size. It's that every file and block is an object in the NameNode's memory, and every file usually becomes its own task, so millions of small files overload the NameNode and slow jobs down. The fix is compacting files to a few hundred MB each."

---

**Q. Why is mapreduce not used much anymore**

**A. (Class answer)**

MapReduce fell out of favor when Apache Spark was released. Spark is able to process data 100x faster than MapReduce, and because of that, it made MapReduce obsolete.

The reason that Spark is so much faster than MapReduce is that it performs all computations in memory. MapReduce, on the other hand, performs some operations in memory and other operations on disk. It is neither the memory nor the disk that makes it slow, rather it is the transfer of data from the disk to the memory or from the memory to the disk that causes the problem. This is called Disk I/O, meaning disk input and output. The act of needing to transfer the data between different parts of the machine causes a bottleneck, meaning that the flow of data becomes restricted at that point. Because Spark does all computations in memory, it avoids the need to do Disk I/O completely, therefore removing a restriction on processing speed.

**Expanded:**

**Correction:** Spark does **not** do all computation in memory or avoid disk I/O completely. Spark reads input from disk, writes **shuffle files to local disk**, and **spills** to disk when memory runs out. What makes it faster:
- **No HDFS writes between steps.** A chain of MapReduce jobs writes each job's full output to HDFS (replicated 3 times) and reads it back for the next job. Spark keeps intermediate data in memory where it can and pipelines narrow steps inside one stage.
- **One optimized DAG** for the whole job instead of separate rigid map-then-reduce jobs.
- **Caching** of data reused across steps, which is a big win for iterative work such as machine learning.
- **Lower overhead:** long-lived executors instead of a new JVM per task.

The "100x faster" figure is Spark's marketing benchmark for in-memory, iterative workloads. For ordinary disk-bound ETL the gain is smaller (often a few times). Spark also wins on usability: high-level DataFrame/SQL APIs, plus streaming and ML in one engine.

See [Training 6 notes](/training-notes-site/notes/training-6/) ("MapReduce: Memory vs. Disk").

**Say it out loud:** "Spark replaced MapReduce because it doesn't write intermediate results to HDFS between every step. It pipelines work in one optimized DAG, keeps data in memory where it can and can cache reused data. It still uses disk for shuffles and spills, but it's much faster, especially for iterative jobs, and much easier to write."

---

**Q. What is Sqoop?**

**A. (Class answer)**

Sqoop is a command line tool that can be used to migrate data between a standard SQL database and HDFS. Its name can be understood as "SQL to Hadoop", which describes exactly what it does.

**Expanded:**

**Correction:** The description is right, but Sqoop is no longer an active project. **Apache Sqoop was retired to the Apache Attic in 2021.** It moved data in **both directions** (`sqoop import` from a database into HDFS or Hive, `sqoop export` back out), running as parallel MapReduce jobs over JDBC. Modern replacements:

| Need | Tool |
|---|---|
| Bulk copy from a database | Spark JDBC reads (`spark.read.jdbc` with partitioning options), AWS Glue |
| Database migration or ongoing replication | AWS DMS |
| Change data capture into Kafka | Debezium / Kafka Connect |

See [Training 24 notes](/training-notes-site/notes/training-24/) ("CDC and AWS DMS").

**Say it out loud:** "Sqoop was a command-line tool for bulk importing tables from relational databases into HDFS or Hive and exporting them back, using parallel MapReduce jobs. It was retired in 2021, so today I'd use Spark JDBC, Glue or DMS, or Debezium for change data capture."

---


## Clusters


**Q. What is a distributed system?**

**A. (Class answer)**

A distributed system is any group of computers that are connected together and which work together on a common task. Examples include clusters, which we use in Hadoop and Spark, as well as peer-to-peer networks (p2p) which includes systems such as SETI (Search for Extraterrestrial Intelligence) and Folding At Home (a distributed program for computing protein folds for biological research), as well as file sharing software such as Bittorrent and Napster.

Many Big Data Engineers with a masters degree have their degree in Distributed Systems.

**Expanded:**

**Correction:** Two of the examples are not really peer-to-peer. **SETI@home and Folding@home are volunteer computing**: a central server hands out work units to clients, which is client-server. **Napster** used a **central index server** to find files, with only the downloads going peer-to-peer. **BitTorrent** is a good peer-to-peer example.

A distributed system is a set of computers that communicate over a network and coordinate to act like one system. The core challenges are the reasons behind most big data design choices: partial failures (one node dies while others continue), network delays and partitions, keeping data consistent across copies (CAP), and coordinating without a shared clock.

See [Training 0 notes](/training-notes-site/notes/training-0/) ("What's the difference between a peer-to-peer network and a compute cluster?") and [Training 6 notes](/training-notes-site/notes/training-6/) ("Fault Tolerance").

**Say it out loud:** "A distributed system is a group of networked computers that work together and appear as one system, like a Hadoop or Kafka cluster. The hard parts are partial failures, network partitions and keeping copies of data consistent, which is why things like replication and the CAP theorem matter."

---

**Q. What is a cluster?**

**A. (Class answer)**

A cluster is a specific type of distributed system in which each node is connected to each other node using a Local Area Network (LAN) connection in which all of the nodes are configured to work together on a common task.

**Expanded:** The teacher's answer is fine. Precision: nodes are not wired directly to every other node. They connect through network **switches**, so any node can reach any other. A cluster is centrally managed, usually in one data center (or one cloud region), with a fast, low-latency network, and is used as a single resource for storage or computing (HDFS, Spark, Kafka). That central management and shared purpose is what separates it from a loose peer-to-peer network.

See [Training 0 notes](/training-notes-site/notes/training-0/) ("How do the machines in a compute cluster actually connect (SSH, local IPs, switches)?").

**Say it out loud:** "A cluster is a group of machines on a fast local network, managed as one system for a shared job like storage or processing, for example a Hadoop or Spark cluster."

---

**Q. What is a node?**

**A. (Class answer)**

A node in a cluster refers to a physical computer which makes up one part of a compute cluster.

It is important to remember that a Spark Executor IS NOT A NODE. An executor is a software process that runs on a node. There can be multiple executors running on one node.

**Expanded:** The teacher's answer is fine, with one update: in the cloud, a "node" is usually a **virtual machine** (for example an EC2 instance in an EMR cluster), not a dedicated physical computer. Kubernetes also calls its machines nodes. The executor point is important: an executor is a process, and one node can run several.

**Say it out loud:** "A node is one machine in a cluster, physical on-prem or usually a VM in the cloud. Processes like Spark executors run on nodes, and one node can host several executors."

---


## Hive


**Q. What is Hive**

**A. (Class answer)**

Hive is a combination of a SQL Query Engine that can work with HDFS data, as well as a Data Warehousing platform that can run on a Hadoop system. It originally used MapReduce as its processing engine, but today we are far more likely to use Tez instead, as it is the default and it has Spark-like processing speeds.

**Expanded:** The teacher's answer is right. More precisely: Hive is a **data warehouse layer on Hadoop**. It puts tables on top of files in HDFS or S3, lets you query them with **HiveQL** (SQL), and compiles the queries into jobs on an execution engine: originally MapReduce (deprecated in Hive 2), today **Tez** by default, or Spark. Its most lasting part is the **Hive Metastore**, the table catalog that Spark, Presto/Trino and others still use. It is **schema-on-read** and built for large batch queries, not low-latency lookups or frequent row-level updates (ACID tables exist but are limited).

See [Training 6 notes](/training-notes-site/notes/training-6/) ("Hive" and "HiveQL") and [Training 8 notes](/training-notes-site/notes/training-8/) ("Hive Architecture and Partitioned Tables").

**Say it out loud:** "Hive is a SQL data warehouse layer on Hadoop. It maps tables onto files in HDFS or S3, and HiveQL queries run on Tez or Spark. Its metastore is still the standard table catalog that Spark and other engines use."

---

**Q. Partitioning vs Bucketing**

**A. (Class answer)** *(no answer given)*

**Expanded:**

| | Partitioning | Bucketing |
|---|---|---|
| How | One **directory** per value of the partition column (`.../dt=2024-01-01/`) | Rows hashed on a column into a **fixed number of files** (buckets) |
| Best column | Low-cardinality columns you filter on (date, region) | High-cardinality columns you join or aggregate on (`customer_id`) |
| Main benefit | **Partition pruning**: skip whole directories when filtering | Fewer shuffles for joins on the bucket column, efficient sampling |
| Risk | Too many partitions → the small file problem | Bucket count is fixed when the table is created |

```sql
CREATE TABLE trips (trip_id BIGINT, customer_id BIGINT, amount DOUBLE)
PARTITIONED BY (dt STRING)
CLUSTERED BY (customer_id) INTO 32 BUCKETS
STORED AS PARQUET;
```

See [Training 6 notes](/training-notes-site/notes/training-6/) ("Partitioning vs. Bucketing").

**Say it out loud:** "Partitioning creates a directory per value of a low-cardinality column like date, so filters can skip whole partitions. Bucketing hashes a high-cardinality column like customer ID into a fixed number of files, which helps joins on that column avoid shuffles."

---

**Q. Internal vs External table**

**A. (Class answer)** *(no answer given)*

**Expanded:**

| | Internal (managed) | External |
|---|---|---|
| Who owns the data | Hive manages it, stored in the warehouse directory | You do. The table points to a `LOCATION` you choose (HDFS path, S3 prefix) |
| `DROP TABLE` | Deletes **metadata and data** | Deletes **only metadata**. The files remain |
| Typical use | Intermediate or temporary tables fully owned by Hive | Data lakes, where files are shared with other tools (Spark, Athena) or loaded by other pipelines |

```sql
CREATE EXTERNAL TABLE bronze_trips (...)
STORED AS PARQUET
LOCATION 's3://bucket/bronze/trips/';
```

See [Training 6 notes](/training-notes-site/notes/training-6/) ("Internal (Managed) vs. External Tables").

**Say it out loud:** "With a managed table, Hive owns the data, so dropping the table deletes the files. An external table just points at files in a location I control, so dropping it only removes the metadata. Data lakes use external tables."

---

**Q. What is the Hive Metastore**

**A. (Class answer)** *(no answer given)*

**Expanded:** The Hive Metastore (HMS) is the **catalog** of table metadata: database and table names, column schemas, partition lists, file locations, formats and SerDes. The metadata is stored in a relational database (MySQL or Postgres in production, embedded Derby only for testing) and served by a Thrift service. It matters beyond Hive: **Spark SQL, Trino/Presto and Impala** read the same metastore, so one table definition works across engines. AWS's **Glue Data Catalog** is a managed, Hive-metastore-compatible replacement (EMR and Athena use it), and Databricks' **Unity Catalog** is a newer successor.

See [Training 6 notes](/training-notes-site/notes/training-6/) ("Metastore (General Definition)" and "Hive Metastore").

**Say it out loud:** "The Hive Metastore is the catalog of table metadata, schemas, partitions and file locations, stored in a relational database. Spark, Trino and others share it, and on AWS the Glue Data Catalog plays the same role."

---


## HBase


**Q. What is HBase**

**A. (Class answer)**

HBase is a NoSQL database that runs on the Hadoop stack. It is a column family type NoSQL database, which means that it uses column families as a substitute for tables. This means that queries can be performed in a way that the columns that are not queried can be completely ignored, which makes for faster query performance.

**Expanded:**

**Correction:** Column families are not "a substitute for tables". HBase **has tables**. Each table has a **row key** and one or more **column families**, and each family holds any number of columns (qualifiers) that can differ from row to row. Data in each column family is stored in separate files, which is why reading one family can skip the others.

HBase is a **wide-column NoSQL store** modeled on Google's Bigtable, running on HDFS (with ZooKeeper for coordination). Key facts:
- Rows are sorted by **row key**, and that key is the only built-in index, so key design is everything (avoid hot-spotting with sequential keys).
- Strongly consistent reads and writes per row (**CP** in CAP terms).
- Built for random, low-latency reads and writes on huge tables, unlike HDFS + Hive, which are for batch scans.
- Cells are versioned by timestamp.

See [Training 13 notes](/training-notes-site/notes/training-13/) ("Types of NoSQL Database").

**Say it out loud:** "HBase is a wide-column NoSQL database on top of HDFS, modeled on Bigtable. Tables are sorted by row key and split into column families stored separately. It gives fast, strongly consistent random reads and writes by key, where Hive is for batch scans."

---


## Cassandra


**Q. What is a column family?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A column family is a **group of columns stored together**, the core unit of **wide-column** databases (Bigtable, HBase, Cassandra).
- **HBase/Bigtable:** a table has a row key and a few column families defined up front. Each family can hold any number of columns, which can differ per row, and each family is stored in its own files, so reading one family skips the others.
- **Cassandra:** "column family" is the **old name for a table** (CQL renamed it). Rows are identified by a partition key and ordered by clustering columns.

Not to be confused with **columnar** storage (Parquet, Redshift), which stores each column separately for analytics.

See [Training 13 notes](/training-notes-site/notes/training-13/) ("Types of NoSQL Database").

**Say it out loud:** "A column family is a group of related columns stored together in wide-column databases like HBase, where each row can have different columns within a family. In Cassandra, column family is just the old name for a table."

---

**Q. What is peer to peer architecture?**

**A. (Class answer)** *(no answer given)*

**Expanded:** In peer-to-peer architecture **all nodes are equal**: there is no master, and any node can serve any request. Nodes discover each other and share state directly (in Cassandra, through the **gossip** protocol), and data is spread and replicated among peers. Benefits: no single point of failure, easy horizontal scaling (add a node), high availability. Cost: coordinating consistency is harder, so these systems often offer **tunable or eventual consistency**. Examples: **Cassandra**, Amazon's original Dynamo design, Riak, BitTorrent.

| | Master-worker | Peer-to-peer |
|---|---|---|
| Coordinator | One master (with standby) | Any node |
| Single point of failure | The master | None |
| Examples | HDFS, YARN, Spark | Cassandra, BitTorrent |

See [Training 0 notes](/training-notes-site/notes/training-0/) ("What's the difference between a peer-to-peer network and a compute cluster?").

**Say it out loud:** "In peer-to-peer architecture every node is equal, with no master, so any node can handle any request and there's no single point of failure. Cassandra works this way, with nodes sharing cluster state by gossip."

---

**Q. What is ring architecture?**

**A. (Class answer)**

The ring architecture of a feature of the hardware portion of Cassandra which provides us with a leaderless system which is optimized for high availability. In a ring architecture, each node is connected to exactly two other nodes. This can be visualized as a circle of dots connected to each other. This gives us high availability because every node is equal, with no master. If any node in a Cassandra cluster fails, the nodes to either side of the failed node simply connect. That way the ring is preserved.

**Expanded:**

**Correction:** The "ring" is **not a physical network** where each node connects to exactly two neighbors, and nodes don't "reconnect around" a failure. The ring is a **logical token ring from consistent hashing**:
- Each row's **partition key** is hashed (Murmur3) to a **token**. The full token range forms a circle, and each node (through many **virtual nodes**) owns slices of it.
- A row is stored on the node that owns its token, and **replicated to the next nodes clockwise** until the **replication factor** is reached (with `NetworkTopologyStrategy`, spread across racks and data centers).
- Nodes talk to **any** other node directly, and share membership and health via **gossip**. **Any node can coordinate** a client request.
- When a node fails, its data is still available from the **replicas**. **Hinted handoff** stores writes for the down node, and **repair** syncs it later. Adding a node only moves the data for the token ranges it takes over (the benefit of consistent hashing).
- Availability vs consistency is **tunable** per query: `ONE`, `QUORUM`, `LOCAL_QUORUM`, `ALL`. With RF=3, `QUORUM` reads + `QUORUM` writes (2 + 2 > 3) give strong consistency.

So high availability comes from **replication and tunable consistency**, not from neighbors reconnecting.

**Say it out loud:** "Cassandra's ring is a logical token ring from consistent hashing: each partition key hashes to a token, each node owns ranges of tokens, and data is replicated to the next nodes clockwise. Any node can coordinate a request, and if a node fails the replicas serve the data, with consistency tunable per query, such as QUORUM."

---

**Q. What is meant by high availability?**

**A. (Class answer)** *(no answer given)*

**Expanded:** High availability means a system **keeps working with minimal downtime** even when parts of it fail. It is measured as uptime percentage ("nines"):

| Availability | Downtime per year |
|---|---|
| 99.9% | About 8.8 hours |
| 99.99% | About 53 minutes |
| 99.999% | About 5 minutes |

Achieved by **eliminating single points of failure**: redundancy and replication (HDFS 3 copies, Kafka RF 3), automatic **failover** (Standby NameNode, Kafka leader election, RDS Multi-AZ), spreading across **availability zones**, health checks and load balancing. Related but different: **fault tolerance** (keep working through failure without interruption), **durability** (data isn't lost) and **disaster recovery** (recover from a full region or site loss, measured by RPO and RTO).

See [Training 6 notes](/training-notes-site/notes/training-6/) ("Fault Tolerance").

**Say it out loud:** "High availability means the system stays up despite failures, measured in nines of uptime. It comes from removing single points of failure with replication, automatic failover and spreading across availability zones, like Kafka's replicated partitions or RDS Multi-AZ."

---


## MongoDB


**Q. What format does MongoDB use?**

**A. (Class answer)** *(no answer given)*

**Expanded:** MongoDB stores **documents** in **BSON** (Binary JSON): a binary encoding of JSON-like documents that adds types JSON lacks (`ObjectId`, `Date`, `Decimal128`, binary data, 32/64-bit integers) and is fast to traverse. You read and write them as JSON-like documents. Documents live in **collections** (instead of tables), can nest objects and arrays, and need not share a schema (optional schema validation exists). Each has a unique `_id`. Maximum document size is **16 MB**. Data modeling question: **embed** related data in one document when it's read together, or **reference** it in another collection when it's large or shared.

See [Training 14 notes](/training-notes-site/notes/training-14/) ("MongoDB Document Model and Nested JSON") and [Training 13 notes](/training-notes-site/notes/training-13/) ("MongoDB as the Spark Sink").

**Say it out loud:** "MongoDB stores documents in BSON, a binary form of JSON with extra types like ObjectId and dates. Documents sit in collections, can nest objects and arrays, don't need a fixed schema, and can be up to 16 MB each."

---


## Data Lakes, Warehouses, and Lakehouses


**Q. What is a data warehouse?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A data warehouse is a central database **optimized for analytics (OLAP)**. It integrates cleaned, structured data from many sources and keeps history, for reporting and BI. Characteristics: **schema-on-write** (data is modeled before it's loaded), **columnar storage** and MPP processing, **dimensional models** (star schemas). Examples: Redshift, Snowflake, BigQuery, Synapse. Bill Inmon's classic definition: subject-oriented, integrated, time-variant and non-volatile.

| | OLTP database | Data warehouse |
|---|---|---|
| Purpose | Run the business (transactions) | Analyze the business |
| Workload | Many small reads and writes | Large scans and aggregations |
| Modeling | Normalized (3NF) | Denormalized (star schema) |
| Storage | Row-oriented | Columnar |

See [Training 4 notes](/training-notes-site/notes/training-4/) ("What is a Data Warehouse?") and [Training 5 notes](/training-notes-site/notes/training-5/) ("Analytical Databases: On-Premises vs Cloud").

**Say it out loud:** "A data warehouse is a central, analytics-optimized database that integrates cleaned, structured data from many sources with history, usually modeled as star schemas in columnar storage, like Redshift or Snowflake. It's for analysis, unlike transactional databases."

---

**Q. What is a data lake?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A data lake is a central repository that stores **raw data of any type** (structured, semi-structured, unstructured) **in its native format**, cheaply, in **object storage** (S3, ADLS, GCS). It is **schema-on-read**: structure is applied when the data is queried (Athena, Spark), not when it's stored. Strengths: cheap, scalable, flexible, good for ML and keeping raw history. Risks: without a catalog, governance and quality controls it becomes a **"data swamp"**, and plain files lack ACID transactions, which **table formats** (Delta, Iceberg, Hudi) and the **lakehouse** model fix.

See [Training 5 notes](/training-notes-site/notes/training-5/) ("Data Lakehouse vs Data Warehouse" and "Object Store") and [Training 18 notes](/training-notes-site/notes/training-18/) ("S3 in the Lakehouse").

**Say it out loud:** "A data lake stores raw data of any type in its native format in cheap object storage like S3, and applies the schema when it's read. It's flexible and cheap, but it needs a catalog and governance, and table formats like Delta or Iceberg add the reliability it lacks."

---

**Q. What is a star schema?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A star schema is a dimensional model with one central **fact table** surrounded by **dimension tables**, each joined directly to the fact through a key, so the diagram looks like a star.
- **Fact table:** measurable events at a defined **grain** (one row per trip, per sale): numeric **measures** (amount, quantity) plus **foreign keys** to dimensions. Long and narrow.
- **Dimension tables:** descriptive context (date, station, customer, product), **denormalized**, usually with a surrogate key. Short and wide.

Benefits: simple, fast queries (one join per dimension), easy for BI tools and business users.

```sql
SELECT d.month, s.borough, SUM(f.trip_count)
FROM fact_trips f
JOIN dim_date d    ON f.date_key = d.date_key
JOIN dim_station s ON f.station_key = s.station_key
GROUP BY d.month, s.borough;
```

See [Training 5 notes](/training-notes-site/notes/training-5/) ("Star Schema", "Fact Table" and "Dimension Table") and [Training 21 notes](/training-notes-site/notes/training-21/) ("Building the star schema").

**Say it out loud:** "A star schema has a central fact table of measurable events at a set grain, with foreign keys to denormalized dimension tables like date, product or customer. Each dimension is one join away, so queries are simple and fast."

---

**Q. What is a snowflake schema?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A snowflake schema is a star schema whose **dimensions are normalized** into sub-dimensions: for example `dim_product → dim_category → dim_department`, instead of keeping category and department as columns in `dim_product`.

| | Star | Snowflake |
|---|---|---|
| Dimensions | Denormalized, one table each | Normalized into several tables |
| Joins | Fewer | More |
| Redundancy / storage | More | Less |
| Query simplicity and speed | Better | Worse |

Modern columnar warehouses make storage cheap, so star schemas are usually preferred. (It's unrelated to the company Snowflake.)

See [Training 5 notes](/training-notes-site/notes/training-5/) ("Snowflake Schema").

**Say it out loud:** "A snowflake schema is a star schema with normalized dimensions, split into sub-tables like product, category and department. It saves storage and redundancy but needs more joins, so star schemas are usually preferred in modern warehouses."

---

**Q. What is dimensional modeling?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Dimensional modeling is a design technique for analytical databases, popularized by **Ralph Kimball**, that organizes data into **facts** (measurements of business processes) and **dimensions** (the context for those measurements), usually as star schemas. Kimball's four-step process:
1. **Choose the business process** (bike trips, orders).
2. **Declare the grain** (one row per trip).
3. **Identify the dimensions** (date, station, customer).
4. **Identify the facts** (duration, count, amount).

Vocabulary: additive vs semi-additive vs non-additive facts, conformed dimensions (shared across fact tables), surrogate keys, slowly changing dimensions, degenerate dimensions (an order number kept in the fact), junk dimensions.

See [Training 5 notes](/training-notes-site/notes/training-5/) ("Dimensional Schemas" and "Dimensional Modeling Vocabulary (Interview Staples)").

**Say it out loud:** "Dimensional modeling organizes analytical data into facts, the measurements, and dimensions, the context, usually as a star schema. Kimball's steps are: pick the business process, declare the grain, then identify the dimensions and the facts."

---

**Q. Who is Ralph Kimball?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Ralph Kimball is a data warehousing pioneer who popularized **dimensional modeling** (star schemas, facts and dimensions, slowly changing dimensions) and the **bottom-up** approach: build business-process data marts with **conformed dimensions** that together form the warehouse (the "bus architecture"). Key book: ***The Data Warehouse Toolkit*** (first edition 1996). His approach is usually contrasted with **Bill Inmon's** top-down approach: a normalized (3NF) enterprise warehouse first, with data marts built from it. Data Vault (Dan Linstedt) is a third method.

| | Kimball | Inmon |
|---|---|---|
| Direction | Bottom-up | Top-down |
| Core model | Dimensional (star schemas) | Normalized enterprise warehouse (3NF) |
| Speed to value | Faster | Slower, more upfront design |

See [Training 5 notes](/training-notes-site/notes/training-5/) and [Training 22 notes](/training-notes-site/notes/training-22/) ("Data Warehouse Design (Beyond Dimensional Modeling)").

**Say it out loud:** "Ralph Kimball is the data warehousing pioneer behind dimensional modeling and *The Data Warehouse Toolkit*. His bottom-up approach builds star schemas per business process with conformed dimensions, in contrast to Bill Inmon's top-down normalized enterprise warehouse."

---


## Data Formats


**Q. What is parquet?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Apache Parquet is an open-source **columnar** file format for analytics.
- **Columnar:** each column is stored together, so queries read only the columns they need (**column pruning**), and similar values compress very well (Snappy, ZSTD, dictionary and run-length encoding).
- **Structure:** a file is split into **row groups**, each holding a **column chunk** per column, made of pages. The footer stores the **schema** and **min/max statistics** per row group, which enables **predicate pushdown** (skipping row groups that can't match a filter).
- **Self-describing** with a schema, supports nested data, splittable for parallel processing.
- Downsides: slower to write, not human-readable, not good for single-row lookups or frequent updates (table formats solve updates).

It's the default format of Spark, and the file format under Delta Lake and Iceberg.

See [Training 6 notes](/training-notes-site/notes/training-6/) ("File Storage Formats").

**Say it out loud:** "Parquet is a columnar file format: each column is stored and compressed together, so queries read only the columns they need, and min/max statistics in the footer let engines skip row groups. It's the standard for analytics and sits under Delta and Iceberg."

---

**Q. What is ORC**

**A. (Class answer)** *(no answer given)*

**Expanded:** ORC (Optimized Row Columnar) is a **columnar** file format created for **Hive** (by Hortonworks, 2013). Data is stored in **stripes** (about 64 MB by default) with lightweight indexes (min/max per 10,000 rows), stripe statistics and a file footer, giving column pruning, predicate pushdown and strong compression (ZLIB or Snappy). It supports Hive ACID tables and has bloom filters. Compared with Parquet: very similar in idea and performance. ORC is strongest in the Hive ecosystem, while Parquet has broader support across tools and clouds (Spark, Athena, BigQuery, Snowflake), so Parquet is the more common choice today.

See [Training 6 notes](/training-notes-site/notes/training-6/) ("ORC").

**Say it out loud:** "ORC is a columnar format built for Hive, storing data in stripes with indexes and statistics for predicate pushdown and good compression. It's very similar to Parquet. ORC is common in Hive shops, while Parquet has wider ecosystem support."

---

**Q. What is Avro**

**A. (Class answer)** *(no answer given)*

**Expanded:** Apache Avro is a **row-based**, binary serialization format with a **schema defined in JSON**. The schema is stored in the file header, or in a **Schema Registry** for Kafka messages, where each message carries only a small schema ID.
- **Row-based**, so it is fast to write and read whole records: good for **streaming and messaging** (Kafka) and for raw/landing data. It's not ideal for analytical scans (Parquet is better).
- **Schema evolution** is its strength: you can add fields with defaults or remove optional fields, and old and new readers and writers stay compatible (backward/forward compatibility rules).
- Compact, splittable, language-neutral.

| | Avro | Parquet / ORC |
|---|---|---|
| Layout | Row-based | Columnar |
| Best for | Writing records, streaming, Kafka | Analytical reads |
| Schema evolution | Excellent | Supported, more limited |

See [Training 6 notes](/training-notes-site/notes/training-6/) ("Avro" and "Schema Evolution: Beyond Avro") and [Training 13 notes](/training-notes-site/notes/training-13/) ("Avro").

**Say it out loud:** "Avro is a row-based binary format with a JSON schema. It's fast for writing whole records and has excellent schema evolution, so it's the usual choice for Kafka messages with a schema registry, while Parquet is better for analytical queries."

---


## Elastic Stack


**Q. What is ElasticSearch**

**A. (Class answer)**

ElasticSearch is a combination of a search engine and a NoSQL database. It is used primarily to build internal search engines for websites. Famously, it is used by Ebay to power their auction search. Data is ingested into Elasticsearch using a REST API command, and must be in JSON format to be accepted. Once it is in the database, it is searchable using a normal text search as you would find on a regular website.

**Expanded:** The answer is broadly right. Elasticsearch is a distributed **search and analytics engine** built on **Apache Lucene**. It stores JSON **documents** in **indexes** and builds an **inverted index** (word → documents) so full-text search is fast, with results ranked by **relevance**. Indexes are split into **shards** with replicas across nodes. Queries use the JSON **Query DSL** over a REST API (plus a SQL interface). Main uses: site and product search, **log analytics** (the ELK stack), metrics, and **vector search**. It isn't a primary transactional database: it's near-real-time (documents become searchable after a refresh, about 1 second by default) and has no multi-document transactions.

Precision on eBay (verify): eBay is often cited as a large Elasticsearch user and does run it at large scale, but eBay's main marketplace search engine is reported to be its own system (Cassini). Safer interview examples: Wikipedia, GitHub search and log analytics generally.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("Elasticsearch / AWS OpenSearch" and "Elasticsearch: why eBay, not Google").

**Say it out loud:** "Elasticsearch is a distributed search and analytics engine built on Lucene. It stores JSON documents and uses an inverted index for fast full-text search ranked by relevance, and it's used for site search, log analytics and vector search."

---

**Q. What is Logstash**

**A. (Class answer)**

Logstash is a system that can connect ElasticSearch to other systems, among other features. It got its name from being a repository for ElasticSearch logs, which it still does, but now has other features and extensions. The extensions to logstash are called Beats. Popular beats include FileBeat, MetricBeat, and HeartBeat.

**Expanded:**

**Correction:** Two corrections:
- Logstash isn't named for being "a repository for Elasticsearch logs", and it doesn't store data. It is a server-side **data processing pipeline** with three stages: **inputs** (files, Beats, Kafka, JDBC, S3) → **filters** (parse and transform, for example `grok` for log lines, `date`, `mutate`, `geoip`) → **outputs** (Elasticsearch, S3, Kafka). Elasticsearch does the storing.
- **Beats are not extensions of Logstash.** They are separate, lightweight **data shippers** (agents written in Go) installed on servers, such as Filebeat (log files), Metricbeat (system and service metrics) and Heartbeat (uptime). They send data **to** Logstash or directly to Elasticsearch. Logstash's own extensions are called **plugins**.

Typical flow: **Beats → Logstash → Elasticsearch → Kibana**.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("The ELK Stack").

**Say it out loud:** "Logstash is the processing pipeline of the ELK stack: inputs collect data, filters like grok parse and enrich it, and outputs send it to Elasticsearch. Beats are separate lightweight agents, like Filebeat, that ship data from servers into Logstash or Elasticsearch."

---

**Q. What is Kibana**

**A. (Class answer)**

Kibana is a data visualization tool which is built into the Elastic Stack. It is JavaScript-based and runs in a website. It is known for being able to create high quality visualizations with a relatively low amount of input.

**Expanded:** The answer is correct. Precision: Kibana is the **web UI for Elasticsearch**, a separate component of the Elastic Stack that reads from Elasticsearch. Features: **Discover** (search and filter raw documents and logs), visualizations and **dashboards**, alerting, and stack management. It's mostly used for log and operational analytics rather than business BI. On AWS, the fork is **OpenSearch Dashboards**.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("The ELK Stack").

**Say it out loud:** "Kibana is the web interface of the Elastic Stack. It lets you search the data in Elasticsearch and build visualizations and dashboards, mostly for logs and operational monitoring."

---

**Q. What data format does Elasticsearch accept?**

**A. (Class answer)**

JSON

**Expanded:** The answer is correct: **JSON documents**. Bulk loads use **NDJSON** (newline-delimited JSON) through the `_bulk` API. Other formats (CSV, log lines, PDFs) are converted to JSON first, by Logstash, Beats or an **ingest pipeline** (for example the attachment processor for files). Each index has a **mapping** (its schema: field types such as `text` for full-text search vs `keyword` for exact values), inferred automatically or defined explicitly.

**Say it out loud:** "JSON documents. Bulk loads use newline-delimited JSON, and other formats are converted by Logstash or ingest pipelines. Each index has a mapping that defines field types like text versus keyword."

---

**Q. How do you enter data into Elasticsearch?**

**A. (Class answer)**

Data is entered into ElasticSearch using a RESTful API command, which can be done programmatically in any programming language that supports HTTP, or it can be done using CURL.

**Expanded:** The answer is correct. Concretely:

```bash
# one document
curl -X POST "localhost:9200/listings/_doc" -H "Content-Type: application/json" \
     -d '{"title": "red running shoes", "price": 49.99}'

# many documents in one request (NDJSON)
curl -X POST "localhost:9200/_bulk" -H "Content-Type: application/x-ndjson" --data-binary @bulk.ndjson
```

Other routes: official **client libraries** (Python `elasticsearch` with `helpers.bulk`), **Logstash** and **Beats**, Kafka Connect's Elasticsearch sink, **Amazon Data Firehose** into OpenSearch, and the Spark connector (`elasticsearch-hadoop`). For volume, always use the bulk API.

See [Training 29 notes](/training-notes-site/notes/training-29/).

**Say it out loud:** "Through its REST API, with curl or a client library: a single document goes to the `_doc` endpoint and large loads use the `_bulk` API. In pipelines, data usually arrives through Logstash, Beats, Kafka Connect or Firehose."

---

