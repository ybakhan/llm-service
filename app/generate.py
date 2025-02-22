import os
import torch

def generate_text(prompt: str, tokenizer, model, device):
    
    inputs = tokenizer(prompt, 
        return_tensors="pt", 
        padding=False,
        truncation=True, 
        max_length=int(os.environ.get('MAX_LENGTH', 512)))
    
    # move tensors to device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']

    # Generate text with sampling
    with torch.no_grad():
        outputs = model.generate(
            input_ids = input_ids, 
            attention_mask = attention_mask,
            do_sample = True,
            num_return_sequences = 1,  
            max_new_tokens = int(os.environ.get('MAX_NEW_TOKENS', 50)),               
            temperature = float(os.environ.get('TEMPERATURE', 0.3)),                
            top_k = int(os.environ.get('TOP_K', 20)),                       
            top_p = float(os.environ.get('TOP_P', 0.9)),                      
            repetition_penalty = float(os.environ.get('REPETITION_PENALTY', 1.2))
        )

    # Decode the generated text
    return tokenizer.decode(outputs[0], skip_special_tokens=True) 
       