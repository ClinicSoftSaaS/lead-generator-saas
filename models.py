from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


# ================= USER =================
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

    # relationships
    leads = relationship("LeadDB", back_populates="owner", cascade="all, delete")
    subscriptions = relationship("SubscriptionDB", back_populates="user", cascade="all, delete")


# ================= LEAD =================
class LeadDB(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(String(255), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("UserDB", back_populates="leads")


# ================= SUBSCRIPTION =================
class SubscriptionDB(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    plan = Column(String(50), nullable=True)
    status = Column(String(50), default="pending")
    transaction_id = Column(String(100), nullable=True)

    # relationship back to user
    user = relationship("UserDB", back_populates="subscriptions")