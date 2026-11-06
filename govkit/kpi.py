"""KPI/OKR register checker: baseline, measurable target, band, owner."""
import yaml


def load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)["kpis"]


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def check(kpis):
    errors = []
    for k in kpis:
        kid = k.get("id") or "<no id>"
        if not _num(k.get("baseline")):
            errors.append(f"{kid}: missing baseline")
        if k.get("target") is None:
            errors.append(f"{kid}: missing target")
        elif not _num(k["target"]):
            errors.append(f"{kid}: target {k['target']!r} is not measurable (needs a number)")
        elif _num(k.get("baseline")):
            up = k.get("direction") == "up"
            ok = k["target"] > k["baseline"] if up else k["target"] < k["baseline"]
            if k.get("direction") not in ("up", "down") or not ok:
                errors.append(f"{kid}: target {k['target']} is not measurable progress "
                              f"from baseline {k['baseline']} (direction {k.get('direction')})")
        if not (k.get("owner") or "").strip():
            errors.append(f"{kid}: missing owner")
        band = k.get("band") or {}
        if not (_num(band.get("amber")) and _num(band.get("green"))
                and 0 < band["amber"] < band["green"] <= 1):
            errors.append(f"{kid}: band needs 0 < amber < green <= 1")
    return errors


def status(k):
    att = (k["current"] - k["baseline"]) / (k["target"] - k["baseline"])
    if att >= k["band"]["green"]:
        return "green"
    return "amber" if att >= k["band"]["amber"] else "red"


def report(kpis):
    lines = ["# KPI register (fictional, synthetic)", "",
             "id | baseline | current | target | status | owner"]
    counts = {"green": 0, "amber": 0, "red": 0}
    for k in kpis:
        s = status(k)
        counts[s] += 1
        lines.append(f"{k['id']} | {k['baseline']} | {k['current']} | {k['target']} | "
                     f"{s} | {k['owner']}")
    lines += ["", "green {green}, amber {amber}, red {red}".format(**counts)]
    return "\n".join(lines) + "\n"
