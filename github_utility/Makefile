# Define variables
PYTHON_FILE_DIR := ./github_cli
REQUIREMENTS := $(PYTHON_FILE_DIR)/requirements.txt
VENV_DIR := .venv
PYTHON := python3
PIPREQS := $(VENV_DIR)/bin/pipreqs
PIP := $(VENV_DIR)/bin/pip
ACTIVATE := source $(VENV_DIR)/bin/activate

# Default target
all: $(VENV_DIR) $(REQUIREMENTS)
	@$(PIP) install -r $(REQUIREMENTS)

# Create virtual environment if it does not exist
$(VENV_DIR):
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV_DIR)
	@$(PIP) install --upgrade pip

# Generate requirements.txt using pipreqs
$(REQUIREMENTS): $(VENV_DIR)
	@if [ ! -f $(REQUIREMENTS) ]; then \
		echo "Generating $(REQUIREMENTS)..."; \
		$(PIP) install pipreqs; \
		$(PIPREQS) $(PYTHON_FILE_DIR) --force; \
	else \
		echo "$(REQUIREMENTS) already exists. Skipping generation."; \
	fi

# Clean up generated files
clean:
	rm -rf $(REQUIREMENTS) $(VENV_DIR)

# Install pipreqs in the virtual environment if not already installed
install-pipreqs: $(VENV_DIR)
	@$(PIP) install pipreqs
