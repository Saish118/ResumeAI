from datasets import load_dataset
import pandas as pd

print("Loading dataset...")

dataset = load_dataset("opensporks/resumes")

print("\nDataset loaded successfully!")
print(dataset)

# Inspect available splits
print("\nAvailable splits:")
print(dataset.keys())

# Use the training split if available
split_name = "train" if "train" in dataset else list(dataset.keys())[0]
df = dataset[split_name].to_pandas()

print(f"\nUsing split: {split_name}")

print("\nDataset shape:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

# Look for the category column
if "Category" in df.columns:
    print("\nNumber of categories:")
    print(df["Category"].nunique())

    print("\nCategories:")
    print(df["Category"].value_counts())

    print("\nCategory distribution:")
    print(df["Category"].value_counts(normalize=True).round(3))

# Check duplicates
print("\nNumber of duplicate rows:")
print(df.duplicated().sum())