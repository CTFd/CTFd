lint:
	ruff check --select E,F,W,B,C4,I --ignore E402,E501,E712,B904,B905,I001 --exclude=CTFd/uploads CTFd/ migrations/ tests/
	isort --profile=black --check-only --skip=CTFd/uploads --skip-glob **/node_modules CTFd/ tests/
	yarn --cwd CTFd/themes/admin lint
	black --check --diff --exclude=CTFd/uploads --exclude=node_modules .
	prettier --check 'CTFd/themes/*/assets/**/*'
	prettier --check '**/*.md'

format:
	isort --profile=black --skip=CTFd/uploads --skip-glob **/node_modules CTFd/ tests/
	black --exclude=CTFd/uploads --exclude=node_modules .
	prettier --write 'CTFd/themes/**/assets/**/*'
	prettier --write '**/*.md'

test:
	pytest -rf --cov=CTFd --cov-context=test --cov-report=xml \
		--ignore-glob="**/node_modules/" \
		--ignore=node_modules/ \
		-W ignore::sqlalchemy.exc.SADeprecationWarning \
		-W ignore::sqlalchemy.exc.SAWarning \
		-n auto
	bandit -r CTFd -x CTFd/uploads --skip B105,B322
	pipdeptree

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
