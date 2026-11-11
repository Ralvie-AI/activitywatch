import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

FILE_TIMESTAMP_RE = re.compile(
    r"_(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+Z)"
)

def get_file_timestamp(file_path: Path):
    match = FILE_TIMESTAMP_RE.search(file_path.name)
    if not match:
        return None

    return datetime.strptime(
        match.group(1),
        "%Y-%m-%dT%H-%M-%S.%fZ",
    ).replace(tzinfo=timezone.utc)

def main():
    parser = argparse.ArgumentParser(
        description="Delete screenshots older than timestamp for a given user ID."
    )
    parser.add_argument(
        "user_id",
        type=str,
        help="User ID",
    )
    parser.add_argument(
            "company_id",
            type=str,
            help="Company ID",
        )
    parser.add_argument(
        "timestamp",
        type=str,
        help='Timestamp in ISO format, e.g. "2026-09-17 03:47:08.972000+00:00"',
    )
    parser.add_argument(
        "event",
        type=str.lower,
        choices=["yes", "no"],
        default="yes",
        help="Whether to process event screenshots (yes/no)",
    )
    args = parser.parse_args()

    try:
        cutoff_dt = datetime.fromisoformat(args.timestamp)
    except ValueError as e:
        sys.exit(f"Error parsing timestamp: {e}")

    # Build path dynamically to current Windows user's AppData
    screenshot_dir = (
        Path.home()
        / "AppData"
        / "Local"
        / "Sundial"
        / "Sundial"
        / "EventScreenshots"
        / args.user_id
        / args.company_id
    )

    if not screenshot_dir.exists():
        sys.exit(f"Directory does not exist: {screenshot_dir}")

    if args.event == "yes":
        for file_path in screenshot_dir.glob("*.png"):
            file_timestamp = get_file_timestamp(file_path)
            if file_timestamp and file_timestamp < cutoff_dt:
                try:
                    file_path.unlink()
                except OSError as err:
                    print(f"Failed to delete {file_path.name}: {err}")
    else:
        for file_path in screenshot_dir.glob("*.png"):
            file_timestamp = get_file_timestamp(file_path)
            if file_timestamp and file_timestamp > cutoff_dt:
                try:
                    file_path.unlink()
                except OSError as err:
                    print(f"Failed to delete {file_path.name}: {err}")

if __name__ == "__main__":
    main()

    # python cleanup_screenshot.py "840c895a938ec8cc9f455b89eba91465" "56741d09ff09b3c626fc467fa4734a54" "2026-11-11 03:26:27.828000+00:00" "no"
    