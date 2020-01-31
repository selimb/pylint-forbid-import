packages = pylint_forbid_import tests

.PHONY: lint
lint:
	poetry run black --check $(packages)
	poetry run isort --check-only -rc $(packages)
	poetry run pylint $(packages)

.PHONY: format
format:
	poetry run black $(packages)
	poetry run isort -rc $(packages)

.PHONY: mypy
mypy:
	poetry run mypy $(packages)

.PHONY: test
test:
	poetry run pytest -vv
