# LLM Microservice

A text generation service based on language models from https://huggingface.co/

## Prerequisites

- Python Python 3.13+
- Docker Desktop with Kubernetes enabled
- Helm
- kubectl

If you don't use kubernetes on docker desktop, change context of kubectl to docker-desktop

```
kubectl config use-context docker-desktop
```

## Setup virtual environment

Start a virtual environment terminal and install project dependencies

```
python3 -m venv myenv
source myenv/bin/activate  
pip install pytest locust httpx
pip install -r requirements.txt
```

## Download language models

In your virtual environment termina terminal run below command

```
make download-model-distilgpt2
```

## Run unit tests

In your virtual environment termina terminal run below command

```
make unit
```

## Run integration tests

In your virtual environment termina terminal run below command

```
make integration
```

## Run all tests

In your virtual environment termina terminal run below command

```
make test-all
```

## Run service locally

In your virtual environment termina terminal run below command

```
make run-local
```

See below log line to ensure language model is loaded

```
Model and tokenizer successfully loaded from /path/to/directory/of/language/model
```

Prompt the /generate api to generate some text

```
curl http://localhost:8000/generate -X POST \
	-H 'Content-Type: application/json' \
	-d '{"prompt":"Once upon a time in a land far away "}'
```

The output should include generated text and response time

```
{
  "generated_text": "Once upon a time in a land far away The Lord of the Rings: The Fellowship, I was told that my father had been killed by an evil wizard.\nI remember seeing him as he looked down on me and said to myself “What are you doing?” He asked if",
  "response_time": 2.16
}
```

## Build service as docker image

```
make image
```

The image is tagged qlik-llm-service:latest

## Run service as docker container

```
make run-image
```

The container name is qlik-llm-service

## Run service on kubernetes

```
make helm-install-dev
```

Should see output

```
NAME: qlik-llm
LAST DEPLOYED: Fri Feb 14 19:13:02 2025
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

Too inspect all kubernetes resources created by the helm package

```
kubectl get all -l app=qlik-llm-service
```

You should see 1 deployment, service, replicaset, configmap, horizontal pod autoscaler, and 3 pods

```
NAME                                    READY   STATUS    RESTARTS   AGE
pod/qlik-llm-service-6f49fbb7c9-5nlmc   1/1     Running   0          56s
pod/qlik-llm-service-6f49fbb7c9-f85bh   1/1     Running   0          116s
pod/qlik-llm-service-6f49fbb7c9-h9ssh   1/1     Running   0          56s

NAME                       TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)        AGE
service/qlik-llm-service   NodePort   10.100.167.144   <none>        80:30000/TCP   116s

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/qlik-llm-service   3/3     3            3           116s

NAME                                          DESIRED   CURRENT   READY   AGE
replicaset.apps/qlik-llm-service-6f49fbb7c9   3         3         3       116s

NAME                                               REFERENCE                     TARGETS              MINPODS   MAXPODS   REPLICAS
AGE
horizontalpodautoscaler.autoscaling/qlik-llm-hpa   Deployment/qlik-llm-service   cpu: <unknown>/50%   3         5         1
116s
```

The service is exposed on port 30000

Prompt the /generate api on port 30000 to generate some text

```
curl http://localhost:30000/generate -X POST \
	-H 'Content-Type: application/json' \
	-d '{"prompt":"Once upon a time in a land far away "}'
```

## Run load tests

In your venv terminal run below command

```
make load-test
```

Browse to http://0.0.0.0:8089

Start a load test with 50 concurrent users for 5 minutes.

Run below command to find the service automatically scales to 5 pods 

```
kubectl get pods -l app=qlik-llm-service
```

If the service doesn't scale immediately restart the load-test with higher number of concurrent users. 

You may check the logs of each pod to ensure the service is load balancing as expected

```
kubectl logs -f qlik-llm-service-<pod_id>
```

## Service configuration on kubernetes

The default service configuration parameters are defined in ./helm/qlik-llm-service/values.yaml

They allow configuring 
- service image version
- cpu and memory allocation of service pods
- language model parameters - max length, max new tokens, temperature, top_k, top_p, repetition_penalty
- source directory of laguage models
- directory name of language model
- pod auto scaling
- service port

The dev environment service configuration parameters are defined in ./helm/qlik-llm-service/values/dev-values.yaml

The prod environment service configuration parameters are defined in ./helm/qlik-llm-service/values/prod-values.yaml

### Update service configuration on kubernetes

To update configuration of an existing service in dev environment

```
make helm-upgrade-dev
```

Note the revision of the service has incremented

```
Release "qlik-llm" has been upgraded. Happy Helming!
NAME: qlik-llm
LAST DEPLOYED: Fri Feb 14 20:20:02 2025
NAMESPACE: default
STATUS: deployed
REVISION: 2
TEST SUITE: None
```

### Check status of service on kubernetes

```
make helm-status
```

## Stop service on kubernetes

To stop the service and release all resource

```
make helm-delete
```