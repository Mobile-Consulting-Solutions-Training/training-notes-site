---
title: Study Guide - Day 9
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 9: IntelliJ/Scala Setup & Scala Fundamentals"
sidebar:
  order: 90
---

Study Guide - Day 9 (source: notes/Training 9.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**IntelliJ "sbt project is not loaded".** The Scala plugin is installed, but IntelliJ couldn't import the project through sbt, so code insight is off. It's an IDE/build-tool import problem, not a Scala code problem; fix the import before touching code.

**The Fix, in Order.** (1) Set a project JDK: File → Project Structure → Project → JDK 17. (2) Set sbt's own JRE to the same JDK: Settings → Build Tools → sbt. These are two separate settings and both must agree. (3) Click **Load sbt project** and wait for downloads and indexing. (4) If it still fails: sbt tool window → **Reload All sbt Projects**. Then check `sbt compile` in the terminal, `project/build.properties` (`sbt.version=1.11.7`) and `build.sbt` (`scalaVersion := "2.13.18"`). A known JetBrains plugin bug can cause the same symptoms.

**Standard Setup Chain.** IntelliJ → Scala plugin → JDK 17 → sbt 1.x → Scala 2.13.x. Create with New Project → Scala → sbt, and let the first sbt sync finish before writing code.

**Singleton Object.** Declared with `object` instead of `class`; exactly one instance exists, built into the language (no design pattern needed as in Java). Used for `main` and shared utilities.

**Immutability.** Once something is created it can't be altered; to change it you create a new version. Immutable values are safe to share across threads and executors because nothing can modify them in place.

**Data Lineage.** The steps data passes through between input and output, each preserved so transformations make sense over time. Bronze → Silver → Gold is lineage made concrete: you can trace why a number is wrong or a record was rejected by querying each layer in order.

---

# Part 2: Cheat Sheet

## sbt Import Failure
- Symptom: "sbt project is not loaded" / "extracting structure failed"
- Project SDK = JDK 17 · sbt JRE = JDK 17 · Load sbt project · Reload All sbt Projects
- Check: `sbt compile` · `project/build.properties` · `build.sbt` `scalaVersion`
- Import problem ≠ code problem

## Setup Chain
- IntelliJ → Scala plugin → JDK 17 → sbt 1.x → Scala 2.13.x

## Scala Basics
- `object` = singleton (one instance)
- Immutable: change = new object · mutable: change in place

## Lineage
- Every stage preserved · trace backwards to find the bad step · medallion layers = lineage

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: IntelliJ says code insight is unavailable because the sbt project isn't loaded. What does that mean?
A: The Scala plugin is fine, but IntelliJ failed to import the project through sbt, so it doesn't know the project's structure. It's an import problem, not a problem with the Scala code.

Q: What are the first things to check when the sbt import fails?
A: That a JDK, ideally 17, is set as the project SDK, and that sbt's own JRE setting uses the same JDK. Then load the sbt project, and if that fails, reload all sbt projects from the sbt tool window.

Q: Why are there two JDK settings to check?
A: The project SDK and the JRE that sbt runs with are configured in different places. If they disagree, the import can fail even though the project looks right.

Q: What's the recommended setup chain for the class?
A: IntelliJ with the Scala plugin, JDK 17, sbt 1.x and Scala 2.13. Create the project as Scala with sbt and let the first sync finish before writing code.

Q: What is a singleton object in Scala?
A: A type declared with the object keyword that has exactly one instance. Scala builds it into the language, so you don't need a design pattern like in Java.

Q: What is immutability?
A: Once something is created it can't be changed. If you want a different value, you create a new object, and the original stays the same.

Q: Why does immutability matter in distributed processing?
A: An immutable value can be shared across threads or executors safely, because no task can change it and corrupt another task's view of the data.

Q: What is data lineage?
A: The record of every step data goes through from input to output, with each stage preserved. It lets you trace backwards to find where a value changed or why a record was rejected.

Q: How does medallion architecture relate to lineage?
A: Bronze, Silver and Gold are preserved checkpoints. Because each layer is a real queryable table, you can follow one record through every layer.
