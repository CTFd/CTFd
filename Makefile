lint:
	flake8 --ignore=E402,E501,E712,W503,E203 --exclude=CTFd/uploads CTFd/ tests/
	black --check --exclude=CTFd/uploads CTFd/**/*.py tests/**/*.py
	prettier --check 'CTFd/themes/**/*'

test:
	pytest --cov=CTFd --disable-warnings -n auto
	bandit -r CTFd -x CTFd/uploads

serve:
	python serve.py

shell:
	python manage.py shell
