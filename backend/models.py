from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from database import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Float)
    shipping_fee = Column(Float, default=0.0)
    mall = Column(String)  # e.g., 11st, Gmarket
    source = Column(String) # e.g., fmkorea, algumon
    url = Column(String)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    is_ended = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DealAlert(Base):
    __tablename__ = "deal_alerts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    keyword = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
