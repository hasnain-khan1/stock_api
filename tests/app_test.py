import unittest
from fastapi.testclient import TestClient
from main import app, cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///./test.db"

# Create a test database engine
test_engine = create_engine(TEST_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


class TestFastAPIApp(unittest.TestCase):
    def setUp(self):
        # Create all tables in the test database
        test_engine.echo = True  # Optional, for debugging purposes
        Base.metadata.create_all(bind=test_engine)
        self.client = TestClient(app)

    def tearDown(self):
        # Clear the cache and remove all data from tables after each test
        cache.clear()
        with SessionLocal() as db:
            db.execute("DELETE FROM users")
            db.execute("DELETE FROM stocks")
            db.execute("DELETE FROM transactions")

    def test_user_signup_success(self):
        user_data = {"username": "test_user", "password": "password123"}
        response = self.client.post("/users/", json=user_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], user_data["username"])

    def test_user_signup_username_conflict(self):
        user_data = {"username": "existing_user", "password": "password456"}
        # Manually add an existing user to the test database to simulate a conflict
        with SessionLocal() as db:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                       {"username": "existing_user", "password": "password789"})
        response = self.client.post("/users/", json=user_data)
        self.assertEqual(response.status_code, 409)

    def test_user_details_success(self):
        # Manually add a user to the test database to retrieve their details
        with SessionLocal() as db:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                       {"username": "user123", "password": "pass123"})
        response = self.client.get("/users/user123/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "user123")

    def test_user_details_not_found(self):
        response = self.client.get("/users/non_existent_user/")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
