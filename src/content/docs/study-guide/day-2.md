---
title: Study Guide - Day 2
description: Quick summary, cheat sheet, and flashcards for Training 2 (Python and Pandas)
---

Study Guide - Day 2 (source: notes/Training 2.md)

Note: File I/O, JSON/CSV, Filtering, Joins, and the Small ETL Exercise sections are still empty in Training 2.md pending the class recording - this guide covers everything documented so far (Python Background through DataFrames/Pandas, plus the Agent Generated Notes added while working through the Pandas homework). Update this guide once those sections are filled in.

# Part 1: Quick Summary

**Python Background.** Python is interpreted (no separate compile step, run directly with `python script.py`), unlike compiled languages (C, C++, Rust, Go) that build to machine code first, or hybrid Java (compiles to bytecode, then JVM interprets/JIT-compiles it). Python is dynamically typed - types are checked at runtime, not declared upfront - though optional type hints plus external tools (`mypy`, `pyright`) can add static checking on top without changing how Python actually runs. Packages should come from PyPI (pypi.org), the official trusted registry `pip install` pulls from by default - always verify an unfamiliar package's name/maintainer to avoid typosquatting. Python's `threading` module is limited by the GIL (Global Interpreter Lock) - only one thread executes Python bytecode at a time, so threading only helps I/O-bound work, not CPU-bound work (`multiprocessing` is needed for real CPU parallelism). This is why Spark doesn't rely on Python threads for its heavy lifting: the actual distributed computation happens at the JVM/cluster/process level, not within a single Python process.

**Loops, Functions, and Functional Tools.** `for` loops iterate over a known sequence; `while` loops repeat until a condition changes (risk: infinite loops if the condition never flips). Functions are defined with `def name(params): ... return value`, support default parameter values, `*args` (any number of positional args), and `**kwargs` (any number of keyword args). `map()`, `filter()`, and `reduce()` are higher-order functions - `map` transforms every item, `filter` keeps items matching a condition, `reduce` (from `functools`) collapses a sequence into one value. List comprehensions are generally preferred over `map`/`filter` for readability today.

**Booleans & Conditionals.** `True`/`False` are case-sensitive - lowercase `true`/`false` raises a `NameError`, unlike JavaScript/JSON or SQL. `if`/`elif`/`else` chains run only the first matching block and skip the rest, even if a later condition would also match. `else` is Python's "default" case. Python had no switch statement until 3.10's `match`/`case` (with `case _:` as the wildcard default). `==` compares values; `is` compares object identity (two equal-valued objects can still be different objects in memory).

**Exceptions & Logging.** `try`/`except`/`else`/`finally` - `finally` always runs regardless of success, a caught exception, or an uncaught one. Catching an exception does NOT stop the rest of the script - execution continues normally after a handled exception; only an uncaught (or re-raised) exception actually halts things. Exception order matters: specific exceptions should be caught before generic `Exception`, since only the first match fires. The `logging` module (`logging.basicConfig`, `logging.info/debug/warning/error`) is preferred over `print()` in production code since severity levels can be filtered without editing the code, and `%s`-style placeholders avoid building the log string unless that level is actually enabled.

**DataFrames (Pandas).** Pandas replaces record-at-a-time Python loops with vectorized, column-oriented operations - `df["salary"] * 1.05` operates on an entire column at once instead of looping row by row. Core building blocks: `pd.read_csv()` (extract), boolean indexing `df[condition]` (filter, works with a fixed value OR another column, since both sides just need to be same-length/aligned Series), `.groupby(...).agg()/.mean()/.count()/.min()/.max()` (aggregate, collapses to one row per group), `.groupby(...).transform(...)` (broadcasts an aggregate back onto every original row without collapsing - needed to compare a row's own value against its group's aggregate), `.groupby(...).rank(...)` (ranks within each group, same non-collapsing behavior as transform), `.merge()` (join two DataFrames on a shared column), and `.sort_values(columns, ascending=[...])` (reorder rows, optionally by multiple keys with independent directions). A Series (one column, no column names) is different from a DataFrame (a full table) - `.to_frame()` converts one to the other, which matters because you can only assign new named columns onto a DataFrame, not a Series.

**Agent Generated Notes (Pandas homework additions, not from live class).** `pd.cut()` bins a numeric column into labeled categories in one vectorized call (e.g. salary -> "Low"/"Medium"/"High"/"Very High") - edges are exclusive-low/inclusive-high by default. `.unstack()` reshapes a two-column `groupby()` result from "long" format (stacked MultiIndex rows) into "wide" format (a spreadsheet-style grid), typically paired with `fill_value=0` so missing combinations show a true zero instead of `NaN`. `observed=True` on a `groupby()` over a categorical column (like one produced by `pd.cut()`) avoids generating "phantom" groups for category combinations that don't actually appear in the data.

---

# Part 2: Cheat Sheet

## Python Background
- Interpreted (Python, JS, Ruby) = no build step, runs line-by-line. Compiled (C, C++, Rust, Go) = full machine-code build first. Java = hybrid (bytecode + JVM).
- Dynamically typed by default; optional type hints (`def f(a: int) -> int`) are NOT enforced at runtime - only external tools (`mypy`, `pyright`) actually check them.
- Install packages from **PyPI** (pypi.org) - watch for typosquatting on unfamiliar package names.
- **GIL**: only one thread runs Python bytecode at a time. Threading helps I/O-bound work only; `multiprocessing` needed for CPU-bound parallelism. Spark's real parallelism happens at the JVM/cluster level, not via Python threads.
- `if __name__ == "__main__":` (double underscores!) - guards code that should only run when the file is executed directly, not imported.

## Loops / Functions / Functional Tools
- `for x in sequence:` (known iteration count) vs `while condition:` (repeats until condition changes - watch for infinite loops).
- `def name(a, b=default, *args, **kwargs): ... return value`.
- `map(func, seq)` -> transform every item | `filter(func, seq)` -> keep matches | `reduce(func, seq, start)` (from `functools`) -> single value.
- List comprehensions `[x*2 for x in nums]` / `[x for x in nums if cond]` are the modern preferred style over `map`/`filter`.

## Booleans / Conditionals
- `True`/`False` only - capital first letter, case-sensitive. `true`/`false` -> `NameError`.
- `if`/`elif`/`else` - first `True` condition wins, rest are skipped.
- `else` = default/catch-all. Python 3.10+ `match`/`case` with `case _:` as wildcard default.
- `==` (value equality) vs `is` (identity - same object in memory).

## Exceptions & Logging
- `try` / `except SpecificError:` / `except Exception:` / `else` / `finally` - order matters, most specific first.
- `finally` always runs, no matter what. A **caught** exception does NOT stop the rest of the script - only uncaught/re-raised ones do.
- `logging.basicConfig(level=..., format=...)` once, then `logging.debug/info/warning/error(...)`. Prefer over `print()` - filterable by severity, `%s` placeholders avoid unnecessary string building.

## DataFrames (Pandas)
- `pd.read_csv("file.csv")` -> DataFrame. `df["salary"] * 1.05` -> vectorized, whole column at once.
- `df[condition]` -> boolean filter. `condition` can compare a column to a fixed value OR to another column (both are just same-length Series).
- `df.groupby("col")["target"].mean()/.count()/.min()/.max()` -> **collapses** to one row per group.
- `df.groupby("col")["target"].transform("mean")` -> broadcasts the aggregate back onto every original row, **no collapsing** - use this to compare a row against its own group's stat.
- `df.groupby("col")["target"].rank(ascending=False)` -> ranks within each group, also non-collapsing.
- `df1.merge(df2, on="col", how="left")` -> join two DataFrames.
- `df.sort_values(["col1", "col2"], ascending=[True, False])` -> multi-key sort, independent directions per column.
- Series (one column, no column names) vs DataFrame (full table) - `.to_frame()` converts Series -> DataFrame; only a DataFrame can have new named columns assigned onto it.

## Agent Generated Notes (not from live class)
- `pd.cut(series, bins=[...], labels=[...])` -> bins a numeric column into labeled categories in one vectorized call. Edges: low-exclusive, high-inclusive by default.
- `.unstack()` -> reshapes a 2-column `groupby()` result from long (stacked) to wide (spreadsheet grid). Pair with `fill_value=0` for true zeros instead of `NaN`.
- `observed=True` on `groupby()` over a categorical column -> skips phantom category combinations that don't appear in the data.

---

# Part 3: Flashcards

Q: What's the key practical difference between a compiled and an interpreted language?
A: Compiled languages build to machine code before running (separate build step); interpreted languages (like Python) run directly, line-by-line, no build step.

Q: Is Python statically or dynamically typed?
A: Dynamically typed - types are checked at runtime. Type hints exist but aren't enforced by Python itself; only external tools like `mypy` actually check them.

Q: Where should Python packages be installed from, and why does it matter?
A: PyPI (pypi.org) - always double check package names, since typosquatting (malicious lookalike package names) is a real risk.

Q: What is the GIL, and what does it mean for Python threading?
A: The Global Interpreter Lock - only one thread can execute Python bytecode at a time in CPython. Threading helps I/O-bound work but gives no real parallelism for CPU-bound work.

Q: Why doesn't Spark's performance suffer from Python's GIL, even in PySpark?
A: Spark's actual distributed computation runs at the JVM/cluster/process level (separate OS processes per executor), not via Python threads within one process.

Q: What's the correct idiom for "only run this code if the file is executed directly"?
A: `if __name__ == "__main__":` - note the double underscores on both sides of `name` and `main`.

Q: What's the difference between `map()`, `filter()`, and `reduce()`?
A: `map()` transforms every item (same length out), `filter()` keeps only items passing a condition (same or shorter), `reduce()` collapses the whole sequence into one value.

Q: Are `True` and `False` case-sensitive in Python?
A: Yes - only capitalized `True`/`False` work. Lowercase `true`/`false` raises a `NameError`.

Q: Does Python have a native switch statement?
A: Not until Python 3.10's `match`/`case` (with `case _:` as the default/wildcard case). Before that, people used `if`/`elif`/`else` chains.

Q: What's the difference between `==` and `is`?
A: `==` compares values for equality. `is` compares identity - whether two variables point to the exact same object in memory.

Q: Does a caught exception stop the rest of a script from running?
A: No - once an exception is caught by a matching `except`, the rest of the script continues normally. Only an uncaught (or re-raised) exception actually halts execution.

Q: Why does exception order matter in a multi-except block?
A: Only the first matching `except` runs. Specific exceptions must come before generic `Exception`, or the specific handler will never be reached.

Q: When does Python's `finally` block run?
A: Always - whether the `try` succeeded, an exception was caught, or even if an exception was never caught at all.

Q: Why is `logging` generally preferred over `print()` in production code?
A: Log messages can be filtered by severity level (debug/info/warning/error) without editing the code, unlike scattered `print()` statements.

Q: What's the core idea behind Pandas vectorization?
A: Operations act on an entire column at once (e.g. `df["salary"] * 1.05`) instead of looping through rows one at a time in plain Python.

Q: What's the difference between `groupby().mean()` and `groupby().transform("mean")`?
A: `.mean()` collapses to one row per group. `.transform("mean")` broadcasts the same aggregate back onto every original row, keeping the row count unchanged - needed to compare an individual row against its group's stat.

Q: Why does `df["salary"] > df["department_average"]` work as a filter condition?
A: Because both sides are Series aligned to the same DataFrame's rows - comparing two columns with `>` works exactly like comparing a column to a fixed number, producing a True/False Series per row.

Q: What's the difference between a Pandas Series and a DataFrame?
A: A Series is one column of values with an index, no column names. A DataFrame is a full table with named columns. `.to_frame()` converts a Series into a one-column DataFrame.

Q: How do you sort a DataFrame by department first, then by salary descending within each department?
A: `df.sort_values(["department", "salary"], ascending=[True, False])` - the two lists line up positionally (primary key + direction, then tie-breaker + direction).

Q: What does `pd.cut()` do, and what's the edge-boundary gotcha?
A: Bins a numeric column into labeled categories in one vectorized call. Bin edges are low-exclusive/high-inclusive by default, so matching a rule like "under 70,000 is Low" requires setting the edge at `69_999`, not `70_000`.

Q: What does `.unstack()` do, and why is `fill_value=0` often used with it?
A: Reshapes a `groupby()` result from long (stacked MultiIndex rows) to wide (spreadsheet-style columns). `fill_value=0` replaces missing combinations with a true `0` instead of a misleading `NaN`.

Q: What problem does `observed=True` solve in `groupby()`?
A: It stops Pandas from generating a group for every possible category combination (including ones that never occur in the data) when grouping by a categorical column, like one produced by `pd.cut()`.
