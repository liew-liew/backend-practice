# main.py
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI


app = FastAPI(title="Note API", description="带权限的笔记后端")

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.openapi.utils import get_openapi 
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base
from schemas import UserCreate, UserOut, Token, NoteCreate, NoteOut, NoteUpdate
from auth import create_access_token, get_current_user, verify_password
from crud import create_user, get_user_by_email, create_note, get_notes_by_owner, \
                 get_note_by_id_and_owner, update_note, delete_note, search_notes_by_title

# 创建表（开发用；生产用 Alembic）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Note API", description="带权限的笔记后端")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Note API",
        version="1.0.0",
        routes=app.routes,
    )
    # ✅ 添加 Bearer Token 安全方案
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

# ─────────────── Auth Endpoints ───────────────
@app.post("/auth/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)

@app.post("/auth/token", response_model=Token)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# ─────────────── Note Endpoints (需登录) ───────────────
@app.post("/notes/", response_model=NoteOut)
def create_new_note(
    note: NoteCreate,
    current_user: UserOut = Depends(get_current_user),  # ← 关键：自动校验 token
    db: Session = Depends(get_db)
):
    return create_note(db, note, owner_id=current_user.id)

@app.get("/notes/", response_model=list[NoteOut])
def read_notes(
    skip: int = 0, limit: int = 100,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_notes_by_owner(db, current_user.id, skip, limit)

@app.get("/notes/search", response_model=list[NoteOut])
def search_notes(
    keyword: str = Query(..., min_length=1, max_length=50),
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return search_notes_by_title(db, current_user.id, keyword)

@app.get("/notes/{note_id}", response_model=NoteOut)
def read_note(
    note_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = get_note_by_id_and_owner(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or not owned by you")
    return note

@app.put("/notes/{note_id}", response_model=NoteOut)
def update_existing_note(
    note_id: int,
    note_update: NoteUpdate,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = update_note(db, note_id, note_update, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or not owned by you")
    return note

@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_note(
    note_id: int,
    current_user: UserOut = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not delete_note(db, note_id, current_user.id):
        raise HTTPException(status_code=404, detail="Note not found or not owned by you")