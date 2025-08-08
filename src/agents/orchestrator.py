import os
import tempfile
from src.api.github.client import GitHubClient
from src.core.analysis.static_analysis import StaticAnalyzer
from src.core.reporting.markdown_generator import ReportGenerator
from src.api.huggingface import HuggingFaceLLM
from src.data_models.analysis import AnalysisContext
from src.utils.logger import logger

class AuditOrchestrator:
    def __init__(self):
        self.github = GitHubClient()
        self.analyzer = StaticAnalyzer()
        self.llm = HuggingFaceLLM()
        self.reporter = ReportGenerator()
    
    def audit_repository(self, repo_url, full_scan=False):
        logger.info(f"Starting audit for repository: {repo_url}")
        
        # Clone repository
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = self.github.clone_repository(repo_url, temp_dir)
            
            # Run static analysis
            analysis_results = self.analyzer.analyze_repository(temp_dir)
            context = AnalysisContext(repository=repo, analysis=analysis_results)  # Pass repo object
            
            # Generate AI summary
            llm_summary = self.llm.generate_audit_summary(context)
            
            # Generate report
            report = self.reporter.generate_markdown(context, llm_summary)
        
        logger.info(f"Audit completed for: {repo.name}")
        return report