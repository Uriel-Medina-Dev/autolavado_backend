from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
import config.db
import models.model_user as model_user
import schemas.schema_user as schema_user
import crud.crud_user as crud
from routes.routes_auth import get_current_user
from core.security import decode_token
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])
security = HTTPBearer()


def get_db():
    db = config.db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[schema_user.Usuario])
def read_users(skip: int = 0, limit: int = 100, current_user: model_user.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_users(db=db, skip=skip, limit=limit)


@router.get("/{user_id}")
def read_user(user_id: int, current_user: model_user.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", status_code=201)
def create_user(user: schema_user.UsuarioCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@router.put("/{user_id}")
def update_user(user_id: int, user: schema_user.UsuarioUpdate, current_user: model_user.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = crud.update_user(db=db, user_id=user_id, user=user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, current_user: model_user.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = crud.delete_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}
