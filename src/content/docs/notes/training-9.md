---
title: Training 9 - IntelliJ/Scala Setup & Scala Fundamentals
description: Troubleshooting IntelliJ/sbt Scala project setup, then the start of Scala fundamentals and a short note on data lineage.
---

Teacher: Evan Flint

Syllabus Day 10 (per file numbering) - actual coverage: IntelliJ/Scala/sbt environment setup and troubleshooting, then Scala language fundamentals beginning (Singleton Object, Immutability). Note: this continues the pacing drift already visible in `Training 6.md`-`Training 8.md` - this session's content lines up with the roadmap's Day 11 topic ("Scala Fundamentals") rather than its own nominal Day 10 slot ("Spark Advanced").

# IntelliJ + Scala/sbt Project Setup Troubleshooting

Q. A student's IntelliJ shows "Code insight is unavailable because the sbt project is not loaded" and "extracting structure failed: Build status: Error" right after installing the Scala plugin - what does this mean and how do you fix it?

A. (Teacher's definition) This screen means the Scala plugin is installed, but IntelliJ failed to import the project as an sbt project. The build.sbt itself looks normal. IntelliJ uses sbt to discover the project structure, so until that succeeds, Scala support won't initialize correctly.

Expanded: this is specifically an **IDE/build-tool import problem, not a Scala-programming problem** - the Scala plugin itself is installed and working, but IntelliJ relies on successfully running an sbt import (reading `build.sbt`, resolving dependencies, discovering source roots) to enable code insight (syntax highlighting depth, autocomplete, error checking). Until that import succeeds, the editor is essentially "blind" to the project's actual structure, even though the plugin is present and the `.scala`/`build.sbt` files look completely normal on their own. Worth remembering as a category distinction: don't start debugging Scala *code* when the actual symptom is an import failure - fix the import first.

## Fastest Path to Fix It (in order)

**1. Make sure a JDK is actually installed/configured.**
```text
File → Project Structure → Project
```
Check the SDK field. If it says `<No SDK>`:
```text
Add SDK → Download JDK
```
For an introductory Scala class, JDK 17 is the safe, recommended choice for modern sbt/Scala projects.

**2. Tell IntelliJ to use that JDK for sbt specifically** (a separate setting from the project SDK above):
```text
File → Settings → Build, Execution, Deployment → Build Tools → sbt
```
Set `JRE` to `Project JDK` / `JDK 17`. JDK incompatibility is a documented common cause of Scala/sbt compilation and import problems (per JetBrains' own docs) - the project-level SDK and sbt's own JRE setting are two different places JDK version can be misconfigured, and both need to agree.

**3. Load the sbt project.** IntelliJ typically offers this directly as a top-right action button: **"Load sbt project"** - click it, then wait for dependency downloads and indexing to finish (can take a while on a first Scala project, since IntelliJ/sbt has to download Scala itself plus other artifacts).

**4. If it still fails with "extracting structure failed":**
```text
View → Tool Windows → sbt
```
Click **"Reload All sbt Projects"** - JetBrains documents this as the normal way to force a complete reimport.

## If It Still Fails After All Four Steps

Verify sbt independently of IntelliJ - open IntelliJ's terminal in the project directory:
```bash
sbt --version
sbt compile
```
If `sbt` isn't recognized as a command, that's not necessarily fatal - IntelliJ can fall back to its own bundled sbt launcher. More important to check:

```text
project/build.properties
```
Should contain something like `sbt.version=1.11.7`.

Then check `build.sbt` itself:
```scala
scalaVersion := "2.13.18"

lazy val root = (project in file("."))
  .settings(
    name := "HelloWorld"
  )
```
This basic configuration is fine conceptually for a first lesson - no `libraryDependencies` entries needed yet, even as empty/commented placeholders.

**Worth knowing:** there's a documented JetBrains Scala-plugin issue that produces almost exactly this same symptom pair (`extracting structure failed` followed by `Code insight is not available because sbt project is not loaded`) as a genuine IDE bug, independent of anything the student did wrong. So if JDK 17 is confirmed correctly configured and a reload still fails - don't spend half the class debugging the student's Scala code. This is an IDE/sbt import problem, not a Scala-programming problem (same point as above, worth repeating since it's the single most time-wasteful mistake to make here).

## Standardized Classroom Setup Chain

```text
IntelliJ IDEA
    ↓
Scala plugin
    ↓
JDK 17
    ↓
sbt 1.x
    ↓
Scala 2.13.x
```

Recommended project creation workflow: `New Project → Scala → sbt`, select JDK 17, and **let IntelliJ finish the initial sbt synchronization before touching any code** - this is also the workflow JetBrains' own current documentation describes for creating Scala/sbt projects.

| Setting | Where | Recommended value |
|---|---|---|
| Project SDK | File → Project Structure → Project | JDK 17 |
| sbt's own JRE | File → Settings → Build Tools → sbt | Project JDK / JDK 17 |
| sbt version | `project/build.properties` | `sbt.version=1.11.7` (or current) |
| Scala version | `build.sbt` → `scalaVersion` | `2.13.18` (or current 2.13.x) |

---

# Scala Fundamentals

Q. What is a Singleton Object, in Scala?

Expanded: flagged here as a term introduced without a definition yet in this session - to be filled in as more detail is given. In general Scala terms, a `singleton object` (declared with the `object` keyword rather than `class`) is a language-level construct that guarantees exactly one instance exists - Scala doesn't require a separate design-pattern implementation for this the way Java traditionally does, since `object` is a first-class part of the language syntax itself.

---

Q. What is immutability?

A. (Teacher's definition) Immutability - once something has been created, it cannot itself be altered - if you want to alter it, you need to create a new version of the object.

Expanded: this is a core functional-programming principle Scala leans on heavily (distinct from the mutable-by-default style common in imperative languages) - once a value is created, its contents never change in place. Instead of mutating an existing object, any "change" is expressed by producing a brand-new object with the updated value, leaving the original untouched. This has direct practical consequences worth connecting forward to: it's part of why functional/immutable data structures are considered safer in concurrent/distributed contexts (per this course's Spark coverage) - an immutable value can be freely shared across threads/executors with no risk of one task's changes corrupting another's view of the same data, since no in-place mutation is ever possible in the first place.

| Term | Meaning |
|---|---|
| Mutable | Can be changed in place after creation - the same object's internal state is directly altered |
| Immutable | Cannot be changed in place - any "change" produces a new, separate object instead |

*(Placeholder - both Singleton Object and Immutability are flagged for further expansion as more of today's Scala Fundamentals content comes in.)*

---

# Data Lineage

Q. What is data lineage?

A. (Teacher's definition) Data lineage - the steps that are taken in data processing between the input data and the output data - each stage should be preserved so that transformations make sense over time.

Expanded: data lineage is the traceable record of a piece of data's journey - every transformation step it passed through, from wherever it originated (the source system) to wherever it ended up (the final output/report). "Preserved so that transformations make sense over time" is the key practical point - without tracking lineage, if a number in a final report looks wrong, there's no way to trace backward and figure out *which* step introduced the problem, or even *what steps* the data went through at all. This connects directly to this project's own Medallion Architecture work (`Training 8.md`, `hive-spark-etl-walkthrough.md`) - the Bronze -> Silver -> Gold layering *is* a form of lineage made concrete: each layer is a preserved checkpoint, which is exactly what made the "trace `sale_id` 20001/20003 through every layer" exercise possible. Without keeping Bronze and Silver around as their own real, queryable tables (rather than just an in-memory pipeline that only exposes the final Gold result), there would be no way to answer "why did this record get rejected" after the fact - lineage is the reason that question was answerable at all.

| Without lineage | With lineage |
|---|---|
| Only the final output is kept/inspectable | Every intermediate stage is preserved and queryable |
| "Why is this number wrong?" has no answer | Can trace backward through each transformation to find where it changed/was rejected |
| Debugging a bad result means guessing | Debugging means querying each stage in order, same as the Bronze/Silver/Gold trace exercise |
