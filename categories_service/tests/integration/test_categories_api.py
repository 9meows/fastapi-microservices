import pytest

@pytest.mark.asyncio
async def test_create_category_success(client):
    response = await client.post("/categories/", json={"name":"Technology"})
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Technology"
    assert "id" in data
    assert data["id"] == 1
    
@pytest.mark.asyncio
async def test_create_category_duplicate(client):
    await client.post("/categories/", json={"name":"Technology"})
    
    response = await client.post("/categories/", json={"name":"Technology"})
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
    
    
@pytest.mark.asyncio
async def test_get_category_by_id_success(client):
    create_response = await client.post("/categories/", json={"name": "Sports"})
    category_id = create_response.json()["id"]
    
    response = await client.get(f"/categories/{category_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == "Sports"


@pytest.mark.asyncio
async def test_get_category_by_id_not_found(client):
    response = await client.get("/categories/999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


@pytest.mark.asyncio
async def test_get_all_categories_empty(client):
    response = await client.get("/categories/")
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_categories_with_data(client):
    await client.post("/categories/", json={"name": "Tech"})
    await client.post("/categories/", json={"name": "Sports"})
    await client.post("/categories/", json={"name": "Music"})
    
    response = await client.get("/categories/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Tech"
    assert data[1]["name"] == "Sports"
    assert data[2]["name"] == "Music"


@pytest.mark.asyncio
async def test_get_categories_with_pagination(client):
    for i in range(5):
        await client.post("/categories/", json={"name": f"Category{i}"})
    
    response = await client.get("/categories/?skip=2&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Category2"
    assert data[1]["name"] == "Category3"


@pytest.mark.asyncio
async def test_create_category_invalid_data(client):
    response = await client.post("/categories/", json={"name": ""})
    assert response.status_code == 422