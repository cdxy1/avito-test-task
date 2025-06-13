# Магазин мерча на FastAPI

## Технологии

- **Python 3.12**
- **FastAPI** — фреймворк для создания API.
- **SQLAlchemy** — ORM для работы с базой данных.
- **Alembic** — инструмент для миграций базы данных.
- **Redis** — кэширование и хранение сессий.
- **PostgreSQL** — основная база данных.
- **Docker** — контейнеризация приложения.
- **Pytest** — тестирование.
- **Locust** — нагрузочное тестирование.

## Зависимости

Проект использует Poetry для управления зависимостями. Все зависимости перечислены в `pyproject.toml`.

Основные зависимости:
- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `passlib`
- `pyjwt`
- `bcrypt`
- `alembic`
- `redis`
- `asyncpg`
- `psycopg2-binary`

Для разработки и тестирования:
- `ruff`
- `aiosqlite`
- `pytest-asyncio`
- `httpx`
- `pytest-cov`
- `locust`

## Установка и запуск

### 1. Клонируйте репозиторий

```
git clone https://github.com/cdxy1/avito-test-task.git
```

### 2. Установите зависимости

Убедитесь, что у вас установлен Poetry. Затем выполните:

```
poetry install
```

### 3. Настройка окружения

Создайте файл `.env` в корне проекта и добавьте туда необходимые переменные окружения:

### 4. Запуск с Docker

Проект включает `docker-compose.yml` для запуска приложения, PostgreSQL и Redis.

```
docker-compose up --build
```

После запуска приложение будет доступно по адресу: `http://localhost:8000`.

### 5. Миграции базы данных

Для применения миграций используйте Alembic:

```
alembic upgrade head
```

### 6. Запуск без Docker

Если вы хотите запустить приложение без Docker, убедитесь, что у вас установлены PostgreSQL и Redis. Затем выполните:

```
uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: `http://localhost:8000`.

## Тестирование

Покрытие тестами:

```
---------- coverage: platform darwin, python 3.12.0-final-0 ----------
Name                               Stmts   Miss  Cover
------------------------------------------------------
app/__init__.py                        0      0   100%
app/db.py                             22      4    82%
app/init_data.py                       8      8     0%
app/main.py                           32      3    91%
app/models/__init__.py                 0      0   100%
app/models/item.py                     7      0   100%
app/models/transaction.py             16      0   100%
app/models/user.py                    10      0   100%
app/routes/__init__.py                 0      0   100%
app/routes/auth.py                    72     22    69%
app/routes/transaction.py             55     26    53%
app/schemas/__init__.py                0      0   100%
app/schemas/response.py               24      0   100%
app/schemas/transaction.py             4      0   100%
app/schemas/user.py                   11      0   100%
app/utils/__init__.py                  0      0   100%
app/utils/info_utils.py               35      7    80%
app/utils/redis_utils.py              34      6    82%
app/utils/security_utils.py           42      5    88%
app/utils/transaction_utils.py        15      4    73%
locustfile.py                         45     45     0%
tests/__init__.py                      0      0   100%
tests/conftest.py                     35      1    97%
tests/routes/__init__.py               0      0   100%
tests/routes/test_auth.py             72      0   100%
tests/routes/test_transaction.py      81      0   100%
------------------------------------------------------
TOTAL                                620    131    79%

=============================================== 17 passed, 30 warnings in 3.09s ================================================
```

Результаты нагрузочного тестирования:

```
Type     Name                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|--------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
POST     /api/auth                                       1272  404(31.76%) |  18046     234   60058  12000 |    1.19        0.38
POST     /api/buy/book                                   4416   427(9.67%) |   5104       2   60652    150 |    4.15        0.40
POST     /api/buy/cup                                    4295  453(10.55%) |   5110       2   61046    150 |    4.03        0.43
POST     /api/buy/pen                                    4280   414(9.67%) |   4658       2   61499    140 |    4.02        0.39
POST     /api/buy/powerbank                              4232   403(9.52%) |   4819       1   61163    150 |    3.97        0.38
POST     /api/buy/t-shirt                                4305  435(10.10%) |   4861       2   60109    160 |    4.04        0.41
GET      /api/info                                      21727  2033(9.36%) |   4590       1   62061    140 |   20.40        1.91
POST     /api/register                                   1694  331(19.54%) |   7810     252   33670   6300 |    1.59        0.31
POST     /api/sendCoin                                  21534  2047(9.51%) |   4663       1   61720    130 |   20.21        1.92
--------|--------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                     67755 6947(10.25%) |   5049       1   62061    160 |   63.60        6.52

Response time percentiles (approximated)
Type     Name                                                  50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
POST     /api/auth                                           12000  17000  40000  43000  48000  60000  60000  60000  60000  60000  60000   1272
POST     /api/buy/book                                         150    290    420    510  17000  43000  53000  60000  60000  61000  61000   4416
POST     /api/buy/cup                                          150    310    440    520  17000  44000  53000  60000  60000  61000  61000   4295
POST     /api/buy/pen                                          140    280    400    480  16000  42000  52000  60000  60000  61000  61000   4280
POST     /api/buy/powerbank                                    150    300    420    490  16000  43000  55000  60000  60000  61000  61000   4232
POST     /api/buy/t-shirt                                      160    300    430    500  16000  42000  51000  60000  60000  60000  60000   4305
GET      /api/info                                             140    280    390    480  16000  41000  50000  60000  60000  62000  62000  21727
POST     /api/register                                        6300  11000  12000  13000  16000  26000  31000  32000  34000  34000  34000   1694
POST     /api/sendCoin                                         130    260    370    470  16000  42000  50000  60000  60000  61000  62000  21534
--------|------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                            160    290    430    520  16000  42000  51000  60000  60000  61000  62000  67755
```

## API Документация

После запуска приложения, документация API будет доступна по адресам:

- **Swagger UI**: `http://localhost:8000/docs`


## Структура проекта

```
.
├── Dockerfile
├── README.md
├── alembic.ini
├── app
│   ├── __init__.py
│   ├── db.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── item.py
│   │   ├── transaction.py
│   │   └── user.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── transaction.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── response.py
│   │   ├── transaction.py
│   │   └── user.py
│   └── utils
│       ├── __init__.py
│       ├── info_utils.py
│       ├── redis_utils.py
│       ├── security_utils.py
│       └── transaction_utils.py
│
├── docker-compose.yml
├── locustfile.py
├── migrations
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│     
├── poetry.lock
├── pyproject.toml
├── ruff.toml
└── tests
    ├── __init__.py
    ├── conftest.py
    └── routes
        ├── __init__.py
        ├── test_auth.py
        └── test_transaction.py

```

## Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.
