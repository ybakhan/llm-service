from fastapi import FastAPI, HTTPException, Response
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi.openapi.utils import get_openapi
from generate import generate_text
import time 
import yaml
import os
import uvicorn    
import logging

app = FastAPI()

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
    'REPETITION_PENALTY',
    'MODEL_DIR_NAME'
]
logger.info("Qlik LLM service environment variables:")
for key in configured_vars:
    if key in os.environ:
        logger.info(f"{key}={os.environ[key]}")
    else:
        logger.info(f"{key} is not set")
#############################################################################

# load the model and tokenizer
model_dir_name = os.environ.get('MODEL_DIR_NAME', "distilgpt2")
logger.info(f"loading model from directory : {model_dir_name}")

model_dir_path = f"./models/{model_dir_name}"
model = AutoModelForCausalLM.from_pretrained(model_dir_path)
tokenizer = AutoTokenizer.from_pretrained(model_dir_path)

# Set pad_token for the tokenizer and model
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = model.config.eos_token_id

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
        generated_text = generate_text(prompt, tokenizer, model)
        
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

@app.get("/openapi.yaml", response_class=Response)
async def get_openapi_yaml():
    openapi_schema = get_openapi(
        title="Text Generation API",
        version="1.0.0",
        description="This API generates text based on given prompts using a pre-trained model.",
        routes=app.routes
    )
    yaml_schema = yaml.dump(openapi_schema)
    return Response(content=yaml_schema, media_type="application/yaml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)