"""Maturity scorer over the four NIST AI RMF functions."""
import yaml


def load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def score(data):
    rows = []
    for name, f in data["functions"].items():
        evidence = f.get("evidence") or {}
        proven = 0
        while evidence.get(proven + 1):
            proven += 1
        effective = min(f["claimed"], proven)
        gaps = []
        if effective < f["claimed"]:
            nxt = effective + 1
            gaps.append(f"claimed {f['claimed']} but level {nxt} has no evidence: "
                        f"{data['levels'][nxt]}")
        if effective < f["target"]:
            gaps.append(f"target {f['target']} not reached (effective {effective})")
        rows.append({"function": name, "claimed": f["claimed"],
                     "effective": effective, "target": f["target"], "gaps": gaps})
    return rows


def report(data):
    rows = score(data)
    lines = ["# Maturity (fictional, synthetic)", "",
             "function | claimed | effective | target"]
    for r in rows:
        lines.append(f"{r['function']} | {r['claimed']} | {r['effective']} | {r['target']}")
    lines += ["", "gaps:"]
    n = 0
    for r in rows:
        for g in r["gaps"]:
            lines.append(f"- {r['function']}: {g}")
            n += 1
    if n == 0:
        lines.append("- none")
    return "\n".join(lines) + "\n"
