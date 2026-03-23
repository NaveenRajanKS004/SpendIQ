import os
import csv
from io import StringIO
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..security import get_current_user
from ..services.ml_service import predict_category, retrain_model


# This router handles transaction operations:
# - manual creation
# - listing with filters
# - CSV uploads
# - category correction (ML feedback loop)
# - available months extraction

router = APIRouter()


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
# CREATE TRANSACTION
# =========================

@router.post("/transactions", response_model=schemas.TransactionResponse)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    description = (transaction.description or "").strip()
    category = transaction.category

    # ML fallback (will work after Step 2)
    if not category and description:
        category = predict_category(description.lower())

    new_transaction = models.Transaction(
        amount=transaction.amount,
        category=category,
        description=description,
        transaction_type=transaction.transaction_type.value,  # ✅ ENUM FIX
        user_id=current_user.id,
        created_at=datetime.utcnow()
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


# =========================
# LIST TRANSACTIONS
# =========================

@router.get("/transactions", response_model=List[schemas.TransactionResponse])
def get_transactions(
    month: Optional[str] = None,
    category: Optional[str] = None,
    txn_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    query = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    )

    # Month filter
    if month:
        try:
            start_date = datetime.strptime(month, "%Y-%m")

            if start_date.month == 12:
                end_date = datetime(start_date.year + 1, 1, 1)
            else:
                end_date = datetime(start_date.year, start_date.month + 1, 1)

            query = query.filter(
                models.Transaction.created_at >= start_date,
                models.Transaction.created_at < end_date
            )

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid month format. Use YYYY-MM"
            )

    # Optional filters
    if category:
        query = query.filter(models.Transaction.category == category)

    if txn_type:
        query = query.filter(
            models.Transaction.transaction_type == txn_type.lower()
        )

    return query.all()


# =========================
# CSV UPLOAD
# =========================

@router.post("/transactions/upload")
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
            description = (row.get("description") or "").strip()
            category = (row.get("category") or "").strip()

            if not description:
                continue

            if not category:
                category = predict_category(description.lower())

            txn_date = None
            if row.get("date"):
                txn_date = datetime.strptime(row["date"], "%Y-%m-%d")

            amount = float(str(row.get("amount", 0)).replace(",", ""))

            # ⚠️ TEMP: keep as-is (Step 3 will fix mapping)
            txn_type = (row.get("transaction_type") or "expense").lower()

            new_transaction = models.Transaction(
                amount=amount,
                category=category,
                description=description,
                transaction_type=txn_type,
                user_id=current_user.id,
                created_at=txn_date if txn_date else datetime.utcnow()
            )

            db.add(new_transaction)
            inserted_count += 1

        except Exception as e:
            print("CSV row error:", e)
            continue

    db.commit()

    return {
        "message": "CSV processed successfully",
        "transactions_inserted": inserted_count
    }


# =========================
# CATEGORY CORRECTION
# =========================

@router.put("/transactions/{transaction_id}/correct")
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

    feedback_path = os.path.join("ml", "user_feedback.csv")
    file_exists = os.path.exists(feedback_path)

    with open(feedback_path, "a") as f:

        if not file_exists:
            f.write("description,category\n")

        f.write(f"{txn.description},{correction.category}\n")

    txn.category = correction.category
    db.commit()

    retrain_model()

    return {
        "message": "Category corrected. Model retraining in background."
    }


# =========================
# AVAILABLE MONTHS
# =========================

@router.get("/transactions/months")
def get_available_months(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()

    months = set()

    for txn in transactions:
        months.add(txn.created_at.strftime("%Y-%m"))

    return sorted(list(months))