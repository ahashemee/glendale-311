"""Fail if any notebook under notebooks/ has cell outputs or execution counts.

Fix a failing notebook with:
    jupyter nbconvert --clear-output --inplace notebooks/<file>.ipynb
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def problems(path):
    nb = json.loads(path.read_text(encoding="utf-8"))
    found = []
    for i, cell in enumerate(nb.get("cells", []), start=1):
        if cell.get("cell_type") != "code":
            continue
        if cell.get("outputs"):
            found.append(f"cell {i} has {len(cell['outputs'])} output(s)")
        if cell.get("execution_count") is not None:
            found.append(f"cell {i} has execution_count {cell['execution_count']}")
    return found


def main():
    notebooks = sorted((ROOT / "notebooks").glob("**/*.ipynb"))
    notebooks = [p for p in notebooks if ".ipynb_checkpoints" not in p.parts]
    dirty = 0
    for nb in notebooks:
        rel = nb.relative_to(ROOT).as_posix()
        try:
            found = problems(nb)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            found = [f"not valid notebook JSON ({exc})"]
        for msg in found:
            print(f"::error file={rel}::{msg}")
        if found:
            dirty += 1
    print(f"Checked {len(notebooks)} notebook(s); {dirty} not clean.")
    if dirty:
        print("Run: jupyter nbconvert --clear-output --inplace <notebook> and commit again.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
