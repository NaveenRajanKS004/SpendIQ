from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # One user -> Many transactions
    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    transaction_type = Column(String, nullable=False)  # income or expense

    # More robust timestamp handling
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Many transactions -> One user
    user = relationship("User", back_populates="transactions")
