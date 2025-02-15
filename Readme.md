# LLM Microservice

A text generation service based on language models from https://huggingface.co/

## Prerequisites

- Python Python 3.13.2+
- Docker Desktop with Kubernetes enabled
- Helm
- kubectl

If you don't use kubernetes on docker desktop, change context to kubectl to docker-desktop

```
kubectl config use-context docker-desktop
```

## Setup virtual environment

```
python3 -m venv myenv
source myenv/bin/activate  
pip install pytest locust httpx
pip install -r requirements.txt
```

## Download language models

In your venv terminal run below command

```
make download-model-distilgpt2
```

## Run unit tests

In your venv terminal run below command

```
make unit
```

## Run integration tests

In your venv terminal run below command

```
make integration
```

## Run all tests

In your venv terminal run below command

```
make test-all
```

## Run service locally

In your venv terminal run below command

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

Sample output of load test

```
Successful response for input: According to the new amendment, the rights of the accused include . Time: 24295.14ms
Successful response for input: In the year 1789, during the French Revolution, . Time: 28058.04ms
Successful response for input: Once upon a time, in a galaxy far away . Time: 43286.28ms
Successful response for input: In a world where magic is forbidden, a young wizard must . Time: 24703.93ms
Successful response for input: As a grumpy old man, I would say . Time: 29933.46ms
Successful response for input: Once upon a time, in a galaxy far away . Time: 45944.39ms
Successful response for input: Thank you for contacting customer support. How can I assist you with your . Time: 23491.65ms
```

You may check the logs of each pod to ensure the service is load balancing as expected

```
kubectl logs -f qlik-llm-service-<pod_id>
```

