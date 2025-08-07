import os
import psutil
import torch
from src.utils.logger import logger

def optimize_cpu_settings():
    """Apply CPU-specific optimizations for transformers"""
    
    cpu_threads = int(os.getenv("LLM_THREADS", psutil.cpu_count(logical=False)))
    os.environ["OMP_NUM_THREADS"] = str(cpu_threads)
    
    
    os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
    
    
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    logger.info(f"CPU optimization applied: {cpu_threads} threads")