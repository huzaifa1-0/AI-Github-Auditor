# download_models.py
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

def download_model(model_id):
    print(f"Downloading {model_id}...")
    try:
        # Create cache directory
        cache_dir = os.path.join(os.getenv('CACHE_DIR', '.cache'), 'models')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Download tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
        
        # Download model
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            cache_dir=cache_dir
        )
        
        print(f"Successfully downloaded {model_id}")
        return True
    except Exception as e:
        print(f"Failed to download {model_id}: {str(e)}")
        return False

if __name__ == "__main__":
    models = ["microsoft/phi-1_5", "microsoft/phi-2", "gpt2"]
    for model_id in models:
        download_model(model_id)