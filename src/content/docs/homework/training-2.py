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
