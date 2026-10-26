---
title: "Training 7 Homework"
description: "Homework assignment for Training 7: Spark Submit, Architecture & Execution."
sidebar:
  order: 7
---

:::note
The assignment prompt as given in class. Related notes: [Training 7](/training-notes-site/notes/training-7/).
:::

## Homework Assignment: Apache Spark Execution and Performance

**Objective:** Demonstrate your understanding of Spark architecture, execution, transformations, optimization, resource configuration, and performance tuning.

**Instructions:** Complete all 10 questions. For coding questions, submit the requested PySpark code. Be prepared to explain your answers and demonstrate your code.

#### 1. Spark Architecture — Verbal

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

#### 2. `spark-submit` — Command

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

#### 3. JVM and Spark Dependencies — Verbal

Explain the relationship between **Spark, Scala, Java, the JVM, Java bytecode, and JAR files**.

Then explain the difference between these two `spark-submit` options:

```text
--jars
--packages
```

Give an example of when a Spark application processing a format such as XML or Avro might require an additional dependency.

#### 4. Narrow, Wide, or Action — Classification

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

#### 5. Lazy Evaluation — Code and Verbal

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

#### 6. Catalyst, AQE, and Execution Plans — Verbal

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

#### 7. Data Skew — Code and Troubleshooting

You have a 2 TB transaction dataset partitioned by `customer_id`. Most customers have a few hundred transactions, but one customer has **300 million transactions**.

The Spark job runs quickly on almost every task, but one task takes 40 minutes longer than the others.

Answer the following:

* What problem is occurring?
* Why does the entire stage wait for the slow task?
* How would you identify this problem?
* How can AQE help?
* Describe how **salting** could be used if you needed to handle the skew manually.

Write a small PySpark example showing how you could repartition a DataFrame using a key.

#### 8. `coalesce()` vs. `repartition()` — Code and Verbal

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

#### 9. Cache and Persist — Code and Design

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

#### 10. Broadcast Join and Predicate Pushdown — Code and Performance

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
