import os
import torch
from src.utils.logger import logger

def optimize_cpu_settings():
    """Apply CPU-specific optimizations for transformers"""
    # Set thread count for PyTorch
    cpu_threads = int(os.getenv("LLM_THREADS", 4))
    torch.set_num_threads(cpu_threads)
    
    # Configure memory-efficient settings
    os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
    
    # Set float32 matmul precision for better CPU performance
    torch.set_float32_matmul_precision('medium')
    
    # Reduce memory fragmentation
    os.environ["PYTORCH_NO_CUDA_MEMORY_CACHING"] = "1"
    
    logger.info(f"CPU optimization applied: {cpu_threads} threads")