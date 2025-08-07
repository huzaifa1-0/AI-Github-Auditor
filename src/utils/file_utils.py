import os 
import shutil
import glob
from pathlib import Path

def safe_delete_directory(path):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"Warning: Couldn't delete {path}: {str(e)}")


def ensure_dir_exists(path):
    os.makedirs(path, exist_ok=True)

def find_files(root_dir, pattern):
    return glob.glob(os.path.join(root_dir, "**", pattern), recursive=True)


def read_prompt_template(name):
    base_path = os.getenv("PROMPT_DIR", "config/prompts")
    file_path = os.path.join(base_path, name)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"# Audit Report\n\n## Analysis of {{repo_name}}\n\n{{findings}}"