import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig

def test_model():
    model_id = "microsoft/phi-2"
    print(f"Testing model: {model_id}")
    
    # Configure 4-bit quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float32
    )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    print("Tokenizer loaded")
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        device_map="auto",
        quantization_config=bnb_config
    )
    print("Model loaded")
    
    # Create pipeline
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device_map="auto"
    )
    
    # Test prompt
    prompt = "Write a Python function to calculate factorial"
    response = pipe(
        prompt,
        max_new_tokens=100,
        temperature=0.3,
        top_p=0.95,
        do_sample=True
    )
    
    print("\nTest successful!")
    print("Prompt:", prompt)
    print("Response:", response[0]['generated_text'])

if __name__ == "__main__":
    test_model()