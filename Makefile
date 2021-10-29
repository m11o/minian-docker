.PHONY: clean
clean:
	rm -rf dist/

.PHONY: prepare_build
prepare_build:
	python3 -m pip install --upgrade twine wheel

.PHONY: build
build: clean prepare_build
	python3 setup.py sdist bdist_wheel

.PHONY: upload_test
upload_test: prepare_build
	python3 -m twine upload --repository testpypi dist/*

.PHONY: upload
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

base_docker_image_id = $(shell docker images --format '{{.ID}}' minian-docker-base)
.PHONY: docker_base_push
docker_base_push:
	docker tag $(base_docker_image_id) velonica2227/minian-docker-base
	docker push velonica2227/minian-docker-base:latest

notebook_docker_image_id = $(shell docker images --format '{{.ID}}' minian-docker-notebook)
.PHONY: docker_notebook_push
docker_notebook_push:
	docker tag $(notebook_docker_image_id) velonica2227/minian-docker-notebook
	docker push velonica2227/minian-docker-notebook:latest
