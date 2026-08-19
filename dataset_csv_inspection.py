import pandas as pd

CSV_PATH = "/Users/saijoshi/.cache/huggingface/hub/datasets--opensporks--resumes/snapshots/ed4cb5f3fd1ce7e0a0e74e1a09c1a3b702c2c2eb/Resume/Resume.csv"

print("Loading CSV...")
df = pd.read_csv(CSV_PATH)

print("\nDataset loaded successfully.")

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 3 rows:")
print(df.head(3))

print("\nMissing values:")
print(df.isnull().sum())

print("\nNumber of categories:")
print(df["Category"].nunique())

print("\nCategory counts:")
print(df["Category"].value_counts())

print("\nCategory proportions:")
print(df["Category"].value_counts(normalize=True).round(3))

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nDuplicate resume texts:")
print(df["Resume_str"].duplicated().sum())

print("\nResume text length statistics:")
text_lengths = df["Resume_str"].fillna("").str.len()
print(text_lengths.describe())

print("\nShortest resume length:")
print(text_lengths.min())

print("\nLongest resume length:")
print(text_lengths.max())

print("\nInspection complete.")