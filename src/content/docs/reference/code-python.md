---
title: "Code: Python and PySpark"
description: "Every Python, pandas and PySpark example from the notes, grouped by training day."
sidebar:
  order: 7
---

Every Python, pandas and PySpark example from the notes, grouped by training day. Each example is titled with the question it answers in the notes; the day heading links to the full notes for context. Use the copy button on any block.
**81 examples.**


Code marked "from the class demo (not exact)" in the notes was rewritten from the demo, so check names and paths before running it.

## Training 0: Data Engineering Fundamentals

[Open the Training 0 notes](/training-notes-site/notes/training-0/)

### How is error handling implemented in Python? (try/except)

```python
try:
    # Code that might fail
    process_data()

except SomeSpecificError as e:
    # Handle an expected failure
    handle_error(e)

except Exception as e:
    # Handle unexpected failures
    log_error(e)

finally:
    # Cleanup that must always happen
    cleanup()
```

```python
import pandas as pd

files = [
    "customers_2026_09_01.csv",
    "customers_2026_09_02.csv",
    "customers_2026_09_03.csv"
]

for file in files:
    try:
        print(f"Processing {file}...")

        # Extract
        df = pd.read_csv(file)

        # Validate
        required_columns = ["customer_id", "name", "email"]
        missing = [col for col in required_columns if col not in df.columns]

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Transform
        df["email"] = df["email"].str.lower()

        # Load
        df.to_parquet(file.replace(".csv", ".parquet"))

        print(f"Successfully processed {file}")

    except FileNotFoundError:
        # Handle a specific error
        print(f"ERROR: {file} does not exist")

    except pd.errors.ParserError as e:
        # Handle malformed CSV data
        print(f"ERROR: Could not parse {file}: {e}")

    except ValueError as e:
        # Handle our validation error
        print(f"VALIDATION ERROR in {file}: {e}")

    except Exception as e:
        # Catch unexpected errors so the batch can continue
        print(f"UNEXPECTED ERROR in {file}: {e}")

    finally:
        # Runs whether processing succeeds or fails
        print(f"Finished attempt for {file}\n")
```

## Training 1: Linux and Shell Scripting

[Open the Training 1 notes](/training-notes-site/notes/training-1/)

### How do I use regex in Python (the re module)?

```python
import re
text = "Customer number is 83921"
match = re.search(r"[0-9]+", text)
if match:
    print(match.group())   # 83921
```

```python
import re
text = """
customer_id=123
customer_id=456
customer_id=789
"""
ids = re.findall(r"customer_id=([0-9]+)", text)
print(ids)   # ['123', '456', '789']
```

```python
import re
text = "Customer SSN: 123-45-6789"
cleaned = re.sub(r"[0-9]{3}-[0-9]{2}-[0-9]{4}", "***-**-****", text)
print(cleaned)   # Customer SSN: ***-**-****
```

```python
re.findall(r"\d+", text)      # \d = digit
re.findall(r"\w+", text)      # \w = letters, digits, underscore (Unicode-aware)
re.split(r"\s+", text)        # \s = whitespace

re.split(r"\s+", "Spark     Kafka   Hadoop")
# ['Spark', 'Kafka', 'Hadoop']
```

```python
import re
email = "evan@example.com"
pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
if re.match(pattern, email):
    print("Looks like an email")
```

```python
import re
log = "2026-09-11 ERROR server=db01 message=connection_failed"
pattern = (
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<level>\w+) "
    r"server=(?P<server>\w+) "
    r"message=(?P<message>\w+)"
)
match = re.search(pattern, log)
if match:
    print(match.groupdict())
# {'date': '2026-09-11', 'level': 'ERROR', 'server': 'db01', 'message': 'connection_failed'}
```

## Training 2: Python and Pandas

[Open the Training 2 notes](/training-notes-site/notes/training-2/)

### What is threading in Python, and how does it relate to big data processing?

```python
import threading

def count_to(n):
    total = 0
    for i in range(n):
        total += i
    return total

# These two threads will NOT run truly in parallel on separate cores
# because of the GIL - they take turns, not run simultaneously
t1 = threading.Thread(target=count_to, args=(10_000_000,))
t2 = threading.Thread(target=count_to, args=(10_000_000,))
t1.start(); t2.start()
```

### Worked example: multithreading vs multiprocessing

```python
import threading
import multiprocessing
import time
import os


# -----------------------------
# Multithreading example
# -----------------------------
def thread_worker(name):
    print(
        f"Thread {name} started "
        f"| PID: {os.getpid()} "
        f"| Thread ID: {threading.get_ident()}"
    )

    time.sleep(2)

    print(f"Thread {name} finished")


def threading_demo():
    print("\n--- MULTITHREADING ---")

    threads = []

    for i in range(3):
        t = threading.Thread(
            target=thread_worker,
            args=(i,)
        )

        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()


# -----------------------------
# Multiprocessing example
# -----------------------------
def process_worker(name):
    print(
        f"Process {name} started "
        f"| PID: {os.getpid()}"
    )

    time.sleep(2)

    print(f"Process {name} finished")


def multiprocessing_demo():
    print("\n--- MULTIPROCESSING ---")

    processes = []

    for i in range(3):
        p = multiprocessing.Process(
            target=process_worker,
            args=(i,)
        )

        processes.append(p)
        p.start()

    # Wait for all processes to finish
    for p in processes:
        p.join()


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":

    print(f"Main program PID: {os.getpid()}")

    start = time.time()
    threading_demo()
    print(f"Threading took: {time.time() - start:.2f} seconds")

    start = time.time()
    multiprocessing_demo()
    print(f"Multiprocessing took: {time.time() - start:.2f} seconds")
```

### What are list comprehensions and generators, and why use a generator for big files?

```python
squares = [x * x for x in range(10)]            # list comprehension - all in memory
evens = {x for x in range(10) if x % 2 == 0}    # set comprehension
lookup = {r["id"]: r for r in rows}             # dict comprehension

def read_rows(path):                            # generator function
    with open(path) as f:
        for line in f:
            yield line.rstrip("\n").split(",")  # one row at a time

total = sum(1 for _ in read_rows("big.csv"))    # generator expression - constant memory
```

### apply vs vectorized operations, and shallow vs deep copy?

```python
import copy
a = [[1, 2], [3]]
b = copy.copy(a)        # shallow: b[0] is the same inner list as a[0]
c = copy.deepcopy(a)    # deep: fully independent
a[0].append(99)         # b sees the change, c does not
```

### How do you write a for loop and a while loop in Python?

```python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

for i in range(5):        # 0, 1, 2, 3, 4
    print(i)

for i, fruit in enumerate(fruits):   # get index + value together
    print(i, fruit)
```

```python
count = 0
while count < 5:
    print(count)
    count += 1

# Loop until a condition is met, with a way to break out early
while True:
    user_input = input("Type 'quit' to stop: ")
    if user_input == "quit":
        break
```

### How do you define a function in Python?

```python
def function_name(parameter1, parameter2):
    # function body
    result = parameter1 + parameter2
    return result

# calling it
answer = function_name(3, 4)
print(answer)   # 7
```

```python
def greet(name="World"):          # default parameter value
    return f"Hello, {name}!"

greet()          # "Hello, World!"
greet("Alex")    # "Hello, Alex!"

def add_all(*numbers):            # accepts any number of positional args
    return sum(numbers)

add_all(1, 2, 3, 4)   # 10

def describe(**kwargs):           # accepts any number of keyword args
    for key, value in kwargs.items():
        print(f"{key}: {value}")

describe(name="Alex", role="student")
```

### What are map, filter, and reduce in Python?

```python
from functools import reduce

numbers = [1, 2, 3, 4]
total = reduce(lambda acc, x: acc + x, numbers)
print(total)   # 10 (((1+2)+3)+4)
```

### Full worked example: map/filter/reduce on a realistic CSV-based ETL pipeline

```python
import csv
from io import StringIO
from functools import reduce

# ============================================================
# 1. RAW CSV DATA (100 employee rows: id, name, department,
#    salary, years_experience, active)
# ============================================================
csv_data = """employee_id,name,department,salary,years_experience,active
1,Alice Johnson,Engineering,92000,6,true
2,Bob Smith,Sales,68000,4,true
...
100,Zara Ford,Engineering,106000,9,true
"""

# ============================================================
# 2. EXTRACT: READ THE CSV
# ============================================================
reader = csv.DictReader(StringIO(csv_data))

# DictReader produces dictionaries, but everything is currently
# represented as strings.
raw_employees = list(reader)

print("Total records read:", len(raw_employees))

# ============================================================
# 3. TRANSFORM: CONVERT DATA TYPES USING map()
# ============================================================
def convert_employee(employee):
    return {
        "employee_id": int(employee["employee_id"]),
        "name": employee["name"],
        "department": employee["department"],
        "salary": float(employee["salary"]),
        "years_experience": int(employee["years_experience"]),
        "active": employee["active"].lower() == "true"
    }

employees = list(map(convert_employee, raw_employees))

print("\nFirst converted employee:")
print(employees[0])

# ============================================================
# 4. FILTER: FIND ACTIVE EMPLOYEES MAKING $70,000+
# ============================================================
def is_high_earning_active_employee(employee):
    return employee["active"] and employee["salary"] >= 70000

filtered_employees = list(
    filter(is_high_earning_active_employee, employees)
)

print("\nEmployees after filtering:")
print(len(filtered_employees))

# ============================================================
# 5. MAP: GIVE FILTERED EMPLOYEES A 5% RAISE
# ============================================================
def give_raise(employee):
    return {
        **employee,
        "old_salary": employee["salary"],
        "salary": round(employee["salary"] * 1.05, 2)
    }

employees_with_raise = list(
    map(give_raise, filtered_employees)
)

print("\nEmployees receiving raises:")
for employee in employees_with_raise[:10]:
    print(
        employee["name"],
        employee["department"],
        employee["old_salary"],
        "->",
        employee["salary"]
    )

# ============================================================
# 6. REDUCE: CALCULATE TOTAL PAYROLL
# ============================================================
total_payroll = reduce(
    lambda total, employee: total + employee["salary"],
    employees_with_raise,
    0
)

print("\nTotal payroll after raises:")
print(f"${total_payroll:,.2f}")

# ============================================================
# 7. REDUCE: CALCULATE PAYROLL BY DEPARTMENT
# ============================================================
def add_to_department(accumulator, employee):
    department = employee["department"]

    if department not in accumulator:
        accumulator[department] = 0

    accumulator[department] += employee["salary"]

    return accumulator

department_payroll = reduce(
    add_to_department,
    employees_with_raise,
    {}
)

print("\nPayroll by department:")
for department, payroll in department_payroll.items():
    print(f"{department:15} ${payroll:,.2f}")

# ============================================================
# 8. REDUCE: CALCULATE AVERAGE SALARY
# ============================================================
salary_total = reduce(
    lambda total, employee: total + employee["salary"],
    employees_with_raise,
    0
)

average_salary = salary_total / len(employees_with_raise)

print("\nAverage salary:")
print(f"${average_salary:,.2f}")

# ============================================================
# 9. SIMPLE PIPELINE VERSION
# ============================================================
# The same core transformation can be chained together.
pipeline_result = list(
    map(
        give_raise,
        filter(
            is_high_earning_active_employee,
            map(convert_employee, raw_employees)
        )
    )
)

print("\nPipeline produced:", len(pipeline_result), "records")
```

### Are True and False case-sensitive in Python?

```python
True    # correct - the boolean value
False   # correct - the boolean value

true    # NameError: name 'true' is not defined
false   # NameError: name 'false' is not defined
```

### How do if, elif, and else work in Python?

```python
age = 20

if age < 13:
    print("Child")
elif age < 20:
    print("Teenager")
else:
    print("Adult")
```

```python
score = 85
if score >= 60:
    print("Pass")
elif score >= 90:
    print("This never prints - score >= 60 already matched above")
```

### What is the default case for an if chain, and does Python have a switch statement?

```python
if age < 13:
    print("Child")
elif age < 20:
    print("Teenager")
else:
    print("Adult")   # the "default" - catches everything else
```

```python
def describe(day):
    match day:
        case "Mon" | "Tue" | "Wed" | "Thu" | "Fri":
            return "Weekday"
        case "Sat" | "Sun":
            return "Weekend"
        case _:                    # this is the "default" case
            return "Not a valid day"
```

### What is the equivalency (equality) operator in Python?

```python
5 == 5          # True
5 == 6          # False
"cat" == "cat"  # True
"cat" == "dog"  # False
```

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b   # True  - same values
a is b   # False - different list objects in memory
```

### Does Python have finally?

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Can't divide by zero!")
finally:
    print("This always runs.")
```

### Worked example: multiple except clauses, raise, and finally together

```python
try:
    x = 1/0
    raise ValueError("This is a custom error message.")
except ZeroDivisionError:
    print("You can't divide by zero!")
except ValueError as e:
    print("A value error occurred:", e)
except Exception as e:
    print("An error occurred:", e)
finally:
    print("This block always executes, regardless of whether an exception occurred or not.")

print("This line will not execute because of the exception above.")
print("This line will also not execute because of the exception above.")
print("This line will also not execute because of the exception above.")
```

### Worked example: the logging module in a small data-processing script

```python
import logging

# Configure the logging system
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def divide(a, b):
    logging.info("Attempting to divide %s by %s", a, b)

    try:
        result = a / b
        logging.debug("Calculation result: %s", result)
        return result

    except ZeroDivisionError:
        logging.error("Cannot divide by zero")
        return None


def process_data():
    logging.info("Starting data processing")

    numbers = [
        (10, 2),
        (20, 4),
        (30, 0),
        (40, 5)
    ]

    for a, b in numbers:
        result = divide(a, b)

        if result is None:
            logging.warning("Processing failed for %s / %s", a, b)
        else:
            logging.info("Successfully processed %s / %s", a, b)

    logging.info("Data processing complete")


if __name__ == "__main__":
    logging.debug("Program started")

    process_data()

    logging.debug("Program finished")
```

### How do I read and write files in Python?

```python
from pathlib import Path

with open("data.txt", "r") as f:        # "r" read, "w" overwrite, "a" append
    for line in f:                       # reads one line at a time - fine for huge files
        print(line.strip())

with open("out.txt", "w") as f:
    f.write("hello\n")

p = Path("data") / "sales.csv"          # pathlib builds paths safely on any OS
print(p.exists(), p.suffix, p.stem)
```

### How do I work with JSON and CSV files in Python and Pandas?

```python
import json, pandas as pd

with open("users.json") as f:
    users = json.load(f)                        # list of nested dicts
df = pd.json_normalize(users)                   # nested keys become columns
```

### Worked example: the same employee CSV pipeline, rewritten with Pandas

```python
import pandas as pd


# ============================================================
# 1. EXTRACT: READ CSV
# ============================================================

df = pd.read_csv("data.csv")

print("Total records read:", len(df))

print("\nFirst 5 employees:")
print(df.head())


# ============================================================
# 2. TRANSFORM: CONVERT DATA TYPES
# ============================================================

df["employee_id"] = df["employee_id"].astype(int)
df["salary"] = df["salary"].astype(float)
df["years_experience"] = df["years_experience"].astype(int)

# Depending on how pandas interpreted the CSV, active may already
# be boolean. Converting to string first makes this robust.
df["active"] = (
    df["active"]
    .astype(str)
    .str.lower()
    .eq("true")
)

print("\nData types:")
print(df.dtypes)


# ============================================================
# 3. FILTER: ACTIVE EMPLOYEES MAKING $70,000+
# ============================================================

filtered_df = df[
    (df["active"]) &
    (df["salary"] >= 70_000)
].copy()

print("\nEmployees after filtering:")
print(len(filtered_df))


# ============================================================
# 4. TRANSFORM: GIVE FILTERED EMPLOYEES A 5% RAISE
# ============================================================

filtered_df["old_salary"] = filtered_df["salary"]

filtered_df["salary"] = (
    filtered_df["salary"] * 1.05
).round(2)


print("\nEmployees receiving raises:")

print(
    filtered_df[
        ["name", "department", "old_salary", "salary"]
    ].head(10)
)


# ============================================================
# 5. AGGREGATE: TOTAL PAYROLL
# ============================================================

total_payroll = filtered_df["salary"].sum()

print("\nTotal payroll after raises:")
print(f"${total_payroll:,.2f}")


# ============================================================
# 6. AGGREGATE: PAYROLL BY DEPARTMENT
# ============================================================

department_payroll = (
    filtered_df
    .groupby("department")["salary"]
    .sum()
)

print("\nPayroll by department:")
print(department_payroll)


# ============================================================
# 7. AGGREGATE: AVERAGE SALARY
# ============================================================

average_salary = filtered_df["salary"].mean()

print("\nAverage salary:")
print(f"${average_salary:,.2f}")


# ============================================================
# 8. SAVE THE RESULT
# ============================================================

filtered_df.to_csv(
    "processed_employees.csv",
    index=False
)

print("\nResults saved to processed_employees.csv")
```

### How do I filter rows in a Pandas DataFrame?

```python
active_high = df[(df["active"]) & (df["salary"] >= 70_000)]
not_hr = df[~(df["department"] == "HR")]
some = df[df["department"].isin(["Sales", "Finance"])]
mid = df[df["salary"].between(60_000, 90_000)]
q = df.query("salary >= 70000 and active")
```

### pd.cut() - binning continuous values into labeled categories

```python
ages = pd.Series([5, 17, 40, 70])

groups = pd.cut(
    ages,
    bins=[0, 12, 19, 64, 120],
    labels=["Child", "Teen", "Adult", "Senior"]
)
# -> ["Child", "Teen", "Adult", "Senior"]
```

### .value_counts() - counting occurrences of each unique value

```python
data_frame["department"].value_counts()
# department
# Sales      20
# Finance    20
# ...
```

### .rank() - assigning each row a rank number within its group

```python
exercise5_df["salary_rank"] = (
    exercise5_df
    .groupby("department")["salary"]
    .rank(method="min", ascending=False)
    .astype(int)
)
```

### Named aggregation - multiple stats, multiple source columns, one .agg() call

```python
department_report = data_frame.groupby("department").agg(
    employee_count=("employee_id", "count"),
    average_salary=("salary", "mean"),
    highest_salary=("salary", "max"),
)
```

## Training 3: Git Workflow

[Open the Training 3 notes](/training-notes-site/notes/training-3/)

### How do you actually write a test in Python, for the Unit Test / Integration Test stages above?

```python
# test_math_utils.py
from math_utils import add

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(5, 0) == 5
```

```python
import unittest
from math_utils import add

class TestAdd(unittest.TestCase):
    def test_add_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -1), -2)

if __name__ == "__main__":
    unittest.main()
```

## Training 4: SQL Fundamentals & Data Warehousing

[Open the Training 4 notes](/training-notes-site/notes/training-4/)

### What does a minimal ETL pipeline into the warehouse look like?

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://student:password@localhost/sample_database"
)

orders = pd.read_sql("SELECT * FROM orders", engine)
order_details = pd.read_sql("SELECT * FROM orderdetails", engine)

sales = order_details.merge(orders, on="order_number")

sales["revenue"] = (
    sales["quantity_ordered"] *
    sales["price_each"]
)

sales.to_sql(
    "fact_sales",
    engine,
    schema="warehouse",
    if_exists="append",
    index=False
)
```

### What is a lakehouse, and where does Databricks fit?

```python
df = spark.read.format("delta").load("/sales")

result = (
    df.groupBy("country")
      .sum("revenue")
)
```

## Training 7: Spark Submit, Architecture & Execution

[Open the Training 7 notes](/training-notes-site/notes/training-7/)

### Window Functions

```python
window = (
    Window
    .partitionBy("department")
    .orderBy(col("salary").desc())
)

df.withColumn("rank", rank().over(window))
```

### Actions

```python
df = spark.read.parquet("employees")
filtered = df.filter(col("salary") > 100000)
selected = filtered.select("name", "salary")
# Nothing necessarily executes yet.

selected.show()  # <- this is the action that triggers execution
```

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

### What are the concrete steps for applying salting?

```python
from pyspark.sql.functions import rand, col, sum as _sum

N = 10
salted = df.withColumn("salt", (rand() * N).cast("int"))

# Stage 1: partial aggregate per (key, salt) - the hot key is now spread over N tasks
partial = salted.groupBy("customer_id", "salt").agg(_sum("amount").alias("partial_amount"))

# Stage 2: combine the partials per real key - only N rows per key left to shuffle
result = partial.groupBy("customer_id").agg(_sum("partial_amount").alias("total_amount"))
```

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

## Training 8: Spark Partitioning, Salting & Hive Setup

[Open the Training 8 notes](/training-notes-site/notes/training-8/)

### Can Spark's generic JDBC data source (df.write.format("jdbc")) write directly to Hive, the same way it writes to Postgres?

```python
spark = (SparkSession.builder
         .appName("etl")
         .config("hive.metastore.uris", "thrift://hive-metastore:9083")
         .enableHiveSupport()
         .getOrCreate())

spark.sql("SHOW TABLES IN silver").show()
df.write.mode("overwrite").format("parquet").saveAsTable("silver.sales")   # create/replace
df.write.insertInto("silver.sales")                                          # append to existing table
```

## Training 11: Postgres to Hive with Scala Spark

[Open the Training 11 notes](/training-notes-site/notes/training-11/)

### What does generate_sales.py do, and how does it feed the incremental exercise?

```python
import os
import random
import psycopg2
from datetime import date, timedelta

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "sample_database",
    "user": "evan",
    "password": os.environ["PG_PASSWORD"]
}

BATCH_SIZE = 5

# ---------------------------------------------------------
# Valid values for generated Bronze records
# ---------------------------------------------------------
FIRST_NAMES = [
    "Michael", "Sarah", "James", "Emily", "Daniel",
    "Jessica", "Robert", "Laura", "Kevin", "Amanda",
    "Brian", "Rachel", "Steven", "Nicole", "Andrew",
    "Michelle", "Jason", "Rebecca", "Thomas", "Jennifer"
]

LAST_NAMES = [
    "Johnson", "Williams", "Martinez", "Garcia", "Robinson",
    "Clark", "Lewis", "Walker", "Hall", "Allen",
    "Young", "King", "Wright", "Scott", "Green",
    "Baker", "Adams", "Nelson", "Carter", "Mitchell"
]

PRODUCTS = {
    "Laptop": ("Electronics", 1200.00),
    "Mouse": ("Electronics", 25.00),
    "Monitor": ("Electronics", 300.00),
    "Keyboard": ("Electronics", 75.00),
    "Desk": ("Furniture", 450.00),
    "Chair": ("Furniture", 125.00)
}

COUNTRIES = [
    "USA",
    "Canada"
]

def connect():
    return psycopg2.connect(**DB_CONFIG)

# ---------------------------------------------------------
# Find the largest existing T-number
# T001 -> 1
# T010 -> 10
# T125 -> 125
# Invalid IDs such as "12" are ignored.
# ---------------------------------------------------------
def get_next_transaction_id(cur):

    cur.execute("""
        SELECT COALESCE(
            MAX(
                CAST(
                    SUBSTRING(transaction_id FROM 2)
                    AS INTEGER
                )
            ),
            0
        )
        FROM bronze.sales
        WHERE transaction_id ~ '^T[0-9]+$';
    """)

    max_id = cur.fetchone()[0]

    return max_id + 1


# ---------------------------------------------------------
# Generate random customer
# ---------------------------------------------------------
def generate_customer():

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)

    return f"{first} {last}"


# ---------------------------------------------------------
# Generate random transaction date
# Generates a date within the last 30 days.
# ---------------------------------------------------------
def generate_date():

    days_ago = random.randint(0, 30)

    transaction_date = (
        date.today() - timedelta(days=days_ago)
    )

    return transaction_date.isoformat()


# ---------------------------------------------------------
# Generate one complete valid sales record
# ---------------------------------------------------------
def generate_sale(transaction_id):

    customer_name = generate_customer()

    product = random.choice(list(PRODUCTS.keys()))

    category, base_price = PRODUCTS[product]

    quantity = random.randint(1, 5)

    # Give prices a little realistic variation
    price_multiplier = random.uniform(0.90, 1.10)

    unit_price = round(
        base_price * price_multiplier,
        2
    )

    country = random.choice(COUNTRIES)

    return (
        transaction_id,
        generate_date(),
        customer_name,
        product,
        category,
        str(quantity),
        f"{unit_price:.2f}",
        country
    )


# ---------------------------------------------------------
# Generate and insert a batch
# ---------------------------------------------------------
def generate_batch():

    conn = connect()
    cur = conn.cursor()

    next_id = get_next_transaction_id(cur)

    print("\nGenerating batch...")
    print("-" * 80)

    sql = """
        INSERT INTO bronze.sales (
            transaction_id,
            transaction_date,
            customer_name,
            product,
            category,
            quantity,
            unit_price,
            country
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """

    generated_ids = []

    for i in range(BATCH_SIZE):

        numeric_id = next_id + i

        transaction_id = f"T{numeric_id:03d}"

        row = generate_sale(transaction_id)

        cur.execute(sql, row)

        generated_ids.append(transaction_id)

        print(
            f"{row[0]} | "
            f"{row[1]} | "
            f"{row[2]:20} | "
            f"{row[3]:10} | "
            f"{row[4]:12} | "
            f"qty={row[5]} | "
            f"${row[6]} | "
            f"{row[7]}"
        )

    conn.commit()

    print(
        f"\nSuccessfully inserted "
        f"{BATCH_SIZE} new transactions."
    )

    # -----------------------------------------------------
    # Verify exactly the rows we just inserted
    # -----------------------------------------------------

    cur.execute("""
        SELECT
            transaction_id,
            transaction_date,
            customer_name,
            product,
            category,
            quantity,
            unit_price,
            country
        FROM bronze.sales
        WHERE transaction_id = ANY(%s)
        ORDER BY
            CAST(
                SUBSTRING(transaction_id FROM 2)
                AS INTEGER
            );
    """, (generated_ids,))

    print("\nInserted records:")
    print("-" * 80)

    for row in cur.fetchall():
        print(row)

    cur.close()
    conn.close()


if __name__ == "__main__":
    generate_batch()
```

## Training 12: Streaming Data

[Open the Training 12 notes](/training-notes-site/notes/training-12/)

### What is Spark Structured Streaming?

```python
from pyspark.sql.functions import col, from_json

raw = (spark.readStream.format("kafka")
       .option("kafka.bootstrap.servers", "localhost:9092")
       .option("subscribe", "test-topic")
       .option("startingOffsets", "latest")
       .load())                                   # columns: key, value (binary), topic, partition, offset, timestamp

events = (raw.selectExpr("CAST(value AS STRING) AS json")
             .select(from_json(col("json"), schema).alias("data"))
             .select("data.*"))

query = (events.writeStream.format("console").outputMode("append")
         .option("checkpointLocation", "/tmp/chk/test-topic")   # offsets + state live here
         .start())
query.awaitTermination()
```

## Training 13: Open Table Formats and NoSQL

[Open the Training 13 notes](/training-notes-site/notes/training-13/)

### What is a Kafka message key, and how do you choose one?

```python
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    key_serializer=lambda k: k.encode("utf-8"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)
producer.send("weather", key=city, value=message)
```

### What does foreachBatch() do in Structured Streaming?

```python
def write_to_mongodb(batch_df, batch_id):
    print(f"Writing batch {batch_id} to MongoDB")
    batch_df.write.format("mongodb").mode("append") \
        .option("spark.mongodb.write.connection.uri", "mongodb://localhost:27017/") \
        .option("spark.mongodb.write.database", "streaming_demo") \
        .option("spark.mongodb.write.collection", "weather") \
        .save()

query = processed_df.writeStream.foreachBatch(write_to_mongodb) \
    .outputMode("append").trigger(processingTime="5 seconds") \
    .option("checkpointLocation", "/tmp/weather-mongodb-checkpoint").start()
```

## Training 14: Kafka Cluster Setup & Spark Streaming

[Open the Training 14 notes](/training-notes-site/notes/training-14/)

### What are the trade-offs between a file sink and a MongoDB sink?

```python
query = processed_df.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("path", "/tmp/weather-stream") \
    .option("checkpointLocation", "/tmp/weather-stream-checkpoint") \
    .trigger(processingTime="5 seconds") \
    .start()
```

### Parallel Demo: Spark vs. Flink on the Same Kafka Topic

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

### 1. Synthetic Market Data API (FastAPI)

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

### 3. Spark Consumer: market_consumer_spark.py

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

### The Producer: Pacing to a Target Rate

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

### The Flink Consumer: flink_market_consumer.py (first version)

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

### What are event time, windows and watermarks?

```python
from pyspark.sql.functions import window, avg

result = (events
    .withWatermark("event_time", "10 minutes")                       # accept data up to 10 min late
    .groupBy(window("event_time", "5 minutes"), "city")
    .agg(avg("temperature").alias("avg_temp")))

query = (result.writeStream
    .outputMode("append")                                            # each window written once, after it closes
    .format("parquet").option("path", "/tmp/weather-agg")
    .option("checkpointLocation", "/tmp/weather-agg-chk")
    .trigger(processingTime="1 minute")
    .start())
```

## Training 15: Cloud Platforms and Snowflake

[Open the Training 15 notes](/training-notes-site/notes/training-15/)

### What is Snowpark?

```python
from snowflake.snowpark.functions import col, sum as sum_

sales = session.table("gold.fact_sales")
result = (sales.filter(col("quantity") > 0)
               .group_by("product_id")
               .agg(sum_(col("quantity") * col("unit_price")).alias("revenue")))
result.show()   # executes now, inside Snowflake
```

## Training 18: AWS Cloud Fundamentals

[Open the Training 18 notes](/training-notes-site/notes/training-18/)

### What is AWS Lambda?

```python
import json

def lambda_handler(event, context):
    # event arrives as JSON (a Python dict); e.g. an S3 upload event
    bucket = event.get("bucket")
    key = event.get("key")
    ...
    return {"statusCode": 200, "body": json.dumps("done")}
```

### AWS Glue: Extra Points from Class

```python
import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext

sc = SparkContext()
glueContext = GlueContext(sc)          # GlueContext wraps a SparkContext
spark = glueContext.spark_session      # ...and gives back a normal SparkSession
job = Job(glueContext)

df = spark.read.option("header", "true").csv("s3://bucket/path/")   # regular Spark still works
```

## Training 19: AWS Batch Pipelines

[Open the Training 19 notes](/training-notes-site/notes/training-19/)

### What is EMR Serverless?

```python
import sys
from pyspark.sql import SparkSession, functions as F

src, dst = sys.argv[1], sys.argv[2]
spark = SparkSession.builder.appName("clean_sales").getOrCreate()

df = spark.read.option("header", True).csv(src)
clean = (df.dropDuplicates(["sale_id"])
           .withColumn("amount", F.col("amount").cast("decimal(10,2)"))
           .withColumn("sale_date", F.to_date("sale_date")))
clean.write.mode("overwrite").partitionBy("sale_date").parquet(dst)
```

### Deploy steps

```python
# app.py
import streamlit as st
import redshift_connector, pandas as pd, os

conn = redshift_connector.connect(
    host=os.environ["REDSHIFT_HOST"], database="dev",
    user=os.environ["REDSHIFT_USER"], password=os.environ["REDSHIFT_PASSWORD"],  # from Secrets Manager, never hard-coded
)
df = pd.read_sql("SELECT sale_date, SUM(amount) AS revenue FROM analytics.fact_sales GROUP BY 1 ORDER BY 1", conn)

st.title("Daily Sales")
st.line_chart(df, x="sale_date", y="revenue")
st.dataframe(df)
```

## Training 20: AWS Glue and Redshift

[Open the Training 20 notes](/training-notes-site/notes/training-20/)

### What did it take to create the Glue job?

```python
src = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": ["s3://<bucket>/bronze/citibike/station_status/"]},
    format="json",
    transformation_ctx="src",          # bookmark state is stored under this name
)
```

### What does Glue-specific code look like (Silver → Gold)?

```python
import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from pyspark.context import SparkContext

args = getResolvedOptions(sys.argv, ["JOB_NAME"])   # job parameters
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session                   # plain Spark still available
job = Job(glueContext)
job.init(args["JOB_NAME"], args)                    # needed for bookmarks

df = spark.read.parquet("s3://<bucket>/silver/...")  # ...normal Spark transforms...
dyf = DynamicFrame.fromDF(df, glueContext, "gold")

glueContext.write_dynamic_frame.from_jdbc_conf(      # load into Redshift via the Glue connection
    frame=dyf,
    catalog_connection="<glue-connection-name>",
    connection_options={"dbtable": "public.citibike_station_snapshot", "database": "dev"},
    redshift_tmp_dir="s3://<bucket>/glue-temp/",    # Glue stages files here, then Redshift COPYs them
)
job.commit()                                         # saves the bookmark
```

## Training 22: Warehouse Design and AWS Streaming

[Open the Training 22 notes](/training-notes-site/notes/training-22/)

### What are the producer and consumer options on the Kinesis console?

```python
import boto3
import json

kinesis = boto3.client("kinesis", region_name="us-east-2")

record = {"station_id": "123", "num_bikes_available": 8}

kinesis.put_record(
    StreamName="citibike-stream",
    Data=json.dumps(record).encode("utf-8"),
    PartitionKey=record["station_id"],   # decides which shard the record lands on
)
```

## Training 25: AI on the Pipeline

[Open the Training 25 notes](/training-notes-site/notes/training-25/)

### What does a Bedrock call with a system prompt look like?

```python
import boto3
client = boto3.client("bedrock-runtime", region_name="us-east-2")
response = client.converse(
    modelId=MODEL_ID,                                    # Nova Micro by default
    system=[{"text": SYSTEM_PROMPT}],                     # role, rules, output format
    messages=[{"role": "user",
               "content": [{"text": f"Schema:\n{schema}\n\nQuestion: {question}"}]}],
    inferenceConfig={"maxTokens": 500, "temperature": 0}, # deterministic SQL
)
sql = response["output"]["message"]["content"][0]["text"]
```

## Training 26: Kinesis Streaming Ingestion

[Open the Training 26 notes](/training-notes-site/notes/training-26/)

### How the code works

```python
STREAM_NAME = "citibike-station-stream"
STATION_STATUS_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
kinesis = boto3.client("kinesis", region_name="us-east-2")   # created once, reused on warm starts

def lambda_handler(event, context):
    # 1. Download the feed (User-Agent header, 15 s timeout)
    # 2. For each station, build a small record:
    #    station_id, num_bikes_available, num_docks_available, last_reported, ingested_at (UTC)
    #    -> {"Data": json bytes, "PartitionKey": station_id}
    # 3. Send in chunks of 500, retrying only the records that failed
    for start in range(0, len(records), 500):
        pending = records[start:start + 500]
        for attempt in range(5):
            result = kinesis.put_records(StreamName=STREAM_NAME, Records=pending)
            failed = [orig for orig, resp in zip(pending, result["Records"]) if "ErrorCode" in resp]
            published += len(pending) - len(failed)
            pending = failed
            if not pending:
                break
            time.sleep(min(2 ** attempt, 8))      # 1, 2, 4, 8, 8 seconds
        if pending:
            raise RuntimeError(f"Failed to publish {len(pending)} records")
    return {"statusCode": 200, "stations_received": len(stations), "records_published": published}
```

### Why not just run aws scheduler update-schedule --state DISABLED?

```python
session = boto3.Session(profile_name="company", region_name="us-east-2")
# Safety check: refuse to run against the wrong AWS account
if session.client("sts").get_caller_identity()["Account"] != "<account-id>":
    raise RuntimeError("Wrong AWS account")

scheduler = session.client("scheduler")
fields = ["Name", "GroupName", "ScheduleExpression", "ScheduleExpressionTimezone", "StartDate",
          "EndDate", "Description", "KmsKeyArn", "FlexibleTimeWindow", "Target", "ActionAfterCompletion"]

for name in names:
    schedule = scheduler.get_schedule(Name=name, GroupName="default")
    if schedule["State"] == "DISABLED":
        continue                                   # don't touch what was already off
    request = {f: schedule[f] for f in fields if f in schedule}
    request["State"] = "DISABLED"                  # the only change
    scheduler.update_schedule(**request)
# then get_schedule again for each name to verify
```

### What do a DAG, operators and TaskFlow look like?

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator

with DAG(
    dag_id="citibike_incremental",
    schedule="*/30 * * * *",                 # cron, same as EventBridge
    start_date=datetime(2026, 10, 1),
    catchup=False,                           # don't run every missed interval since start_date
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
) as dag:
    wait_for_bronze = S3KeySensor(
        task_id="wait_for_bronze",
        bucket_key="s3://<bucket>/bronze/citibike/station_status/*",
        wildcard_match=True,
        mode="reschedule",                   # free the worker slot between checks
    )
    bronze_to_silver = GlueJobOperator(task_id="bronze_to_silver",
        job_name="CitiBikeBronzeToSilverIncrementalV2",
        script_args={"--BATCH_ID": "{{ run_id }}"})          # templated: unique per run
    complete_batch = RedshiftDataOperator(task_id="complete_batch",
        workgroup_name="<workgroup>", database="dev",
        sql="CALL public.sp_complete_citibike_batch('{{ run_id }}', '{{ data_interval_end }}');")

    wait_for_bronze >> bronze_to_silver >> complete_batch
```

## Training 27: Getting into Azure

[Open the Training 27 notes](/training-notes-site/notes/training-27/)

### What was missing from the AI's Spark code, and why didn't it matter?

```python
from pyspark.sql import functions as F

# Plain PySpark would need this first; Databricks already provides `spark`:
# from pyspark.sql import SparkSession
# spark = SparkSession.builder.appName("demo").master("local[*]").getOrCreate()

data = [(1, "Ana", 1500.0), (2, "Ben", 800.0), (3, "Cy", 2400.0)]
df = spark.createDataFrame(data, ["customer_id", "name", "total_spent"])
display(df)

display(df.filter(F.col("total_spent") >= 1000))

display(df.withColumn("customer_tier",
        F.when(F.col("total_spent") >= 2000, "premium").otherwise("standard")))
```

## Training 28: ADF and Databricks Medallion

[Open the Training 28 notes](/training-notes-site/notes/training-28/)

### How did Evan test the connection and read the JSON?

```python
landing_path = "/Volumes/<catalog>/default/citibike_bronze_landing/"
display(dbutils.fs.ls(landing_path))

df = (spark.read
      .option("multiLine", "true")
      .json(landing_path + "station_information/<date>/<hour>/<file>.json"))
df.printSchema()
display(df.limit(10))
```

### What does "flatten" mean, and how did Evan do it?

```python
from pyspark.sql import functions as F

root = "/Volumes/<catalog>/default/citibike_bronze_landing/"
src = root + "station_status/"

raw = (spark.read
       .option("multiLine", "true")
       .option("recursiveFileLookup", "true")
       .json(src))

bronze_df = (raw
    .select(F.explode("data.stations").alias("station"),
            F.col("last_updated").alias("snapshot_epoch"),
            F.col("_metadata.file_path").alias("source_file"))
    .select("station.*", "snapshot_epoch", "source_file")
    .withColumn("ingested_at", F.current_timestamp()))

(bronze_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("<catalog>.bronze.station_status"))
```

### What did the Bronze → Silver job do?

```python
bronze = spark.table("<catalog>.bronze.station_status")

silver_df = (bronze
    .select(
        F.col("station_id").cast("string").alias("station_id"),
        F.col("num_bikes_available").cast("int").alias("num_bikes_available"),
        F.col("num_docks_available").cast("int").alias("num_docks_available"),
        F.col("snapshot_epoch").cast("long").alias("snapshot_epoch"),
        "source_file")
    .withColumn("snapshot_time", F.to_timestamp(F.from_unixtime("snapshot_epoch")))
    .filter(F.col("station_id").isNotNull())
    .filter(F.col("num_bikes_available") >= 0)
    .filter(F.col("num_docks_available") >= 0)
    .dropDuplicates(["station_id", "snapshot_epoch"]))

(silver_df.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("<catalog>.silver.station_history"))
```

### How was the Gold table built?

```python
from pyspark.sql import Window

silver = spark.table("<catalog>.silver.station_history")

w = (Window.partitionBy("station_id", "hour")
           .orderBy(F.col("snapshot_time").desc()))

latest_hourly = (silver
    .withColumn("hour", F.date_trunc("hour", "snapshot_time"))
    .withColumn("rn", F.row_number().over(w))
    .filter("rn = 1")
    .drop("rn"))

gold_df = (latest_hourly.groupBy("hour")
    .agg(F.countDistinct("station_id").alias("stations_reporting"),
         F.sum("num_bikes_available").alias("total_bikes_available"),
         F.sum("num_docks_available").alias("total_docks_available"),
         F.round(F.avg("num_bikes_available"), 2).alias("avg_bikes_per_station"))
    .orderBy("hour"))

(gold_df.write.format("delta").mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("<catalog>.gold.hourly_network_availability"))
```

## Training 29: Elasticsearch, ELK and Lakeflow

[Open the Training 29 notes](/training-notes-site/notes/training-29/)

### What is Databricks Auto Loader?

```python
from pyspark import pipelines as dp     # newer name; older code uses: import dlt
from pyspark.sql import functions as F

@dp.table                                # streaming table
def bronze_station_raw():
    return (spark.readStream.format("cloudFiles")       # = Auto Loader
            .option("cloudFiles.format", "json")
            .schema(station_schema)                      # explicit schema (see the fix below)
            .load(source_path)
            .withColumn("source_file", F.col("_metadata.file_path"))
            .withColumn("ingested_at", F.current_timestamp()))
```

## Training 30: Delta Lake, Auto Loader and MLflow

[Open the Training 30 notes](/training-notes-site/notes/training-30/)

### What did the LangChain demo show?

```python
# from the class demo (not exact)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{user_input}"),
])
chain = prompt | llm

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.get_json()["message"]
    try:
        response = chain.invoke({"user_input": user_input})
        return jsonify({"response": response.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### How did the Auto Loader demo go? (step by step)

```python
# from the class demo (not exact)
from pyspark.sql import functions as F

source_path     = "<landing folder with the Citi Bike JSON>"
checkpoint_path = "<checkpoint folder>/bronze_station_status"
target_table    = "<catalog>.<schema>.bronze_station_status"

bronze_stream = (
    spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("multiLine", "true")
        .schema(station_status_schema)          # the AI-generated nested schema
        .load(source_path)
        .withColumn("source_file", F.col("_metadata.file_path"))
        .withColumn("ingested_at", F.current_timestamp())
)

query = (
    bronze_stream.writeStream
        .format("delta")
        .option("checkpointLocation", checkpoint_path)
        .trigger(availableNow=True)
        .toTable(target_table)
)
query.awaitTermination()

spark.table(target_table).count()   # 1230, then 1231 after one new file
```

### How did the Job demo go? (step by step)

```python
# Gold notebook, from the class demo (not exact)
from pyspark.sql import functions as F
from pyspark.sql.window import Window

silver = spark.table("<catalog>.<schema>.station_status_silver")
hourly = silver.withColumn("snapshot_hour", F.date_trunc("hour", "snapshot_time"))

w = Window.partitionBy("station_id", "snapshot_hour").orderBy(F.col("snapshot_time").desc())

latest_per_station = (
    hourly.withColumn("rn", F.row_number().over(w))
          .filter(F.col("rn") == 1)            # dedup: latest snapshot per station per hour
)

gold = (
    latest_per_station.groupBy("snapshot_hour")
        .agg(
            F.countDistinct("station_id").alias("active_stations"),
            F.sum("num_bikes_available").alias("bikes_available"),
            F.sum("num_docks_available").alias("docks_available"),
            F.avg("num_bikes_available").alias("avg_bikes_per_station"),
        )
)

gold.write.mode("overwrite").saveAsTable("<catalog>.<schema>.station_hourly_gold")
```

### How did the Databricks MLflow demo go? (step by step)

```python
# from the class demo (not exact)
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from pyspark.sql import functions as F
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")

df = spark.table("<catalog>.<schema>.station_status_silver")
features_df = (
    df.select("station_id", "snapshot_time", "num_bikes_available")
      .filter(F.col("num_bikes_available").isNotNull())
      .withColumn("hour", F.hour("snapshot_time"))
      .withColumn("day_of_week", F.dayofweek("snapshot_time"))
)

pdf = features_df.orderBy("snapshot_time").limit(50000).toPandas()   # pandas, not a PDF file

cutoff = pdf["snapshot_time"].quantile(0.8)                           # time-based split
train_df, test_df = pdf[pdf.snapshot_time <= cutoff], pdf[pdf.snapshot_time > cutoff]
features, target = ["station_id", "hour", "day_of_week"], "num_bikes_available"
X_train, y_train = train_df[features], train_df[target]
X_test,  y_test  = test_df[features],  test_df[target]

mlflow.set_experiment("/Users/<your-user>/citibike_mlflow_class")

model = Pipeline([
    ("prep", ColumnTransformer(
        [("station", OneHotEncoder(handle_unknown="ignore"), ["station_id"])],
        remainder="passthrough")),
    ("rf", RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)),
])

with mlflow.start_run() as run:
    mlflow.log_params({"n_estimators": 50, "max_depth": 10})
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = mean_squared_error(y_test, preds) ** 0.5
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("rmse", rmse)
    signature = infer_signature(X_train, preds)
    info = mlflow.sklearn.log_model(model, "model", signature=signature)
    print(run.info.run_id, mae, rmse, info.model_uri)
```

## Training 31: Azure Synapse and Event Hubs

[Open the Training 31 notes](/training-notes-site/notes/training-31/)

### What did the Databricks notebook do?

```python
# written from the class demo (not exact). Field names match the Citi Bike GBFS feed.
from pyspark.sql import functions as F

bronze_path = "abfss://bronze@<storageaccount>.dfs.core.windows.net/<station_status_path>/"
silver_path = "abfss://bronze@<storageaccount>.dfs.core.windows.net/silver/station_status/"  # Evan's demo location

bronze = spark.read.json(bronze_path)
bronze.printSchema()                      # data -> stations -> element -> fields; last_updated, ttl, version

flat = (bronze
        .withColumn("station", F.explode("data.stations"))
        .select(
            F.col("station.station_id").cast("string").alias("station_id"),
            F.col("station.num_bikes_available").cast("int").alias("num_bikes_available"),
            F.col("station.num_docks_available").cast("int").alias("num_docks_available"),
            F.col("station.is_renting").cast("int").alias("is_renting"),
            F.col("station.is_returning").cast("int").alias("is_returning"),
            F.to_timestamp(F.from_unixtime("station.last_reported")).alias("last_reported"),
            F.to_timestamp(F.from_unixtime("last_updated")).alias("snapshot_time"),
        ))

silver = (flat
          .filter(F.col("station_id").isNotNull())
          .filter(F.col("num_bikes_available") >= 0)
          .filter(F.col("num_docks_available") >= 0)
          .dropDuplicates(["station_id", "snapshot_time"])
          .withColumn("snapshot_date", F.to_date("snapshot_time")))

print("bronze station rows:", flat.count(), " silver rows:", silver.count())

silver.coalesce(4).write.mode("overwrite").parquet(silver_path)
spark.read.parquet(silver_path).display()
```
