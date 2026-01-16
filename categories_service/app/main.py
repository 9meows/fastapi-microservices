import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.api.routers import categories
from app.core.database import create_db_and_tables
from app.core.rabbitmq_worker import run_consumer
from app.core.logging import get_logger

logger = get_logger("categories_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info({"event": "service_startup"})
    # Запускаем consumer как фоновую задачу
    consumer_task = asyncio.create_task(run_consumer())
    await create_db_and_tables()
    logger.info({"event": "service_ready"})
    yield
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        logger.info({"event": "rabbitmq_consumer_stopped"})

app = FastAPI(
    title="Сервис для категорий",
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info({
        "event": "request_started",
        "method": request.method,
        "path": str(request.url.path),
        "client_ip": request.client.host if request.client else None
    })
    
    response = await call_next(request)
    
    process_time_ms = (time.time() - start_time) * 1000
    
    log_data = {
        "event": "request_completed",
        "method": request.method,
        "path": str(request.url.path),
        "status_code": response.status_code,
        "duration_ms": round(process_time_ms, 2)
    }
    
    if response.status_code >= 500:
        logger.error(log_data)
    elif response.status_code >= 400:
        logger.warning(log_data)
    else:
        logger.info(log_data)
    
    return response



app.include_router(categories.router)


@app.get("/health")
async def health_check():
    """Healthcheck"""
    return {"status": "healthy", "service": "categories_service"}
