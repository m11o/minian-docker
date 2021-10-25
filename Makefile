clean:
	rm -rf dist/

prepare_build:
	python3 -m pip install --upgrade twine wheel

build: clean prepare_build
	python3 setup.py sdist bdist_wheel

upload_test: prepare_build
	python3 -m twine upload --repository testpypi dist/*

upload: prepare_build
	python3 -m twine upload dist/*
