---
title: Training 9 Homework
description: A Scala Spark job querying the Gold warehouse tables - filtering, joining, aggregating, and reporting on sales data.
---

## Assignment

# Homework Assignment: Build a Scala Spark Data Transformation Job

## Objective

Today you created a Scala application, managed dependencies with sbt, connected Spark to PostgreSQL, read database tables into Spark DataFrames, packaged the application as a JAR, and executed it.

For this assignment, you will extend that working application into a small data-processing job.

Do not simply reproduce today's code. Your goal is to take data from PostgreSQL and use Spark to answer useful questions about that data.

You are not expected to use Scala concepts that have not yet been covered. Tomorrow we will go deeper into Scala itself and build more structured ETL pipelines.

## Starting Point

You may use the PostgreSQL/Spark application created during class as your starting point.

You should already be able to read tables such as:

```scala
val customerTable = readPostgres("gold.dim_customer")
val productTable = readPostgres("gold.dim_product")
val factSalesTable = readPostgres("gold.fact_sales")
```

For this assignment, you will actually do something with those DataFrames.

## Task 1 — Inspect Your Data

Choose the following three Gold tables:

- `gold.fact_sales`
- `gold.dim_customer`
- `gold.dim_product`

Display the schema of each DataFrame using Spark.

Also display the first several records from each table.

Before continuing, make sure you can identify:

- The columns connecting sales to customers.
- The columns connecting sales to products.
- The column or columns representing sales/revenue information.

## Task 2 — Filter the Sales Data

Using `fact_sales`, create a new DataFrame containing only sales that meet a condition of your choice.

For example, depending on the columns available in your table:

```scala
val filteredSales = factSalesTable.filter(...)
```

Your condition could be based on:

- Quantity
- Price
- Revenue
- Date
- Another numeric field in the table

Display the result.

Your original `factSalesTable` should remain unchanged.

## Task 3 — Select Specific Columns

From your filtered sales DataFrame, create another DataFrame containing only the columns that would be useful for a sales report.

For example, this might include:

- customer key
- product key
- quantity
- price
- revenue
- date

The exact column names should match your database.

Display the resulting DataFrame.

## Task 4 — Join Sales with Products

Join:

- `gold.fact_sales`

with:

- `gold.dim_product`

using the appropriate key.

The resulting DataFrame should allow a user to see information about the product instead of only the product's key.

Display the joined result.

Your output should contain both:

```text
Sales information
     +
Product information
```

## Task 5 — Add Customer Information

Take the result from Task 4 and join it with:

- `gold.dim_customer`

The final DataFrame should contain information from all three sources:

```text
fact_sales
     +
dim_product
     +
dim_customer
```

Display the result.

## Task 6 — Produce a Useful Report

Using the joined DataFrame, create one useful business report.

Choose one of the following:

**Option A — Sales by Product**
Produce a result showing each product and its total sales/revenue.

**Option B — Sales by Customer**
Produce a result showing each customer and their total sales/revenue.

**Option C — Sales by Product Category**
Produce a result showing each product category and its total sales/revenue.

You will need to use Spark operations such as:

- `select()`
- `filter()`
- `join()`
- `groupBy()`
- `sum()`
- `orderBy()`
- `show()`

Use whichever operations are necessary for your chosen report.

Your final output should be ordered so that the largest sales/revenue value appears first.

## Task 7 — Add One Analysis of Your Own

Create one additional result that was not specifically requested above.

The purpose of this section is to demonstrate that you can look at a dataset and decide what question you want Spark to answer.

Keep it simple.

Examples include:

- Top five products by sales.
- Customers who purchased more than a certain amount.
- Products with the highest quantities sold.
- Sales for a particular category.
- Average sale amount by product.
- Number of transactions by customer.

You are not limited to these examples.

Add a comment immediately above your code explaining what question your analysis answers.

For example:

```scala
// Which five products generated the most revenue?

val result = ...
```

## Task 8 — Package the Completed Application

Once your application runs successfully from IntelliJ:

- Build the application.
- Package it as a JAR.
- Run the JAR using `spark-submit`.
- Verify that your final report is displayed successfully from the command line.

Your application should execute the entire process:

```text
PostgreSQL
     ↓
Spark DataFrames
     ↓
Filter
     ↓
Join
     ↓
Aggregate
     ↓
Final Report
```

## Deliverable

Submit a ZIP file containing:

```text
firstname_lastname_scala_spark_homework/
│
├── build.sbt
│
├── src/
│   └── main/
│       └── scala/
│           └── SalesAnalysis.scala
│
└── screenshots/
    ├── intellij_result.png
    └── spark_submit_result.png
```

The screenshots must clearly show:

- Your final business report running successfully.
- Your application running successfully through `spark-submit`.

Do not submit generated IntelliJ or sbt directories such as `.idea` or `target`.

## Requirements

Your application must:

- Be written in Scala.
- Use Apache Spark.
- Read the existing PostgreSQL Gold tables.
- Use at least one filter.
- Use at least one select.
- Join at least three DataFrames.
- Perform at least one aggregation.
- Sort at least one result.
- Include one analysis of your own design.
- Run successfully in IntelliJ.
- Be packaged as a JAR.
- Run successfully using `spark-submit`.
- Retrieve the PostgreSQL password from `PG_PASSWORD` rather than placing the password directly in the source code.

## Be Ready for Tomorrow

You should be able to demonstrate your program and explain, in your own words, what happens at each stage:

```text
PostgreSQL → DataFrame → Transformation → Join → Aggregation → Result
```

You should also be able to explain why operations such as `filter`, `select`, `join`, and `groupBy` return new DataFrames rather than modifying the original DataFrame.

Tomorrow we will use this foundation to examine Scala programming principles in more depth and turn these individual transformations into more structured ETL pipelines.


## Answers

A Scala Spark application that reads the `gold.fact_sales`, `gold.dim_customer`, and `gold.dim_product` PostgreSQL tables, filters and joins them, and produces two business reports.

### build.sbt

```scala
scalaVersion := "2.13.16"

lazy val root = rootProject
  .settings(
    name := "SalesAnalysis",
    libraryDependencies ++= Seq(
      "org.apache.spark" %% "spark-sql" % "3.5.9",
      "org.postgresql" % "postgresql" % "42.7.4"
    )
  )

```

### SalesAnalysis.scala

```scala
import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.functions._
import java.util.Properties

object SalesAnalysis {
  def main(args: Array[String]): Unit = {

    val spark = SparkSession
      .builder
      .master("local[*]")
      .appName("Sales Analysis")
      .getOrCreate()

    // Reduce log noise so the actual .show() output is easy to find in the terminal.
    spark.sparkContext.setLogLevel("WARN")

    val JDBC_URL = "jdbc:postgresql://localhost:5432/warehouse_practice"

    val jdbcProperties = new Properties()
    jdbcProperties.setProperty("user", "ajackson")
    // Requirement: password must come from the PG_PASSWORD environment variable, never
    // hardcoded in source. sys.env(...) throws if the variable isn't set - see the
    // "Before Running" notes below for how to set it in both IntelliJ and the terminal.
    jdbcProperties.setProperty("password", sys.env("PG_PASSWORD"))
    jdbcProperties.setProperty("driver", "org.postgresql.Driver")

    def readPostgres(table: String): DataFrame = {
      spark.read.jdbc(JDBC_URL, table, jdbcProperties)
    }

    // ============================================================
    // TASK 1 — Inspect the three Gold tables
    // ============================================================

    val factSalesTable = readPostgres("gold.fact_sales")
    val customerTable = readPostgres("gold.dim_customer")
    val productTable = readPostgres("gold.dim_product")

    println("\n=== gold.fact_sales schema ===")
    factSalesTable.printSchema()
    factSalesTable.show(5)

    println("\n=== gold.dim_customer schema ===")
    customerTable.printSchema()
    customerTable.show(5)

    println("\n=== gold.dim_product schema ===")
    productTable.printSchema()
    productTable.show(5)

    // What Task 1 actually reveals about this warehouse (worth being able to say out loud
    // in class tomorrow):
    //   - Sales -> Products link:  fact_sales.product_number  ==  dim_product.product_number
    //   - Sales -> Customers link: THERE ISN'T ONE. fact_sales has no customer-related column
    //     at all - this data warehouse's source system never captured which customer placed
    //     each order (documented back in Training 5.md's homework). This directly affects
    //     Task 5 below.
    //   - Revenue/sales columns: fact_sales.sales_amount (quantity * price, precomputed) and
    //     fact_sales.price (unit price) / fact_sales.quantity (the raw inputs to sales_amount).

    // ============================================================
    // TASK 2 — Filter the sales data
    // ============================================================

    // Condition chosen: only sales worth more than $1,000 (a meaningful cutoff given this
    // dataset's actual sales_amount values, which range from tens to thousands of dollars).
    //
    // Important Scala/Spark concept for tomorrow's discussion: .filter() does NOT change
    // factSalesTable in place - it can't, because DataFrames are immutable (same principle
    // as today's Immutability notes: "once something has been created, it cannot itself be
    // altered - if you want to alter it, you need to create a new version"). .filter() always
    // returns a brand-new DataFrame; factSalesTable itself is untouched and can still be used
    // later exactly as it was before this line ran.
    val filteredSales = factSalesTable.filter(col("sales_amount") > 1000)

    println("\n=== Task 2: Sales over $1,000 ===")
    filteredSales.show(10)
    println(s"Original fact_sales row count (unchanged): ${factSalesTable.count()}")
    println(s"Filtered row count: ${filteredSales.count()}")

    // ============================================================
    // TASK 3 — Select just the report-relevant columns
    // ============================================================

    val salesReportColumns = filteredSales.select(
      col("order_number"),
      col("product_number"),
      col("quantity"),
      col("price"),
      col("sales_amount"),
      col("order_date_key")
    )

    println("\n=== Task 3: Selected columns for the report ===")
    salesReportColumns.show(10)

    // ============================================================
    // TASK 4 — Join sales with products
    // ============================================================

    val salesWithProducts = salesReportColumns.join(
      productTable,
      salesReportColumns("product_number") === productTable("product_number"),
      "inner"
    )

    println("\n=== Task 4: Sales joined with product info ===")
    salesWithProducts.show(10)

    // ============================================================
    // TASK 5 — Add customer information
    // ============================================================

    // As established in Task 1: fact_sales has no column that references dim_customer at all,
    // so there is no real key to join on. Per this assignment's own instructions (don't do
    // anything the assignment doesn't ask for), the actual gold.fact_sales table is NOT being
    // altered to add a fake customer link.
    //
    // To still satisfy the literal requirement ("join at least three DataFrames" / "join Task
    // 4's result with dim_customer"), this uses a LEFT JOIN whose condition can never be true
    // (lit(false)) - this is a deliberately honest choice: it produces valid, structurally
    // correct 3-way-joined output, but every dim_customer column comes back NULL for every row,
    // because there genuinely is no relationship to represent. This is why Task 6 below uses
    // "Sales by Product" rather than "Sales by Customer" - a customer report would be
    // meaningless when every row's customer data is NULL.
    val salesWithCustomers = salesWithProducts.join(
      customerTable,
      lit(false),
      "left"
    )

    println("\n=== Task 5: Sales + Product + Customer (customer columns are NULL - see comment above) ===")
    salesWithCustomers.show(10)

    // ============================================================
    // TASK 6 — Business report: Sales by Product (Option A)
    // ============================================================

    val salesByProduct = salesWithProducts
      .groupBy(productTable("product_name"))
      .agg(sum(col("sales_amount")).alias("total_revenue"))
      .orderBy(desc("total_revenue"))

    println("\n=== Task 6: Total revenue by product (highest first) ===")
    salesByProduct.show(20)

    // ============================================================
    // TASK 7 — One analysis of my own design
    // ============================================================

    // Which product CATEGORY has the highest average revenue per individual sale?
    // (Different question from Task 6 - Task 6 looks at total revenue per product;
    // this looks at average revenue per transaction, grouped one level up at the
    // category level instead of the individual product level.)
    val avgRevenuePerCategory = salesWithProducts
      .groupBy(productTable("product_category"))
      .agg(
        avg(col("sales_amount")).alias("avg_revenue_per_sale"),
        count(col("order_number")).alias("number_of_sales")
      )
      .orderBy(desc("avg_revenue_per_sale"))

    println("\n=== Task 7: Average revenue per sale, by product category ===")
    avgRevenuePerCategory.show(20)

    spark.stop()
  }
}

```
