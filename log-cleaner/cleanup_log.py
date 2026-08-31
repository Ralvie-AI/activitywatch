import os
import time
from pathlib import Path


LOG_DIR = (
    Path(os.environ["LOCALAPPDATA"])
    / "Sundial"
    / "Sundial"
    / "Logs"
)

DAYS_THRESHOLD = 180  # Approx. 6 months

def cleanup_activity_logs(log_directory: str, days: int):
    target_path = Path(log_directory)

    if not target_path.exists() or not target_path.is_dir():
        print(f"Error: Directory '{log_directory}' does not exist or is not a directory.")
        return

    # Calculate cutoff timestamp (180 days ago)
    cutoff_time = time.time() - (days * 86400)
    
    print(f"Scanning '{log_directory}' for .log files older than {days} days...")

    for file_path in target_path.rglob("*.log*"):
        if file_path.is_file():
            try:
                # Check last modified timestamp
                file_mtime = file_path.stat().st_mtime
                
                if file_mtime < cutoff_time:
                    file_path.unlink()

            except Exception as e:
                print(f"Failed to process {file_path}: {e}")

if __name__ == "__main__":
    cleanup_activity_logs(LOG_DIR, DAYS_THRESHOLD)
    