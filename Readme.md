# LLM Microservice

A text generation service based on language models from https://huggingface.co/

## Prerequisites

- Python Python 3.13+
- Docker Desktop with Kubernetes enabled
- Helm
- kubectl

If you don't use kubernetes on docker desktop, change context of kubectl to docker-desktop

```bash
kubectl config use-context docker-desktop
```

## Setup virtual environment

Start a virtual environment terminal and install project dependencies

```bash
python3 -m venv myenv
source myenv/bin/activate  
pip install pytest locust httpx pytest-asyncio -r requirements.txt
```

## Download language models

In your virtual environment terminal run below command

```bash
make download-model-distilgpt2
```

## Run unit tests

In your virtual environment terminal run below command

```bash
make unit
```

## Run integration tests

In your virtual environment terminal run below command

```bash
make integration
```

## Run all tests

In your virtual environment terminal run below command

```bash
make test-all
```

## Run service locally

In your virtual environment terminal run below command

```bash
make run-local
```

See below log line to ensure language model is loaded

```
Model and tokenizer successfully loaded from /path/to/directory/of/language/model on device cpu
```

Prompt the /generate api to generate some text

```bash
curl http://localhost:8000/generate -X POST \
	-H 'Content-Type: application/json' \
	-d '{"prompt":"Once upon a time in a land far away "}'
```

The output should include generated text and response time

```json
{
  "generated_text": "Once upon a time in a land far away The Lord of the Rings: The Fellowship, I was told that my father had been killed by an evil wizard.\nI remember seeing him as he looked down on me and said to myself “What are you doing?” He asked if",
  "response_time": 2.16
}
```

### Access API docs

Browse to http://localhost:8000/docs

## Build service as docker image

```bash
make image
```

The image is tagged qlik-llm-service:latest

## Run service as docker container

```bash
make run-image
```

The container name is qlik-llm-service

## Run service on kubernetes

```bash
make helm-install-dev
```

The status of the service should be deployed

```bash
NAME: qlik-llm
LAST DEPLOYED: Fri Feb 14 19:13:02 2025
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

Too inspect all kubernetes resources created by the helm package

```bash
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

```bash
curl http://localhost:30000/generate -X POST \
	-H 'Content-Type: application/json' \
	-d '{"prompt":"Once upon a time in a land far away "}'
```

## Run load tests

In your venv terminal run below command

```bash
make load-test
```

Browse to http://0.0.0.0:8089

Start a load test with 100 concurrent users for 5 minutes. 
Your docker desktop must be allocated 6 CPU and 6 GB memory for such setup.
If not, test with lower concurrent users.

Run below command to find the service automatically scales out to 5 pods 

```bash
kubectl get pods -l app=qlik-llm-service
```

If the service doesn't scale out immediately restart the load-test with higher number of concurrent users. 

You may check the logs of each pod to ensure the service is load balancing as expected

```bash
kubectl logs -f qlik-llm-service-<pod_id>
```

Check the resource consumption of service pods 

```bash
kubectl top pods -l app=qlik-llm-service
```

Notice resource consumption reaches peak capacity for 100 concurrent users.

```
qlik-llm-service-568746bb8c-7f2cm   868m         772Mi
qlik-llm-service-568746bb8c-g46hl   885m         877Mi
qlik-llm-service-568746bb8c-jmgfs   855m         826Mi
qlik-llm-service-568746bb8c-lrqh7   874m         879Mi
qlik-llm-service-568746bb8c-xbwrt   882m         878Mi
```

The service should scale in back to 3 pods after the load test completes

## Service configuration on kubernetes

The default service configuration parameters are defined in ./helm/qlik-llm-service/values.yaml

They allow configuring 
- service image version
- cpu and memory allocation of service pods
- language model parameters - max length, max new tokens, temperature, top_k, top_p, repetition_penalty
- directory path of of laguage model
- pod auto scaling
- service port

The dev environment service configuration parameters are defined in ./helm/qlik-llm-service/values/dev-values.yaml

For e.g to change the language model used by the service to gpt.
First download the language model to models directory in the project root.

```bash
make download-model-gpt2
```

In dev-values.yaml set path of gpt2 model

```yaml
volumes:
  modelVolume:
    path: /set/to/directory/of/gpt2/model/in/dev
```

The prod environment service configuration parameters are defined in ./helm/qlik-llm-service/values/prod-values.yaml

### Update service configuration on kubernetes

To apply service configuration changes in dev environment

```bash
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

To apply configuration changes in prod environment

```bash
make helm-upgrade-prod
```

### Check status of service on kubernetes

```bash
make helm-status
```

## Stop service on kubernetes

To stop the service and release all resource

```bash
make helm-delete
```

## Troubleshooting load test

If pods are restarting check if service health check is failing due to request timeout

```bash
kubectl get events -o jsonpath='{range .items[*]}{.involvedObject.kind}{"\t"}{.involvedObject.name}{"\t"}{.reason}{"\t"}{.message}{"\n"}{end}' | grep -E 'Probe|Liveness'
```

```
Pod	qlik-llm-service-79ff47b6f4-d9n7q	Unhealthy	Liveness probe failed: Get "http://10.1.1.32:8000/health": context deadline exceeded (Client.Timeout exceeded while awaiting headers)
```

In this case, you may want scale down concurrency of the load test, or allocate more resources to pods, and kubernetes on docker desktop.

For e.g, to allocate maximum 2GB memory to a pod, in dev-values.yaml set

```yaml
resources:
  limits:
    memory: "2Gi"
```

