# Makefile for DaVinci Resolve Scripts
# Cross-platform support via Python installer

.PHONY: help install uninstall check lint format fix

help:
	@echo "Usage:"
	@echo "  make install    - Interactive installation (choose Free or Studio)"
	@echo "  make uninstall  - Remove all scripts"
	@echo "  make check      - Check Python and required libraries"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Run ruff formatter"
	@echo "  make fix        - Auto-fix linting issues"

install:
	@python3 scripts/install.py install

uninstall:
	@python3 scripts/install.py uninstall

check:
	@python3 scripts/install.py check

lint:
	@echo "Running ruff linter..."
	@uv run ruff check scripts/

format:
	@echo "Running ruff formatter..."
	@uv run ruff format scripts/

fix:
	@echo "Auto-fixing linting issues..."
	@uv run ruff check --fix scripts/
	@uv run ruff format scripts/
