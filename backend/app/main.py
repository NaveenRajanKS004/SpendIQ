import pickle
import os
from fastapi import UploadFile, File
import csv
from io import StringIO
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt

from .database import engine, SessionLocal
from . import models, schemas
from .security import hash_password, verify_password

# =========================
# JWT CONFIG
# =========================

SECRET_KEY = "change_this_to_a_random_secure_string"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# =========================
# DATABASE SETUP
# =========================

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SpendIQ API")

# =========================
# LOGIN PAGE ROUTE
# =========================

@app.get("/login-page")
def serve_login_page():
    return FileResponse("app/static/login.html")

# =========================
# REGISTER PAGE ROUTE
# =========================

@app.get("/register-page")
def serve_register_page():
    return FileResponse("app/static/register.html")

# =========================
# DASHBOARD STATIC FILES
# =========================

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/dashboard")
def serve_dashboard():
    return FileResponse("app/static/dashboard.html")

# =========================
# LOAD ML MODEL
# =========================

MODEL_PATH = os.path.join("ml", "transaction_classifier.pkl")

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        ml_model = pickle.load(f)
else:
    ml_model = None

# =========================
# RULE-BASED KEYWORDS (HYBRID LAYER)
# =========================

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
# DATABASE DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# TOKEN CREATION
# =========================

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# =========================
# AUTH DEPENDENCY
# =========================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(
        models.User.id == int(user_id)
    ).first()

    if user is None:
        raise credentials_exception

    return user

# =========================
# HYBRID PREDICTION FUNCTION
# =========================

def predict_category(description: str):
    description_lower = description.lower()

    # 🔹 Rule Layer
    for category, keywords in RULE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category

    # 🔹 ML Layer
    if not ml_model:
        return "Uncategorized"

    prediction = ml_model.predict([description_lower])
    return prediction[0]

# =========================
# ROUTES
# =========================

@app.get("/")
def root():
    return {"message": "SpendIQ backend is running"}

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_pw = hash_password(user.password)

    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )

    if not verify_password(
        form_data.password,
        db_user.hashed_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )

    access_token_expires = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/me", response_model=schemas.UserResponse)
def read_current_user(
    current_user: models.User = Depends(get_current_user)
):
    return current_user

# =========================
# TRANSACTION ROUTES
# =========================

@app.post("/transactions", response_model=schemas.TransactionResponse)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_transaction = models.Transaction(
        amount=transaction.amount,
        category=transaction.category,
        description=transaction.description,
        transaction_type=transaction.transaction_type,
        user_id=current_user.id
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

@app.get("/transactions", response_model=List[schemas.TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()

# =========================
# SUMMARY ROUTES
# =========================

@app.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()

    total_income = 0
    total_expense = 0

    for txn in transactions:
        if txn.transaction_type == "income":
            total_income += txn.amount
        elif txn.transaction_type == "expense":
            total_expense += txn.amount

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }

@app.get("/summary/categories")
def get_category_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.transaction_type == "expense"
    ).all()

    category_totals = {}

    for txn in transactions:
        category_totals[txn.category] = (
            category_totals.get(txn.category, 0) + txn.amount
        )

    return category_totals

@app.get("/summary/monthly")
def get_monthly_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()

    monthly_data = {}

    for txn in transactions:
        month_key = txn.created_at.strftime("%Y-%m")

        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "income": 0,
                "expense": 0,
                "balance": 0
            }

        if txn.transaction_type == "income":
            monthly_data[month_key]["income"] += txn.amount
        elif txn.transaction_type == "expense":
            monthly_data[month_key]["expense"] += txn.amount

        monthly_data[month_key]["balance"] = (
            monthly_data[month_key]["income"]
            - monthly_data[month_key]["expense"]
        )

    return monthly_data

# =========================
# SMART INSIGHTS
# =========================

@app.get("/summary/insights")
def get_insights(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()

    total_transactions = len(transactions)

    highest_expense = 0
    category_totals = {}

    for txn in transactions:
        if txn.transaction_type == "expense":
            if txn.amount > highest_expense:
                highest_expense = txn.amount

            category_totals[txn.category] = (
                category_totals.get(txn.category, 0) + txn.amount
            )

    top_category = None
    if category_totals:
        top_category = max(category_totals, key=category_totals.get)

    return {
        "total_transactions": total_transactions,
        "highest_expense": highest_expense,
        "top_category": top_category
    }

# =========================
# CSV UPLOAD ROUTE (HYBRID ENABLED)
# =========================

@app.post("/transactions/upload")
def upload_transactions_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(content))

    inserted_count = 0

    for row in csv_reader:
        try:
            description = row.get("description", "").strip()
            category = row.get("category", "").strip()

            if not category:
                category = predict_category(description)

            new_transaction = models.Transaction(
                amount=float(row["amount"]),
                category=category,
                description=description,
                transaction_type=row["transaction_type"],
                user_id=current_user.id
            )

            db.add(new_transaction)
            inserted_count += 1

        except Exception:
            continue

    db.commit()

    return {
        "message": "CSV processed successfully",
        "transactions_inserted": inserted_count
    }


@app.put("/transactions/{transaction_id}/correct")
def correct_transaction_category(
    transaction_id: int,
    correction: schemas.CategoryCorrection,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    txn = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()

    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Save correction to feedback dataset
    feedback_path = os.path.join("ml", "user_feedback.csv")
    file_exists = os.path.exists(feedback_path)

    with open(feedback_path, "a") as f:
        if not file_exists:
            f.write("description,category\n")
        f.write(f"{txn.description},{correction.category}\n")

    # Update transaction in DB
    txn.category = correction.category
    db.commit()

    return {"message": "Category corrected and feedback stored"}


#source venv/bin/activate
#uvicorn app.main:app --reload