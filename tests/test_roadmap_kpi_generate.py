import filecmp

import pytest

from govkit import generate, kpi, roadmap


def it(i, effort, deps=()):
    return {"id": i, "title": "T" + i, "effort": effort, "deps": list(deps)}


def test_dependency_lands_in_later_quarter():
    plan = roadmap.schedule([it("A", 5, ["B"]), it("B", 5)], capacity=20)
    pos = {i: q for q, ids in plan.items() for i in ids}
    assert pos["B"] != pos["A"]
    assert list(plan).index(pos["B"]) < list(plan).index(pos["A"])


def test_cycle_is_hard_error():
    with pytest.raises(roadmap.CycleError):
        roadmap.schedule([it("A", 1, ["B"]), it("B", 1, ["A"])], capacity=10)


def test_unknown_dep_and_oversize_item_rejected():
    with pytest.raises(ValueError):
        roadmap.schedule([it("A", 1, ["Z"])], capacity=10)
    with pytest.raises(ValueError):
        roadmap.schedule([it("A", 11)], capacity=10)


def test_capacity_respected_and_priority_first():
    items = [it("A", 8), it("B", 8), it("C", 8)]
    plan = roadmap.schedule(items, capacity=10)
    efforts = {i["id"]: i["effort"] for i in items}
    for ids in plan.values():
        assert sum(efforts[i] for i in ids) <= 10
    assert plan["2027-Q1"] == ["A"]


def test_render_has_gantt():
    md = roadmap.render(roadmap.schedule([it("A", 1)], capacity=5),
                        [it("A", 1)], capacity=5)
    assert "```mermaid" in md and "gantt" in md


def k(**kw):
    base = {"id": "K1", "name": "n", "unit": "%", "direction": "up",
            "baseline": 10, "target": 20, "owner": "Ops",
            "band": {"amber": 0.5, "green": 0.9}}
    base.update(kw)
    return base


def test_kpi_valid_passes():
    assert kpi.check([k()]) == []


@pytest.mark.parametrize("kw,word", [
    ({"baseline": None}, "baseline"),
    ({"target": None}, "target"),
    ({"target": "improve a lot"}, "measurable"),
    ({"target": 10}, "measurable"),
    ({"target": 5}, "measurable"),
    ({"owner": ""}, "owner"),
])
def test_kpi_defects_flagged(kw, word):
    assert any(word in e for e in kpi.check([k(**kw)]))


def test_kpi_status_band():
    assert kpi.status(k(current=19)) == "green"
    assert kpi.status(k(current=16)) == "amber"
    assert kpi.status(k(current=11)) == "red"


def test_real_kpis_clean():
    assert kpi.check(kpi.load("data/kpis.yaml")) == []


def test_generate_is_deterministic(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    names = generate.main(str(a))
    generate.main(str(b))
    assert len(names) >= 7
    for n in names:
        assert (a / n).stat().st_size > 0
        assert filecmp.cmp(a / n, b / n, shallow=False)
