.PHONY: target format lint test pr build

target:
	@$(MAKE) pr

format:
	poetry run ruff format json_logic_asp/ tests/

lint: format
	poetry run ruff check --fix json_logic_asp/ tests/

lint-strict: format
	poetry run ruff check json_logic_asp/ tests/

mypy:
	poetry run mypy --pretty --check-untyped-def json_logic_asp/ tests/

test:
	poetry run pytest

pr: lint mypy test

build: pr
	poetry build
