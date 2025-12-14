# crud.py
from sqlalchemy.orm import Session
from models import User, Note
from schemas import UserCreate, NoteCreate, NoteUpdate
from auth import get_password_hash 

def create_user(db: Session, user: UserCreate):
    hashed_pw = get_password_hash(user.password)  # ← 来自 auth.py
    db_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# --- Note CRUD ---
def create_note(db: Session, note: NoteCreate, owner_id: int):
    db_note = Note(**note.model_dump(), owner_id=owner_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_notes_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(Note).filter(Note.owner_id == owner_id).offset(skip).limit(limit).all()

def get_note_by_id_and_owner(db: Session, note_id: int, owner_id: int):
    return db.query(Note).filter(Note.id == note_id, Note.owner_id == owner_id).first()

def update_note(db: Session, note_id: int, note_update: NoteUpdate, owner_id: int):
    db_note = get_note_by_id_and_owner(db, note_id, owner_id)
    if not db_note:
        return None
    update_data = note_update.model_dump(exclude_unset=True)  # ← 只更新非 None 字段
    for key, value in update_data.items():
        setattr(db_note, key, value)
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int, owner_id: int):
    db_note = get_note_by_id_and_owner(db, note_id, owner_id)
    if db_note:
        db.delete(db_note)
        db.commit()
        return True
    return False

def search_notes_by_title(db: Session, owner_id: int, keyword: str):
    # 安全：用 SQLAlchemy 的 bindparam 防 SQL 注入
    return db.query(Note).filter(
        Note.owner_id == owner_id,
        Note.title.ilike(f"%{keyword}%")  # ← 不区分大小写模糊搜索
    ).all()