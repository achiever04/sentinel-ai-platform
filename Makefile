.PHONY: help setup install run-backend run-frontend run-all test clean

help:
	@echo "Sentinel AI Platform - Make Commands"
	@echo "===================================="
	@echo "setup          - Initial setup (install dependencies)"
	@echo "install        - Install Python and Node dependencies"
	@echo "run-backend    - Run backend server"
	@echo "run-frontend   - Run frontend server"
	@echo "run-all        - Run both backend and frontend"
	@echo "test           - Run tests"
	@echo "clean          - Clean generated files"
	@echo "docker-up      - Start with Docker Compose"
	@echo "docker-down    - Stop Docker containers"

setup:
	bash setup.sh

install:
	pip install -r requirements.txt
	cd frontend && npm install

run-backend:
	bash run_backend.sh

run-frontend:
	bash run_frontend.sh

run-all:
	bash run_backend.sh & bash run_frontend.sh

test:
	pytest tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf dist build *.egg-info

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f
