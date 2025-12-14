# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 👇 正确：用 DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # 🚨 本地开发 fallback（安全！）
    DATABASE_URL = "postgresql://postgres:yourpassword@localhost/note_db"

engine = create_engine(DATABASE_URL)  # ✅ 用 DATABASE_URL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()