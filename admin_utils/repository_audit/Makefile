.PHONY: setup clean run run-single lint test

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Default organization from environment or prompt
ORG ?= $(GITHUB_ORG)
# Optional repository name
REPO ?= 

setup: $(VENV)/bin/activate

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Clean up all generated files and virtual environment
clean:
	rm -rf $(VENV)
	find . -type f -name "github_actions_audit_*.csv" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run audit for all repositories in organization
run:
ifdef ORG
	$(PYTHON) github_actions_audit.py --org $(ORG)
else
	@echo "Error: ORG is not set. Use 'make run ORG=your-org-name'"
endif

# Run audit for a single repository
run-single:
ifdef REPO
ifdef ORG
	$(PYTHON) github_actions_audit.py --org $(ORG) --repo $(REPO)
else
	@echo "Error: ORG is not set. Use 'make run-single ORG=your-org-name REPO=repo-name'"
endif
else
	@echo "Error: REPO is not set. Use 'make run-single ORG=your-org-name REPO=repo-name'"
endif

# Add linting
lint:
	$(PYTHON) -m flake8 github_actions_audit.py

# Install dev dependencies (for lint and test)
dev-setup: setup
	$(PIP) install flake8 pytest