import os
import tempfile
from src.api.github.client import GitHubClient
from src.core.analysis.static_analysis import staticanalyzer
from src.core.reporting.markdown_generator import ReportGenerator
from src.api.huggingface import HuggingFaceLLM
from src.data_models.analysis import AnalysisContext
from src.utils.logger import logger


class AuditOrchestrator:
    def __init__(self):
        self.github = GitHubClient()
        self.analyzer = staticanalyzer()
        self.llm = HuggingFaceLLM()
        self.reporter = ReportGenerator()
        
