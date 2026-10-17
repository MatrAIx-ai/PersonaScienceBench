"""Does the 'withheld values handed over' measure of logs_check.py separate the disclosure conditions of PR #25?
Same number matching, applied to the GLM-5 behaviour-card chats (neutral, terse, volunteer; 62 OpenFOAM cases x 6).
Inputs are not in this repository: the run directory of PR #25, and from the persona-behaviour-cards branch of
https://github.com/joverwiening/SciConvBench the foam fact cards and the foam disambiguation dataset.
python handover_check.py RUN_DIR persona/fact_cards/foam/disambiguation_foam.cards.json dataset/foam/disambiguation_foam.json
"""
import json, re, random, statistics as st, sys
from collections import defaultdict
from pathlib import Path

RUN = Path(sys.argv[1])
CARDS = json.load(open(sys.argv[2]))["cases"]
OPEN = {x["id"]: x["incomplete_user_req"] for x in json.load(open(sys.argv[3]))}
NUM = re.compile(r"(?<![A-Za-z0-9_.])[-−]?\d+(?:[.,]\d+)?(?:[eE][-−+]?\d+)?")


def nums(t):
    out = set()
    for m in NUM.findall(t or ""):
        s = m.replace("−", "-")
        s = s.replace(",", "") if re.fullmatch(r"-?\d{1,3},\d{3}", s) else s.replace(",", ".")
        try:
            out.add(float(s))
        except ValueError:
            pass
    return out


ARMS = ["bf_neutral", "bv_terse", "bv_volunteer"]
val = defaultdict(lambda: defaultdict(list))  # case -> arm -> [delivered per rep]
for a in ARMS:
    for cdir in sorted(RUN.glob(f"{a}/rep*/foam/bedrock_glm5_Disambiguation/case_*")):
        case = cdir.name
        e = CARDS.get(case)
        if not e or e.get("status") not in ("ok", "needs_review"):
            continue
        cl = cdir / "clarifications.json"
        if not cl.exists():
            continue
        reps = "\n".join(x.get("answer", "") for x in json.load(open(cl)))
        on = nums(OPEN[case])
        shares = []
        for c in e["cards"]:
            cn = nums(c.get("text", "")) - on
            if cn:
                shares.append(len(cn & nums(reps)) / len(cn))
        if shares:
            val[case][a].append(st.mean(shares))

cases = sorted(c for c in val if all(val[c][a] for a in ARMS))
m = {c: {a: st.mean(val[c][a]) for a in ARMS} for c in cases}
print(f"{len(cases)} cases with numeric withheld facts; chats per arm:", {a: sum(len(val[c][a]) for c in cases) for a in ARMS})
for a in ARMS:
    print(f"{a:13s} handed over {st.mean(m[c][a] for c in cases):.3f}")


def boot(v, n=4000):
    r = random.Random(0)
    s = sorted(st.mean(r.choices(v, k=len(v))) for _ in range(n))
    return f"{st.mean(v):+.3f} [{s[int(.025*n)]:+.3f}, {s[int(.975*n)]:+.3f}]"


for x, y in [("bv_volunteer", "bf_neutral"), ("bv_terse", "bf_neutral"), ("bv_volunteer", "bv_terse")]:
    print(f"{x} - {y}: {boot([m[c][x] - m[c][y] for c in cases])}")
