---
title: "Training 2 Homework"
description: "Homework assignment for Training 2: Python and Pandas."
sidebar:
  order: 2
---

:::note
The assignment prompt as given in class. Related notes: [Training 2](/training-notes-site/notes/training-2/).
:::

## Homework Assignment: Pandas — 10 Exercises

**Teacher:** Evan Flint
**Related notes:** [Training 2](/training-notes-site/notes/training-2/) (Python + Pandas)

### Objective

Use the [`data.csv`](/training-notes-site/homework/data.csv) employee dataset from class. Unless specifically instructed otherwise, solve each problem using Pandas rather than loops over individual rows.

### Exercises

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
   70,000–89,999       -> "Medium"
   90,000–109,999      -> "High"
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
   Salary $70,000–$89,999       -> 5% raise
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
   0–4 years    -> Junior
   5–7 years    -> Mid
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

### Challenge Constraint

For **questions 2, 5, 7, 9, and 10**, do not use a Python `for` loop to process employees individually. The objective is to solve the problem using DataFrame operations such as `groupby()`, `transform()`, `rank()`, `agg()`, `merge()`, boolean indexing, and related Pandas functionality.

These should push beyond the basic `read_csv()` → filter → `.sum()` examples from class and require discovering several important Pandas operations independently.

---

### Submission

*(Add your answers below, one section per exercise.)*

#### 1. Department statistics

#### 2. Above-department-average employees

#### 3. Salary bands

#### 4. Experienced but underpaid

#### 5. Department ranking

#### 6. Create and perform a join

#### 7. Detect salary outliers

#### 8. Simulate a compensation adjustment

#### 9. Experience vs. compensation

#### 10. Mini ETL challenge
