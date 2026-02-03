# backend/test_db_simple.py
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Ambil DATABASE_URL
db_url = os.getenv("DATABASE_URL")
print(f"🔗 DATABASE_URL: {db_url}")

# Test koneksi
try:
    engine = create_engine(db_url)
    connection = engine.connect()
    print("✅ Koneksi ke database BERHASIL!")
    print(f"📊 Database: {db_url.split('/')[-1]}")
    connection.close()
except Exception as e:
    print(f"❌ Koneksi GAGAL: {e}")