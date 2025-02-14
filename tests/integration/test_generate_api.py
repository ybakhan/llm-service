from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)

def test_generate_api_valid_payload():
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
    payload = {}
    response = client.post("/generate", json=payload)
    
    # expected 400 Bad Request because no prompt was provided
    assert response.status_code == 400
    assert response.json() == {"detail": "No prompt provided in payload"}