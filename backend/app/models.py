# =========================
# IMPORTS
# =========================

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


# =========================
# USER MODEL
# =========================

class User(Base):
    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Info
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)

    # Profile
    profile_picture = Column(String, nullable=True)

    # Auth
    hashed_password = Column(String, nullable=False)

    # Relationships
    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# =========================
# TRANSACTION MODEL
# =========================

class Transaction(Base):
    __tablename__ = "transactions"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Core Fields
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    transaction_type = Column(String, nullable=False)  # income / expense

    # Metadata
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="transactions")


# =========================
# BUDGET MODEL
# =========================

class Budget(Base):
    __tablename__ = "budgets"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Core Fields
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    month = Column(String, nullable=False)  # format: YYYY-MM

    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"))