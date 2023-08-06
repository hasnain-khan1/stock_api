from sqlalchemy.orm import Session
from db.models import User, Stock, Transaction
from schemas.schema import UserSchema, StockSchema, TransactionSchema
from sqlalchemy.orm.exc import NoResultFound


def create_user(db: Session, user: UserSchema):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_stock(db: Session, stock_id: int):
    return db.query(Stock).filter(Stock.id == stock_id).first()


def get_stock_by_symbol(db: Session, symbol: str):
    return db.query(Stock).filter(Stock.symbol == symbol).first()


def get_all_stocks(db: Session):
    return db.query(Stock).all()


def create_stock(db: Session, stock: StockSchema):
    db_stock = Stock(**stock.model_dump())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock


def create_transaction(db: Session, transaction: TransactionSchema):
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def get_transaction(db: Session, user_id: int):
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()


def get_transaction_timestamp(db: Session, user_id: int, start_timestamp, end_timestamp):
    try:
        return db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.timestamp >= start_timestamp,
            Transaction.timestamp <= end_timestamp
        ).all()
    except NoResultFound:
        return


def create_or_update_stock(db: Session, stock):
    existing_stock = get_stock_by_symbol(db, stock.symbol)
    if existing_stock:
        existing_stock.current_price = stock.current_price
        db.merge(existing_stock)
        db.commit()
        return existing_stock
    else:
        new_stack = create_stock(db, stock)
        return new_stack
