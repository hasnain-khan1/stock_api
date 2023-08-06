import json

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app, get_db, StockSchema, stock_tasks, redis_client
from db.db_configuration import Base
from schemas.schema import TransactionSchema

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db():
    # Set up the database and create the tables
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    # Tear down the database after testing
    Base.metadata.drop_all(bind=engine)


def test_create_stock(db):
    client = TestClient(app)

    # Define test data
    test_stock_data = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "price": 150.00,
    }

    # Send a POST request to create a stock
    response = client.post("/stocks/", json=test_stock_data)

    # Assert that the request was successful (HTTP status code 200)
    assert response.status_code == 200

    # Assert the response data matches the input data
    assert response.json() == test_stock_data

    # Check if the stock was correctly inserted into the database
    created_stock = db.query(stock_tasks.Stock).filter_by(symbol="AAPL").first()
    assert created_stock is not None
    assert created_stock.symbol == "AAPL"
    assert created_stock.name == "Apple Inc."
    assert created_stock.price == 150.00


def test_get_stock_empty_db(client):
    response = client.get("/stocks/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Stock is Empty"}


def test_get_stock_cached_data(client, db, monkeypatch):
    test_stocks = [StockSchema(name="Stock1", symbol="AAPL", company_name="AAPL", current_price=150),
                   StockSchema(name="Stock2", company_name="AAPL", current_price=150)]
    monkeypatch.setattr("app.get_all_stocks", lambda db: test_stocks)
    monkeypatch.setattr("app.redis_client.get", lambda key: json.dumps(jsonable_encoder(test_stocks)))

    response = client.get("/stocks/")
    assert response.status_code == 200
    assert response.json() == [{"name": "Stock1"}, {"name": "Stock2"}]


def test_get_stock_ticker_not_found(client):
    response = client.get("/stocks/invalid_ticker/")
    assert response.status_code == 404
    assert response.json() == {"detail": "No stock Found"}


def test_get_user_transaction_not_found(client):
    response = client.get("/transaction/123456/")
    assert response.status_code == 404
    assert response.json() == {"detail": "No Transaction Found"}


def test_get_user_transaction_cached_data(client, db, monkeypatch):
    test_transactions = [
        TransactionSchema(id=1, user_id=123456, amount=100),
        TransactionSchema(id=2, user_id=123456, amount=200)
    ]
    monkeypatch.setattr("app.stock_tasks.get_transaction", lambda db, user_id: None)
    monkeypatch.setattr("app.redis_client.get", lambda key: json.dumps(jsonable_encoder(test_transactions)))

    response = client.get("/transaction/123456/")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "user_id": 123456, "amount": 100},
        {"id": 2, "user_id": 123456, "amount": 200}
    ]


def test_get_user_transaction_db_data(client, db, monkeypatch):
    test_transactions = [
        TransactionSchema(id=1, user_id=123456, amount=100),
        TransactionSchema(id=2, user_id=123456, amount=200)
    ]
    monkeypatch.setattr("app.stock_tasks.get_transaction", lambda db, user_id: test_transactions)
    monkeypatch.setattr("app.redis_client.get", lambda key: None)

    response = client.get("/transaction/123456/")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "user_id": 123456, "amount": 100},
        {"id": 2, "user_id": 123456, "amount": 200}
    ]

    # Check if the data was cached in redis
    cached_data = redis_client.get("transaction_123456")
    assert cached_data is not None
    assert json.loads(cached_data) == jsonable_encoder(test_transactions)
