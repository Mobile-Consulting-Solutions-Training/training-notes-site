---
title: Day 2 Vocabulary
description: Glossary of terms and definitions from the Training 2 study guide.
sidebar:
  order: 2
---

Vocabulary — Study Guide Day 2

## Python Background
- **Interpreted language** — Runs directly, line-by-line, with no separate build step (e.g. Python, JS, Ruby).
- **Compiled language** — Builds to machine code before running, as a separate step (e.g. C, C++, Rust, Go); Java is a hybrid, compiling to bytecode which the JVM then interprets/JIT-compiles.
- **Dynamically typed** — Types are checked at runtime rather than declared/enforced upfront; Python's default. Optional type hints exist but aren't enforced by Python itself — only external tools (`mypy`, `pyright`) actually check them.
- **PyPI** — The official, trusted Python package registry (pypi.org) that `pip install` pulls from by default; watch for typosquatting on unfamiliar package names.
- **GIL (Global Interpreter Lock)** — CPython's restriction that only one thread executes Python bytecode at a time; makes `threading` useful only for I/O-bound work, not CPU-bound work (`multiprocessing` is needed for real CPU parallelism).
- **`if __name__ == "__main__":`** — Idiom that guards code to only run when a file is executed directly, not when it's imported as a module.

## Loops, Functions, and Functional Tools
- **`for` loop** — Iterates over a sequence with a known iteration count.
- **`while` loop** — Repeats until a condition changes; risks an infinite loop if the condition never flips.
- **Function definition** — `def name(params): ... return value`; supports default parameter values, `*args` (any number of positional args), and `**kwargs` (any number of keyword args).
- **`map()`** — Higher-order function that transforms every item in a sequence.
- **`filter()`** — Higher-order function that keeps only items matching a condition.
- **`reduce()`** — Higher-order function (from `functools`) that collapses a sequence into a single value.
- **List comprehension** — `[expr for x in seq if cond]` syntax, generally preferred over `map`/`filter` for readability.

## Booleans & Conditionals
- **`True`/`False`** — Python's boolean literals; case-sensitive (lowercase `true`/`false` raises a `NameError`).
- **`if`/`elif`/`else`** — Conditional chain that runs only the first matching block, skipping the rest even if a later condition would also match.
- **`match`/`case`** — Python 3.10+'s switch-statement equivalent, with `case _:` as the wildcard default.
- **`==`** — Compares two values for equality.
- **`is`** — Compares object identity (whether two variables reference the exact same object in memory).

## Exceptions & Logging
- **`try`/`except`/`else`/`finally`** — Python's exception-handling structure; `finally` always runs regardless of success, a caught exception, or an uncaught one.
- **Caught exception** — Does not stop script execution; the script continues normally after a handled exception. Only an uncaught (or re-raised) exception halts execution.
- **Exception ordering** — Specific exception types must be caught before generic `Exception`, since only the first matching `except` block fires.
- **`logging` module** — Preferred over `print()` in production code; supports severity-level filtering (`debug`/`info`/`warning`/`error`) without editing code, and `%s`-style placeholders avoid building the log string unless that level is enabled.

## DataFrames (Pandas)
- **Vectorization** — Pandas operating on an entire column at once (e.g. `df["salary"] * 1.05`) instead of looping row by row.
- **`pd.read_csv()`** — Reads a CSV file into a DataFrame.
- **Boolean indexing (`df[condition]`)** — Filters rows using a True/False condition, which can compare a column to a fixed value or to another same-length column.
- **`.groupby(...).agg()` / `.mean()` / `.count()` / etc.** — Aggregates data, collapsing to one row per group.
- **`.groupby(...).transform(...)`** — Broadcasts an aggregate value back onto every original row without collapsing, used to compare a row's own value against its group's aggregate.
- **`.groupby(...).rank(...)`** — Ranks rows within each group, without collapsing (same non-collapsing behavior as `transform`).
- **`.merge()`** — Joins two DataFrames on a shared column.
- **`.sort_values(columns, ascending=[...])`** — Reorders rows, optionally by multiple keys with independent sort directions.
- **Series** — A single column of values with an index, no column names.
- **DataFrame** — A full table with named columns; only a DataFrame (not a Series) can have new named columns assigned onto it.
- **`.to_frame()`** — Converts a Series into a one-column DataFrame.

## File I/O
- **`open()`** — Opens a file and returns a file object; the mode says how (`"r"` read, `"w"` overwrite, `"a"` append, `"rb"`/`"wb"` binary).
- **`with` block (context manager)** — Runs code with a resource and cleans it up automatically; `with open(...) as f:` closes the file even if an error happens.
- **`pathlib.Path`** — An object for building and inspecting file paths safely on any OS (`Path("data") / "sales.csv"`, `.exists()`, `.suffix`, `.stem`).

## JSON / CSV
- **`json.load()` / `json.loads()`** — Parse JSON from a file object / from a string into Python dicts and lists.
- **`json.dump()` / `json.dumps()`** — Write Python objects as JSON to a file object / to a string.
- **`csv.DictReader`** — Reads a CSV so each row is a dict keyed by the header; every value comes back as a string.
- **`csv.DictWriter`** — Writes dicts as CSV rows using a list of field names.
- **`chunksize`** — A `pd.read_csv` option that reads a large file in pieces instead of all at once.
- **Newline-delimited JSON (NDJSON)** — One JSON object per line; read with `pd.read_json(path, lines=True)`.
- **`pd.json_normalize()`** — Flattens nested JSON records into columns such as `address.city`.

## Filtering
- **Boolean mask** — A True/False Series used inside `df[...]` to keep only the True rows.
- **`&`, `|`, `~`** — Row-by-row and, or, and not for combining masks; each condition needs its own parentheses.
- **"The truth value of a Series is ambiguous"** — The error from using `and`/`or` on whole columns instead of `&`/`|`.
- **`.isin()`** — True where a value is in a given list.
- **`.between()`** — True where a value falls inside a range (inclusive by default).
- **`df.query()`** — Filters with a string expression, e.g. `"salary >= 70000 and active"`.
- **`isna()` / `notna()`** — Find missing / present values.
- **`dropna()` / `fillna()`** — Drop rows with missing values / replace missing values.
- **`drop_duplicates()`** — Removes duplicate rows, optionally judged on a subset of columns.
- **`SettingWithCopyWarning`** — Warning when changing a filtered DataFrame that may be a view of the original; avoid it with `.copy()`.

## Joins
- **`.join()`** — Joins two DataFrames on their index.
- **`pd.concat()`** — Stacks DataFrames on top of each other (like SQL `UNION ALL`), or side by side with `axis=1`.

## Small ETL Exercise
- **ETL (extract, transform, load)** — The pipeline pattern of the employee exercise: read the CSV, convert types, filter, raise salaries, aggregate, then save with `to_csv`.
- **`to_csv(path, index=False)`** — Writes a DataFrame to CSV without the index column.

## Agent Generated Notes (Pandas Homework Additions)
- **`pd.cut()`** — Bins a numeric column into labeled categories in one vectorized call; bin edges are low-exclusive/high-inclusive by default.
- **`.unstack()`** — Reshapes a two-column `groupby()` result from "long" format (stacked MultiIndex rows) into "wide" format (a spreadsheet-style grid); typically paired with `fill_value=0` so missing combinations show a true zero instead of `NaN`.
- **`observed=True`** — A `groupby()` option (over a categorical column, e.g. one from `pd.cut()`) that avoids generating "phantom" groups for category combinations that don't actually appear in the data.
