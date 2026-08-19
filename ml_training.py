import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)

CSV_PATH = "/Users/saijoshi/.cache/huggingface/hub/datasets--opensporks--resumes/snapshots/ed4cb5f3fd1ce7e0a0e74e1a09c1a3b702c2c2eb/Resume/Resume.csv"

# 1. Load dataset
df = pd.read_csv(CSV_PATH)

# 2. Clean dataset
df["Resume_str"] = df["Resume_str"].fillna("").str.strip()

# Remove empty resumes
df = df[df["Resume_str"] != ""].copy()

# Remove duplicate resume texts
df = df.drop_duplicates(subset="Resume_str")

# 3. Input and target
X = df["Resume_str"]
y = df["Category"]

print("Usable resumes:", len(df))
print("Categories:", y.nunique())

# 4. Stratified train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

# 5. TF-IDF + Logistic Regression
model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
        ),
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
        ),
    ),
])

# 6. Train
print("\nTraining model...")
model.fit(X_train, y_train)

# 7. Predict
predictions = model.predict(X_test)

# 8. Evaluate
accuracy = accuracy_score(y_test, predictions)

print("\nAccuracy:")
print(f"{accuracy:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))

# 9. Save serialized pipeline model
import os
import joblib

models_dir = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(models_dir, exist_ok=True)
model_path = os.path.join(models_dir, "role_classifier.joblib")

print(f"\nSaving trained model pipeline to {model_path}...")
joblib.dump(model, model_path)
print("Model saved successfully!")

# 10. Confusion Matrix (optional display)
if os.environ.get("DISPLAY"):
    cm = confusion_matrix(
        y_test,
        predictions,
        labels=model.classes_,
    )

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=model.classes_,
    )

    disp.plot(xticks_rotation=90)
    plt.tight_layout()
    plt.show()