lint:
	flake8 --ignore=E402,E501,E712,W503,E203 --exclude=CTFd/uploads CTFd/ migrations/ tests/
	yarn lint
	black --check --diff --exclude=CTFd/uploads --exclude=node_modules .
	prettier --check 'CTFd/themes/**/assets/**/*'
	prettier --check '**/*.md'

format:
	isort --skip=CTFd/uploads -rc CTFd/ tests/
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
	yarn verify

coverage:
	coverage html --show-contexts

serve:
	python serve.py

shell:
	python manage.py shell
