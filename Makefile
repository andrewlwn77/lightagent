# Makefile
.PHONY: help install dev clean test format lint all

# Python executable (works on both Windows and Unix)
PYTHON ?= python
VENV = .venv

ifeq ($(OS),Windows_NT)
    # Windows settings
    VENV_BIN = $(VENV)\Scripts
    PYTHON_CMD = $(VENV_BIN)\python.exe
    PIP = $(VENV_BIN)\pip.exe
    PYTEST = $(PYTHON_CMD) -m pytest
    BLACK = $(PYTHON_CMD) -m black
    ISORT = $(PYTHON_CMD) -m isort
    MYPY = $(PYTHON_CMD) -m mypy
    FLAKE8 = $(PYTHON_CMD) -m flake8
    # Windows commands
    RM = rd /s /q
    RMDIR = if exist "$(1)" $(RM) "$(1)"
    SEP = \\
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
    RM = rm -rf
    RMDIR = $(RM) $(1)
    SEP = /
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
	$(PYTHON_CMD) -m pip install --upgrade pip

install: $(VENV)/pyvenv.cfg
	$(PIP) install -e .

dev: install
	$(PIP) install -e ".[dev]"

clean:
	$(call RMDIR,build)
	$(call RMDIR,dist)
	$(call RMDIR,*.egg-info)
	$(call RMDIR,**/__pycache__)
	$(call RMDIR,.pytest_cache)
	$(call RMDIR,.coverage)
	$(call RMDIR,htmlcov)
	$(call RMDIR,.mypy_cache)

test:
	$(PYTEST) tests/ --cov=lightagent --cov-report=term-missing

format:
	$(BLACK) src/ tests/
	$(ISORT) src/ tests/

lint:
	$(MYPY) src/
	$(BLACK) --check src/ tests/
	$(FLAKE8) src/ tests/

all: clean install format lint test