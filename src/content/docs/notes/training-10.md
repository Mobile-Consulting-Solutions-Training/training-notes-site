---
title: Training 10 - Scala Fundamentals (Continued)
description: Case classes, traits/inheritance/mixins, the Nil/Null/null/Nothing/None/Unit distinctions, the Option type, flatMap, and companion objects.
sidebar:
  order: 10
---

Teacher: Evan Flint

Syllabus Day 11 (per file numbering) - actual coverage: continuing Scala Fundamentals from `Training 9.md` (Singleton Object, Immutability, IntelliJ/sbt setup) into more Scala language features, following directly from yesterday's Scala Spark homework (`homework/submission/alex_jackson_scala_spark_homework/`). Note: this continues the pacing drift already visible in `Training 6.md`-`Training 9.md` - this session's content lines up with the roadmap's Day 12 topic ("Scala Advanced") rather than its own nominal Day 11 slot.

---

# Scala Fundamentals (continued)

Q. What is a case class?

A. A `case class` is a Scala class for immutable data: the compiler generates `apply`, `toString`, value-based `equals`/`hashCode`, `copy`, and pattern-matching support for you.

Expanded: a `case class` is Scala's special-purpose class for representing **immutable data** - directly the practical, everyday application of yesterday's Immutability principle ("once something has been created, it cannot itself be altered - if you want to alter it, you need to create a new version"). Declaring a class with the `case` keyword tells the compiler to automatically generate a bunch of boilerplate that you'd otherwise have to write by hand for a normal `class`:

```scala
case class Person(name: String, age: Int)
```

**What `case` automatically gives you, for free:**

| Feature | What it means |
|---|---|
| No `new` required | `Person("Alice", 30)` works directly - a companion object with an `apply()` factory method is auto-generated |
| Auto-generated `toString` | `println(Person("Alice", 30))` prints `Person(Alice,30)`, not a meaningless memory address like a normal `class` would |
| Structural equality (`equals`/`hashCode`) | `Person("Alice", 30) == Person("Alice", 30)` is `true` - compares by field *values*, not by object reference identity (unlike a plain `class`) |
| `copy()` method | Creates a **new** instance with some fields changed, leaving the original completely untouched - this is the concrete mechanism behind yesterday's Immutability rule: `alice.copy(age = 31)` produces a brand-new `Person`, `alice` itself never changes |
| Pattern-matching support | Can be deconstructed directly inside a `match` expression (ties to yesterday's `match`/`case` coverage) |

**Example showing the immutability connection directly:**
```scala
val alice = Person("Alice", 30)
val olderAlice = alice.copy(age = 31)

println(alice)       // Person(Alice,30)  - unchanged
println(olderAlice)  // Person(Alice,31)  - a separate, new object
```

**Pattern matching example:**
```scala
alice match {
  case Person(n, a) if a >= 18 => s"$n is an adult"
  case Person(n, _) => s"$n is a minor"
}
```

**Why this matters for Spark specifically (ties to yesterday's `SalesAnalysis.scala` homework):** that homework used untyped `DataFrame`s, where every column is accessed by a String name (`col("sales_amount")`) - no compile-time checking that the column actually exists or has the right type; a typo like `col("sales_amont")` only fails at runtime. A `case class` can instead define a Spark **`Dataset[T]`** schema directly in code:
```scala
case class Sale(orderNumber: Int, productNumber: String, quantity: Int, price: Double)

val sales = spark.read.jdbc(JDBC_URL, "gold.fact_sales", jdbcProperties).as[Sale]
sales.filter(_.price > 1000)   // compiler checks .price actually exists on Sale
```
This is the more type-safe alternative to the DataFrame/`col()` string-based approach used in yesterday's homework - worth remembering as the more "structured ETL pipeline" direction the syllabus flagged as coming up.

Expanded (correction / gotcha): `.as[Sale]` maps columns to case-class fields **by name**, and it needs `import spark.implicits._` in scope. The Postgres table's columns are snake_case (`order_number`, `product_number`), so the camelCase `Sale` above would fail at runtime with an error like `cannot resolve 'orderNumber'`. Either name the fields to match the columns, or rename first:

```scala
import spark.implicits._

val sales = spark.read.jdbc(JDBC_URL, "gold.fact_sales", jdbcProperties)
  .withColumnRenamed("order_number", "orderNumber")
  .withColumnRenamed("product_number", "productNumber")
  .as[Sale]
```

Column types must also be compatible (e.g. a Postgres `numeric` arrives as `DecimalType`, which won't upcast to `Int` automatically - cast it first).

**Interview line ("Dataset vs DataFrame in Scala - when would you use each?"):** "A DataFrame is just `Dataset[Row]` - columns are checked only at runtime, and Catalyst can optimize everything. A `Dataset[T]` with a case class gives compile-time type safety and lets me write plain Scala lambdas on typed objects. I use DataFrames for most SQL-style transformations, and Datasets when the domain model and type checking matter; typed lambdas are opaque to Catalyst, so they can be a bit slower." (Full comparison table: Training 7, RDD vs DataFrame vs Dataset.)

---

## Worked Example (Teacher's Code): `case class` + `Dataset[Person]`

```scala
import org.apache.spark.sql.SparkSession

object CaseClassExample {

  // Define schema using case class
  case class Person(id: Int, name: String, age: Int)

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder()
      .appName("Case Class Dataset Example")
      .master("local[*]")
      .getOrCreate()

    import spark.implicits._

    // Create instances (no CSV needed)
    val people = Seq(
      Person(1, "Alice", 30),
      Person(2, "Bob", 25),
      Person(3, "Charlie", 35)
    )

    // Convert to Dataset[Person]
//    val df = spark.createDataFrame(people)
//
//    df.show()
//    df.printSchema()

    val ds = spark.createDataset(people)

    ds.show()
    ds.printSchema()

    spark.stop()
  }
}
```

Expanded: a few details worth noticing in this exact example:

- **`case class Person(id: Int, name: String, age: Int)`** *is* the schema - defining the case class's fields directly defines what columns the resulting Dataset will have, with their real types (`Int`, `String`) already attached. No separate schema declaration step needed, unlike a raw DataFrame built from untyped data.
- **`import spark.implicits._`** - this import is what makes `spark.createDataset(people)` (and `.as[Sale]` from the Expanded section above) actually work. It brings implicit conversions into scope that let Spark automatically figure out how to encode/decode a case class into its internal columnar format - without this import, `createDataset` wouldn't compile.
- **"Create instances (no CSV needed)"** - the comment is making an explicit point: `Seq(Person(1, "Alice", 30), ...)` builds sample data directly in code, in-memory, with no file I/O at all - useful for examples/testing, as opposed to every other data source covered so far in this course (Postgres via JDBC, CSVs for Hive `LOAD DATA`, etc.).
- **The commented-out `createDataFrame(people)` block** is a deliberate side-by-side comparison left in the code - `spark.createDataFrame(people)` would produce an untyped `DataFrame` (columns accessed by string name, like `col("name")`, same as yesterday's `SalesAnalysis.scala` homework), while `spark.createDataset(people)` produces a **typed** `Dataset[Person]` (columns accessible via real Scala field access, e.g. `.name`, with compiler-checked types) - the exact DataFrame-vs-Dataset distinction already discussed above, now shown as two lines of near-identical code you could swap between.

---

## Other Terms Introduced in Class Chat Today

*(Shared in class chat by a student - not the teacher directly, but accepted as correct in context.)*

---

Q. What is inheritance?

A. (Shared in class chat by a student) Inheritance is when you consume the properties/functions of a parent class/object.

Expanded: inheritance lets one class (a "child"/"subclass") automatically gain all the fields and methods already defined on another class (the "parent"/"superclass"), without having to redeclare them. This is a standard OOP concept, not Scala-specific, but Scala supports it the same way Java does (`class Child extends Parent`). See the `TraitTest` worked example directly below for Scala code (`extends` + `with` mixins).

---

Q. What are higher-order functions?

A. (Shared in class chat by a student) Higher-order functions are functions that can take a function as a parameter.

Expanded: this is a core functional-programming concept Scala leans on heavily (same functional-programming lineage as yesterday's Immutability principle). A higher-order function either accepts another function as an argument, returns a function as its result, or both. Two concrete examples were flagged directly alongside this definition in the chat: `filter` and `map` - both are methods on Scala collections (and Spark DataFrames/Datasets) that take a function as their argument (e.g. `people.filter(p => p.age > 18)` - the `p => p.age > 18` part is itself a function, passed *into* `filter`). This is the same underlying mechanism behind every `.filter(...)`/`.map(...)` call already used throughout this course's Spark code (including yesterday's `SalesAnalysis.scala` homework's `.filter(col("sales_amount") > 1000)`), just not named explicitly as "higher-order functions" until now.

| Term | Meaning |
|---|---|
| Higher-order function | A function that takes another function as a parameter, returns one, or both |
| `filter` | Example - takes a function (a predicate returning true/false) and uses it to decide which elements to keep |
| `map` | Example - takes a function and applies it to transform every element |

---

## Worked Example: Traits, Inheritance, and Mixins (`TraitTest`)

Direct answer to "does Scala support multiple inheritance?" from earlier today - here's the concrete code:

```scala
object TraitTest {

  trait HasFangs {
    val has_fangs = true
  }

  trait HasStripes {
    val has_stripes = true
  }

  class Animal {
    val moves = true
  }

  class Canis extends Animal {
    val is_dog = true
  }

  class Felis extends Animal {
    val is_dog = false
  }

  class Dog extends Canis {
    val sound = "woof"
  }

  class Wolf extends Canis {
    val sound = "howl"
  }

  class Cat extends Felis {
    val sound = "meow"
  }

  class Tiger extends Felis with HasStripes with HasFangs {
    val sound = "growl"
  }

  val Sparky = new Dog()
  val Mittens = new Cat()
  val Hobbes = new Tiger()
  val Buck = new Wolf()

  def main(args: Array[String]): Unit = {
    // println("Sparky " + Sparky.is_dog)
    println("Mittens " + Mittens.is_dog)
    // println("Hobbes " + Hobbes.has_stripes)
    // println("Hobbes " + Hobbes.has_fangs)
    // println("Buck " + Buck.has_stripes)
  }
}
```

Expanded - the key line that answers today's earlier question directly:

```scala
class Tiger extends Felis with HasStripes with HasFangs { ... }
```

This is Scala's actual answer to "multiple inheritance": a class can `extends` exactly **one** other class (single inheritance, same restriction as Java), but can mix in **any number of traits** via chained `with` keywords. Traits are how Scala gets the practical benefit of multiple inheritance (gaining behavior/fields from several sources at once) without the classic ambiguity problems true multiple class-inheritance can cause (e.g. "which parent's version of a field wins if two parents both define it") - traits have their own well-defined linearization rules for resolving that.

**Class hierarchy this example builds:**
```text
Animal (moves)
├── Canis (is_dog = true)
│   ├── Dog (sound = "woof")
│   └── Wolf (sound = "howl")
└── Felis (is_dog = false)
    ├── Cat (sound = "meow")
    └── Tiger (sound = "growl") with HasStripes, HasFangs
```

**Worth noticing - `is_dog` isn't inherited/overridden, it's independently redeclared:** `Animal` itself never declares `is_dog` at all - `Canis` and `Felis` each independently add their *own* `is_dog` field (`true` and `false` respectively). This isn't polymorphic overriding of a shared parent field, it's two sibling subclasses coincidentally choosing the same field name with different values - worth distinguishing from true method overriding.

**Where the instances live:** `Sparky`, `Mittens`, `Hobbes`, `Buck` are declared directly inside the `TraitTest` object body, not inside `main` - meaning they're fields of the Singleton Object itself (see `Training 9.md`'s Singleton Object entry), created once when `TraitTest` is first initialized, not re-created on every call to `main`.

**What the commented-out lines would actually do if uncommented - not all of them are equal:**

| Line | Would it compile? | Why |
|---|---|---|
| `Sparky.is_dog` | Yes | `Dog extends Canis`, and `Canis` declares `is_dog` |
| `Hobbes.has_stripes` | Yes | `Tiger` mixes in `HasStripes` directly |
| `Hobbes.has_fangs` | Yes | `Tiger` mixes in `HasFangs` directly |
| `Buck.has_stripes` | **No - compile error** | `Wolf extends Canis` only - no trait ever mixed in, so `Wolf` (and its ancestors `Canis`/`Animal`) never gained `has_stripes` at all |

That last row is the most instructive one - it's not that `Buck.has_stripes` would print `false`, it wouldn't compile *at all*, since `has_stripes` simply doesn't exist anywhere in `Wolf`'s type hierarchy. This is exactly the kind of compile-time safety `Training 10.md`'s earlier `Dataset[Person]` section flagged as an advantage over untyped/stringly-typed access - a typo or a wrong assumption about what a type has gets caught before the program ever runs, not silently at runtime.

---

Q. What's the difference between a trait and an abstract class?

A. Both can have abstract and concrete members, but a class can mix in many traits and extend only one (abstract) class.

Expanded:

| | Trait | Abstract class |
|---|---|---|
| How many per class | Many (`extends A with B with C`) | One |
| Constructor parameters | Not in Scala 2 (allowed in Scala 3) | Yes |
| Conflicting methods | Resolved by **linearization** - the right-most trait's version wins, and `super` calls go right-to-left | N/A (single parent) |
| Java interop | Compiles to a Java interface (with default methods) | Compiles to a Java abstract class - easiest to extend from Java |
| Use for | Reusable behavior to mix in (`HasStripes`) | A base type that needs constructor params or Java callers |

**Interview line:** "Use a trait for mixable behavior, since a class can mix in many; use an abstract class when you need constructor parameters or Java code needs to extend it."

**Interview line ("case class vs class"):** "A case class is for immutable data - the compiler gives me `apply`, value-based equality, `toString`, `copy` and pattern matching. A regular class compares by reference and gets none of that, so I use it for behavior or mutable state."

---

## Scala Basics the Class Skipped (Roadmap Topics)

Q. What's the difference between `val`, `var`, and `lazy val`?

A. `val` is an immutable reference, `var` can be reassigned, and `lazy val` is a `val` computed only the first time it is used.

Expanded:

| Keyword | Reassignable? | When evaluated | Example |
|---|---|---|---|
| `val` | No (default choice in Scala) | Immediately | `val rate = 0.08` |
| `var` | Yes | Immediately | `var count = 0; count += 1` |
| `lazy val` | No | Once, on first access, then cached | `lazy val conf = loadConfig()` |

`val` makes the *reference* immutable, not the object: `val buf = scala.collection.mutable.ListBuffer(1)` can still be appended to.

**Interview line:** "`val` can't be reassigned and is the default; `var` can, and I avoid it; `lazy val` is a `val` whose value is computed on first use and then cached - handy for expensive setup like a connection or config."

---

Q. What are the main Scala collections?

A. Immutable `List`, `Vector`, `Set` and `Map` by default (from `scala.collection.immutable`), with mutable versions in `scala.collection.mutable`, plus Java-style `Array`.

Expanded:

| Collection | Ordered? | Notes |
|---|---|---|
| `Seq` | Yes | General trait for ordered sequences; `List` and `Vector` are implementations |
| `List` | Yes | Immutable linked list - fast head/prepend, slow index access |
| `Vector` | Yes | Immutable, fast random access and append |
| `Array` | Yes | Mutable, fixed size, a Java array underneath |
| `Set` | No | Unique elements |
| `Map` | No | Key -> value pairs, e.g. `Map("a" -> 1)` |
| `ListBuffer`, `ArrayBuffer`, `mutable.Map` | - | Mutable versions, from `scala.collection.mutable` |

Common methods: `map`, `filter`, `flatMap`, `foldLeft(0)(_ + _)`, `reduce(_ + _)`, `groupBy(_.dept)`, `zip`, `mkString(", ")`, `sortBy`, `take`.

---

Q. How do you handle errors the Scala way (`Try` and `Either`)?

A. Wrap code that can fail in `Try` (giving `Success` or `Failure`), or return `Either[Error, Value]` (`Left` = error, `Right` = value), instead of throwing exceptions through your pipeline.

Expanded:

```scala
import scala.util.{Try, Success, Failure}

val parsed: Try[Int] = Try("42x".toInt)
parsed match {
  case Success(n)  => println(n)
  case Failure(ex) => println(s"Bad input: ${ex.getMessage}")
}

def parseAge(s: String): Either[String, Int] =
  s.toIntOption.toRight(s"'$s' is not a number")   // Left(error) or Right(age)
```

| Type | Cases | Use when |
|---|---|---|
| `Option[T]` | `Some` / `None` | A value may be missing (no reason needed) |
| `Try[T]` | `Success` / `Failure(exception)` | Wrapping code that throws (parsing, I/O) |
| `Either[E, T]` | `Left(error)` / `Right(value)` | You want a custom error type, e.g. sending bad ETL rows to a rejects table |

---

Q. What is a for-comprehension?

A. Syntactic sugar for chained `flatMap`/`map` (and `withFilter`) calls - it works on `List`, `Option`, `Try`, `Future`, and any type with those methods.

Expanded: the nested `flatMap { ... map ... }` used in the Option example below can be written as:

```scala
val result = for {
  e <- email   // Option[String]
  a <- age     // Option[Int]
} yield s"$e is $a"
// same as: email.flatMap(e => age.map(a => s"$e is $a"))
```

If any step is `None` (or `Failure`), the whole result is `None`.

---

Q. What are function values, string interpolation, and tuples?

A. Three everyday Scala features: functions stored in `val`s, `s""`/`f""` strings, and fixed-size groupings of mixed types.

Expanded:

| Feature | Example | Note |
|---|---|---|
| `def` method | `def add(x: Int, y: Int): Int = x + y` | A method on an object/class |
| Function value | `val add = (x: Int, y: Int) => x + y` | A first-class value - can be passed to `map`/`filter` |
| `s` interpolation | `s"Hello $name, total ${a + b}"` | Inserts values |
| `f` interpolation | `f"$price%.2f"` | printf-style formatting |
| Tuple | `val t = ("Alice", 30); t._1` | Fixed size, mixed types; destructure with `val (n, a) = t` |

---

## The "Nothing-Like" Types: `Nil` vs `Null` vs `null` vs `Nothing` vs `None` vs `Unit`

Q. What's the difference between `Nil`, `Null`, `null`, `Nothing`, `None`, and `Unit`?

A. (Teacher's definition)
- **Nil** - represents an empty list.
- **Null** - a trait that represents a null value.
- **null** - the standard Java null value.
- **Nothing** - represents truly nothing.
- **None** - represents an absent value in an option type.
- **Unit** - a return type that is equivalent to Java's void, basically returning nothing.

Expanded: six distinct concepts that are easy to blur together, but each solves a genuinely different problem:

| Term | What it actually is | Example |
|---|---|---|
| `Nil` | A concrete singleton object - the empty `List` | `val empty = Nil` or `List()` |
| `Null` | A *type* - the type of the `null` literal itself, a subtype of every reference type (`AnyRef`); only reference types can hold it | Rarely written directly - it's the inferred type of `null` |
| `null` | The actual *value* (lowercase) - Scala's inherited-from-Java "no object" reference | `var x: String = null` |
| `Nothing` | The *bottom type* - a subtype of every other type in Scala; no real value of type `Nothing` ever exists at runtime, used for computations that never return normally (e.g. always throwing) | `def fail(): Nothing = throw new Exception("boom")` |
| `None` | A concrete singleton object - one of `Option[T]`'s two cases (the other being `Some(value)`), representing "no value," the type-safe alternative to `null` | `val missing: Option[String] = None` |
| `Unit` | A *type* - the return type for expressions/methods that don't produce a meaningful value, Scala's equivalent of Java's `void`. Has exactly one possible value, written `()` | `def printIt(): Unit = println("hi")` |

Expanded (correction): `Null` is not a trait. In Scala 2 it is a final abstract **class** (in Scala 3 it is a special built-in type) - the subtype of every reference type, whose only value is `null`.

**Why `Nil` connects to `Nothing`:** `Nil` is actually typed as `List[Nothing]` - which works precisely because `Nothing` is a subtype of everything, so an empty list can be safely treated as a `List[Int]`, `List[String]`, or any other list type with zero type-checking issues, since it contains no elements to type-check in the first place.

**Why this matters practically:** `None`/`Option` exists specifically to make `null`/`Null` largely unnecessary in idiomatic Scala - see the Option coverage directly below.

---

## Scala's `Option` Type

Q. What is Scala's Option type?

A. (Teacher's definition) It's part of the Option/Some/None structure. Basically it's there in order to provide a sort of conditional where there is either some value or there is no value.

Expanded: `Option[T]` is Scala's type-safe replacement for using `null` to represent "no value" (directly connecting to the `None` row in the table above). It has exactly two possible states: `Some(value)` (a value genuinely exists) or `None` (no value exists) - and critically, the type system *forces* you to handle both cases before you can use the value, unlike `null`, which lets you forget to check and crash at runtime with a `NullPointerException`. See the full worked example below for `Option` used in practice (pattern matching, `getOrElse`, `map`, `flatMap`).

A. (Teacher's definition, fuller restatement) Option type is the foundation of the Option/Some/None construction, which is used to make programs that need data to fill variables into something flexible - if the values exist, then we get a result populated with them - if the values do not exist, we have a defined fallback.

Expanded: this reframes the same idea in terms of *why* it's useful, not just what it is - `Option` exists for exactly the situation this course's own data keeps running into (e.g. `gold.fact_sales` having no customer link, or `bronze.sales.customer_id` being `NULL` for historical rows, from `Training 8.md`/`Training 9.md`). Real data is frequently incomplete, and a program that needs to "fill a variable" from that data needs a defined, type-safe way to handle both outcomes - `Some(value)` when the data is actually there, and a **defined fallback** (`None`, handled via `getOrElse` or pattern matching, per the `OptionExample` below) when it isn't - rather than the program crashing or silently producing garbage when a value turns out to be missing.

---

## Worked Example: `flatMap` on Nested Lists

```scala
val myList = List(
  List(1, 2),
  List(8, 9),
  List(3, 4, 5)
)

val flatMappedList = myList.flatMap(x => x.map(_ * 2))

println(flatMappedList)
```

---

Q. What does `flatMap` actually do differently from `map`?

A. (Teacher's definition) [flatMap] flattens the list, or brings all the sub-elements to the top level. It removes internal groupings.

Expanded, tracing through the example step by step:
1. `myList` is a list of lists: `List(List(1, 2), List(8, 9), List(3, 4, 5))`.
2. For each inner list `x`, `x.map(_ * 2)` doubles every element: `List(1,2)` → `List(2,4)`, `List(8,9)` → `List(16,18)`, `List(3,4,5)` → `List(6,8,10)`.
3. If this were plain `.map(x => x.map(_ * 2))` (no `flatMap`), the result would *still be nested*: `List(List(2,4), List(16,18), List(6,8,10))`.
4. `flatMap` additionally **flattens** that nested result by one level, merging all the inner lists' elements into a single top-level list: `List(2, 4, 16, 18, 6, 8, 10)`.

So `flatMap` = `map` + flatten, always in that order - it's literally a contraction of the two operations, which is exactly why it's named that. This same "map + flatten" idea reappears below applied to `Option` instead of `List` - `flatMap` isn't List-specific, it works on any container type that supports it (`List`, `Option`, `Seq`, etc.), and `Seq` itself is a general trait with many implementations (`List`, `Vector`, `ArrayBuffer`) - see the Collections table in this file.

---

## Worked Example: `Option` in Practice (`OptionExample`)

```scala
object OptionExample {

  case class Person(
    id: Int,
    name: String,
    email: Option[String],
    age: Option[Int]
  )

  def main(args: Array[String]): Unit = {

    // Some means a value exists
    val person1 = Person(
      1,
      "Alice",
      Some("alice@example.com"),
      Some(30)
    )

    // None means the value is missing
    val person2 = Person(
      2,
      "Bob",
      None,
      None
    )

    println("=== Raw Option values ===")

    println(person1.email) // Some(alice@example.com)
    println(person2.email) // None


    // --------------------------------------------------
    // 1. Pattern matching
    // --------------------------------------------------

    println("\n=== Pattern Matching ===")

    def printEmail(person: Person): Unit = {
      person.email match {
        case Some(email) =>
          println(s"${person.name}'s email is $email")

        case None =>
          println(s"${person.name} does not have an email")
      }
    }

    printEmail(person1)
    printEmail(person2)


    // --------------------------------------------------
    // 2. getOrElse
    // --------------------------------------------------

    println("\n=== getOrElse ===")

    println(
      person1.email.getOrElse("No email provided")
    )

    println(
      person2.email.getOrElse("No email provided")
    )


    // --------------------------------------------------
    // 3. map
    // --------------------------------------------------

    println("\n=== map ===")

    val upperEmail1 =
      person1.email.map(_.toUpperCase)

    val upperEmail2 =
      person2.email.map(_.toUpperCase)

    println(upperEmail1) // Some(ALICE@EXAMPLE.COM)
    println(upperEmail2) // None


    // --------------------------------------------------
    // 4. Option avoids null checks
    // --------------------------------------------------

    println("\n=== Safe calculation ===")

    val ageNextYear1 =
      person1.age.map(_ + 1)

    val ageNextYear2 =
      person2.age.map(_ + 1)

    println(ageNextYear1) // Some(31)
    println(ageNextYear2) // None


    // --------------------------------------------------
    // 5. flatMap / combining Options
    // --------------------------------------------------

    println("\n=== Combining Options ===")

    val description1 =
      person1.email.flatMap { email =>
        person1.age.map { age =>
          s"${person1.name} is $age and can be contacted at $email"
        }
      }

    val description2 =
      person2.email.flatMap { email =>
        person2.age.map { age =>
          s"${person2.name} is $age and can be contacted at $email"
        }
      }

    println(description1)
    println(description2)
  }
}
```

Expanded - this example ties together nearly everything covered today into one place:

- **`email: Option[String]`, `age: Option[Int]` as case class fields** - the idiomatic Scala way to model "this field might legitimately be missing" directly in the schema itself (ties to `Training 10.md`'s earlier `case class`/`Dataset[Person]` coverage), instead of allowing `null` and hoping every caller remembers to check for it.
- **Section 1, pattern matching** - `person.email match { case Some(email) => ...; case None => ... }` is the same `match`/`case` syntax from yesterday's conditional-statements coverage, now destructuring an `Option` specifically. The compiler can verify both cases (`Some`/`None`) are handled - unlike checking `if (x != null)`, which is easy to forget.
- **Section 2, `getOrElse`** - unwraps the value if present, or supplies a fallback default if `None` - the simplest way to "escape" the `Option` wrapper when you just need a plain value and have a sensible default.
- **Section 3, `map`** - confirms today's Higher-Order Functions definition applies to `Option` too, not just collections: `person.email.map(_.toUpperCase)` only actually runs `.toUpperCase` if a value is present (`Some`) - on `None`, `map` just safely stays `None`, no function ever gets called, no crash.
- **Section 4, "Option avoids null checks"** - `person.age.map(_ + 1)` is the direct illustration of *why* this matters: doing `person.age + 1` on a `null`/missing age in a null-based world would throw a `NullPointerException`; doing it through `Option.map` instead just safely propagates `None` through - the absence of a value doesn't crash the program, it just flows through as "still absent."
- **Section 5, `flatMap` combining two Options** - this is the direct real-world payoff of the `flatMap`-on-lists lesson just above, applied to `Option` instead: `person1.age.map { age => s"...$age..." }` produces an `Option[String]` (not a plain `String`), so nesting it inside `person1.email.map { email => ... }` would produce `Option[Option[String]]` - a doubly-wrapped, awkward result. Using `flatMap` on the outer `Option` instead flattens that extra layer away, giving back a clean single `Option[String]` - exactly the same "map + flatten" idea as the nested-`List` example above, just operating on `Option` instead of `List`.

---

## Companion Objects

Q. What is a companion object?

A. (Teacher's definition) An object with the exact same name as its class, contained in the same file as the class.

Expanded: a companion object is a specific, special case of the Singleton Object concept from `Training 9.md` - it's still just an `object` (single-instance, no `new` needed), but the language grants it a privileged relationship with a `class` sharing its exact name *in the same file*: the companion object can access the class's private members, and idiomatically, it's where you put functionality that's about the type as a whole rather than about one specific instance (shared constants, factory methods, utility functions).

```scala
class Person(val name: String, val age: Int) {

  // Instance method - belongs to each Person object
  def introduce(): Unit = {
    println(s"My name is $name and I am $age years old.")
  }
}

// Companion object
// Same name as the class, in the same file
object Person {

  // Shared value
  val species = "Human"

  // Factory method
  def create(name: String, age: Int): Person = {
    new Person(name, age)
  }

  // Utility method
  def isAdult(person: Person): Boolean = {
    person.age >= 18
  }
}

object CompanionObjectExample {

  def main(args: Array[String]): Unit = {

    // Normal constructor
    val person1 = new Person("Alice", 30)

    // Factory method from companion object
    val person2 = Person.create("Bob", 16)

    // Instance methods
    person1.introduce()
    person2.introduce()

    // Access companion object directly
    println(Person.species)

    println(Person.isAdult(person1))
    println(Person.isAdult(person2))
  }
}
```

Expanded, breaking down the roles at play:

| Piece | What it is | Belongs to |
|---|---|---|
| `class Person(...)` | The instance-level blueprint - each `new Person(...)` call creates a separate object with its own `name`/`age` | Individual instances |
| `person.introduce()` | An **instance method** - only makes sense in the context of one specific `Person` | One instance at a time |
| `object Person { ... }` | The **companion object** - a single, shared object living alongside the class, same name, same file | The type as a whole, not any one instance |
| `Person.species` | A value shared across *all* `Person`s - doesn't belong to any single instance, so it lives on the companion object instead of the class | The type as a whole |
| `Person.create(...)` | A **factory method** - an alternative way to construct a `Person` without writing `new` directly - useful when construction needs extra logic beyond a bare constructor call | The type as a whole |
| `Person.isAdult(person)` | A **utility method** - operates *on* a `Person` passed in, but isn't really "part of" any specific person's own behavior | The type as a whole |

**This is exactly the same pattern already seen without the name "companion object" attached to it:** yesterday's `case class` coverage (`Training 10.md`, earlier in this file) mentioned that `case class` auto-generates a companion object with an `apply()` factory method, which is precisely *why* `Person("Alice", 30)` works without `new` for a case class - a hand-written companion object with its own `create()` method (as in this example) is the manual, non-`case`-class version of that same mechanism.

---

## Future Classes - Asynchronous Programming in Scala

Q. What are Future classes, and what are they for?

A. (Teacher's definition) Future Classes - how asynchronous programming is done in Scala.

```scala
import scala.concurrent.Future
import scala.concurrent.ExecutionContext.Implicits.global
import scala.concurrent.Await
import scala.concurrent.duration._

object FutureExample {

  def main(args: Array[String]): Unit = {

    println("1. Program starts")

    // This code runs asynchronously
    val myFuture: Future[Int] = Future {

      println("2. Future starts working...")

      Thread.sleep(3000)

      println("3. Future finishes")

      10
    }

    // Main thread continues without waiting
    println("4. Main program continues")


    // map transforms the result of the Future
    val mappedFuture: Future[Int] =
      myFuture.map(x => x * 2)


    // foreach runs when the result becomes available
    mappedFuture.foreach(result =>
      println(s"5. Future result: $result")
    )


    // Keep program alive long enough to see result
    Await.result(mappedFuture, 5.seconds)

    println("6. Program ends")
  }
}
```

Expanded: `Future[T]` represents a value that will exist *eventually*, computed on a separate thread without blocking the thread that created it. Tracing through what this program actually prints, and in what order, is the best way to understand it:

**Expected output order:**
```text
1. Program starts
4. Main program continues
2. Future starts working...
(~3 second pause)
3. Future finishes
5. Future result: 20
6. Program ends
```

**Why lines 1 and 4 print before line 2 (usually):** the moment `Future { ... }` is written, Scala hands that block off to run on a *different* thread (from the `ExecutionContext` imported at the top) and immediately returns control to `main` - it does not wait for the block to finish, or even necessarily to start. That's why `println("4. Main program continues")` typically executes before the Future's own `println("2. ...")` - the main thread races ahead while the Future's thread is just getting started. (This ordering isn't 100% guaranteed - it's a genuine race between two threads - but "4 before 2" is the overwhelmingly typical outcome.)

**Why `import scala.concurrent.ExecutionContext.Implicits.global` is required:** a `Future` needs to know *which thread pool* should actually run its code - this import brings a default, general-purpose thread pool into implicit scope, which `Future { ... }` then uses automatically without it needing to be passed explicitly every time.

**`.map` on a `Future` - the same higher-order function pattern, a third time:** `myFuture.map(x => x * 2)` is the exact same `map` concept already seen on `List` (doubling elements) and `Option` (transforming a value if present) from earlier in this file - here it transforms the Future's eventual result (`10` becomes `20`) once it's available, without blocking anything to do so. Also worth noting via today's Immutability lens: `.map` doesn't modify `myFuture` in place - it returns a **brand-new** `Future` (`mappedFuture`), leaving `myFuture` itself untouched, same as every other immutable transformation covered so far.

**`.foreach` on a `Future`:** registers a callback - "once this Future's value is ready, run this function on it" - without blocking. This is *also* a higher-order function (it takes a function as its argument), but unlike `.map`, it's used purely for its side effect (`println`) rather than to produce a new, useful `Future`.

**`Await.result(mappedFuture, 5.seconds)` - the one genuinely blocking line in this whole program:** everything above it (`Future { ... }`, `.map`, `.foreach`) is non-blocking - the whole point of `Future` is to avoid making any thread wait around. `Await.result` is the deliberate exception: it forces the *main* thread to pause and wait (up to a 5-second timeout) until `mappedFuture` actually completes. The comment in the code is explicit about why: without it, `main` would reach its end and the program could exit *before* the background thread ever finishes its 3-second sleep - `Await.result` exists here purely to keep this small demo program alive long enough to observe the async result. **Worth remembering for real code:** production async Scala code generally avoids `Await` entirely (since blocking defeats the purpose of using `Future` in the first place) and instead keeps chaining more callbacks (`map`/`flatMap`/`foreach`) - `Await` is mostly a testing/demo/small-program tool, not a production pattern.

| Call | Blocking? | Purpose |
|---|---|---|
| `Future { ... }` | No | Starts async work on a separate thread, returns immediately |
| `.map(...)` | No | Transforms the eventual result once available; returns a new `Future` (immutability - original untouched) |
| `.foreach(...)` | No | Runs a side-effecting callback once the result is available |
| `Await.result(...)` | **Yes** | Deliberately pauses the calling thread until the `Future` completes or times out - the one exception in this example |

**Handling a failed `Future`:** if the code inside `Future { ... }` throws, the `Future` completes as a `Failure` - `.map`/`.foreach` callbacks simply never run, so the error is silent unless you handle it:

```scala
import scala.util.{Success, Failure}

mappedFuture.onComplete {
  case Success(v)  => println(s"Got $v")
  case Failure(ex) => println(s"Failed: ${ex.getMessage}")
}

val safe = mappedFuture.recover { case _: Exception => -1 }   // fallback value instead of a failure
```

`Await.result` re-throws the failure on the calling thread, and also throws a `TimeoutException` if the timeout passes. Always give `Await` a finite timeout - `Duration.Inf` can hang the program forever if the `Future` never completes.

---

## Sealed Traits/Classes - Exhaustive Pattern Matching

```scala
sealed trait PaymentMethod

case class CreditCard(
  cardNumber: String
) extends PaymentMethod

case class PayPal(
  email: String
) extends PaymentMethod

case object Cash extends PaymentMethod

object SealedExample {

  def describePayment(payment: PaymentMethod): String = {

    payment match {

      case CreditCard(number) =>
        s"Paid with credit card ending in ${number.takeRight(4)}"

      case PayPal(email) =>
        s"Paid using PayPal account: $email"

      case Cash =>
        "Paid with cash"
    }
  }

  def main(args: Array[String]): Unit = {

    val payment1: PaymentMethod =
      CreditCard("1234567812345678")

    val payment2: PaymentMethod =
      PayPal("alice@example.com")

    val payment3: PaymentMethod =
      Cash

    println(describePayment(payment1))
    println(describePayment(payment2))
    println(describePayment(payment3))
  }
}
```

Expanded: this pattern - a `sealed trait` with a fixed set of `case class`/`case object` subtypes - is Scala's standard way of modeling "this value must be *one of exactly these alternatives, and nothing else*." It's the same underlying idea as an `enum` in other languages, but strictly more powerful: each variant (`CreditCard`, `PayPal`, `Cash`) can carry its *own* different data, not just a bare name.

**What `sealed` specifically changes:** an ordinary (non-sealed) `trait` can be extended by any class, in any file, at any time - there's no way to ever know the *complete* list of subtypes. `sealed` restricts every subtype of `PaymentMethod` to be declared in this **same file** - which means the compiler *can* know the full, closed set of possibilities (`CreditCard`, `PayPal`, `Cash`, and nothing else, ever). Trying to `extends PaymentMethod` from a different file would be a compile error.

**Why that restriction is the whole point - exhaustiveness checking:** because the compiler knows every possible subtype of a `sealed trait`, it can verify a `match` expression actually handles *all of them*. If `describePayment`'s `match` forgot a case (say, `case Cash => ...` were deleted), the compiler would flag a **non-exhaustive match** warning/error - catching a real bug (a payment type silently falling through unhandled) at compile time, before the program ever runs. This is the same "catch it before runtime" theme already seen today in the `TraitTest` example (`Buck.has_stripes` failing to compile) - `sealed` is what makes that same guarantee possible specifically for pattern matching over a fixed set of alternatives.

**`case class` vs. `case object` - which to use for each variant:** `CreditCard` and `PayPal` are `case class`es because each instance carries its own data (a card number, an email). `Cash` is a `case object` instead, because it carries no data at all - there's nothing to distinguish one "Cash" from another, so it only ever needs to exist as a single shared instance. This is the Singleton Object concept from `Training 9.md` again, just spelled `case object` here to *also* get the case-class-style benefits (works directly in pattern matching, e.g. `case Cash => ...` with no destructuring needed, since there's no data to extract).

| Concept | Role in this example |
|---|---|
| `sealed trait PaymentMethod` | Declares the closed set of alternatives - nothing outside this file can extend it |
| `case class CreditCard(...)` / `PayPal(...)` | Variants that carry their own data |
| `case object Cash` | A variant with no data - a singleton, matched directly with no destructuring |
| Exhaustive `match` | The compiler verifies every sealed subtype is handled - a missing case is caught at compile time, not discovered as a runtime bug |

---

## Implicits - Why `import spark.implicits._` and Similar Lines Actually Work

Q. What are implicits, in Scala?

A. (Teacher's definition) In Scala, implicits allow the compiler to automatically supply something that your code requires when you haven't supplied it explicitly. They are heavily used in Scala libraries, including Spark, because they let APIs add behavior or configuration without requiring you to repeatedly pass the same values.

Expanded: this is the direct explanation of something already used *without* explanation multiple times today - every `import spark.implicits._` line (in this morning's `CaseClassExample`/`OptionExample`) and `import scala.concurrent.ExecutionContext.Implicits.global` (in the `FutureExample`, above) are both implicits in action. Two mechanisms matter most:

- **Implicit parameters** - Scala automatically supplies an *argument* to a function you didn't explicitly pass.
- **Implicit conversions** - Scala automatically converts one type into another, or adds functionality to an existing type.

---

### 1. Implicit Parameters

Without implicits, a repeated argument has to be passed every time:
```scala
def greet(name: String, greeting: String): Unit = {
  println(s"$greeting, $name!")
}

greet("Alice", "Hello")
greet("Bob", "Hello")
greet("Charlie", "Hello")
```

Scala 2 lets you mark a separate parameter list `implicit`:
```scala
def greet(name: String)(implicit greeting: String): Unit = {
  println(s"$greeting, $name!")
}

implicit val defaultGreeting: String = "Hello"

greet("Alice")   // works - no second argument needed
```

**What's actually happening, traced step by step:** `greet("Alice")` is missing its second (implicit) parameter → Scala searches for an eligible `implicit String` currently in scope → finds `defaultGreeting` → the call effectively becomes `greet("Alice")("Hello")`. **The argument hasn't disappeared - it's still being passed, just found by the compiler instead of typed by you.** You can prove this by supplying one explicitly instead: `greet("Alice")("Good morning")` - once you do, Scala skips the implicit search entirely for that call.

---

### 2. What Is "Implicit Scope"?

The compiler doesn't search your *entire* application for anything marked `implicit` - that would be unpredictable and slow. Instead, Scala has specific rules for *where* it's allowed to look. At an introductory level: **implicit scope is the set of places Scala searches when it needs to find an implicit value or conversion of a particular type.**

```scala
object ImplicitScopeExample {

  def greet(name: String)(implicit greeting: String): Unit = {
    println(s"$greeting, $name!")
  }

  def main(args: Array[String]): Unit = {

    implicit val greeting: String = "Hello"

    greet("Alice")
  }
}
```

---

### 3. Imports Can Bring Implicits Into Scope

Implicits don't have to be defined right next to the call site - they can be **imported**:
```scala
object MyImplicits {
  implicit val greeting: String = "Hello"
}

object Main {
  import MyImplicits._

  def greet(name: String)(implicit greeting: String): Unit = {
    println(s"$greeting, $name!")
  }

  def main(args: Array[String]): Unit = {
    greet("Alice")
  }
}
```

**This is precisely the `import spark.implicits._` pattern** used in every Spark example so far this session - the import isn't grabbing "some random utilities," it's bringing a set of `implicit` definitions into scope, exactly like `import MyImplicits._` above.

---

### 4. Why Spark Uses `spark.implicits._`

```scala
import spark.implicits._

val ds = Seq(
  Person(1, "Alice"),
  Person(2, "Bob")
).toDS()
```

Reasonable question: *where did `.toDS()` come from? `Seq` doesn't normally have a `.toDS()` method.* That's exactly what `import spark.implicits._` enables - Spark provides implicit functionality that enriches ordinary Scala collections with Spark-specific operations. Without the import, `Seq(1, 2, 3).toDS()` typically won't even compile, since Scala has no way to supply the Spark-specific machinery `.toDS()` needs.

**Direct tie to this morning's `CaseClassExample`:** `people.toDS()` here and `spark.createDataset(people)` from this morning's worked example accomplish the *same* thing - `.toDS()` is the implicit-powered shorthand, `spark.createDataset(...)` is the explicit method call underneath. Both require `import spark.implicits._` to work at all.

---

### 5. Implicit Conversions

A different mechanism - converting between types automatically:
```scala
def double(number: Int): Int = number * 2

double(10)     // fine
double("10")   // normally a type error - String isn't Int
```

Historically, Scala lets you define a conversion:
```scala
implicit def stringToInt(value: String): Int = value.toInt
```
Now `double("10")` effectively becomes `double(stringToInt("10"))` → `double(10)` → `20`. The compiler sees a type mismatch and searches for an eligible conversion to resolve it.

---

### 6. Implicits Can Add Methods Entirely

One of the more surprising uses - "enriching" an existing type with a method it doesn't actually have:
```scala
implicit class BetterString(value: String) {
  def shout(): String = value.toUpperCase + "!"
}

val name = "Alice"
println(name.shout())   // "ALICE!"
```
`String` has no `.shout()` method - the compiler, seeing that method doesn't exist, looks for an applicable implicit enrichment, finds `BetterString`, and effectively rewrites the call as `BetterString("Alice").shout()`. **This is a major reason Scala APIs can seem to have methods "magically" available** that aren't on the base type at all.

---

### 7. Type Matters During Implicit Search - It's Not "Anything Marked Implicit"

```scala
def calculate(x: Int)(implicit multiplier: Int): Int = x * multiplier

implicit val multiplier: Int = 10
println(calculate(5))   // 50
```
If instead only `implicit val message: String = "Hello"` were in scope, that wouldn't help at all - Scala isn't searching for "anything marked implicit," it's searching for **an eligible implicit value whose type matches what's currently needed.**

---

### 8. Ambiguous Implicits

```scala
implicit val multiplier1: Int = 10
implicit val multiplier2: Int = 20

calculate(5)   // ambiguity error - NOT an arbitrary pick
```
When two eligible implicits of the same type both exist, Scala does **not** arbitrarily choose one - it raises an ambiguity error, since implicit resolution is required to produce one unambiguous best candidate. **This is exactly why using generic types like `String`/`Int` for real implicit configuration is poor design** - instead of `implicit val value: String = "production"`, wrap it in a purpose-built type:
```scala
case class Environment(name: String)
implicit val environment: Environment = Environment("production")
```
Now the compiler searches specifically for `Environment`, not some arbitrary, easily-collided-with `String`.

---

### 9. Companion Objects Matter to Implicit Scope

Directly building on this morning's Companion Objects section - a type's companion object is one of the specific places Scala's implicit resolution rules look:
```scala
case class DatabaseConfig(host: String, port: Int)

object DatabaseConfig {
  implicit val defaultConfig: DatabaseConfig =
    DatabaseConfig("localhost", 5432)
}

def connect()(implicit config: DatabaseConfig): Unit = {
  println(s"Connecting to ${config.host}:${config.port}")
}
```
When Scala needs a `DatabaseConfig`, `DatabaseConfig`'s own companion object is checked as part of the search - this lets library authors place sensible default implicits directly alongside the type itself, rather than requiring every caller to import them separately.

---

### 10. Why This Matters Beyond Saving Keystrokes

The real point isn't convenience - it's letting library designers express: *"perform operation X, using whatever appropriate configuration/type-class/execution context/encoder is currently available."* Async Scala code is the clearest example - **directly explaining today's `FutureExample`'s** `import scala.concurrent.ExecutionContext.Implicits.global` line:
```scala
implicit val ec: ExecutionContext = ...

doSomething(data)       // not doSomething(data, ec)
doSomethingElse(data)   // not doSomethingElse(data, ec)
```
Without implicits, every single async call in a program would need the same `ExecutionContext` threaded through by hand, every time. With it, that shared context is supplied automatically to every call that needs one.

---

### 11. Full Spark Picture

```scala
val spark = SparkSession.builder()
  .appName("Example")
  .master("local[*]")
  .getOrCreate()

import spark.implicits._

case class Person(id: Int, name: String, age: Int)

val people = Seq(Person(1, "Alice", 30), Person(2, "Bob", 25))
val ds = people.toDS()
```
`spark.implicits` belongs to *that specific* `SparkSession` instance (`spark`) - which is exactly why the import has to appear **after** `spark` is created, not before. `import spark.implicits._` is bringing Spark's implicit machinery (needed for `Dataset` encoders, among other things) into scope, not just "some Spark utilities."

---

### 12. Scala 3 Renamed This: `given`/`using`

Worth knowing since Spark/Scala code in the wild still overwhelmingly uses the older Scala 2 syntax covered above:

| Scala 2 | Scala 3 |
|---|---|
| `implicit val greeting: String = "Hello"` | `given greeting: String = "Hello"` |
| `def greet(name: String)(implicit greeting: String)` | `def greet(name: String)(using greeting: String)` |

Same underlying concept either way: a function requires a contextual value → the compiler searches the appropriate scope → finds a compatible value → supplies it automatically. Scala 3's terminology (**contextual abstractions**) arguably names the concept more clearly - but for this course specifically, the older `implicit` syntax is what you'll actually encounter in existing Spark/Scala code, so it's the one worth knowing cold.

---

### The Simplest Mental Model

```text
EXPLICIT
  def f(x: Int): ...
  f(10)
  "I need an Int, and you explicitly gave me one."

IMPLICIT
  def f()(implicit x: Config): ...
  implicit val config: Config = ...
  f()
  "I need a Config. You didn't explicitly give me one,
   so I'll search the appropriate implicit scope for a compatible Config."

IMPLICIT CONVERSION / ENRICHMENT
  someObject.someMethod()
  "This method/type doesn't directly work here. Is there an eligible
   implicit conversion or enrichment that makes it work?"
```

"Implicit scope" isn't just "variables available in this block" - it's the compiler's *structured* search for eligible contextual values/conversions, covering lexical context, imports, and (per section 9) companion/type scope. That structured search is what makes implicits powerful - and also exactly why poorly-designed implicits can make Scala code genuinely hard to read.

---

## Implicits Applied: Datasets, Encoders, and Spark Column Syntax

Q. Where do implicits show up most visibly in Spark data engineering specifically?

A. (Teacher's definition) In Spark data engineering, implicits show up most visibly around Datasets, Encoders, column syntax, typed transformations, and conversions between Scala collections/DataFrames/Datasets.

Expanded: this builds directly on the general Implicits section above - here's exactly what `import spark.implicits._` unlocks, piece by piece.

---

### 1. `Seq` → `Dataset` via `.toDS()`

```scala
import org.apache.spark.sql.SparkSession

object DatasetExample {

  case class Customer(id: Int, name: String, state: String)

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder()
      .appName("Implicit Example")
      .master("local[*]")
      .getOrCreate()

    import spark.implicits._

    val customers = Seq(
      Customer(1, "Alice", "TX"),
      Customer(2, "Bob", "CA"),
      Customer(3, "Charlie", "NY")
    )

    val customerDS = customers.toDS()
    customerDS.show()

    spark.stop()
  }
}
```
A plain Scala `Seq` doesn't inherently belong to Spark and has no built-in notion of becoming a `Dataset` - `import spark.implicits._` is what supplies the implicit machinery that makes `.toDS()` exist at all.

---

### 2. The Implicit `Encoder`

There's something more fundamental happening under `.toDS()`: `Dataset[Customer]` needs an **`Encoder[Customer]`** - the thing that tells Spark how to represent a JVM object like `Customer(1, "Alice", "TX")` in Spark SQL's internal (columnar) data representation. You can ask for it explicitly:

```scala
import org.apache.spark.sql.{Encoder, SparkSession}

val customerEncoder: Encoder[Customer] = implicitly[Encoder[Customer]]
println(customerEncoder)
```

`implicitly[Encoder[Customer]]` means: *"Compiler, search the implicit scope and give me the `Encoder[Customer]` you'd normally supply automatically."* Normally you never ask for it directly - `.toDS()` triggers the exact same search behind the scenes:

```text
Seq[Customer] → .toDS() → need Dataset[Customer]
  → Spark needs Encoder[Customer] → compiler searches implicit scope
  → Encoder found → Dataset[Customer]
```
**This is one of the clearest real demonstrations of why implicit scope matters at all** - without a resolvable `Encoder[Customer]`, `.toDS()` simply won't compile.

---

### 3. `$"column"` Syntax

```scala
import spark.implicits._
val result = df.select($"name", $"state")
```
The `$"name"` shorthand is also supplied by Spark's implicits - it doesn't exist without that import. The alternative, not requiring `spark.implicits._`:
```scala
import org.apache.spark.sql.functions.col
val result = df.select(col("name"), col("state"))
```
Both produce identical `Column` expressions. **Teacher's stated production preference: `col("name")` is generally clearer** - but `$"name"` shows up constantly in real Spark/Scala codebases, so it's worth recognizing even if you don't reach for it yourself.

---

### 4. Typed Dataset Column Syntax

```scala
val ages = employees.select($"age".as[Int])
```
`$"age".as[Int]` produces a **typed** result - `Dataset[Int]`, not an untyped `DataFrame` column. An `Encoder[Int]` is involved here too, resolved the same implicit way.

---

### 5. `.toDF()` From Plain Scala Collections

```scala
import spark.implicits._

val data = Seq((1, "Alice", "TX"), (2, "Bob", "CA"), (3, "Charlie", "NY"))
val df = data.toDF("customer_id", "customer_name", "state")
```
Very common for building small test DataFrames quickly. Same story as `.toDS()`: a plain `Seq[(Int, String, String)]` has no native `.toDF()` - `spark.implicits._` enriches it with one.

---

### 6. `DataFrame` → Typed `Dataset` via `.as[T]`

Directly relevant to this file's earlier DataFrame-vs-Dataset discussion:
```scala
val df = spark.read.option("header", "true").json("customers.json")
// df is effectively Dataset[Row] here - untyped

case class Customer(id: Long, name: String, state: String)

import spark.implicits._
val customers = df.as[Customer]   // now Dataset[Customer] - typed
```
```text
DataFrame → .as[Customer] → need Dataset[Customer]
  → need Encoder[Customer] → search implicit scope → found → Dataset[Customer]
```
This is the concrete mechanism behind converting the untyped `DataFrame`/`col()` style used in yesterday's `SalesAnalysis.scala` homework into the typed `Dataset[T]` style shown throughout today's examples - `.as[Customer]` is the bridge between the two.

---

### 7. Typed Transformations Need Encoders Too - Not Just the Input Type

```scala
val customers = Seq(Customer(1,"Alice","TX"), Customer(2,"Bob","CA"), Customer(3,"Charlie","TX")).toDS()
val names = customers.map(customer => customer.name)   // Dataset[Customer] -> Dataset[String]
```
`.map`'s real signature is conceptually `map[U](f)(implicit encoder: Encoder[U]): Dataset[U]` - so transforming `Dataset[Customer]` into `Dataset[String]` silently requires an `Encoder[String]` too, resolved implicitly, even though you never write `Encoder[String]` anywhere in the code.

---

### 8. Custom Output Case Classes Make This Especially Visible

```scala
case class CustomerSummary(name: String, state: String)

val summaries = customers.map { customer =>
  CustomerSummary(customer.name, customer.state)
}
```
Going from `Dataset[Customer]` to `Dataset[CustomerSummary]` requires Spark to resolve an `Encoder[CustomerSummary]` for this brand-new, arbitrary case class - a good demonstration that Spark genuinely has to figure out, generically, how to represent *any* case class you throw at it, not just a fixed built-in list of types.

---

### 9. Using the Same Pattern in Your Own Pipeline Code

Implicits aren't Spark-exclusive - the same mechanism works for your own pipeline configuration:
```scala
case class PipelineConfig(environment: String, database: String)

def processCustomers(df: DataFrame)(implicit config: PipelineConfig): DataFrame = {
  println(s"Running in ${config.environment}")
  df
}

implicit val config: PipelineConfig = PipelineConfig("production", "gold")
val result = processCustomers(df)   // config supplied automatically
```
Versus the alternative of threading `config` through every single function call by hand (`processCustomers(df1, config)`, `processOrders(df2, config)`, ...) - this isn't a Spark requirement, but shows the identical mechanism applied to a data-engineering library of your own design.

---

### 10. `ExecutionContext` for Async Pipeline Work (Not Spark's Own Parallelism)

```scala
import scala.concurrent.Future
import scala.concurrent.ExecutionContext

def loadMetadata()(implicit ec: ExecutionContext): Future[String] = {
  Future { "Metadata loaded" }
}

import scala.concurrent.ExecutionContext.Implicits.global
val result = loadMetadata()
```
Same pattern as today's earlier `FutureExample` - `loadMetadata()` needs an `ExecutionContext`, never explicitly passed, resolved implicitly to `global`. This kind of thing comes up in orchestration code, API calls, and metadata services around a Spark pipeline.

**Important distinction the teacher flagged explicitly:** using a Scala `Future` here is **not** how Spark parallelizes `DataFrame`/`Dataset` transformations across a cluster - Spark's own distributed execution model (Driver/Executors/Tasks, per `Training 7.md`) is a completely separate mechanism. `Future`/`ExecutionContext` is for ordinary async *application* code sitting around your Spark pipeline, not the pipeline's own internal parallelism.

---

### The Capstone Example - Case Class + Option + Dataset + Implicits, All Together

```scala
import org.apache.spark.sql.SparkSession

object SparkImplicitDemo {

  case class Customer(id: Int, name: String, email: Option[String])

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder()
      .appName("Spark Implicit Demo")
      .master("local[*]")
      .getOrCreate()

    import spark.implicits._

    val customers = Seq(
      Customer(1, "Alice", Some("alice@test.com")),
      Customer(2, "Bob", None),
      Customer(3, "Charlie", Some("charlie@test.com"))
    )

    // Implicit conversion + implicit Encoder
    val customerDS = customers.toDS()
    customerDS.show(false)

    // Spark column syntax supplied by implicits
    customerDS.filter($"email".isNotNull).show(false)

    // Typed transformation requiring an Encoder[String]
    val names = customerDS.map(customer => customer.name.toUpperCase)
    names.show()

    spark.stop()
  }
}
```

```text
case class Customer          (today's case class coverage)
Option[String] email         (today's Option coverage)
Seq[Customer].toDS()         → implicit conversion + Encoder[Customer]  → Dataset[Customer]
$"email".isNotNull           → Spark's implicit column syntax
Dataset.map(...)             → produces Dataset[String], requires Encoder[String], found implicitly
```

**The larger lesson:** Spark's Scala API leans on implicits specifically to hide infrastructure (encoders, type conversions) that would otherwise make every single `Dataset` operation verbose and repetitive. Instead of writing out encoders and conversions by hand constantly, Spark lets the compiler resolve that plumbing from implicit scope automatically - which is exactly why `import spark.implicits._` is such a ubiquitous line across Scala-based Spark code.

---

## Overloading vs. Overriding

Q. What's the difference between overloading and overriding in Scala?

A. (Teacher's definition) In Scala, overloading and overriding both involve methods with the same name, but they solve completely different problems.

---

### Overloading - Same Name, Different Parameters, Resolved at Compile Time

A. (Teacher's definition) Overloading means defining multiple methods with the same name but different parameter lists. The compiler determines which method to call based on the arguments you provide.

```scala
object OverloadingExample {

  def calculate(x: Int): Int = x * 2
  def calculate(x: Int, y: Int): Int = x + y
  def calculate(x: String): String = x.toUpperCase

  def main(args: Array[String]): Unit = {
    println(calculate(5))        // 10
    println(calculate(5, 10))    // 15
    println(calculate("hello"))  // HELLO
  }
}
```
Three distinct `calculate` methods coexist (`calculate(Int)`, `calculate(Int, Int)`, `calculate(String)`) - the compiler picks the right one purely from the arguments given at the call site. This is **compile-time polymorphism** - the decision is fully resolved before the program ever runs.

---

### Overriding - A Subclass Replaces an Inherited Method, Resolved at Runtime

A. (Teacher's definition) Overriding means a subclass provides a new implementation of a method it inherited from a parent class or trait.

```scala
class Employee {
  def work(): Unit = println("Employee is working")
}

class DataEngineer extends Employee {
  override def work(): Unit = println("Data Engineer is building pipelines")
}

object OverridingExample {
  def main(args: Array[String]): Unit = {
    val employee = new Employee()
    val engineer = new DataEngineer()

    employee.work()   // Employee is working
    engineer.work()   // Data Engineer is building pipelines
  }
}
```
`DataEngineer` inherits `work()` from `Employee` (per this file's earlier `TraitTest`/inheritance coverage) but **replaces** its implementation. Scala requires the `override` keyword explicitly - it tells the compiler *"I'm intentionally replacing a method inherited from a parent,"* rather than accidentally shadowing it.

---

### The Comparison

| | Overloading | Overriding |
|---|---|---|
| Same method name | Yes | Yes |
| Different parameters | Yes | Usually no |
| Requires inheritance | No | Yes |
| Different implementation | Yes | Yes |
| Decided | Compile time | Runtime |
| Purpose | Different ways to *call* something | *Change* inherited behavior |

**The easiest rule to remember:**
```text
OVERLOADING                          OVERRIDING
Same name, different parameters      Same method, Parent → Child
process(Int)                         Employee.work()
process(String)                            ↓
process(Int, Int)                    DataEngineer.work()
```

---

### An Example Showing Both at Once

```scala
class DataProcessor {

  // Original method
  def process(data: String): Unit = println(s"Processing string: $data")

  // OVERLOADED method
  def process(data: List[String]): Unit = println(s"Processing ${data.size} records")
}

class SparkDataProcessor extends DataProcessor {

  // OVERRIDDEN method
  override def process(data: String): Unit = println(s"Processing '$data' using Spark")
}

object Main {
  def main(args: Array[String]): Unit = {
    val processor = new SparkDataProcessor()
    processor.process("customers.csv")
    processor.process(List("Alice", "Bob", "Charlie"))
  }
}
```
`process(String)` and `process(List[String])` on `DataProcessor` are **overloaded** (same name, different parameter types, both defined on the same class). `SparkDataProcessor`'s `process(String)` is **overridden** (replacing `DataProcessor`'s own implementation of that exact same signature).

---

### Why Overriding Specifically Enables Runtime Polymorphism

```scala
val processor: DataProcessor = new SparkDataProcessor()
processor.process("customers.csv")
// -> "Processing 'customers.csv' using Spark"
```
The variable's **declared type** is `DataProcessor`, but the **actual object** is `SparkDataProcessor` - and the *overridden* version runs anyway. This is runtime polymorphism: the JVM picks which implementation to run based on the object's real type at runtime, not the variable's declared type at compile time - the exact opposite of overloading, which is fully settled at compile time.

**Concise interview/classroom summary:** overloading is the same method name with different parameter lists, resolved at compile time. Overriding is when a subclass replaces an inherited method implementation, enabling runtime polymorphism.

---

## Closures

Q. What is a closure?

A. (Teacher's definition) A closure is a function that uses a variable defined outside the function itself. The function "closes over" that external variable.

```scala
object ClosureExample {

  def main(args: Array[String]): Unit = {

    // Variable defined outside the function
    val multiplier = 10

    // This function uses multiplier from the surrounding scope
    val multiply = (number: Int) => {
      number * multiplier
    }

    println(multiply(2))   // 20
    println(multiply(5))   // 50
    println(multiply(10))  // 100
  }
}
```

Expanded: `number` is `multiply`'s actual parameter - but `multiplier` isn't. The function reaches *outside* itself and captures `multiplier` from the surrounding scope. That's what makes `multiply` a closure - it's "closed over" a variable it never received as an argument.

**A stronger demonstration - a function that returns another function:**
```scala
object ClosureExample {

  def createMultiplier(multiplier: Int): Int => Int = {
    val multiply = (number: Int) => {
      number * multiplier
    }
    multiply
  }

  def main(args: Array[String]): Unit = {

    val double = createMultiplier(2)
    val triple = createMultiplier(3)
    val timesTen = createMultiplier(10)

    println(double(5))    // 10
    println(triple(5))    // 15
    println(timesTen(5))  // 50
  }
}
```
This is the more convincing example, because something genuinely interesting happens: `createMultiplier(2)` **finishes executing and returns** - yet the function it returned (`double`) still remembers `multiplier = 2`, permanently. Likewise `triple` independently remembers `multiplier = 3`. **The closure retains access to the environment it needs, even after the function that created that environment has already returned.**

---

### Closures Are Everywhere in Spark Code

```scala
val minimumAge = 21

val adults = people.filter(
  person => person.age >= minimumAge
)
```
`person => person.age >= minimumAge` has one real parameter (`person`), but also references `minimumAge` from outside itself - so it's a closure, exactly like the examples above.

```scala
val taxRate = 0.08

val results = sales.map { sale =>
  val tax = sale.amount * taxRate
  (sale.id, sale.amount, tax)
}
```
`taxRate` is captured by this closure the same way.

**Important Spark-specific consequence - closure serialization:** Spark may need to send the function *and the values it captures* from the driver out to the executors (since the actual filtering/mapping runs distributed, per this file's own `Training 7.md` Driver/Executor coverage). This is exactly why capturing large objects, database connections, a `SparkSession`, or other non-serializable objects inside a Spark transformation can cause performance problems or outright serialization errors - the closure has to travel over the network to every executor, and everything it captures has to travel with it. The error you see when something captured can't be serialized is **`org.apache.spark.SparkException: Task not serializable`** (caused by `java.io.NotSerializableException: <class>`). Common fixes: copy the needed field into a local `val` before the lambda, make the class `Serializable`, create connections inside `foreachPartition`/`mapPartitions` (on the executor), or use a broadcast variable for large lookup data. See Training 7 for the driver/executor split.

**Concise definition:** a closure is a function that captures and retains access to variables from its surrounding lexical scope, even though those variables were never passed to the function as parameters.

---

## Currying

Q. What is currying?

A. (Teacher's correction/refinement) Currying transforms a function like `f(a, b, c)` into the conceptual equivalent of `f(a)(b)(c)` - where each stage takes one argument and returns another function, until the final function produces the result.

*(This corrects an earlier, blurrier explanation that conflated three closely-related-but-distinct ideas: currying, partial application, and Scala's multiple-parameter-list syntax - worth keeping the three separate, per the table below.)*

**The explicit, function-returning-function form** - what currying literally *is*:
```scala
def add(a: Int, b: Int, c: Int): Int = a + b + c   // normal, uncurried

def curriedAdd(a: Int): Int => Int => Int = {
  (b: Int) => {
    (c: Int) => {
      a + b + c
    }
  }
}
```
```scala
object CurryingExample {

  def curriedAdd(a: Int): Int => Int => Int = {
    (b: Int) => {
      (c: Int) => {
        a + b + c
      }
    }
  }

  def main(args: Array[String]): Unit = {

    val result = curriedAdd(10)(20)(30)
    println(result)   // 60

    // Get the first returned function
    val add10: Int => Int => Int = curriedAdd(10)

    // Get the second returned function
    val add10And20: Int => Int = add10(20)

    // Finally produce the result
    val finalResult: Int = add10And20(30)
    println(finalResult)   // 60
  }
}
```
**Why this is the best teaching example:** you can literally see each intermediate function get returned and stored - `add10` is a real, holdable value of type `Int => Int => Int`, `add10And20` is a real value of type `Int => Int`, and only the final call produces an actual `Int`.

**Scala's shorthand for the same thing** - multiple parameter lists:
```scala
def curriedAdd(a: Int)(b: Int)(c: Int): Int = a + b + c
```
This expresses the *identical* curried calling structure (`curriedAdd(10)(20)(30)`) without manually nesting `=>` functions - it's syntax sugar over the explicit form above.

---

### Currying vs. Partial Application vs. Multiple Parameter Lists - Keeping the Terms Separate

Using the full call `add(10)(20)(30)` is using a curried function *completely*. Stopping early:
```scala
val add10: Int => Int => Int = add(10)          // partial application
val add10And20: Int => Int = add10(20)          // partially applying again
val result = add10And20(30)                      // finally, the result
```
is **partial application** - supplying *some* arguments now and getting back a function still waiting for the rest.

| Concept | Meaning |
|---|---|
| Currying | Transforming `f(a, b, c)` into `f(a)(b)(c)` - each stage takes one argument, returns another function |
| Partial application | Supplying some arguments now, getting back a function waiting for the remaining ones |
| Multiple parameter lists | Scala's own syntax (`def f(a)(b)(c)`) that naturally supports curried-style calling |

**Scala's built-in `.curried` method** makes the concept unmistakable:
```scala
val add = (a: Int, b: Int, c: Int) => a + b + c
val curriedAdd = add.curried

println(add(10, 20, 30))          // 60
println(curriedAdd(10)(20)(30))   // 60
```
This takes an ordinary three-argument function and mechanically curries it into a chain of one-argument functions - probably the clearest single example of what currying *is*, independent of any hand-written boilerplate.

---

### Why Currying Actually Matters for Data Engineering

Not a Spark performance tool - **its value is software design**: separating configuration from the data being processed, to build reusable, composable transformation functions. It "fits naturally into functional ETL design" without being required for every job.

**1. Configure once, apply to many records:**
```scala
def convertCurrency(rate: Double)(amount: Double): Double = amount * rate

val usdToEuro: Double => Double = convertCurrency(0.92)

val amounts = List(100.0, 500.0, 1000.0)
val euros = amounts.map(usdToEuro)
```
Instead of repeating `convertCurrency(0.92, 100)`, `convertCurrency(0.92, 500)`, ... every time, `usdToEuro` is a reusable, pre-configured function you can hand directly to `.map(...)`.

**2. Configuring Spark transformations the same way:**
```scala
case class Transaction(id: Int, amount: Double)

def aboveAmount(minimum: Double)(transaction: Transaction): Boolean =
  transaction.amount >= minimum

val above1000 = aboveAmount(1000)

val largeTransactions = transactions.filter(above1000)
// Works identically against a typed Dataset:
val largeTransactionsDS = transactionDS.filter(above1000)
```
You're building **parameterized transformation factories** - `above1000` is a fully reusable predicate, not a one-off inline lambda.

**3. `DataFrame => DataFrame` as a common shape:**
```scala
// Without currying - config and data mixed together:
def filterCountry(df: DataFrame, country: String): DataFrame =
  df.filter(col("country") === country)

// With currying - config separated from data:
def filterCountry(country: String)(df: DataFrame): DataFrame =
  df.filter(col("country") === country)

val filterUSA = filterCountry("USA")
val filterBrazil = filterCountry("Brazil")
```
Both `filterUSA` and `filterBrazil` now have the exact same shape: `DataFrame => DataFrame`.

**4. That common shape makes pipelines composable via `.transform`:**
```scala
def filterCountry(country: String)(df: DataFrame): DataFrame =
  df.filter(col("country") === country)

def minimumAmount(amount: Double)(df: DataFrame): DataFrame =
  df.filter(col("amount") >= amount)

def selectColumns(columns: String*)(df: DataFrame): DataFrame =
  df.select(columns.map(col): _*)

val result = rawDF
  .transform(filterCountry("USA"))
  .transform(minimumAmount(1000))
  .transform(selectColumns("order_id", "customer_id", "amount"))
```
Each curried function slots directly into Spark's own `.transform(...)` pipeline style, since they're all `DataFrame => DataFrame` - this is a genuinely practical, idiomatic Spark pattern, not just a theoretical exercise.

**5. Configuration and processing become separate concerns:**
```scala
// Without currying: config repeated at every call site
val result1 = filterCountry(df1, "USA")
val result2 = filterCountry(df2, "USA")

// With currying: decide "what transformation" once, apply "to what data" later
val usaOnly = filterCountry("USA")
val result1 = usaOnly(df1)
val result2 = usaOnly(df2)
```

**6. Multi-stage configuration (e.g. environment-specific writes):**
```scala
def writeTable(database: String)(table: String)(df: DataFrame): Unit = {
  df.write.mode("overwrite").saveAsTable(s"$database.$table")
}

val writeToGold = writeTable("gold")            // stage 1: database configured
val writeCustomers = writeToGold("customers")   // stage 2: table configured
writeCustomers(customerDF)                       // stage 3: data provided, write occurs
```
This is currying's definition made fully concrete: each stage accepts one piece of information and produces a function waiting for the next piece - database, then table, then data.

---

### Where This Ranks in Priority (Teacher's Guidance)

| Tier | Concepts |
|---|---|
| **Essential** | `map`, `flatMap`, `filter`, `Option`, collections, case classes, pattern matching, higher-order functions, closures |
| **Important for reading Scala/Spark code** | implicits/contextual parameters, traits, companion objects, inheritance, overriding |
| **Useful functional design technique** | currying and partial application |

You're very unlikely to hit a Spark *performance* problem whose solution is "use currying." Its real value is design-level: building configurable, reusable, composable ETL transformations - and the pattern that makes this concrete is exactly `def transformation(config)(df: DataFrame): DataFrame`, which turns configuration into a reusable `DataFrame => DataFrame` function that plugs directly into `df.transform(...)`.
