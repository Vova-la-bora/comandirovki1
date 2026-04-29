# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base, SessionLocal
from app.middleware.user_context import UserContextMiddleware

# ВАЖНО: импортируем observers ПОСЛЕ создания engine
from app.api import auth, changelog, users, roles, permissions

# Создаём таблицы
Base.metadata.create_all(bind=engine)

# Импортируем observers (они регистрируют события)
import app.observers.sqlalchemy_events

# Импортируем сиды ПОСЛЕ observers
from app.seeders.database_seeder import run_seeds

# Запускаем сиды
with SessionLocal() as db:
    run_seeds(db)

app = FastAPI(title="Audit System API", version="1.0.0")

app.add_middleware(UserContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(changelog.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(permissions.router)

@app.get("/")
def root():
    return {"message": "Audit System API", "version": "1.0.0"}