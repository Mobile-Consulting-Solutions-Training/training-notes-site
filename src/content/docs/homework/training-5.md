---
title: "Training 5 Homework"
description: "Homework assignment for Training 5: Data Warehouse Concepts."
sidebar:
  order: 5
---

:::note
The assignment prompt as given in class. Related notes: [Training 5](/training-notes-site/notes/training-5/).
:::

### Data Warehousing Homework — 10 Questions

Assume the PostgreSQL warehouse and **Bronze → Silver → Gold** pipeline created during class are available. Complete each question using SQL, Python/Pandas, or a written answer as specified.

1. **Facts and Dimensions**
   In 2–4 sentences, explain the difference between a **fact table** and a **dimension table**. Then identify one fact table and two dimension tables from the warehouse we created in class.

2. **Grain**
   Examine `gold.fact_sales`. Describe the **grain** of this table. What does one row represent? Why is it important to decide the grain of a fact table before designing it?

3. **Querying a Star Schema**
   Write a SQL query using:

   * `gold.fact_sales`
   * `gold.dim_product`
   * `gold.dim_date`

   Return the **total sales amount by product category and year**, ordered by year and total sales descending.

4. **Surrogate Keys**
   Explain what a **surrogate key** is and how it differs from a natural/business key such as `product_number`. Give one reason a data warehouse might use a surrogate key even when the source system already provides a unique identifier.

5. **SCD Type 1**
   Suppose a product in `dim_product` has the category:

   ```text
   Electronics
   ```

   but the business determines that it should actually be:

   ```text
   Computer Electronics
   ```

   Explain how this change would be handled using **Slowly Changing Dimension Type 1 (SCD1)**. What happens to the old value?

6. **SCD Type 2**
   Suppose a customer moves from **New York to Miami**, and the business wants reports from previous years to continue showing the customer as living in New York at that time. Explain how **SCD2** could represent this change. What additional columns would you add to `dim_customer`?

7. **Star vs. Snowflake Schema**
   Explain the difference between a **star schema** and a **snowflake schema**. Then choose one of our existing dimensions and describe how it could be normalized into multiple tables to create a more snowflake-like design.

8. **Medallion Architecture**
   Explain the purpose of each of these layers:

   ```text
   Bronze
   Silver
   Gold
   ```

   For each layer, give one example of what happened to data in that layer during our PostgreSQL/Pandas exercise.

9. **Bronze → Silver with Pandas**
   The Bronze data contains the following records:

   ```text
   transaction_id | category      | quantity | unit_price
   T101           | electronics   | 2        | 50.00
   T102           | ELECTRONICS   | 3        | 75.00
   T103           | Furniture     | -2       | 200.00
   T104           | electronics   | 1        | INVALID
   ```

   Write Pandas code that:

   * standardizes `category`
   * converts `quantity` and `unit_price` to numeric values
   * converts invalid values to `NaN`
   * removes rows where quantity or price is invalid
   * removes rows where quantity is 0 or negative
   * creates `sales_amount = quantity * unit_price`

10. **Silver → Gold Warehouse Load**
    A new Silver batch contains:

    ```text
    transaction_id = T500
    transaction_date = 2026-09-15
    product = Laptop
    category = Electronics
    quantity = 2
    unit_price = 900.00
    sales_amount = 1800.00
    ```

    Describe the steps an ETL process should perform to load this record into the existing **Gold star schema**. Your answer should discuss:

    * looking up or adding the product dimension member
    * looking up the appropriate date in `dim_date`
    * resolving the appropriate keys
    * constructing the `fact_sales` record
    * what to do if information required by the Gold schema is missing from the incoming batch

These questions progress from the core dimensional-modeling concepts into the **actual Medallion pipeline the students built**, so #9 and #10 require them to apply the architecture rather than just define it.
