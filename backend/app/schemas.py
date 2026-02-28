from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum

# =========================
# ALLOWED CATEGORIES ENUM
# =========================

class AllowedCategory(str, Enum):
    Food = "Food"
    Transport = "Transport"
    Shopping = "Shopping"
    Healthcare = "Healthcare"
    Utilities = "Utilities"
    Entertainment = "Entertainment"
    Income = "Income"
    Transfers = "Transfers"


# =========================
# USER SCHEMAS
# =========================

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


# =========================
# TRANSACTION SCHEMAS
# =========================

class TransactionCreate(BaseModel):
    amount: float
    category: AllowedCategory
    description: Optional[str] = None
    transaction_type: str  # income or expense


class TransactionResponse(BaseModel):
    id: int
    amount: float
    category: AllowedCategory
    description: Optional[str]
    transaction_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# CATEGORY CORRECTION SCHEMA
# =========================

class CategoryCorrection(BaseModel):
    category: AllowedCategory