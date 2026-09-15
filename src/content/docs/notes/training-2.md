---
title: Training 2 - Python and Pandas
description: Python background, loops, functions, exceptions, logging, and Pandas DataFrames - concepts and worked examples
---

Teacher: Evan Flint

Syllabus Day 3: Python + Pandas
Coverage: Functions, exceptions, logging, file I/O, JSON/CSV, DataFrames, filtering, joins, and small ETL.

## Video Resources

| Video | Purpose | Link |
|---|---|---|
| you need to learn Python RIGHT NOW!! // EP 1 | Fast-paced intro/motivation video for getting started with Python | https://www.youtube.com/watch?v=mRMmlo_Uqcs |
| Python Tutorial: CSV Module - How to Read, Parse, and Write CSV Files | Covers Python's built-in `csv` module (`DictReader`, etc.) - directly relevant to the JSON/CSV and File I/O sections below | https://www.youtube.com/watch?v=q5uM4VKywbA |

## References

| Resource | Purpose | Link |
|---|---|---|
| Automate the Boring Stuff with Python (3rd Edition) | Free, well-known Python book. Chapter 4 (Functions), Chapter 10 (basics of working with files), and Chapter 18 (working with data files) map directly to this training's Functions, File I/O, and JSON/CSV sections | https://automatetheboringstuff.com/3e/ |
| Pandas Getting Started Tutorials | Official beginner-friendly walkthroughs of core Pandas concepts (reading data, selecting subsets, plotting, etc.) | https://pandas.pydata.org/docs/getting_started/intro_tutorials/ |
| Pandas API Reference | Full official reference for every Pandas function/method (`groupby`, `cut`, `unstack`, `sort_values`, and everything else in the DataFrames section below) - the place to look up exact arguments and behavior | https://pandas.pydata.org/docs/reference/ |

# Python Background

Q. What is the difference between compiled and interpreted languages?

A. Compiled languages translate the entire source code into machine code (binary) before it runs, via a separate build step. Interpreted languages are read and executed line-by-line by an interpreter program at runtime, with no separate machine-code build step.

| | Compiled | Interpreted |
|---|---|---|
| Execution | Source -> compiler -> machine code -> run the binary | Source -> interpreter reads/executes it directly |
| Speed | Faster at runtime (already machine code) | Slower at runtime (translated on the fly) |
| Build step | Required (compile first, then run) | None - run the source file directly |
| Error discovery | Many errors caught at compile time, before running | Errors often only surface when that line actually executes |
| Portability | Compiled binary is platform-specific (needs recompiling per OS/CPU) | Same source runs anywhere the interpreter is installed |
| Examples | C, C++, Rust, Go, Java* | Python, JavaScript, Ruby, PHP |

*Java is a middle case: it compiles to bytecode, then the JVM interprets/JIT-compiles that bytecode - this hybrid model is common (Python does something similar internally with `.pyc` bytecode caching).

Why this matters for Python specifically: Python is interpreted, which is exactly why you can run a script immediately with `python script.py` with no separate build step - but it's also part of why Python is generally slower than a compiled language like C for raw computation. This tradeoff (developer speed/ease vs. raw execution speed) is a big part of why performance-critical Python libraries (NumPy, Pandas) are actually implemented in C/C++ underneath.

Q. Java vs Python - what's the difference?

A. | | Java | Python |
|---|---|---|
| Execution model | Compiles to bytecode, run by the JVM (compile + interpret hybrid) | Interpreted directly (with internal bytecode caching, but no separate compile step for the developer) |
| Typing | Statically typed - variable types declared and checked at compile time | Dynamically typed - types checked at runtime, not declared upfront |
| Syntax verbosity | More verbose (explicit types, class boilerplate, semicolons, curly braces) | Concise, readable syntax - whitespace/indentation defines blocks |
| Speed | Generally faster (JIT-compiled bytecode, static typing enables more optimization) | Generally slower for raw computation (dynamic typing, interpreted line-by-line) |
| Error catching | Many type/syntax errors caught at compile time before running | Most errors only surface at runtime, when that code path executes |
| Common use cases | Large enterprise systems, Android apps, backend services requiring performance/scale | Data engineering/science, scripting, automation, rapid prototyping, AI/ML |
| Ecosystem relevant here | Spark and Hadoop were originally written in Java/Scala (JVM languages) | PySpark is Python's interface to Spark; Pandas, NumPy for data manipulation |

Why this matters for data engineering: Spark itself runs on the JVM (written in Scala, which compiles to Java bytecode) - that's why Spark has both a native Scala/Java API and a Python API (PySpark). PySpark is genuinely slower in some cases than native Scala/Java Spark code because of the overhead of passing data between the Python process and the JVM - something worth knowing if performance ever comes up in an interview.

Q. Can Python be statically typed?

A. Not natively - but it can be checked statically with optional tooling. Python is fundamentally dynamically typed - the interpreter itself never checks or enforces types before running code; a variable can hold any type, and type errors only surface at runtime when the offending line executes.

Python supports optional type hints (PEP 484, via the `typing` module) that annotate expected types:
```python
def add(a: int, b: int) -> int:
    return a + b
```

The key catch: these hints are NOT enforced by Python itself at runtime - calling `add("hello", "world")` still runs (Python won't stop it just because the hints say `int`). The hints only become real static type checking when a separate external tool analyzes the code against them:

| Tool | What it does |
|---|---|
| `mypy` | The most common static type checker for Python - analyzes code against its type hints without running it, flags mismatches |
| `pyright` / Pylance | Microsoft's type checker, used by VS Code's IntelliSense |
| `ruff` | Can also do some type-adjacent linting |

Accurate description: Python is dynamically typed, with optional static type checking available via external tools - not statically typed the way Java is, where the compiler itself refuses to build the code if types don't match.

Q. Where should Python packages be installed from?

A. PyPI (pypi.org) - the Python Package Index - is the official, trusted source for third-party Python packages. It's the default registry `pip install <package>` pulls from.

| | Detail |
|---|---|
| What it is | The official public repository of Python packages, hosted by the Python Software Foundation |
| Default behavior | `pip install <package>` automatically pulls from pypi.org unless configured otherwise |
| Why "trusted" matters | Anyone can publish a package to PyPI - always double-check a package name is spelled correctly and matches the real project (typosquatting - malicious packages with names similar to popular ones - is a real supply-chain risk) |
| Verifying a package | Check the project's PyPI page for download counts, GitHub link, maintainer activity, and recent updates before installing something unfamiliar |
| Private/internal packages | Companies often run their own private package index (e.g. via Artifactory, AWS CodeArtifact) for internal-only packages, configured as an additional or alternate source for pip |

Q. What is threading in Python, and how does it relate to big data processing?

A. Python has a `threading` module for running multiple threads concurrently, but there's a critical catch: the GIL (Global Interpreter Lock). Only one thread can execute Python bytecode at a time in CPython (the standard Python implementation), even on a multi-core machine - so Python threading does NOT give true parallel execution for CPU-bound work.

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

| Workload type | Does Python threading help? |
|---|---|
| I/O-bound (waiting on network, disk, database) | Yes - threads release the GIL while waiting, so this works well |
| CPU-bound (heavy computation/data processing) | No - the GIL serializes execution, threads don't add real parallelism |

For CPU-bound parallelism in plain Python, `multiprocessing` is used instead (separate processes, each with its own GIL/interpreter) - but that has its own overhead (memory duplication, inter-process communication).

Why this matters for big data specifically: this is exactly why Spark doesn't rely on Python threads for its actual heavy lifting, even when writing PySpark code:
- Spark's core engine runs on the JVM (Scala/Java), which has real multi-threaded parallelism (no GIL) - this is where the actual distributed computation happens
- PySpark code mostly just builds instructions that get sent to the JVM to execute; the parallel processing across partitions/executors happens at the JVM/cluster level, not via Python threads
- This connects to the PySpark <-> JVM overhead already noted in the Java vs Python entry above - a worthwhile tradeoff since the actual parallel computation isn't limited by Python's GIL at all

Bottom line: Python's GIL is a real limitation for pure-Python concurrency, but it's largely irrelevant to Spark's actual distributed processing power, since that parallelism happens at the JVM/cluster/process level (multiple executors, each a separate OS process), not via Python threads within a single process.

Q. Worked example: multithreading vs multiprocessing

A. (Shared by the teacher) A side-by-side demo showing that threads share the same process (same PID, different thread IDs) while processes each get their own PID - directly demonstrating the GIL/JVM distinction above.

Note: the original had `if name == "main":` - missing the double underscores. Fixed below to `if __name__ == "__main__":`, which is the real Python idiom for "only run this if the file is executed directly, not imported."

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

What to notice in the output: all 3 threads print the **same PID** (same process) but different Thread IDs - confirming they share one process/interpreter (and therefore one GIL). All 3 processes print **different PIDs** - confirming each got its own independent process (and its own separate GIL/interpreter), which is why multiprocessing achieves true parallelism for CPU-bound work where threading can't.

---

# Loops

Q. How do you write a `for` loop and a `while` loop in Python?

A. A `for` loop iterates over a sequence (list, string, range, etc.) - runs once per item. A `while` loop repeats as long as a condition stays `True` - you control when it stops, not how many iterations up front.

`for` loop:
```python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

for i in range(5):        # 0, 1, 2, 3, 4
    print(i)

for i, fruit in enumerate(fruits):   # get index + value together
    print(i, fruit)
```

`while` loop:
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

When to use which:

| | `for` | `while` |
|---|---|---|
| Use when | You know what you're iterating over (a list, a range, a file's lines) | You're repeating until some condition changes (unknown number of iterations upfront) |
| Risk | Rare - bounded by the sequence length | Infinite loop if the condition never becomes `False` (and you forget a `break`) |
| Common keywords | `break` (exit early), `continue` (skip to next iteration) - both work in either loop type |

---

# Functions

Q. How do you define a function in Python?

A. ```python
def function_name(parameter1, parameter2):
    # function body
    result = parameter1 + parameter2
    return result

# calling it
answer = function_name(3, 4)
print(answer)   # 7
```

| Part | Meaning |
|---|---|
| `def` | Keyword that starts a function definition |
| `function_name` | The name you call it by later |
| `(parameter1, parameter2)` | Inputs the function accepts - optional, can have zero or many |
| `:` + indented block | Everything indented under the `def` line is the function's body |
| `return` | Sends a value back to whoever called the function (optional - a function with no `return` returns `None`) |

Common variations:
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

# Functional Tools (map, filter, reduce)

Q. What are `map`, `filter`, and `reduce` in Python?

A. They're higher-order functions - they take a function as an argument and apply it across a sequence, instead of writing a manual loop.

`map()` - transform every item, returns a new sequence of results:
```python
numbers = [1, 2, 3, 4]
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)   # [2, 4, 6, 8]
```

`filter()` - keep only items that pass a True/False test:
```python
numbers = [1, 2, 3, 4, 5, 6]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)   # [2, 4, 6]
```

`reduce()` - not a built-in, must be imported from `functools`. Repeatedly applies a function to pairs of items, reducing the whole sequence to a single value:
```python
from functools import reduce

numbers = [1, 2, 3, 4]
total = reduce(lambda acc, x: acc + x, numbers)
print(total)   # 10 (((1+2)+3)+4)
```

| Function | Input -> Output | Common use |
|---|---|---|
| `map(func, seq)` | Sequence -> Sequence (same length) | Transform every item (e.g. double every number) |
| `filter(func, seq)` | Sequence -> Sequence (same or shorter) | Keep only items matching a condition |
| `reduce(func, seq)` | Sequence -> single value | Aggregate into one result (sum, product, max) |

In practice: most Python developers today prefer list comprehensions over `map`/`filter` since they're generally considered more readable:
```python
doubled = [x * 2 for x in numbers]              # same as map()
evens = [x for x in numbers if x % 2 == 0]       # same as filter()
```
`reduce` doesn't have as clean a comprehension equivalent, so it still shows up more often, though a simple `sum()` or `for` loop is common for basic cases like the total above.

Q. Full worked example: map/filter/reduce on a realistic CSV-based ETL pipeline

A. (Shared by the teacher, ChatGPT-generated) A complete example combining CSV parsing, type conversion, filtering, transformation, and multiple aggregation patterns - given a 100-row `employee_id,name,department,salary,years_experience,active` dataset.

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

Walkthrough of the pipeline shape:

| Step | Tool used | What it does |
|---|---|---|
| Extract | `csv.DictReader` | Reads raw CSV text into a list of dicts (all values are strings at this point) |
| Transform (types) | `map(convert_employee, ...)` | Converts string fields to `int`/`float`/`bool` |
| Filter | `filter(is_high_earning_active_employee, ...)` | Keeps only active employees earning >= $70,000 |
| Transform (business logic) | `map(give_raise, ...)` | Applies a 5% raise, keeps the old salary for comparison |
| Aggregate (sum) | `reduce(..., 0)` | Totals the payroll across all filtered/raised employees |
| Aggregate (group-by) | `reduce(..., {})` | Builds a dict of department -> total payroll, using a dict as the accumulator |
| Aggregate (average) | Reuses the `reduce` sum, divided by count | Average salary across the filtered group |
| Pipeline version | Nested `map(filter(map(...)))` | Same E-T-F-T chain written as one nested expression instead of separate named variables |

Note: this maps directly onto ETL - step 2 is Extract, steps 3-5 are Transform (type conversion, filtering, business logic), and printing/aggregating the results plays the role of Load/reporting in a small-scale example.

# Booleans

Q. Are `True` and `False` case-sensitive in Python?

A. Yes - Python requires exactly `True` and `False` (capital first letter only). Lowercase `true`/`false` (JavaScript/JSON style) or all-caps `TRUE`/`FALSE` (SQL style) will raise a `NameError` - Python doesn't recognize them as anything.

```python
True    # correct - the boolean value
False   # correct - the boolean value

true    # NameError: name 'true' is not defined
false   # NameError: name 'false' is not defined
```

This trips people up coming from JavaScript/JSON (`true`/`false`, lowercase) or SQL (`TRUE`/`FALSE`, often case-insensitive) - Python's rule is specifically capitalized, nothing else.

# Conditionals

Q. How do `if`, `elif`, and `else` work in Python?

A. They form a conditional chain - Python checks each condition in order and runs the first block whose condition is `True`, skipping the rest.

```python
age = 20

if age < 13:
    print("Child")
elif age < 20:
    print("Teenager")
else:
    print("Adult")
```

| Keyword | Meaning |
|---|---|
| `if` | The first condition checked - required, every conditional chain starts here |
| `elif` | "else if" - checked only if all preceding conditions were `False`. Optional, can have zero or many |
| `else` | Catch-all - runs only if every `if`/`elif` above was `False`. Optional, at most one, always last |

Key behavior: as soon as one condition is `True`, its block runs and Python skips the rest of the chain entirely - even if a later condition would also be `True`.

```python
score = 85
if score >= 60:
    print("Pass")
elif score >= 90:
    print("This never prints - score >= 60 already matched above")
```

Comparison/logical operators commonly used in conditions: `==`, `!=`, `<`, `>`, `<=`, `>=`, combined with `and`, `or`, `not`.

```python
if age >= 18 and has_id:
    print("Allowed in")
```

There's also a one-line "ternary" conditional expression for simple cases:
```python
status = "Adult" if age >= 18 else "Minor"
```

Q. What is the default case for an `if` chain, and does Python have a `switch` statement?

A. The `else` block is the "default" - it only runs if every `if`/`elif` above it was `False`. It's Python's equivalent of a switch statement's `default` case.

```python
if age < 13:
    print("Child")
elif age < 20:
    print("Teenager")
else:
    print("Adult")   # the "default" - catches everything else
```

Python historically had no switch/case statement at all (unlike Java, C, or JavaScript) - people just used `if`/`elif`/`else` chains instead. Python 3.10+ added `match`/`case` (structural pattern matching), which serves a similar purpose:

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

| | `if`/`elif`/`else` | `match`/`case` (3.10+) |
|---|---|---|
| Default/catch-all | `else` | `case _:` (underscore = wildcard, matches anything) |
| Availability | All Python versions | Only Python 3.10 and later |
| Best for | General conditions, ranges, comparisons | Matching against specific values or patterns/shapes of data |

Q. What is the equivalency (equality) operator in Python?

A. `==` compares two values and returns `True` if they're equal, `False` otherwise.

```python
5 == 5          # True
5 == 6          # False
"cat" == "cat"  # True
"cat" == "dog"  # False
```

Don't confuse it with `=` (assignment, not comparison) - a very common beginner bug:
```python
x = 5     # assignment - x now holds 5
x == 5    # comparison - checks if x equals 5, returns True
```

| Operator | Meaning |
|---|---|
| `==` | Equal to (compares values) |
| `!=` | Not equal to |
| `is` | Identity comparison - checks if two variables point to the exact same object in memory, not just equal values |
| `is not` | The opposite of `is` |

The `==` vs `is` distinction matters - two variables can hold equal values but be different objects in memory:
```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b   # True  - same values
a is b   # False - different list objects in memory
```

# Exceptions & Error Handling

Q. Does Python have `finally`?

A. Yes - `finally` is part of Python's `try`/`except`/`finally` block, and it runs no matter what: whether the `try` succeeds, an exception is caught, or even if an exception isn't caught at all.

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Can't divide by zero!")
finally:
    print("This always runs.")
```

| Block | Runs when |
|---|---|
| `try` | Always attempted first |
| `except` | Only if a matching exception was raised in `try` |
| `else` | Only if `try` succeeded with no exception (optional, less commonly used) |
| `finally` | Always - success, caught exception, or even an uncaught exception re-raising after cleanup |

`finally` is used for cleanup code that must happen regardless of success or failure - closing a file, releasing a database connection, closing a network socket.

Note: this pattern is already covered in more depth in `Training 0.md`'s "How is error handling implemented in Python?" entry, including a full pandas/CSV example with specific exception types (FileNotFoundError, ValueError, etc.) - see that entry for the complete walkthrough.

Q. Worked example: multiple except clauses, raise, and finally together

A. (Shared by the teacher) Demonstrates catching specific exceptions before a general fallback, manually raising an exception with `raise`, and that code after an uncaught/re-raised exception never executes.

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

What actually happens when this runs:
1. `1/0` raises `ZeroDivisionError` immediately - so the `raise ValueError(...)` line right after it never runs at all
2. The first matching `except ZeroDivisionError:` catches it and prints "You can't divide by zero!"
3. `finally` always runs next, printing its message
4. Since the exception was caught (not re-raised), the three `print()` lines after the whole `try` block... **would** normally execute, since the exception was successfully handled - the comments in this example are actually a common misconception worth flagging: catching an exception means the program continues normally afterward, it does NOT skip the rest of the script. Only an *uncaught* exception (or one re-raised inside `except`) would stop execution before reaching those lines.

Note: `except ValueError` and `except Exception` never actually run in this particular example, since `ZeroDivisionError` is raised and caught first - a good illustration of why exception order matters (most specific exceptions first, generic `Exception` last as a catch-all).

# Logging

Q. Worked example: the `logging` module in a small data-processing script

A. (Shared by the teacher) Same `if name == "main":` typo as the threading example - fixed below to `if __name__ == "__main__":`.

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

Key things to notice:
- `logging.basicConfig(level=logging.DEBUG, format=...)` sets up the logger once, globally - the format string includes a timestamp, the log level, and the message
- `%s` placeholders (e.g. `logging.info("Attempting to divide %s by %s", a, b)`) let the logging module handle string formatting itself, rather than pre-formatting with an f-string - this is a small performance win, since the string is only actually built if that log level is enabled
- Different severity levels used here: `debug` (fine-grained internal detail), `info` (normal progress), `warning` (something recoverable went wrong), `error` (a real failure) - this ties directly to why `logging` is preferred over `print()` in production code (from the Training 0 error handling notes) - you can filter by severity level instead of manually removing/adding print statements

# File I/O

# JSON / CSV

# DataFrames (Pandas)

Q. Worked example: the same employee CSV pipeline, rewritten with Pandas

A. (Shared by the teacher) This is the Pandas equivalent of the earlier `map()` -> `filter()` -> `map()` -> `reduce()` employee pipeline (see the Functional Tools section above), reading from the same `data.csv`. No bugs in this one - well-formatted as pasted.

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

The key teaching point: Pandas replaces record-at-a-time operations (looping over rows one by one) with **column-oriented/vectorized operations** (acting on an entire column at once).

| Pure Python                  | Pandas                         |
| ----------------------------- | ------------------------------- |
| `csv.DictReader()`            | `pd.read_csv()`                 |
| `map(convert_employee, ...)`  | column operations / `astype()`  |
| `filter(condition, ...)`      | `df[condition]`                 |
| `map(give_raise, ...)`        | `df["salary"] * 1.05`           |
| `reduce(... total ...)`       | `.sum()`                        |
| custom grouped reduction      | `.groupby().sum()`              |
| custom average calculation    | `.mean()`                       |

You *could* use Pandas' own `.map()`/`.apply()` to make it look like the pure-Python version:

```python
df["salary"] = df["salary"].map(lambda x: x * 1.05)
```

...but for a transformation like this, that's not the idiomatic Pandas style. Prefer the vectorized form:

```python
df["salary"] = df["salary"] * 1.05
```

This operates on the entire column at once rather than one row at a time:

```text
salary
------
92000
68000
105000
62000
88000
   |
   | * 1.05
   v
salary
------
96600
71400
110250
65100
92400
```

This sets up a progression worth remembering for the rest of the course: **plain Python record processing -> Pandas DataFrames/vectorization -> Spark DataFrames/distributed transformations**. Each step trades some manual control for automatic parallelism/optimization over larger data - Pandas vectorizes across your local CPU's columns in memory, and Spark (see Training 0) extends that same DataFrame concept across a distributed cluster.

# Filtering

# Joins

# Small ETL Exercise

---

# Agent Generated Notes

*(Concepts below were not covered live in class - added while working through the Pandas homework, since they were needed to solve specific exercises. Flagged here rather than under the main headings above so it's clear which content came from Evan directly vs. filled in afterward.)*

## `pd.cut()` - binning continuous values into labeled categories

**Docs:** [pandas.cut — pandas documentation](https://pandas.pydata.org/docs/reference/api/pandas.cut.html)

**What it does:** `pd.cut()` bins values into discrete intervals, converting a continuous numeric variable into a categorical one by segmenting and sorting data into specified ranges.

**Signature (the pieces that matter here):**
```python
pd.cut(series, bins=[...], labels=[...])
```
- `bins` is a list of boundary numbers (edges). If you have N labels, you need N+1 edges - each label describes the gap *between* two consecutive edges.
- `labels` is what each resulting bucket should be called.
- Bins are edge-exclusive on the low end and inclusive on the high end by default - a value sitting exactly on a boundary falls into the *upper* bucket. This matters when translating a requirement like "under 70,000 is Low, 70,000+ is Medium" into edges: setting the edge at `69_999` (not `70_000`) guarantees a salary of exactly 70,000 lands in "Medium," matching the wording precisely.

**Small example:**
```python
ages = pd.Series([5, 17, 40, 70])

groups = pd.cut(
    ages,
    bins=[0, 12, 19, 64, 120],
    labels=["Child", "Teen", "Adult", "Senior"]
)
# -> ["Child", "Teen", "Adult", "Senior"]
```
5 falls between 0-12 -> "Child", 17 falls between 12-19 -> "Teen", and so on. `float("inf")` can be used as the final edge when there's no natural upper limit (e.g. "$110,000 and above").

**Why use this instead of a manual if/elif chain:** you could write a plain Python function with if/elif branches (like the ones in the Conditionals section above) and apply it row-by-row with `.apply()`. `pd.cut()` does the same job in a single vectorized call across the entire column at once - same vectorization idea as `df["salary"] * 1.05` from the DataFrames section, rather than checking one row at a time.

| Manual approach | `pd.cut()` |
|---|---|
| Write an if/elif function per bucket | One declarative call: edges + labels |
| Apply row-by-row with `.apply()` | Vectorized across the whole column |
| Easy to mismatch a boundary | Edges are explicit and centralized in one place |

## `.unstack()` - reshaping a grouped result from "long" to "wide"

**Docs:** [pandas.DataFrame.unstack — pandas documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.unstack.html)

**The setup:** grouping by *two* columns at once, e.g. `groupby(["department", "salary_band"]).size()`, doesn't produce a simple table - it produces a Series with a **MultiIndex** (a two-level row label combining department + salary_band), with one row per combination that actually exists in the data:

```text
department   salary_band
Engineering  High           17
             Medium          8
             Very High       6
Finance      High           12
             Medium          8
HR           Low             7
             Medium          7
```

This is **"long" format** - correct, but hard to scan or compare across departments.

**What `.unstack()` does:** takes one level of that row index (by default the *innermost* one - here, `salary_band`) and rotates it so it becomes column headers instead of part of the row label. Each distinct band becomes its own column:

```text
salary_band   High   Low   Medium   Very High
department
Engineering    17     0        8           6
Finance        12     0        8           0
HR              0     7        7           0
```

This is **"wide" format** - one row per department, one column per category, easy to read like a spreadsheet.

**Why `fill_value=0` is needed alongside it:** HR has zero "Very High" earners, so that combination never appeared in the original long Series at all - without `fill_value=0`, `.unstack()` would leave that cell as `NaN` (meaning "no data"), when the accurate answer is `0` (meaning "zero, we counted"). `fill_value=0` fills those true gaps with the correct number instead of a missing marker.

**Rule of thumb:** whenever a `groupby()` uses two or more columns and the result should read like a spreadsheet grid instead of a tall stacked list, `.unstack()` is the reshaping tool for long -> wide.

## `observed=True` - avoiding phantom groups on categorical columns

`pd.cut()` doesn't return a plain string column - it returns a special `Categorical` dtype that secretly remembers the *entire list of possible categories* (e.g. `Low, Medium, High, Very High`), not just the ones present in the data.

By default, grouping by a categorical column makes Pandas generate a group for **every possible category combination** - the full cross-product (5 departments x 4 bands = 20 groups) - even combinations that never actually occur in a single row (e.g. HR + "Very High"). That's wasted work, and current Pandas versions raise a `FutureWarning` about this default changing in an upcoming release.

`observed=True` tells `groupby()` to only create groups for combinations that **actually appear** in the data, skipping the phantom ones. Since the true zeros are already being filled in afterward via `unstack(fill_value=0)`, there's no need for Pandas to manufacture the empty combinations itself - same correct final result, without the extra overhead or the warning.

## `.value_counts()` - counting occurrences of each unique value

**Docs:** [pandas.Series.value_counts — pandas documentation](https://pandas.pydata.org/docs/reference/api/pandas.Series.value_counts.html)

**What it does:** called on a single column (Series), it counts how many times each unique value appears and returns the results as a Series, already sorted from most to least common (descending frequency) by default.

```python
data_frame["department"].value_counts()
# department
# Sales      20
# Finance    20
# ...
```

**How it relates to `groupby().size()`:** functionally similar to `groupby("department").size()` from the salary-bands exercise, but `value_counts()` is a shortcut for the common case of counting one column's values - no need to spell out `groupby()` + `.size()` when there's only one column involved and you don't need a multi-column grid.

## `.idxmax()` - finding which row/label holds the maximum value

**Docs:** [pandas.Series.idxmax — pandas documentation](https://pandas.pydata.org/docs/reference/api/pandas.Series.idxmax.html)

**What it does:** returns the **label** (index entry) associated with the largest value in a Series - not the value itself.

```python
counts = pd.Series([4, 6, 2], index=["Sales", "Finance", "HR"])
counts.idxmax()   # -> "Finance" (the label, not 6)
counts.max()      # -> 6 (the value itself)
```

**Why both `.idxmax()` and `.max()` are often used together:** they answer two different questions - `.idxmax()` answers "*which* group/row has the largest value," `.max()` answers "*what is* that largest value." A sentence like "Department X has the most employees (N of them)" needs both pieces, pulled out programmatically instead of eyeballing the top row of a printed, sorted list.

If multiple entries are tied for the maximum, `.idxmax()` returns the *first* one it encounters, not all of them.

## `.rank()` - assigning each row a rank number within its group

**Docs:** [pandas.Series.rank — pandas documentation](https://pandas.pydata.org/docs/reference/api/pandas.Series.rank.html)

**What it does:** computes a numeric rank (1 through N) for every value, based on where it falls relative to the others. Used after `groupby()`, it ranks values *within each group separately* rather than across the whole column.

```python
exercise5_df["salary_rank"] = (
    exercise5_df
    .groupby("department")["salary"]
    .rank(method="min", ascending=False)
    .astype(int)
)
```
- `ascending=False` - the *highest* salary in each department gets rank 1 (default `ascending=True` would rank the smallest value as 1).
- `.astype(int)` - `.rank()` returns decimals by default (e.g. `1.0`, `2.0`), since some tie-handling methods can produce fractional ranks. Converting to `int` is safe here because `method="min"` never actually produces a fraction.

**Why `.rank()` and not just `.sort_values()`:** sorting only reorders *rows for display* - it never attaches a new stored value to each row saying "you are rank 2 in your group." `.rank()` actually computes and stores that number as real data, which matters when the requirement is "add a column" rather than "show me these rows in a certain order." You could reconstruct something similar with sorting plus `groupby().cumcount()`, but that reimplements `.rank()` by hand and still leaves tie-handling to you.

**The `method` parameter - how ties are handled** (values `[4, 2, 4, 8]`, ranked ascending):

| `method` | Result | Behavior |
|---|---|---|
| `"average"` (default) | `[2.5, 1, 2.5, 4]` | Tied values split the average of the ranks they'd occupy |
| `"min"` | `[2, 1, 2, 4]` | Tied values all get the *lowest* rank they'd occupy; the next rank is skipped |
| `"max"` | `[3, 1, 3, 4]` | Tied values all get the *highest* rank they'd occupy |
| `"first"` | `[2, 1, 3, 4]` | Ties broken by order of appearance in the data (no ties in the output) |
| `"dense"` | `[2, 1, 2, 3]` | Like `"min"`, but the next rank always increases by exactly 1 (no skipped numbers) |

`method="min"` was the right choice for exercise 5: if two employees in the same department are tied for the highest salary, both should correctly show as rank 1 (not an arbitrary 1-and-2 split), and the next distinct salary becomes rank 3 - correctly reflecting that two people already hold the top spot.

## `.merge()` - joining two DataFrames on a shared column

**Docs:** [pandas.DataFrame.merge — pandas documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html)

**What it does:** combines two DataFrames based on matching values in a shared column - the Pandas equivalent of a SQL `JOIN`.

```python
exercise6_df = data_frame.merge(department_info, on="department", how="left")
```
- `department_info` - the other DataFrame being joined in.
- `on="department"` - the shared column both DataFrames have, used to match rows between them.
- `how="left"` - the join type, controlling which rows survive when a match is missing.

**The `how` parameter - join types (same concepts as SQL joins):**

| `how` | Behavior |
|---|---|
| `"left"` | Keep every row from the left (calling) DataFrame; attach matching columns from the right wherever a match exists (SQL LEFT OUTER JOIN) |
| `"right"` | Keep every row from the right DataFrame instead (SQL RIGHT OUTER JOIN) |
| `"inner"` (default) | Keep only rows where the key exists in *both* DataFrames (SQL INNER JOIN) |
| `"outer"` | Keep every row from *both* DataFrames, filling in missing pieces with `NaN` where there's no match (SQL FULL OUTER JOIN) |
| `"cross"` | Every row of the left paired with every row of the right (cartesian product) - rarely what you want |

`how="left"` was the right choice for exercise 6: the goal is "every employee record also contains their manager and office location" - meaning no employee row should ever be dropped just because of the join, even if (hypothetically) a department had no matching row in `department_info`. `"left"` guarantees the full employee list survives; `"inner"` could silently drop employees if a department name were ever missing or misspelled in one of the two tables.

## `sort_values()` - reordering a DataFrame's rows

**Docs:** [pandas.DataFrame.sort_values — pandas documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html)

**What it does:** reorders the rows of a DataFrame based on the values in one or more columns. By default, sorts **ascending** (low to high).

**Single column:**
```python
df.sort_values("salary")                    # ascending (default): lowest first
df.sort_values("salary", ascending=False)   # descending: highest first
```

**Multiple columns (a primary key plus tie-breakers):**
```python
df.sort_values(["department", "salary"], ascending=[True, False])
```
The column list and the `ascending` list line up positionally - sort by `department` first (alphabetical, since `True`), and *within* rows that share the same department, break ties using `salary` (highest first, since `False`). Each column in the list can have its own independent direction.

**Toy example** - sorting `[{dept: Sales, salary: 80000}, {dept: Engineering, salary: 90000}, {dept: Sales, salary: 95000}, {dept: Engineering, salary: 85000}]` by `["department", "salary"]` with `ascending=[True, False]`:
```text
department    salary
Engineering   90000
Engineering   85000
Sales         95000
Sales         80000
```
Engineering sorts before Sales (alphabetical), and within each department, the higher salary appears first (descending).

## Standard deviation (statistics background for `.transform("std")`)

Standard deviation measures how spread out a set of numbers is around their average. A *small* standard deviation means values cluster close to the mean; a *large* one means they're scattered widely above and below it.

**How it's calculated, step by step**, for one group of numbers:
1. Find the mean (average).
2. For each value, find its deviation from the mean (can be positive or negative).
3. Square each deviation (makes everything positive, and weights larger deviations more heavily).
4. Average those squared deviations - this is called the **variance**.
5. Take the square root of the variance - that's the standard deviation, back in the original units.

**Example:** Department A salaries `[60000, 62000, 58000]` - all close together -> small standard deviation. Department B salaries `[40000, 60000, 100000]` - same rough average, but widely scattered -> much larger standard deviation, even with a similar mean.

**Why "mean + 1 standard deviation" is a meaningful outlier threshold:** it's a standard statistical convention - for many real-world distributions, most values cluster within one standard deviation of the mean, so "more than one standard deviation above the mean" is a widely-used, non-arbitrary definition of "unusually high" relative to a specific group.

**In Pandas**, `"std"` is just another built-in aggregation function name, usable anywhere `"mean"` or `"count"` are (inside `.agg()`, `.transform()`, or called directly as `.std()`) - the statistics are the interesting part here, not new Pandas syntax.

## Named aggregation - multiple stats, multiple source columns, one `.agg()` call

**Docs:** [Named aggregation — pandas user guide](https://pandas.pydata.org/docs/user_guide/groupby.html#named-aggregation)

**What it does:** lets `.agg()` compute several differently-named stats from several different source columns in a single call, instead of building each stat as a separate Series and stitching them together with `to_frame()` + column assignment (the approach used in exercise 1).

```python
department_report = data_frame.groupby("department").agg(
    employee_count=("employee_id", "count"),
    average_salary=("salary", "mean"),
    highest_salary=("salary", "max"),
)
```
Each line follows the pattern `new_column_name = ("source_column", "function_name")` - the left side is a name you choose for the output column, the right side is a tuple of (which column to read from, which aggregation to apply). `active_employee_count=("active", "sum")` is a useful trick: summing a `True`/`False` column counts the `True` values, since Python treats `True` as `1` and `False` as `0` in arithmetic.

## `.reset_index()` - turning a groupby's index back into a normal column

**Docs:** [pandas.DataFrame.reset_index — pandas documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html)

**What it does:** after any `groupby()`, the column grouped on (e.g. `department`) becomes the result's **index**, not an ordinary column - this has been true of every `groupby()` result throughout this training. `.reset_index()` converts that index back into a normal, selectable column (and replaces the index with plain default row numbers 0, 1, 2...).

**Why it matters:** operations like `.merge()` join on regular *columns*, not on the index. If `department` is still sitting as the index after a `groupby()`, `.merge(..., on="department")` won't find it - `.reset_index()` needs to run first so `department` is a real column again.

## `.loc[]` - selecting rows by label

**Docs:** [pandas.DataFrame.loc — pandas documentation](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html)

**What it does:** selects rows (and optionally columns) by their **label** (the index value), not by their position in the DataFrame.

```python
idx_of_max_salary = data_frame.groupby("department")["salary"].idxmax()
highest_paid_names = data_frame.loc[idx_of_max_salary, ["department", "name"]]
```
`idx_of_max_salary` is a collection of specific row labels - one per department, each pointing at that department's highest-salary row (from `.idxmax()`, grouped). `.loc[idx_of_max_salary, ["department", "name"]]` jumps directly to exactly those rows and pulls out just the `department` and `name` columns from each one - turning "the row label of the maximum" into "the actual name sitting at that row."

**`.loc[]` vs `.iloc[]`** (not used in this homework, but worth knowing the distinction): `.loc[]` selects by label/index value; `.iloc[]` selects by integer position (0, 1, 2...) regardless of what the labels actually are. They can give different results whenever a DataFrame's index isn't just a simple 0,1,2... sequence - such as right after using `.idxmax()` results, or after filtering rows (which keeps the original row labels rather than renumbering them).

