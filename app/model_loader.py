from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import torch
import logging 

logger = logging.getLogger(__name__)

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