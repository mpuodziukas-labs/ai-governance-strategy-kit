# ai-governance-strategy-kit

[![CI](https://github.com/mpuodziukas-labs/ai-governance-strategy-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/mpuodziukas-labs/ai-governance-strategy-kit/actions/workflows/ci.yml)

AI strategy and governance-program skills as runnable, auditable code. Everything runs over a fictional company, "Northwind Health Analytics". Every number is synthetic.

## What it proves

Seven small modules, each with tests, each producing a checkable artifact:

| Module | Artifact |
| --- | --- |
| `inventory` | 12-system AI inventory; validator rejects missing owners, unknown risk tiers, and high-risk systems with no human-oversight field |
| `maturity` | NIST AI RMF function scorer, levels 1-5; a level without evidence caps at the level below |
| `prioritize` | Backlog ranked by (impact x likelihood) x value / effort, ties by id, plus a +/-20% weight sensitivity check |
| `build_vs_buy` | Weighted matrix with the weight at which each criterion flips the decision |
| `business_case` | NPV, payback month, ROI, and a tornado on the 3 biggest drivers |
| `roadmap` | Ranked backlog placed into quarters under a capacity limit; a dependency cycle is a hard error |
| `kpi` | KPI register checker: flags missing baselines and targets that are not measurable |

## 60-second run

```
python3 -m pip install pytest pyyaml
bash scripts/verify.sh              # pytest, double generation compared byte for byte, selftest, shellcheck, leak grep
bash scripts/verify.sh --selftest   # 4 planted defects and 1 control
```

`verify.sh` prints `GREEN` only when every step passes. It writes the reports to `out/` and `ROADMAP.md`.

## Outputs excerpt

All figures below are printed by the code from the synthetic data files.

```
Map | claimed 4 | effective 2 | target 4        (level 3 has no evidence)
build 3.700, buy 3.350, decision: build
data_control flips the decision at weight 0.500 (current weight 4)
npv: 425154.05, payback month: 18, roi: 0.6037
top driver: monthly_benefit_at_full, NPV swing 517180.37
backlog rank 1: B01 (score 20.000)
roadmap: 5 quarters at capacity 12
selftest 5/5
```

## Honesty Statement

Northwind Health Analytics is a fictional organization. All data in `data/` is synthetic and the business-case assumptions are illustrative, not measured. This is a method demonstration and not a client engagement. The regulatory mappings (risk tiers and framework functions) are the author's reading and are not legal advice.

## Limitations

- Scores and maturity levels are inputs from a self-assessment; the code checks consistency and evidence, not truth.
- Weights in the prioritization are exponents on each factor, one of several defensible choices.
- Flip points vary one criterion at a time with the others held fixed.
- The business case is a deterministic model with no uncertainty distribution; the tornado is a one-at-a-time sensitivity.
- The roadmap treats a dependency as finishing in an earlier quarter and does not model partial progress.
- Risk tiers are labels the author assigned to fictional systems; no real system was classified.

## License

MIT, see `LICENSE`.
