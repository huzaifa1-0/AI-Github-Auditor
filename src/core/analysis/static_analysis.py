import os
import subprocess
import json
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
                file_result = self.analyze_file()