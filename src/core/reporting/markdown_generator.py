import os 
from datetime import datetime
from src.data_models.report import AuditReport
from src.utils.file_utils import ensure_dir_exists


class ReportGenerator:
    def generate_markdown(self, analysis_results, llm_summary):
        repo_name = analysis_results.repository.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{repo_name}_audit_{timestamp}.md"
        output_dir = os.getenv("OUTPUT_DIR", "outputs/reports")
        ensure_dir_exists(output_dir)
        filepath = os.path.join(output_dir, filename)