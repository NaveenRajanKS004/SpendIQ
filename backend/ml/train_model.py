import pandas as pd
import pickle
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report

# ==============================
# CLEANING FUNCTION
# ==============================

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ==============================
# LOAD BASE DATASET
# ==============================

base_path = os.path.join("ml", "dataset.csv")
df = pd.read_csv(base_path)

# ==============================
# LOAD USER FEEDBACK (if exists)
# ==============================

feedback_path = os.path.join("ml", "user_feedback.csv")

if os.path.exists(feedback_path):
    feedback_df = pd.read_csv(feedback_path)
    print(f"Loaded {len(feedback_df)} feedback samples.")
    df = pd.concat([df, feedback_df], ignore_index=True)
else:
    print("No feedback dataset found.")

df = df.dropna()

# ==============================
# CLEAN TEXT
# ==============================

df["description"] = df["description"].apply(clean_text)

X = df["description"]
y = df["category"]

# ==============================
# SAFE TRAIN TEST SPLIT
# ==============================

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

# ==============================
# BUILD PIPELINE
# ==============================

model_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words="english"
    )),
    ("clf", LinearSVC(
        class_weight="balanced"
    ))
])

model_pipeline.fit(X_train, y_train)

# ==============================
# EVALUATE
# ==============================

y_pred = model_pipeline.predict(X_test)

print("\nModel Evaluation:\n")
print(classification_report(y_test, y_pred, zero_division=0))

# ==============================
# SAVE MODEL
# ==============================

model_path = os.path.join("ml", "transaction_classifier.pkl")

with open(model_path, "wb") as f:
    pickle.dump(model_pipeline, f)

print("\nModel trained and saved successfully.")