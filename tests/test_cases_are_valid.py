"""Every coach folder must contain well-formed cases that the runner understands."""
from pathlib import Path

import yaml

from evals import checks as C

COACHES = Path(__file__).resolve().parent.parent / "coaches"


def test_all_cases_load_and_checks_exist():
    for folder in COACHES.iterdir():
        cfg = yaml.safe_load((folder / "cases.yml").read_text(encoding="utf-8"))
        ids = [c["id"] for c in cfg["cases"]]
        assert len(ids) == len(set(ids)), f"duplicate case ids in {folder.name}"
        for case in cfg["cases"]:
            assert case["conversation"][-1]["role"] == "user"
            for spec in case.get("checks", []):
                C.build(spec)
