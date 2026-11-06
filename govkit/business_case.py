"""NPV, payback and ROI from explicit assumptions, plus a tornado sensitivity."""
import yaml

DRIVERS = ("upfront_cost", "monthly_run_cost", "monthly_benefit_at_full",
           "discount_rate_annual")


def load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def analyze(a):
    h = int(a["horizon_months"])
    ramp = a["ramp_months"]
    i = (1 + a["discount_rate_annual"]) ** (1 / 12) - 1
    npv = -a["upfront_cost"]
    cum = -a["upfront_cost"]
    payback = None
    benefits = costs = 0.0
    costs = a["upfront_cost"]
    for m in range(1, h + 1):
        frac = min(1.0, m / ramp) if ramp > 0 else 1.0
        ben = a["monthly_benefit_at_full"] * frac
        net = ben - a["monthly_run_cost"]
        benefits += ben
        costs += a["monthly_run_cost"]
        npv += net / (1 + i) ** m
        cum += net
        if payback is None and cum >= 0:
            payback = m
    return {"npv": round(npv, 2), "payback_month": payback,
            "roi": round((benefits - costs) / costs, 4)}


def tornado(a, pct=0.2, top=3):
    rows = []
    for d in DRIVERS:
        lo = analyze({**a, d: a[d] * (1 - pct)})["npv"]
        hi = analyze({**a, d: a[d] * (1 + pct)})["npv"]
        rows.append({"driver": d, "npv_low": lo, "npv_high": hi,
                     "swing": round(abs(hi - lo), 2)})
    rows.sort(key=lambda r: (-r["swing"], r["driver"]))
    return rows[:top]


def report(a):
    r = analyze(a)
    pb = "never within horizon" if r["payback_month"] is None else r["payback_month"]
    lines = ["# Business case (ILLUSTRATIVE assumptions, fictional)", "",
             f"npv: {r['npv']:.2f}", f"payback month: {pb}",
             f"roi: {r['roi']:.4f}", "",
             "tornado, 3 biggest drivers at +/-20%:",
             "driver | npv at -20% | npv at +20% | swing"]
    for t in tornado(a):
        lines.append(f"{t['driver']} | {t['npv_low']:.2f} | {t['npv_high']:.2f} | {t['swing']:.2f}")
    return "\n".join(lines) + "\n"
