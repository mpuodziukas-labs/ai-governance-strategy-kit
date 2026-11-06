"""Risk-based backlog ranking with a +/-20% weight sensitivity check.

score = (impact x likelihood) x value / effort. Weights are exponents on each
factor (base 1.0), so scaling a weight changes how much that factor matters.
"""
import csv

FACTORS = ("impact", "likelihood", "value", "effort")
BASE = {f: 1.0 for f in FACTORS}


def load(path):
    items = []
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            it = {"id": row["id"], "title": row["title"],
                  "deps": [d for d in row["deps"].split(";") if d]}
            for f in FACTORS:
                it[f] = float(row[f])
            items.append(it)
    return items


def rank(items, weights=None):
    w = {**BASE, **(weights or {})}
    out = []
    for it in items:
        if it["effort"] <= 0:
            raise ValueError(f"{it['id']}: effort must be positive")
        s = (it["impact"] ** w["impact"] * it["likelihood"] ** w["likelihood"]
             * it["value"] ** w["value"] / it["effort"] ** w["effort"])
        out.append({**it, "score": round(s, 9)})
    return sorted(out, key=lambda x: (-x["score"], x["id"]))


def sensitivity(items, pct=0.2):
    base = {x["id"]: i for i, x in enumerate(rank(items))}
    moved = {}
    for f in FACTORS:
        for sign, tag in ((1 + pct, "+"), (1 - pct, "-")):
            alt = {x["id"]: i for i, x in enumerate(rank(items, {f: sign}))}
            for iid, pos in alt.items():
                if pos != base[iid]:
                    moved.setdefault(iid, []).append(f"{tag}{int(pct * 100)}% {f}: "
                                                     f"{base[iid] + 1}->{pos + 1}")
    return [{"id": i, "base_rank": base[i] + 1, "scenarios": moved[i]}
            for i in sorted(moved, key=lambda k: (base[k], k))]


def report(items):
    ranked = rank(items)
    lines = ["# Priority backlog (fictional, synthetic)", "",
             "rank | id | score | title"]
    for i, x in enumerate(ranked, 1):
        lines.append(f"{i} | {x['id']} | {x['score']:.3f} | {x['title']}")
    lines += ["", "rank changes under +/-20% weights:"]
    changed = sensitivity(items)
    if not changed:
        lines.append("- none")
    for c in changed:
        lines.append(f"- {c['id']} (rank {c['base_rank']}): {'; '.join(c['scenarios'])}")
    return "\n".join(lines) + "\n"
