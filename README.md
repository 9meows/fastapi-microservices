# FastAPI Microservices Architecture

Проект демонстрирующий микросервисную архитектуру с использованием FastAPI, RabbitMQ и Docker.

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-4.1.1-orange.svg)](https://www.rabbitmq.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)
[![Tests](https://img.shields.io/badge/Tests-Passing-success.svg)](https://github.com/9meows/fastapi-microservices)

---

## 📋 Содержание

- [Описание проекта](#описание-проекта)
- [Архитектура](#архитектура)
- [Технологический стек](#технологический-стек)
- [Структура проекта](#структура-проекта)
- [Быстрый старт](#быстрый-старт)
- [API документация](#api-документация)
- [Особенности реализации](#особенности-реализации)
- [Тестирование](#тестирование)
- [Мониторинг и логирование](#мониторинг-и-логирование)
- [Безопасность](#безопасность)
- [Примеры использования](#примеры-использования)
- [CI/CD](#cicd)

---

## 🎯 Описание проекта

Это проект, демонстрирующий реализацию микросервисной архитектуры для управления постами и категориями. Проект включает три основных сервиса, взаимодействующих через API Gateway и RabbitMQ.

### Основные возможности

- ✅ **Микросервисная архитектура** с независимыми сервисами
- ✅ **API Gateway** для маршрутизации запросов
- ✅ **Асинхронная коммуникация** между сервисами через RabbitMQ (RPC pattern)
- ✅ **Clean Architecture** с разделением на слои (routers → services → repositories)
- ✅ **Dependency Injection** через FastAPI
- ✅ **Docker Compose** для оркестрации сервисов
- ✅ **Комплексное тестирование** (unit, integration тесты)
- ✅ **Structured Logging** с JSON-форматом
- ✅ **Rate Limiting** через Redis
- ✅ **CI/CD Pipeline** через GitHub Actions

---

## 🏗 Архитектура

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│    API Gateway          │
│  • Rate Limiting        │
│  • Request Logging      │
│  • Proxy Routing        │
└───────┬─────────────────┘
        │
        ├─────────────────┬─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Posts Service │  │Categories    │  │  RabbitMQ    │
│              │  │Service       │  │              │
│  SQLite DB   │  │  SQLite DB   │  │   (RPC)      │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
           RPC через RabbitMQ для валидации
                         │
                         ▼
                  ┌──────────────┐
                  │    Redis     │
                  │ Rate Limiter │
                  └──────────────┘
```

### Поток данных

1. **Клиент** → отправляет запрос к API Gateway (`:8000`)
2. **API Gateway** → 
   - Проверяет rate limit в Redis (100 req/5min)
   - Логирует запрос с correlation ID
   - Маршрутизирует запрос к нужному сервису
3. **Posts Service** → при создании поста проверяет существование категории через RabbitMQ RPC
4. **Categories Service** → обрабатывает RPC-запрос и возвращает результат валидации
5. **Response** → логируется и возвращается клиенту

---

## 🛠 Технологический стек

### Backend Framework

- **FastAPI** - современный асинхронный веб-фреймворк
- **Uvicorn** - ASGI сервер

### База данных

- **SQLAlchemy** (async) - ORM для работы с БД
- **SQLite** + **aiosqlite** - встроенная БД (для разработки)

### Межсервисная коммуникация

- **RabbitMQ** - брокер сообщений для RPC
- **aio-pika** - асинхронный клиент для RabbitMQ
- **httpx** - HTTP клиент для API Gateway

### Кэширование и Rate Limiting

- **Redis** - хранилище для rate limiting
- **fastapi-limiter** - middleware для ограничения запросов

### Логирование

- **Loguru** - structured logging с JSON форматом

### Инфраструктура

- **Docker** + **Docker Compose** - контейнеризация
- **Pydantic** - валидация данных

### Тестирование

- **pytest** - фреймворк для тестирования
- **pytest-asyncio** - поддержка async тестов
- **pytest-mock** - создание моков
- **httpx** - HTTP клиент для тестов
- **respx** - мокирование HTTP запросов

---

## 📁 Структура проекта

```
fastapi-microservices/
│
├── api_gateway_service/          # API Gateway
│   ├── app/
│   │   ├── core/
│   │   │   └── logging.py 
│   │   └── main.py              # Прокси-логика маршрутизации
│   ├── tests/                   # Тесты Gateway
│   │   ├── conftest.py
│   │   └── test_gateway.py
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── posts_service/                # Сервис постов
│   ├── app/
│   │   ├── api/routers/         # REST API endpoints
│   │   ├── core/                # Конфигурация, зависимости
│   │   │   ├── database.py      # Подключение к БД
│   │   │   ├── dependencies.py  # DI контейнеры
│   │   │   ├── logging.py       # Structured logging
│   │   │   └── rabbitmq.py      # RPC клиент
│   │   ├── models/              # SQLAlchemy модели
│   │   ├── repositories/        # Слой работы с БД
│   │   ├── schemas/             # Pydantic схемы
│   │   ├── services/            # Бизнес-логика
│   │   └── main.py
│   ├── tests/                   # Тесты Posts Service
│   │   ├── integration/
│   │   │   └── test_posts_api.py
│   │   ├── unit/
│   │   │   └── test_post_service.py
│   │   └── conftest.py
│   ├── Dockerfile
│   ├── pytest.ini
│   └── requirements.txt
│
├── categories_service/           # Сервис категорий
│   ├── app/
│   │   ├── api/routers/
│   │   ├── core/
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   ├── logging.py
│   │   │   └── rabbitmq_worker.py  # RPC server
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/                   #  Тесты Categories Service
│   │   ├── integration/
│   │   │   └── test_categories_api.py
│   │   ├── unit/
│   │   │   └── test_category_service.py
│   │   └── conftest.py
│   ├── Dockerfile
│   ├── pytest.ini
│   └── requirements.txt
│
├── .github/
│   └── workflows/
│       └── main.yml              # CI/CD pipeline
│
├── docker-compose.yml            # Оркестрация сервисов
├── .env.example                  # Пример переменных окружения
└── .gitignore
```

---

## 🚀 Быстрый старт

### Установка и запуск

1. **Клонируйте репозиторий**

```bash
git clone https://github.com/9meows/fastapi-microservices.git
cd fastapi-microservices
```

2. **Создайте файл `.env`**

```bash
cp .env.example .env
```

Содержимое `.env`:

```env
# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# Database paths
POSTS_DB_URL=sqlite+aiosqlite:///./data/posts.db
CATEGORIES_DB_URL=sqlite+aiosqlite:///./data/categories.db

# Service URLs
POSTS_SERVICE_URL=http://posts_service:8000
CATEGORIES_SERVICE_URL=http://categories_service:8000
```

3. **Запустите сервисы**

```bash
docker-compose up --build
```

4. **Проверьте работоспособность**

- API Gateway: http://localhost:8000
- RabbitMQ Management: http://localhost:15672 (guest/guest)
- Posts: http://localhost:8000/posts
- Categories: http://localhost:8000/categories

---

## 📖 API документация

### API Gateway (`:8000`)

Единая точка входа для всех клиентских запросов.

**Маршрутизация:**

- `/posts/*` → Posts Service
- `/categories/*` → Categories Service

### Categories Service

#### Создать категорию

```http
POST /categories/
Content-Type: application/json

{
  "name": "Technology"
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "name": "Technology"
}
```

#### Получить все категории

```http
GET /categories/?skip=0&limit=100
```

#### Получить категорию по ID

```http
GET /categories/{category_id}
```

### Posts Service

#### Создать пост

```http
POST /posts/
Content-Type: application/json

{
  "title": "My First Post",
  "content": "This is the content of the post",
  "category_id": 1
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "title": "My First Post",
  "content": "This is the content of the post",
  "category_id": 1
}
```

**Валидация:** Перед созданием поста проверяется существование `category_id` через RabbitMQ RPC.

#### Получить все посты

```http
GET /posts/?skip=0&limit=100
```

#### Получить посты по категории

```http
GET /posts/?category_id=1&skip=0&limit=100
```

#### Получить пост по ID

```http
GET /posts/{post_id}
```

---

## 🔍 Особенности реализации

### 1. API Gateway Pattern

API Gateway использует **httpx** для проксирования запросов:

```python
# Определение целевого сервиса по префиксу пути
if path.startswith("posts"):
    target_url = f"{POSTS_SERVICE_URL}/{path}"
elif path.startswith("categories"):
    target_url = f"{CATEGORIES_SERVICE_URL}/{path}"
```

**Преимущества:**

- Единая точка входа для клиентов
- Скрывает внутреннюю архитектуру
- Упрощает обработку CORS, аутентификации, rate limiting

### 2. RabbitMQ RPC для валидации

Posts Service проверяет существование категории **асинхронно** через RabbitMQ:

**Posts Service (RPC Client):**

```python
async def check_exists(self, category_id: int) -> bool:
    response = await self.rpc_client.call(category_id)
    return response == b'true'
```

**Categories Service (RPC Server):**

```python
async def process_category_check(message):
    category_id = int(message.body.decode())
    # Проверка в БД
    category = await service.get_category_by_id(category_id)
    response = b"true" if category else b"false"
    # Отправка ответа
    await default_exchange.publish(...)
```

**Почему RabbitMQ, а не прямой HTTP?**

- Демонстрация паттерна асинхронной коммуникации
- Отказоустойчивость через очереди
- Масштабируемость (можно добавить несколько consumer'ов)

### 3. Clean Architecture

Каждый сервис следует принципам чистой архитектуры:

```
Routers (HTTP layer)
    ↓
Services (Business logic)
    ↓
Repositories (Data access)
    ↓
Models (Database entities)
```

**Пример Flow:**

```python
# 1. Router принимает запрос
@router.post("/")
async def create_post(post: PostBase, service: PostService = Depends(...)):
    return await service.create_post(post)

# 2. Service выполняет бизнес-логику
async def create_post(self, post: PostBase) -> Post:
    # Валидация через RabbitMQ
    if not await self.category_validator.check_exists(post.category_id):
        raise HTTPException(400, "Invalid category")
    # Сохранение через репозиторий
    return await self.post_repo.create(...)

# 3. Repository работает с БД
async def create(self, title: str, content: str, category_id: int) -> Post:
    db_post = Post(title=title, content=content, category_id=category_id)
    self.db.add(db_post)
    await self.db.commit()
    return db_post
```

### 4. Dependency Injection

FastAPI автоматически внедряет зависимости:

```python
def get_post_service(
    post_repo: PostRepository = Depends(get_post_repository),
    category_validator: RabbitMQCategoryValidator = Depends(get_category_validator)
) -> PostService:
    return PostService(post_repo=post_repo, category_validator=category_validator)
```

**Преимущества:**

- Легкая замена реализаций (например, моки для тестов)
- Инверсия зависимостей (SOLID)
- Чистый и тестируемый код

### 5. Lifespan Events

Управление подключениями через контекстный менеджер:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_db_and_tables()
    await category_validator_instance.connect()
    consumer_task = asyncio.create_task(run_consumer())

    yield

    # Shutdown
    consumer_task.cancel()
    await category_validator_instance.close()
```

---

## 🧪 Тестирование

### Стратегия тестирования

Проект покрыт **комплексными тестами** на нескольких уровнях:

```
📦 Тестовое покрытие
├── Unit Tests          # Тестирование бизнес-логики
│   ├── Service layer
│   ├── Repository
│   └── Validation logic
│
├── Integration Tests   # Тестирование API
│   ├── API endpoints
│   ├── Database interactions
│   └── Pydantic validation
│
└── Gateway Tests        # Тестирование маршрутизации
    ├── Proxy routing
    └── Request forwarding
```

### Запуск тестов

**Все тесты всех сервисов:**

```bash
# Через docker-compose
docker-compose run posts_service pytest -v
docker-compose run categories_service pytest -v
docker-compose run api_gateway_service pytest -v
```

**Тесты конкретного сервиса:**

```bash
# Posts Service
cd posts_service
pytest -v

# С покрытием кода
pytest --cov=app --cov-report=html

# Конкретный тест-файл
pytest tests/unit/test_post_service.py -v

# С детальным выводом
pytest -v --tb=short
```

**CI/CD автоматически запускает тесты:**

```bash
# Через GitHub Actions при каждом push/PR
# См. .github/workflows/main.yml
```


### Что покрыто тестами

#### ✅ Posts Service

**Unit Tests:**
- Создание поста с валидной категорией
- Создание поста с невалидной категорией
- Получение поста по ID
- Получение всех постов
- Получение постов по категории

**Integration Tests:**
- POST /posts/ - успешное создание
- POST /posts/ - невалидная категория
- GET /posts/{id} - существующий пост
- GET /posts/{id} - несуществующий пост (404)
- GET /posts/ - пустой список
- GET /posts/ - список с данными
- GET /posts/?category_id=X - фильтрация
- GET /posts/?skip=N&limit=M - пагинация
- POST /posts/ - невалидные данные (422)

#### ✅ Categories Service

**Unit Tests:**
- Создание категории
- Создание дубликата категории
- Получение категории по ID
- Получение всех категорий
- Пагинация

**Integration Tests:**
- POST /categories/ - успешное создание
- POST /categories/ - дубликат (400)
- GET /categories/{id} - существующая категория
- GET /categories/{id} - несуществующая (404)
- GET /categories/ - пустой список
- GET /categories/ - список с данными
- GET /categories/?skip=N&limit=M - пагинация
- POST /categories/ - невалидные данные (422)

#### ✅ API Gateway

**Integration Tests:**
- Проксирование GET к Posts Service
- Проксирование GET к Categories Service
- Проксирование POST запросов
- Обработка неизвестных путей (404)

### Преимущества подхода

- ✅ **Изоляция**: Каждый тест независим (in-memory DB, моки)
- ✅ **Скорость**: Тесты выполняются быстро (нет реальных RPC вызовов)
- ✅ **Детерминированность**: Моки обеспечивают предсказуемое поведение
- ✅ **Покрытие**: Unit + Integration = полное покрытие функционала
- ✅ **CI/CD**: Автоматический запуск в GitHub Actions

---

## 📊 Мониторинг и логирование

### Structured Logging

Все сервисы используют **Loguru** для JSON-форматированного логирования:

```python
# Конфигурация
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    serialize=True,  # JSON формат
    level="INFO"
)
```

**Пример лога:**

```json
{
  "time": "2024-01-26T10:30:15.123+00:00",
  "level": "INFO",
  "message": {
    "event": "create_post_success",
    "post_id": 1,
    "title": "My Post",
    "category_id": 1,
    "service": "posts_service"
  }
}
```

### События логирования

| Event | Сервис | Описание |
|-------|--------|----------|
| `service_startup` | Все | Запуск сервиса |
| `service_ready` | Все | Сервис готов к работе |
| `request_started` | Все | Входящий запрос |
| `request_completed` | Все | Запрос обработан |
| `create_post_success` | Posts | Пост создан |
| `rpc_request_received` | Categories | Получен RPC запрос |
| `rpc_response_sent` | Categories | Отправлен RPC ответ |
| `gateway_forwarding` | Gateway | Проксирование запроса |
| `proxy_response_received` | Gateway | Получен ответ от сервиса |

### Request Duration Tracking

Каждый запрос логируется с временем выполнения:

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    
    logger.info({
        "event": "request_completed",
        "method": request.method,
        "path": str(request.url.path),
        "status_code": response.status_code,
        "duration_ms": round(duration_ms, 2)
    })
```

### Health Checks

Каждый сервис предоставляет health check endpoint:

```bash
# API Gateway
curl http://localhost:8000/health
# {"status": "healthy", "service": "api_gateway"}

# Posts Service (через Gateway)
curl http://localhost:8000/posts/ 
# Проверка доступности

# RabbitMQ Management
curl http://localhost:15672/api/health/checks/alarms
```

---

## 🔒 Безопасность

### Rate Limiting

API Gateway ограничивает количество запросов через **Redis**:

```python
@app.api_route("/{path:path}", 
               dependencies=[Depends(RateLimiter(times=100, minutes=5))])
```

**Параметры:**
- 100 запросов на IP адрес
- В течение 5 минут
- При превышении: `429 Too Many Requests`

**Заголовок ответа:**
```
X-RateLimit-Limit: 100
```

### Input Validation

Pydantic схемы валидируют входные данные:

```python
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1)
    category_id: PositiveInt  # Только положительные числа
```

**Невалидный запрос возвращает 422:**

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### SQL Injection Protection

SQLAlchemy ORM защищает от SQL injection:

```python
# ✅ Безопасно: параметризованные запросы
result = await self.db.scalar(
    select(Post).where(Post.id == post_id)
)
```

### Environment Variables

Конфиденциальные данные в переменных окружения:

```env
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
DATABASE_URL=sqlite+aiosqlite:///./data/posts.db
```

**Не коммитятся в Git** (через `.gitignore`).

---

## 💡 Примеры использования

### Полный workflow создания поста

```bash
# 1. Создать категорию
curl -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Technology"}'

# Response: {"id": 1, "name": "Technology"}

# 2. Создать пост в этой категории
curl -X POST http://localhost:8000/posts/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "FastAPI is awesome",
    "content": "Learn microservices with FastAPI",
    "category_id": 1
  }'

# Response: {"id": 1, "title": "FastAPI is awesome", ...}

# 3. Получить все посты в категории
curl http://localhost:8000/posts/?category_id=1

# 4. Попытка создать пост с несуществующей категорией (валидация)
curl -X POST http://localhost:8000/posts/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Invalid post",
    "content": "This should fail",
    "category_id": 999
  }'

# Response: 400 {"detail": "Invalid category_id: Category not found"}
```

### Примеры с curl

**Создание нескольких категорий:**

```bash
curl -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Technology"}'

curl -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Sports"}'

curl -X POST http://localhost:8000/categories/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Travel"}'
```

**Получение списка с пагинацией:**

```bash
# Первая страница (2 записи)
curl "http://localhost:8000/categories/?skip=0&limit=2"

# Вторая страница
curl "http://localhost:8000/categories/?skip=2&limit=2"
```

**Фильтрация постов по категории:**

```bash
# Все посты в категории "Technology" (id=1)
curl "http://localhost:8000/posts/?category_id=1"

# С пагинацией
curl "http://localhost:8000/posts/?category_id=1&skip=0&limit=10"
```

---

## 🔄 CI/CD

### GitHub Actions Pipeline

Проект использует **автоматическое тестирование** при каждом push/PR:

```yaml
# .github/workflows/main.yml
name: tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-categories:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install dependencies
        working-directory: ./categories_service
        run: |
          pip install -r requirements-dev.txt
      - name: Run tests
        working-directory: ./categories_service
        run: pytest -v --tb=short

  test-posts:
    # Аналогично для Posts Service

  test-api-gateway:
    # Аналогично для API Gateway
```

**Что проверяется:**
- ✅ Все unit тесты
- ✅ Все integration тесты
- ✅ Линтинг кода (в будущем)
- ✅ Покрытие тестами (в будущем)

**Статус тестов:**

[![Tests](https://img.shields.io/badge/Tests-Passing-success.svg)](https://github.com/9meows/fastapi-microservices/actions)

---

## 📝 Лицензия

MIT License

---

## 👤 Автор

**9meows**

- GitHub: [@9meows](https://github.com/9meows)
- Проект создан для демонстрации навыков в backend-разработке

---

<3


