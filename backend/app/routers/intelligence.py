from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict
from datetime import datetime

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


@router.get("/subscriptions")
def detect_recurring_expenses(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    transactions = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.transaction_type == "expense"
    ).all()

    groups = defaultdict(list)

    for txn in transactions:
        key = (txn.description.lower(), txn.amount)
        groups[key].append(txn.created_at)

    recurring = []

    for (description, amount), dates in groups.items():

        if len(dates) < 3:
            continue

        dates.sort()

        gaps = []

        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            gaps.append(gap)

        avg_gap = sum(gaps) / len(gaps)

        if 25 <= avg_gap <= 35:

            recurring.append({
                "description": description,
                "amount": amount,
                "frequency": "monthly"
            })

    return recurring