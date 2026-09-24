---
title: Training 10 - Scala Fundamentals (Continued)
description: Case classes, traits/inheritance/mixins, the Nil/Null/null/Nothing/None/Unit distinctions, the Option type, flatMap, and companion objects.
---

Teacher: Evan Flint

Syllabus Day 11 (per file numbering) - actual coverage: continuing Scala Fundamentals from `Training 9.md` (Singleton Object, Immutability, IntelliJ/sbt setup) into more Scala language features, following directly from yesterday's Scala Spark homework (`homework/submission/alex_jackson_scala_spark_homework/`). Note: this continues the pacing drift already visible in `Training 6.md`-`Training 9.md` - this session's content lines up with the roadmap's Day 12 topic ("Scala Advanced") rather than its own nominal Day 11 slot.

# Scala Fundamentals (continued)

Q. What is a case class?

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

*(Shared by a fellow student, Alex, in the class chat - not the teacher directly, but confirmed/accepted as correct in context. Captured here since they're genuine definitions from today's session.)*

Q. What is inheritance?

A. (Shared in class chat by a student) Inheritance is when you consume the properties/functions of a parent class/object.

Expanded: inheritance lets one class (a "child"/"subclass") automatically gain all the fields and methods already defined on another class (the "parent"/"superclass"), without having to redeclare them. This is a standard OOP concept, not Scala-specific, but Scala supports it the same way Java does (`class Child extends Parent`). Worth flagging as a placeholder here - no code example given yet in this session, expand further once the teacher covers it directly with Scala syntax.

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
| `Null` | A *trait/type* - the type of the `null` literal itself; only reference types can hold it | Rarely written directly - it's the inferred type of `null` |
| `null` | The actual *value* (lowercase) - Scala's inherited-from-Java "no object" reference | `var x: String = null` |
| `Nothing` | The *bottom type* - a subtype of every other type in Scala; no real value of type `Nothing` ever exists at runtime, used for computations that never return normally (e.g. always throwing) | `def fail(): Nothing = throw new Exception("boom")` |
| `None` | A concrete singleton object - one of `Option[T]`'s two cases (the other being `Some(value)`), representing "no value," the type-safe alternative to `null` | `val missing: Option[String] = None` |
| `Unit` | A *type* - the return type for expressions/methods that don't produce a meaningful value, Scala's equivalent of Java's `void`. Has exactly one possible value, written `()` | `def printIt(): Unit = println("hi")` |

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

Q. What does `flatMap` actually do differently from `map`?

A. (Teacher's definition) [flatMap] flattens the list, or brings all the sub-elements to the top level. It removes internal groupings.

Expanded, tracing through the example step by step:
1. `myList` is a list of lists: `List(List(1, 2), List(8, 9), List(3, 4, 5))`.
2. For each inner list `x`, `x.map(_ * 2)` doubles every element: `List(1,2)` → `List(2,4)`, `List(8,9)` → `List(16,18)`, `List(3,4,5)` → `List(6,8,10)`.
3. If this were plain `.map(x => x.map(_ * 2))` (no `flatMap`), the result would *still be nested*: `List(List(2,4), List(16,18), List(6,8,10))`.
4. `flatMap` additionally **flattens** that nested result by one level, merging all the inner lists' elements into a single top-level list: `List(2, 4, 16, 18, 6, 8, 10)`.

So `flatMap` = `map` + flatten, always in that order - it's literally a contraction of the two operations, which is exactly why it's named that. This same "map + flatten" idea reappears below applied to `Option` instead of `List` - `flatMap` isn't List-specific, it works on any container type that supports it (`List`, `Option`, `Seq`, etc.), same as `Training 7.md`'s point about `Seq` being a general trait with many implementations.

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
