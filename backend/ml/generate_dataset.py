import random
import pandas as pd
import string

categories = {
    "Food": [
        "swiggy", "zomato", "restaurant",
        "kirana store", "cafe", "hotel"
    ],
    "Transport": [
        "uber", "ola", "petrol pump",
        "fuel station", "hpcl"
    ],
    "Shopping": [
        "amazon", "flipkart", "store",
        "mall purchase", "retail shop"
    ],
    "Healthcare": [
        "apollo", "medplus", "hospital",
        "clinic", "pharmacy"
    ],
    "Utilities": [
        "electricity", "water bill",
        "gas bill", "mobile recharge",
        "internet payment"
    ],
    "Entertainment": [
        "netflix", "spotify",
        "movie", "gaming",
        "bookmyshow"
    ],
    "Income": [
        "salary", "bonus",
        "consulting payment",
        "freelance credit"
    ],
    "Transfers": [
        "upi transfer", "bank transfer",
        "imps", "sent to friend",
        "upi to ramesh"
    ]
}

formats = [
    "UPI/{rand}/{merchant}/{code}",
    "POS {rand} {merchant} MUMBAI",
    "NEFT-{merchant}-{rand}",
    "{merchant} PAYMENT",
    "{merchant} ONLINE",
]

def random_digits(n=6):
    return ''.join(random.choices(string.digits, k=n))

def random_code():
    return ''.join(random.choices(string.ascii_lowercase, k=4)) + "@okaxis"

rows = []

for category, merchants in categories.items():
    for _ in range(150):
        merchant = random.choice(merchants).upper()
        fmt = random.choice(formats)

        description = fmt.format(
            merchant=merchant,
            rand=random_digits(),
            code=random_code()
        )

        # 5% label noise
        if random.random() < 0.02:
            category = random.choice(list(categories.keys()))

        rows.append({
            "description": description,
            "category": category
        })

df = pd.DataFrame(rows)
df.to_csv("ml/dataset.csv", index=False)

print("Hard-mode noisy dataset generated with", len(df), "rows.")