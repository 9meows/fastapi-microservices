import os
import httpx
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    try:
        yield
    finally:
        await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

POSTS_SERVICE_URL = os.getenv("POSTS_SERVICE_URL")
CATEGORIES_SERVICE_URL = os.getenv("CATEGORIES_SERVICE_URL")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(request: Request, path: str):
    """Функция определяет, какому сервису перенаправить запрос, основываясь на начальной части URL пути."""
    target_url = None
    if path.startswith("posts"):
        target_url = f"{POSTS_SERVICE_URL}/{path}"
    elif path.startswith("categories"):
        target_url = f"{CATEGORIES_SERVICE_URL}/{path}"

    if not target_url:
        return Response(content="Not Found", status_code=404)

    # тело запроса
    body = await request.body()

    # Формируем запрос к целевому сервису
    proxied_req = app.state.http_client.build_request(
        method=request.method,
        url=target_url,
        headers=request.headers,
        params=request.query_params,
        content=body
    )

    # Отправляем запрос
    response = await app.state.http_client.send(proxied_req)

    # Возвращаем ответ клиенту
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )