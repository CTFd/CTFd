PRETTIER := CTFd/themes/admin/node_modules/.bin/prettier

lint:
	ruff check CTFd/ migrations/ tests/
	ruff format --check --diff .
	yarn --cwd CTFd/themes/admin lint
	yarn --cwd CTFd/themes/core lint
	$(PRETTIER) --check '**/*.md'

format:
	ruff check --select I --fix CTFd/ migrations/ tests/
	ruff format .
	yarn --cwd CTFd/themes/admin format
	yarn --cwd CTFd/themes/core format
	$(PRETTIER) --write '**/*.md'

# requirements.txt is generated from uv.lock for consumers that install with
# pip. uv.lock is the source of truth - edit pyproject.toml and re-run this.
requirements:
	uv export --frozen --no-dev --no-hashes --no-emit-project --output-file requirements.txt

test:
	pytest -rf --cov=CTFd --cov-context=test --cov-report=xml \
		--ignore-glob="**/node_modules/" \
		--ignore=node_modules/ \
		-W ignore::sqlalchemy.exc.SADeprecationWarning \
		-W ignore::sqlalchemy.exc.SAWarning \
		-n auto

coverage:
	coverage html --show-contexts

serve:
	python serve.py

shell:
	python manage.py shell

translations-init:
	# make translations-init lang=af
	pybabel init -i messages.pot -d CTFd/translations -l $(lang)

translations-extract:
	pybabel extract -F babel.cfg -k lazy_gettext -k _l -o messages.pot .

translations-update:
	pybabel update --ignore-obsolete -i messages.pot -d CTFd/translations

translations-compile:
	pybabel compile -f -d CTFd/translations

translations-lint:
	dennis-cmd lint CTFd/translations
