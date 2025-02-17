import os
import uvicorn    
import logging
from model_loader import load_model_and_tokenizer
from fastapi import FastAPI
from contextlib import asynccontextmanager
from api import router

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
app.include_router(router)

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

####################### log service configuration#########################
configured_vars = [
    'MAX_LENGTH',
    'MAX_NEW_TOKENS',
    'TEMPERATURE',
    'TOP_K',
    'TOP_P',
    'REPETITION_PENALTY'
]
logger = logging.getLogger(__name__)
logger.info("Qlik LLM service environment variables:")
for key in configured_vars:
    if key in os.environ:
        logger.info(f"{key}={os.environ[key]}")
    else:
        logger.info(f"{key} is not set")
#############################################################################

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)