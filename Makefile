.PHONY: help clean clean-build clean-pyc clean-test lint test test-all coverage docs install dev-install dist publish publish-test check bump-patch bump-minor bump-major

help:
	@echo "Chandojñānam - Sanskrit Meter Identification Library"
	@echo ""
	@echo "Available commands:"
	@echo "  make install        Install the package"
	@echo "  make dev-install    Install package in development mode with dev dependencies"
	@echo "  make test           Run tests (requires package installed)"
	@echo "  make coverage       Run tests with coverage report"
	@echo "  make lint           Check code style with flake8"
	@echo "  make format         Format code with black"
	@echo "  make type-check     Run mypy type checking"
	@echo "  make check          Run all checks (format, lint, test)"
	@echo "  make check-all      Run all checks including type-check"
	@echo "  make docs           Build documentation"
	@echo "  make docs-serve     Build and serve documentation locally"
	@echo "  make clean          Remove all build, test, coverage and Python artifacts"
	@echo "  make dist           Build source and wheel distributions"
	@echo "  make publish-test   Publish to Test PyPI (dry run)"
	@echo "  make publish        Publish to PyPI (production)"
	@echo "  make bump-patch     Bump patch version (0.1.0 -> 0.1.1)"
	@echo "  make bump-minor     Bump minor version (0.1.0 -> 0.2.0)"
	@echo "  make bump-major     Bump major version (0.1.0 -> 1.0.0)"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -f .coverage
	rm -f coverage.xml

lint:
	flake8 chanda tests

format:
	black chanda tests examples

format-check:
	black --check chanda tests examples

type-check:
	mypy chanda

test:
	pytest

test-all:
	pytest --verbose

coverage:
	pytest --cov=chanda --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

docs:
	cd docs && $(MAKE) html
	@echo "Documentation built in docs/_build/html/index.html"

docs-serve: docs
	@echo "Serving documentation at http://localhost:8000"
	cd docs/_build/html && python -m http.server 8000

docs-clean:
	cd docs && $(MAKE) clean

install:
	pip install .

dev-install:
	pip install -e ".[dev,docs]"

dist: clean
	python -m build
	ls -lh dist

publish-test: dist
	python -m twine upload --repository testpypi dist/*

publish: dist
	python -m twine upload dist/*

# Quick test of the CLI
test-cli:
	chanda "को न्वस्मिन् साम्प्रतं लोके गुणवान् कश्च वीर्यवान्"

# Run all checks before committing
check: format-check lint test
	@echo "All checks passed!"

# Run all checks including optional type-check
check-all: format-check lint type-check test
	@echo "All checks passed!"

# Version bumping with bump2version
bump-patch:
	bump2version patch

bump-minor:
	bump2version minor

bump-major:
	bump2version major
