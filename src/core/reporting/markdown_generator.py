import os
import json
import subprocess
import sys
from datetime import datetime
import pypandoc
from src.data_models.report import AuditReport
from src.utils.file_utils import ensure_dir_exists

class ReportGenerator:
    TOOL_FORMATTERS = {
        "bandit": lambda r: ReportGenerator._format_bandit(r),
        "pylint": lambda r: ReportGenerator._format_pylint(r),
        "eslint": lambda r: ReportGenerator._format_eslint(r),
        "yamllint": lambda r: ReportGenerator._format_yamllint(r),
    }

    SEVERITY_ICONS = {
        "HIGH": "🛑",
        "MEDIUM": "⚠️",
        "LOW": "ℹ️",
        "CONVENTION": "💅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "INFO": "ℹ️"
    }

    def generate_markdown(self, analysis_results, llm_summary):
        repo_name = analysis_results.repository.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{repo_name}_audit_{timestamp}.md"
        output_dir = os.getenv("OUTPUT_DIR", "outputs/reports")
        ensure_dir_exists(output_dir)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            # Header and metadata
            f.write(f"# GitHub Repository Audit Report\n\n")
            f.write(f"**Repository**: `{repo_name}`  \n")
            f.write(f"**Audit Date**: {timestamp.replace('_', ' ')}  \n")
            f.write(f"**Analyzed Files**: {len(analysis_results.analysis.files)}  \n\n")
            
            # Executive summary
            f.write("## 🔍 Executive Summary\n")
            f.write(llm_summary + "\n\n")
            
            # Security and quality overview
            f.write("## 🛡️ Security & Quality Overview\n")
            f.write(self._generate_summary_table(analysis_results))
            
            # Detailed findings
            f.write("## 📝 Detailed Findings\n")
            for file_analysis in analysis_results.analysis.files:
                self._write_file_analysis(f, file_analysis)
                
            # Recommendations section
            f.write("\n## 🚀 Recommendations\n")
            f.write(self._extract_recommendations(llm_summary))
            
            # Appendix
            f.write("\n## 🔧 Appendix: Tool Configuration\n")
            f.write("| Tool | Version |\n|------|---------|\n")
            f.write(f"| Bandit | {self._get_tool_version('bandit')} |\n")
            f.write(f"| Pylint | {self._get_tool_version('pylint')} |\n")
        
        pdf_filepath = filepath.replace(".md", ".pdf")
        self._export_pdf(filepath, pdf_filepath)
            
        return AuditReport(
            repository=analysis_results.repository,
            file_path=filepath,
            summary=llm_summary,
            generated_at=timestamp
        )
    
    def _export_pdf(self, md_path, pdf_path):
        """Convert Markdown to PDF using pypandoc"""
        try:
            pypandoc.convert_file(
                md_path,
                'pdf',
                outputfile=pdf_path,
                extra_args=['--standalone']
            )
            print(f"✅ PDF report generated: {pdf_path}")
        except OSError as e:
            print(f"⚠️ PDF generation failed. Ensure Pandoc is installed. Error: {e}")


    def _write_file_analysis(self, f, file_analysis):
        f.write(f"### 📄 File: `{file_analysis.file_path}`\n")
        has_issues = False
        
        for tool, results in file_analysis.results.items():
            tool_header = f"#### {tool.upper()} Results\n"
            
            if "error" in results:
                f.write(tool_header)
                self._write_error(f, results["error"])
                continue
                
            formatter = self.TOOL_FORMATTERS.get(tool)
            if formatter:
                formatted = formatter(results)
                if formatted:
                    f.write(tool_header)
                    f.write(formatted + "\n")
                    has_issues = True
            else:
                f.write(tool_header)
                f.write("```json\n")
                f.write(json.dumps(results, indent=2)[:2000] + "\n")
                f.write("```\n")
                has_issues = True
        
        if not has_issues:
            f.write("✅ No significant issues found\n\n")

    def _write_error(self, f, error):
        if isinstance(error, dict):
            f.write(f"{self.SEVERITY_ICONS['ERROR']} **Error Code**: {error.get('exit_code', 'Unknown')}  \n")
            f.write(f"**Diagnosis**: {error.get('stderr', 'No details')}  \n")
            f.write(f"**Recommendation**: {error.get('suggestion', 'Check tool configuration')}\n\n")
        else:
            f.write(f"❌ {error}\n\n")

    def _generate_summary_table(self, analysis):
        """Generate security/quality overview table"""
        summary = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0
        }
        
        for file_analysis in analysis.analysis.files:
            for tool, results in file_analysis.results.items():
                if "error" in results or not results:
                    continue
                    
                if tool == "bandit" and "results" in results:
                    for issue in results["results"]:
                        sev = issue.get("issue_severity", "MEDIUM").upper()
                        summary[sev] = summary.get(sev, 0) + 1
        
        return (
            "| Severity | Count |\n|----------|-------|\n"
            f"| Critical | {summary.get('CRITICAL', 0)} |\n"
            f"| High | {summary.get('HIGH', 0)} |\n"
            f"| Medium | {summary.get('MEDIUM', 0)} |\n"
            f"| Low | {summary.get('LOW', 0)} |\n\n"
        )

    def _extract_recommendations(self, llm_summary):
        """Parse LLM summary for actionable items"""
        # Extract recommendations section from LLM output
        start = llm_summary.find("Top Recommendations")
        end = llm_summary.find("Overall Project Health")
        
        if start == -1 or end == -1:
            return "⚠️ No specific recommendations provided in LLM summary"
            
        return llm_summary[start:end] + "\n"

    @staticmethod
    def _format_bandit(results):
        """Format Bandit security results"""
        if not results.get("results"):
            return "✅ No security issues found\n"
            
        output = []
        for issue in results["results"]:
            severity = issue.get("issue_severity", "MEDIUM").upper()
            output.append(
                f"{ReportGenerator.SEVERITY_ICONS.get(severity, '')} "
                f"**{severity}**: {issue.get('issue_text')}  \n"
                f"  - Location: Line {issue.get('line_number')}  \n"
                f"  - Confidence: {issue.get('issue_confidence')}  \n"
                f"  - CWE: {issue.get('issue_cwe', {}).get('id', 'N/A')}  \n"
            )
        return "\n".join(output)

    @staticmethod
    def _format_pylint(results):
        """Format Pylint code quality results"""
        if not isinstance(results, list) or len(results) == 0:
            return "✅ No code quality issues found\n"
            
        # Group by message type
        categories = {}
        for issue in results:
            msg_type = issue.get("type", "UNKNOWN")
            categories.setdefault(msg_type, []).append(issue)
            
        output = []
        for msg_type, issues in categories.items():
            icon = ReportGenerator.SEVERITY_ICONS.get(
                "ERROR" if msg_type in ("error", "fatal") else msg_type.upper()
            )
            output.append(f"{icon} **{msg_type.upper()}**: {len(issues)} issues")
            for issue in issues[:3]:  # Show top 3 per category
                output.append(
                    f"  - Line {issue.get('line')}: {issue.get('message')} "
                    f"(`{issue.get('message-id')}`)"
                )
            if len(issues) > 3:
                output.append(f"  ... and {len(issues)-3} more")
                
        return "\n".join(output) + "\n"

    @staticmethod
    def _format_eslint(results):
        """Format ESLint JavaScript results"""
        return "ℹ️ ESLint formatter not implemented\n"

    @staticmethod
    def _format_yamllint(results):
        """Format YAMLlint results"""
        if not results:
            return "✅ No YAML issues found\n"
            
        output = []
        for issue in results:
            level = issue.get("level", "warning").upper()
            output.append(
                f"{ReportGenerator.SEVERITY_ICONS.get(level, '')} "
                f"**{level}**: Line {issue.get('line')} - {issue.get('message')}"
            )
        return "\n".join(output) + "\n"

    def _get_tool_version(self, tool):
        """Get version of analysis tool"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", tool, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.split("\n")[0].strip()
        except Exception:
            return "Unknown"