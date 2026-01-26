import pytest
import respx
from httpx import Response


@pytest.mark.asyncio
@respx.mock
async def test_proxy_to_posts_service(client):
    """Тест: проксирования get запроса к posts service"""
    mock_posts = respx.get("http://posts_service:8000/posts/").mock(
        return_value=Response(status_code=200,
                              json=[{"id": 1, "title": "Test Post", "content": "Content", "category_id": 1}]))
    
    response = await client.get("/posts/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Post"
    
    assert mock_posts.called


@pytest.mark.asyncio
@respx.mock
async def test_proxy_to_categories_service(client):
    """Тест: проксирования get запроса к categories service"""
    mock_categories = respx.get("http://categories_service:8000/categories/").mock(
        return_value=Response(status_code=200,
                              json=[{"id": 1, "name": "Technology"}]))
    
    response = await client.get("/categories/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Technology"
    assert mock_categories.called


@pytest.mark.asyncio
@respx.mock
async def test_proxy_post_request(client):
    """Тест: проксированя POST-запроса"""
    mock_create = respx.post("http://categories_service:8000/categories/").mock(
        return_value=Response(status_code=201,
                              json={"id": 1, "name": "Sports"}))
    
    response = await client.post("/categories/", json={"name": "Sports"})
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sports"
    assert mock_create.called


@pytest.mark.asyncio
async def test_unknown_path_returns_404(client):
    """Тест: для неизвестного пути"""
    response = await client.get("/htap/path/")
    
    assert response.status_code == 404


