# 🚀 FastAPI SWAPI Importer

A fully Dockerized FastAPI application for importing and exposing Star Wars data from [SWAPI](https://swapi.dev) with SQLModel, async SQLAlchemy, and PostgreSQL.

---

## 📦 Features

* ✅ **FastAPI**
* 📄 **SQLModel** (Pydantic + SQLAlchemy) for schema & ORM models.
* 🧪 **Tested** with `pytest`, `httpx`, `asyncpg`, and `pytest-asyncio`.
* 🧱 **Docker + Docker Compose** with separate test and dev environments.
* 🔄 **Background worker** and data importer from SWAPI.
* 💠 **Migrations** using Alembic.
* 📊 **Test coverage** via `pytest-cov`.
* 🧹 **Linting + formatting** with `ruff`.

---

## 🚀 Quickstart

### 0. Prerequisites

Make sure the following are installed on your machine:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [`make`](https://www.gnu.org/software/make/) (included by default on most Unix systems)

### 1. Build and Start the App

```bash
make build
make start
```

### 2. Run Migrations

```bash
make alembic-upgrade
```

### 3. Import SWAPI Data [Optional]

```bash
make import-swapi
```

---

## 🧪 Running Tests

### Full test suite (Dockerized)

```bash
make test
```

### Run with coverage

```bash
make coverage
```

---

## 💃 Database Commands

### Reset database and re-import data

```bash
make reset-db
```

---

## 🧢 Migrations

* Initialize: `make alembic-init`
* Generate revision: `make alembic-revision`
* Apply latest: `make alembic-upgrade`
* Downgrade: `make alembic-downgrade`

---

## 🧰 Developer Tools

### Format & lint

```bash
make format
```

---

## 📁 Project Structure

```
.
├── core/                   # Main application code
│   ├── models/             # SQLModel models
│   ├── routes/             # Endpoints
│   ├── schemas/            # Pydantic schemas
│   ├── crud/               # Business logic
│   ├── crud/utils/         # Paginator
│   ├── database/           # DB session and settings
│   ├── services/swapi/     # SWAPI importers
│   └── tests/              # Pytest suite
│   └── main.py             # FastAPI app entry
│
├── scripts/
│   └── import_swapi.py     # CLI importer
├── alembic/                # DB migrations
├── docker-compose.yml
├── docker-compose.test.yml
├── Makefile                # Shortcut commands
└── .env                    # Environmet Variables
```

---

## 🧪 Test Strategy

* Test each model, schema, route, and CRUD method.
* Integration tests for importers.
* Coverage tracked with `pytest-cov`.

---

## 📌 Requirements

* Python 3.13+
* Docker & Docker Compose
* `make`

---

## 📬 API Example

```http
GET /api/characters/1/
GET /api/characters/?name=Luke
GET /api/starships/?page=2
GET /api/films/
POST /api/import/
```
## Swagger
```http
http://127.0.0.1:8000/docs#/
```
