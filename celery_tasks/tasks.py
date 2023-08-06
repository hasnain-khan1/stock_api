import time
from celery import Celery
from sqlalchemy import and_

from db.db_configuration import SessionLocal
from db.models import User, Stock, Transaction, UserStock

app = Celery('tasks',
             broker='redis://redis:6379/0',
             backend='rpc://')


@app.task(default_retry_delay=10)
def create_or_update_stock(stock):
    """
    Stock data will be processed through celery.
    :param stock:
    :return:
    """
    print(f'Got Request - {stock}')
    volume = stock["quantity"]
    symbol = stock["ticker"]
    user_id = stock["user_id"]
    transaction_type = stock["transaction_type"]

    session = SessionLocal()
    # Check if a record with the given name already exists
    user_record = session.query(User).filter_by(user_id=user_id).first()
    if user_record:
        balance = user_record.balance
        ticker_object = session.query(Stock).filter_by(Stock.symbol == symbol).first()

        if transaction_type == "buy":
            """
            If user wants to buy the stock for specific price for example if user wants to 
            buy the twitter stock for 50$ then check the balance in wallet.
            if required balance is available then the stock will added to user history and balance
            will be deducted.
            """
            if int(balance) == 0 or balance < volume:
                session.close()
                return "Not enough Balance "
            if ticker_object:
                ticker_price = ticker_object.current_price
                purchase_volume = volume / ticker_price
                balance = balance - volume
                user_record.balance = balance
                session.merge(user_record)
                new_transaction = Transaction(user_id=user_id, stock_id=ticker_object.id,
                                              transaction_type="buy", quantity=purchase_volume,
                                              price=ticker_price)
                session.add(new_transaction)
                update_or_create_stock(session, user_id=user_id, stock_id=ticker_object.id,
                                       volume=purchase_volume)
        if transaction_type == "sell":
            """
            if user wants to sell the stock For example if user have 5.2 twitter stocks and hw wants to 
            sell 4 stocks then the order will be processed and balance will be increased. if volume is greater 
            than the stocks then nothing will happen.
            """
            user_stock = session.query(UserStock).filter(
                and_(UserStock.user_id == user_id,
                     UserStock.stock_id == ticker_object.id)).first()
            if user_stock:
                ticker_volume = user_stock.volume
                if volume > ticker_volume:
                    session.close()
                    return "Not enough Volume"
                ticker_price = ticker_object.current_price
                user_record.balance = ticker_price * volume
                user_stock.volume = user_stock.volume - volume
                session.merge(user_record)
                session.merge(user_stock)

    session.commit()
    session.close()
    print("this is stock:", stock)
    time.sleep(4)

    print('Work Finished ')


def update_or_create_stock(session, user_id, stock_id, volume):
    """
    if users have buyed the stock then it will go to its stock data along with stock information
    :param session: Database Session
    :param user_id:
    :param stock_id: ID of stock purchased by User
    :param volume: Total Volume of stock purchased by user
    :return:
    """
    query_result = session.query(UserStock).filter(
        and_(UserStock.user_id == user_id, UserStock.stock_id == stock_id)).first()
    if query_result:
        query_result.volume = query_result.volume + volume
        session.merge(query_result)
        session.commit()

    else:
        new_user_stock = UserStock(user_id=user_id, stock_id=stock_id, volume=volume)
        session.add(new_user_stock)
        session.commit()
        return
