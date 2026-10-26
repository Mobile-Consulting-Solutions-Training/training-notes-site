---
title: Day 10 Vocabulary
description: Glossary of terms and definitions from the Training 10 notes.
sidebar:
  order: 10
---

Vocabulary — Study Guide Day 10

Source: notes/Training 10.md

## Case Classes and Datasets
- **case class** — A Scala class for immutable data that auto-generates `apply`, `toString`, structural equality, `copy()` and pattern-matching support.
- **Immutability** — Once created, a value cannot be altered; to change it you create a new version.
- **apply() factory method** — Auto-generated companion-object method that lets a case class be created without `new`.
- **Structural equality** — Comparing two objects by their field values rather than by object reference identity.
- **copy()** — Case class method that creates a new instance with some fields changed, leaving the original untouched.
- **Pattern matching** — Deconstructing a value inside a `match` expression with `case` branches.
- **Guard (in a case)** — An `if` condition added to a `case` pattern, e.g. `case Person(n, a) if a >= 18`.
- **DataFrame** — Spark's untyped table of rows where columns are referenced by string name, checked only at runtime.
- **Dataset[T]** — Spark's typed collection whose schema comes from a case class, so field access is checked at compile time.
- **Schema** — The column names and types of a dataset; in Scala a case class's fields define it.
- **SparkSession** — The entry point to Spark, built with `SparkSession.builder()`.
- **appName** — Builder setting that names the Spark application.
- **master("local[*]")** — Builder setting that runs Spark locally using all available CPU cores.
- **getOrCreate()** — Returns an existing SparkSession or creates a new one.
- **spark.createDataset** — Converts a local Scala collection into a typed `Dataset`.
- **spark.createDataFrame** — Converts a local Scala collection into an untyped `DataFrame`.
- **show()** — Prints a DataFrame or Dataset's rows to the console.
- **printSchema()** — Prints a DataFrame or Dataset's column names and types.
- **spark.stop()** — Shuts down the SparkSession.
- **Seq** — A general ordered-collection trait in Scala with many implementations, such as `List`.

## Object-Oriented Concepts
- **Inheritance** — When a class consumes the properties and functions of a parent class.
- **Parent class (superclass)** — The class whose fields and methods are inherited.
- **Child class (subclass)** — A class that inherits from a parent using `extends`.
- **extends** — Scala keyword making a class inherit from exactly one parent class.
- **Trait** — A reusable unit of fields and methods that can be mixed into classes, like an interface that can hold implementation.
- **Mixin (with)** — Adding traits to a class with the `with` keyword, any number per class.
- **Multiple inheritance** — Gaining behavior from several parents; Scala allows only one parent class but many traits.
- **Linearization** — Scala's well-defined rules for resolving conflicts when multiple traits define the same member.
- **Singleton Object (object)** — A class with exactly one instance, created without `new`.
- **Compile-time safety** — Errors such as accessing a nonexistent field are caught before the program runs.

## Functional Programming
- **Higher-order function** — A function that takes a function as a parameter, returns one, or both.
- **filter** — Higher-order function that keeps only elements for which a predicate returns true.
- **map** — Higher-order function that applies a function to transform every element.
- **flatMap** — Maps each element then flattens the result one level, removing internal groupings.
- **Predicate** — A function returning true or false, used to decide which elements to keep.
- **Lambda (anonymous function)** — An unnamed function written inline, e.g. `p => p.age > 18`.
- **Underscore placeholder (_)** — Shorthand for a lambda's parameter, e.g. `_ * 2`.

## Nothing-Like Types
- **Nil** — Represents an empty list; typed as `List[Nothing]`.
- **Null** — A trait that represents a null value; the type of the `null` literal.
- **null** — The standard Java null value meaning no object reference.
- **Nothing** — Represents truly nothing; the bottom type, a subtype of every other type with no runtime values.
- **None** — Represents an absent value in an Option type.
- **Unit** — A return type equivalent to Java's void, with the single value `()`.
- **Bottom type** — A type that is a subtype of every other type, which in Scala is `Nothing`.
- **NullPointerException** — Runtime crash caused by using a null reference as if it held an object.

## Option
- **Option[T]** — The foundation of the Option/Some/None structure, giving either some value or no value with a defined fallback.
- **Some(value)** — The Option case meaning a value exists.
- **getOrElse** — Returns an Option's value if present, otherwise a supplied default.
- **Option.map** — Transforms the value only if it is `Some`; `None` stays `None`.
- **Option.flatMap** — Combines Options without producing a nested `Option[Option[T]]`.

## Companion Objects
- **Companion object** — An object with the exact same name as its class, in the same file, able to access the class's private members.
- **Instance method** — A method that belongs to and acts on one specific object.
- **Factory method** — A method that constructs and returns an instance, as an alternative to calling `new`.
- **Utility method** — A method that operates on instances of a type but belongs to the type as a whole.

## Futures and Asynchronous Programming
- **Future** — How asynchronous programming is done in Scala; a value that will exist eventually, computed on a separate thread.
- **Asynchronous programming** — Starting work that runs independently so the calling thread does not wait for it.
- **ExecutionContext** — The thread pool a Future runs on.
- **ExecutionContext.Implicits.global** — Scala's default general-purpose thread pool, imported as an implicit.
- **Future.map** — Transforms a Future's eventual result and returns a new Future without blocking.
- **Future.foreach** — Registers a side-effecting callback that runs when a Future's result is available.
- **Await.result** — Blocks the calling thread until a Future completes or a timeout expires; mainly for demos and tests.
- **Blocking** — Making a thread pause and wait for a result.
- **Thread.sleep** — Pauses the current thread for a given number of milliseconds.
- **Race condition** — When output order depends on which of two threads runs first.

## Sealed Traits
- **sealed trait** — A trait whose subtypes must all be declared in the same file, giving the compiler a closed set of alternatives.
- **case object** — A singleton variant with no data that works directly in pattern matching.
- **Exhaustive pattern matching** — The compiler verifies every subtype of a sealed trait is handled in a `match`.
- **Non-exhaustive match** — A compiler warning that a `match` misses at least one possible case.
- **Algebraic data type (sealed trait + case classes)** — Modelling a value as one of a fixed set of variants that can each carry different data, like a more powerful enum.

## Implicits
- **Implicits** — Let the compiler automatically supply something your code requires when you have not supplied it explicitly.
- **Implicit parameter** — A parameter in an `implicit` parameter list that the compiler fills from scope.
- **Implicit conversion** — Automatic conversion of one type to another to fix a type mismatch, e.g. `implicit def stringToInt`.
- **Implicit scope** — The set of places Scala searches for an implicit value or conversion of a needed type: lexical context, imports and companion objects.
- **implicit class (enrichment)** — Adds new methods to an existing type, such as giving `String` a `shout()` method.
- **Ambiguous implicits** — A compile error when two eligible implicits of the same type are in scope.
- **implicitly[T]** — Asks the compiler to return the implicit value of type T it would supply automatically.
- **import spark.implicits._** — Brings a SparkSession's implicit encoders and conversions into scope; must come after the session is created.
- **given / using** — Scala 3's replacements for Scala 2 `implicit` values and parameters.
- **Contextual abstractions** — Scala 3's name for the implicits concept.

## Spark Implicits, Encoders and Column Syntax
- **Encoder[T]** — Tells Spark how to convert a JVM object of type T to and from Spark SQL's internal columnar format.
- **.toDS()** — Implicit-powered method converting a Scala collection into a typed Dataset.
- **.toDF()** — Implicit-powered method converting a Scala collection into a DataFrame with given column names.
- **.as[T]** — Converts a DataFrame (`Dataset[Row]`) into a typed `Dataset[T]`, or types a column.
- **Dataset[Row]** — What a DataFrame effectively is: an untyped Dataset of rows.
- **$"column"** — Implicit shorthand for creating a Spark Column reference.
- **col()** — Function from `org.apache.spark.sql.functions` that references a column by name; the teacher's production preference.
- **isNotNull** — Column method that keeps rows where the column has a value.
- **Typed transformation** — A Dataset operation like `map` that produces a new typed Dataset and needs an Encoder for its output type.
- **PipelineConfig pattern** — Passing your own pipeline configuration to functions as an implicit parameter.
- **Driver and Executors** — Spark's own distributed execution model, separate from Scala Futures.

## Overloading and Overriding
- **Overloading** — Defining multiple methods with the same name but different parameter lists; the compiler picks one from the arguments.
- **Overriding** — A subclass providing a new implementation of a method it inherited from a parent class or trait.
- **override** — Required Scala keyword marking a method as intentionally replacing an inherited one.
- **Compile-time polymorphism** — Choosing which method runs before the program runs, as with overloading.
- **Runtime polymorphism** — Choosing the implementation from the object's actual type at runtime, as with overriding.
- **Method signature** — A method's name plus its parameter types.

## Closures
- **Closure** — A function that uses a variable defined outside the function itself, closing over it and retaining access even after the creating scope returns.
- **Lexical scope** — The surrounding code region where a variable is defined and visible.
- **Closure serialization** — Spark sending a function and its captured values from the driver to executors, which fails or slows down if they capture non-serializable or large objects.

## Currying
- **Currying** — Transforming `f(a, b, c)` into `f(a)(b)(c)`, where each stage takes one argument and returns another function until the final result.
- **Partial application** — Supplying some arguments now and getting back a function that waits for the rest.
- **Multiple parameter lists** — Scala syntax `def f(a)(b)(c)` that supports curried-style calling.
- **.curried** — Built-in method that converts a multi-argument function into a chain of one-argument functions.
- **Function type (A => B)** — The type of a function taking A and returning B, e.g. `Int => Int`.
- **Parameterized transformation factory** — A curried function that builds reusable, pre-configured transformations such as `above1000`.
- **DataFrame => DataFrame** — The common shape of curried transformation functions that makes them composable.
- **.transform** — Spark method that applies a `DataFrame => DataFrame` function, enabling chained pipeline steps.
- **saveAsTable** — Spark write method that saves a DataFrame as a named table.
- **mode("overwrite")** — Write option that replaces existing data in the target.
