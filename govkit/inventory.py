"""AI system inventory schema and validator."""
import yaml

TIERS = ("unacceptable", "high", "limited", "minimal")
FUNCTIONS = ("govern", "map", "measure", "manage")
SOURCING = ("built", "vendor")
REQUIRED = ("id", "name", "owner", "purpose", "data_classes",
            "risk_tier", "rmf_functions", "sourcing")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)["systems"]


def validate(systems):
    errors, seen = [], set()
    for s in systems:
        sid = s.get("id") or "<no id>"
        for key in REQUIRED:
            if s.get(key) in (None, "", []):
                errors.append(f"{sid}: missing {key}")
        if sid in seen:
            errors.append(f"{sid}: duplicate id")
        seen.add(sid)
        if s.get("risk_tier") and s["risk_tier"] not in TIERS:
            errors.append(f"{sid}: unknown risk_tier {s['risk_tier']!r}")
        if s.get("sourcing") and s["sourcing"] not in SOURCING:
            errors.append(f"{sid}: unknown sourcing {s['sourcing']!r}")
        for f in s.get("rmf_functions") or []:
            if f not in FUNCTIONS:
                errors.append(f"{sid}: unknown rmf_functions entry {f!r}")
        if s.get("risk_tier") in ("high", "unacceptable") \
                and not (s.get("human_oversight") or "").strip():
            errors.append(f"{sid}: {s['risk_tier']} system needs human_oversight")
    return errors


def report(systems):
    lines = ["# Inventory (fictional, synthetic)", ""]
    lines.append(f"systems: {len(systems)}")
    for tier in TIERS:
        n = sum(1 for s in systems if s["risk_tier"] == tier)
        lines.append(f"tier {tier}: {n}")
    for fn in FUNCTIONS:
        n = sum(1 for s in systems if fn in s["rmf_functions"])
        lines.append(f"covers {fn}: {n}/{len(systems)}")
    built = sum(1 for s in systems if s["sourcing"] == "built")
    lines.append(f"built: {built}, vendor: {len(systems) - built}")
    lines.append("")
    lines.append("id | tier | sourcing | owner")
    for s in sorted(systems, key=lambda x: x["id"]):
        lines.append(f"{s['id']} | {s['risk_tier']} | {s['sourcing']} | {s['owner']}")
    return "\n".join(lines) + "\n"
