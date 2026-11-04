"""
CampusVoice - Portable Package Exporter
Creates a standalone, clean zip package of the complete project
ready to transfer to any machine or directory.
"""

import os
import zipfile
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_ZIP = ROOT_DIR / "CampusVoice-AI-Platform.zip"

EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    ".pytest_cache",
    ".ruff_cache"
}

EXCLUDE_FILES = {
    "CampusVoice-AI-Platform.zip",
    ".DS_Store",
    "Thumbs.db"
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd"
}

def make_package():
    print(f"[*] Packaging CampusVoice from: {ROOT_DIR}")
    if OUTPUT_ZIP.exists():
        try:
            OUTPUT_ZIP.unlink()
        except Exception as e:
            print(f"[!] Warning removing old zip: {e}")

    file_count = 0
    total_bytes = 0

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(ROOT_DIR):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            rel_root = Path(root).relative_to(ROOT_DIR)

            for file_name in files:
                if file_name in EXCLUDE_FILES:
                    continue
                if any(file_name.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                    continue

                full_path = Path(root) / file_name
                arc_name = rel_root / file_name

                zip_file.write(full_path, arcname=str(arc_name))
                file_count += 1
                total_bytes += full_path.stat().st_size

    zip_size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
    print(f"[+] Package created successfully!")
    print(f"    Target: {OUTPUT_ZIP.name}")
    print(f"    Path:   {OUTPUT_ZIP}")
    print(f"    Files:  {file_count}")
    print(f"    Size:   {zip_size_mb:.2f} MB")
    print(f"\nTo use on any machine:")
    print(f"1. Unzip '{OUTPUT_ZIP.name}' into any folder.")
    print(f"2. Double click 'start_platform.bat' (Windows) or run './start_platform.sh' (Mac/Linux).")
    print(f"3. Open http://127.0.0.1:8000 in your browser.")

if __name__ == "__main__":
    make_package()
