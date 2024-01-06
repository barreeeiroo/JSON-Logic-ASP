.PHONY: target format lint test test-integ pr build

target:
	@$(MAKE) pr

format:
	poetry run ruff format json_logic_asp/ tests/ tests_integ/

lint: format
	poetry run ruff check --fix json_logic_asp/ tests/ tests_integ/

lint-strict: format
	poetry run ruff check json_logic_asp/ tests/ tests_integ/

mypy:
	poetry run mypy --pretty --check-untyped-def json_logic_asp/ tests/ tests_integ/

test:
	poetry run pytest -c .pytest-tests.ini

test-integ: test
	poetry run pytest -c .pytest-tests_integ.ini -v

pr: lint mypy test-integ

build: pr
	poetry build
