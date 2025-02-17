from fastapi import HTTPException, Response, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi import APIRouter, Request
from pathlib import Path
from generate import generate_text
import time 
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate")
async def generate_handler(request: Request, payload: dict):
    logger.info(f"Received payload: {payload}")
        
    prompt = payload.get('prompt')
    if not prompt:
        warning = "No prompt provided in payload"
        logger.warning(warning)
        raise HTTPException(status_code=400, detail = warning)
        
    start_time = time.time()
    logger.info(f"Prompt extracted: {prompt}")
                
    try:
        generated_text = generate_text(prompt, 
            request.app.state.tokenizer, 
            request.app.state.model, 
            request.app.state.device)
        
        response_time = round(time.time() - start_time, 2)
        
        result = {"generated_text": generated_text, "response_time": response_time}
        
        logger.info(f"Response: {result['generated_text']}")
        
        return result
    
    except ValueError as ve:
        error = f"ValueError occurred: {str(ve)}"
        logger.error(error)
        raise HTTPException(status_code=400, detail=error)
    
    except RuntimeError as re:
        error = f"Model generation failed: {str(re)}"
        logger.error(error)
        raise HTTPException(status_code=500, detail=error)
    
    except Exception as e:
        error = f"Unexpected error occurred: {str(e)}"
        logger.critical(error, exc_info=True)
        raise HTTPException(status_code=500, detail=error)
    
    finally:
        logger.info(f"Total request time: {time.time() - start_time:.2f} seconds")

# Serve openapi documentation UI
@router.get("/docs", include_in_schema=False)
async def docs_handler():
    return get_swagger_ui_html(
        openapi_url="/openapi.yaml", 
        title="LLM Service API Documentation"
    )

# Serve openapi documentation
@router.get("/openapi.yaml", include_in_schema=False)
async def openapi_handler():
    with open(Path(__file__).parent / "docs/openapi.yaml", "r") as yaml_file:
        content = yaml_file.read()
    return Response(content=content, media_type="application/yaml")

@router.get("/health")
async def health_check(request: Request):
    # Check if model and tokenizer are accessible and functional
    if not hasattr(request.app.state, 'model') or not hasattr(request.app.state, 'tokenizer'):
        content = "Model or tokenizer not loaded"
        logger.info(f"Health check failed - {content}")
        
        return Response(content='{"status": "unhealthy", "detail": "' + content + '"}', 
            media_type="application/json", 
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    return {"status": "healthy"}