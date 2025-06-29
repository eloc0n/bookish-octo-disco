include .env
export $(shell sed 's/=.*//' .env)

# Check id docker-compose is available else use docker compose
ifeq (, $(shell which docker-compose))
    DC = docker compose
else
    DC = docker-compose
endif
APP_NAME=fastapi
UID = $(shell id -u)
TEST_PROJECT_NAME=swapi_test


# Format python files.
format:
	${DC} up --remove-orphans --no-deps -d $(APP_NAME)
	${DC} exec --user ${UID} $(APP_NAME) sh -c "ruff check --fix . && ruff format ."

# Build docker images.
build:
	${DC} build --pull

# Start project.
start:
	${DC} up --remove-orphans

alembic-init:
	$(DC) run --rm --no-deps $(APP_NAME) sh -c "alembic init alembic"

alembic-reset:
	@echo "Dropping alembic_version table..."
	$(DC) exec -T db psql -U $(POSTGRES_USER) -d $(POSTGRES_USER) -c "DROP TABLE IF EXISTS alembic_version;"

alembic-revision:
	make alembic-reset
	@read -p "Enter revision message: " msg; \
	$(DC) run --rm --no-deps $(APP_NAME) sh -c "alembic revision --autogenerate -m '$$msg'"

alembic-downgrade:
	@read -p "Enter downgrade revision: " msg; \
	$(DC) run --rm --no-deps $(APP_NAME) sh -c "alembic downgrade '$$msg'"

alembic-upgrade:
	$(DC) run --rm $(APP_NAME) sh -c "alembic upgrade head"

# Run the worker
worker:
	$(DC) run --rm $(APP_NAME) python service/consumer.py

# Run tests.
test-up:
	docker compose -f docker-compose.test.yml --project-name $(TEST_PROJECT_NAME) up -d

test-down:
	docker compose -f docker-compose.test.yml --project-name $(TEST_PROJECT_NAME) down -v

test:
	make test-up
	@echo "🔄 Waiting for test_db to become healthy..."
	@sleep 5 && until docker exec $$(docker ps -qf "name=$(TEST_PROJECT_NAME)-test_db") pg_isready -U postgres -d test_db; do sleep 1; done
	@echo "✅ Test DB is ready. Running tests..."
	docker compose -f docker-compose.test.yml --project-name $(TEST_PROJECT_NAME) exec test_runner sh -c "ENVIRONMENT=test pytest -s"
	make test-down


# Exec sh shell on fastapi container.
shell:
	${DC} run --user ${UID} --rm $(APP_NAME) sh

# run this command and then 
# psql -U postgres -d mydatabase
db-connect:
	docker exec --user=root -ti $(CONTAINER) /bin/sh

import-swapi:
	docker compose run --rm fastapi python scripts/import_swapi.py

reset-db:
	@echo "🧨 Dropping and recreating database..."
	$(DC) exec -T db psql -U $(POSTGRES_USER) -d $(POSTGRES_USER) -c "DROP DATABASE IF EXISTS $(POSTGRES_DB);"
	$(DC) exec -T db psql -U $(POSTGRES_USER) -d $(POSTGRES_USER) -c "CREATE DATABASE $(POSTGRES_DB);"
	@echo "📦 Applying migrations..."
	make alembic-upgrade
	@echo "🛰️  Reimporting SWAPI data..."
	make import-swapi

coverage:
	make test-up
	@echo "🔄 Waiting for test_db to become healthy..."
	@sleep 5 && until docker exec $$(docker ps -qf "name=$(TEST_PROJECT_NAME)-test_db") pg_isready -U postgres -d test_db; do sleep 1; done
	@echo "✅ Test DB is ready. Running coverage..."
	docker compose -f docker-compose.test.yml --project-name $(TEST_PROJECT_NAME) exec test_runner sh -c "ENVIRONMENT=test pytest --cov=core --cov-report=term-missing"
	make test-down