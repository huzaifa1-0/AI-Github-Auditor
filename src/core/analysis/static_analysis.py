import os
import subprocess
import json
import sys  # Added import
from pathlib import Path
from src.utils.logger import logger
from src.utils.file_utils import find_files
from src.data_models.analysis import AnalysisResult, FileAnalysis

class StaticAnalyzer:
    TOOLS = {
        "py": ["bandit", "pylint"],
        "js": ["eslint"],
        "yaml": ["yamllint"],
        "yml": ["yamllint"]
    }
    
    def analyze_repository(self, repo_path):
        results = []
        file_types = set(self.TOOLS.keys())
        
        for ext in file_types:
            files = find_files(repo_path, f"*.{ext}")
            for file_path in files:
                relative_path = str(Path(file_path).relative_to(repo_path))
                file_result = self.analyze_file(file_path, ext)
                results.append(
                    FileAnalysis(
                        file_path=relative_path,
                        language=ext,
                        results=file_result
                    )
                )
        
        return AnalysisResult(files=results)

    def analyze_file(self, file_path, language):
        results = {}
        for tool in self.TOOLS.get(language, []):
            try:
                if tool == "bandit":
                    # Use the Python module directly
                    output = subprocess.check_output(
                        [sys.executable, "-m", "bandit", "-f", "json", "-q", file_path],
                        stderr=subprocess.STDOUT,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    results[tool] = json.loads(output)
                elif tool == "pylint":
                    # Use the Python module directly
                    output = subprocess.check_output(
                        [sys.executable, "-m", "pylint", "--output-format=json", file_path],
                        stderr=subprocess.STDOUT,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    results[tool] = json.loads(output)
                elif tool == "eslint":
                    # Use the full path to eslint
                    eslint_path = os.path.join(os.path.dirname(sys.executable), "eslint")
                    output = subprocess.check_output(
                        [eslint_path, "--format=json", file_path],
                        stderr=subprocess.STDOUT,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    results[tool] = json.loads(output)
                elif tool == "yamllint":
                    # Use the Python module directly
                    output = subprocess.check_output(
                        [sys.executable, "-m", "yamllint", "-f", "parsable", file_path],
                        stderr=subprocess.STDOUT,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    results[tool] = self.parse_yamllint(output)
            except Exception as e:
                logger.warning(f"{tool} failed on {file_path}: {str(e)}")
                results[tool] = {"error": str(e)}
        
        return results

    def parse_yamllint(self, output):
        issues = []
        for line in output.strip().split('\n'):
            if not line:
                continue
            parts = line.split(':')
            if len(parts) >= 4:
                issues.append({
                    "file": parts[0],
                    "line": int(parts[1]),
                    "column": int(parts[2]),
                    "level": parts[3].strip()[0],
                    "message": parts[3].strip()[2:]
                })
        return issues