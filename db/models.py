from db.db_configuration import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    balance = Column(Float)
    hashed_password = Column(String)
    transactions = relationship("Transaction", back_populates="user")
    stock_quantity = relationship("UserStock", back_populates="user")

    class Config:
        orm_mode = True


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String, unique=True, index=True)
    company_name = Column(String)
    current_price = Column(Float, default=0.0)
    transactions = relationship("Transaction", back_populates="stock")
    stock_quantity = relationship("UserStock", back_populates="stock")

    class Config:
        orm_mode = True


class UserStock(Base):
    __tablename__ = "user_stock"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    volume = Column(Float)
    user = relationship("User", back_populates="stock_quantity")
    stock = relationship("Stock", back_populates="stock_quantity")

    class Config:
        orm_mode = True


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    quantity = Column(Integer)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    transaction_type = Column(String)

    user = relationship("User", back_populates="transactions")
    stock = relationship("Stock", back_populates="transactions")

    class Config:
        orm_mode = True
