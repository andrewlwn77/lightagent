# Makefile
.PHONY: help install dev clean test format lint all

# Python executable (works on both Windows and Unix)
PYTHON ?= python
VENV = .venv
BIN = $(VENV)/Scripts
ifeq ($(OS),Windows_NT)
    VENV_BIN = $(BIN)
    # Windows needs different activation
    ACTIVATE = $(VENV_BIN)/activate.bat
else
    VENV_BIN = $(VENV)/bin
    ACTIVATE = . $(VENV_BIN)/activate
endif

help:
	@echo "make install    - Install package and dependencies"
	@echo "make dev        - Install development dependencies"
	@echo "make clean      - Clean up build artifacts"
	@echo "make test       - Run tests"
	@echo "make format     - Format code"
	@echo "make lint       - Run linters"
	@echo "make all        - Run clean install format lint test"

$(VENV)/pyvenv.cfg:
	$(PYTHON) -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade pip

install: $(VENV)/pyvenv.cfg
	$(VENV_BIN)/pip install -e .

dev: install
	$(VENV_BIN)/pip install -e ".[dev]"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf **/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache

test:
	$(VENV_BIN)/pytest tests/ --cov=lightagent --cov-report=term-missing

format:
	$(VENV_BIN)/black src/ tests/
	$(VENV_BIN)/isort src/ tests/

lint:
	$(VENV_BIN)/mypy src/
	$(VENV_BIN)/black --check src/ tests/
	$(VENV_BIN)/flake8 src/ tests/

all: clean install format lint test