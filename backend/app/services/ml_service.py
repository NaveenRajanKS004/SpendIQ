import pickle
import os
import subprocess
import threading


# =========================
# MODEL CONFIGURATION
# =========================

# Path to trained ML model
MODEL_PATH = os.path.join("ml", "transaction_classifier.pkl")

# Global model instance (lazy-loaded)
model = None


# =========================
# MODEL LOADING
# =========================

def load_model():
    """
    Load ML model from disk into memory.
    Called lazily when prediction is first needed
    or after retraining.
    """
    global model

    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)


# =========================
# CATEGORY PREDICTION
# =========================

def predict_category(description: str):
    """
    Predict transaction category using ML model.
    Falls back to 'Uncategorized' if model is unavailable.
    """
    global model

    # Lazy-load model if not already loaded
    if model is None:
        load_model()

    # If still unavailable, fallback
    if model is None:
        return "Uncategorized"

    # Perform prediction
    prediction = model.predict([description])[0]

    return prediction


# =========================
# BACKGROUND RETRAINING
# =========================

def retrain_model():
    """
    Trigger model retraining in a background thread.
    This prevents blocking API responses.
    """

    def train():
        try:
            # Run training script
            subprocess.run(
                ["python", "ml/train_model.py"],
                check=True
            )

            # Reload updated model into memory
            load_model()

            print("Model retrained successfully")

        except Exception as e:
            # Log failure without crashing main app
            print("Retraining failed:", e)

    # Run training in background thread
    thread = threading.Thread(target=train)
    thread.start()