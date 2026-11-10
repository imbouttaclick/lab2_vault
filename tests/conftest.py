import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import app.graphql.context  # <--- Импортируем модуль контекста

from app.main import app as fastapi_app
from app.db.base import Base
from app.db.session import get_db
import app.models

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    # 1. Подменяем get_db для FastAPI (REST)
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    fastapi_app.dependency_overrides[get_db] = override_get_db

    # 2. Подменяем SessionLocal для GraphQL (Ariadne)
    # Чтобы Ariadne использовал тестовую базу данных
    monkeypatch.setattr(app.graphql.context, "SessionLocal", TestingSessionLocal)

    with TestClient(fastapi_app) as c:
        yield c
        
    fastapi_app.dependency_overrides.clear()