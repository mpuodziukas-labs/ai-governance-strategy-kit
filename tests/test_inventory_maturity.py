import copy

from govkit import inventory, maturity

GOOD = {
    "id": "S-X", "name": "Demo", "owner": "Head of Data", "purpose": "demo",
    "data_classes": ["synthetic"], "risk_tier": "limited",
    "rmf_functions": ["govern", "map"], "sourcing": "built",
    "human_oversight": "",
}


def test_valid_system_passes():
    assert inventory.validate([GOOD]) == []


def test_missing_owner_rejected():
    s = copy.deepcopy(GOOD)
    s["owner"] = ""
    assert any("owner" in e for e in inventory.validate([s]))


def test_unknown_tier_rejected():
    s = copy.deepcopy(GOOD)
    s["risk_tier"] = "medium-ish"
    assert any("risk_tier" in e for e in inventory.validate([s]))


def test_high_risk_without_oversight_rejected():
    s = copy.deepcopy(GOOD)
    s["risk_tier"] = "high"
    assert any("human_oversight" in e for e in inventory.validate([s]))
    s["human_oversight"] = "Clinician signs off every output"
    assert inventory.validate([s]) == []


def test_duplicate_id_and_bad_function_rejected():
    s = copy.deepcopy(GOOD)
    s["rmf_functions"] = ["govern", "nonsense"]
    errs = inventory.validate([s, copy.deepcopy(GOOD)])
    assert any("duplicate" in e for e in errs)
    assert any("rmf_functions" in e for e in errs)


def test_real_inventory_has_twelve_and_validates():
    systems = inventory.load("data/inventory.yaml")
    assert len(systems) == 12
    assert inventory.validate(systems) == []
    assert "high" in {s["risk_tier"] for s in systems}


DATA = {
    "levels": {1: "a", 2: "b", 3: "c", 4: "d", 5: "e"},
    "functions": {
        "Govern": {"claimed": 3, "target": 4,
                   "evidence": {1: ["x"], 2: ["y"], 3: ["z"]}},
        "Map": {"claimed": 4, "target": 4,
                "evidence": {1: ["x"], 2: ["y"], 4: ["w"]}},
        "Measure": {"claimed": 2, "target": 2, "evidence": {}},
    },
}


def test_level_without_evidence_caps_below():
    rows = {r["function"]: r for r in maturity.score(DATA)}
    assert rows["Govern"]["effective"] == 3
    assert rows["Map"]["effective"] == 2  # level 3 has no evidence
    assert rows["Measure"]["effective"] == 0
    assert rows["Map"]["gaps"], "capped function must list a gap"


def test_claim_is_never_raised_by_evidence():
    data = copy.deepcopy(DATA)
    data["functions"]["Govern"]["claimed"] = 1
    rows = {r["function"]: r for r in maturity.score(data)}
    assert rows["Govern"]["effective"] == 1


def test_real_maturity_has_four_functions():
    data = maturity.load("data/maturity.yaml")
    rows = maturity.score(data)
    assert [r["function"] for r in rows] == ["Govern", "Map", "Measure", "Manage"]
    assert any(r["effective"] < r["claimed"] for r in rows)
