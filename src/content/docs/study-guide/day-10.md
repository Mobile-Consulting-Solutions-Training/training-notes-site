---
title: Study Guide - Day 10
description: "Quick summary, cheat sheet, and verbal-quiz flashcards for Training 10: Scala Fundamentals (Continued)"
sidebar:
  order: 100
---

Study Guide - Day 10 (source: notes/Training 10.md)

Note: built for verbal-quiz prep - flashcards (Part 3) are phrased the way a quiz question would actually be asked out loud, with answers short enough to say aloud in a few sentences.

# Part 1: Quick Summary

**Case Classes.** Scala's class for immutable data: `case class Person(name: String, age: Int)`. You get for free: no `new` (companion `apply`), readable `toString`, equality by value, `copy()` to make a changed copy, and pattern matching. In Spark a case class defines a typed **Dataset[T]** schema (`.as[Sale]`, `spark.createDataset(people)`), so field names and types are checked at compile time, unlike `col("name")` strings in a DataFrame.

**Inheritance, Higher-Order Functions, Traits.** Inheritance = a child class gets a parent's fields and methods (`extends`). A higher-order function takes or returns a function (`map`, `filter`). Scala allows extending **one** class but mixing in any number of **traits** with `with` (`class Tiger extends Felis with HasStripes with HasFangs`), which is Scala's answer to multiple inheritance. Accessing a member a type doesn't have (`Buck.has_stripes`) is a compile error, not `false`.

**Nil, Null, null, Nothing, None, Unit.** `Nil` = empty list. `Null` = the trait/type of `null`. `null` = Java's null value. `Nothing` = bottom type, subtype of everything, no values (e.g. a method that always throws). `None` = the empty case of `Option`. `Unit` = Java's `void`, single value `()`.

**Option.** `Option[T]` is `Some(value)` or `None`, a type-safe replacement for `null` with a defined fallback. Handle it with pattern matching, `getOrElse`, `map` (runs only if a value exists) and `flatMap` (combine Options without nesting). Model optional fields as `Option` in case classes.

**flatMap.** `map` then flatten one level: `List(List(1,2), List(8,9)).flatMap(_.map(_*2))` = `List(2,4,16,18)`. Works on List, Option, Seq and Future.

**Companion Objects.** An `object` with the same name as a class, in the same file. Holds things about the type as a whole: shared values, factory methods, utilities; can access the class's private members. A case class's auto-generated companion is why `Person("Alice", 30)` works without `new`.

**Futures.** `Future[T]` = asynchronous result computed on another thread. Needs an `ExecutionContext` (`import scala.concurrent.ExecutionContext.Implicits.global`). `map` and `foreach` don't block; `Await.result` blocks (demos and tests only). This is not how Spark parallelizes; Spark uses driver/executors.

**Sealed Traits.** `sealed trait PaymentMethod` with `case class CreditCard`, `case class PayPal` and `case object Cash`. Sealed = all subtypes in the same file, so the compiler can check a `match` is **exhaustive**. Use `case object` for variants with no data.

**Implicits.** The compiler automatically supplies something you didn't pass. **Implicit parameters**: `def greet(name: String)(implicit greeting: String)` uses an `implicit val` of the matching type in scope. **Implicit conversions** change types; **implicit classes** add methods (`"Alice".shout()`). The search is by type, in implicit scope (local, imports, companion objects); two candidates of the same type cause an ambiguity error, so wrap config in its own type. Scala 3 renames them `given`/`using`.

**Implicits in Spark.** `import spark.implicits._` (after creating `spark`) provides `.toDS()`, `.toDF()`, `$"col"` syntax, `.as[T]`, and the **Encoder[T]** that tells Spark how to store a case class internally. Typed `map` needs an encoder for its output type too. `col("name")` is clearer than `$"name"` in production.

**Overloading vs Overriding.** Overloading = same name, different parameters, chosen at compile time. Overriding = subclass replaces an inherited method with `override`, chosen at runtime by the object's real type (runtime polymorphism).

**Closures.** A function that uses a variable from outside itself and keeps it even after the creating function returns (`createMultiplier(2)` → `double`). Spark closures are serialized and shipped to executors with everything they capture, so don't capture big or non-serializable objects (connections, `SparkSession`).

**Currying.** Turns `f(a, b, c)` into `f(a)(b)(c)`; shorthand `def f(a: Int)(b: Int)(c: Int)`; `.curried` does it mechanically. **Partial application** = supply some arguments and get back a function waiting for the rest. In ETL: `def filterCountry(country: String)(df: DataFrame): DataFrame` gives reusable `DataFrame => DataFrame` steps for `df.transform(...)`. Value is design, not performance.

**Priority.** Essential: map, flatMap, filter, Option, collections, case classes, pattern matching, higher-order functions, closures. Important for reading code: implicits, traits, companion objects, inheritance, overriding. Useful technique: currying and partial application.

---

# Part 2: Cheat Sheet

## Case Classes
- No `new` · `toString` · value equality · `copy()` · pattern matching
- Typed Dataset: `case class` = schema · `.as[T]` · `createDataset` / `.toDS()`

## Traits and Inheritance
- `extends` one class · `with` many traits
- Missing member = compile error

## Nothing-like Types
- `Nil` empty list · `Null` type of null · `null` value · `Nothing` bottom type · `None` empty Option · `Unit` void `()`

## Option
- `Some(x)` / `None` · `match` · `getOrElse` · `map` · `flatMap`

## Companion Objects
- Same name + same file · shared values, factories, utilities · private access

## Future
- `Future { }` async · `ExecutionContext` · `map`/`foreach` non-blocking · `Await` blocks

## Sealed
- Subtypes in same file → exhaustive `match` · `case object` for no-data variants

## Implicits
- Implicit params, conversions, implicit classes · search by type in scope
- Ambiguity error with two candidates · wrap config in its own type · Scala 3 `given`/`using`
- `import spark.implicits._` → `.toDS`, `.toDF`, `$"x"`, `.as[T]`, Encoders

## Overload vs Override
- Overload: same name, different params, compile time
- Override: subclass replaces, `override`, runtime

## Closures and Currying
- Closure captures outer variables · Spark ships captured values to executors
- Curry `f(a)(b)(c)` · partial application · `def step(cfg)(df): DataFrame` + `.transform`

---

# Part 3: Flashcards (Verbal Quiz Practice)

Q: What does making a class a case class give you?
A: You can create it without new, it gets a readable toString, equality compares field values, there's a copy method for making a changed copy, and it works in pattern matching.

Q: How does a case class help in Spark?
A: It defines the schema of a typed Dataset. Fields are accessed as real properties the compiler checks, instead of string column names that only fail at runtime.

Q: How does copy relate to immutability?
A: Copy creates a new object with some fields changed and leaves the original untouched, so you never modify the object in place.

Q: Does Scala support multiple inheritance?
A: A class can extend only one class, but it can mix in any number of traits with the with keyword. That gives the benefits of multiple inheritance without its ambiguity.

Q: What's a higher-order function?
A: A function that takes another function as a parameter or returns one, like map and filter.

Q: Explain Nil, null, None and Unit.
A: Nil is the empty list. null is Java's null value. None is the empty case of Option. Unit is the return type for methods that return nothing, like void in Java.

Q: What is Nothing?
A: The bottom type: a subtype of every type with no values. It's the return type of something that never returns normally, like a method that always throws.

Q: Why use Option instead of null?
A: Option forces you to handle both the Some and None cases, so you can't forget to check and crash with a null pointer exception. Methods like map and getOrElse handle the missing case safely.

Q: What's the difference between map and flatMap?
A: Map transforms each element. FlatMap transforms and then flattens one level, so a list of lists becomes one list, or an Option of an Option becomes one Option.

Q: What is a companion object?
A: An object with the same name as a class in the same file. It holds things that belong to the type as a whole, like shared values and factory methods, and can access the class's private members.

Q: What is a Future?
A: A value that will be available later, computed asynchronously on another thread so the caller doesn't block. You transform it with map and react with foreach.

Q: Is a Scala Future how Spark runs things in parallel?
A: No. Spark parallelizes through its driver and executors. Futures are for ordinary async code around a pipeline, like API or metadata calls.

Q: What does sealed do?
A: It requires all subtypes to be in the same file, so the compiler knows the full list and can warn if a match doesn't handle every case.

Q: What are implicits?
A: Values or conversions the compiler supplies automatically when you didn't pass them. It searches the implicit scope for something of the right type.

Q: What happens if two implicits of the same type are in scope?
A: You get an ambiguity error; Scala doesn't pick one. That's why implicit configuration should use its own type instead of plain String or Int.

Q: What does import spark.implicits._ give you?
A: Methods like toDS and toDF on Scala collections, the dollar-sign column syntax, as[T] conversions, and the Encoders Spark needs to store case classes. It has to come after the SparkSession is created.

Q: What's an Encoder in Spark?
A: The object that tells Spark how to convert a JVM type like a case class into its internal columnar format. Spark finds it implicitly whenever you create or map a Dataset.

Q: What's the difference between overloading and overriding?
A: Overloading is several methods with the same name but different parameters, chosen at compile time. Overriding is a subclass replacing an inherited method, chosen at runtime by the object's actual type.

Q: What is a closure?
A: A function that uses a variable defined outside itself and keeps access to it, even after the function that created it has returned.

Q: Why do closures matter in Spark?
A: Spark sends your functions to the executors along with every variable they capture. Capturing something large or non-serializable, like a database connection or the SparkSession, causes slowdowns or serialization errors.

Q: What is currying?
A: Turning a function of several arguments into a chain of one-argument functions, so f(a, b, c) becomes f(a)(b)(c).

Q: How is currying useful in ETL?
A: You can separate configuration from data. A function like filterCountry(country)(df) gives you reusable DataFrame-to-DataFrame steps that chain with df.transform.

Q: What's partial application?
A: Supplying some of a function's arguments now and getting back a function that waits for the rest.
