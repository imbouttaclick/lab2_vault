from uuid import uuid4
from ariadne import QueryType, MutationType, convert_kwargs_to_snake_case
from fastapi import HTTPException
from sqlalchemy import or_

from app.models.user import User
from app.models.oauth_client import OAuthClient
from app.models.audit_event import AuditEvent
from app.core.passwords import hash_password, validate_policy, WeakPasswordError
from app.core.jwt import create_access_token
from app.audit.service import write_event

query = QueryType()
mutation = MutationType()


def _serialize_dt(dt) -> str:
    return dt.isoformat() if dt else None


# ---------- Query ----------

@query.field("me")
def resolve_me(_, info):
    return info.context["user"]


@query.field("users")
@convert_kwargs_to_snake_case
def resolve_users(_, info, search=None, limit=50, offset=0):
    db = info.context["db"]
    q = db.query(User)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(User.email.ilike(like)))
    return q.offset(offset).limit(limit).all()


@query.field("clients")
def resolve_clients(_, info):
    db = info.context["db"]
    return db.query(OAuthClient).all()


@query.field("auditEvents")
@convert_kwargs_to_snake_case
def resolve_audit_events(_, info, event_type=None, limit=50, offset=0):
    db = info.context["db"]
    q = db.query(AuditEvent)
    if event_type:
        q = q.filter(AuditEvent.event_type == event_type)
    return q.order_by(AuditEvent.created_at.desc()).offset(offset).limit(limit).all()

# ---------- Mutation ----------

@mutation.field("registerUser")
@convert_kwargs_to_snake_case
def resolve_register_user(_, info, email, password):
    db = info.context["db"]
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        validate_policy(password, user_inputs=[email])
    except WeakPasswordError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    request = info.context["request"]
    write_event(
        db,
        "user.created",
        actor_id=user.id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    token = create_access_token(sub=user.email)
    return {"accessToken": token, "tokenType": "bearer"}


@mutation.field("createClient")
@convert_kwargs_to_snake_case
def resolve_create_client(_, info, name, is_confidential=True):
    db = info.context["db"]
    client = OAuthClient(
        client_id=str(uuid4()),
        name=name,
        is_confidential=is_confidential,
        redirect_uris=[],
    )
    db.add(client)
    db.commit()
    db.refresh(client)

    user = info.context["user"]
    request = info.context["request"]
    write_event(
        db,
        "client.created",
        actor_id=user.id if user else None,
        client_id=client.client_id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return client


@mutation.field("disableUser")
@convert_kwargs_to_snake_case
def resolve_disable_user(_, info, user_id):
    db = info.context["db"]
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)

    actor = info.context["user"]
    request = info.context["request"]
    write_event(
        db,
        "user.disabled",
        actor_id=actor.id if actor else None,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return user

from ariadne import ObjectType

user_type = ObjectType("User")
client_type = ObjectType("Client")
audit_type = ObjectType("AuditEvent")


@user_type.field("createdAt")
def _user_created_at(user, _info):
    return _serialize_dt(user.created_at)


@client_type.field("redirectUris")
def _client_redirect_uris(client, _info):
    return client.redirect_uris or []


@client_type.field("createdAt")
def _client_created_at(client, _info):
    return _serialize_dt(client.created_at)


@audit_type.field("metadata")
def _audit_metadata(event, _info):
    import json
    return json.dumps(event.metadata_json, ensure_ascii=False) if event.metadata_json else None


@audit_type.field("createdAt")
def _audit_created_at(event, _info):
    return _serialize_dt(event.created_at)


@user_type.field("isAdmin")
def _user_is_admin(user, _info):
    return bool(user.is_admin)


@user_type.field("isActive")
def _user_is_active(user, _info):
    return bool(user.is_active)


@client_type.field("clientId")
def _client_id(client, _info):
    return client.client_id

bindables = [query, mutation, user_type, client_type, audit_type]