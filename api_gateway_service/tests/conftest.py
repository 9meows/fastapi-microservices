import os
import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI, Request, Response

test_app = FastAPI(title="API Gateway Test")

POSTS_SERVICE_URL = os.getenv("POSTS_SERVICE_URL", "http://posts_service:8000")
CATEGORIES_SERVICE_URL = os.getenv("CATEGORIES_SERVICE_URL", "http://categories_service:8000")


@test_app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api_gateway"}


@test_app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(request: Request, path: str):
    target_url = None    
    if path.startswith("posts"):
        target_url = f"{POSTS_SERVICE_URL}/{path}"
    elif path.startswith("categories"):
        target_url = f"{CATEGORIES_SERVICE_URL}/{path}"

    if not target_url:
        return Response(
            content='{"detail": "Not Found"}',
            status_code=404,
            media_type="application/json"
        )

    body = await request.body()
    headers = {
        key: value for key, value in request.headers.items()
        if key.lower() not in ['host', 'content-length']
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body
            )
            
            response_headers = {
                k: v for k, v in response.headers.items()
                if k.lower() not in ["location"]
            }
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response_headers)
            )
            
        except httpx.RequestError as e:
            return Response(
                content=f'{{"detail": "Service unavailable: {str(e)}"}}',
                status_code=503,
                media_type="application/json"
            )
        except Exception as e:
            return Response(
                content='{"detail": "Internal gateway error"}',
                status_code=500,
                media_type="application/json"
            )


@pytest_asyncio.fixture()
async def client():
    """HTTP клиент"""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c