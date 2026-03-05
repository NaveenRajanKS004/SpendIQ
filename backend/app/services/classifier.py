import os
import pickle

MODEL_PATH = os.path.join("ml", "transaction_classifier.pkl")

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        ml_model = pickle.load(f)
else:
    ml_model = None


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


def predict_category(description: str):

    description_lower = description.lower()

    for category, keywords in RULE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category

    if not ml_model:
        return "Uncategorized"

    try:
        prediction = ml_model.predict([description_lower])
        return prediction[0]
    except:
        return "Uncategorized"