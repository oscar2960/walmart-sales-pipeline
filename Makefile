.PHONY: help up down build test logs clean ps

help:
	@echo "Comandos disponibles:"
	@echo "  make up      -> Levanta PostgreSQL + App con Docker Compose"
	@echo "  make down    -> Detiene y elimina los contenedores"
	@echo "  make build   -> Reconstruye la imagen Docker de la app"
	@echo "  make test    -> Ejecuta la suite de pruebas dentro de un contenedor"
	@echo "  make logs    -> Muestra los logs en tiempo real"
	@echo "  make clean   -> Limpia contenedores, volúmenes y artefactos locales"
	@echo "  make ps      -> Lista los contenedores del proyecto"

up:
	docker compose up --build -d
	@echo "Esperando a que los servicios estén listos..."
	@sleep 3
	docker compose logs -f app

down:
	docker compose down -v --remove-orphans

build:
	docker compose build

test:
	docker compose up -d postgres
	docker compose run --rm -e DB_HOST=postgres app sh -c \
		"pip install -r requirements-dev.txt && pytest tests/ -v --cov=app"

logs:
	docker compose logs -f

clean:
	docker compose down -v --remove-orphans
	rm -rf venv __pycache__ .pytest_cache htmlcov .coverage reports

ps:
	docker compose ps
