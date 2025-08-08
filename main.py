
from src.utils.cpu_optimization import optimize_cpu_settings
from src.utils.windows_fixes import enable_long_paths, fix_win32_unicode
from src.utils.logger import configure_logger
from src.agents.orchestrator import AuditOrchestrator
from dotenv import load_dotenv
from pathlib import Path
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def load_environment():
    
    base_dir = Path(__file__).resolve().parent

    
    env_paths = [
        base_dir / ".env",
        base_dir / "config" / ".env",
        base_dir / "src" / ".env"
    ]

    for path in env_paths:
        if path.exists():
            print(f"Loading environment from: {path}")
            load_dotenv(dotenv_path=path)
            return True

    print("No .env file found!")
    return False


if __name__ == "__main__":

    if not load_environment():
        print("ERROR: Could not find .env file")
        sys.exit(1)

    
    print("\nEnvironment variables:")
    for key in ["GITHUB_TOKEN", "LOCAL_LLM_MODEL_PATH", "LLM_THREADS"]:
        print(f"{key}: {os.getenv(key, 'Not set')}")

    fix_win32_unicode()
    enable_long_paths()

    configure_logger()
    optimize_cpu_settings()

    if len(sys.argv) < 2:
        print("Usage: python main.py <repo_url> [--full]")
        sys.exit(1)

    repo_url = sys.argv[1]
    full_scan = "--full" in sys.argv

    orchestrator = AuditOrchestrator()
    report = orchestrator.audit_repository(repo_url, full_scan=full_scan)

    print(f"\nAudit completed! Report saved to: {report.file_path}")
