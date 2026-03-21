from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models
from ..security import get_current_user


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# OVERALL SUMMARY
# =========================

@router.get("/summary")
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


# =========================
# CATEGORY SUMMARY
# =========================

@router.get("/summary/categories")
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


# =========================
# MONTHLY SUMMARY
# =========================

@router.get("/summary/monthly")
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
# YEARLY SUMMARY
# =========================

@router.get("/summary/yearly")
def get_yearly_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()

    yearly_data = {}

    for txn in transactions:

        year_key = txn.created_at.strftime("%Y")

        if year_key not in yearly_data:
            yearly_data[year_key] = {
                "income": 0,
                "expense": 0,
                "balance": 0
            }

        if txn.transaction_type == "income":
            yearly_data[year_key]["income"] += txn.amount

        elif txn.transaction_type == "expense":
            yearly_data[year_key]["expense"] += txn.amount

        yearly_data[year_key]["balance"] = (
            yearly_data[year_key]["income"]
            - yearly_data[year_key]["expense"]
        )

    return yearly_data


# =========================
# INSIGHTS
# =========================

@router.get("/summary/insights")
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
# YEARLY ANALYTICS
# =========================

@router.get("/analytics/yearly")
def get_yearly_analytics(
    year: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()

    monthly_income = [0] * 12
    monthly_expense = [0] * 12
    category_totals = {}

    total_income = 0
    total_expense = 0

    for txn in transactions:

        if txn.created_at.year != year:
            continue

        month_index = txn.created_at.month - 1

        if txn.transaction_type == "income":

            monthly_income[month_index] += txn.amount
            total_income += txn.amount

        else:

            monthly_expense[month_index] += txn.amount
            total_expense += txn.amount

            category_totals[txn.category] = (
                category_totals.get(txn.category, 0) + txn.amount
            )

    return {
        "income": total_income,
        "expense": total_expense,
        "balance": total_income - total_expense,
        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense,
        "category_totals": category_totals
    }


# =========================
# MONTHLY ANALYTICS
# =========================

@router.get("/analytics/monthly")
def get_monthly_analytics(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()

    total_income = 0
    total_expense = 0
    category_totals = {}
    month_transactions = []

    for txn in transactions:

        if txn.created_at.year != year:
            continue

        if txn.created_at.month != month:
            continue

        if txn.transaction_type == "income":
            total_income += txn.amount
        else:
            total_expense += txn.amount

            category_totals[txn.category] = (
                category_totals.get(txn.category, 0) + txn.amount
            )

        month_transactions.append({
            "id": txn.id,  # ✅ FIX: required for correction
            "date": txn.created_at.strftime("%Y-%m-%d"),
            "category": txn.category,
            "description": txn.description,
            "amount": txn.amount,
            "type": txn.transaction_type
        })

    return {
        "income": total_income,
        "expense": total_expense,
        "balance": total_income - total_expense,
        "category_totals": category_totals,
        "transactions": month_transactions
    }