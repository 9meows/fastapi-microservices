import os
import httpx
import time
import redis.asyncio as redis

from fastapi import FastAPI, Request, Response, Depends
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from app.core.logging import get_logger


logger = get_logger("api_gateway")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info({"event": "gateway_startup"})
    app.state.redis = redis.from_url("redis://redis:6379", encoding = "utf-8", decode_responses = True)
    await FastAPILimiter.init(app.state.redis)
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    logger.info({"event": "gateway_ready"})
    try:
        yield
    finally:
        logger.info({"event": "gateway_shutdown"})
        await app.state.redis.close()
        await app.state.http_client.aclose()

app = FastAPI(title="API Gateway", lifespan=lifespan)

POSTS_SERVICE_URL = os.getenv("POSTS_SERVICE_URL")
CATEGORIES_SERVICE_URL = os.getenv("CATEGORIES_SERVICE_URL")

@app.middleware("http")
async def log_gateway_requests(request: Request, call_next):
    """Middleware для логирования через Gateway"""
    start_time = time.time()
    
    logger.info({
        "event": "gateway_request_received",
        "method": request.method,
        "path": str(request.url.path),
        "client_ip": request.client.host if request.client else None
    })
    
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    
    log_data = {
        "event": "gateway_request_completed",
        "method": request.method,
        "path": str(request.url.path),
        "status_code": response.status_code,
        "duration_ms": round(duration_ms, 2)
    }
    
    if response.status_code >= 500:
        logger.error(log_data)
    elif response.status_code >= 400:
        logger.warning(log_data)
    else:
        logger.info(log_data)
    
    response.headers["X-RateLimit-Limit"] = "100"
    
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api_gateway"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
               dependencies=[Depends(RateLimiter(times=100, minutes=5))])
async def proxy_request(request: Request, path: str):
    """Функция определяет, какому сервису перенаправить запрос, основываясь на начальной части URL пути."""
    target_url = None
    target_service = None
    
    if path.startswith("posts"):
        target_url = f"{POSTS_SERVICE_URL}/{path}"
        target_service = "posts_service"
    elif path.startswith("categories"):
        target_service = "categories_service"
        target_url = f"{CATEGORIES_SERVICE_URL}/{path}"

    if not target_url:
        logger.warning({"event": "proxy_route_not_found", "path": path})
        return Response(content="Not Found", status_code=404)

    logger.info({"event": "proxy_forwarding", "target_service": target_service,
                 "target_url": target_url, "method": request.method})

    # тело запроса
    body = await request.body()
    
    headers = {key: value for key, value in request.headers.items()
               if key.lower() not in ['host', 'content-length']}
    
    
    # Формируем запрос к целевому сервису
    proxied_req = app.state.http_client.build_request(
        method=request.method,
        url=target_url,
        headers=headers,
        params=request.query_params,
        content=body
    )
    
    start_time = time.time()    
    try:
        # Отправляем запрос
        response = await app.state.http_client.send(proxied_req)
        
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info({
            "event": "proxy_response_received",
            "target_service": target_service,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2)
        })
        
        # Возвращаем ответ клиенту
        response_headers = {
        k: v for k, v in response.headers.items()
        if k.lower() not in ["location"]}
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response_headers)
        )
    except httpx.RequestError as e:
        duration_ms = (time.time() - start_time) * 1000
        
        logger.error({
            "event": "proxy_request_error",
            "target_service": target_service,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "duration_ms": round(duration_ms, 2)
        })
        
        return Response(
            content=f'{{"detail": "Service unavailable: {str(e)}"}}',
            status_code=503,
            media_type="application/json"
        )
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        logger.error({
            "event": "proxy_unexpected_error",
            "target_service": target_service,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "duration_ms": round(duration_ms, 2)
        })
        
        return Response(
            content=f'{{"detail": "Internal gateway error"}}',
            status_code=500,
            media_type="application/json"
            )