import os
from ctransformers import AutoModelForCausalLM
from src.utils.logger import logger
from src.utils.file_utils import read_prompt_template

class HuggingFaceLLM:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HuggingFaceLLM, cls).__new__(cls)
            model_path = os.getenv("LOCAL_LLM_MODEL_PATH", "models/phi-2.Q4_K_M.gguf")
            cls._instance.model = AutoModelForCausalLM(
                model_path = model_path,
                model_type = 'phi2',
                lib = "avx2",
                threads=int(os.getenv("LLM_THREADS", 4)),
                context_length=int(os.getenv("LLM_CONTEXT_SIZE", 2048)),
                gpu_layers = 0
            )
            logger.info(f"Loaded Hugging Face GGUF model: {model_path}")
        return cls._instance
    
    def generate_audit_summary(self, analysis_results):
        prompt_template = read_prompt_template("audit_prompt.md")
        prompt = prompt_template.format(
            repo_name=analysis_results.repository.name,
            findings=str(analysis_results.to_dict())
        )
        try:
            response = self.model(
                prompt=prompt,
                max_new_tokens=1024,
                temperature=0.3,
                top_p=0.95,
                stop=["</s>", "[INST]"]
            )
            return self._clean_response(response)
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return "LLM analysis failed. Please check logs for details."
        
               