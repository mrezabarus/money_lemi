from sqlalchemy import text
from .database import engine

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connected")
            print(f"Result: {result.fetchone()}")
    except Exception as e:
        print(f" Failed Connection Database: {e}")

if __name__ == "__main__":
    test_connection()