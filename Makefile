lint:
	flake8 \
		--ignore=E402,E501,E712,W503,E203 \
		--exclude=CTFd/uploads \
		CTFd/ tests/
	black \
		--check \
		--exclude=CTFd/uploads \
		CTFd/**/*.py tests/**/*.py
	prettier --check 'CTFd/themes/**/*'

test:
	pytest \
		--driver Chrome \
		--needle-engine imagemagick \
		--needle-viewport-size "1920 x 1080" \
		--needle-cleanup-on-success \
		--cov=CTFd \
		--disable-warnings \
		-n auto
	bandit -r CTFd -x CTFd/uploads

screens:
	pytest \
		--driver Chrome \
		--needle-save-baseline \
		--needle-viewport-size "1920 x 1080" \
		--needle-engine imagemagick \
		tests/test_screens.py

serve:
	python serve.py

shell:
	python manage.py shell
