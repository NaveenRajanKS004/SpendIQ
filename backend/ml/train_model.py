# =========================
# IMPORTS
# =========================

import os
import re
import pickle

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report


# =========================
# CONFIG
# =========================

BASE_DATASET_PATH = os.path.join("ml", "dataset.csv")
FEEDBACK_DATASET_PATH = os.path.join("ml", "user_feedback.csv")
MODEL_PATH = os.path.join("ml", "transaction_classifier.pkl")


# =========================
# TEXT CLEANING
# =========================

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =========================
# LOAD DATA
# =========================

# Load base dataset
df = pd.read_csv(BASE_DATASET_PATH)


# =========================
# LOAD USER FEEDBACK (OPTIONAL)
# =========================

if os.path.exists(FEEDBACK_DATASET_PATH):

    feedback_df = pd.read_csv(FEEDBACK_DATASET_PATH)

    print(f"Loaded {len(feedback_df)} feedback samples.")

    df = pd.concat([df, feedback_df], ignore_index=True)

else:
    print("No feedback dataset found.")


# =========================
# PREPROCESSING
# =========================

# Drop invalid rows
df = df.dropna()

# Clean descriptions
df["description"] = df["description"].apply(clean_text)

# Features & labels
X = df["description"]
y = df["category"]


# =========================
# TRAIN-TEST SPLIT (SAFE)
# =========================

class_counts = y.value_counts()

if class_counts.min() < 2:
    print("Warning: Some classes have <2 samples. Disabling stratified split.")
    stratify_option = None
else:
    stratify_option = y


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=stratify_option
)


# =========================
# MODEL PIPELINE
# =========================

model_pipeline = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english"
        )
    ),
    (
        "clf",
        LinearSVC(
            class_weight="balanced"
        )
    )
])


# =========================
# TRAIN MODEL
# =========================

model_pipeline.fit(X_train, y_train)


# =========================
# EVALUATION
# =========================

y_pred = model_pipeline.predict(X_test)

print("\nModel Evaluation:\n")
print(classification_report(y_test, y_pred, zero_division=0))


# =========================
# SAVE MODEL
# =========================

with open(MODEL_PATH, "wb") as f:
    pickle.dump(model_pipeline, f)

print("\nModel trained and saved successfully.")