import json

from celery import Celery
from fastapi import HTTPException, Depends, FastAPI
from sqlalchemy.orm import Session
from operations.stock_tasks import create_user, get_user_by_username, get_stock_by_symbol, get_all_stocks
from operations import stock_tasks
from db.db_configuration import SessionLocal, Base, engine
from schemas.schema import UserSchema, StockSchema, TransactionSchema, TransactionTimeStampSchema
import uvicorn
import redis
from fastapi.encoders import jsonable_encoder
from pydantic import parse_obj_as
from typing import List

from cachetools import TTLCache

app = FastAPI()
Base.metadata.create_all(bind=engine)

celery_app = Celery('tasks',
                    broker='redis://redis:6379/0',
                    backend='rpc://')

redis_client = redis.StrictRedis(host='redis', port=6379, db=0)
print(redis_client)
# Cache setup with a TTL (Time to Live) of 300 seconds (5 minutes)
cache = TTLCache(maxsize=100, ttl=300)


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@app.post("/users/", response_model=UserSchema)
def user_signup(user: UserSchema, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=409, detail="Username already registered")
    return create_user(db, user)


@app.get("/users/{user_name}/", response_model=UserSchema)
def user_details(username: str, db: Session = Depends(get_db)):
    cached_user = redis_client.get(f"user_{username}")
    if cached_user:
        return UserSchema.model_validate(json.loads(cached_user))
    db_user = get_user_by_username(db, username)
    if not db_user:
        raise HTTPException(status_code=404, detail="Username not registered")
    redis_client.set(f"user_{username}", json.dumps(jsonable_encoder(db_user)))
    return db_user


@app.post("/stocks/", response_model=StockSchema)
def create_stock(stock: StockSchema, db: Session = Depends(get_db)):
    db_stock = stock_tasks.create_or_update_stock(db, stock)
    return db_stock


@app.get("/stocks/", response_model=list[StockSchema])
def get_stock(db: Session = Depends(get_db)):
    cached_user = redis_client.get("all_stocks")
    if cached_user:
        data = json.loads(cached_user)
        return parse_obj_as(List[StockSchema], data)

    db_stock = get_all_stocks(db)
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock is Empty")
    redis_client.set("all_stocks", json.dumps(jsonable_encoder(db_stock)))
    return db_stock


@app.get("/stocks/{ticker}/", response_model=StockSchema)
def get_stock_ticker(ticker: str, db: Session = Depends(get_db)):
    cached_user = redis_client.get(f"symbol_{ticker}")
    if cached_user:
        data = json.loads(cached_user)
        return StockSchema.model_validate(data)
    db_stock = get_stock_by_symbol(db, ticker)
    if not db_stock:
        raise HTTPException(status_code=404, detail="No stock Found")
    redis_client.set(f"symbol_{ticker}", json.dumps(jsonable_encoder(db_stock)))

    return db_stock


@app.post("/transactions/", response_model=dict)
def create_transaction(transaction: TransactionSchema, db: Session = Depends(get_db)):
    data = jsonable_encoder(transaction)
    celery_enqueue = celery_app.send_task('tasks.create_or_update_stock', args=[data])
    transaction_response = {"message": f"request queued {celery_enqueue.id}"}
    return transaction_response


@app.get("/transaction/{user_id}/", response_model=list[TransactionSchema])
def get_user_transaction(user_id: int, db: Session = Depends(get_db)):
    cached_user = redis_client.get(f"transaction_{str(user_id)}")
    if cached_user:
        data = json.loads(cached_user)
        return parse_obj_as(List[TransactionSchema], data)

    db_stock = stock_tasks.get_transaction(db, user_id)
    if not db_stock:
        raise HTTPException(status_code=404, detail="No Transaction Found")
    redis_client.set(f"transaction_{str(user_id)}", json.dumps(jsonable_encoder(db_stock)))
    return db_stock


@app.get("/transaction/{start_timestamp}/{end_timestamp}/", response_model=list[TransactionTimeStampSchema])
def get_user_transaction_time(user_id: int, start_timestamp, end_timestamp, db: Session = Depends(get_db)):
    db_stock = stock_tasks.get_transaction_timestamp(db, user_id, start_timestamp, end_timestamp)
    if not db_stock:
        raise HTTPException(status_code=404, detail="No Transaction Found")
    return db_stock


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
