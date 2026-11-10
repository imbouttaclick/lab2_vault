from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.auth.schemas import Credentials, TokenResponse, MeResponse
from app.core.passwords import hash_password, verify_password, validate_policy, WeakPasswordError
from app.core.jwt import create_access_token
from app.core.deps import get_current_user
from app.models.user import User
from app.audit.service import write_event

router = APIRouter(prefix="/auth", tags=["auth"])

def _client_meta(request: Request) -> dict:
    return {
        "ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }

@router.post("/register", response_model=TokenResponse)
def register(payload: Credentials, request: Request, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        validate_policy(payload.password, user_inputs=[payload.email])
    except WeakPasswordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    meta = _client_meta(request)
    write_event(db, "user.created", actor_id=user.id, **meta)
    token = create_access_token(sub=user.email)
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
def login(payload: Credentials, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    meta = _client_meta(request)
    if user is None or not verify_password(payload.password, user.hashed_password):
        write_event(db, "user.login.failure", actor_id=user.id if user else None,
                    metadata={"email": payload.email}, **meta)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        write_event(db, "user.login.failure", actor_id=user.id,
                    metadata={"email": payload.email, "reason": "inactive"}, **meta)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    write_event(db, "user.login.success", actor_id=user.id, **meta)
    token = create_access_token(sub=user.email)
    return TokenResponse(access_token=token)

@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)):
    return MeResponse(id=user.id, email=user.email, is_admin=user.is_admin)