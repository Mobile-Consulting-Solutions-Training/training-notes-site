---
title: Training 2 Homework
description: Pandas - 10 exercises using the class employee dataset, with worked solutions and output
---

## Assignment

## Objective

Use the `data.csv` employee dataset from class. Unless specifically instructed otherwise, solve each problem using Pandas rather than loops over individual rows.

## Exercises

1. **Department statistics**
   Produce a DataFrame containing one row per department with:
   - Number of employees
   - Average salary
   - Minimum salary
   - Maximum salary
   - Average years of experience

   Sort the result from highest to lowest average salary.

2. **Above-department-average employees**
   Find every employee whose salary is **greater than the average salary of their own department**. Display:

   ```text
   name | department | salary | department_average
   ```

   Sort by department and then salary descending.

3. **Salary bands**
   Add a new column called `salary_band` according to these rules:

   ```text
   Under 70,000        -> "Low"
   70,000-89,999       -> "Medium"
   90,000-109,999      -> "High"
   110,000 and above   -> "Very High"
   ```

   Then determine how many employees from each department fall into each salary band.

4. **Experienced but underpaid**
   Find employees who have **at least 7 years of experience** but earn **less than $90,000**. Determine which department has the largest number of these employees.

5. **Department ranking**
   Add a column called `salary_rank` that ranks employees by salary **within their own department**, where the highest-paid employee in each department receives rank 1. Display the three highest-paid employees from each department.

6. **Create and perform a join**
   Create a second DataFrame in your Python program:

   ```python
   department_info = pd.DataFrame({
       "department": [
           "Engineering",
           "Sales",
           "Marketing",
           "Finance",
           "HR"
       ],
       "manager": [
           "Sarah Connor",
           "Michael Scott",
           "Don Draper",
           "Bruce Wayne",
           "Leslie Knope"
       ],
       "location": [
           "New York",
           "Chicago",
           "Los Angeles",
           "New York",
           "Chicago"
       ]
   })
   ```

   Join this DataFrame with the employee data so that every employee record also contains their manager and office location. Then calculate the average salary for each office location.

7. **Detect salary outliers**
   For each department, calculate its mean salary and standard deviation. Find employees whose salary is **more than one standard deviation above their department's mean**. Do not hard-code the department averages or standard deviations.

8. **Simulate a compensation adjustment**
   The company decides to implement the following raises:

   ```text
   Salary < $70,000             -> 8% raise
   Salary $70,000-$89,999       -> 5% raise
   Salary $90,000 or greater    -> 3% raise
   ```

   Add a `new_salary` column without changing the original `salary` column. Then calculate:
   - Original total payroll
   - New total payroll
   - Total cost of the raises
   - Percentage increase in payroll

9. **Experience vs. compensation**
   Create experience groups:

   ```text
   0-4 years    -> Junior
   5-7 years    -> Mid
   8+ years     -> Senior
   ```

   Calculate the average salary for each experience group **within each department**. Determine which department has the largest salary difference between its Junior and Senior employees. Handle departments that don't have employees in both groups appropriately.

10. **Mini ETL challenge**
    Write a Pandas program that reads `data.csv` and produces a new file called:

    ```text
    department_report.csv
    ```

    The output must contain exactly one row per department and these columns:

    ```text
    department
    employee_count
    active_employee_count
    average_salary
    median_salary
    average_experience
    highest_salary
    highest_paid_employee
    ```

    Round monetary averages to two decimal places and sort the final file by `average_salary` descending.

## Challenge Constraint

For **questions 2, 5, 7, 9, and 10**, do not use a Python `for` loop to process employees individually. The objective is to solve the problem using DataFrame operations such as `groupby()`, `transform()`, `rank()`, `agg()`, `merge()`, boolean indexing, and related Pandas functionality.

These should push beyond the basic `read_csv()` -> filter -> `.sum()` examples from class and require discovering several important Pandas operations independently.

---

## Submission

A few of the tools used below (`pd.cut()`, `.unstack()`, `observed=True`, multi-column `sort_values`) weren't covered live in class - they're documented with explanations and doc links in [Training 2 notes](/training-notes-site/notes/training-2/#agent-generated-notes), under "Agent Generated Notes."

```python
import pandas as pd

# Show full tables when printing, instead of truncating wide/long output
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

data_frame = pd.read_csv("data.csv")

# ============================================================
# EXERCISE 1: Department statistics
# ============================================================
# Built column-by-column: groupby()+one-agg-function-at-a-time,
# then attach each Series onto a single DataFrame as a new column
# (this is the pattern from the class assignment, no .agg() dict
# since that wasn't covered yet).

number_of_employees = (
    data_frame
    .groupby("department")["name"]
    .count()
)

average_salary = (
    data_frame
    .groupby("department")["salary"]
    .mean()
).round(2)

minimum_salary = (
    data_frame
    .groupby("department")["salary"]
    .min()
)

maximum_salary = (
    data_frame
    .groupby("department")["salary"]
    .max()
)

year_of_experience = (
    data_frame
    .groupby("department")["years_experience"]
    .mean()
).round(2)

new_data_frame = number_of_employees.to_frame(name="number_of_employees")
new_data_frame["average_salary"] = average_salary
new_data_frame["minimum_salary"] = minimum_salary
new_data_frame["maximum_salary"] = maximum_salary
new_data_frame["years_of_experience"] = year_of_experience

# Requirement: sort highest -> lowest average salary
new_data_frame = new_data_frame.sort_values("average_salary", ascending=False)

print("\n=== Exercise 1: Department statistics ===")
print(new_data_frame)


# ============================================================
# EXERCISE 2: Above-department-average employees
# ============================================================
# Work on a COPY of data_frame (like the class .copy() example) so
# this exercise's extra column doesn't leak into later exercises.
# transform("mean") broadcasts the group average back to every row
# (100 values, not collapsed to 5), so it can be compared row-by-row
# against that same row's own salary - no for loop needed.

exercise2_df = data_frame.copy()
exercise2_df["department_average"] = (
    exercise2_df.groupby("department")["salary"].transform("mean")
)

above_average = exercise2_df[
    exercise2_df["salary"] > exercise2_df["department_average"]
]

exercise2_result = above_average[
    ["name", "department", "salary", "department_average"]
].sort_values(["department", "salary"], ascending=[True, False])

print("\n=== Exercise 2: Above-department-average employees ===")
print(exercise2_result)


# ============================================================
# EXERCISE 3: Salary bands
# ============================================================
# pd.cut() slices a numeric column into labeled buckets in one call -
# no manual if/elif chain needed. Bin edges are set just below/above
# the stated boundaries so each edge value lands in the right band
# (e.g. 69999 is the top of "Low", so 70000 falls in "Medium").

exercise3_df = data_frame.copy()
exercise3_df["salary_band"] = pd.cut(
    exercise3_df["salary"],
    bins=[0, 69_999, 89_999, 109_999, float("inf")],
    labels=["Low", "Medium", "High", "Very High"],
)

band_counts = (
    exercise3_df
    .groupby(["department", "salary_band"], observed=True)
    .size()
    .unstack(fill_value=0)
)

print("\n=== Exercise 3: Salary bands ===")
print(exercise3_df[["name", "department", "salary", "salary_band"]].head(10))
print("\nCounts by department and band:")
print(band_counts)


# ============================================================
# EXERCISE 4: Experienced but underpaid
# ============================================================

exercise4_df = data_frame[
    (data_frame["years_experience"] >= 7) & (data_frame["salary"] < 90_000)
]

department_with_most = exercise4_df["department"].value_counts()

print("\n=== Exercise 4: Experienced but underpaid ===")
print(exercise4_df[["name", "department", "salary", "years_experience"]])
print("\nCount by department:")
print(department_with_most)
print(
    f"\nDepartment with the most: {department_with_most.idxmax()} "
    f"({department_with_most.max()} employees)"
)


# ============================================================
# EXERCISE 5: Department ranking
# ============================================================
# groupby().rank() ranks values WITHIN each group (no collapsing,
# same 100-row shape as transform) - ascending=False makes the
# highest salary in each department rank 1.

exercise5_df = data_frame.copy()
exercise5_df["salary_rank"] = (
    exercise5_df
    .groupby("department")["salary"]
    .rank(method="min", ascending=False)
    .astype(int)
)

top_three_per_department = (
    exercise5_df[exercise5_df["salary_rank"] <= 3]
    .sort_values(["department", "salary_rank"])
)

print("\n=== Exercise 5: Top 3 earners per department ===")
print(top_three_per_department[["name", "department", "salary", "salary_rank"]])


# ============================================================
# EXERCISE 6: Create and perform a join
# ============================================================

department_info = pd.DataFrame({
    "department": [
        "Engineering",
        "Sales",
        "Marketing",
        "Finance",
        "HR"
    ],
    "manager": [
        "Sarah Connor",
        "Michael Scott",
        "Don Draper",
        "Bruce Wayne",
        "Leslie Knope"
    ],
    "location": [
        "New York",
        "Chicago",
        "Los Angeles",
        "New York",
        "Chicago"
    ]
})

exercise6_df = data_frame.merge(department_info, on="department", how="left")

average_salary_by_location = (
    exercise6_df
    .groupby("location")["salary"]
    .mean()
    .round(2)
)

print("\n=== Exercise 6: Employees with manager/location ===")
print(exercise6_df[["name", "department", "manager", "location", "salary"]].head(10))
print("\nAverage salary by office location:")
print(average_salary_by_location)


# ============================================================
# EXERCISE 7: Detect salary outliers
# ============================================================
# Same transform() trick as exercise 2, but with "std" instead of
# "mean" for the second column, so each row carries both its
# department's mean AND standard deviation to compare against.

exercise7_df = data_frame.copy()
exercise7_df["department_mean"] = (
    exercise7_df.groupby("department")["salary"].transform("mean")
)
exercise7_df["department_std"] = (
    exercise7_df.groupby("department")["salary"].transform("std")
)

outliers = exercise7_df[
    exercise7_df["salary"] > (exercise7_df["department_mean"] + exercise7_df["department_std"])
]

print("\n=== Exercise 7: Salary outliers (> 1 std dev above department mean) ===")
print(outliers[["name", "department", "salary", "department_mean", "department_std"]])


# ============================================================
# EXERCISE 8: Simulate a compensation adjustment
# ============================================================
# pd.cut() again, this time mapping salary bands directly to raise
# percentages, so the whole column gets multiplied in one vectorized
# expression instead of looping row by row.

exercise8_df = data_frame.copy()

raise_bracket = pd.cut(
    exercise8_df["salary"],
    bins=[0, 69_999, 89_999, float("inf")],
    labels=[0.08, 0.05, 0.03],
).astype(float)

exercise8_df["new_salary"] = (exercise8_df["salary"] * (1 + raise_bracket)).round(2)

original_total = exercise8_df["salary"].sum()
new_total = exercise8_df["new_salary"].sum()
raise_cost = new_total - original_total
percent_increase = (raise_cost / original_total) * 100

print("\n=== Exercise 8: Compensation adjustment ===")
print(exercise8_df[["name", "salary", "new_salary"]].head(10))
print(f"\nOriginal total payroll: ${original_total:,.2f}")
print(f"New total payroll:      ${new_total:,.2f}")
print(f"Total cost of raises:   ${raise_cost:,.2f}")
print(f"Percentage increase:    {percent_increase:.2f}%")


# ============================================================
# EXERCISE 9: Experience vs. compensation
# ============================================================

exercise9_df = data_frame.copy()
exercise9_df["experience_group"] = pd.cut(
    exercise9_df["years_experience"],
    bins=[-1, 4, 7, float("inf")],
    labels=["Junior", "Mid", "Senior"],
)

avg_salary_by_group = (
    exercise9_df
    .groupby(["department", "experience_group"], observed=True)["salary"]
    .mean()
    .unstack()
)

# Departments missing a Junior or Senior group get NaN here automatically -
# that's the "handle appropriately" case: idxmax() below skips NaN on its
# own, so a department can't win "biggest gap" on an incomplete comparison.
avg_salary_by_group["junior_to_senior_gap"] = (
    avg_salary_by_group["Senior"] - avg_salary_by_group["Junior"]
)

department_with_biggest_gap = avg_salary_by_group["junior_to_senior_gap"].idxmax()

print("\n=== Exercise 9: Experience vs. compensation ===")
print(avg_salary_by_group.round(2))
print(f"\nDepartment with the largest Junior-to-Senior gap: {department_with_biggest_gap}")


# ============================================================
# EXERCISE 10: Mini ETL challenge
# ============================================================

department_report = data_frame.groupby("department").agg(
    employee_count=("employee_id", "count"),
    active_employee_count=("active", "sum"),
    average_salary=("salary", "mean"),
    median_salary=("salary", "median"),
    average_experience=("years_experience", "mean"),
    highest_salary=("salary", "max"),
).reset_index()

# highest_paid_employee needs the NAME tied to the highest salary in each
# department, which agg() can't do (it only ever sees one column at a
# time). idxmax() gives the ROW LABEL of the max salary per group, which
# is then used to look up that row's name.
idx_of_max_salary = data_frame.groupby("department")["salary"].idxmax()
highest_paid_names = data_frame.loc[idx_of_max_salary, ["department", "name"]]
highest_paid_names = highest_paid_names.rename(columns={"name": "highest_paid_employee"})

department_report = department_report.merge(highest_paid_names, on="department")

department_report["average_salary"] = department_report["average_salary"].round(2)
department_report["average_experience"] = department_report["average_experience"].round(2)

department_report = department_report.sort_values("average_salary", ascending=False)

department_report.to_csv("department_report.csv", index=False)

print("\n=== Exercise 10: Mini ETL challenge ===")
print(department_report)
print("\nSaved to department_report.csv")
```

### Output

```text
=== Exercise 1: Department statistics ===
             number_of_employees  average_salary  minimum_salary  maximum_salary  years_of_experience
department
Engineering                   31        98677.42           76000          120000                 7.87
Finance                       20        91200.00           79000          102000                 7.15
Sales                         20        77300.00           66000           86000                 5.50
Marketing                     15        73133.33           62000           80000                 5.13
HR                            14        69642.86           64000           75000                 4.57

=== Exercise 2: Above-department-average employees ===
                name   department  salary  department_average
42    Queen Phillips  Engineering  120000        98677.419355
75         Xena Wood  Engineering  118000        98677.419355
22         Wendy Lee  Engineering  115000        98677.419355
95      Sara Griffin  Engineering  114000        98677.419355
55        Derek Bell  Engineering  112000        98677.419355
9      Jack Anderson  Engineering  110000        98677.419355
89      Luna Simmons  Engineering  109000        98677.419355
32        Gina Scott  Engineering  108000        98677.419355
69    Rebecca Watson  Engineering  107000        98677.419355
99         Zara Ford  Engineering  106000        98677.419355
2     Carol Williams  Engineering  105000        98677.419355
82      Ethan Powell  Engineering  104000        98677.419355
62       Kira Howard  Engineering  103000        98677.419355
49    Xander Sanchez  Engineering  101000        98677.419355
29     Daniel Wright  Engineering   99000        98677.419355
18   Samuel Robinson      Finance  102000        91200.000000
98       Wyatt Myers      Finance  100000        91200.000000
78    Adam Henderson      Finance   99000        91200.000000
38     Maya Mitchell      Finance   98000        91200.000000
58    Georgia Rivera      Finance   97000        91200.000000
87  Julia Washington      Finance   96000        91200.000000
8       Irene Taylor      Finance   95000        91200.000000
43     Ryan Campbell      Finance   93000        91200.000000
67     Penny Ramirez      Finance   92000        91200.000000
94     Roger Russell           HR   75000        69642.857143
74    Walter Bennett           HR   74000        69642.857143
60    Ivy Richardson           HR   73000        69642.857143
28        Chloe King           HR   72000        69642.857143
88      Kevin Butler           HR   72000        69642.857143
40      Opal Roberts           HR   71000        69642.857143
68      Quincy James           HR   70000        69642.857143
97      Violet Hayes    Marketing   80000        73133.333333
90     Marcus Foster    Marketing   79000        73133.333333
70      Steve Brooks    Marketing   78000        73133.333333
77          Zoe Ross    Marketing   77000        73133.333333
37        Leo Carter    Marketing   76000        73133.333333
57       Fred Bailey    Marketing   75000        73133.333333
30        Ella Lopez    Marketing   74000        73133.333333
96       Trevor Diaz        Sales   86000        77300.000000
76      Yosef Barnes        Sales   85000        77300.000000
91     Nina Gonzales        Sales   84000        77300.000000
21      Victor Lewis        Sales   83000        77300.000000
71        Tara Kelly        Sales   82000        77300.000000
56      Elena Murphy        Sales   81000        77300.000000
41       Paul Turner        Sales   80000        77300.000000
81       Diana Perry        Sales   80000        77300.000000
61         Jason Cox        Sales   79000        77300.000000
46    Ursula Edwards        Sales   78000        77300.000000
86        Ian Flores        Sales   78000        77300.000000

=== Exercise 3: Salary bands ===
             name   department  salary salary_band
0   Alice Johnson  Engineering   92000        High
1       Bob Smith        Sales   68000         Low
2  Carol Williams  Engineering  105000        High
3     David Brown    Marketing   62000         Low
4      Emma Davis      Finance   88000      Medium
5    Frank Miller  Engineering   76000      Medium
6    Grace Wilson           HR   65000         Low
7     Henry Moore        Sales   72000      Medium
8    Irene Taylor      Finance   95000        High
9   Jack Anderson  Engineering  110000   Very High

Counts by department and band:
salary_band  Low  Medium  High  Very High
department
Engineering    0       8    17          6
Finance        0       8    12          0
HR             7       7     0          0
Marketing      3      12     0          0
Sales          3      17     0          0

=== Exercise 4: Experienced but underpaid ===
             name department  salary  years_experience
4      Emma Davis    Finance   88000                 7
21   Victor Lewis      Sales   83000                 7
47  Vince Collins    Finance   89000                 7
76   Yosef Barnes      Sales   85000                 7
91  Nina Gonzales      Sales   84000                 7
96    Trevor Diaz      Sales   86000                 7

Count by department:
department
Sales      4
Finance    2
Name: count, dtype: int64

Department with the most: Sales (4 employees)

=== Exercise 5: Top 3 earners per department ===
               name   department  salary  salary_rank
42   Queen Phillips  Engineering  120000            1
75        Xena Wood  Engineering  118000            2
22        Wendy Lee  Engineering  115000            3
18  Samuel Robinson      Finance  102000            1
98      Wyatt Myers      Finance  100000            2
78   Adam Henderson      Finance   99000            3
94    Roger Russell           HR   75000            1
74   Walter Bennett           HR   74000            2
60   Ivy Richardson           HR   73000            3
97     Violet Hayes    Marketing   80000            1
90    Marcus Foster    Marketing   79000            2
70     Steve Brooks    Marketing   78000            3
96      Trevor Diaz        Sales   86000            1
76     Yosef Barnes        Sales   85000            2
91    Nina Gonzales        Sales   84000            3

=== Exercise 6: Employees with manager/location ===
             name   department        manager     location  salary
0   Alice Johnson  Engineering   Sarah Connor     New York   92000
1       Bob Smith        Sales  Michael Scott      Chicago   68000
2  Carol Williams  Engineering   Sarah Connor     New York  105000
3     David Brown    Marketing     Don Draper  Los Angeles   62000
4      Emma Davis      Finance    Bruce Wayne     New York   88000
5    Frank Miller  Engineering   Sarah Connor     New York   76000
6    Grace Wilson           HR   Leslie Knope      Chicago   65000
7     Henry Moore        Sales  Michael Scott      Chicago   72000
8    Irene Taylor      Finance    Bruce Wayne     New York   95000
9   Jack Anderson  Engineering   Sarah Connor     New York  110000

Average salary by office location:
location
Chicago        74147.06
Los Angeles    73133.33
New York       95745.10
Name: salary, dtype: float64

=== Exercise 7: Salary outliers (> 1 std dev above department mean) ===
               name   department  salary  department_mean  department_std
18  Samuel Robinson      Finance  102000     91200.000000     6329.546421
21     Victor Lewis        Sales   83000     77300.000000     5685.623606
22        Wendy Lee  Engineering  115000     98677.419355    11634.394689
38    Maya Mitchell      Finance   98000     91200.000000     6329.546421
42   Queen Phillips  Engineering  120000     98677.419355    11634.394689
55       Derek Bell  Engineering  112000     98677.419355    11634.394689
70     Steve Brooks    Marketing   78000     73133.333333     4748.934718
74   Walter Bennett           HR   74000     69642.857143     3387.922959
75        Xena Wood  Engineering  118000     98677.419355    11634.394689
76     Yosef Barnes        Sales   85000     77300.000000     5685.623606
78   Adam Henderson      Finance   99000     91200.000000     6329.546421
90    Marcus Foster    Marketing   79000     73133.333333     4748.934718
91    Nina Gonzales        Sales   84000     77300.000000     5685.623606
94    Roger Russell           HR   75000     69642.857143     3387.922959
95     Sara Griffin  Engineering  114000     98677.419355    11634.394689
96      Trevor Diaz        Sales   86000     77300.000000     5685.623606
97     Violet Hayes    Marketing   80000     73133.333333     4748.934718
98      Wyatt Myers      Finance  100000     91200.000000     6329.546421

=== Exercise 8: Compensation adjustment ===
             name  salary  new_salary
0   Alice Johnson   92000     94760.0
1       Bob Smith   68000     73440.0
2  Carol Williams  105000    108150.0
3     David Brown   62000     66960.0
4      Emma Davis   88000     92400.0
5    Frank Miller   76000     79800.0
6    Grace Wilson   65000     70200.0
7     Henry Moore   72000     75600.0
8    Irene Taylor   95000     97850.0
9   Jack Anderson  110000    113300.0

Original total payroll: $8,501,000.00
New total payroll:      $8,881,550.00
Total cost of raises:   $380,550.00
Percentage increase:    4.48%

=== Exercise 9: Experience vs. compensation ===
experience_group    Junior       Mid     Senior  junior_to_senior_gap
department
Engineering       76000.00  89000.00  107411.76              31411.76
Finance                NaN  87461.54   98142.86                   NaN
HR                67166.67  71500.00        NaN                   NaN
Marketing         66333.33  74833.33        NaN                   NaN
Sales             67666.67  79000.00        NaN                   NaN

Department with the largest Junior-to-Senior gap: Engineering

=== Exercise 10: Mini ETL challenge ===
    department  employee_count  active_employee_count  average_salary  median_salary  average_experience  highest_salary highest_paid_employee
0  Engineering              31                     29        98677.42        98000.0                7.87          120000        Queen Phillips
1      Finance              20                     18        91200.00        91000.0                7.15          102000       Samuel Robinson
4        Sales              20                     17        77300.00        78000.0                5.50           86000           Trevor Diaz
3    Marketing              15                     14        73133.33        73000.0                5.13           80000          Violet Hayes
2           HR              14                     13        69642.86        69500.0                4.57           75000         Roger Russell

Saved to department_report.csv
```
