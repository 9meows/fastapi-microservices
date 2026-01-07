import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import categories
from app.core.database import create_db_and_tables
from app.core.rabbitmq_worker import run_consumer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем consumer как фоновую задачу
    consumer_task = asyncio.create_task(run_consumer())
    await create_db_and_tables()
    print("Инициализация завершена.")
    yield
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        print("Consumer RabbitMQ остановлен.")

app = FastAPI(
    title="Сервис для категорий",
    lifespan=lifespan
)

app.include_router(categories.router)


@app.get("/")
async def root():
    return {"message": "Hello Category Service"}

