import pickle
import os
import subprocess
import threading

MODEL_PATH = os.path.join("ml", "transaction_classifier.pkl")

model = None


def load_model():
    global model

    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)


def predict_category(description: str):

    global model

    if model is None:
        load_model()

    if model is None:
        return "Uncategorized"

    prediction = model.predict([description])[0]

    return prediction


# =========================
# BACKGROUND RETRAINING
# =========================

def retrain_model():

    def train():

        try:

            subprocess.run(
                ["python", "ml/train_model.py"],
                check=True
            )

            load_model()

            print("Model retrained successfully")

        except Exception as e:
            print("Retraining failed:", e)

    thread = threading.Thread(target=train)

    thread.start()