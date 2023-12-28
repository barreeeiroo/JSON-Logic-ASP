.PHONY: target format lint test pr build security-baseline complexity-baseline release

target:
	@$(MAKE) pr

format:
	poetry run ruff format json_logic_asp/ tests/

lint: format
	poetry run ruff check --fix json_logic_asp/ tests/

lint-strict: format
	poetry run ruff check json_logic_asp/ tests/

mypy:
	poetry run mypy --pretty json_logic_asp/ tests/

test:
	poetry run pytest

security-baseline:
	poetry run bandit -r json_logic_asp/

complexity-baseline:
	$(info Maintenability index)
	poetry run radon mi json_logic_asp/
	$(info Cyclomatic complexity index)
	poetry run xenon --max-absolute C --max-modules B --max-average A json_logic_asp/

pr: lint mypy test security-baseline complexity-baseline

build: pr
	poetry build
