---
title: Day 7 Vocabulary
description: Glossary of terms and definitions from the Training 7 notes.
sidebar:
  order: 7
---

Vocabulary — Study Guide Day 7

Source: notes/Training 7.md

## spark-submit Core Arguments
- **spark-submit** — Command-line tool that launches a Spark application (Python, Scala or Java) onto a cluster; its many arguments are best learned by category.
- **spark-submit --help** — Shows the exact arguments supported by the installed Spark version.
- **--master** — Sets the cluster manager / execution target (e.g. `yarn`, `spark://...`, `k8s://...`).
- **--deploy-mode** — Sets where the driver runs: `client` or `cluster`.
- **--class** — Main class for compiled Java/Scala applications; not needed for `.py` files.
- **--name** — Sets the application name.
- **--conf** — Sets any `spark.*` configuration property, giving access to settings that have no dedicated flag.
- **--properties-file** — Loads Spark properties from a file.
- **--verbose** — Shows detailed submission information.

## Driver and Executor Resources
- **Driver** — The process that reads the job's configuration and logic, builds the plans, schedules tasks onto executors and collects results.
- **Executor** — A process, part of Spark's software (a JVM process), that runs on the cluster's nodes and executes tasks.
- **Worker** — In Spark, a computer: the physical (or virtual) node in the cluster on which the program runs; usually hosts multiple executors.
- **--driver-memory** — Like executor memory, but for the driver application.
- **--driver-java-options** — Extra JVM options for the driver.
- **--driver-library-path** — Extra native library path for the driver.
- **--driver-class-path** — Extra classpath entries for the driver.
- **--executor-memory** — The amount of RAM allocated to each executor.
- **--executor-cores** — The number of CPU cores each executor uses to process its share of the data.
- **--num-executors** — The number of executors used in the job, distributed across the nodes (commonly YARN).
- **--total-executor-cores** — Total core budget across all executors, mainly for Standalone/Mesos.
- **.collect()** — Action that returns all results to the driver; dangerous for large data.

## Executor Sizing
- **Executor sizing rule of thumb** — Use 5 cores per executor; executors per node = cores per node / 5, rounded down.
- **Executor memory calculation** — RAM per node divided by executors per node, rounded down, leaving the remainder for system processes.
- **System reserve** — Leftover cores and RAM per node left unallocated to Spark for the OS and daemons.
- **Multi-tenant cluster** — A cluster shared by multiple teams, which is why the programmer, not Spark, chooses the hardware a job uses.

## Dependencies and Files
- **JAR (Java Archive)** — A packaged file of compiled JVM bytecode used as a dependency or application.
- **--jars** — Adds local JAR dependencies (e.g. a JDBC driver) to the driver and executors.
- **--packages** — Downloads Maven dependencies (e.g. `spark-avro`, `spark-xml`) at submit time.
- **--exclude-packages** — Excludes conflicting Maven dependencies.
- **--repositories** — Adds extra Maven repositories to search.
- **--py-files** — Adds Python `.py`, `.zip` or `.egg` dependencies.
- **--files** — Distributes files (e.g. config) to every executor's working directory.
- **--archives** — Distributes and extracts archives (e.g. a Python environment) on executors.
- **Maven** — Java dependency repository and tooling from which `--packages` pulls libraries.
- **JDBC driver** — Library that lets JVM code (including Spark) connect to a database such as PostgreSQL.
- **spark-avro** — External package required for Spark to read and write Avro.
- **spark-xml** — External package required for Spark to read and write XML.

## Spark Configuration Properties
- **spark.sql.shuffle.partitions** — Sets the number of partitions used after a shuffle.
- **spark.sql.adaptive.enabled** — Turns Adaptive Query Execution on.
- **spark.executor.memoryOverhead** — Extra non-heap memory allocated per executor.
- **spark.dynamicAllocation.enabled** — Lets Spark add and remove executors based on workload.
- **spark.kubernetes.*** — Family of properties through which Kubernetes deployment settings are supplied via `--conf`.

## Cluster-Manager-Specific Arguments
- **Cluster manager** — The system (YARN, Spark Standalone, Kubernetes) that allocates resources and distributes work to executors.
- **YARN (Yet Another Resource Negotiator)** — Hadoop's cluster manager, a common `--master` target.
- **--queue** — YARN queue to submit the job into.
- **--principal** — Kerberos principal for secured YARN clusters.
- **--keytab** — Kerberos keytab file for secured YARN clusters.
- **Kerberos** — Network authentication protocol used to secure Hadoop clusters.
- **Spark Standalone** — Spark's own built-in cluster manager, targeted with `--master spark://host:7077`.
- **--supervise** — Standalone-only flag that restarts the driver automatically if it fails.
- **Kubernetes** — Container orchestrator usable as a Spark cluster manager, configured mostly through `--conf`.
- **Mesos** — An older cluster manager supported by Spark.
- **Application arguments** — Anything after the application file/JAR in `spark-submit`, passed to the application rather than to Spark.

## Deploy Modes
- **Client deploy mode** — The driver runs on the machine where `spark-submit` was run; good for interactive work, but the job dies if that machine disconnects.
- **Cluster deploy mode** — The driver runs on a node inside the cluster; preferred for production jobs.

## Spark Architecture and Execution Flow
- **Master-slave architecture** — Classic name for one controlling master node directing multiple worker nodes; now replaced by terms like driver/executor.
- **Master node** — In classic terminology, the node the developer works through that controls the other nodes.
- **Spark architecture (5 steps)** — Driver spins up; optimizer builds logical and physical plans; cluster manager distributes partitioned data to executors; executors process their share; results return to the driver and are written out.
- **Optimizer** — Component that determines before execution the most efficient way to perform the job.
- **Catalyst optimizer** — Spark SQL's modern, preferred optimizer, which produces the logical and physical plans.
- **Default optimizer** — Older optimizer path generally superseded by Catalyst.
- **Logical plan** — A high-level, formal plan describing the operations needed to turn input data into output data.
- **Physical plan** — The formal description of the low-level execution steps the computer takes to implement the logical plan.
- **Cost-based optimization (CBO)** — Generating multiple candidate plans and choosing the cheapest using data statistics and cluster knowledge.
- **Predicate** — Anything that removes data from the dataset, such as a SQL `WHERE` clause or Spark `filter`.
- **Predicate pushdown** — Applying predicate operations as early as possible so unneeded rows are removed at the start of the job.
- **Predicate logic** — Branch of formal logic, formalized by Frege, that is an intellectual ancestor of logic programming and SQL.
- **Prolog** — A logic programming language, cited as an ancestor-line of SQL.
- **DAG (Directed Acyclic Graph)** — A graph-theory structure of nodes and directed edges with no loops; Spark uses it for its chain of transformations and Airflow for task pipelines.
- **Graph node** — A circle in a graph, representing one step.
- **Edge** — A line connecting two nodes in a graph.
- **Directed** — Each edge has a direction, flowing from one node to the next.
- **Acyclic** — Once you move from one stage to the next, you can never go back to a previous stage.
- **Apache Airflow** — Workflow orchestration tool that also models pipelines as DAGs.
- **Lineage** — The recorded chain of transformations from one RDD/DataFrame to the next.

## Adaptive Query Execution
- **AQE (Adaptive Query Execution)** — Spark 3.0's big feature that re-plans logical and physical plans after each stage, using observed executor performance, to improve efficiency during execution.
- **Dynamic join strategy switching** — AQE capability that changes join strategy mid-query, e.g. to a broadcast join when a table proves small.
- **Partition coalescing (AQE)** — AQE capability that merges unnecessarily small shuffle partitions.
- **Skew mitigation (AQE)** — AQE capability that detects and splits skewed partitions.

## Jobs, Stages and Tasks
- **Application (App)** — The whole program submitted by one `spark-submit`, which can contain multiple jobs.
- **Job** — A unit of work within an app, triggered by an action.
- **Stage** — A group of lazily evaluated tasks: zero or more narrow transformations followed by at least one wide transformation or action.
- **Task** — An individual data processing operation Spark performs; one task per partition within a stage.
- **Partition** — A chunk of a distributed dataset processed by one task.

## Transformations and Actions
- **Transformation** — A lazy operation that returns a new DataFrame or RDD.
- **Narrow transformation** — An operation that does NOT shuffle the data; each output partition depends on typically one input partition.
- **Wide transformation** — An operation that shuffles the data; output partitions depend on multiple input partitions.
- **Action** — An operation that returns something other than a new DataFrame or RDD and triggers execution of the lazy DAG.
- **Shuffle** — Redistributing data across partitions and nodes over the network; Spark's most expensive operation.
- **Exchange** — The physical-plan operator representing a shuffle.
- **map()** — Narrow RDD transformation producing one output element per input element.
- **flatMap()** — Narrow RDD transformation producing zero or many outputs per input.
- **mapPartitions()** — Narrow RDD transformation applied to an entire partition at once.
- **filter() / where()** — Narrow transformation removing rows that don't meet a condition.
- **select()** — Narrow DataFrame transformation choosing (projecting) columns.
- **withColumn()** — Usually narrow DataFrame transformation adding or replacing a column; window expressions can make it shuffle.
- **union()** — Narrow transformation combining datasets without deduplication.
- **unionByName()** — Union that matches columns by name.
- **cast()** — Column expression converting a data type.
- **when() / otherwise()** — Column expressions for conditional values.
- **mapInPandas()** — DataFrame transformation applying Pandas processing by batches/partitions.
- **reduceByKey()** — Wide RDD transformation aggregating values per key, with map-side combining.
- **groupByKey()** — Wide RDD transformation grouping values per key; usually more expensive than `reduceByKey()`.
- **groupBy()** — Wide DataFrame transformation grouping rows by key for aggregation.
- **cube() / rollup()** — Wide DataFrame multidimensional and hierarchical aggregations.
- **pivot()** — Wide DataFrame operation turning grouped values into columns.
- **sort() / orderBy()** — Wide DataFrame operations producing a global ordering.
- **repartitionByRange()** — Wide DataFrame operation redistributing data by value ranges.
- **partitionBy()** — Wide pair-RDD operation redistributing data according to a partitioner.
- **distinct() / dropDuplicates()** — Wide operations removing duplicates across partitions.
- **crossJoin()** — Cartesian-product join; expensive.
- **countByKey()** — An action, not a transformation, that counts each key.
- **show()** — DataFrame action displaying rows.
- **count()** — Action returning the number of rows or elements.
- **take(n)** — Action retrieving the first n rows or elements.
- **Write operations** — `df.write...` calls (parquet, csv, saveAsTable, jdbc) are effectively actions because they execute the DAG.
- **df.explain()** — Prints the physical plan so you can see whether Spark inserted an Exchange and which join strategy it chose.
- **Narrow vs. wide mental model** — Ask whether Spark needs records from other partitions to compute a result; if yes, it shuffles and is wide.

## Partitioning Operations
- **coalesce()** — Reduces partition count by combining partitions already on the same node; only decreases, no guarantee of equal sizes, usually narrow.
- **repartition()** — Performs a coalesce, then shuffles and divides data into the specified number of even partitions; can increase or decrease; wide.
- **Repartition data safety** — Repartitioning only changes how data is divided, so no backup is needed and no data is lost.

## Joins
- **Sort-merge join** — Join strategy that shuffles both tables by key and sorts them before merging; wide.
- **BroadcastHashJoin** — Join strategy that copies the small table to every executor, avoiding a shuffle.

## Window Functions
- **Window function** — Calculation over a group of related rows (via `Window.partitionBy().orderBy()`), usually requiring an exchange and sort.
- **rank() / dense_rank() / row_number()** — Window functions assigning positions within a window.
- **lag() / lead()** — Window functions reading a previous or next row's value.

## Lazy Evaluation
- **Lazy evaluation** — Operations are not performed until the data is shuffled from one stage to the next or an action is called.

## Data Skew and Salting
- **Data skew (skewness)** — One executor must do more work than the others, so the whole job is delayed by that trailing executor; caused by not partitioning data properly.
- **Salting** — Somewhat outdated skew fix: add a column of discrete values, `repartition()` on key plus salt, then drop the salt; largely replaced by AQE.
- **Salt column** — Temporary column of random discrete values used only to spread a heavy key across partitions.
- **rand()** — Spark function generating random numbers, used to create salt values.
- **Hive bucketing vs. salting** — Bucketing assigns rows via a cryptographic hash deterministically; salting uses random values with no hash.

## Caching, Persist and Broadcast
- **Caching** — Storing frequently used data in memory so it remains easily accessible during execution.
- **cache()** — Shorthand for `persist()` at the Memory Only level.
- **persist()** — Stores data at a chosen storage level (memory, disk or combinations); used when data is too big to cache in memory.
- **unpersist()** — Removes cached/persisted blocks.
- **Storage level** — A persist option: Memory Only, Disk Only, Memory and Disk, Memory and Disk Serialized, Memory Only Serialized.
- **StorageLevel.MEMORY_ONLY** — The persist level equivalent to `cache()`.
- **Serialized** — Converted into a string of zeros and ones (bytes); useful in streaming to reduce memory use.
- **Broadcast variable** — Logically a table cached in the memory of every node in the cluster.
- **broadcast()** — PySpark function marking a DataFrame to be broadcast.
- **Broadcast join** — Joins a large non-broadcast table to a small broadcast table so each node joins locally with no network requests; generally for tables of about 5 GB or less.

## Spark and HDFS Layout
- **Client** — The machine that submits the Spark application.
- **Spark Master** — The cluster manager component that allocates cores and memory to an application.
- **NameNode** — HDFS component tracking metadata such as block locations.
- **DataNode** — HDFS component storing the actual data blocks.
- **Replication factor 3 (RF 3)** — Each HDFS block is stored on three different DataNodes.
- **Data locality** — Running a task on the node that already holds its data block, enabled by co-locating Spark workers with DataNodes.

## The JVM
- **JVM (Java Virtual Machine)** — Runtime that gives write-once-run-anywhere capability by executing code through a combination of compilation and interpretation.
- **Write once, run anywhere** — The same compiled code runs on any OS or processor that has a JVM.
- **javac** — The Java compiler, which compiles source code to Java Bytecode rather than machine code.
- **Java Bytecode** — Machine-code-like instructions (`.class` files) that target the JVM instead of a real CPU.
- **Machine code** — Native instructions for a specific processor, which C/C++ compile directly to.
- **JIT (Just-In-Time) compiler** — JVM component that compiles frequently run bytecode into native machine code at runtime.
- **Heap memory** — JVM memory region where objects are allocated and garbage collection operates.
- **Garbage collection (GC)** — The JVM's automatic freeing of unused heap memory, which can cause pauses.
- **On-heap memory** — Standard JVM heap memory used by executor tasks, managed by the GC.
- **Off-heap memory** — Memory outside the JVM heap managed directly by Spark, avoiding GC overhead.
- **JVM languages** — Languages compatible with Java that use the JVM as their execution environment, e.g. Scala, Kotlin, Groovy, Clojure.
- **Scala** — Functional and object-oriented JVM language in which Spark itself is written.
- **PySpark** — Spark's Python API, which runs Python that talks to the JVM engine through an interop layer.
