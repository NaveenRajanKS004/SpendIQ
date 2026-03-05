from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import models, schemas
from ..security import get_current_user


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# SET BUDGET
# =========================

@router.post("/budgets", response_model=schemas.BudgetResponse)
def set_budget(
    budget: schemas.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    existing_budget = db.query(models.Budget).filter(
        models.Budget.user_id == current_user.id,
        models.Budget.category == budget.category,
        models.Budget.month == budget.month
    ).first()

    if existing_budget:

        existing_budget.amount = budget.amount
        db.commit()
        db.refresh(existing_budget)

        return existing_budget

    new_budget = models.Budget(
        category=budget.category,
        amount=budget.amount,
        month=budget.month,
        user_id=current_user.id
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget


# =========================
# BUDGET SUMMARY
# =========================

@router.get("/budgets/summary")
def budget_summary(
    month: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    budgets = db.query(models.Budget).filter(
        models.Budget.user_id == current_user.id,
        models.Budget.month == month
    ).all()

    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id
    ).all()

    result = {}

    for budget in budgets:

        spent = 0

        for txn in transactions:

            txn_month = txn.created_at.strftime("%Y-%m")

            if (
                txn_month == month
                and txn.category == budget.category
                and txn.transaction_type == "expense"
            ):
                spent += txn.amount

        result[budget.category] = {
            "budget": budget.amount,
            "spent": spent,
            "remaining": budget.amount - spent
        }

    return result