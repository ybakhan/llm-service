import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)
    
@pytest.fixture(autouse=True)
def mock_model_and_tokenizer():
    mock_model = MagicMock()
    mock_tokenizer = MagicMock()
    
    # Set the mock model and tokenizer in app.state
    app.state.model = mock_model
    app.state.tokenizer = mock_tokenizer
    
    yield mock_model, mock_tokenizer
    
    # Clean up after the test
    del app.state.model
    del app.state.tokenizer
    
@pytest.mark.asyncio
async def test_generate_handler_valid_payload(mock_model_and_tokenizer):
    expected_response = "generated text"
    mock_generate_text = MagicMock(return_value = expected_response)
    mock_model, mock_tokenizer = mock_model_and_tokenizer
    
    # Mocking logger for cleaner test output
    with patch('main.logger') as mock_logger:
        with patch('main.generate_text', new=mock_generate_text):
            payload = {"prompt": "test prompt"}
            response = client.post("/generate", json=payload)
            assert response.status_code == 200
            
            # verify response content
            result = response.json()
            assert result['generated_text'] == expected_response
            assert 'response_time' in result
            assert isinstance(result['response_time'], float)
            
            # verify logger calls
            mock_logger.info.assert_any_call(f"Received payload: {payload}")
            mock_logger.info.assert_any_call(f"Prompt extracted: {payload['prompt']}")
            mock_logger.info.assert_any_call(f"Response: {result['generated_text']}")
            
            # verify `generate_text` was called with correct arguments
            mock_generate_text.assert_called_once_with("test prompt", mock_tokenizer, mock_model)
        
@pytest.mark.asyncio
async def test_generate_handler_no_prompt():
    expected_response = "No prompt provided in payload"
    with patch('main.logger') as mock_logger:
        payload = {}
        response = client.post("/generate", json=payload)
        
        # verify 400 Bad Request because no prompt was provided
        assert response.status_code == 400
        assert response.json() == {"detail": expected_response}
        
        # verify logger calls
        mock_logger.warning.assert_called_once_with(expected_response)
        
@pytest.mark.asyncio
async def test_generate_handler_value_error():
    expected_error = "value error"
    expected_error_response = f"ValueError occurred: {expected_error}"
    mock_generate_text = MagicMock(side_effect=ValueError(expected_error))
    
    with patch('main.logger') as mock_logger:
        with patch('main.generate_text', new=mock_generate_text):
            payload = {"prompt": "Test prompt"}
            response = client.post("/generate", json=payload)
            
            # verify 400 Bad Request due to ValueError
            assert response.status_code == 400
            assert response.json() == {"detail": expected_error_response}
            
            # verify logger calls
            mock_logger.error.assert_called_once_with(expected_error_response)
            
@pytest.mark.asyncio
async def test_generate_handler_runtime_error():
    expected_error = "runtime error"
    expected_error_response = f"Model generation failed: {expected_error}"
    mock_generate_text = MagicMock(side_effect=RuntimeError(expected_error))
    
    with patch('main.logger') as mock_logger:
        with patch('main.generate_text', new=mock_generate_text):
            payload = {"prompt": "test prompt"}
            response = client.post("/generate", json=payload)
            
            # verify 500 Internal Server Error
            assert response.status_code == 500
            assert response.json() == {"detail": expected_error_response}
            
            # verify logger calls
            mock_logger.error.assert_called_once_with(expected_error_response)
            
@pytest.mark.asyncio
async def test_generate_handler_unexpected_error():
    expected_error = "some error"
    expected_error_response = f"Unexpected error occurred: {expected_error}"
    mock_generate_text = MagicMock(side_effect=Exception(expected_error))
        
    with patch('main.logger') as mock_logger:
        with patch('main.generate_text', new=mock_generate_text):
            payload = {"prompt": "test prompt"}
            response = client.post("/generate", json=payload)
            
            # verify 500 Internal Server Error
            assert response.status_code == 500
            assert response.json() == {"detail": expected_error_response}
            
            # verify logger calls
            mock_logger.critical.assert_called_once_with(expected_error_response, exc_info=True)