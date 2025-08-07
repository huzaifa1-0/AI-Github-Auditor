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
        
    def audit_repository(self, repo_url, full_scan = False):
        logger.info(f"starting audit for repository: {repo_url}")

        with tempfile.TemporaryDirectory() as temp_dir:
            self.github.clone_repository(repo_url, temp_dir)

            analysis_results = self.analyzer.analyze_repository(temp_dir)
            context = AnalysisContext(repository=repo_url, analysis=analysis_results)

            llm_summary = self.llm.generate_audit_summary(context)

            report = self.reporter.generate_markdown(context, llm_summary)

        logger.info(f"Audit completed for this repository: {repo_url}")
        return report
