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

.PHONY: docker_build
docker_build:
	@make docker_base_build
	@make docker_notebook_build

.PHONY: docker_base_build
docker_base_build: Dockerfile.base
	docker build -t minian-docker-base -f ./Dockerfile.base .

.PHONY: docker_notebook_build
docker_notebook_build: Docker.notebook
	docker build -t minian-docker-notebook -f ./Dockerfile.notebook .

.PHONY: docker_push
docker_push:
	@make docker_base_push
	@make docker_notebook_push

.PHONY: docker_base_push
docker_base_push:
	docker push velonica2227/minian-docker-base

.PHONY: docker_notebook_push
docker_notebook_push:
	docker push velonica2227/minian-docker-notebook
