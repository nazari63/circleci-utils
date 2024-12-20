.PHONY: setup clean run

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

setup: $(VENV)/bin/activate

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

clean:
	rm -rf $(VENV)
	find . -type f -name "github_actions_audit_*.csv" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +

run:
	$(PYTHON) github_actions_audit.py