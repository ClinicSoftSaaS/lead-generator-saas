from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from database import get_db
from models import UserDB
from auth import decode_token

router = APIRouter()


def get_user(authorization: str, db: Session):
    if not authorization:
        return None

    token = authorization.replace("Bearer ", "")
    user_id = decode_token(token)

    if not user_id:
        return None

    return db.query(UserDB).filter(UserDB.id == user_id).first()


def is_active(user_id: int, db: Session):
    # TEMP: always active (you can improve later)
    return True


@router.post("/subscription/request")
def request_subscription(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_user(authorization, db)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {"status": "subscription requested"}


@router.post("/subscription/approve/{sub_id}")
def approve_subscription(sub_id: int):
    return {"status": f"subscription {sub_id} approved"}


@router.get("/subscription/my")
def my_subscription(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    user = get_user(authorization, db)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {"status": "active"}