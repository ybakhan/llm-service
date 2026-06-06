# Sovereign LLM

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/)
[![Docker](https://img.shields.io/badge/Docker-Containerised-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Helm-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Locust](https://img.shields.io/badge/Locust-Load%20Testing-4CAF50)](https://locust.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

A production-ready, self-hosted LLM inference API — own your models, own your compute, own your data. No third-party API dependency, no data leaving your infrastructure. Runs open-source HuggingFace models on your own Kubernetes cluster with horizontal pod auto-scaling and full observability.

## Architecture

```
POST /generate  →  FastAPI  →  HuggingFace Transformers  →  PyTorch (CPU / Apple MPS)
```

| Layer | Technology | Role |
|---|---|---|
| HTTP | FastAPI + Uvicorn | Async request handling, validation, error responses |
| Inference | HuggingFace Transformers | Model and tokenizer management |
| Compute | PyTorch | Tensor ops; auto-detects Apple Silicon (MPS) |
| Packaging | Docker | Reproducible container image |
| Deployment | Helm + Kubernetes | Parameterised rollout, ConfigMap, NodePort service |
| Auto-scaling | HPA | CPU-based horizontal pod scaling (3–5 replicas) |
| Load testing | Locust | Concurrent user simulation and scaling verification |

## Prerequisites

| Tool | Purpose |
|---|---|
| Python 3.13+ | Running the service and tests locally |
| Docker Desktop (Kubernetes enabled) | Container runtime and local cluster |
| Helm | Kubernetes package management |
| kubectl | Cluster interaction |

Switch kubectl context to Docker Desktop if needed:

```bash
kubectl config use-context docker-desktop
```

## Quick start

### 1. Set up the virtual environment

```bash
python3 -m venv myenv
source myenv/bin/activate
pip install pytest locust httpx pytest-asyncio -r requirements.txt
```

### 2. Download a language model

```bash
# Lightweight — good for local development (82 M params)
make download-model-distilgpt2

# Full GPT-2 (124 M params)
make download-model-gpt2
```

Models are saved under `./models/` and loaded at service startup via `MODEL_DIR_PATH`.

### 3. Run the service locally

```bash
make run-local
```

Wait for the model-loaded log line:

```
Model and tokenizer successfully loaded from /path/to/models/distilgpt2 on device cpu
```

### 4. Generate text

```bash
curl http://localhost:8000/generate -X POST \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Once upon a time in a land far away "}'
```

```json
{
  "generated_text": "Once upon a time in a land far away The Lord of the Rings: The Fellowship...",
  "response_time": 2.16
}
```

API docs are available at **http://localhost:8000/docs**

## Testing

```bash
make unit          # unit tests only
make integration   # integration tests (service must be running)
make test-all      # unit + integration
```

## Docker

```bash
# Build image
make image

# Run container (mounts distilgpt2 model from ./models/distilgpt2)
make run-image
```

## Kubernetes deployment

### Deploy (dev)

```bash
make helm-install-dev
```

Expected output:

```
NAME: llm
LAST DEPLOYED: ...
NAMESPACE: default
STATUS: deployed
REVISION: 1
```

Verify all resources are healthy:

```bash
kubectl get all -l app=sovereign-llm
```

You should see 1 deployment, service, replicaset, configmap, HPA, and 3 pods.

The service is exposed on **NodePort 30000**:

```bash
curl http://localhost:30000/generate -X POST \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Once upon a time in a land far away "}'
```

### Kubernetes operations

| Command | Action |
|---|---|
| `make helm-upgrade-dev` | Apply config changes to dev |
| `make helm-upgrade-prod` | Apply config changes to prod |
| `make helm-status` | Check release status |
| `make helm-delete` | Tear down all resources |

## Load testing & auto-scaling

```bash
make load-test
```

Browse to **http://0.0.0.0:8089**, then start a test with 100 concurrent users for 5 minutes (requires Docker Desktop allocated at least 6 CPU / 6 GB memory).

Watch the HPA scale out to 5 pods under load:

```bash
kubectl get pods -l app=sovereign-llm --watch
```

Check per-pod resource usage at peak:

```bash
kubectl top pods -l app=sovereign-llm
```

```
llm-service-568746bb8c-7f2cm   868m   772Mi
llm-service-568746bb8c-g46hl   885m   877Mi
llm-service-568746bb8c-jmgfs   855m   826Mi
llm-service-568746bb8c-lrqh7   874m   879Mi
llm-service-568746bb8c-xbwrt   882m   878Mi
```

The HPA scales back to 3 pods once load drops.

## Configuration

Model behaviour and resource limits are controlled via Helm values. Defaults live in `helm/llm-microservice/values.yaml`; environment overrides in `values/dev-values.yaml` and `values/prod-values.yaml`.

| Parameter | Default | Description |
|---|---|---|
| `MAX_LENGTH` | 32 | Maximum input token length |
| `MAX_NEW_TOKENS` | 20 | Tokens to generate per request |
| `TEMPERATURE` | 0.2 | Sampling temperature (lower = more deterministic) |
| `TOP_K` | 5 | Top-K sampling |
| `TOP_P` | 0.7 | Nucleus sampling threshold |
| `REPETITION_PENALTY` | 1.1 | Penalises repeated tokens |

To switch models, download the target model and set `volumes.modelVolume.path` in `dev-values.yaml`:

```yaml
volumes:
  modelVolume:
    path: /absolute/path/to/gpt2
```

## Troubleshooting

**Liveness probe failures during load test**

```bash
kubectl get events -o jsonpath='{range .items[*]}{.involvedObject.kind}{"\t"}{.involvedObject.name}{"\t"}{.reason}{"\t"}{.message}{"\n"}{end}' | grep -E 'Probe|Liveness'
```

If you see `context deadline exceeded`, reduce load test concurrency or increase pod memory limit in `dev-values.yaml`:

```yaml
resources:
  limits:
    memory: "2Gi"
```

## License

[MIT](./LICENSE)

---

Made by [@ybakhan](https://github.com/ybakhan)
