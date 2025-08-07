import os
from github import Github, Auth
from git import Repo, GitCommandError
from src.data_models.repository import Repository
from src.utils.logger import logger
from src.utils.file_utils import safe_delete_directory

class GitHubClient:
    def __init__(self, access_token=None):
        self.access_token = access_token or os.getenv("GITHUB_TOKEN")
        self.auth = Auth.Token(self.access_token)
        self.g = Github(auth=self.auth)
    
    def get_repo_info(self, repo_url):
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        org_name = repo_url.split('/')[-2]
        return self.g.get_organization(org_name).get_repo(repo_name)
    
    def clone_repository(self, repo_url, clone_path):
        safe_delete_directory(clone_path)
        
        authed_url = f"https://{self.access_token}@{repo_url.split('//')[1]}"
        try:
            repo = Repo.clone_from(authed_url, clone_path)
            logger.info(f"Cloned repository to: {clone_path}")
            return Repository(
                path=clone_path,
                url=repo_url,
                name=repo_url.split('/')[-1].replace('.git', ''),
                default_branch=repo.active_branch.name
            )
        except GitCommandError as e:
            logger.error(f"Clone failed: {str(e)}")
            raise