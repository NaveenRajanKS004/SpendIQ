from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict

from ..database import SessionLocal
from .. import models
from ..security import get_current_user


# This router handles intelligent insights:
# - detecting recurring expenses (subscriptions)
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
# DETECT RECURRING EXPENSES
# =========================

@router.get("/subscriptions")
def detect_recurring_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    # Fetch all expense transactions for the user
    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.transaction_type == "expense"
    ).all()

    # Group transactions by (description, amount)
    # Assumption: recurring payments usually have same description + amount
    groups = defaultdict(list)

    for txn in transactions:
        key = (txn.description.lower(), txn.amount)
        groups[key].append(txn.created_at)

    recurring = []

    # Analyze each group to detect recurring patterns
    for (description, amount), dates in groups.items():

        # Require at least 3 occurrences to consider it recurring
        if len(dates) < 3:
            continue

        # Sort transaction dates chronologically
        dates.sort()

        gaps = []

        # Calculate day gaps between consecutive transactions
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i - 1]).days
            gaps.append(gap)

        # Compute average gap between transactions
        avg_gap = sum(gaps) / len(gaps)

        # Heuristic:
        # If average gap is roughly 1 month → treat as subscription
        if 25 <= avg_gap <= 35:

            recurring.append({
                "description": description,
                "amount": amount,
                "frequency": "monthly"
            })

    return recurring