# Makefile for DaVinci Resolve Scripts

# macOS path for DaVinci Resolve Utility scripts
# This is where scripts appear under Workspace > Scripts > Utility
INSTALL_DIR := $(HOME)/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility

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
	@echo "Select scripts to install:"
	@echo "  1) Free version (add_exif_frame_dv_lite.py)"
	@echo "  2) Studio version (add_exif_frame_dv.py)"
	@read -p "Enter choice [1-2]: " choice; \
	case "$$choice" in \
		1) SCRIPTS="scripts/add_exif_frame_dv_lite.py" ;; \
		2) SCRIPTS="scripts/add_exif_frame_dv.py" ;; \
		*) echo "Invalid choice"; exit 1 ;; \
	esac; \
	VENV_SITE_PACKAGES=$$(uv run python -c "import sys; print([p for p in sys.path if 'site-packages' in p][0] if any('site-packages' in p for p in sys.path) else '')" 2>/dev/null); \
	if [ -z "$$VENV_SITE_PACKAGES" ]; then \
		echo "ERROR: Could not detect .venv site-packages path."; \
		echo "Please run 'uv sync' first to create virtual environment."; \
		exit 1; \
	fi; \
	echo "Using site-packages: $$VENV_SITE_PACKAGES"; \
	mkdir -p "$(INSTALL_DIR)"; \
	for script in $$SCRIPTS; do \
		sed 's|^VENV_PATH = "{{VENV_PATH}}"$$|VENV_PATH = "'"$$VENV_SITE_PACKAGES"'"|' "$$script" > "$(INSTALL_DIR)/$$(basename $$script)"; \
		echo "Installed: $$script"; \
	done
	@echo "Installation complete. Please restart DaVinci Resolve if scripts do not appear."

uninstall:
	@rm -f "$(INSTALL_DIR)/add_exif_frame_dv.py"
	@rm -f "$(INSTALL_DIR)/add_exif_frame_dv_lite.py"
	@echo "Removed scripts from $(INSTALL_DIR)"

check:
	@echo "=== Environment Check ==="
	@echo ""
	@echo "1. Checking Python3 and uv..."
	@if command -v python3 >/dev/null 2>&1; then \
		echo "✓ Python3 found: $$(python3 --version)"; \
	else \
		echo "✗ Python3 not found"; \
		exit 1; \
	fi
	@if command -v uv >/dev/null 2>&1; then \
		echo "✓ uv found: $$(uv --version)"; \
	else \
		echo "✗ uv not found (required for installation)"; \
		exit 1; \
	fi
	@echo ""
	@echo "2. Checking virtual environment and libraries..."
	@SITE_PACKAGES=$$(uv run python -c "import sys; print([p for p in sys.path if 'site-packages' in p][0] if any('site-packages' in p for p in sys.path) else '')" 2>/dev/null); \
	if [ -z "$$SITE_PACKAGES" ]; then \
		echo "✗ Virtual environment not found"; \
		echo "   Please run 'uv sync' to create it"; \
		exit 1; \
	fi; \
	echo "✓ Virtual environment found: $$SITE_PACKAGES"; \
	echo ""; \
	for lib in PIL rawpy exifread; do \
		if uv run python -c "import $$lib" 2>/dev/null; then \
			echo "✓ $$lib installed"; \
		else \
			echo "✗ $$lib not found (run 'uv sync')"; \
		fi; \
	done
	@echo ""
	@echo "3. Checking install directory..."
	@if [ -d "$(INSTALL_DIR)" ]; then \
		echo "✓ Install directory exists: $(INSTALL_DIR)"; \
	else \
		echo "! Install directory does not exist (will be created on install)"; \
	fi
	@echo ""
	@echo "=== Check Complete ==="

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
