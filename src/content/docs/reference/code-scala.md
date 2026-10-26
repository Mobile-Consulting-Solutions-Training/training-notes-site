---
title: "Code: Scala"
description: "Every Scala and Spark-in-Scala example from the notes, grouped by training day."
sidebar:
  order: 9
---

Every Scala and Spark-in-Scala example from the notes, grouped by training day. Each example is titled with the question it answers in the notes; the day heading links to the full notes for context. Use the copy button on any block.
**56 examples.**


Code marked "from the class demo (not exact)" in the notes was rewritten from the demo, so check names and paths before running it.

## Training 9: IntelliJ/Scala Setup & Scala Fundamentals

[Open the Training 9 notes](/training-notes-site/notes/training-9/)

### If It Still Fails After All Four Steps

```scala
scalaVersion := "2.13.18"

lazy val root = (project in file("."))
  .settings(
    name := "HelloWorld"
  )
```

### What is a Singleton Object, in Scala?

```scala
class Account(val owner: String, val balance: Double)

object Account {                       // companion object
  def apply(owner: String): Account = new Account(owner, 0.0)
}

object Main {                          // singleton entry point
  def main(args: Array[String]): Unit = {
    val a = Account("alex")            // calls Account.apply, no `new`
    println(a.balance)
  }
}
```

### What is immutability?

```scala
val xs = List(1, 2)
val ys = xs :+ 3      // new list List(1, 2, 3); xs is still List(1, 2)
var n = 1
n = 2                 // allowed for var; `xs = ys` would not compile
```

### What goes in build.sbt for a Spark job, and what do %% and provided mean?

```scala
scalaVersion := "2.13.16"

lazy val root = rootProject
  .settings(
    name := "SalesAnalysis",
    libraryDependencies ++= Seq(
      "org.apache.spark" %% "spark-sql" % "3.5.9",
      "org.postgresql" % "postgresql" % "42.7.4"
    )
  )
```

## Training 10: Scala Fundamentals (Continued)

[Open the Training 10 notes](/training-notes-site/notes/training-10/)

### What is a case class?

```scala
val alice = Person("Alice", 30)
val olderAlice = alice.copy(age = 31)

println(alice)       // Person(Alice,30)  - unchanged
println(olderAlice)  // Person(Alice,31)  - a separate, new object
```

```scala
alice match {
  case Person(n, a) if a >= 18 => s"$n is an adult"
  case Person(n, _) => s"$n is a minor"
}
```

```scala
case class Sale(orderNumber: Int, productNumber: String, quantity: Int, price: Double)

val sales = spark.read.jdbc(JDBC_URL, "gold.fact_sales", jdbcProperties).as[Sale]
sales.filter(_.price > 1000)   // compiler checks .price actually exists on Sale
```

```scala
import spark.implicits._

val sales = spark.read.jdbc(JDBC_URL, "gold.fact_sales", jdbcProperties)
  .withColumnRenamed("order_number", "orderNumber")
  .withColumnRenamed("product_number", "productNumber")
  .as[Sale]
```

### Worked Example (Teacher's Code): case class + Dataset[Person]

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

### Worked Example: Traits, Inheritance, and Mixins (TraitTest)

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

### How do you handle errors the Scala way (Try and Either)?

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

### What is a for-comprehension?

```scala
val result = for {
  e <- email   // Option[String]
  a <- age     // Option[Int]
} yield s"$e is $a"
// same as: email.flatMap(e => age.map(a => s"$e is $a"))
```

### Worked Example: flatMap on Nested Lists

```scala
val myList = List(
  List(1, 2),
  List(8, 9),
  List(3, 4, 5)
)

val flatMappedList = myList.flatMap(x => x.map(_ * 2))

println(flatMappedList)
```

### Worked Example: Option in Practice (OptionExample)

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

### What is a companion object?

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

### What are Future classes, and what are they for?

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

```scala
import scala.util.{Success, Failure}

mappedFuture.onComplete {
  case Success(v)  => println(s"Got $v")
  case Failure(ex) => println(s"Failed: ${ex.getMessage}")
}

val safe = mappedFuture.recover { case _: Exception => -1 }   // fallback value instead of a failure
```

### Sealed Traits/Classes - Exhaustive Pattern Matching

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

### 1. Implicit Parameters

```scala
def greet(name: String, greeting: String): Unit = {
  println(s"$greeting, $name!")
}

greet("Alice", "Hello")
greet("Bob", "Hello")
greet("Charlie", "Hello")
```

```scala
def greet(name: String)(implicit greeting: String): Unit = {
  println(s"$greeting, $name!")
}

implicit val defaultGreeting: String = "Hello"

greet("Alice")   // works - no second argument needed
```

### 2. What Is "Implicit Scope"?

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

### 3. Imports Can Bring Implicits Into Scope

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

### 4. Why Spark Uses spark.implicits._

```scala
import spark.implicits._

val ds = Seq(
  Person(1, "Alice"),
  Person(2, "Bob")
).toDS()
```

### 5. Implicit Conversions

```scala
def double(number: Int): Int = number * 2

double(10)     // fine
double("10")   // normally a type error - String isn't Int
```

### 6. Implicits Can Add Methods Entirely

```scala
implicit class BetterString(value: String) {
  def shout(): String = value.toUpperCase + "!"
}

val name = "Alice"
println(name.shout())   // "ALICE!"
```

### 7. Type Matters During Implicit Search - It's Not "Anything Marked Implicit"

```scala
def calculate(x: Int)(implicit multiplier: Int): Int = x * multiplier

implicit val multiplier: Int = 10
println(calculate(5))   // 50
```

### 8. Ambiguous Implicits

```scala
implicit val multiplier1: Int = 10
implicit val multiplier2: Int = 20

calculate(5)   // ambiguity error - NOT an arbitrary pick
```

### 9. Companion Objects Matter to Implicit Scope

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

### 10. Why This Matters Beyond Saving Keystrokes

```scala
implicit val ec: ExecutionContext = ...

doSomething(data)       // not doSomething(data, ec)
doSomethingElse(data)   // not doSomethingElse(data, ec)
```

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

### 1. Seq → Dataset via .toDS()

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

### 2. The Implicit Encoder

```scala
import org.apache.spark.sql.{Encoder, SparkSession}

val customerEncoder: Encoder[Customer] = implicitly[Encoder[Customer]]
println(customerEncoder)
```

### 5. .toDF() From Plain Scala Collections

```scala
import spark.implicits._

val data = Seq((1, "Alice", "TX"), (2, "Bob", "CA"), (3, "Charlie", "NY"))
val df = data.toDF("customer_id", "customer_name", "state")
```

### 6. DataFrame → Typed Dataset via .as[T]

```scala
val df = spark.read.option("header", "true").json("customers.json")
// df is effectively Dataset[Row] here - untyped

case class Customer(id: Long, name: String, state: String)

import spark.implicits._
val customers = df.as[Customer]   // now Dataset[Customer] - typed
```

### 8. Custom Output Case Classes Make This Especially Visible

```scala
case class CustomerSummary(name: String, state: String)

val summaries = customers.map { customer =>
  CustomerSummary(customer.name, customer.state)
}
```

### 9. Using the Same Pattern in Your Own Pipeline Code

```scala
case class PipelineConfig(environment: String, database: String)

def processCustomers(df: DataFrame)(implicit config: PipelineConfig): DataFrame = {
  println(s"Running in ${config.environment}")
  df
}

implicit val config: PipelineConfig = PipelineConfig("production", "gold")
val result = processCustomers(df)   // config supplied automatically
```

### 10. ExecutionContext for Async Pipeline Work (Not Spark's Own Parallelism)

```scala
import scala.concurrent.Future
import scala.concurrent.ExecutionContext

def loadMetadata()(implicit ec: ExecutionContext): Future[String] = {
  Future { "Metadata loaded" }
}

import scala.concurrent.ExecutionContext.Implicits.global
val result = loadMetadata()
```

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

### Overloading - Same Name, Different Parameters, Resolved at Compile Time

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

### Overriding - A Subclass Replaces an Inherited Method, Resolved at Runtime

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

### What is a closure?

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

### Closures Are Everywhere in Spark Code

```scala
val minimumAge = 21

val adults = people.filter(
  person => person.age >= minimumAge
)
```

```scala
val taxRate = 0.08

val results = sales.map { sale =>
  val tax = sale.amount * taxRate
  (sale.id, sale.amount, tax)
}
```

### What is currying?

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

### Currying vs. Partial Application vs. Multiple Parameter Lists - Keeping the Terms Separate

```scala
val add = (a: Int, b: Int, c: Int) => a + b + c
val curriedAdd = add.curried

println(add(10, 20, 30))          // 60
println(curriedAdd(10)(20)(30))   // 60
```

### Why Currying Actually Matters for Data Engineering

```scala
def convertCurrency(rate: Double)(amount: Double): Double = amount * rate

val usdToEuro: Double => Double = convertCurrency(0.92)

val amounts = List(100.0, 500.0, 1000.0)
val euros = amounts.map(usdToEuro)
```

```scala
case class Transaction(id: Int, amount: Double)

def aboveAmount(minimum: Double)(transaction: Transaction): Boolean =
  transaction.amount >= minimum

val above1000 = aboveAmount(1000)

val largeTransactions = transactions.filter(above1000)
// Works identically against a typed Dataset:
val largeTransactionsDS = transactionDS.filter(above1000)
```

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

```scala
// Without currying: config repeated at every call site
val result1 = filterCountry(df1, "USA")
val result2 = filterCountry(df2, "USA")

// With currying: decide "what transformation" once, apply "to what data" later
val usaOnly = filterCountry("USA")
val result1 = usaOnly(df1)
val result2 = usaOnly(df2)
```

```scala
def writeTable(database: String)(table: String)(df: DataFrame): Unit = {
  df.write.mode("overwrite").saveAsTable(s"$database.$table")
}

val writeToGold = writeTable("gold")            // stage 1: database configured
val writeCustomers = writeToGold("customers")   // stage 2: table configured
writeCustomers(customerDF)                       // stage 3: data provided, write occurs
```

## Training 11: Postgres to Hive with Scala Spark

[Open the Training 11 notes](/training-notes-site/notes/training-11/)

### How does a Spark job write Postgres tables straight into Hive, without a CSV bridge?

```scala
import org.apache.spark.sql.{SparkSession, DataFrame}
import java.util.Properties

object HelloWorld {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession
      .builder
      .master("local[*]")
      .appName("Test Scala App")
      .config("hive.metastore.uris", "thrift://localhost:9083")
      .config("spark.sql.hive.metastore.version", "3.1.3")
      .config("spark.sql.hive.metastore.jars", "maven")
      .enableHiveSupport()
      .getOrCreate()

    val JDBC_URL = "jdbc:postgresql://localhost:5432/sample_database"

    val jdbcProperties = new Properties()
    jdbcProperties.setProperty("user", "evan")
    jdbcProperties.setProperty("password", sys.env("PG_PASSWORD"))
    jdbcProperties.setProperty("driver", "org.postgresql.Driver")

    def readPostgres(table: String): DataFrame = {
      spark.read.jdbc(JDBC_URL, table, jdbcProperties)
    }

    val bronze = readPostgres("bronze.sales")
    val silver = readPostgres("silver.sales")
    val customerTable = readPostgres("gold.dim_customer")
    val dateTable = readPostgres("gold.dim_date")
    val departmentTable = readPostgres("gold.dim_department")
    val employeeTable = readPostgres("gold.dim_employee")
    val officeTable = readPostgres("gold.dim_office")
    val productTable = readPostgres("gold.dim_product")
    val factPaymentTable = readPostgres("gold.fact_payment")
    val factSalesTable = readPostgres("gold.fact_sales")

    bronze.show()
    silver.show()
    customerTable.show()
    dateTable.show()
    departmentTable.show()
    employeeTable.show()
    officeTable.show()
    productTable.show()
    factPaymentTable.show()
    factSalesTable.show()

    // Native Spark-Hive write - no CSV bridge, no LOAD DATA
    bronze.write.mode("overwrite").saveAsTable("bronze.sales")
    silver.write.mode("overwrite").saveAsTable("silver.sales")
    customerTable.write.mode("overwrite").saveAsTable("gold.dim_customer")
    dateTable.write.mode("overwrite").saveAsTable("gold.dim_date")
    departmentTable.write.mode("overwrite").saveAsTable("gold.dim_department")
    employeeTable.write.mode("overwrite").saveAsTable("gold.dim_employee")
    officeTable.write.mode("overwrite").saveAsTable("gold.dim_office")
    productTable.write.mode("overwrite").saveAsTable("gold.dim_product")
    factPaymentTable.write.mode("overwrite").saveAsTable("gold.fact_payment")
    factSalesTable.write.mode("overwrite").saveAsTable("gold.fact_sales")

    spark.stop()
  }
}
```

### How do you make a Bronze -> Silver load incremental and idempotent?

```scala
val bronze   = spark.read.jdbc(JDBC_URL, "bronze.sales", jdbcProperties)
val existing = spark.table("silver.sales").select("sale_id")

val newRows = bronze
  .dropDuplicates("sale_id")                  // no duplicates inside this batch
  .join(existing, Seq("sale_id"), "left_anti") // keep only keys Silver doesn't have yet

newRows.write.mode("append").saveAsTable("silver.sales")
```
