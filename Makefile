export MODEL_DIR_PATH := $(shell realpath ./models/distilgpt2)

## download gpt2 LLM from https://huggingface.co/
.PHONY: download-model-gpt2
download-model-gpt2:
	python ./scripts/model_download.py --model-name openai-community/gpt2

## download distilgpt2 LLM from https://huggingface.co/
.PHONY: download-model-distilgpt2
download-model-distilgpt2:
	python ./scripts/model_download.py --model-name distilbert/distilgpt2

## run unit test
.PHONY: unit
unit:
	PYTHONPATH=./app pytest tests/unit

## run integration test - browse http://0.0.0.0:8089 to configure tests
.PHONY: integration
integration:
	PYTHONPATH=./app pytest tests/integration

## run unit test and integration tests
.PHONY: test-all
test-all:
	PYTHONPATH=./app pytest tests/unit tests/integration

## run service
.PHONY: run-local
run-local:
	python ./app/main.py

## build docker image
.PHONY: image
image:
	docker build . -t llm-microservice:latest

## run service image
.PHONY: run-image
run-image:
	docker run --rm -it  -p 8000:8000 -v "./models/distilgpt2:/app/model" --name llm-microservice llm-microservice:latest

## generate service manifest
.PHONY: helm-template
helm-template:
	helm template llm ./helm/llm-microservice --set volumes.modelVolume.path=$(MODEL_DIR_PATH)

## install service in dev environment
.PHONY: helm-install-dev
helm-install-dev:
	helm install llm ./helm/llm-microservice -f ./helm/llm-microservice/values/dev-values.yaml --set volumes.modelVolume.path=$(MODEL_DIR_PATH)

## install service in prod environment
.PHONY: helm-install-prod
helm-install-prod:
	helm install llm ./helm/llm-microservice -f ./helm/llm-microservice/values/prod-values.yaml

## upgrade service in dev environment
.PHONY: helm-upgrade-dev
helm-upgrade-dev:
	helm upgrade llm ./helm/llm-microservice -f ./helm/llm-microservice/values/dev-values.yaml --set volumes.modelVolume.path=$(MODEL_DIR_PATH)

## upgrade service in prod environment
.PHONY: helm-upgrade-prod
helm-upgrade-prod:
	helm upgrade llm ./helm/llm-microservice -f ./helm/llm-microservice/values/prod-values.yaml

## delete service deployment
.PHONY: helm-delete
helm-delete:
	helm delete llm

## service status
.PHONY: helm-status
helm-status:
	helm status llm

## run load test
.PHONY: load-test
load-test:
	locust -f ./tests/load/test_generate_api.py --host http://localhost:30000
