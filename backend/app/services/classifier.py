import os
import pickle


# =========================
# MODEL LOADING
# =========================

# Path to trained ML model
MODEL_PATH = os.path.join("ml", "transaction_classifier.pkl")

# Load model if available, else fallback to rule-based classification
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        ml_model = pickle.load(f)
else:
    ml_model = None


# =========================
# RULE-BASED KEYWORDS
# =========================

# Simple keyword mapping for fast, deterministic classification
# Used as primary fallback before ML
RULE_KEYWORDS = {
    "Income": ["salary", "bonus", "credit"],
    "Food": ["swiggy", "zomato", "restaurant", "cafe", "kirana", "tea", "stall"],
    "Transport": ["uber", "ola", "petrol", "fuel"],
    "Shopping": ["amazon", "flipkart", "myntra", "mall"],
    "Healthcare": ["apollo", "medplus", "hospital", "clinic", "pharmacy"],
    "Utilities": ["electricity", "water", "gas", "recharge", "internet"],
    "Entertainment": ["netflix", "spotify", "movie", "gaming", "bookmyshow"],
    "Transfers": ["upi to", "imps", "bank transfer", "sent to"]
}


# =========================
# CATEGORY PREDICTION
# =========================

def predict_category(description: str):
    """
    Predict category using:
    1. Rule-based keyword matching (fast, deterministic)
    2. ML model (if available)
    3. Fallback to 'Uncategorized'
    """

    description_lower = description.lower()

    # Step 1: Rule-based keyword matching
    for category, keywords in RULE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category

    # Step 2: ML-based prediction (if model exists)
    if not ml_model:
        return "Uncategorized"

    try:
        prediction = ml_model.predict([description_lower])
        return prediction[0]

    except Exception:
        # Fallback if model prediction fails
        return "Uncategorized"