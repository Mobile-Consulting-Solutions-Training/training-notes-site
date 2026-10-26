---
title: "Interview Questions: Programming and SQL"
description: "Interview questions with the class answer, a corrected expanded answer and a short answer to say out loud: General Programming, Python, Scala, Java, SQL, Git, Testing, General / Code Challenges."
sidebar:
  order: 13
---

Each question has three parts: **A. (Class answer)**, the answer from the class question bank as given; **Expanded**, a corrected and fuller explanation (starting with **Correction:** when the class answer was wrong); and **Say it out loud**, a short answer for the interview itself. Start with the [traps to unlearn](/training-notes-site/reference/interview-prep/#traps-to-unlearn).

## General Programming


**Q. What is object oriented programming**

**A. (Class answer)**

Object Oriented Programming (OOP) is a method for writing computer programs that models the world based on the concept of objects and them taking actions. The foundational concepts of OOP are the class, the object, and the method. Because we may want to create many objects that are similar to each other, we usually create them based on a class. The class, sometimes called a "blueprint" for objects, allows us... *(source cuts off here)*

**Expanded:** The teacher's answer is cut off in the source. A complete answer: OOP organizes code around **objects**, which bundle **state** (fields) with **behavior** (methods). A **class** is the blueprint and an object is one instance of it. The four principles:

| Principle | Meaning | Example |
|---|---|---|
| Encapsulation | Hide internal state behind methods | A `BankAccount` exposes `deposit()`, not a writable balance field |
| Abstraction | Expose what something does, not how | A `Storage` interface with `read()`/`write()` |
| Inheritance | A class reuses and extends a parent class | `S3Storage extends Storage` |
| Polymorphism | One interface, many implementations | Code calls `storage.write()` and gets S3 or local behavior |

**Say it out loud:** "OOP models a program as objects that combine data and the methods that act on it, created from classes. Its four pillars are encapsulation, abstraction, inheritance and polymorphism."

---

**Q. What is functional programming**

**A. (Class answer)** *(no answer given)*

**Expanded:** Functional programming builds programs from **functions** that take inputs and return outputs, avoiding shared mutable state. Core ideas: **pure functions**, **immutability** (create new values instead of changing old ones), **functions as values** (passed to and returned from other functions), and composition with `map`, `filter` and `reduce`. It matters for data engineering because Spark works this way: immutable DataFrames/RDDs, transformations that return new datasets, and functions shipped to executors. Without side effects, Spark can safely rerun a task on another node after a failure. Scala is a functional-first language, and Python supports the style.

See [Training 2 notes](/training-notes-site/notes/training-2/) ("Functional Tools (map, filter, reduce)") and [Training 10 notes](/training-notes-site/notes/training-10/).

**Say it out loud:** "Functional programming builds programs from pure functions and immutable data, passing functions around as values with things like `map` and `filter`. Spark is built on it, which is why its datasets are immutable and tasks can be safely retried."

---

**Q. What is a pure function**

**A. (Class answer)** *(no answer given)*

**Expanded:** A pure function (1) always returns the **same output for the same input**, and (2) has **no side effects**: it doesn't modify globals or its arguments, write files, print or call the network.

```python
def add_tax(price, rate):      # pure
    return price * (1 + rate)

total = 0
def add_to_total(x):           # impure: changes outside state
    global total
    total += x
```

Pure functions are easy to test, safe to run in parallel and safe to retry, which is exactly what Spark needs when it reruns a failed task.

**Say it out loud:** "A pure function always gives the same output for the same input and has no side effects, so it's easy to test and safe to run in parallel or retry."

---

**Q. What is a programmer API?**

**A. (Class answer)** *(no answer given)*

**Expanded:** An API (Application Programming Interface) is a defined contract for how one piece of software uses another: the functions, classes, endpoints, inputs and outputs it exposes, while hiding the implementation. Kinds you will meet:
- **Library APIs:** the functions you call in code, such as the PySpark DataFrame API or the pandas API.
- **Web APIs:** endpoints called over HTTP, such as a REST API that returns JSON.
- **Service/SDK APIs:** cloud APIs reached through an SDK such as boto3.

**Say it out loud:** "An API is the published interface a piece of software exposes so other code can use it without knowing its internals, whether that's a library like the Spark DataFrame API or a web API over HTTP."

---

**Q. What is a RESTful API?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A REST API is a web API that follows REST (Representational State Transfer) conventions: everything is a **resource** with a URL, and you act on it with standard **HTTP methods**. It is **stateless** (each request carries everything needed, such as an auth token), and responses are usually **JSON** with HTTP status codes.

| Method | Action | Example |
|---|---|---|
| GET | Read | `GET /stations/42` |
| POST | Create | `POST /stations` |
| PUT / PATCH | Replace / partly update | `PATCH /stations/42` |
| DELETE | Delete | `DELETE /stations/42` |

In data engineering, REST APIs are a common **source**: a Python job pages through an API and lands the JSON in S3 (the class's Citi Bike GBFS feed is an example). Watch for pagination, rate limits (HTTP 429) and retries.

See [Training 12 notes](/training-notes-site/notes/training-12/) ("HTTP Fundamentals") and [Training 19 notes](/training-notes-site/notes/training-19/) ("Class Project Data Source: Citi Bike GBFS Feed").

**Say it out loud:** "A REST API exposes resources at URLs that you work with through HTTP methods like GET and POST. It's stateless and usually returns JSON. I've used them as pipeline sources, handling pagination, rate limits and retries."

---

**Q. What is a higher order function?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A higher-order function either **takes a function as an argument** or **returns a function**. Examples: `map`, `filter`, `reduce`, `sorted(key=...)`, Python decorators, and Spark's `rdd.map(lambda x: ...)`.

```python
def apply_twice(f, x):        # takes a function
    return f(f(x))

def multiplier(n):            # returns a function (a closure)
    return lambda x: x * n

apply_twice(multiplier(3), 2)  # 18
```

See [Training 2 notes](/training-notes-site/notes/training-2/) ("Functional Tools (map, filter, reduce)").

**Say it out loud:** "A higher-order function takes another function as a parameter or returns one, like `map`, `filter` or a decorator. Spark's RDD API is built on them."

---

**Q. What is the CAP theorem?**

**A. (Class answer)** *(no answer given)*

**Expanded:** In a distributed data store, when a **network partition** happens (some nodes can't reach others), you must choose between **Consistency** (every read sees the latest write, or gets an error) and **Availability** (every request gets a non-error response, possibly stale). Partitions can't be ruled out in a real network, so the practical choice is **CP or AP**.

| Choice | Behavior during a partition | Examples |
|---|---|---|
| CP | Refuses or delays some requests rather than return stale data | HBase, ZooKeeper, HDFS (one active NameNode) |
| AP | Keeps answering, may return stale data, reconciles later | Cassandra, DynamoDB with default eventually consistent reads |

Many systems are tunable. Cassandra with `QUORUM` reads and writes behaves much more consistently than with `ONE`.

See [Training 6 notes](/training-notes-site/notes/training-6/) ("CAP Theorem").

**Say it out loud:** "CAP says that during a network partition a distributed store has to choose between consistency and availability. CP systems like HBase refuse requests rather than serve stale data, and AP systems like Cassandra keep answering and reconcile later."

---

**Q. What are ACID transactions?**

**A. (Class answer)** *(no answer given)*

**Expanded:** ACID describes the guarantees of a reliable database transaction:

| Letter | Property | Meaning |
|---|---|---|
| A | Atomicity | All of the transaction's changes happen, or none do (rollback on failure) |
| C | Consistency | The database moves from one valid state to another; constraints (keys, checks) are never broken |
| I | Isolation | Concurrent transactions don't see each other's partial work (isolation levels: read committed, repeatable read, serializable) |
| D | Durability | Once committed, the change survives a crash (write-ahead log) |

Classic example: a bank transfer debits one account and credits another. Both must happen or neither. Relational databases (Postgres, MySQL) are ACID. Plain files in a data lake are not, which is why **table formats** like Delta Lake and Iceberg add a transaction log to get ACID on S3/ADLS.

See [Training 5 notes](/training-notes-site/notes/training-5/) ("Data Lakehouse vs Data Warehouse") and [Training 13 notes](/training-notes-site/notes/training-13/) ("Delta and Iceberg").

**Say it out loud:** "ACID stands for atomicity, consistency, isolation and durability: a transaction fully happens or not at all, keeps the data valid, isn't disturbed by concurrent transactions, and survives crashes once committed. Data lakes get it through table formats like Delta Lake."

---

**Q. Structured data vs unstructured data vs semistructured data**

**A. (Class answer)** *(no answer given)*

**Expanded:**

| Type | What it is | Examples | Typical storage |
|---|---|---|---|
| Structured | Fixed schema of rows and columns, types known in advance | SQL tables, CSV with fixed columns | Relational DBs, warehouses, Parquet |
| Semi-structured | Self-describing with tags or keys, flexible or nested schema | JSON, XML, Avro, logs with key=value | Document DBs (MongoDB), data lakes, `VARIANT` columns in Snowflake |
| Unstructured | No data model | Images, video, audio, PDFs, free text | Object storage (S3), then processed with ML or text tools |

A typical pipeline turns semi-structured raw data (JSON in a Bronze layer) into structured tables (Silver/Gold).

**Say it out loud:** "Structured data has a fixed schema, like SQL tables. Semi-structured data carries its own flexible structure, like JSON or XML. Unstructured data has no model, like images or free text. Pipelines often flatten semi-structured JSON into structured tables."

---

**Q. What Is class inheritance?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Inheritance lets a **child class** (subclass) reuse the fields and methods of a **parent class** (superclass), and add to them or **override** them. It models an "is-a" relationship.

```python
class Source:
    def read(self): raise NotImplementedError
    def describe(self): return f"source {self.__class__.__name__}"

class S3Source(Source):           # S3Source is-a Source
    def read(self): return "reading from S3"   # overrides read()
```

Prefer composition ("has-a") when the relationship isn't truly "is-a"; deep inheritance trees get fragile.

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Worked Example: Traits, Inheritance, and Mixins (`TraitTest`)").

**Say it out loud:** "Inheritance lets a subclass reuse and extend a parent class's fields and methods, and override the ones it needs to change. It models an is-a relationship, like an S3 source being a kind of data source."

---

**Q. What is multiple inheritance?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Multiple inheritance means one class inherits from **more than one** parent class. It creates the **diamond problem**: if B and C both override a method from A and D inherits from both, which version does D get?

| Language | Multiple inheritance of classes? | How it handles the diamond |
|---|---|---|
| Python | Yes | Method Resolution Order (C3 linearization, see `D.__mro__`) |
| C++ | Yes | Virtual inheritance, programmer resolves ambiguity |
| Java | No (classes); yes for interfaces | Interfaces with default methods must be resolved explicitly |
| Scala | No (classes); yes via **traits** | Trait linearization: the rightmost mixed-in trait wins |

**Say it out loud:** "Multiple inheritance is inheriting from more than one parent class. It raises the diamond problem, so Java and Scala allow only one parent class plus multiple interfaces or traits, while Python allows it and resolves conflicts with its method resolution order."

---

**Q. What does it mean to instantiate a class?**

**A. (Class answer)** *(no answer given)*

**Expanded:** To instantiate a class is to **create an object (an instance) from it**. Memory is allocated and the **constructor** runs to set the initial state. Each instance has its own state.

```python
class Job:
    def __init__(self, name):   # constructor
        self.name = name
etl = Job("daily_sales")        # instantiation
```

```scala
val etl = new Job("daily_sales")   // Scala; case classes can drop `new`
```

Abstract classes and traits can't be instantiated directly. Scala `object`s are instantiated automatically, once.

**Say it out loud:** "Instantiating a class means creating an object from it: memory is allocated and the constructor runs, like `Job("daily_sales")` in Python or `new Job(...)` in Scala."

---

**Q. What is a package manager?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A package manager installs, upgrades and removes software packages and **resolves their dependencies** (including the right versions) from a repository.

| Ecosystem | Tool | Repository |
|---|---|---|
| Python | pip (with venv), conda, Poetry, uv | PyPI |
| JVM | Maven, sbt, Gradle (build tools with dependency management) | Maven Central |
| JavaScript | npm | npm registry |
| OS | apt (Debian/Ubuntu), yum/dnf (RHEL/Amazon Linux), Homebrew (macOS) | Distro repositories |

Pin versions (`requirements.txt`, lock files) so builds are reproducible.

See [Training 14 notes](/training-notes-site/notes/training-14/) ("Virtual Environments (Python)").

**Say it out loud:** "A package manager installs libraries and their dependencies at the right versions, like pip for Python, Maven or sbt for JVM projects and apt on Linux. I pin versions so the build is reproducible."

---

**Q. What is the SDLC?**

**A. (Class answer)** *(no answer given)*

**Expanded:** The Software Development Life Cycle is the set of phases software goes through: **planning/requirements → design → implementation (coding) → testing → deployment → maintenance**. Models differ in how they move through it: **Waterfall** does each phase once in order, while **Agile** repeats the cycle in short iterations (sprints). **CI/CD** automates the testing and deployment steps. For a data pipeline: gather requirements from stakeholders, design the architecture and data model, build, test with sample data, deploy through dev/test/prod, then monitor and maintain.

See [Training 4 notes](/training-notes-site/notes/training-4/) ("Environments") and [Training 0 notes](/training-notes-site/notes/training-0/) ("What are the three environments, and why was CI/CD invented?").

**Say it out loud:** "The SDLC is the lifecycle of requirements, design, development, testing, deployment and maintenance. Waterfall does it once in order, Agile repeats it in short sprints, and CI/CD automates the test and deploy steps."

---

**Q. What is compilation**

**A. (Class answer)** *(no answer given)*

**Expanded:** Compilation translates source code into a lower-level form **before** it runs: either native machine code (C, C++, Go, Rust) or an intermediate **bytecode** (Java, Scala, Kotlin compile to JVM bytecode, which the JVM then runs and JIT-compiles). Benefits: errors such as type mismatches are caught at compile time, and the result runs fast. Scala code is compiled with `scalac` (via sbt) into `.class` files, then packaged into a JAR.

See [Training 7 notes](/training-notes-site/notes/training-7/) ("The JVM (Java Virtual Machine)").

**Say it out loud:** "Compilation translates source code ahead of time into machine code or bytecode, like Scala compiling to JVM bytecode in a JAR. It catches many errors before the program runs and produces fast code."

---

**Q. What is an interpreted language?**

**A. (Class answer)** *(no answer given)*

**Expanded:** An interpreted language is executed by an **interpreter** that reads and runs the program at runtime, without a separate ahead-of-time compile step you manage. Python, JavaScript, Ruby and R are the usual examples. The line is blurry: CPython actually compiles your code to **bytecode** (`.pyc`) and then interprets that bytecode, and the JVM interprets bytecode and also JIT-compiles hot code. Trade-off: faster development and a REPL, but slower execution and errors found only when that line runs.

**Say it out loud:** "An interpreted language like Python is run by an interpreter at runtime instead of being compiled ahead of time. It's quicker to develop with, but slower, and errors show up only when the code runs. In practice Python compiles to bytecode and interprets that."

---

**Q. What is Big O Notation**

**A. (Class answer)** *(no answer given)*

**Expanded:** Big O describes how an algorithm's time (or memory) **grows as the input size n grows**, usually for the worst case, ignoring constants.

| Big O | Name | Example |
|---|---|---|
| O(1) | Constant | Dict/set lookup, list index |
| O(log n) | Logarithmic | Binary search, B-tree index lookup |
| O(n) | Linear | Scanning a list, `x in my_list` |
| O(n log n) | Linearithmic | Sorting (Timsort, merge sort) |
| O(n²) | Quadratic | Nested loops comparing every pair |

Data engineering angle: checking `x in list` inside a loop is O(n²) overall, while using a set makes it O(n). A database index turns an O(n) full scan into an O(log n) lookup.

**Say it out loud:** "Big O describes how runtime or memory grows with input size, ignoring constants. A dictionary lookup is O(1), a scan is O(n), sorting is O(n log n) and nested loops are O(n squared), so I'd use a set instead of a list for membership checks in a loop."

---

**Q. What is JSON format?**

**A. (Class answer)** *(no answer given)*

**Expanded:** JSON (JavaScript Object Notation) is a text format for data made of **objects** (`{"key": value}`), **arrays** (`[...]`), strings, numbers, booleans and `null`. It is human-readable, language-independent and semi-structured (it can nest, and records can have different fields). It's the default format of REST APIs and common in raw data layers. Downsides for analytics: it is verbose, has no enforced schema, has no date type, and is slow to scan compared with columnar formats such as Parquet. Big data tools often use **JSON Lines** (one JSON object per line) so files can be split. In Python: `json.loads`/`json.dumps`. In Spark: `spark.read.json`.

See [Training 2 notes](/training-notes-site/notes/training-2/) ("JSON / CSV").

**Say it out loud:** "JSON is a human-readable text format of key-value objects and arrays that can nest. It's the standard for APIs and raw data, but it's verbose and schema-less, so I usually convert it to Parquet for analytics."

---

**Q. What is string interpolation?**

**A. (Class answer)**

String interpolation is the process of putting variables into a string whose value will depend on the context in which the string is used. Examples include f-strings in Python and s-strings in Scala.

**Expanded:** The teacher's answer is correct. Examples:

```python
name, n = "sales", 42
f"{name} has {n} rows"            # Python f-string (3.6+)
f"{n:,} rows, {0.5:.1%}"          # with formatting: '42 rows, 50.0%'
```

```scala
val name = "sales"; val n = 42
s"$name has $n rows"              // s-interpolator
f"$n%05d"                          // f-interpolator, printf-style: 00042
raw"no\nescape"                    // raw-interpolator
```

Caution: never build SQL by interpolating user input (SQL injection). Use parameterized queries.

**Say it out loud:** "String interpolation embeds variables or expressions directly in a string, like Python f-strings or Scala's `s` interpolator. For SQL I'd use parameters instead to avoid injection."

---


## Python


**Q. What is an iterator**

**A. (Class answer)**

An iterator is an object that can traverse a collection.

Iterators are best known to developers by their use in loops. In the convention "for i in my_collection", i represents the iterator. It moves through the collection and is able to access the value of each element, which is necessary for a loop to function.

**Expanded:**

**Correction:** In `for i in my_collection`, `i` is the **loop variable**, the current element, not the iterator. The iterator is a hidden object the loop creates by calling `iter(my_collection)`. The loop then calls `next()` on it until it raises `StopIteration`.

| Term | Meaning | Example |
|---|---|---|
| Iterable | Something you can loop over (has `__iter__`) | list, dict, file, range |
| Iterator | The object that produces elements one at a time (has `__next__`), and is used up once | `it = iter([1, 2])` |

```python
it = iter([10, 20])
next(it)   # 10
next(it)   # 20
next(it)   # StopIteration
```

Iterators are lazy, so they can walk through data without holding all of it in memory (a file object is an iterator over lines).

**Say it out loud:** "An iterator is an object that returns elements one at a time through `next()` until it's exhausted. A for loop calls `iter()` on the collection to get one; the loop variable is just the current element."

---

**Q. What is a decorator**

**A. (Class answer)**

A decorator is basically a function modifier. It is applied to a function by placing an `@` symbol plus the name of the decorator above the name of the function, like so:

```python
@my_decorator
def my_function():
    return
```

Decorators are implemented as higher order functions. They take the function that they will modify as an argument and return the function with modifications.

**Expanded:** The teacher's answer is correct. A decorator is a higher-order function that **wraps** another function to add behavior (logging, timing, retries, caching, auth) without changing its code. `@my_decorator` above `def f` is shorthand for `f = my_decorator(f)`.

```python
import functools, time

def retry(times=3):
    def decorator(func):
        @functools.wraps(func)              # keep the original name and docstring
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == times - 1:
                        raise
                    time.sleep(2 ** attempt)
        return wrapper
    return decorator

@retry(times=3)
def call_api(): ...
```

Built-in examples: `@functools.lru_cache`, `@staticmethod`, `@property`. In data engineering: `@pandas_udf` in PySpark, `@task`/`@dag` in Airflow, `@dlt.table` in Databricks.

See [Training 2 notes](/training-notes-site/notes/training-2/) ("Core Python for Interviews").

**Say it out loud:** "A decorator is a function that wraps another function to add behavior like logging, retries or caching. Writing `@retry` above a function is shorthand for `func = retry(func)`. I've used them in Airflow's TaskFlow API and for PySpark pandas UDFs."

---

**Q. What is a generator**

**A. (Class answer)**

Generators are constructions in Python that allow us to traverse a collection without loading the entire collection into memory. When we use a regular loop, the entire collection must be loaded into memory in order to be used, which is a problem with very large datasets, especially datasets that are larger than the computer's available memory.

Generators allow us to load only one element of the collection into memory at a time. This allows us to iterate through very large datasets in a memory-efficient way.

**Expanded:**

**Correction:** A regular `for` loop doesn't require the whole collection in memory; the problem is when you **build** a full collection first (for example a list comprehension over millions of rows). A generator produces values **one at a time, on demand**, using `yield`, and pauses its state between values. A generator is a kind of iterator and can be consumed only once.

```python
def read_rows(path):
    with open(path) as f:
        for line in f:
            yield line.rstrip("\n").split(",")   # one row at a time

total = sum(float(r[2]) for r in read_rows("big.csv"))   # generator expression
```

`[x for x in ...]` builds a full list, while `(x for x in ...)` is a lazy generator.

See [Training 2 notes](/training-notes-site/notes/training-2/) ("Core Python for Interviews").

**Say it out loud:** "A generator is a function that uses `yield` to produce values one at a time, pausing in between, so I can stream through a huge file without loading it all into memory. It's a lazy iterator and can only be consumed once."

---

**Q. What is a dictionary**

**A. (Class answer)**

A dictionary is a data object in Python which stores data in key-value pair format, similar to a JSON object. We can use Python's json library to convert dictionaries to json files, and from json files to python dictionaries.

**Expanded:** The teacher's answer is correct. Additional points: dictionaries are implemented as **hash tables**, so lookup, insert and delete are **O(1)** on average. Keys must be **hashable** (immutable types like str, int, tuple). Since Python 3.7, dicts **preserve insertion order**. A JSON object maps directly to a dict through `json.loads`/`json.dumps`. Useful extras: `.get(key, default)`, `collections.defaultdict`, `collections.Counter`.

**Say it out loud:** "A dictionary is Python's key-value hash map with O(1) average lookups. Keys must be hashable, it keeps insertion order since Python 3.7, and it maps directly to JSON objects."

---

**Q. What is a lambda function?**

**A. (Class answer)**

A lambda function is a Python function which can be written on a single line.

A lambda function is also capable of being anonymous, unlike standard Python functions, but this is not its definition - this is because lambda functions are also capable of being named, which you can do if you assign them to a variable.

**Expanded:**

**Correction:** The defining restriction is that a lambda body is a **single expression**, not "a single line". It can't contain statements such as assignments, `return`, `for` or `try`. A long lambda can also span lines inside brackets. Lambdas are anonymous; assigning one to a variable works, but style guides (PEP 8) recommend a `def` in that case.

```python
sorted(rows, key=lambda r: r["date"])
rdd.map(lambda x: (x.station_id, 1))
```

**Say it out loud:** "A lambda is a small anonymous function whose body is a single expression, like `lambda r: r['date']`. I use them inline for sort keys or Spark `map` calls, and a regular `def` for anything more."

---

**Q. What is the GIL?**

**A. (Class answer)**

The GIL, which stands for Global Interpreter Lock, is a feature of Python that enforces single-threaded programming globally. This implies that multithreaded programming is not allowed. (Multithreaded programming is programming in which two or more processes can execute at the same time, rather than sequentially.)

**Expanded:**

**Correction:** The GIL does **not** forbid multithreaded programming. Threads are allowed and widely used. The Global Interpreter Lock is a lock in CPython that lets **only one thread execute Python bytecode at a time** within a process. Threads still help with **I/O-bound** work, because a thread waiting on the network or disk releases the GIL. They don't speed up **CPU-bound** pure-Python work. (Also, the parenthetical mixes terms: threads run inside one process; multiple processes is multiprocessing.)

Two updates: libraries like NumPy and pandas release the GIL inside their C code. And Python 3.13 added an optional, experimental **free-threaded build** without the GIL (PEP 703), which Python 3.14 made officially supported.

See [Training 2 notes](/training-notes-site/notes/training-2/) ("Python Background", multithreading and multiprocessing examples).

**Say it out loud:** "The GIL is a lock in CPython that lets only one thread run Python bytecode at a time per process. Threads are still fine for I/O-bound work like API calls, but for CPU-bound work I use multiprocessing or a distributed engine like Spark."

---

**Q. How can you get around the limitations of the GIL?**

**A. (Class answer)**

There are two libraries that allow us to get around the GIL.

The first is called Multithreading. It's part of Python's standard library, so it does not need to be installed with PIP. It allows for multithreaded programming within a single Python environment, which means that it is limited to multithreading on a single machine. This allows you to take advantage of a multi-core processor on one machine by making use of as many as all available cores.

The other is called Multiprocessing. It allows us to do multithreaded programming across multiple Python environments, meaning that it can be programmed to do multithreaded programming across a cluster. This is essential for writing distributed programs on a cluster, which we are highly likely to need to do as data engineers.

**Expanded:**

**Correction:** Three corrections:
- The standard-library module is **`threading`** (plus `concurrent.futures.ThreadPoolExecutor`), not "Multithreading". It does **not** get around the GIL for CPU work and does not let pure-Python code use all cores. It helps I/O-bound work.
- **`multiprocessing`** gets around the GIL by running **separate processes, each with its own interpreter and GIL**, but **on one machine**. It does not run across a cluster.
- For a **cluster**, use a distributed framework: **Spark (PySpark)**, **Dask** or **Ray**.

| Workload | Tool |
|---|---|
| I/O-bound (APIs, S3, DB calls) | `threading`, `ThreadPoolExecutor`, `asyncio` |
| CPU-bound on one machine | `multiprocessing`, `ProcessPoolExecutor`, or vectorized NumPy/pandas (C code releases the GIL) |
| More data or compute than one machine | Spark, Dask, Ray |

See [Training 2 notes](/training-notes-site/notes/training-2/) ("Python Background").

**Say it out loud:** "For I/O-bound work, threads or asyncio are fine because waiting threads release the GIL. For CPU-bound work on one machine I use multiprocessing, since each process has its own GIL. To go beyond one machine I use Spark, Dask or Ray."

---

**Q. List vs tuple**

**A. (Class answer)**

A tuple is immutable, a list is mutable - this is the standard interview answer.

Other details include that lists are declared with square brackets and tuples are declared with parentheses. Also, tuples are often used to represent rows in a dataset, while lists are usually employed when the use of the data is less rigid.

**Expanded:** The teacher's answer is correct. More detail: because a tuple is immutable it is **hashable** (if its items are), so it can be a dict key or set member, and it is slightly smaller and faster. A list can grow and change in place (`append`, `sort`). Use a tuple for fixed records (a row, a coordinate, multiple return values) and a list for a collection that changes. Note: a one-element tuple needs a comma: `(5,)`.

See [Training 2 notes](/training-notes-site/notes/training-2/) ("Core Python for Interviews").

**Say it out loud:** "A list is mutable and a tuple is immutable. Because tuples can't change they're hashable, so they can be dictionary keys, and they suit fixed records like a row, while lists suit collections that change."

---

**Q. List vs set**

**A. (Class answer)**

A list allows for duplicate values and preserves the order of the elements that are put into it. A set does not allow for duplicates, and it does not preserve the order of the elements.

This means that if you want to remove duplicates from a list and you don't need to worry about the order, you can simply convert it to a set.

**Expanded:** The teacher's answer is correct, with one important addition: a set is a **hash table**, so `x in my_set` is **O(1)**, while `x in my_list` is **O(n)**. Sets also support set math (`|` union, `&` intersection, `-` difference), and items must be hashable. To remove duplicates **and keep order**, use `list(dict.fromkeys(items))`, since dicts keep insertion order.

**Say it out loud:** "A list keeps order and allows duplicates. A set has no duplicates and no order, but membership checks are O(1) instead of O(n), so I use sets for de-duplication and fast lookups."

---

**Q. Which Python libraries have you used?**

**A. (Class answer)**

Pyspark, Pandas, boto3, multithreading, multiprocessing, matplotlib, seaborn, numpy, plotly, Koalas, Dask, kafka-python, pytest

**Expanded:** Update two names in the teacher's list: the standard-library modules are **`threading`** and `multiprocessing` (there is no "multithreading" module), and **Koalas** was merged into Spark as the **pandas API on Spark** (`pyspark.pandas`) in Spark 3.2. Only list libraries you can actually talk about. A strong data engineering set, grouped:

| Area | Libraries |
|---|---|
| Processing | PySpark, pandas, NumPy, Polars, Dask |
| Cloud / I/O | boto3, requests, SQLAlchemy, psycopg2, pyarrow |
| Streaming | kafka-python or confluent-kafka |
| Orchestration | Apache Airflow |
| Testing / quality | pytest, unittest, Great Expectations |
| Visualization | matplotlib, seaborn, plotly, Streamlit |

**Say it out loud:** "Mostly PySpark and pandas for processing, boto3 for AWS, kafka-python for streaming, pytest for testing and Streamlit or matplotlib for quick dashboards. I've also used `threading` and `multiprocessing` for parallel work."

---


## Scala


**Q. Do scala classes support multiple inheritance?**

**A. (Class answer)**

No. Multiple inheritance is not allowed in Scala. This helps us to avoid what is called the diamond problem. The diamond problem is an issue in which there is an ambiguity about which chain of logic should reference a class that is referenced by another class.

So, consider this diagram:

```text
Class A - base class

Class B - Inherits from Class A       Class C - Inherits from Class A

Class D - Inherits from both classes B and C
```

When a method in class D is called, which is inherited from class A through both classes B and C, there is a problem that the compiler encounters in which it can't decide whether the class should be inherited through the chain of classes D -> B -> A or from D -> C -> A.

This is the official reason given for why multiple inheritance is not supported, but there is a way around this problem, which is the use of a trait.

**Expanded:** The teacher's answer is correct: a Scala class can **extend only one class**, but it can **mix in any number of traits** with `with`. Scala avoids the diamond problem through **linearization**: the traits are ordered, and a call resolves to the **rightmost** trait's implementation, with `super` calls chaining leftward. So Scala gets most of the benefit of multiple inheritance without ambiguity.

```scala
trait A { def hi = "A" }
trait B extends A { override def hi = "B" + super.hi }
trait C extends A { override def hi = "C" + super.hi }
class D extends B with C
new D().hi   // "CBA": C is rightmost, then B, then A
```

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Worked Example: Traits, Inheritance, and Mixins (`TraitTest`)").

**Say it out loud:** "A Scala class can extend only one class, but it can mix in many traits. Scala resolves the diamond problem with linearization, where the rightmost trait wins and `super` calls chain through the others."

---

**Q. What is a case class**

**A. (Class answer)**

A case class is a special type of class in Scala which has key-value parameters which can be used to specify a number of traits within it.

A basic use of case classes is to define aspects of objects that can be used in a match statement for pattern matching.

The reason why case classes are important to Data Engineers is because case classes can be used to create a number of objects from which the schema can be inferred. Each key-value argument in the case class will be interpreted by Spark as the name and data type of a column in a DataFrame or DataSet, respectively.

**Expanded:**

**Correction:** A case class does not have "key-value parameters that specify traits". A case class is an **immutable data class**: its constructor parameters automatically become public `val` fields, and the compiler generates `equals`/`hashCode` (compared by value), `toString`, `copy`, a companion `apply` (no `new` needed) and `unapply` (which is what makes pattern matching work).

```scala
case class Trip(stationId: String, bikes: Int)
val t = Trip("S1", 5)                 // no `new`
val t2 = t.copy(bikes = 6)            // immutable update
t match { case Trip(id, b) if b > 0 => println(s"$id has bikes") }

import spark.implicits._
val ds = Seq(t, t2).toDS()            // columns stationId: string, bikes: int
```

The teacher's Spark point is right: Spark uses a case class's field names and types as the **schema** of a Dataset or DataFrame.

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Worked Example (Teacher's Code): `case class` + `Dataset[Person]`").

**Say it out loud:** "A case class is Scala's immutable data class. The compiler generates equality by value, `toString`, `copy` and `apply`/`unapply`, so it works with pattern matching. In Spark, its fields become the schema of a typed Dataset."

---

**Q. What is a trait**

**A. (Class answer)**

A trait is an object that is similar to a class, but which is not a class. We can define methods within it and we can inherit from it. The major difference between a trait and a class is that a class can inherit from multiple traits. Also, the syntax for inheriting from traits is different.

When inheriting from a class, we use the "extends" keyword, as in:

```scala
class Class_B extends Class_A
```

Whereas when inheriting from a trait, we can use either "extends" or "with". It's using the "with" keyword that allows us to do multiple inheritance. For example:

```scala
class Class_D extends Class_A with Class_B with Class_C
```

Doing this allows us to implement something that is similar to multiple inheritance, but which does not cause the diamond problem.

Traits also cannot be instantiated as objects. They are only used as things to be inherited from.

It's important to remember traits are "mixed in to" classes. Even though we use the "with" keyword in the actual syntax, when we are talking about the code, we say that we are "mixing the trait into the class".

**Expanded:** The teacher's answer is mostly correct. Precision: a trait is a **type**, like a Java interface that can also contain implemented methods and fields. It is not "an object". A class extends one class but can mix in many traits, the first with `extends` and the rest with `with` (or all with `with` after an `extends` of a class). Traits can't be instantiated on their own (only as an anonymous class: `new MyTrait {}`). In Scala 2, traits can't take constructor parameters; Scala 3 allows it.

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Worked Example: Traits, Inheritance, and Mixins (`TraitTest`)").

**Say it out loud:** "A trait is like a Java interface that can also hold implemented methods. A class can mix in many traits, which is how Scala gets multiple-inheritance-like reuse without the diamond problem."

---

**Q. What is an abstract class?**

**A. (Class answer)**

An abstract class is a class which cannot be instantiated as an object. That means that the only use for an abstract class is for other classes to inherit from it.

The reason that we have abstract classes is because there are certain classes which are not designed to be used as objects, and which the developers on a team want to create a rule that disallows other team members from using those classes improperly.

**Expanded:** The teacher's answer is correct. An abstract class can contain both **abstract members** (declared, not implemented) and concrete ones, and subclasses must implement the abstract members. It defines a shared base with some common code.

```scala
abstract class Source(val name: String) {
  def read(): Seq[String]                 // abstract
  def describe = s"source $name"          // concrete
}
class CsvSource extends Source("csv") { def read() = Seq("row") }
```

**Say it out loud:** "An abstract class can't be instantiated. It defines some methods without implementations that subclasses must fill in, plus shared code they inherit."

---

**Q. What is the difference between an abstract class and a trait?**

**A. (Class answer)**

Both an abstract class and a trait are used exclusively for inheritance and not for instantiation as objects.

The major difference is that a trait is not a class, and therefore the rules of classes do not apply to a trait. Therefore, because an abstract class is a class, it does not allow multiple inheritance. Whereas a trait allows multiple inheritance, because it is not a class.

**Expanded:** The teacher's answer is right that a class can mix in many traits but extend only one abstract class. More differences interviewers look for:

| | Abstract class | Trait |
|---|---|---|
| How many per class | One | Many (mixins) |
| Constructor parameters | Yes | No in Scala 2, yes in Scala 3 |
| Java interop | Maps cleanly to a Java abstract class | Compiles to an interface |
| Typical use | A base class with constructor state | Reusable behavior mixed into many classes |

Rule of thumb: prefer traits, and use an abstract class when you need constructor parameters or Java code needs to extend it.

**Say it out loud:** "A class can extend only one abstract class but mix in many traits. Abstract classes can take constructor parameters and interoperate cleanly with Java, while traits are for reusable behavior. I default to traits."

---

**Q. What is a singleton**

**A. (Class answer)**

A singleton, also called a singleton object, is an object in Scala that does not have an associated class. It is declared using the object keyword, and it cannot be instantiated more than once. It is self-instantiating and self-executing, so it is a straightforward way to write a simple app.

**Expanded:**

**Correction:** A Scala `object` is created **lazily, once**, the first time it is used. That part is right. But it is not "self-executing". Its code runs as a program only if it defines a `main` method or `extends App` (Scala 2) or uses `@main` (Scala 3). Also, an `object` can share its name with a class; that's a **companion object**.

```scala
object Config {                 // singleton: one instance, created on first use
  val bucket = "my-bucket"
}
object MyJob {
  def main(args: Array[String]): Unit = println(Config.bucket)   // entry point
}
```

Common uses: entry points for Spark jobs, utility functions, constants, and companion objects with factory methods.

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Companion Objects") and [Training 9 notes](/training-notes-site/notes/training-9/) ("Scala Fundamentals").

**Say it out loud:** "A singleton in Scala is an `object`: a single instance created lazily the first time it's used. It holds utilities or constants, and it becomes a program's entry point only if it defines `main` or extends `App`."

---

**Q. What is a future class**

**A. (Class answer)** *(no answer given)*

**Expanded:** A `Future[T]` represents a value that will be available **later**, computed asynchronously on another thread from an `ExecutionContext` (a thread pool). It completes with either a value or an exception. You combine futures with `map`, `flatMap` and for-comprehensions instead of blocking, and handle results with `onComplete` or `recover`. `Await.result` blocks, so use it only at the edge of a program.

```scala
import scala.concurrent.{Future, Await}
import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.duration._

val a = Future { loadTable("a") }
val b = Future { loadTable("b") }
val both = for { x <- a; y <- b } yield x ++ y    // a and b run in parallel
Await.result(both, 5.minutes)
```

In data engineering it's useful for running independent I/O calls in parallel (several API calls, uploads). It's not how Spark parallelizes work; Spark has its own executors.

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Future Classes - Asynchronous Programming in Scala").

**Say it out loud:** "A Future is a placeholder for a result computed asynchronously on a thread pool. I compose futures with `map` and `flatMap` instead of blocking, which is handy for running independent I/O tasks in parallel."

---

**Q. What is a sealed class**

**A. (Class answer)** *(no answer given)*

**Expanded:** A `sealed` trait or class can only be extended **in the same source file**. Because the compiler knows every subtype, it can warn when a `match` is **not exhaustive**. That makes sealed traits the standard way to model a fixed set of cases (an algebraic data type).

```scala
sealed trait LoadResult
case class Success(rows: Long) extends LoadResult
case class Failure(err: String) extends LoadResult

def report(r: LoadResult) = r match {
  case Success(n) => s"loaded $n"
  case Failure(e) => s"failed: $e"     // leave this out and the compiler warns
}
```

`Option` (`Some`/`None`) is itself built this way.

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Sealed Traits/Classes - Exhaustive Pattern Matching").

**Say it out loud:** "A sealed trait or class can only be extended in its own file, so the compiler knows all the subtypes and warns me if a pattern match misses a case. It's how Scala models a fixed set of outcomes, like `Option`."

---

**Q. What is an implicit function**

**A. (Class answer)** *(no answer given)*

**Expanded:** In Scala 2, `implicit` lets the compiler fill something in for you:
- **Implicit parameters:** values the compiler passes automatically if one of the right type is in scope (for example an `ExecutionContext` or a Spark `Encoder`).
- **Implicit conversions / implicit classes:** add methods to an existing type ("extension methods").

`import spark.implicits._` is the Spark example: it brings in the encoders for case classes and the conversions that make `.toDF()`, `.toDS()`, `.as[T]` and `$"col"` work. Scala 3 replaces most of this with `given`/`using` and `extension` methods. Overusing implicits makes code hard to read.

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Implicits - Why `import spark.implicits._` and Similar Lines Actually Work").

**Say it out loud:** "Implicits let the Scala compiler supply parameters or conversions automatically when they're in scope. The everyday example is `import spark.implicits._`, which provides the encoders and conversions behind `toDF`, `toDS` and the `$` column syntax. Scala 3 calls them `given` and `using`."

---

**Q. What is a closure**

**A. (Class answer)** *(no answer given)*

**Expanded:** A closure is a function that **captures variables from the scope where it was defined** and can use them later, even after that scope has ended.

```scala
val threshold = 100
val isBig = (x: Int) => x > threshold   // captures threshold
```

In Spark this matters a lot: the function you pass to `map` or `filter` is a closure, and Spark **serializes it together with everything it captures** and ships it to the executors. Two consequences: anything captured must be serializable (capturing a non-serializable object gives `Task not serializable`), and changing a captured driver variable inside a task changes only the executor's copy (use an accumulator instead).

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Closures" and "Closures Are Everywhere in Spark Code").

**Say it out loud:** "A closure is a function that captures variables from its surrounding scope. In Spark, the lambdas I pass to `map` are closures that get serialized and sent to executors, so captured objects must be serializable and changes on executors don't come back to the driver."

---

**Q. What is a companion object?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A companion object is an `object` with the **same name as a class, in the same file**. The two can access each other's private members. The object holds what Java would make `static`: factory `apply` methods, constants and helpers. Case classes get a companion automatically (that's why `Trip("S1", 5)` works without `new`).

```scala
class Station private (val id: String)
object Station {
  def apply(id: String): Station = new Station(id.trim.toUpperCase)   // factory
}
val s = Station(" s1 ")
```

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Companion Objects").

**Say it out loud:** "A companion object is an object with the same name as a class in the same file. It holds the class's static-style members like factory `apply` methods, and the two can see each other's private members."

---

**Q. Nil vs Null vs null vs Nothing vs None vs Unit**

**A. (Class answer)**

- Nil - represents an empty list
- Null - a trait that represents a null value
- null - the standard Java null value
- Nothing - represents truly nothing
- None - represents an absent value in an option type
- Unit - a return type that is equivalent to Java's void, basically returning nothing

**Expanded:** The teacher's list is right. Two precisions: `Null` is a **type** (the type of the value `null`, a subtype of every reference type), and `Nothing` is the **bottom type**, a subtype of every type that has **no values at all**. It's the type of an expression that never returns normally, such as `throw`.

| Term | Kind | Meaning | Example |
|---|---|---|---|
| `Nil` | Value | The empty `List` | `1 :: 2 :: Nil` |
| `Null` | Type | Type whose only value is `null` | Rarely written directly |
| `null` | Value | Java's null reference, avoid in Scala | Comes from Java libraries, Spark nulls |
| `Nothing` | Type | Bottom type, has no values | `def fail(): Nothing = throw new Exception` |
| `None` | Value | Empty case of `Option` | `Option(null) == None` |
| `Unit` | Type (value `()`) | No meaningful result, like Java `void` | `def log(s: String): Unit` |

See [Training 10 notes](/training-notes-site/notes/training-10/) (the "Nothing-Like" Types section).

**Say it out loud:** "`Nil` is the empty list, `None` is the empty Option, `Unit` is the no-result return type like void, `null` is the Java null reference, `Null` is its type, and `Nothing` is the bottom type with no values, used for things like throwing an exception."

---

**Q. What is the difference between overloading and overriding?**

**A. (Class answer)** *(no answer given)*

**Expanded:**

| | Overloading | Overriding |
|---|---|---|
| What | Same method name, **different parameter lists**, in the same class | A subclass **replaces** an inherited method with the same signature |
| Resolved | At **compile time** (by argument types) | At **runtime** (by the object's actual class: polymorphism) |
| Keyword (Scala) | None | `override` (required when replacing a concrete method) |

```scala
class Writer {
  def write(s: String) = println(s)
  def write(n: Int) = println(n.toString)        // overloading
}
class S3Writer extends Writer {
  override def write(s: String) = println(s"s3: $s")   // overriding
}
```

Python has no real overloading: a second `def` with the same name replaces the first, and you use default or variable arguments instead.

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Overloading vs. Overriding").

**Say it out loud:** "Overloading is the same method name with different parameters in one class, chosen at compile time. Overriding is a subclass replacing a parent's method with the same signature, chosen at runtime, which is how polymorphism works."

---

**Q. What is SBT and how have you used it?**

**A. (Class answer)**

SBT stands for Scala Build Tool, and it is the main package manager that is specific to Scala. Scala projects can also use Maven or other package managers, but most Scala projects use SBT because it is a simpler interface relative to Maven.

**Expanded:** Precision: sbt is a **build tool** (it includes dependency management), not just a package manager. It compiles, tests, runs and packages Scala/Java projects, is configured in `build.sbt`, and downloads libraries from Maven Central.

```scala
// build.sbt
name := "citibike-etl"
scalaVersion := "2.12.18"
libraryDependencies += "org.apache.spark" %% "spark-sql" % "3.5.1" % "provided"
```

| Command | Does |
|---|---|
| `sbt compile` / `sbt test` / `sbt run` | Compile, run tests, run the main class |
| `sbt package` | JAR of **your classes only** |
| `sbt assembly` (plugin) | **Fat JAR** with dependencies (mark Spark as `provided` so it isn't bundled) |

See [Training 9 notes](/training-notes-site/notes/training-9/) ("Scala Spark Job with sbt (Homework 9)").

**Say it out loud:** "sbt is Scala's build tool. I declare dependencies in `build.sbt`, compile and test with it, and package my Spark job, using `sbt assembly` for a fat JAR with Spark marked as provided, then run it with spark-submit."

---

**Q. What is currying?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Currying turns a function of several arguments into a chain of functions that each take **one argument list**. That lets you supply some arguments now and the rest later (partial application).

```scala
def add(a: Int)(b: Int): Int = a + b
val addTen = add(10) _        // supply the first list now
addTen(5)                      // 15
```

Where you see it in Scala: `foldLeft(0)(_ + _)`, and putting implicit parameters in a second list (`def run(sql: String)(implicit spark: SparkSession)`).

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Currying").

**Say it out loud:** "Currying turns a multi-argument function into a chain of single-argument-list functions, so I can fix some arguments now and pass the rest later. Scala uses it in `foldLeft` and for implicit parameter lists."

---

**Q. What is an artifact? What is a JAR file?**

**A. (Class answer)**

An artifact in JVM languages is a package of the input files and classes that you use when programming, which are compressed into a single file, which is executable on the command line. It will have the .jar extension, and it can be executed with the command `java -jar <name of your file> <any other command line arguments>`.

JAR files are very useful for sharing your code and making it easier to execute your code outside of an IDE. Package management in JVM languages can be difficult if trying to execute your code outside of an IDE, but if you package your code into a JAR file, then the dependencies are included in the JAR, so you don't have to worry about your code failing because you didn't include a dependency.

**Expanded:**

**Correction:** Two precisions:
- "Artifact" is the general word for **any file a build produces** and publishes (a JAR, a wheel, a Docker image, a zip). A JAR is the usual JVM artifact.
- A JAR includes its dependencies only if it is a **fat (uber) JAR**, built with `sbt assembly` or Maven's shade plugin. A plain `sbt package` JAR contains only your compiled classes. Also, `java -jar` works only if the JAR's manifest names a `Main-Class`.

A JAR is a zip archive of compiled `.class` files plus resources and a manifest. For Spark you usually build a fat JAR with Spark itself marked `provided` (the cluster already has it) and run it with `spark-submit --class com.example.Main app.jar`.

**Say it out loud:** "An artifact is any output of a build, and for JVM projects that's usually a JAR, a zip of compiled classes and a manifest. A plain JAR has only my code. A fat JAR from `sbt assembly` also bundles the dependencies, which is what I submit to Spark."

---

**Q. What is an option type in Scala**

**A. (Class answer)**

An option is a type of object that has the pattern Option/Some/None. It represents a way of giving us the flexibility for objects in a collection to have either some type of value or no value, to be determined at a later time.

**Expanded:** The teacher's answer is close. More precisely: `Option[T]` is a container that holds either **`Some(value)`** or **`None`**. It replaces `null` so the type itself says "this may be missing" and the compiler makes you handle it. It's not mainly about values being "determined at a later time".

```scala
val m = Map("a" -> 1)
m.get("b")                     // None, instead of null
m.get("a").map(_ * 2)          // Some(2)
m.get("b").getOrElse(0)        // 0
Option(javaValueThatMayBeNull) // wraps a possible null safely
```

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Scala's `Option` Type").

**Say it out loud:** "Option represents a value that may be missing: `Some(value)` or `None`. It replaces null, so the type forces callers to handle the missing case with things like `getOrElse`, `map` or pattern matching."

---


## Java


**Q. What is method overloading?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Method overloading is defining **several methods with the same name but different parameter lists** (number or types of parameters) in the same class. The compiler picks the right one at **compile time** from the argument types. The return type alone can't distinguish overloads.

```java
class Calc {
    int add(int a, int b) { return a + b; }
    double add(double a, double b) { return a + b; }
    int add(int a, int b, int c) { return a + b + c; }
}
```

Contrast with **overriding** (a subclass replacing an inherited method, resolved at runtime). See the Scala overloading/overriding question above and [Training 10 notes](/training-notes-site/notes/training-10/) ("Overloading vs. Overriding").

**Say it out loud:** "Method overloading means several methods with the same name but different parameter lists in one class, like `add(int, int)` and `add(double, double)`. Java picks the right one at compile time from the argument types."

---

**Q. What is the JVM?**

**A. (Class answer)**

The JVM is one of the most important parts of Java and all other languages in the JVM family. Any language called a JVM language can be run on the JVM.

The JVM is very complex, but at its core it is a special kind of combination of compiler and interpreter.

What it does is that it will take your code written in Java, Scala, or any other JVM language and it will compile that code to something called Java Bytecode, which is similar to assembly language.

The reason that we use Java Bytecode in the JVM is to implement one of the most important features of Java, which is called Write Once, Run Anywhere.

So in compiled languages that were created before Java, one of the issues that teams would have to deal with is that the code would compile to a sequence of 0s and 1s which were designed to be run on the computer on which it was compiled. The problem with this is that if that code was then sent to another computer which runs a different kind of processor, that processor might not use the same sequences of 0s and 1s to do the same thing. So if you would write your C or C++ code on a computer running an Intel processor, and then you tried to send it to another computer which was running an AMD processor, there was a possibility of getting errors that were simply due to the fact that the processor was different.

The JVM was created in part to solve this problem. Rather than the team having to write multiple versions of its code in order to run it on multiple types of processors, the JVM is designed to be able to run on any commercially available piece of hardware, and there is a team of people at Oracle that make sure that the latest version of the JVM is going to be able to run on any piece of hardware that you can buy.

This means that teams of developers who work on a JVM language do not need to do that themselves, which saves a lot of programmer time, and a lot of work that most programmers find unpleasant.

The way that Write Once, Run Anywhere is achieved is that the written code is compiled to Java bytecode, and the JVM interprets that code, using the specific way that the code is supposed to be run on the specific processor that it's running on. So, if you write your Java code on an Intel X86 processor and then try to run that same code on an ARM chip, you are guaranteed to not have any processor-related errors.

The JVM also manages memory and does other low-level tasks, but write-once-run-anywhere is its most important feature, and it's what originally made Java into a popular language.

**Expanded:**

**Correction:** Three corrections:
- The **JVM does not compile your Java or Scala source into bytecode**. The language's **compiler** does that (`javac`, `scalac`) ahead of time, producing `.class` files. The JVM then **loads and runs** the bytecode: it interprets it at first and **JIT-compiles** frequently used code into native machine code.
- The Intel-vs-AMD example is wrong. Both make **x86-64** processors that run the **same** compiled binaries. The real portability problems for C/C++ binaries are different **CPU architectures** (x86-64 vs ARM) and different **operating systems** (Windows vs Linux vs macOS), which need separate builds.
- The JVM isn't maintained only by "a team at Oracle". **OpenJDK** is the open-source reference implementation, and several vendors build and support JVMs (Oracle, Amazon Corretto, Eclipse Temurin, Microsoft, Azul) for the major OS/CPU combinations.

| Step | Tool | Output |
|---|---|---|
| Compile | `javac` / `scalac` (through sbt or Maven) | Platform-independent bytecode (`.class`, packaged in a JAR) |
| Run | JVM (`java`) | Interprets bytecode, JIT-compiles hot code to native code for that CPU and OS |

The JVM also manages memory through **garbage collection**, which matters for Spark: GC pauses and heap sizing are common tuning topics.

See [Training 7 notes](/training-notes-site/notes/training-7/) ("The JVM (Java Virtual Machine)", "JVM Languages" and "Why the JVM Exists (Historical Motivation)").

**Say it out loud:** "The JVM runs Java bytecode. Compilers like `javac` or `scalac` turn source code into bytecode, and the JVM interprets and JIT-compiles it for whatever CPU and OS it's on, which gives write once, run anywhere. It also handles memory with garbage collection. Spark, Kafka and Hadoop all run on it."

---

**Q. What version of Java is most common today?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Teams standardize on **LTS (long-term support)** releases: **Java 8, 11, 17, 21 and 25** (25 arrived in September 2025). Java 17 and 21 are the most common for current projects, and plenty of legacy systems still run Java 8 or 11 (verify current survey numbers if asked). Data engineering compatibility: **Spark 3.5** runs on Java 8, 11 and 17, and **Spark 4.0 requires Java 17 or 21** (and Scala 2.13). Kafka 4.0 brokers need Java 17.

**Say it out loud:** "Companies standardize on LTS releases. Java 17 and 21 are the most common now, with some legacy 8 and 11. For Spark it matters: Spark 3.5 supports up to 17, and Spark 4 requires 17 or 21."

---

**Q. What is Maven and how have you used it?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Maven is a **build and dependency management tool** for Java (and Scala) projects. A `pom.xml` file declares the project's coordinates (`groupId:artifactId:version`), dependencies and plugins. Maven downloads dependencies from **Maven Central** and runs a standard lifecycle: `mvn compile`, `mvn test`, `mvn package` (JAR), `mvn install` (into the local `~/.m2` repository). The **shade** plugin builds fat JARs. Even outside Maven projects you use Maven coordinates all the time, for example `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1` downloads from Maven Central.

**Say it out loud:** "Maven is Java's build and dependency tool. You declare dependencies in `pom.xml`, and it downloads them from Maven Central and compiles, tests and packages the project. I mostly use Maven coordinates with `spark-submit --packages` and sbt, which uses the same repositories."

---

**Q. What is Spring Boot?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Spring Boot is a Java framework for quickly building **production-ready applications**, especially **REST APIs and microservices**, on top of the Spring Framework. It provides auto-configuration, an embedded web server (you run a single JAR, no separate Tomcat install), "starter" dependencies, and built-in health checks and metrics (Actuator). It's mostly backend development rather than data engineering, but data engineers meet it when a Spring Boot service is a data source (an API, or a Kafka producer through Spring Kafka).

**Say it out loud:** "Spring Boot is a Java framework for building REST APIs and microservices fast, with auto-configuration and an embedded web server so the app runs as a single JAR. It's more backend than data engineering, but those services are often our data sources."

---

**Q. Is Java strongly or dynamically typed?**

**A. (Class answer)** *(no answer given)*

**Expanded:** The question mixes two separate axes. Java is **statically typed** (types are checked at compile time) and **strongly typed** (no silent conversions between unrelated types). It is not dynamically typed. Since Java 10, `var` lets the compiler infer a local variable's type, but the type is still fixed at compile time.

| | Static (checked at compile time) | Dynamic (checked at runtime) |
|---|---|---|
| Strong | Java, Scala | Python |
| Weak | C | JavaScript |

**Say it out loud:** "Java is statically and strongly typed: every variable's type is known and checked at compile time, and it won't silently convert between unrelated types. Python, by comparison, is dynamically but strongly typed."

---

**Q. What is the difference between the JDK and the JRE?**

**A. (Class answer)**

The JRE is the Java Runtime Environment, which means that it is capable of running Java code, but it does not allow the user to write and compile their own Java code. This is the standard Java installation that comes on machines that have Java installed by default, because most computer users only need to run Java programs, and they do not need to know how to write them.

The JDK is the Java Development Kit, which is what you need if you are going to run your own Java code. If you are trying to run Java, Scala, or any other JVM language, you need to make sure that you have the JDK and not just the JRE.

**Expanded:**

**Correction:** The second paragraph contradicts the first. You need the **JDK to compile and build** code. A **JRE is enough to run** already-compiled code. In practice the difference has faded: since **Java 11** Oracle and most vendors no longer ship a separate JRE, and Java isn't preinstalled on most machines anymore, so you simply install a JDK (which includes everything needed to run code). Tools like sbt and IntelliJ need a JDK because they compile.

| | JRE | JDK |
|---|---|---|
| Contains | JVM + standard class libraries | JRE contents + compiler (`javac`), `jar`, debugger and other tools |
| Needed for | Running compiled Java/Scala programs | Developing, compiling and packaging |

See [Training 9 notes](/training-notes-site/notes/training-9/) ("IntelliJ + Scala/sbt Project Setup Troubleshooting").

**Say it out loud:** "The JRE is the runtime, the JVM plus libraries, which is enough to run compiled programs. The JDK adds the compiler and dev tools, so you need it to build code. Since Java 11 there's usually no separate JRE, so you just install a JDK."

---


## SQL


**Q. Which SQL distributions have you used?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Name the engines you can talk about and where you used them. Grouping them shows you know the difference between transactional and analytical systems:

| Kind | Examples |
|---|---|
| OLTP (transactional) databases | PostgreSQL, MySQL/MariaDB, SQL Server, Oracle, Amazon RDS/Aurora |
| Cloud warehouses (OLAP) | Amazon Redshift, Snowflake, Google BigQuery, Azure Synapse |
| Query engines over files | Spark SQL, Hive (HiveQL), Athena / Trino, Databricks SQL |

The dialects differ in details (`LIMIT` vs `TOP`, date functions, `QUALIFY` in Snowflake/BigQuery/Databricks, upsert syntax).

See [Training 4 notes](/training-notes-site/notes/training-4/) ("Databases & SQL Providers").

**Say it out loud:** "I've used PostgreSQL for transactional work, Redshift and Snowflake as warehouses, and Spark SQL, Hive and Athena for querying files in a data lake. The core SQL is the same, the dialect details differ."

---

**Q. What is a schema? What properties does a schema have?**

**A. (Class answer)** *(no answer given)*

**Expanded:** "Schema" has two meanings:
1. **The structure of the data:** table and column names, **data types**, **nullability**, **constraints** (primary key, foreign keys, unique, check, default) and relationships. In Spark, a DataFrame's schema is a `StructType` of fields.
2. **A namespace** inside a database that groups tables, views and other objects (for example `bronze.trips` vs `gold.fact_trips` in Postgres, Redshift or Snowflake), often used for permissions.

Related terms: **schema-on-write** (warehouse: data must fit the schema when it's loaded) vs **schema-on-read** (data lake: the schema is applied when reading), and **schema evolution** (adding or changing columns safely over time).

See [Training 4 notes](/training-notes-site/notes/training-4/) ("SQL Data Types & Rules") and [Training 6 notes](/training-notes-site/notes/training-6/) ("Schema Evolution: Beyond Avro").

**Say it out loud:** "A schema defines the structure of the data, its tables, columns, types, nullability and constraints like primary and foreign keys. The word also means a namespace that groups tables inside a database, like separate bronze and gold schemas."

---

**Q. What is structured data?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Structured data follows a **fixed, predefined schema** of rows and columns with known types, so it can be stored in tables and queried directly with SQL. Examples: relational tables, CSVs with consistent columns, Parquet files. Contrast with semi-structured data (JSON, XML) and unstructured data (images, text). See the "Structured data vs unstructured data vs semistructured data" question in General Programming.

**Say it out loud:** "Structured data has a fixed schema of rows and columns with known types, like a database table, so it can be queried directly with SQL."

---

**Q. What is T-SQL**

**A. (Class answer)** *(no answer given)*

**Expanded:** T-SQL (Transact-SQL) is **Microsoft's SQL dialect**, used by **SQL Server, Azure SQL and Azure Synapse**. It adds procedural features to standard SQL: variables (`DECLARE @x INT`), `IF`/`WHILE`, `TRY...CATCH` error handling, stored procedures, functions and triggers. Dialect quirks: `SELECT TOP 10` instead of `LIMIT 10`, `GETDATE()`, square brackets around names.

See [Training 31 notes](/training-notes-site/notes/training-31/) ("Azure Synapse Analytics").

**Say it out loud:** "T-SQL is Microsoft's SQL dialect for SQL Server, Azure SQL and Synapse. It adds procedural features like variables, control flow, error handling and stored procedures, and has quirks like `TOP` instead of `LIMIT`."

---

**Q. What is PL/SQL**

**A. (Class answer)** *(no answer given)*

**Expanded:** PL/SQL (Procedural Language/SQL) is **Oracle's** procedural extension of SQL. Code is organized in **blocks** (`DECLARE ... BEGIN ... EXCEPTION ... END`) and supports variables, loops, cursors, exception handling, stored procedures, functions, triggers and **packages**. PostgreSQL's equivalent is PL/pgSQL, and Microsoft's is T-SQL.

**Say it out loud:** "PL/SQL is Oracle's procedural extension of SQL, with blocks, variables, loops, cursors and exception handling, used for stored procedures, triggers and packages. It's Oracle's counterpart to Microsoft's T-SQL."

---

**Q. What is a window function?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A window function computes a value **across a set of rows related to the current row** without collapsing them the way `GROUP BY` does. Every input row stays in the output.

```sql
SELECT station_id, snapshot_ts, bikes,
       AVG(bikes) OVER (PARTITION BY station_id)                          AS station_avg,
       LAG(bikes) OVER (PARTITION BY station_id ORDER BY snapshot_ts)     AS prev_bikes,
       SUM(bikes) OVER (PARTITION BY station_id ORDER BY snapshot_ts
                        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)         AS rolling_7
FROM trips;
```

| Part | Role |
|---|---|
| `PARTITION BY` | Splits rows into groups (like GROUP BY, but rows are kept) |
| `ORDER BY` | Order within each partition |
| Frame (`ROWS BETWEEN ...`) | Which nearby rows to include, for running totals and moving averages |

Families: ranking (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`), offset (`LAG`, `LEAD`, `FIRST_VALUE`), and aggregates used with `OVER`. Typical uses: top-N per group, de-duplication, running totals, change since previous row. The same exists in Spark through `Window`.

See [Training 4 notes](/training-notes-site/notes/training-4/) ("Subqueries, CTEs & Window Functions") and [Training 7 notes](/training-notes-site/notes/training-7/) ("Window Functions").

**Say it out loud:** "A window function calculates across a set of related rows, defined by `PARTITION BY` and `ORDER BY`, but keeps every row, unlike `GROUP BY`. I use it for top-N per group, de-duplication with `ROW_NUMBER`, running totals and `LAG` comparisons."

---

**Q. What's the difference between rank and dense_rank?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Both give tied rows the same rank. The difference is what comes **after** a tie: `RANK` **skips** numbers, `DENSE_RANK` doesn't. `ROW_NUMBER` never ties.

| Salary | ROW_NUMBER | RANK | DENSE_RANK |
|---|---|---|---|
| 100 | 1 | 1 | 1 |
| 90 | 2 | 2 | 2 |
| 90 | 3 | 2 | 2 |
| 80 | 4 | **4** | **3** |

For "Nth highest salary" questions use `DENSE_RANK`, so ties don't create gaps.

See [Training 4 notes](/training-notes-site/notes/training-4/) ("Nth-Highest-Per-Group: RANK / DENSE_RANK / ROW_NUMBER (Common Interview Question)").

**Say it out loud:** "Both give ties the same rank, but `RANK` then skips numbers, so 1, 2, 2, 4, while `DENSE_RANK` doesn't, so 1, 2, 2, 3. For nth-highest questions I use `DENSE_RANK`."

---

**Q. What's an index**

**A. (Class answer)** *(no answer given)*

**Expanded:** An index is a separate data structure, usually a **B-tree**, that maps column values to row locations so the database can find matching rows **without scanning the whole table**: about O(log n) instead of O(n). Cost: extra storage, and slower `INSERT`/`UPDATE`/`DELETE`, because every index must be updated. Index columns that are often filtered, joined or sorted on, especially with high selectivity. Check usage with `EXPLAIN ANALYZE`. Analytical warehouses mostly don't use B-tree indexes: they rely on columnar storage, **sort keys** and partition pruning instead (Redshift sort keys, Snowflake micro-partitions and clustering keys).

See [Training 4 notes](/training-notes-site/notes/training-4/) ("Indexing & Query Plans (EXPLAIN ANALYZE)").

**Say it out loud:** "An index is a structure, usually a B-tree, that lets the database find rows by a column's value without a full table scan. It speeds up reads at the cost of storage and slower writes, so I index columns used in filters and joins and check with `EXPLAIN ANALYZE`."

---

**Q. Clustered vs non clustered index**

**A. (Class answer)** *(no answer given)*

**Expanded:**

| | Clustered index | Non-clustered index |
|---|---|---|
| What it is | The table's rows are **physically stored in the index's key order**; the leaf level *is* the data | A separate structure with key values and **pointers** to the rows |
| How many | **One** per table | Many |
| Best for | Range scans and ordered reads on the key | Lookups on other columns |
| Typical default | The primary key (SQL Server, MySQL InnoDB) | Secondary indexes |

Postgres note: Postgres tables are heaps and all indexes are non-clustered. The `CLUSTER` command reorders a table once but doesn't keep it ordered.

**Say it out loud:** "A clustered index stores the table's rows physically in key order, so there can only be one, usually on the primary key. A non-clustered index is a separate structure that points to the rows, and you can have many."

---

**Q. What is normalization?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Normalization organizes a relational schema to **reduce redundancy and prevent update anomalies** (insert, update and delete anomalies) by splitting data into related tables linked by keys, so each fact is stored once. It suits **OLTP** systems with frequent writes. **Denormalization** goes the other way for analytics: star schemas deliberately repeat data in wide dimension tables so queries need fewer joins.

See [Training 5 notes](/training-notes-site/notes/training-5/) ("Database Normalization").

**Say it out loud:** "Normalization splits data into related tables so each fact is stored only once, which prevents update anomalies. It's right for transactional systems, while warehouses deliberately denormalize into star schemas for faster reads."

---

**Q. What are the normal forms?**

**A. (Class answer)** *(no answer given)*

**Expanded:**

| Form | Rule | Violation example |
|---|---|---|
| 1NF | Atomic values, no repeating groups, each row unique | A `phones` column holding "555-1, 555-2" |
| 2NF | 1NF + every non-key column depends on the **whole** primary key (no partial dependency on part of a composite key) | In `(order_id, product_id) → product_name`, the name depends only on `product_id` |
| 3NF | 2NF + no **transitive** dependencies (non-key columns depend only on the key) | `customer_id → zip → city`: city depends on zip |
| BCNF | Every determinant is a candidate key (stricter 3NF) | Rare edge cases |

Memory line: every non-key column depends on "the key, the whole key, and nothing but the key". In practice, 3NF is the usual target for OLTP.

See [Training 5 notes](/training-notes-site/notes/training-5/) ("Normal Forms").

**Say it out loud:** "1NF means atomic values and no repeating groups, 2NF removes partial dependencies on part of a composite key, and 3NF removes transitive dependencies, so every column depends on the key, the whole key and nothing but the key."

---

**Q. What are ACID transactions?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Same question as in General Programming above: **Atomicity** (all or nothing), **Consistency** (constraints always hold), **Isolation** (concurrent transactions don't see each other's partial work) and **Durability** (committed changes survive crashes). SQL angle:

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;   -- or ROLLBACK; on error, neither update is kept
```

Isolation levels, from weakest to strongest: read uncommitted, read committed (the Postgres default), repeatable read, serializable.

See [Training 5 notes](/training-notes-site/notes/training-5/).

**Say it out loud:** "ACID is atomicity, consistency, isolation and durability. In SQL, wrapping both sides of a transfer in `BEGIN` and `COMMIT` means either both updates happen or neither does."

---

**Q. What are CRUD operations?**

**A. (Class answer)** *(no answer given)*

**Expanded:**

| CRUD | SQL | HTTP (REST) |
|---|---|---|
| Create | `INSERT` | POST |
| Read | `SELECT` | GET |
| Update | `UPDATE` | PUT / PATCH |
| Delete | `DELETE` | DELETE |

Data engineering adds **upsert** (`MERGE` / `INSERT ... ON CONFLICT`), which combines create and update. It is the core of incremental loads and CDC.

See [Training 4 notes](/training-notes-site/notes/training-4/) ("INSERT & SELECT Basics").

**Say it out loud:** "CRUD is create, read, update and delete, which map to `INSERT`, `SELECT`, `UPDATE` and `DELETE` in SQL and to POST, GET, PUT and DELETE in REST. In pipelines we also use upserts with `MERGE`."

---

**Q. What is a primary key?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A primary key is the column (or set of columns, a **composite key**) that **uniquely identifies each row**. It must be **unique and NOT NULL**, and there is one per table. Most databases automatically create an index for it. A **foreign key** in another table references it, which enforces referential integrity. Key types: **natural/business key** (an email, an order number from the source) vs **surrogate key** (a generated ID with no business meaning, used in warehouse dimensions and needed for SCD Type 2). Note: Redshift, Snowflake and BigQuery accept primary key declarations but **don't enforce** them, so pipelines must de-duplicate themselves.

See [Training 4 notes](/training-notes-site/notes/training-4/) ("Primary Keys & Foreign Keys") and [Training 5 notes](/training-notes-site/notes/training-5/) ("Surrogate Keys").

**Say it out loud:** "A primary key uniquely identifies each row; it has to be unique and not null, and other tables reference it with foreign keys. In warehouses we often use surrogate keys, and since Redshift and Snowflake don't enforce primary keys, the pipeline has to de-duplicate."

---

**Q. When to use a materialized view**

**A. (Class answer)** *(no answer given)*

**Expanded:** A regular view is a stored query that runs every time you read it. A **materialized view stores the query's result**, so reads are fast but the result must be **refreshed** to stay current.

Use one when:
- An expensive query (big joins and aggregations) is read **much more often** than the source data changes, such as dashboards and summary tables.
- Some staleness is acceptable, or the platform refreshes it incrementally.

Avoid it when the data must be exactly current on every read, or the source changes constantly and refreshes would cost more than they save.

| Platform | Refresh |
|---|---|
| PostgreSQL | Manual `REFRESH MATERIALIZED VIEW` (`CONCURRENTLY` avoids blocking readers) |
| Redshift | `REFRESH`, or auto-refresh, incremental where possible |
| Snowflake | Maintained automatically (Enterprise edition); **dynamic tables** are the more flexible option |
| dbt | `materialized='table'` or `'incremental'` models play the same role |

See [Training 16 notes](/training-notes-site/notes/training-16/) ("Snowflake Dynamic Tables" and its "Why not just use a view?" section).

**Say it out loud:** "A materialized view stores a query's results, so I'd use it for expensive aggregations read far more often than the data changes, like dashboard summaries. The trade-off is that it has to be refreshed, so it can be slightly stale."

---

**Q. What is Change Data Capture?**

**A. (Class answer)** *(no answer given)*

**Expanded:** CDC captures **row-level changes** (inserts, updates, deletes) in a source database as they happen and delivers them downstream, so you move **only what changed** instead of reloading whole tables.

| Approach | How | Pros / cons |
|---|---|---|
| **Log-based** (preferred) | Read the database's transaction log (Postgres WAL, MySQL binlog) | Captures deletes, low load on the source, near real-time. Needs log access |
| Query-based | Poll with `WHERE updated_at > last_watermark` | Simple. Misses hard deletes, needs a reliable timestamp column |
| Trigger-based | Triggers write changes to an audit table | Works anywhere, but adds load on every write |

Tools: **Debezium** (into Kafka), **AWS DMS** (full load + ongoing CDC), Fivetran, Snowflake Streams, Delta Lake Change Data Feed. Downstream, changes are applied with **`MERGE`** (upsert) into the target, ordered by the source's log position.

See [Training 24 notes](/training-notes-site/notes/training-24/) ("CDC and AWS DMS") and [Training 12 notes](/training-notes-site/notes/training-12/) ("Incremental Loads and CDC").

**Say it out loud:** "CDC captures inserts, updates and deletes from a source database as they happen, ideally by reading its transaction log with a tool like Debezium or DMS, and then applies them downstream with a `MERGE`. It avoids full reloads and captures deletes, which timestamp polling misses."

---

**Q. What are slowly changing dimensions - type 1, type 2, type 3**

**A. (Class answer)** *(no answer given)*

**Expanded:** An SCD is a dimension whose attributes change occasionally (a customer moves city). The type says how you handle history:

| Type | How | History kept | Example |
|---|---|---|---|
| 0 | Never change the value | Original only | Date of birth |
| 1 | **Overwrite** the old value | None | Fix a typo in a name |
| 2 | **Add a new row** per change, with `valid_from`, `valid_to`, `is_current` and a new **surrogate key** | Full history | Customer moves: old row closed, new row current |
| 3 | **Add a column** for the previous value (`current_city`, `previous_city`) | Only the last change | Sales territory reassignment |

Type 2 is the one interviewers focus on. Facts join to the dimension's surrogate key, so old facts keep pointing to the old version. It is implemented with `MERGE` (close the current row, insert the new one), or with dbt **snapshots**.

See [Training 5 notes](/training-notes-site/notes/training-5/) ("Surrogate Keys & Slowly Changing Dimensions (SCD)").

**Say it out loud:** "Type 1 overwrites the value, so there's no history. Type 2 adds a new row with a new surrogate key and validity dates for each change, so full history is kept. Type 3 adds a 'previous value' column, so only the last change is kept. Type 2 is the most common for things like customer address."

---


## Git


**Q. What is Git?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Git is a **distributed version control system** created by Linus Torvalds in 2005. It tracks changes to files as a history of **commits** (snapshots identified by a SHA hash). Every developer has the **full repository and history locally**, so most operations are fast and work offline. It supports cheap **branching and merging** for parallel work. Git is the tool; GitHub, GitLab and Bitbucket are **hosting services** for Git repositories that add pull requests, CI/CD and permissions.

Three areas to know: the **working directory** (your files), the **staging area / index** (`git add`), and the **repository** (`git commit`), plus the **remote** (`git push`).

See [Training 3 notes](/training-notes-site/notes/training-3/) ("Git Background").

**Say it out loud:** "Git is a distributed version control system: it records the project's history as commits, every clone has the full history, and branches make parallel work easy. GitHub and GitLab are hosting services built around it."

---

**Q. Which remote repository services have you used?**

**A. (Class answer)**

Good answers include Github, Bitbucket, Gitlab, AWS Code Commit.

**Expanded:** The teacher's list is good, with one update: **AWS CodeCommit was closed to new customers in July 2024**, so mention it only if you used it. Also valid: **Azure Repos** (Azure DevOps). Mention what you did there: pull requests and code review, branch protection rules, CI pipelines (GitHub Actions, GitLab CI).

**Say it out loud:** "Mainly GitHub, for pull requests, code reviews, branch protection and GitHub Actions CI. I'm also familiar with GitLab and Bitbucket, which work the same way."

---

**Q. What are the steps in committing files to a git repo?**

**A. (Class answer)**

Committing files to a Git repo involves the following steps:

1. Use the command `git add .` or `git add -A` in order to add the files to the shelf.
2. Use the command `git commit -m 'my message here'` to commit the files and add a commit message.
3. Use the command `git push origin my_branch` to push the changes to the branch of your choice.

The repository that it will push to is determined by the remote origin settings, which you can configure on the CLI.

**Expanded:**

**Correction:** `git add` adds files to the **staging area** (also called the **index**), not "the shelf" ("shelve" is a JetBrains IDE feature, closer to `git stash`). Also, committing and pushing are separate: `git commit` saves the snapshot to your **local** repository, and `git push` sends commits to the **remote**. A fuller workflow:

```bash
git status                      # see what changed
git checkout -b feature/add-dim-date   # work on a branch (or git switch -c)
git add path/to/file.py         # stage specific files (git add . stages everything)
git commit -m "Add dim_date load"      # snapshot into the local repo
git pull --rebase origin main   # optional: bring in the latest main first
git push -u origin feature/add-dim-date   # publish the branch
```

Then open a pull request. Prefer staging specific files over `git add .` so you don't commit secrets or junk (use `.gitignore`).

See [Training 3 notes](/training-notes-site/notes/training-3/) ("Git Background", "Commits" and "Core Git Operations").

**Say it out loud:** "I check `git status`, stage the files with `git add` into the staging area, commit them locally with a clear message, then `git push` the branch to the remote and open a pull request."

---

**Q. How do you move code from one git branch to another?**

**A. (Class answer)**

Use a pull request, featured in the GUI of the repository service that you are using. After you initiate the PR, then you can merge the branches.

**Expanded:** A pull request is the right answer for team workflows on a hosting service. But a PR is a **GitHub/GitLab feature**, not part of Git. In Git itself:

| Command | What it does | When |
|---|---|---|
| `git merge feature` | Combines the branch's history into the current branch (may create a merge commit) | Standard integration, keeps history as it happened |
| `git rebase main` | Replays your commits on top of another branch for a linear history | Updating a feature branch. Don't rebase shared branches |
| `git cherry-pick <sha>` | Copies specific commits onto the current branch | A hotfix needed on another branch |
| Pull request | Review + CI checks + merge (merge commit, squash or rebase) | Team workflow to `main` |

See [Training 3 notes](/training-notes-site/notes/training-3/) ("Pull Requests", "Merge Conflicts" and "Core Git Operations").

**Say it out loud:** "On a team, I open a pull request so the change is reviewed and tested before merging. Under the hood that's `git merge`, and I also use `rebase` to update my branch and `cherry-pick` to copy a single commit, like a hotfix."

---

**Q. What is a branch?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A branch is a **movable pointer to a commit**, an independent line of development. Creating one is instant and cheap (it's just a reference), and each new commit on it moves the pointer forward. `HEAD` points to the branch you're on. Branches let you develop features, fixes and experiments in isolation without breaking `main`, then merge them through a pull request. Strategies: **feature branches** with **trunk-based development** (short-lived branches merged often) or **Git Flow** (`main`, `develop`, `feature/*`, `release/*`, `hotfix/*`).

See [Training 3 notes](/training-notes-site/notes/training-3/) ("Branching") and [Training 0 notes](/training-notes-site/notes/training-0/) ("What is Git Flow, and how does branching work in a team?").

**Say it out loud:** "A branch is a lightweight, movable pointer to a commit, so I can develop a feature in isolation from main and merge it back through a pull request. We used short-lived feature branches."

---

**Q. What is a pull request?**

**A. (Class answer)** *(no answer given)*

*(Teacher's section notes, verbatim:)*

*Note: Git and repository services like Github, Gitlab, and Bitbucket are separate things.*
*Note: Git was invented by Linus Torvalds, who is also the inventor of Linux.*

**Expanded:** A pull request (GitLab calls it a **merge request**) is a request, made on a hosting service like GitHub, to **merge one branch into another**. It shows the diff, lets teammates **review and comment**, runs **automated CI checks** (tests, linting), and is merged only when approvals and checks pass (enforced with **branch protection**). Merge options: merge commit, squash, or rebase. Good PRs are small, focused, and describe what changed and why. The teacher's notes are right: Git and hosting services are separate things, and Linus Torvalds created both Git and Linux.

See [Training 3 notes](/training-notes-site/notes/training-3/) ("Pull Requests" and "Code Review").

**Say it out loud:** "A pull request asks to merge my branch into another, usually main. Teammates review the diff, CI runs the tests, and it's merged once approved, so nothing reaches main without review and passing checks."

---


## Testing


**Q. What is a unit test?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A unit test checks **one small unit of code (a function or class) in isolation**, quickly and automatically, with known inputs and expected outputs. External dependencies (databases, APIs, S3) are replaced with **mocks or fakes**. Unit tests run on every commit in CI. For data engineering: test transformation functions with a tiny DataFrame built in the test.

```python
# test_transform.py
from transform import add_tax

def test_add_tax():
    assert add_tax(100, 0.1) == 110

def test_clean_trips(spark):              # spark fixture from conftest.py
    df = spark.createDataFrame([("S1", None), ("S2", 5)], "station string, bikes int")
    assert clean_trips(df).count() == 1   # rows with null bikes dropped
```

See [Training 3 notes](/training-notes-site/notes/training-3/) ("CI/CD Pipeline Stages", the `test_math_utils.py` example).

**Say it out loud:** "A unit test checks one function in isolation with known inputs and expected outputs, mocking things like databases. For Spark code I build a tiny DataFrame in the test and assert on the output, and they run automatically in CI."

---

**Q. What unit testing frameworks have you used?**

**A. (Class answer)**

- Python: Pytest, Unittest
- Scala: Scalatest

**Expanded:** The teacher's list is correct. Details worth adding:

| Language | Framework | Notes |
|---|---|---|
| Python | **pytest** | Plain `assert`, **fixtures** (e.g. a shared SparkSession in `conftest.py`), `parametrize`. The most common choice |
| Python | unittest | Standard library, class-based (`TestCase`) |
| Python | `unittest.mock`, moto | Mocking; moto fakes AWS services for boto3 |
| Scala | **ScalaTest** | Styles like `AnyFunSuite`; run with `sbt test` |
| Java | JUnit | |
| Data | dbt tests, Great Expectations, Spark's `assertDataFrameEqual` (Spark 3.5+) | Data quality and DataFrame comparison |

See [Training 3 notes](/training-notes-site/notes/training-3/).

**Say it out loud:** "Mainly pytest for Python, with fixtures for a shared SparkSession and moto to mock AWS calls, and ScalaTest for Scala. For data quality I use dbt tests."

---

**Q. What is an integration test?**

**A. (Class answer)** *(no answer given)*

**Expanded:** See "What are integration tests?" in the CI/CD section above. In short: an integration test checks that **multiple components work together** with real or realistic dependencies, for example a pipeline reading from a Postgres container and writing to a test bucket, then asserting on the result. It's slower and less frequent than unit tests.

**Say it out loud:** "An integration test checks that components work together, like my job reading from a real test database and writing to a test bucket, rather than testing one function in isolation."

---

**Q. What is test driven development?**

**A. (Class answer)** *(no answer given)*

**Expanded:** Test-driven development (TDD) means **writing the test before the code**, in a short cycle:
1. **Red:** write a test for the next small behavior. It fails.
2. **Green:** write the minimum code to make it pass.
3. **Refactor:** clean up the code while keeping the tests passing.

Benefits: clear requirements, high test coverage, better design (testable code) and safe refactoring. In data engineering, a practical form is writing the expected output for a sample input first (or the dbt test first), then building the transformation.

**Say it out loud:** "TDD means writing a failing test first, then the minimum code to pass it, then refactoring, the red-green-refactor cycle. It gives clear requirements and safe refactoring."

---


## General / Code Challenges


**Q. What was the data pipeline for your most recent project?**

**A. (Class answer)** *(no answer given)*

**Expanded:** This is the most important question in the interview. Prepare a **two-minute story** that goes **source → ingestion → storage layers → transformation → serving → orchestration → monitoring**, with concrete tools, data sizes and one problem you solved. A template built on the class's Citi Bike project:

| Stage | Example answer |
|---|---|
| Source | Citi Bike GBFS REST API (station status and information) |
| Ingestion | Python job scheduled every few minutes, writing raw JSON to S3 Bronze, partitioned by date |
| Transformation | Glue Spark job: Bronze → Silver Parquet (flatten, type, de-duplicate) |
| Warehouse | Redshift Gold star schema: `fact_station_status`, `dim_station`, `dim_date`, loaded incrementally with `COPY` + `MERGE` |
| Orchestration | Step Functions triggered by EventBridge Scheduler, defined in Terraform |
| Serving | Streamlit dashboard, plus a text-to-SQL chatbot with Bedrock |
| Monitoring | CloudWatch alarms and SNS alerts, row count checks |

See [Training 19 notes](/training-notes-site/notes/training-19/), [Training 20 notes](/training-notes-site/notes/training-20/), [Training 21 notes](/training-notes-site/notes/training-21/), [Training 24 notes](/training-notes-site/notes/training-24/) ("The final architecture") and [Training 29 notes](/training-notes-site/notes/training-29/) ("Profile Narratives & Interviews").

**Say it out loud:** "We ingested the Citi Bike station feed from its REST API into S3 as raw JSON, used a Glue Spark job to clean it into Silver Parquet, and loaded a star schema in Redshift incrementally with a MERGE. Step Functions orchestrated it on an EventBridge schedule, all defined in Terraform, and a Streamlit dashboard served the results."

---

**Q. Python code challenge 1 - given a simple function that is missing a return statement, can the FE determine what is wrong with the function?**

**A. (Class answer)** *(no answer given)*

**Expanded:** A function with no `return` statement returns **`None`**. So code like `total = add(2, 3)` gives `None`, and a later `total + 1` raises `TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'`. Spot it by reading the function (it prints or computes but never returns), then fix it:

```python
def add(a, b):
    result = a + b        # bug: computed but not returned
    # print(result) would display it, but the caller still gets None

def add(a, b):
    return a + b          # fix
```

Talk through your reasoning out loud: what you expect, what actually happens, and how you'd confirm it (run it, print the type, add a test). Other classic bugs in these exercises: mutable default arguments (`def f(x=[])`), `return` inside the loop so it exits on the first item, integer vs float division, and off-by-one ranges.

See [Training 29 notes](/training-notes-site/notes/training-29/) ("Coding tests").

**Say it out loud:** "The function never returns its result, so Python returns `None` and the caller gets `None`, which fails as soon as it's used. The fix is to `return` the value instead of only computing or printing it."

---

**Q. Python code challenge 2**

**A. (Class answer)** *(no answer given)*

**Expanded:** The content isn't given in the source. Prepare the common data engineering Python exercises:
- Count word or item frequencies (`collections.Counter`, or a dict).
- Remove duplicates while keeping order (`list(dict.fromkeys(items))`).
- Find the second largest or top N values (handle duplicates and short lists).
- Reverse a string, check a palindrome, find anagrams.
- Flatten a nested list or nested JSON.
- Merge two sorted lists, or group records by key.
- FizzBuzz, two-sum (use a dict for O(n)).
- Parse a CSV or log file and aggregate, ideally with a generator.
- Small pandas or PySpark tasks: group by, join, de-duplicate with a window.

Approach: restate the problem, ask about edge cases (empty input, duplicates, types), write a simple correct version first, test it with an example, then discuss complexity and improvements.

See [Training 2 notes](/training-notes-site/notes/training-2/) ("Core Python for Interviews") and [Training 29 notes](/training-notes-site/notes/training-29/) ("Coding tests").

**Say it out loud:** "I'd restate the problem, check edge cases like empty input or duplicates, write a simple working solution and test it with an example, then talk about its Big O and how to improve it."

---

**Q. Scala code challenge 1**

**A. (Class answer)** *(no answer given)*

**Expanded:** The content isn't given in the source. Typical Scala exercises test functional style on collections:
- Transform a `List` with `map`, `filter`, `flatMap`, `foldLeft` instead of loops and `var`s.
- Word count: `text.split("\\s+").groupBy(identity).view.mapValues(_.length).toMap`.
- Handle missing values with `Option` (`getOrElse`, `map`, pattern matching) rather than `null`.
- Write a case class and pattern match on it.
- Recursion (factorial, Fibonacci) with `@tailrec`.
- A small Spark Dataset task with a case class.

Common bugs you may be asked to find: a missing `=` before a method body (so it returns `Unit`), forgetting that the last expression is the return value, using `var` and mutation where `val` is expected, non-exhaustive `match`.

See [Training 10 notes](/training-notes-site/notes/training-10/) ("Scala Basics the Class Skipped (Roadmap Topics)").

**Say it out loud:** "In Scala I'd solve it functionally: immutable `val`s, collection methods like `map`, `filter` and `foldLeft`, `Option` for missing values and pattern matching on case classes, then test it on a small example."

---

**Q. Scala code challenge 2**

**A. (Class answer)** *(no answer given)*

**Expanded:** The content isn't given in the source. Prepare the same set as Scala challenge 1, plus:
- Implement `groupBy`-style aggregation with `foldLeft` into a `Map`.
- Model outcomes with a `sealed trait` and exhaustive matching.
- Chain `Future`s or `Option`s with a for-comprehension.
- Explain the output of a snippet that uses `lazy val`, `implicit` parameters or trait linearization.

**Say it out loud:** "I'd talk through it step by step, write it with immutable values and collection functions, use Option or a sealed trait to handle edge cases, and check it against an example."

---

