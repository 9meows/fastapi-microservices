import pytest
from app.services.categories import CategoryService
from app.repositories.categories import CategoryRepository
from app.schemas.category import CategoryBase


@pytest.mark.asyncio
async def test_create_category_success(db_session):
    repository = CategoryRepository(db=db_session)
    service = CategoryService(category_repo=repository)
    category_data = CategoryBase(name="Technology")
    
    result = await service.create_category(category_data)
    
    assert result is not None
    assert result.id == 1
    assert result.name == 'Technology'
    
@pytest.mark.asyncio
async def test_create_category_duplicate(db_session):
    repository = CategoryRepository(db=db_session)
    service = CategoryService(category_repo=repository)
    category_data = CategoryBase(name="Technology")
    
    await service.create_category(category_data)
    result = await service.create_category(category_data)
    
    assert result is None
    
@pytest.mark.asyncio
async def test_get_category_by_id_success(db_session):
    repository = CategoryRepository(db=db_session)
    service = CategoryService(category_repo=repository)
    category_data = CategoryBase(name="Technology")
    
    created = await service.create_category(category_data)
    result = await service.get_category_by_id(created.id)
    
    assert result is not None
    assert result.id == created.id
    assert result.name == "Technology"   

@pytest.mark.asyncio
async def test_get_category_by_id_not_found(db_session):
    repository = CategoryRepository(db=db_session)
    service = CategoryService(category_repo=repository)
    
    result = await service.get_category_by_id(category_id=999)
    
    assert result is None


@pytest.mark.asyncio
async def test_get_all_categories(db_session):
    repository = CategoryRepository(db=db_session)
    service = CategoryService(category_repo=repository)
    
    await service.create_category(CategoryBase(name="Tech"))
    await service.create_category(CategoryBase(name="Sports"))
    await service.create_category(CategoryBase(name="Music"))
    
    result = await service.get_all_categories(skip=0, limit=100)
    
    assert len(result) == 3
    assert result[0].name == "Tech"
    assert result[1].name == "Sports"
    assert result[2].name == "Music"


@pytest.mark.asyncio
async def test_get_all_categories_with_pagination(db_session):
    repository = CategoryRepository(db=db_session)
    service = CategoryService(category_repo=repository)
    
    for i in range(5):
        await service.create_category(CategoryBase(name=f"Category{i}"))
    
    result = await service.get_all_categories(skip=2, limit=2)
    
    assert len(result) == 2
    assert result[0].name == "Category2"
    assert result[1].name == "Category3"