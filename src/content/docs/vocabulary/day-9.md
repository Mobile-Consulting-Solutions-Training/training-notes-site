---
title: Day 9 Vocabulary
description: Glossary of terms and definitions from the Training 9 notes.
sidebar:
  order: 9
---

Vocabulary — Study Guide Day 9

Source: notes/Training 9.md

## IntelliJ, Scala and sbt Setup
- **IntelliJ IDEA** — JetBrains' IDE used for Scala development in class.
- **IDE (Integrated Development Environment)** — An application combining a code editor, build integration and debugging tools.
- **Scala plugin** — IntelliJ plugin that adds Scala language support.
- **sbt (Scala Build Tool)** — Scala's build tool, which IntelliJ uses to discover project structure and resolve dependencies.
- **build.sbt** — The sbt project definition file, setting values like `scalaVersion` and the project name.
- **project/build.properties** — File that pins the sbt version, e.g. `sbt.version=1.11.7`.
- **scalaVersion** — `build.sbt` setting choosing the Scala version (e.g. 2.13.x).
- **libraryDependencies** — `build.sbt` setting listing external libraries; not needed for a first project.
- **sbt import** — IntelliJ running sbt to load the project; until it succeeds, Scala code insight does not work.
- **Code insight** — IDE features like autocomplete, highlighting and error checking that depend on a loaded project.
- **"Extracting structure failed"** — Error meaning IntelliJ failed to import the project as an sbt project; an IDE/build problem, not a Scala code problem.
- **JDK (Java Development Kit)** — The Java toolkit Scala and sbt need; JDK 17 is the recommended version.
- **Project SDK** — IntelliJ's project-level JDK setting under Project Structure.
- **sbt JRE setting** — Separate IntelliJ setting choosing which JDK sbt runs on; must agree with the project SDK.
- **JRE (Java Runtime Environment)** — The Java runtime needed to run JVM programs such as sbt.
- **Load sbt project** — IntelliJ action that imports the sbt project and downloads dependencies.
- **Reload All sbt Projects** — sbt tool-window action forcing a complete reimport.
- **sbt compile** — Command compiling the project from the terminal, verifying sbt independently of IntelliJ.
- **sbt --version** — Command showing the installed sbt version.

## Scala Fundamentals
- **Scala** — A functional and object-oriented JVM language.
- **Singleton Object** — A Scala construct declared with `object` that guarantees exactly one instance exists.
- **Immutability** — Once something has been created it cannot be altered; to change it you create a new version.
- **Mutable** — Able to be changed in place after creation.
- **Immutable** — Unable to be changed in place; any change produces a new object.
- **Functional programming** — Programming style built on immutable values and functions rather than in-place mutation.

## Data Lineage
- **Data lineage** — The steps taken in data processing between input and output data, each preserved so transformations make sense over time.
- **Medallion Architecture** — Bronze, Silver and Gold layers kept as queryable checkpoints, which form a concrete record of lineage.
