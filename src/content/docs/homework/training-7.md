---
title: Training 7 Homework
description: Apache Spark execution and performance - architecture, spark-submit, transformations, lazy evaluation, AQE, data skew, caching, and broadcast joins.
---

## Assignment

# Homework Assignment: Apache Spark Execution and Performance

**Objective:** Demonstrate your understanding of Spark architecture, execution, transformations, optimization, resource configuration, and performance tuning.

**Instructions:** Complete all 10 questions. For coding questions, submit the requested PySpark code. Be prepared to explain your answers and demonstrate your code.

### 1. Spark Architecture — Verbal

Explain what happens from the time the following command is executed until the Spark application finishes:

```bash
spark-submit --master yarn \
  --deploy-mode cluster \
  --num-executors 8 \
  --executor-cores 4 \
  --executor-memory 6g \
  sales_job.py
```

Your explanation must include:

* Driver
* Cluster manager
* Worker nodes
* Executors
* Partitions
* Jobs, stages, and tasks
* Logical and physical execution plans

### 2. `spark-submit` — Command

Write a `spark-submit` command for `customer_etl.py` with the following requirements:

* YARN cluster
* Cluster deploy mode
* Application name `Customer ETL`
* 10 executors
* 4 cores per executor
* 8 GB executor memory
* 4 GB driver memory
* 200 shuffle partitions
* Include `postgresql.jar`
* Include `config.json` as an application file

Then briefly explain the purpose of each argument you used.

### 3. JVM and Spark Dependencies — Verbal

Explain the relationship between **Spark, Scala, Java, the JVM, Java bytecode, and JAR files**.

Then explain the difference between these two `spark-submit` options:

```text
--jars
--packages
```

Give an example of when a Spark application processing a format such as XML or Avro might require an additional dependency.

### 4. Narrow, Wide, or Action — Classification

Classify each of the following as a **narrow transformation**, **wide transformation**, or **action**. Explain why each operation belongs in that category.

```text
filter()
select()
map()
groupBy()
repartition()
coalesce()
distinct()
orderBy()
count()
collect()
show()
```

Also explain why `join()` cannot always be classified simply by looking at the method name.

### 5. Lazy Evaluation — Code and Verbal

Consider the following PySpark code:

```python
df = spark.read.parquet("sales")

result = (
    df.filter(col("amount") > 100)
      .select("customer_id", "amount")
      .withColumn("tax", col("amount") * 0.05)
)

result.show()
```

Answer the following:

* Which operations are transformations?
* Which operation is the action?
* At what point does Spark actually need to execute the transformations?
* Explain how **lazy evaluation** benefits Spark's optimizer.

Then modify the code by adding a `groupBy()` and aggregation that calculates total sales by customer.

### 6. Catalyst, AQE, and Execution Plans — Verbal

Explain the difference between:

* Logical plan
* Physical plan
* Catalyst optimizer
* Cost-Based Optimization (CBO)
* Adaptive Query Execution (AQE)

Then answer this scenario:

Spark initially chooses a **sort-merge join**, but after executing part of the query discovers that one side of the join is only 5 MB.

Explain how AQE could modify the remaining execution plan.

Does AQE remember statistics from previous executions of the same Spark job? Explain.

### 7. Data Skew — Code and Troubleshooting

You have a 2 TB transaction dataset partitioned by `customer_id`. Most customers have a few hundred transactions, but one customer has **300 million transactions**.

The Spark job runs quickly on almost every task, but one task takes 40 minutes longer than the others.

Answer the following:

* What problem is occurring?
* Why does the entire stage wait for the slow task?
* How would you identify this problem?
* How can AQE help?
* Describe how **salting** could be used if you needed to handle the skew manually.

Write a small PySpark example showing how you could repartition a DataFrame using a key.

### 8. `coalesce()` vs. `repartition()` — Code and Verbal

Assume:

```python
df = spark.read.parquet("transactions")
```

and `df` currently has 200 partitions.

Write code to:

1. Reduce it to 20 partitions using `coalesce()`.
2. Redistribute it into 20 partitions using `repartition()`.

Then explain:

* Which operation normally causes a shuffle?
* Which is generally cheaper?
* Which is more likely to produce evenly distributed partitions?
* When would you deliberately choose the more expensive operation?

### 9. Cache and Persist — Code and Design

You have a DataFrame that requires several expensive transformations:

```python
customers = spark.read.parquet("customers")
```

The resulting transformed DataFrame will subsequently be joined against **five different datasets**.

Write PySpark code that caches or persists the transformed customer DataFrame.

Then explain:

* Why caching could improve this application.
* What happens the first time the cached DataFrame is used.
* The relationship between `cache()` and `persist()`.
* Why you might choose a storage level involving disk instead of keeping everything only in memory.
* When the cached/persisted DataFrame should be unpersisted.

### 10. Broadcast Join and Predicate Pushdown — Code and Performance

You have two datasets:

```text
transactions = 4 TB
countries    = 5 MB
```

Each transaction contains a `country_code`.

Write PySpark code that:

1. Reads the two datasets.
2. Filters the transactions to keep only transactions where `amount > 1000`.
3. Joins the transactions to the countries dataset using `country_code`.
4. Explicitly broadcasts the countries DataFrame.
5. Displays the execution plan so you can verify Spark's join strategy.

Then explain:

* Why filtering the transactions as early as possible can improve performance.
* What **predicate pushdown** means.
* Why broadcasting the 5 MB dataset can be preferable to performing a normal shuffle join.
* What network activity a broadcast join is intended to avoid during the join.
* What you would look for in the physical execution plan to determine whether Spark actually used a broadcast join.

## Answers

# Apache Spark Execution and Performance Homework — Answers

*(Original prompt: `Homework - Training 7 (Assignment).md`)*

---

## 1. Spark Architecture — Verbal

When `spark-submit` is run with `--deploy-mode cluster`, the **Client** submits the application to the **Cluster Manager** (YARN, in this case). The Cluster Manager allocates resources — cores and memory, based on `--num-executors`, `--executor-cores`, and `--executor-memory` — and launches the **Driver** onto a node in the cluster (rather than running it locally, since this is cluster mode, not client mode).

Once running, the Driver reads `sales_job.py` and its configuration. Before touching any data, Spark's Catalyst optimizer builds a **logical plan** (what needs to happen to the data, in the abstract) and then a **physical plan** (the concrete execution strategy — which join algorithm, how data gets partitioned — chosen for the actual cluster it's running on).

The Cluster Manager then distributes the data's **partitions** across the cluster, and the **Executors** running on the **Worker nodes** pick up their assigned partitions to process.

Execution itself is broken into a hierarchy: the whole submitted program is the **Application**, which contains one or more **Jobs** (each triggered by an action), each Job is split into **Stages**, and each Stage is split into **Tasks** — one Task per partition, run in parallel across Executors. A new Stage boundary is forced specifically by a **wide transformation** (one that requires a shuffle — moving data across the network to redistribute it); narrow transformations chain together within the same Stage since no data movement is needed.

Once all Tasks in the final Stage complete, the Executors send their results back to the Driver — routed through the Cluster Manager — and the Driver reassembles the full output and writes/returns it, completing the application.

**In short: Driver → Cluster Manager → Worker Nodes → Executors → Tasks.** 

---

## 2. `spark-submit` — Command

```zsh
spark-submit --master yarn \
--deploy-mode cluster \
--name "Customer ETL" \
--num-executors 10 \
--executor-cores 4 \
--executor-memory 8g \
--driver-memory 4g \
--conf spark.sql.shuffle.partitions=200 \
--jars postgresql.jar \
--files config.json \
customer_etl.py
```

The above command has multiple elements that were not discussed on the answer to Q1 on this document like `--name, --conf, --jar, & --files`. These are additional arguments that can be passed to the spark-submit library and each are of course for specific needs. 

`--name` – this argument allows us to to set the actual application name, this helps with identification and monitoring for example UI and logs.
`--conf` – adds Spark configuration to the `spark-submit` command to set the spark configuration properties like shuffling partitions, behavior settings and more.
`--jars` – Spark jobs can depend on a third party libraries, this argument lets us attach these resources to our driver when launching the cluster so every executor has the needed resources to perform jobs, stages and task 
`--files` – This argument distributes additional files to executors, these files are generally needed to complete the job, stages, tasks properly 

---

## 3. JVM and Spark Dependencies — Verbal

Spark is written in Scala, which is a JVM language — a language that compiles down to Java bytecode instead of straight to machine code. The JVM is what actually interprets (and JIT-compiles) that bytecode into real machine code at runtime, which is what gives Java/Scala their "write once, run anywhere" portability. A JAR file is how compiled bytecode gets packaged up and distributed — e.g. `postgresql.jar` from Q2 isn't data, it's the compiled JDBC driver code Spark needs to be able to talk to a Postgres database.

| JVM Language | Notable for |
|:-:|---|
| Java | The original JVM language |
| Scala | Functional + object-oriented; the language Spark itself is written in |

**`--jars` vs `--packages`:** `--packages` pulls Maven dependencies automatically from a public online repository (you just give it a coordinate like `org.postgresql:postgresql:42.7.4`). `--jars` attaches a JAR file you already have locally on disk. Same end result (the dependency is available to the driver/executors) — different source (download-on-the-fly vs. a file you already have).

**XML/Avro example:** Spark's built-in DataFrame reader doesn't natively support XML or Avro the way it does CSV/JSON/Parquet — so processing either format requires an extra connector library, e.g. `--packages org.apache.spark:spark-avro_2.12:3.5.0` for Avro.

---

## 4. Narrow, Wide, or Action — Classification

| Operation | Classification | Why |
|---|---|---|
| `filter()` | Narrow | Each output partition only needs its own input partition - no data has to move between nodes |
| `select()` | Narrow | Just projects columns - doesn't need records from other partitions |
| `map()` | Narrow | One input element → one output element, entirely within its own partition |
| `groupBy()` | Wide | Rows sharing the same key can live in any partition, so they have to be shuffled together before aggregating |
| `repartition()` | Wide | Deliberately redistributes all the data across the cluster - always shuffles |
| `coalesce()` | Usually narrow | Merges partitions that are already on the same node - avoids a full shuffle (though it can't increase partition count) |
| `distinct()` | Wide | Spark has to check for duplicates across *all* partitions, not just within one, so records need to be redistributed |
| `orderBy()` | Wide | Global ordering requires redistributing records so partition ranges are correctly sorted relative to each other |
| `count()` | Action | Returns a number, not a new DataFrame/RDD - triggers execution of everything before it |
| `collect()` | Action | Returns the full result to the driver, not a new DataFrame/RDD |
| `show()` | Action | Triggers execution of enough of the plan to display rows - not a new DataFrame/RDD |

**Why `join()` can't be classified by method name alone:** whether a join shuffles depends on the *physical join strategy* Spark's Catalyst optimizer picks, not on the `join()` call itself. A **sort-merge join** shuffles both sides of the join across the network (wide). A **broadcast join** instead copies the smaller table to every executor and performs the join locally, with no shuffle of the large table at all. Which strategy gets used is a cost-based decision made at plan time (and can even change mid-query with AQE, see Q6) - so the only reliable way to know is to check `df.explain()`, not the method name.

**General rule for anything not on this list:** ask "does Spark need records from other partitions to calculate this result?" If no, it's narrow (`map`, `filter`, `select`, `withColumn`, etc.). If yes - meaning data has to be redistributed/shuffled - it's wide (`groupBy`, `distinct`, `repartition`, global sorts, most joins). If the operation produces an externally observable result instead of another DataFrame/RDD (`show`, `collect`, `count`, `take`, `write`), it's an action.

---

## 5. Lazy Evaluation — Code and Verbal

```python
df = spark.read.parquet("sales")

result = (
    df.filter(col("amount") > 100)
      .select("customer_id", "amount")
      .withColumn("tax", col("amount") * 0.05)
)

result.show()
```

- **Transformations:** `filter()`, `select()`, and `withColumn()` - all three are narrow transformations, and all three are lazy.
- **Action:** `show()` - this is the only call that isn't a transformation.
- **When Spark actually executes:** not until `show()` is called. Reading the parquet file and building up `filter → select → withColumn` only constructs the logical plan (the DAG) - no data is actually read or processed until the action triggers execution.
- **Why this benefits the optimizer:** because Spark waits until an action to run anything, Catalyst gets to see the *entire* chain of transformations at once before committing to an execution strategy - so it can optimize across the whole chain (e.g. predicate pushdown, moving the `amount > 100` filter as early as possible, ideally to the read itself) instead of being forced to execute and optimize each step eagerly and in isolation.

**Modified to add total sales by customer:**

```python
result = (
    df.filter(col("amount") > 100)
      .select("customer_id", "amount")
      .withColumn("tax", col("amount") * 0.05)
      .groupBy("customer_id")
      .agg(sum("amount").alias("total_sales"))
)

result.show()
```

---

## 6. Catalyst, AQE, and Execution Plans — Verbal

- **Logical plan:** a high-level, abstract description of *what* needs to happen to the data - independent of the actual cluster it'll run on.
- **Physical plan:** the concrete, low-level *how* - which join algorithm to use, how data gets partitioned - tailored to the real cluster.
- **Catalyst optimizer:** the component that actually builds and optimizes both plans - generates multiple candidate logical/physical plans and picks the one it estimates will be most efficient.
- **Cost-Based Optimization (CBO):** the part of Catalyst's process that uses statistics (data size estimates, persisted table/column stats) to estimate the cost of each candidate plan and choose the cheapest one - this happens up front, before execution starts.
- **Adaptive Query Execution (AQE):** a Spark 3.0 feature that re-optimizes the physical plan *during* execution - after each stage completes, it looks at real observed runtime statistics (not just pre-execution estimates) and can build new plans for the stages still to come.

**Scenario - sort-merge join, but one side turns out to be 5 MB:** AQE can dynamically switch the join strategy mid-query, from the originally planned sort-merge join to a **broadcast join**, once it observes the real size of that side is small enough to broadcast. This avoids the full shuffle a sort-merge join would have required for the rest of the query. (This join-strategy switch is one of three things AQE can do mid-execution - it can also coalesce unnecessarily small shuffle partitions, and detect and mitigate skewed partitions, not just adjust join strategy.)

**Does AQE remember statistics from previous runs of the same job?** No. AQE only reacts to runtime information gathered *during the current execution* - it has no memory of previous job runs. (Persisted table/column statistics *can* separately feed into Catalyst's CBO when building the *initial* plan, before AQE ever kicks in - but that's a distinct mechanism from AQE's own mid-job adaptation.)

---

## 7. Data Skew — Code and Troubleshooting

- **What problem is occurring:** data skew - the one customer with 300 million transactions ends up concentrated into a single oversized partition, so the task processing that partition has far more work to do than any other task.
- **Why the entire stage waits for the slow task:** a stage only completes once *all* of its tasks finish - Spark doesn't advance to the next stage early just because most tasks are done. The other executors finish quickly and sit idle, but the whole stage (and therefore the job) is bottlenecked by that one straggler task.
- **How to identify it:** the Spark UI's stage/task view - look for one (or a few) tasks with a dramatically longer duration than the rest. That lopsided task-duration pattern is the signature of skew.
- **How AQE can help:** AQE observes actual task execution times/partition sizes after each stage and can automatically detect and split an oversized/skewed partition for the next stage, without any manual intervention.
- **Manual fix - salting:** add a synthetic "salt" column with a small set of discrete random values, then repartition using the combination of the original key (`customer_id`) plus the salt value instead of `customer_id` alone. This spreads the heavy customer's rows across multiple partitions instead of dumping them all into one. Drop the salt column once partitioning is done - it has no meaning in the final data.

```python
# Simple repartition by key
df_repartitioned = df.repartition("customer_id")

# Salting approach for the skewed key
from pyspark.sql.functions import rand

salted = df.withColumn("salt", (rand() * 10).cast("int"))
salted = salted.repartition("customer_id", "salt")
result = salted.drop("salt")
```

---

## 8. `coalesce()` vs. `repartition()` — Code and Verbal

```python
df = spark.read.parquet("transactions")

# 1. Reduce to 20 partitions using coalesce()
df_coalesced = df.coalesce(20)

# 2. Redistribute into 20 partitions using repartition()
df_repartitioned = df.repartition(20)
```

- **Which normally causes a shuffle?** `repartition()` always shuffles. `coalesce()` usually avoids a full shuffle when reducing partition count, since it just merges partitions that are already on the same node.
- **Which is generally cheaper?** `coalesce()` - no network-wide data movement required.
- **Which is more likely to produce evenly distributed partitions?** `repartition()` - its full shuffle redivides the data evenly; `coalesce()` just groups whatever partitions already exist, so sizes can end up uneven.
- **When to deliberately choose the more expensive one:** when even partition sizes matter more than the upfront cost - e.g. to avoid data skew downstream (Q7), when partition count actually needs to *increase* (which `coalesce()` can't do), or when repartitioning by a specific key ahead of a join/`groupBy()`.

---

## 9. Cache and Persist — Code and Design

```python
customers = spark.read.parquet("customers")

customers_transformed = (
    customers
    .filter(col("status") == "active")
    .withColumn("full_name", concat(col("first_name"), lit(" "), col("last_name")))
    # ...other expensive transformations
)

customers_transformed.cache()

result1 = customers_transformed.join(dataset1, "customer_id")
result2 = customers_transformed.join(dataset2, "customer_id")
# ...joined against the remaining 3 datasets the same way

# once every join is done and customers_transformed is no longer needed:
customers_transformed.unpersist()
```

- **Why caching helps here:** without it, Spark's lazy evaluation would recompute the *entire* transformation chain from scratch every time `customers_transformed` is referenced by a new join - five times, once per dataset. Caching computes it once and keeps the result available for all five joins.
- **What happens the first time it's used:** `cache()` itself is lazy - nothing happens until the first action touches `customers_transformed`. That first use triggers the full transformation chain to actually run, and the result gets stored at the configured storage level (memory, by default) for every later access to reuse.
- **Relationship between `cache()` and `persist()`:** `persist()` is the general operation with multiple configurable storage levels (Memory Only, Disk Only, Memory and Disk, and serialized variants). `cache()` is just shorthand for `persist()` using the Memory Only level.
- **Why choose a disk-involving level instead of memory only:** if the transformed DataFrame is too large to comfortably fit in the cluster's available RAM, a Memory Only level either fails or forces repeated partial recomputation. A level like Memory and Disk lets it spill to local disk instead, trading some read speed for reliability on data too big for memory alone.
- **When to unpersist:** once it's no longer needed for any further actions in the job - here, right after all five joins are complete - so Spark can free up the memory/disk space it was holding.
- **Verifying it worked:** the **Storage tab in the Spark UI** shows every cached/persisted RDD or DataFrame, including its storage level and how much memory/disk it's actually using - a quick way to confirm `customers_transformed` really did get cached rather than just assuming it did.

---

## 10. Broadcast Join and Predicate Pushdown — Code and Performance

```python
transactions = spark.read.parquet("transactions_path")
countries = spark.read.parquet("countries_path")

filtered_transactions = transactions.filter(col("amount") > 1000)

from pyspark.sql.functions import broadcast

result = filtered_transactions.join(
    broadcast(countries), "country_code"
)

result.explain()
```

- **Why filtering transactions as early as possible helps:** cutting down to only `amount > 1000` rows *before* the join means far less data has to flow through the join and everything after it - fewer rows moving through the pipeline means less network, disk, and compute cost throughout.
- **What predicate pushdown means:** applying filter conditions (predicates) as early in execution as possible - ideally right at the data source read itself - so unneeded rows are discarded (or never read at all) before flowing through later, more expensive steps, instead of carrying the full dataset through everything and filtering only at the end.
- **Why broadcasting the 5 MB table is preferable to a normal shuffle join:** a sort-merge shuffle join would require redistributing *both* the 4 TB transactions table and the countries table across the network to bring matching keys together - extremely expensive at that scale. Broadcasting the small countries table instead copies it in full to every executor's memory once, so each executor can join its local slice of the 4 TB table against a full local copy of countries entirely locally.
- **What network activity a broadcast join avoids:** the shuffle of the *large* table - only the small table has to move across the network (once, to every node), instead of both tables being shuffled to bring matching keys together.
- **What to look for in the physical plan:** run `.explain()` and look for **`BroadcastHashJoin`** (or a `BroadcastExchange` step) in the output - that confirms Spark actually used a broadcast join rather than a `SortMergeJoin`.
- **Why broadcast this explicitly rather than relying on Spark's default behavior:** Spark can broadcast automatically, but only when a table's estimated size is under `spark.sql.autoBroadcastJoinThreshold` (10 MB by default). A 5 MB `countries` table sits close to that line, and the *estimate* Spark uses could be off - so calling `broadcast(countries)` explicitly guarantees the broadcast join happens regardless of what the automatic size estimate says.

