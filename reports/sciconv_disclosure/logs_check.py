"""Do the profiles change what the researcher simulator hands over in the Haiku-actor / Opus-researcher campaign?
SciConvBench episodes only, read from Experiment/shared/haiku_actor_opus_persona_pilot/traces. No model calls.

delivered: per withheld fact (fact_cards.json), share of its numbers that appear in the simulator's replies,
numbers already in the opening request excluded. Facts without numbers are skipped, because profiles 046 and
155 reply in Spanish and Mandarin, where word matching fails.
multi: share of replies carrying numbers from 2 or more withheld facts.
Run from the repo root: python reports/sciconv_disclosure/logs_check.py > reports/sciconv_disclosure/logs_check.txt
"""
import csv, json, re, random, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TR = HERE.parents[1] / "Experiment/shared/haiku_actor_opus_persona_pilot/traces"
rows = [json.loads(l) for l in open(TR / "full-campaign-shared-events.jsonl")]
sc = [r for r in rows if r["benchmark"] == "sciconvbench"]
ARMS = ["persona_off", "candidate_001", "candidate_003", "candidate_046", "candidate_155"]

# no \w in the lookbehind: it would also block numbers right after CJK characters
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


MET = {}
for r in json.load(open(TR / "full-campaign-results.json")):
    for nr in r.get("native_results") or []:
        if nr.get("benchmark") == "sciconvbench":
            MET[(r["task_id"], r["arm"])] = nr["evaluation"]["metrics"]

cards = {k: [c for c in e["cards"] if c.get("text")]
         for k, e in json.load(open(HERE / "fact_cards.json"))["cases"].items()
         if e.get("status") in ("ok", "needs_review")}


def chat(r):
    ev = r["events"]
    opening = next(e["payload"]["message"] for e in ev if e["type"] == "initial_request")
    qs = [e["payload"].get("question", "") for e in ev if e["type"] == "researcher_question"]
    reps = [e["payload"].get("answer", "") for e in ev if e["type"] == "researcher_reply"]
    allrep = "\n".join(reps)
    d = dict(n_q=len(qs), n_rep=len(reps),
             wpr=st.mean([len(x.split()) for x in reps]) if reps else 0.0,
             npr=st.mean([len(nums(x)) for x in reps]) if reps else 0.0,
             cjk=sum(len(re.findall(r"[一-鿿]", x)) for x in reps) / max(1, sum(len(x) for x in reps)),
             score=r["score_0_100"] / 100)
    m = MET.get((r["task_id"], r["arm"]), {})
    if "/disambiguation/" in r["task_id"]:
        d["ent_rec"] = float(m.get("entity_recovery", float("nan")))
        d["ic"] = float(m.get("intent_capture", float("nan")))
        d["FR"] = float(m.get("FR", float("nan")))
    cs = cards.get(r["task_id"])
    if cs is not None:
        on = nums(opening)
        shares, sets = [], []
        for c in cs:
            cn = nums(c["text"]) - on
            sets.append(cn)
            if cn:
                shares.append(len(cn & nums(allrep)) / len(cn))
        d["delivered"] = st.mean(shares) if shares else float("nan")
        multi = [sum(1 for s in sets if s and (s & nums(x))) >= 2 for x in reps]
        d["multi"] = st.mean(multi) if multi else 0.0
    return d


per = defaultdict(dict)
for r in sc:
    per[r["task_id"]][r["arm"]] = chat(r)


def boot(vals, n=4000, seed=0):
    vals = [v for v in vals if v == v]
    rng = random.Random(seed)
    m = sorted(st.mean(rng.choices(vals, k=len(vals))) for _ in range(n))
    return st.mean(vals), m[int(0.025 * n)], m[int(0.975 * n)]


def fmt(t):
    return f"{t[0]:+.3f} [{t[1]:+.3f}, {t[2]:+.3f}]"


print("columns: score = native 0-1 score; n_q = actor questions; wpr = words per simulator reply; npr = numbers per reply;\n"
      "cjk = share of CJK characters; delivered, multi as in the docstring; ent_rec, FR, ic = SciConvBench native metrics\n"
      "(entity_recovery, fact recovery, intent_capture). Differences: profile minus persona off, paired by case,\n"
      "case-bootstrap 95% interval (4000 draws). pooled = mean of the four profiles minus persona off.")
csv_rows = []
for kind in ("disambiguation", "inconsistency"):
    tasks = sorted(t for t in per if f"/{kind}/" in t and all(a in per[t] for a in ARMS))
    keys = ["score", "n_q", "wpr", "npr", "cjk"] + (["delivered", "multi", "ent_rec", "FR", "ic"] if kind == "disambiguation" else [])
    if kind == "disambiguation":
        tasks = [t for t in tasks if t in cards]
    print(f"\n== {kind}: {len(tasks)} cases")
    print("arm".ljust(15) + "".join(k.rjust(11) for k in keys))
    for a in ARMS:
        print(a.ljust(15) + "".join(f"{st.mean([x for x in (per[t][a][k] for t in tasks) if x == x]):11.3f}" for k in keys))
        csv_rows += [dict(task_id=t, kind=kind, arm=a, **{k: per[t][a].get(k, "") for k in
                     ("score", "n_q", "wpr", "npr", "cjk", "delivered", "multi", "ent_rec", "FR", "ic")}) for t in tasks]
    for k in keys:
        if k == "cjk":
            continue
        line = [f"{a[-3:]} {fmt(boot([per[t][a][k] - per[t]['persona_off'][k] for t in tasks]))}" for a in ARMS[1:]]
        pooled = [st.mean([per[t][a][k] for a in ARMS[1:]]) - per[t]["persona_off"][k] for t in tasks]
        print(f"  {k:9s} vs off: " + " | ".join(line) + f" | pooled {fmt(boot(pooled))}")
    if kind == "disambiguation":
        fails = [per[t][a] for t in tasks for a in ARMS if per[t][a]["score"] == 0]
        print(f"  {len(fails)} failed chats: FR=0 in {sum(x['FR'] == 0 for x in fails)}, intent_capture=0 in "
              f"{sum(x['ic'] == 0 for x in fails)}, both {sum(x['FR'] == 0 and x['ic'] == 0 for x in fails)}")
        print("  per case: score (off 001 003 046 155) | delivered | actor questions")
        for t in tasks:
            print(f"   {t:38s} " + " ".join(str(int(per[t][a]['score'])) for a in ARMS) + "   " +
                  " ".join(f"{per[t][a]['delivered']:.2f}" for a in ARMS) + "   q " + " ".join(str(per[t][a]['n_q']) for a in ARMS))

with open(HERE / "logs_check_chats.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(csv_rows[0]))
    w.writeheader()
    for r in csv_rows:
        w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in r.items()})
