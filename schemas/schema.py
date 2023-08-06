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


class TransactionSchema(BaseModel):
    user_id: int
    quantity: int
    price: float


class TransactionTimeStampSchema(BaseModel):
    user_id: int
    stock_id: int
    quantity: int
    price: float
    timestamp: Optional[datetime]
