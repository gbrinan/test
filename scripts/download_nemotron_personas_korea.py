"""Download the nvidia/Nemotron-Personas-Korea dataset from Hugging Face Hub.

Downloads the full dataset snapshot into data/nemotron-personas-korea/ using
huggingface_hub.snapshot_download, then attempts to load it with the
`datasets` library to report row counts and splits.

Usage:
    python scripts/download_nemotron_personas_korea.py

Notes:
    - If the dataset is gated/requires authentication, this script will
      surface the exact error from huggingface_hub and exit without
      attempting any interactive login or credential entry.
    - Set the HF_TOKEN environment variable (or run `huggingface-cli login`
      beforehand) if authentication is required and you have access.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ID = "nvidia/Nemotron-Personas-Korea"
REPO_TYPE = "dataset"

# Resolve paths relative to this script's location (project root / data / ...)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
LOCAL_DIR = PROJECT_ROOT / "data" / "nemotron-personas-korea"


def download_snapshot() -> Path:
    """Download the dataset repo snapshot to LOCAL_DIR using huggingface_hub."""
    from huggingface_hub import snapshot_download
    from huggingface_hub.errors import GatedRepoError, RepositoryNotFoundError

    LOCAL_DIR.mkdir(parents=True, exist_ok=True)

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")

    print(f"Downloading '{REPO_ID}' (type={REPO_TYPE}) to: {LOCAL_DIR}")
    try:
        local_path = snapshot_download(
            repo_id=REPO_ID,
            repo_type=REPO_TYPE,
            local_dir=str(LOCAL_DIR),
            token=token,
        )
    except GatedRepoError as e:
        print("\n[AUTH REQUIRED] This dataset is gated and requires Hugging Face "
              "authentication with granted access.")
        print(f"Exact error: {e}")
        sys.exit(2)
    except RepositoryNotFoundError as e:
        print("\n[NOT FOUND / AUTH REQUIRED] Repository not found or you do not "
              "have permission to access it (this can also happen for gated "
              "or private repos when unauthenticated).")
        print(f"Exact error: {e}")
        sys.exit(2)
    except Exception as e:  # noqa: BLE001 - surface any other auth/network errors clearly
        msg = str(e)
        print(f"\n[ERROR] Download failed: {type(e).__name__}: {msg}")
        if "401" in msg or "403" in msg or "gated" in msg.lower() or "authentication" in msg.lower():
            print("This looks like an authentication/authorization error. "
                  "Set HF_TOKEN env var with a token that has access, or run "
                  "'huggingface-cli login'. Not attempting any workaround.")
            sys.exit(2)
        raise

    print(f"\nDownload complete. Local path: {local_path}")
    return Path(local_path)


def summarize_directory(path: Path) -> None:
    """Print total size and top-level file/directory structure."""
    total_size = 0
    file_count = 0
    top_level_entries = sorted(path.iterdir()) if path.exists() else []

    for root, _dirs, files in os.walk(path):
        for f in files:
            fp = Path(root) / f
            try:
                total_size += fp.stat().st_size
                file_count += 1
            except OSError:
                pass

    def human_size(n: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if n < 1024:
                return f"{n:.2f} {unit}"
            n /= 1024
        return f"{n:.2f} PB"

    print("\n=== Download Summary ===")
    print(f"Local directory: {path}")
    print(f"Total size: {human_size(total_size)} ({total_size} bytes)")
    print(f"Total file count: {file_count}")
    print("\nTop-level entries:")
    for entry in top_level_entries:
        marker = "DIR " if entry.is_dir() else "FILE"
        try:
            size = entry.stat().st_size if entry.is_file() else 0
        except OSError:
            size = 0
        print(f"  [{marker}] {entry.name}" + (f" ({human_size(size)})" if entry.is_file() else ""))


def try_load_with_datasets() -> None:
    """Attempt to load the dataset via the `datasets` library to report splits/rows."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("\n[INFO] `datasets` library not available; skipping row/split summary.")
        return

    print("\n=== Attempting to load dataset metadata via `datasets` library ===")
    try:
        ds = load_dataset(REPO_ID)
    except Exception as e:  # noqa: BLE001
        print(f"[INFO] Could not load via `datasets.load_dataset`: {type(e).__name__}: {e}")
        print("This is often fine if the dataset uses a custom loading script "
              "or non-standard layout; the snapshot download above is still valid.")
        return

    print(f"Splits found: {list(ds.keys())}")
    for split_name, split_data in ds.items():
        print(f"  - {split_name}: {len(split_data)} rows, columns: {split_data.column_names}")


def main() -> None:
    local_path = download_snapshot()
    summarize_directory(local_path)
    try_load_with_datasets()


if __name__ == "__main__":
    main()
