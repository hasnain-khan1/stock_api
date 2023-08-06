from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserSchema(BaseModel):
    username: str
    balance: float
    hashed_password: str


class StockSchema(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    high_volume: str
    closing_price: str


class TransactionSchema(BaseModel):
    user_id: int
    ticker: str
    quantity: int
    transaction_type: str


class UserStockData(BaseModel):
    user_id: int
    quantity: float
    stock_id: int


class TransactionTimeStampSchema(BaseModel):
    user_id: int
    stock_id: int
    quantity: int
    price: float
    timestamp: Optional[datetime]
