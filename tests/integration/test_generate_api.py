from fastapi.testclient import TestClient
from main import app

def test_generate_api_valid_payload():
    with TestClient(app) as client:
        payload = {
            "prompt": "Once upon a time "
        }
        response = client.post("/generate", json=payload)
        assert response.status_code == 200
        
        # verify response contains the expected keys
        assert 'generated_text' in response.json()
        assert 'response_time' in response.json()
        
        # verify generated_text is not empty or whitespace
        assert response.json()['generated_text'].strip() != ''

def test_generate_api_no_prompt():
    with TestClient(app) as client:
        payload = {}
        response = client.post("/generate", json=payload)
        
        # expected 400 Bad Request because no prompt was provided
        assert response.status_code == 400
        assert response.json() == {"detail": "No prompt provided in payload"}
        
def test_docs_handler():
    with TestClient(app) as client:
        response = client.get("/docs")
        assert response.status_code == 200

def test_openapi_handler():
    with TestClient(app) as client:
        response = client.get("/openapi.yaml")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/yaml"

def test_health_check_healthy():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}