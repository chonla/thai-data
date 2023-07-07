build:
	python3 ./builder/build.py

prod:
	python3 ./builder/build.py -prod

install:
	pip3 install -r requirements.txt

test:
	pytest ./builder_tests

dtest:
	pytest -vv ./builder_tests

lint:
	python -m black . && python -m flake8 .