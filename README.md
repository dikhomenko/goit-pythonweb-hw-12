# goit-pythonweb-hw-10

# Docker environment

## .env

place .env file in 'src'

## run docker-compose

docker-compose up --build or docker-compose --env-file ./src/.env up --build --force-recreate

## run migrations

docker-compose exec web poetry run alembic --config=src/alembic.ini upgrade head

## verify DB

docker-compose exec postgres_hw10 psql -U postgres -d hw10 -c "\dt"

docker-compose up --build -d >> detached mode
docker-compose logs -f >> view logs

## Swagger is available by following url

http://localhost:8000/docs

# Local

## Swagger is available by following url

http://127.0.0.1:8000/docs

## spin up Docker and Postgres

docker run --name my_postgres_task -e POSTGRES_PASSWORD=567234 -p 5432:5432 -d postgres
docker exec -it my_postgres_task psql -U postgres
CREATE DATABASE my_postgres_task_08;
\q

docker exec -it my_postgres_task psql -U postgres -c "\l"
docker exec -it my_postgres_task psql -U postgres -d my_postgres_task_08 -c "\dt"

## run migrations

docker-compose exec web poetry run alembic --config=src/alembic.ini upgrade head

## alembic

alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

## run application

from src >> .\venv\Scripts\activate
uvicorn app.main:app --reload // or we could set reload=true

# Re-set password

/request-password-reset and follow the linf from the email
submit reset_password_form.html
make actual /reset-password

# Run tests

cd src

.\venv\Scripts\activate

## for integration set of tests Redis is expected to be spun up

pytest -v tests/integration/routers/test_users_router.py
pytest -v tests/integration/routers/test_contacts_router.py
pytest -v tests/integration/routers/test_auth_router.py

## for unit tests Redis is mocked

pytest -v tests/unit/services/test_user_service.py
pytest -v tests/unit/services/test_contact_service.py
pytest -v tests/unit/services/test_jwt_manager.py

pytest -v tests/unit/repositories/test_contacts_repository.py
pytest -v tests/unit/repositories/test_users_repository.py

pytest --cache-clear

pytest --cov=src tests/ --cov-report=html
pytest --cov=src tests/ --cov-report=term-missing
