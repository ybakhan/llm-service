from fastapi import FastAPI, HTTPException, Response
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi.openapi.docs import get_swagger_ui_html
from pathlib import Path
from generate import generate_text
from contextlib import asynccontextmanager
import time 
import os
import uvicorn    
import logging
import torch

def load_model_and_tokenizer():
    try:
        model_dir_path = os.environ.get(
            'MODEL_DIR_PATH',   # used to run service natively on host
            os.path.abspath("./model"))

        # load model and tokenizer
        model = AutoModelForCausalLM.from_pretrained(model_dir_path)
        tokenizer = AutoTokenizer.from_pretrained(model_dir_path)

        device = None  
        if torch.backends.mps.is_available():
            device = torch.device("mps") 
            
            # Move model to device with half-precision if MPS is available
            model = model.to(dtype=torch.float16, device=device)
        else:
            device = "cpu"
                
        # set pad_token for the tokenizer and model
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = model.config.eos_token_id

        logger.info(f"Model and tokenizer successfully loaded from {model_dir_path} on device {device}")
        return model, tokenizer, device

    except Exception as e:
        logger.error(f"Failed to load model or tokenizer from {model_dir_path}. Error: {str(e)}")
        raise SystemExit("Model loading process failed. Exiting application.") from e

@asynccontextmanager
async def lifespan(app: FastAPI):
    # load model and tokenizer
    model, tokenizer, device = load_model_and_tokenizer()
    
    app.state.model = model
    app.state.tokenizer = tokenizer
    app.state.device = device
    
    yield
    # shutdown - clean up model and tokenizer
    del model, tokenizer
    logger.info("Model and tokenizer have been cleaned up.")

app = FastAPI(openapi_url=None, lifespan=lifespan)

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

####################### log service configuration#########################
configured_vars = [
    'MAX_LENGTH',
    'MAX_NEW_TOKENS',
    'TEMPERATURE',
    'TOP_K',
    'TOP_P',
    'REPETITION_PENALTY'
]
logger.info("Qlik LLM service environment variables:")
for key in configured_vars:
    if key in os.environ:
        logger.info(f"{key}={os.environ[key]}")
    else:
        logger.info(f"{key} is not set")
#############################################################################

@app.post("/generate")
async def generate_handler(payload: dict):
    logger.info(f"Received payload: {payload}")
        
    prompt = payload.get('prompt')
    if not prompt:
        warning = "No prompt provided in payload"
        logger.warning(warning)
        raise HTTPException(status_code=400, detail = warning)
        
    start_time = time.time()
    logger.info(f"Prompt extracted: {prompt}")
                
    try:
        generated_text = generate_text(prompt, app.state.tokenizer, app.state.model, app.state.device)
        
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
@app.get("/docs", include_in_schema=False)
async def docs_handler():
    return get_swagger_ui_html(
        openapi_url="/openapi.yaml", 
        title="LLM Service API Documentation"
    )

# Serve openapi documentation
@app.get("/openapi.yaml", include_in_schema=False)
async def openapi_handler():
    with open(Path(__file__).parent / "docs/openapi.yaml", "r") as yaml_file:
        content = yaml_file.read()
    return Response(content=content, media_type="application/yaml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)