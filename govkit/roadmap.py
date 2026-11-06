"""Turn a ranked backlog into quarters under a capacity limit with dependencies."""
import datetime


class CycleError(ValueError):
    """The dependency graph contains a cycle."""


def _quarter_names(start, n):
    year, q = int(start[:4]), int(start[-1])
    names = []
    for _ in range(n):
        names.append(f"{year}-Q{q}")
        q += 1
        if q == 5:
            year, q = year + 1, 1
    return names


def schedule(items, capacity, start="2027-Q1"):
    """items are in priority order. A dependency must land in an earlier quarter."""
    ids = {it["id"]: i for i, it in enumerate(items)}
    for it in items:
        if it["effort"] > capacity:
            raise ValueError(f"{it['id']}: effort {it['effort']} exceeds capacity {capacity}")
        for d in it["deps"]:
            if d not in ids:
                raise ValueError(f"{it['id']}: unknown dependency {d}")
    done, pos, used = set(), {}, {}
    remaining = list(items)
    while remaining:
        ready = [it for it in remaining if all(d in done for d in it["deps"])]
        if not ready:
            raise CycleError("dependency cycle among: "
                             + ", ".join(sorted(it["id"] for it in remaining)))
        it = min(ready, key=lambda x: ids[x["id"]])
        q = max([pos[d] + 1 for d in it["deps"]], default=0)
        while used.get(q, 0) + it["effort"] > capacity:
            q += 1
        used[q] = used.get(q, 0) + it["effort"]
        pos[it["id"]] = q
        done.add(it["id"])
        remaining.remove(it)
    names = _quarter_names(start, max(pos.values()) + 1)
    plan = {n: [] for n in names}
    for it in items:
        plan[names[pos[it["id"]]]].append(it["id"])
    return plan


def _dates(quarter):
    year, q = int(quarter[:4]), int(quarter[-1])
    begin = datetime.date(year, 3 * q - 2, 1)
    nyear, nq = (year + 1, 1) if q == 4 else (year, q + 1)
    end = datetime.date(nyear, 3 * nq - 2, 1)
    return begin, (end - begin).days


def render(plan, items, capacity):
    by_id = {it["id"]: it for it in items}
    lines = ["# Roadmap (generated; fictional company, synthetic data)", "",
             f"Capacity per quarter: {capacity} effort points.", "",
             "quarter | load | items"]
    for q, ids in plan.items():
        load = sum(by_id[i]["effort"] for i in ids)
        lines.append(f"{q} | {load:g}/{capacity:g} | "
                     + "; ".join(f"{i} {by_id[i]['title']}" for i in ids))
    lines += ["", "```mermaid", "gantt", "    dateFormat YYYY-MM-DD",
              "    title Governance roadmap (fictional)"]
    for q, ids in plan.items():
        begin, days = _dates(q)
        lines.append(f"    section {q}")
        for i in ids:
            lines.append(f"    {i} {by_id[i]['title'].replace(':', ' ')} "
                         f":{i}, {begin.isoformat()}, {days}d")
    lines.append("```")
    return "\n".join(lines) + "\n"
