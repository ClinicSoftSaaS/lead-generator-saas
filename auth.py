import os
from jose import jwt, JWTError
from passlib.context import CryptContext

# ✅ Load from environment (Render / production)
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")
ALGORITHM = "HS256"

# Password hashing (safe + compatible)
pwd_context = CryptContext(
    schemes=["sha256_crypt"],
    deprecated="auto"
)


# ================= PASSWORD =================
def hash_password(password: str):
    return pwd_context.hash(str(password))


def verify_password(password: str, hashed: str):
    return pwd_context.verify(str(password), hashed)


# ================= JWT =================
def create_token(user_id: int):
    return jwt.encode(
        {"user_id": user_id},
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload.get("user_id")
    except JWTError:
        return None