import pandas as pd

CSV_PATH = "/Users/saijoshi/.cache/huggingface/hub/datasets--opensporks--resumes/snapshots/ed4cb5f3fd1ce7e0a0e74e1a09c1a3b702c2c2eb/Resume/Resume.csv"

df = pd.read_csv(CSV_PATH)

df["text_length"] = df["Resume_str"].fillna("").str.len()

print("10 shortest resumes:\n")
shortest = df.sort_values("text_length").head(10)

for _, row in shortest.iterrows():
    print("=" * 80)
    print("ID:", row["ID"])
    print("Category:", row["Category"])
    print("Length:", row["text_length"])
    print("Text:")
    print(row["Resume_str"])