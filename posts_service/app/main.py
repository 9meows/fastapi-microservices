import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import posts
from app.core.database import create_db_and_tables
from app.core.rabbitmq import category_validator_instance

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается.")
    await create_db_and_tables()
    await category_validator_instance.connect()
    print("БД инициализирована. Подключились к RabbitMQ.")
    yield
    print("Приложение завершает работу.")
    await category_validator_instance.close()


app = FastAPI(
    title="Сервис для постов",
    lifespan=lifespan
)

app.include_router(posts.router)


@app.get("/")
async def root():
    return {"message": "Hello Post Service"}
