"""Run a coach's eval cases and report how it did.

Usage:
    python -m evals.runner new-leaf-coach                 # recorded replies, no network
    python -m evals.runner new-leaf-coach --live URL      # ask the real coach
    python -m evals.runner new-leaf-coach --report        # also write reports/<coach>.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

import yaml

from . import checks as C

ROOT = Path(__file__).resolve().parent.parent
COACHES = ROOT / "coaches"
GLOBAL = ["no_em_dashes", "uk_spelling", "no_ai_tells", "no_stranded_prepositions"]


def load_coach(name: str) -> tuple[dict, list[dict]]:
    folder = COACHES / name
    if not folder.is_dir():
        sys.exit(f"No coach called '{name}'. Choose one of: {', '.join(p.name for p in COACHES.iterdir())}")
    cfg = yaml.safe_load((folder / "cases.yml").read_text(encoding="utf-8"))
    return cfg, cfg["cases"]


def recorded_replies(name: str) -> dict[str, str]:
    path = COACHES / name / "recorded.yml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}


def ask_live(url: str, conversation: list[dict], timeout: int = 60) -> str:
    """Send the conversation the way the New Leaf front end does:
    POST {"messages": [...]} and read {"reply": "..."}."""
    body = json.dumps({"messages": conversation}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"content-type": "application/json", "user-agent": "ai-coach-evals/1.0 (+https://github.com/elleanderson/ai-coach-evals)"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    if not data.get("reply"):
        raise RuntimeError(data.get("error") or "No reply returned")
    return data["reply"]


def run(name: str, live: str | None = None) -> dict:
    cfg, cases = load_coach(name)
    recorded = {} if live else recorded_replies(name)
    use_global = cfg.get("house_style", True)
    results = []
    for case in cases:
        conv = case["conversation"]
        try:
            reply = ask_live(live, conv) if live else recorded.get(case["id"], "")
        except Exception as e:  # network or coach error counts as a failure
            reply, err = "", str(e)
        else:
            err = "" if reply else "No reply recorded for this case"
        specs = (GLOBAL if use_global else []) + case.get("checks", [])
        outcomes = [C.build(s)(reply, conversation=conv) for s in specs] if reply else []
        passed = bool(reply) and all(o.passed for o in outcomes)
        results.append({"case": case, "reply": reply, "error": err, "outcomes": outcomes, "passed": passed})
    total = len(results)
    ok = sum(r["passed"] for r in results)
    return {
        "coach": cfg.get("name", name), "slug": name, "promise": cfg.get("promise", ""),
        "threshold": cfg.get("pass_threshold", 1.0), "results": results,
        "passed": ok, "total": total, "rate": ok / total if total else 0.0,
        "source": f"live: {live}" if live else "recorded replies",
    }


def print_summary(rep: dict) -> None:
    print(f"\n{rep['coach']}  ({rep['source']})")
    print("-" * 64)
    for r in rep["results"]:
        mark = "PASS" if r["passed"] else "FAIL"
        print(f"{mark}  {r['case']['id']:<28} {r['case']['title']}")
        for o in r["outcomes"]:
            if not o.passed:
                print(f"        x {o.name}: {o.detail}")
        if r["error"]:
            print(f"        x {r['error']}")
    print("-" * 64)
    print(f"{rep['passed']} of {rep['total']} cases passed ({rep['rate']:.0%}). Target: {rep['threshold']:.0%}\n")


def write_report(rep: dict) -> Path:
    out = ROOT / "reports" / f"{rep['slug']}.md"
    lines = [
        f"# Eval Report: {rep['coach']}",
        "",
        f"Run on {dt.date.today():%d %B %Y} against {rep['source']}.",
        "",
        f"**{rep['passed']} of {rep['total']} cases passed ({rep['rate']:.0%}).** The target is {rep['threshold']:.0%}.",
        "",
        "| Case | Why It Matters | Result |",
        "|---|---|---|",
    ]
    for r in rep["results"]:
        fails = "; ".join(f"{o.name} ({o.detail})" for o in r["outcomes"] if not o.passed) or r["error"]
        lines.append(f"| {r['case']['title']} | {r['case'].get('why', '')} | {'Pass' if r['passed'] else 'Fail: ' + fails} |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run eval cases against an AI coach.")
    p.add_argument("coach", help="folder name under coaches/, such as new-leaf-coach")
    p.add_argument("--live", metavar="URL", help="send each case to a live coach endpoint")
    p.add_argument("--report", action="store_true", help="write a Markdown report to reports/")
    a = p.parse_args(argv)
    rep = run(a.coach, a.live)
    print_summary(rep)
    if a.report:
        print(f"Report written to {write_report(rep).relative_to(ROOT)}")
    return 0 if rep["rate"] >= rep["threshold"] else 1


if __name__ == "__main__":
    sys.exit(main())
