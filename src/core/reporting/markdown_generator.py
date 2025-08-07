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

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# GitHub Repository Audit Report\n")
            f.write(f"**Repository**: {repo_name}\n\n")
            f.write(f"**Audit Date**: {timestamp.replace('_', ' ')}\n\n")
            f.write("## AI Analysis Summary\n")
            f.write(llm_summary + "\n\n")
            f.write("## Detailed Findings\n")

            for file_analysis in analysis_results.analysis.files:
                f.write(f"### File: `{file_analysis.file_path}`\n")
                for tool, results in file_analysis.results.items():
                    f.write(f"#### {tool.upper()} Results\n")
                    if "error" in results:
                        f.write(f"Error: {results['error']}\n")
                    else:
                        f.write("```json\n")
                        f.write(str(results)[:1000] + "\n")
                        f.write("```\n")
        return AuditReport(
            repository=analysis_results.repository,
            file_path=filepath,
            summary=llm_summary,
            generated_at=timestamp
        )