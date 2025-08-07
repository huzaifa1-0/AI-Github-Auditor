from pydantic import BaseModel

class Repository(BaseModel):
    name: str
    url: str
    path: str
    default_branch: str