lint:
	flake8 --ignore=E402,E501,E712 CTFd/ tests/

test:
	pytest --disable-warnings -n auto
	bandit -r CTFd -x CTFd/uploads

serve:
	python serve.py

shell:
	python manage.py shell
