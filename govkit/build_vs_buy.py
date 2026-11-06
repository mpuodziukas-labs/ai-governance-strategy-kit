"""Weighted build-vs-buy matrix with a per-criterion flip-point analysis."""
from fractions import Fraction

import yaml


def load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _two(data):
    names = list(data["options"])
    if len(names) != 2:
        raise ValueError("exactly two options required")
    return names


def _frac(x):
    return Fraction(str(x))


def decide(data):
    a, b = _two(data)
    w = {c: _frac(v) for c, v in data["criteria"].items()}
    total_w = sum(w.values())
    totals = {n: sum(w[c] * _frac(data["options"][n][c]) for c in w) / total_w
              for n in (a, b)}
    winner = a if totals[a] >= totals[b] else b  # tie goes to the first-listed option
    return {"winner": winner, "totals": {n: float(t) for n, t in totals.items()}}


def flip_points(data):
    """Weight of each criterion at which the two options tie (others fixed).

    Above or below that weight (depending on the sign of the score gap) the
    winner changes. None means the criterion cannot flip the decision.
    """
    a, b = _two(data)
    w = {c: _frac(v) for c, v in data["criteria"].items()}
    d = {c: _frac(data["options"][b][c]) - _frac(data["options"][a][c]) for c in w}
    out = []
    for c in data["criteria"]:
        rest = sum(w[o] * d[o] for o in w if o != c)
        flip = None
        if d[c] != 0 and -rest / d[c] > 0:
            flip = float(-rest / d[c])
        out.append({"criterion": c, "weight": float(w[c]), "flip_weight": flip})
    return out


def report(data):
    d = decide(data)
    a, b = _two(data)
    lines = ["# Build vs buy (fictional, synthetic)", "",
             f"{a}: {d['totals'][a]:.3f}", f"{b}: {d['totals'][b]:.3f}",
             f"decision: {d['winner']}", "",
             "criterion | weight | flip weight"]
    for f in flip_points(data):
        fw = "none" if f["flip_weight"] is None else f"{f['flip_weight']:.3f}"
        lines.append(f"{f['criterion']} | {f['weight']:g} | {fw}")
    return "\n".join(lines) + "\n"
