from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.auth.router import router as auth_router
from app.graphql.schema import graphql_app

app = FastAPI(title=settings.app_name)
app.include_router(auth_router)
app.mount("/graphql", graphql_app)
app.mount("/admin", StaticFiles(directory="app/static", html=True), name="admin")