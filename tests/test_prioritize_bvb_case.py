import pytest

from govkit import build_vs_buy, business_case, prioritize


def item(i, impact, likelihood, value, effort):
    return {"id": i, "impact": impact, "likelihood": likelihood,
            "value": value, "effort": effort}


def test_score_formula():
    r = prioritize.rank([item("A", 2, 3, 4, 2)])
    assert r[0]["score"] == 12


def test_ties_break_by_id():
    r = prioritize.rank([item("B", 2, 2, 2, 2), item("A", 2, 2, 2, 2)])
    assert [x["id"] for x in r] == ["A", "B"]


def test_zero_effort_rejected():
    with pytest.raises(ValueError):
        prioritize.rank([item("A", 1, 1, 1, 0)])


def test_sensitivity_flags_only_close_items():
    items = [item("A", 5, 5, 5, 1), item("X", 4, 4, 4, 1),
             item("Y", 3, 3, 8, 1), item("Z", 1, 1, 1, 1)]
    ids = {c["id"] for c in prioritize.sensitivity(items)}
    assert ids == {"X", "Y"}


def test_real_backlog_ranks():
    items = prioritize.load("data/backlog.csv")
    assert len(items) >= 8
    assert prioritize.rank(items)[0]["score"] >= prioritize.rank(items)[-1]["score"]


BVB = {
    "criteria": {"a": 1, "b": 1},
    "options": {"build": {"a": 5, "b": 1}, "buy": {"a": 2, "b": 3}},
}


def test_decision_and_flip_points():
    d = build_vs_buy.decide(BVB)
    assert d["winner"] == "build"
    assert d["totals"]["build"] == 3
    assert d["totals"]["buy"] == 2.5
    flips = {f["criterion"]: f["flip_weight"] for f in build_vs_buy.flip_points(BVB)}
    assert flips["b"] == 1.5
    assert abs(flips["a"] - 2 / 3) < 1e-9


def test_flip_weight_really_flips():
    lo = {**BVB, "criteria": {"a": 1, "b": 1.4}}
    hi = {**BVB, "criteria": {"a": 1, "b": 1.6}}
    assert build_vs_buy.decide(lo)["winner"] == "build"
    assert build_vs_buy.decide(hi)["winner"] == "buy"


def test_no_flip_when_criterion_is_neutral():
    data = {"criteria": {"a": 1, "b": 1},
            "options": {"build": {"a": 5, "b": 3}, "buy": {"a": 2, "b": 3}}}
    flips = {f["criterion"]: f["flip_weight"] for f in build_vs_buy.flip_points(data)}
    assert flips["b"] is None


ASSUME = {
    "discount_rate_annual": 0.0, "upfront_cost": 1200, "monthly_run_cost": 0,
    "monthly_benefit_at_full": 200, "ramp_months": 0, "horizon_months": 12,
}


def test_npv_payback_roi():
    r = business_case.analyze(ASSUME)
    assert r["npv"] == 1200
    assert r["payback_month"] == 6
    assert r["roi"] == 1.0


def test_never_pays_back():
    r = business_case.analyze({**ASSUME, "monthly_benefit_at_full": 50})
    assert r["payback_month"] is None


def test_tornado_top3_sorted():
    a = {**ASSUME, "discount_rate_annual": 0.1, "monthly_run_cost": 30}
    t = business_case.tornado(a)
    assert len(t) == 3
    swings = [x["swing"] for x in t]
    assert swings == sorted(swings, reverse=True)
    assert t[0]["driver"] == "monthly_benefit_at_full"
