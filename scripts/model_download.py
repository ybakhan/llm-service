from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Download and save a transformer model and tokenizer from https://huggingface.co/")
    parser.add_argument(
        "--model-name",
        type=str,
        default="distilbert/distilgpt2",
        help="Name of the model to download (default: distilbert/distilgpt2)"
    )
    args = parser.parse_args()
    model_name = args.model_name

    model, tokenizer = None, None
    try:
        # load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
    except Exception as e:
        print(f"error loading model: {e}")
        exit(1)

    model_dir_name = model_name.split("/")[-1]
    save_directory = f"./models/{model_dir_name}"
    os.makedirs(save_directory, exist_ok=True)

    # save the model and tokenizer to disk
    model.save_pretrained(save_directory)
    tokenizer.save_pretrained(save_directory)

    print(f"model and tokenizer saved to {save_directory}")

if __name__ == "__main__":
    main()