from pydantic import BaseModel
from src.data_models.repository import Repository

class AuditReport(BaseModel):
    repository: Repository  # Now properly type-annotated
    file_path: str
    summary: str
    generated_at: str