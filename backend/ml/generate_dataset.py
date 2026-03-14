import random
import pandas as pd
import string

rows = []

# ==============================
# REAL MERCHANT PATTERNS
# ==============================

merchant_rules = {
    "Food": [
        "zomato",
        "swiggy",
        "restaurant",
        "cafe",
        "bbnow",
        "bigbasket"
    ],

    "Transport": [
        "uber",
        "ola",
        "fuel",
        "petrol"
    ],

    "Shopping": [
        "amazon",
        "flipkart",
        "store",
        "mall"
    ],

    "Healthcare": [
        "apollo",
        "medplus",
        "hospital",
        "pharmacy"
    ],

    "Utilities": [
        "electricity",
        "billpay",
        "internet",
        "mobile recharge",
        "gas bill"
    ],

    "Entertainment": [
        "netflix",
        "spotify",
        "gaming",
        "bookmyshow"
    ],

    "Income": [
        "salary",
        "sparrkle technologies",
        "bonus",
        "credit"
    ],

    "Transfers": [
        "upi",
        "imps",
        "neft",
        "transfer",
        "payment from phone"
    ]
}

# ==============================
# REALISTIC TRANSACTION FORMATS
# ==============================

formats = [
    "UPI-{merchant}-PAYMENT",
    "UPI-{merchant}-{rand}",
    "POS {merchant} STORE",
    "{merchant} ONLINE PAYMENT",
    "NEFT CR-{merchant}",
    "IMPS-{merchant}",
    "UPI-{merchant}-PAYMENT FROM PHONE"
]

# ==============================
# RANDOM HELPERS
# ==============================

def random_digits(n=6):
    return ''.join(random.choices(string.digits, k=n))


# ==============================
# GENERATE DATASET
# ==============================

for category, merchants in merchant_rules.items():

    for _ in range(300):

        merchant = random.choice(merchants).upper()

        fmt = random.choice(formats)

        description = fmt.format(
            merchant=merchant,
            rand=random_digits()
        )

        rows.append({
            "description": description,
            "category": category
        })


# ==============================
# ADD SOME NOISE
# ==============================

for row in rows:
    if random.random() < 0.02:
        row["category"] = random.choice(list(merchant_rules.keys()))


df = pd.DataFrame(rows)

df.to_csv("ml/dataset.csv", index=False)

print("Dataset generated:", len(df), "rows")