# Makefile
.PHONY: help install dev clean test format lint publish-test publish all

# Python executable (works on both Windows and Unix)
PYTHON ?= python
VENV = .venv

ifeq ($(OS),Windows_NT)
    # Windows settings
    VENV_BIN = $(VENV)\Scripts
    PYTHON_CMD = $(VENV_BIN)\python.exe
    PIP = $(PYTHON_CMD) -m pip
    PYTEST = $(PYTHON_CMD) -m pytest
    BLACK = $(PYTHON_CMD) -m black
    ISORT = $(PYTHON_CMD) -m isort
    MYPY = $(PYTHON_CMD) -m mypy
    FLAKE8 = $(PYTHON_CMD) -m flake8
    # Windows commands with proper error handling
    define RMDIR
        if exist "$(1)" (del /s /q "$(1)" 2>nul & rd /s /q "$(1)" 2>nul || exit 0)
    endef
else
    # Unix settings
    VENV_BIN = $(VENV)/bin
    PYTHON_CMD = $(VENV_BIN)/python
    PIP = $(VENV_BIN)/pip
    PYTEST = $(VENV_BIN)/pytest
    BLACK = $(VENV_BIN)/black
    ISORT = $(VENV_BIN)/isort
    MYPY = $(VENV_BIN)/mypy
    FLAKE8 = $(VENV_BIN)/flake8
    # Unix commands
    RMDIR = rm -rf
endif

help:
	@echo "make install    - Install package and dependencies"
	@echo "make dev        - Install development dependencies"
	@echo "make clean      - Clean up build artifacts"
	@echo "make test       - Run tests"
	@echo "make format     - Format code"
	@echo "make lint       - Run linters"
	@echo "make publish-test - Build and publish to TestPyPI"
	@echo "make publish    - Build and publish to PyPI"
	@echo "make all        - Run clean install format lint test"

$(VENV)/pyvenv.cfg:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

install: $(VENV)/pyvenv.cfg
	$(PIP) install -r requirements.txt

dev: install
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

clean:
	$(call RMDIR,build)
	$(call RMDIR,dist)
	$(call RMDIR,*.egg-info)
	$(call RMDIR,__pycache__)
	$(call RMDIR,src\robotape\__pycache__)
	$(call RMDIR,src\robotape\*\__pycache__)
	$(call RMDIR,tests\__pycache__)
	$(call RMDIR,.pytest_cache)
	$(call RMDIR,.coverage)
	$(call RMDIR,htmlcov)
	$(call RMDIR,.mypy_cache)

test: dev
	$(PYTEST) tests/ --cov=robotape --cov-report=term-missing

format:
	$(BLACK) src/ tests/
	$(ISORT) src/ tests/

lint:
	$(MYPY) src/
	$(BLACK) --check src/ tests/
	$(FLAKE8) src/ tests/

install-poetry:
	$(PIP) install poetry

build: clean install-poetry
	$(PYTHON_CMD) -m poetry build

publish-test: build
ifeq ($(OS),Windows_NT)
	@echo "Please set POETRY_PYPI_TOKEN_TESTPYPI environment variable to your TestPyPI token"
	$(PYTHON_CMD) -m poetry config repositories.testpypi https://test.pypi.org/legacy/
	$(PYTHON_CMD) -m poetry publish -r testpypi
else
	@if [ -z "$(POETRY_PYPI_TOKEN_TESTPYPI)" ]; then \
		echo "Error: POETRY_PYPI_TOKEN_TESTPYPI is not set"; \
		echo "Please set it with: export POETRY_PYPI_TOKEN_TESTPYPI=your_token"; \
		exit 1; \
	fi
	$(PYTHON_CMD) -m poetry config repositories.testpypi https://test.pypi.org/legacy/
	$(PYTHON_CMD) -m poetry publish -r testpypi
endif

publish: build
ifeq ($(OS),Windows_NT)
	@echo "Please set POETRY_PYPI_TOKEN_PYPI environment variable to your PyPI token"
	$(PYTHON_CMD) -m poetry publish
else
	@if [ -z "$(POETRY_PYPI_TOKEN_PYPI)" ]; then \
		echo "Error: POETRY_PYPI_TOKEN_PYPI is not set"; \
		echo "Please set it with: export POETRY_PYPI_TOKEN_PYPI=your_token"; \
		exit 1; \
	fi
	$(PYTHON_CMD) -m poetry publish
endif

all: clean install format lint test