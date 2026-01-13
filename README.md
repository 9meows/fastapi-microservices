# FastAPI Microservices Architecture

Учебный проект демонстрирующий микросервисную архитектуру с использованием FastAPI, RabbitMQ и Docker.

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-4.1.1-orange.svg)](https://www.rabbitmq.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)

---

## 📋 Содержание

- [Описание проекта](#описание-проекта)
- [Архитектура](#архитектура)
- [Технологический стек](#технологический-стек)
- [Структура проекта](#структура-проекта)
- [Быстрый старт](#быстрый-старт)
- [API документация](#api-документация)
- [Особенности реализации](#особенности-реализации)
- [Примеры использования](#примеры-использования)

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
│                         │
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
```

### Поток данных

1. **Клиент** → отправляет запрос к API Gateway (`:8000`)
2. **API Gateway** → маршрутизирует запрос к нужному сервису
3. **Posts Service** → при создании поста проверяет существование категории через RabbitMQ RPC
4. **Categories Service** → обрабатывает RPC-запрос и возвращает результат валидации

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

### Инфраструктура

- **Docker** + **Docker Compose** - контейнеризация
- **Pydantic** - валидация данных

---

## 📁 Структура проекта

```
fastapi-microservices/
│
├── api_gateway_service/          # API Gateway
│   ├── app/
│   │   └── main.py              # Прокси-логика маршрутизации
│   ├── Dockerfile
│   └── requirements.txt
│
├── posts_service/                # Сервис постов
│   ├── app/
│   │   ├── api/routers/         # REST API endpoints
│   │   ├── core/                # Конфигурация, зависимости
│   │   │   ├── database.py      # Подключение к БД
│   │   │   ├── dependencies.py  # DI контейнеры
│   │   │   └── rabbitmq.py      # RPC клиент
│   │   ├── models/              # SQLAlchemy модели
│   │   ├── repositories/        # Слой работы с БД
│   │   ├── schemas/             # Pydantic схемы
│   │   ├── services/            # Бизнес-логика
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── categories_service/           # Сервис категорий
│   ├── app/
│   │   ├── api/routers/
│   │   ├── core/
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   └── rabbitmq_worker.py  # RPC server
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
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
