# .PHONY tells Make these are commands, not files to create
.PHONY: lint test security docs clean pipeline prepare upload download install dev-setup

PYTHON = python
PACKAGES_DIR = packages
SHARED_DIR = shared

# Run all linting tools
lint:
	flake8 $(PACKAGES_DIR)/ $(SHARED_DIR)/
	pylint $(PACKAGES_DIR)/ $(SHARED_DIR)/
	mypy $(PACKAGES_DIR)/ $(SHARED_DIR)/

# Run tests with coverage reporting
test:
	pytest --cov=$(PACKAGES_DIR) --cov=$(SHARED_DIR) tests/

# Run security scanning tools
security:
	bandit -r $(PACKAGES_DIR)/ $(SHARED_DIR)/ -x tests/
	# safety scan ## you need a safety account for scan

# Generate documentation using Sphinx
docs:
	sphinx-build -b html docs/source/ docs/build/html

# Clean up temporary files and build artifacts
clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf docs/build
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Run the full pipeline
pipeline: prepare upload download

# Prepare batch input
prepare:
	PYTHONPATH=$$PYTHONPATH:. $(PYTHON) $(PACKAGES_DIR)/batch-prepare/src/batch_prepare_input.py

# Upload batches to OpenAI
upload:
	PYTHONPATH=$$PYTHONPATH:. $(PYTHON) $(PACKAGES_DIR)/batch-upload/src/batch_upload_input.py

# Download results
download:
	PYTHONPATH=$$PYTHONPATH:. $(PYTHON) $(PACKAGES_DIR)/batch-download/src/batch_download_result.py

# Install all dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Install development dependencies
dev-setup: install
	pip install pytest pytest-cov flake8 pylint mypy bandit safety sphinx sphinx-rtd-theme pre-commit
	pre-commit install
