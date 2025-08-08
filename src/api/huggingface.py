import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from src.utils.logger import logger
from src.utils.file_utils import read_prompt_template
from src.utils.cpu_optimization import optimize_cpu_settings

class HuggingFaceLLM:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HuggingFaceLLM, cls).__new__(cls)
            model_id = os.getenv("HF_MODEL_NAME", "microsoft/phi-1_5")
            
            try:
                # Apply CPU optimizations
                optimize_cpu_settings()
                
                logger.info(f"Loading model: {model_id}")
                
                # Set cache directories from environment variables
                cache_dir = os.getenv("TRANSFORMERS_CACHE", os.path.join(os.getenv("CACHE_DIR", ".cache"), "models"))
                os.makedirs(cache_dir, exist_ok=True)
                
                # Load tokenizer
                tokenizer = AutoTokenizer.from_pretrained(
                    model_id,
                    trust_remote_code=True,
                    cache_dir=cache_dir
                )
                
                # Load model without device mapping
                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    trust_remote_code=True,
                    torch_dtype=torch.float32,
                    low_cpu_mem_usage=True,
                    cache_dir=cache_dir
                )
                
                # Explicitly move model to CPU
                model = model.to('cpu')
                model.eval()  

                cls._instance.tokenizer = tokenizer
                cls._instance.model = model
                
                # Create text generation pipeline without device argument
                cls._instance.pipeline = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device=None  # No device argument since we moved model to CPU
                )
                
                logger.info(f"Successfully loaded model: {model_id}")
            except Exception as e:
                logger.error(f"Failed to load model: {str(e)}")
                raise RuntimeError(f"Model loading failed: {str(e)}")
        
        return cls._instance

    def _generate_in_chunks(self, prompt, max_new_tokens=384):
        """
        Splits prompt into chunks that fit model context size, generates sequentially.
        """
        tokenizer = self.tokenizer
        model = self.model
        
        # Get model context limit
        max_length = getattr(model.config, "max_position_embeddings", 2048)
        
        # Tokenize prompt
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        total_tokens = input_ids.shape[1]

        if total_tokens <= max_length:
            # No need to chunk
            outputs = model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                temperature=0.3,
                top_p=0.95,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
            return tokenizer.decode(outputs[0], skip_special_tokens=True)

        logger.warning(
            f"Prompt too long ({total_tokens} tokens). Splitting into chunks of {max_length} tokens."
        )

        # Generate in chunks
        generated_text = ""
        for start in range(0, total_tokens, max_length):
            end = min(start + max_length, total_tokens)
            chunk_ids = input_ids[:, start:end]

            outputs = model.generate(
                chunk_ids,
                max_new_tokens=max_new_tokens,
                temperature=0.3,
                top_p=0.95,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
            generated_text += tokenizer.decode(outputs[0], skip_special_tokens=True)

        return generated_text

    
    def generate_audit_summary(self, analysis_results):
        prompt_template = read_prompt_template("audit_prompt.md")
        prompt = prompt_template.format(
            repo_name=analysis_results.repository.name,
            findings=str(analysis_results.to_dict()))
        
        try:
            # Now using chunked generation to avoid token overflow errors
            return self._generate_in_chunks(prompt, max_new_tokens=384)
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return "LLM analysis failed. Please check logs for details."