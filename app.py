from fastapi import HTTPException, Depends, FastAPI
from sqlalchemy.orm import Session
from operations.stock_tasks import create_user, get_user_by_username, create_stock, create_transaction, \
    get_stock_by_symbol, get_all_stocks
from operations import stock_tasks
from db.db_configuration import SessionLocal, Base, engine
from schemas.schema import UserSchema, StockSchema, TransactionSchema, TransactionTimeStampSchema
import uvicorn
import redis

# from cachetools import cached, TTLCache


app = FastAPI()
Base.metadata.create_all(bind=engine)


# redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Cache setup with a TTL (Time to Live) of 300 seconds (5 minutes)
# cache = TTLCache(maxsize=100, ttl=300)


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
    db_user = get_user_by_username(db, username)
    if not db_user:
        raise HTTPException(status_code=404, detail="Username not registered")
    return db_user


@app.post("/stocks/", response_model=StockSchema)
def create_stock(stock: StockSchema, db: Session = Depends(get_db)):
    db_stock = stock_tasks.create_or_update_stock(db, stock)
    # if db_stock:
    #     raise HTTPException(status_code=409, detail="Stock symbol already registered")
    return db_stock


@app.get("/stocks/", response_model=list[StockSchema])
def get_stock(db: Session = Depends(get_db)):
    db_stock = get_all_stocks(db)
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock is Empty")
    return db_stock


@app.get("/stocks/{ticker}/", response_model=StockSchema)
def get_stock_ticker(ticker: str, db: Session = Depends(get_db)):
    db_stock = get_stock_by_symbol(db, ticker)
    if not db_stock:
        raise HTTPException(status_code=404, detail="No stock Found")
    return db_stock


@app.post("/transactions/", response_model=TransactionSchema)
def create_transaction_endpoint(transaction: TransactionSchema, db: Session = Depends(get_db)):
    return create_transaction(db, transaction)


@app.get("/transaction/{user_id}/", response_model=list[TransactionSchema])
def get_user_transaction(user_id: int, db: Session = Depends(get_db)):
    db_stock = stock_tasks.get_transaction(db, user_id)
    if not db_stock:
        raise HTTPException(status_code=404, detail="No Transaction Found")
    return db_stock


@app.get("/transaction/{start_timestamp}/{end_timestamp}/", response_model=list[TransactionTimeStampSchema])
def get_user_transaction_time(user_id: int, start_timestamp, end_timestamp, db: Session = Depends(get_db)):
    db_stock = stock_tasks.get_transaction_timestamp(db, user_id, start_timestamp, end_timestamp)
    if not db_stock:
        raise HTTPException(status_code=404, detail="No Transaction Found")
    return db_stock


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
