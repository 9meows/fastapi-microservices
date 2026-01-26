import pytest
from fastapi import HTTPException

from app.services.posts import PostService
from app.repositories.posts import PostRepository
from app.schemas.post import PostBase


@pytest.mark.asyncio
async def test_create_post_success(db_session, mock_category_validator):
    """Тест: успешное создание поста"""
    repository = PostRepository(db=db_session)
    service = PostService(post_repo=repository, category_validator=mock_category_validator)
    post_data = PostBase(title="Test Post", content="Test content", category_id=1)
    
    mock_category_validator.check_exists.return_value = True
    
    result = await service.create_post(post_data)
    
    assert result is not None
    assert result.id == 1
    assert result.title == "Test Post"
    assert result.content == "Test content"
    assert result.category_id == 1
    
    mock_category_validator.check_exists.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_create_post_invalid_category(db_session, mock_category_validator):
    """Тест: создание поста с несуществующей категорией"""
    repository = PostRepository(db=db_session)
    service = PostService(post_repo=repository, category_validator=mock_category_validator)
    post_data = PostBase(title="Test Post", content="Content", category_id=999)
    
    mock_category_validator.check_exists.return_value = False
    
    with pytest.raises(HTTPException) as exc_info:
        await service.create_post(post_data)
    
    assert exc_info.value.status_code == 400
    assert "Invalid category_id" in exc_info.value.detail
    
    mock_category_validator.check_exists.assert_called_once_with(999)


@pytest.mark.asyncio
async def test_get_post_by_id_success(db_session, mock_category_validator):
    """Тест: получение поста по ID"""
    repository = PostRepository(db=db_session)
    service = PostService(post_repo=repository, category_validator=mock_category_validator)
    
    mock_category_validator.check_exists.return_value = True
    post_data = PostBase(title="My Post", content="Content", category_id=1)
    created = await service.create_post(post_data)
    
    result = await service.get_post_by_id(post_id=created.id)
    
    assert result is not None
    assert result.id == created.id
    assert result.title == "My Post"


@pytest.mark.asyncio
async def test_get_post_by_id_not_found(db_session, mock_category_validator):
    """Тест: получение несуществующего поста"""
    repository = PostRepository(db=db_session)
    service = PostService(post_repo=repository, category_validator=mock_category_validator)
    
    result = await service.get_post_by_id(post_id=999)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_all_posts(db_session, mock_category_validator):
    """Тест: получение всех постов"""
    repository = PostRepository(db=db_session)
    service = PostService(post_repo=repository, category_validator=mock_category_validator)
    
    mock_category_validator.check_exists.return_value = True
    await service.create_post(PostBase(title="Post 1", content="Content 1", category_id=1))
    await service.create_post(PostBase(title="Post 2", content="Content 2", category_id=1))
    await service.create_post(PostBase(title="Post 3", content="Content 3", category_id=2))
    
    result = await service.get_all_posts(skip=0, limit=100)
    
    assert len(result) == 3
    assert result[0].title == "Post 1"
    assert result[1].title == "Post 2"
    assert result[2].title == "Post 3"


@pytest.mark.asyncio
async def test_get_posts_by_category_success(db_session, mock_category_validator):
    """Тест: получение постов по категории"""
    repository = PostRepository(db=db_session)
    service = PostService(post_repo=repository, category_validator=mock_category_validator)
    
    mock_category_validator.check_exists.return_value = True
    await service.create_post(PostBase(title="Tech Post 1", content="Content", category_id=1))
    await service.create_post(PostBase(title="Tech Post 2", content="Content", category_id=1))
    await service.create_post(PostBase(title="Sports Post", content="Content", category_id=2))
    
    result = await service.get_posts_by_category(category_id=1, skip=0, limit=100)
    
    assert len(result) == 2
    assert result[0].title == "Tech Post 1"
    assert result[1].title == "Tech Post 2"
    assert result[0].category_id == 1
    assert result[1].category_id == 1
    
    mock_category_validator.check_exists.assert_called_with(1)


@pytest.mark.asyncio
async def test_get_posts_by_category_invalid_category(db_session, mock_category_validator):
    """Тест: получение постов по несуществующей категории"""
    repository = PostRepository(db=db_session)
    service = PostService(post_repo=repository, category_validator=mock_category_validator)
    
    mock_category_validator.check_exists.return_value = False
    
    with pytest.raises(HTTPException) as exc_info:
        await service.get_posts_by_category(category_id=999, skip=0, limit=100)
    
    assert exc_info.value.status_code == 400
    assert "Invalid category_id" in exc_info.value.detail
    mock_category_validator.check_exists.assert_called_once_with(999)