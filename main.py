import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse

from src.utils.cpu_optimization import optimize_cpu_settings
from src.utils.windows_fixes import enable_long_paths, fix_win32_unicode
from src.utils.logger import configure_logger
from src.agents.orchestrator import AuditOrchestrator


# ---- Constants -------------------------------------------------

ENV_VARS_TO_DISPLAY = (
    "GITHUB_TOKEN",
    "LOCAL_LLM_MODEL_PATH",
    "LLM_THREADS",
)

ENV_SEARCH_PATHS = (
    ".env",
    "config/.env",
    "src/.env",
)


# ---- Environment handling -------------------------------------

def load_environment(base_dir: Path) -> Path | None:
    """
    Search for a .env file in predefined locations and load the first one found.
    Returns the path if loaded, otherwise None.
    """
    for relative_path in ENV_SEARCH_PATHS:
        env_path = base_dir / relative_path
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            return env_path
    return None


# ---- CLI -------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a security audit on a GitHub repository"
    )
    parser.add_argument(
        "repo_url",
        help="GitHub repository URL to audit"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run a full (deeper) scan"
    )
    return parser.parse_args()


# ---- Main ------------------------------------------------------

def main() -> None:
    base_dir = Path(__file__).resolve().parent

    env_path = load_environment(base_dir)
    if not env_path:
        print("ERROR: Could not find a .env file")
        sys.exit(1)

    print(f"Loaded environment from: {env_path}\n")

    print("Environment variables:")
    for key in ENV_VARS_TO_DISPLAY:
        print(f"{key}: {os.getenv(key, 'Not set')}")

    # Windows-specific fixes
    fix_win32_unicode()
    enable_long_paths()

    # Runtime configuration
    configure_logger()
    optimize_cpu_settings()

    args = parse_args()

    orchestrator = AuditOrchestrator()
    report = orchestrator.audit_repository(
        args.repo_url,
        full_scan=args.full
    )

    print(f"\nAudit completed! Report saved to: {report.file_path}")


if __name__ == "__main__":
    main()
