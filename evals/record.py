"""Ask a live coach every case once and save the replies to recorded.yml.

    python -m evals.record new-leaf-coach https://your-coach.example/

Recorded replies let the evals run in CI without calling the coach (or paying
for it) on every commit. Re-record whenever the coach's prompt or model changes.
"""
from __future__ import annotations

import sys
import time

import yaml

from .runner import COACHES, ask_live, load_coach


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    name, url = sys.argv[1], sys.argv[2]
    _, cases = load_coach(name)
    out = {}
    for case in cases:
        out[case["id"]] = ask_live(url, case["conversation"])
        print(f"recorded {case['id']}")
        time.sleep(1)
    path = COACHES / name / "recorded.yml"
    path.write_text(yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
    print(f"Saved {len(out)} replies to {path.relative_to(COACHES.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
