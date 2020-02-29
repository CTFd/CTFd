lint:
	flake8 --ignore=E402,E501,E712,W503,E203,I002 --exclude=CTFd/uploads CTFd/ migrations/ tests/
	black --check --exclude=CTFd/uploads --exclude=node_modules .
	prettier --check 'CTFd/themes/**/assets/**/*'

format:
	black --exclude=CTFd/uploads --exclude=node_modules .
	prettier --write 'CTFd/themes/**/assets/**/*'

test:
	pytest --cov=CTFd --ignore=node_modules/ --disable-warnings -n auto
	bandit -r CTFd -x CTFd/uploads
	yarn verify

serve:
	python serve.py

shell:
	python manage.py shell
