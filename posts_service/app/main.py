from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import posts
from app.core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается.")
    await create_db_and_tables()
    print("БД инициализирована.")
    yield
    print("Приложение завершает работу.")


app = FastAPI(
    title="Сервис для постов",
    lifespan=lifespan
)

app.include_router(posts.router)


@app.get("/")
async def root():
    return {"message": "Hello Post Service"}
