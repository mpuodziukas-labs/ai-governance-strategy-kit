"""Planted-defect selftest: 4 defects must be caught, 1 control must be accepted."""
import copy
import sys

from govkit import inventory, kpi, maturity, roadmap

SYSTEM = {"id": "S", "name": "n", "owner": "o", "purpose": "p",
          "data_classes": ["d"], "risk_tier": "high", "rmf_functions": ["govern"],
          "sourcing": "built", "human_oversight": "Reviewer signs off"}
MATURITY = {"levels": {i: "x" for i in range(1, 6)},
            "functions": {"Govern": {"claimed": 3, "target": 3,
                                     "evidence": {1: ["a"], 2: ["b"], 3: ["c"]}}}}
KPI = {"id": "K", "name": "n", "unit": "%", "direction": "up", "baseline": 1,
       "target": 2, "owner": "o", "band": {"amber": 0.5, "green": 0.9}}
ITEMS = [{"id": "A", "title": "a", "effort": 1, "deps": ["B"]},
         {"id": "B", "title": "b", "effort": 1, "deps": []}]


def case_oversight():
    s = copy.deepcopy(SYSTEM)
    s["human_oversight"] = ""
    return bool(inventory.validate([s]))


def case_maturity():
    m = copy.deepcopy(MATURITY)
    m["functions"]["Govern"]["evidence"] = {1: ["a"]}
    return maturity.score(m)[0]["effective"] < 3


def case_cycle():
    items = copy.deepcopy(ITEMS)
    items[1]["deps"] = ["A"]
    try:
        roadmap.schedule(items, capacity=5)
    except roadmap.CycleError:
        return True
    return False


def case_kpi():
    k = copy.deepcopy(KPI)
    k["baseline"] = None
    return bool(kpi.check([k]))


def case_control():
    return (inventory.validate([SYSTEM]) == []
            and maturity.score(MATURITY)[0]["effective"] == 3
            and bool(roadmap.schedule(copy.deepcopy(ITEMS), capacity=5))
            and kpi.check([KPI]) == [])


CASES = (("high-risk without oversight is rejected", case_oversight),
         ("maturity claimed without evidence is capped", case_maturity),
         ("dependency cycle is a hard error", case_cycle),
         ("KPI without baseline is flagged", case_kpi),
         ("control: clean inputs are accepted", case_control))


def main():
    passed = 0
    for name, fn in CASES:
        ok = bool(fn())
        passed += ok
        print(("PASS " if ok else "FAIL ") + name)
    print(f"selftest {passed}/{len(CASES)}")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
