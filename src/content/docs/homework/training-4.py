import hashlib
import pandas as pd

text1 = "Hello Data Engineering"
text2 = "Hello Data Engineering!"


df = pd.DataFrame({
    "employee_id": [1, 2, 3],
    "name": ["Alice", "Bob", "Carol"],
    "department": ["Engineering", "Sales", "Finance"],
    "salary": [92000, 68000, 88000]
})


def create_hash(row):
    # Combine the columns into one string
    text = f"{row['name']}|{row['department']}|{row['salary']}"

    # Generate SHA-256 hash
    return hashlib.sha256(text.encode()).hexdigest()


df["row_hash"] = df.apply(create_hash, axis=1)

print(df)
