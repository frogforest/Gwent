# Gwent Card Game — Микросервисная архитектура

## Описание

Headless REST API приложение на основе микросервисной архитектуры для карточной игры в стиле Gwent.

### Микросервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| **gateway** | 8000 | API Gateway: единая точка входа, проверка JWT, маршрутизация |
| **user_deck** | 8001 | Управление пользователями (регистрация, JWT) и колодами + картами в колоде |
| **card** | 8002 | Каталог карт с фильтрацией, случайная выборка, начальные данные (12 карт) |
| **game** | 8003 | Игровая логика: создание матчей, ходы, подсчёт очков, победитель |

### Технологический стек

- **Язык**: Python 3.11
- **Фреймворк**: FastAPI (асинхронный)
- **HTTP-клиент между сервисами**: httpx
- **Аутентификация**: JWT (HMAC-SHA256)
- **Тестирование**: pytest + TestClient + unittest.mock
- **Линтер**: flake8, mypy
- **Форматтер**: black
- **Git hooks**: pre-commit
- **Контейнеризация**: Docker + docker-compose

---

## Структура проекта

```
services/
├── docker-compose.yml
├── README.md
├── gateway/                         # API Gateway
│   ├── app/
│   │   ├── main.py                  # Прокси + проверка JWT
│   │   ├── auth.py                  # Декодирование JWT
│   │   └── config.py                # URL сервисов, публичные пути
│   └── tests/
│       └── test_gateway.py
├── user_deck/                       # Сервис пользователей и колод
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── auth.py                  # JWT: создание и проверка
│   │   ├── storage.py               # In-memory хранилище
│   │   ├── http_client.py           # HTTP запрос к Card-сервису
│   │   └── routers/
│   │       ├── users.py             # /register, /login, /profile
│   │       └── decks.py             # CRUD колод + карты в колоде
│   └── tests/
│       ├── test_users.py
│       ├── test_decks.py
│       └── test_deck_cards.py
├── card/                            # Сервис каталога карт
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── storage.py
│   │   ├── seed.py                  # 12 стартовых карт
│   │   └── routers/
│   │       └── cards.py             # CRUD + фильтрация + /random
│   └── tests/
│       ├── test_cards.py
│       └── test_random.py
└── game/                            # Игровой сервис
    ├── app/
    │   ├── main.py
    │   ├── models.py
    │   ├── storage.py
    │   ├── game_logic.py            # Логика ходов, определение победителя
    │   ├── http_client.py           # Запросы к Card и Deck сервисам
    │   └── routers/
    │       └── games.py             # CRUD игр + ходы
    └── tests/
        ├── test_games.py
        └── test_moves.py
```

---

## Быстрый старт

### Вариант 1: Docker Compose (рекомендуется)

```bash
cd services
docker-compose up --build
```

| Сервис | URL |
|--------|-----|
| API Gateway (единая точка входа) | http://localhost:8000 |
| user_deck | http://localhost:8001 |
| card | http://localhost:8002 |
| game | http://localhost:8003 |

### Вариант 2: Локальный запуск

```bash
cd services/<service_name>
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port <port>
```

---

## API Документация

Swagger UI доступен по `http://localhost:<port>/docs`

### API Gateway (порт 8000)

Единая точка входа для клиентов. Проверяет JWT во всех запросах кроме:
- `POST /register` — публичный
- `POST /login` — публичный

Маршрутизация:

| Префикс пути | Целевой сервис |
|---|---|
| `/register`, `/login`, `/profile` | user_deck |
| `/decks*` | user_deck |
| `/cards*` | card |
| `/games*` | game |

### user_deck (порт 8001)

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/register` | Регистрация пользователя |
| POST | `/login` | Вход, получение JWT |
| GET | `/profile` | Текущий пользователь |
| POST | `/decks` | Создать колоду |
| GET | `/decks` | Список колод |
| GET | `/decks/{id}` | Колода по ID (включает card_ids) |
| DELETE | `/decks/{id}` | Удалить колоду |
| POST | `/decks/{id}/cards/{card_id}` | Добавить карту в колоду |
| DELETE | `/decks/{id}/cards/{card_id}` | Убрать карту из колоды |

### card (порт 8002)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/cards` | Список карт (фильтры: faction, type, min_strength) |
| GET | `/cards/random` | Случайные карты (параметры: count, faction, type) |
| GET | `/cards/{id}` | Карта по ID |
| POST | `/cards` | Добавить карту в каталог |

### game (порт 8003)

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/games` | Создать игру (загружает руки из колод) |
| GET | `/games/{id}` | Состояние игры |
| POST | `/games/{id}/moves` | Совершить ход |

Тело хода: `{"player_id": 1, "card_id": 101}`

Логика ходов:
1. Проверяется очерёдность хода
2. Карта должна быть в руке игрока
3. Сила карты запрашивается у Card-сервиса
4. Сила прибавляется к счёту игрока
5. Ход переходит к сопернику
6. Когда руки пусты — игра завершается, определяется победитель

---

## Примеры запросов через Gateway

```bash
# Регистрация
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "nikita", "password": "secret"}'

# Вход — получаем токен
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "nikita", "password": "secret"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Создать колоду
curl -X POST http://localhost:8000/decks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Моя колода"}'

# Добавить карту в колоду
curl -X POST http://localhost:8000/decks/1/cards/1 \
  -H "Authorization: Bearer $TOKEN"

# Случайные карты из каталога
curl "http://localhost:8000/cards/random?count=5&faction=Neutral"

# Создать игру
curl -X POST http://localhost:8000/games \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"player1_id":1,"player2_id":2,"player1_deck_id":1,"player2_deck_id":2}'

# Сделать ход
curl -X POST http://localhost:8000/games/1/moves \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1, "card_id": 1}'
```

---

## Тестирование

```bash
# Все тесты в одном сервисе
cd services/<service_name>
pip install -r requirements-dev.txt
PYTHONPATH=. python3 -m pytest tests/ -v

# Все 4 сервиса сразу
for svc in user_deck card game gateway; do
  echo "=== $svc ===" && cd services/$svc && PYTHONPATH=. python3 -m pytest tests/ -v && cd ../..
done
```

Итого тестов: **56** (user_deck: 20, card: 13, game: 15, gateway: 8)

---

## Линтеры и форматтер

```bash
cd services/<service_name>
python3 -m flake8 app tests       # проверка стиля
python3 -m black app tests        # форматирование
python3 -m mypy app               # проверка типов
```

---

## Git Hooks (pre-commit)

```bash
cd services/<service_name>
pip install pre-commit
pre-commit install
```

Хуки при каждом `git commit`: **black → flake8 → mypy → pytest**

---

## Ответственные

| Сервис | Ответственный |
|--------|--------------|
| user_deck + gateway | Никита Сычев |
| card | Полина Васильева |
| game | Аня Смирнова |
