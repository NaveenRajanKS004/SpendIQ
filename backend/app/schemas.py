# =========================
# IMPORTS
# =========================

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


# =========================
# ENUMS
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

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

# =========================
# USER SCHEMAS
# =========================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    date_of_birth: Optional[str]
    profile_picture: Optional[str]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


# =========================
# TRANSACTION SCHEMAS
# =========================

class TransactionCreate(BaseModel):
    amount: float
    category: AllowedCategory
    description: Optional[str] = None
    transaction_type: TransactionType


class TransactionResponse(BaseModel):
    id: int
    amount: float
    category: AllowedCategory
    description: Optional[str]
    transaction_type: TransactionType
    created_at: datetime

    class Config:
        from_attributes = True


# =========================
# CATEGORY CORRECTION
# =========================

class CategoryCorrection(BaseModel):
    category: AllowedCategory


# =========================
# BUDGET SCHEMAS
# =========================

class BudgetCreate(BaseModel):
    category: str
    amount: float
    month: str  # format: YYYY-MM


class BudgetResponse(BaseModel):
    id: int
    category: str
    amount: float
    month: str

    class Config:
        from_attributes = True