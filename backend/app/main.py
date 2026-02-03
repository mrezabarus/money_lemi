from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from typing import Optional
import re

# 🔥 IMPORT ROUTES BARU DI SINI 🔥
from app.routes import router as transaction_router  # Tambahkan ini

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="💰 Transaction Classifier API",
    description="Backend API untuk sistem ERP menggunakan FastAPI",
    version="0.0.1"
)

# CORS Middleware (sudah ada)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 REGISTER ROUTES BARU DI SINI 🔥
app.include_router(transaction_router)  # Tambahkan ini

@app.get("/")
def home():
    return {
        "app": "MonPlan",
        "status": "Running",
        "backend": "FastAPI"
    }

@app.get("/health")
def health_check():
    return {"status":"Healthy", "database": "connected"}