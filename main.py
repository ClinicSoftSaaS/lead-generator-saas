from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import UserDB, LeadDB
from auth import hash_password, verify_password, create_token, decode_token

# ================= CREATE TABLES =================
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ================= CORS (FIXED) =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],   # 🔥 REQUIRED
    allow_headers=["*"],   # 🔥 REQUIRED
)

# ================= SECURITY =================
security = HTTPBearer()

# ================= SCHEMAS =================
class User(BaseModel):
    username: str
    password: str


class Lead(BaseModel):
    name: str
    phone: str
    address: str = ""


# ================= HOME =================
@app.get("/")
def home():
    return {"status": "backend running"}


# ================= AUTH REGISTER =================
@app.post("/auth/register")
def register(user: User, db: Session = Depends(get_db)):

    existing = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = UserDB(
        username=user.username,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "user created"}


# ================= AUTH LOGIN =================
@app.post("/auth/login")
def login(user: User, db: Session = Depends(get_db)):

    db_user = db.query(UserDB).filter(UserDB.username == user.username).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_token(db_user.id)

    return {"access_token": token}


# ================= AUTH MIDDLEWARE =================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials
    user_id = decode_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(UserDB).filter(UserDB.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ================= LEADS GET =================
@app.get("/leads")
def get_leads(
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    leads = db.query(LeadDB).filter(LeadDB.user_id == user.id).all()

    return [
        {
            "id": l.id,
            "name": l.name,
            "phone": l.phone,
            "address": l.address
        }
        for l in leads
    ]


# ================= LEADS CREATE =================
@app.post("/leads")
def create_lead(
    lead: Lead,
    user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    new_lead = LeadDB(
        name=lead.name,
        phone=lead.phone,
        address=lead.address,
        user_id=user.id
    )

    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    return {
        "message": "lead created",
        "lead": {
            "id": new_lead.id,
            "name": new_lead.name,
            "phone": new_lead.phone,
            "address": new_lead.address
        }
    }