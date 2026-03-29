.PHONY: install run pipeline docker-build docker-run docker-pipeline clean lint help

help:
	@echo ""
	@echo "  make install          Install Python dependencies"
	@echo "  make run              Launch Jupyter notebook server"
	@echo "  make pipeline         Run full headless pipeline"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-run       Run Jupyter inside Docker"
	@echo "  make docker-pipeline  Run headless pipeline inside Docker"
	@echo "  make clean            Remove generated files"
	@echo "  make lint             Check code style"
	@echo ""

install:
	pip install -r requirements.txt

run:
	jupyter notebook --notebook-dir=notebooks

pipeline:
	python run_pipeline.py

docker-build:
	docker build -t primetrade-analysis .

docker-run:
	docker compose up notebook

docker-pipeline:
	docker compose --profile pipeline up pipeline

clean:
	rm -rf charts/* outputs/* data/processed/*
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

lint:
	pip install flake8 --quiet
	flake8 src/ run_pipeline.py --max-line-length=100 --ignore=E501,W503
