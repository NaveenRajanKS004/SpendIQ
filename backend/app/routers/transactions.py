import os
import csv
from io import StringIO
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..security import get_current_user
from ..services.classifier import predict_category


router = APIRouter()


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

    if month:
        try:
            start_date = datetime.strptime(month, "%Y-%m")
            end_date = datetime(
                start_date.year + (start_date.month // 12),
                ((start_date.month % 12) + 1),
                1
            )

            query = query.filter(
                models.Transaction.created_at >= start_date,
                models.Transaction.created_at < end_date
            )

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid month format. Use YYYY-MM"
            )

    if category:
        query = query.filter(models.Transaction.category == category)

    if txn_type:
        query = query.filter(models.Transaction.transaction_type == txn_type)

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

            description = row.get("description", "").strip()
            category = row.get("category", "").strip()

            if not category:
                category = predict_category(description)

            new_transaction = models.Transaction(
                amount=float(row.get("amount", 0)),
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

    return {"message": "Category corrected and feedback stored"}