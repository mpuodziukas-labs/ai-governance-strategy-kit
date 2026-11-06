"""Generate every report into a directory. Usage: python3 -m govkit.generate DIR"""
import os
import sys

from govkit import (build_vs_buy, business_case, inventory, kpi, maturity,
                    prioritize, roadmap)

CAPACITY = 12


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    systems = inventory.load("data/inventory.yaml")
    errs = inventory.validate(systems)
    kerrs = kpi.check(kpi.load("data/kpis.yaml"))
    if errs or kerrs:
        raise SystemExit("data invalid:\n" + "\n".join(errs + kerrs))
    ranked = prioritize.rank(prioritize.load("data/backlog.csv"))
    plan = roadmap.schedule(ranked, CAPACITY)
    files = {
        "inventory.txt": inventory.report(systems),
        "maturity.txt": maturity.report(maturity.load("data/maturity.yaml")),
        "prioritize.txt": prioritize.report(prioritize.load("data/backlog.csv")),
        "build_vs_buy.txt": build_vs_buy.report(build_vs_buy.load("data/build_vs_buy.yaml")),
        "business_case.txt": business_case.report(business_case.load("data/assumptions.yaml")),
        "kpi.txt": kpi.report(kpi.load("data/kpis.yaml")),
        "ROADMAP.md": roadmap.render(plan, ranked, CAPACITY),
    }
    for name, text in files.items():
        with open(os.path.join(outdir, name), "w", encoding="utf-8") as fh:
            fh.write(text)
    return sorted(files)


if __name__ == "__main__":
    print("\n".join(main(sys.argv[1])))
