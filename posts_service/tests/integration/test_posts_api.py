import pytest


@pytest.mark.asyncio
async def test_create_post_success(client, mock_category_validator):
    """Тест: создание поста через API"""
    mock_category_validator.check_exists.return_value = True
    
    response = await client.post("/posts/", json={"title": "My First Post", "content": 
        "This is the content", "category_id": 1})
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Post"
    assert data["content"] == "This is the content"
    assert data["category_id"] == 1
    assert "id" in data
    
    mock_category_validator.check_exists.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_create_post_invalid_category(client, mock_category_validator):
    """Тест: создание поста с несуществующей категорией"""
    mock_category_validator.check_exists.return_value = False
    
    response = await client.post("/posts/", json={"title": "Invalid Post","content": 
        "This should fail","category_id": 999})
    
    assert response.status_code == 400
    assert "Invalid category_id" in response.json()["detail"]
    mock_category_validator.check_exists.assert_called_once_with(999)


@pytest.mark.asyncio
async def test_get_post_by_id_success(client, mock_category_validator):
    """Тест:  получение поста по ID"""
    mock_category_validator.check_exists.return_value = True
    create_response = await client.post("/posts/", json={"title": "Test Post",
                                                         "content": "Content","category_id": 1})
    post_id = create_response.json()["id"]
    
    response = await client.get(f"/posts/{post_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_id
    assert data["title"] == "Test Post"


@pytest.mark.asyncio
async def test_get_post_by_id_not_found(client):
    """Тест: получение несуществующего поста"""
    response = await client.get("/posts/999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


@pytest.mark.asyncio
async def test_get_all_posts_empty(client):
    """Тест: получение пустого списка постов"""
    response = await client.get("/posts/")
    
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_posts_with_data(client, mock_category_validator):
    """Тест:  получение списка постов"""
    mock_category_validator.check_exists.return_value = True
    
    await client.post("/posts/", json={"title": "Post 1", "content": "Content 1", "category_id": 1})
    await client.post("/posts/", json={"title": "Post 2", "content": "Content 2", "category_id": 1})
    await client.post("/posts/", json={"title": "Post 3", "content": "Content 3", "category_id": 2})
    
    response = await client.get("/posts/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["title"] == "Post 1"
    assert data[1]["title"] == "Post 2"
    assert data[2]["title"] == "Post 3"


@pytest.mark.asyncio
async def test_get_posts_by_category(client, mock_category_validator):
    """Тест: получение постов по category_id"""
    mock_category_validator.check_exists.return_value = True
    
    await client.post("/posts/", json={"title": "Tech Post 1", "content": "Content", "category_id": 1})
    await client.post("/posts/", json={"title": "Tech Post 2", "content": "Content", "category_id": 1})
    await client.post("/posts/", json={"title": "Sports Post", "content": "Content", "category_id": 2})
    
    response = await client.get("/posts/?category_id=1")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Tech Post 1"
    assert data[1]["title"] == "Tech Post 2"
    assert data[0]["category_id"] == 1


@pytest.mark.asyncio
async def test_get_posts_by_invalid_category(client, mock_category_validator):
    """Тест: получение постов по несуществующей категории"""
    mock_category_validator.check_exists.return_value = False
    
    response = await client.get("/posts/?category_id=999")
    
    assert response.status_code == 400
    assert "Invalid category_id" in response.json()["detail"]
    mock_category_validator.check_exists.assert_called_with(999)


@pytest.mark.asyncio
async def test_get_posts_with_pagination(client, mock_category_validator):
    """Тест: пагинация постов"""
    mock_category_validator.check_exists.return_value = True
    
    for i in range(5):
        await client.post("/posts/", json={"title": f"Post {i}", "content": f"Content {i}","category_id": 1})
    
    response = await client.get("/posts/?skip=2&limit=2")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Post 2"
    assert data[1]["title"] == "Post 3"


@pytest.mark.asyncio
async def test_create_post_invalid_data(client):
    """Тест: создание поста с невалидными данными"""
    response = await client.post("/posts/", json={"title": "","content": "Content","category_id": 1})
    
    assert response.status_code == 422
    
    

    
    















