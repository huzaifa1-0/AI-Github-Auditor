from pydantic import BaseModel
from typing import Dict, Any, List, Type
from src.data_models.repository import Repository

class FileAnalysis(BaseModel):
    file_path: str
    language: str
    results: Dict[str, Any]

class AnalysisResult(BaseModel):
    files: List[FileAnalysis]

class AnalysisContext(BaseModel):
    repository: Repository  # Now properly type-annotated
    analysis: AnalysisResult  # Now properly type-annotated
    
    def to_dict(self):
        return {
            "repository": self.repository.dict(),
            "analysis": {
                "files": [
                    {
                        "file_path": f.file_path,
                        "language": f.language,
                        "results": {
                            tool: res for tool, res in f.results.items()
                        }
                    } for f in self.analysis.files
                ]
            }
        }