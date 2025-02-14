export MODELS_DIR := $(shell realpath ./models)

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

## run load test
.PHONY: load-test
load-test:
	locust -f ./tests/load/test_generate_api.py --host http://localhost:30000

## build docker image
.PHONY: image
image:
	docker build . -t qlik-llm-service:latest

## run service
.PHONY: run-local
run-local:
	python ./app/main.py

## run service image
.PHONY: run-image
run-image:
	docker run --rm -it  -p 8000:8000 -v "./models:/app/models" --name qlik-llm-service qlik-llm-service:latest

## generate service manifest 
.PHONY: helm-template
helm-template:
	helm template qlik-llm ./helm/qlik-llm-service --set volumes.modelsVolume.path=$(MODELS_DIR)

## install service in dev environment
.PHONY: helm-install-dev
helm-install-dev:
	helm install qlik-llm ./helm/qlik-llm-service -f ./helm/qlik-llm-service/values/dev-values.yaml --set volumes.modelsVolume.path=$(MODELS_DIR)

## install service in prod environment
.PHONY: helm-install-prod
helm-install-prod:
	helm install qlik-llm ./helm/qlik-llm-service -f ./helm/qlik-llm-service/values/prod-values.yaml

## upgrade service in dev environment
.PHONY: helm-upgrade-dev 
helm-upgrade-dev:
	helm upgrade qlik-llm ./helm/qlik-llm-service -f ./helm/qlik-llm-service/values/dev-values.yaml --set volumes.modelsVolume.path=$(MODELS_DIR)

## upgrade service in prod environment
.PHONY: helm-upgrade-prod
helm-upgrade-prod:
	helm upgrade qlik-llm ./helm/qlik-llm-service -f ./helm/qlik-llm-service/values/prod-values.yaml

## delete service deployment
.PHONY: helm-delete
helm-delete:
	helm delete qlik-llm 

## service status
.PHONY: helm-status
helm-status:
	helm status qlik-llm