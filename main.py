import os
import sys
from src.agents.orchestrator import AuditOrchestrator
from src.utils.logger import configure_logger
from src.utils.windows_fixes import enable_long_paths, fix_win32_unicode
from src.utils.cpu_optimization import optimize_cpu_settings

if __name__ == "__main__":
    
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