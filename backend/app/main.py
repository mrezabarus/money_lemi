# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.config import engine, Base
from app.routes import router as users_router  # ← Import dari routes
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

# Create app
app = FastAPI(
    title="FastAPI User Management",
    description="Clean API with PostgreSQL",
    version="1.0.0",
    debug=True
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!", "status": "success"}

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)