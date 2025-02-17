import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_health_check_healthy(client):
    app.state.model = Mock()
    app.state.tokenizer = Mock()
    
    with patch('api.logger') as mock_logger: 
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
        mock_logger.info.asset_not_called()
    
@pytest.mark.asyncio
async def test_health_check_model_unhealthy(client):
    if hasattr(app.state, 'model'):
        del app.state.model
    
    with patch('api.logger') as mock_logger:
        response = client.get("/health")
        assert response.status_code == 503
        assert response.json() == {"status": "unhealthy", "detail": "Model or tokenizer not loaded"}
        mock_logger.info.assert_called_once_with("Health check failed - Model or tokenizer not loaded")

@pytest.mark.asyncio
async def test_health_check_tokenizer_unhealthy(client):
    if hasattr(app.state, 'tokenizer'):
        del app.state.tokenizer
    
    with patch('api.logger') as mock_logger:
        response = client.get("/health")
        assert response.status_code == 503
        assert response.json() == {"status": "unhealthy", "detail": "Model or tokenizer not loaded"}
        mock_logger.info.assert_called_once_with("Health check failed - Model or tokenizer not loaded")