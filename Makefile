# Build package, uncompressed
build:
	python3 ./builder/build.py -log=debug

# Build package, compressed
prod:
	python3 ./builder/build.py -prod -log=info

# Install builder's dependencies
install:
	pip3 install -r requirements.txt

# Test the builder
test:
	pytest ./builder_tests

# Test the builder with detailed log
dtest:
	pytest -vv ./builder_tests

# Lint and format files
lint:
	python -m black . && python -m flake8 .

# Check if there any updated data version
check:
	python ./builder/build.py -check