import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable

steps = [
    "collector.py",
    "transform_data.py",
    "data_quality.py",
    "prepare_database.py",
    "load_to_database.py",
]

for step in steps:
    print()
    print("=" * 60)
    print(f"Running: {step}")
    print("=" * 60)
    result = subprocess.run(
        [PYTHON, str(PROJECT_ROOT / "src" / step)],
        cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        print()
        print(f"Pipeline stopped. Failed step: {step}")
        sys.exit(result.returncode)

print()
print("=" * 60)
print("PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 60)