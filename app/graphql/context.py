from typing import Any
from fastapi import Request
from app.db.session import SessionLocal
from app.core.jwt import decode_token
from app.models.user import User

async def get_context_value(request: Request, data: Any) -> dict:
    db = SessionLocal()
    user = None
    # Пытаемся достать заголовок разными способами
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    
    if auth and auth.startswith("Bearer "):
        token = auth.removeprefix("Bearer ").strip()
        try:
            payload = decode_token(token)
            if payload.get("typ") == "access":
                user = db.query(User).filter(User.email == payload.get("sub")).first()
                if user is not None and not user.is_active:
                    user = None
        except ValueError:
            user = None
            
    return {"request": request, "db": db, "user": user}