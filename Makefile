lint:
	flake8 --ignore=E402,E501,E712 CTFd/ tests/

test:
	echo Running on `python -c 'import multiprocessing as m; print(m.cpu_count())'` cores
	pytest --disable-warnings -n `python -c 'import multiprocessing as m; print(m.cpu_count())'`
	bandit -r CTFd -x CTFd/uploads

serve:
	python serve.py

shell:
	python manage.py shell
