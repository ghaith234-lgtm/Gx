# 🪜💉 reinvest phase B — injection into one slot (level · part) by its side, the grid's apply_injections (REINVEST_PLAN.md ٨ · أ)
#   sell side: wallet coins join the sell now (published ⇒ amend-order at OKX · memory ⇒ the state, if the free coins cover it) ·
#   buy side: dollars grow the buy now (published ⇒ amend · memory ⇒ the state) · under a lot / can't now ⇒ the slot's pot ·
#   the capital kept apart (inj_*) · refusals (side · free balance · OKX · unknown slot · old · off · heavy finger · bad file) ·
#   exactly once: OKX applies late · its answer lost · the request never reached OKX · the same request again · a power cut at
#   every moment · the order fills before the resize ⇒ nothing changed · books = wallet every loop (okxsim: the injected coins
#   «as if bought» · pots = credited + injected)
#   python3 devtests/step/t_inj.py [-q] [--only=name,...] [--every=K]   (cut: K = every K-th moment)          (STEP_ENGINE=… tests another engine copy)
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk, D

Q = "-q" in sys.argv
ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:800]}"), flush=True)


def want(n):
    return ONLY is None or n in ONLY


def bot(pct=100, cfg=None, **kw):
    c = Clock()
    ex = Ex(c, **dict(dict(base=100, quote=1000), **kw))
    cf = {"step_window": 8, "step_first": 0.01}
    if pct is not None:
        cf.update(reinvest=True, reinvest_pct=pct)
    cf.update(cfg or {})
    return Bot(ex, cf)


def inject(items, rid="r1", ts=None, raw=None):
    def f(b):
        with open(os.path.join(b.dir, "reinvest_inject.json"), "w", encoding="utf-8") as fh:
            fh.write(raw if raw is not None else json.dumps({"id": rid, "ts": b.clock.t if ts is None else ts, "items": items}))
    return ("do", f)


def snap(store, name):
    def f(b):
        st = b.st
        store[name] = {"slots": json.loads(json.dumps(st["slots"])), "rb": json.loads(json.dumps(st.get("reinvest") or {})),
                       "tp": float(st.get("total_profit") or 0), "orders": {o["ordId"]: (o["side"], str(o["sz"]), str(o["px"]), o["cl"])
                                                                            for o in b.mine_open()}}
    return ("do", f)


def order_of(b, key):
    o = (b.st["slots"][key].get("o") or {})
    eo = b._ex_of(o) if o else None
    return eo


def inj_lines(b):
    return [m for m in b.hist() if m.startswith(("💉", "⚠️ [حقن]"))]


W = 20.0
UP = [1.0, 1.0, 1.005, 1.01, 1.01, 1.0, 1.0]                  # the wallet slot 0:1 (sp 1.01) sells · buys back at 1.0
DN = [1.0, 0.99, 0.98, 0.9709, 0.97, 0.9806, 0.9903, 1.0, 1.0]  # level −1 (0.97087) buys · its 3 parts sell

# ── coins into a published sell (amend-order) · the sale sells them · the capital stays in the slot
if want("coin_live"):
    b = bot(100)
    M = {}
    b.run(walk([1.0, 1.0], W) + [snap(M, "a"), inject([{"k": "0:1", "coin": 2.0}]), ("wait", 10), snap(M, "b")] + walk(UP, W) + [snap(M, "c")])
    a, bb, c = M["a"], M["b"], M["c"]
    s_a, s_b = a["slots"]["0:1"], bb["slots"]["0:1"]
    oid = (s_b.get("o") or {}).get("id")
    eo = b.ex.orders.get(str(oid)) if oid else None
    ok("coins → a published sell: OKX's order grew by 2 (amend-order, the same order) · the slot sells 2 more · growth 2 · capital"
       " 2 × its price · «💉» line", eo and str(eo["sz"]) == str(D(str(s_a["sq"])) + 2) and (s_a.get("o") or {}).get("id") == oid
       and abs(s_b["sq"] - s_a["sq"] - 2) < 1e-12 and abs(s_b.get("g", 0) - 2) < 1e-12 and abs(bb["rb"].get("inj_coin", 0) - 2) < 1e-12
       and abs(bb["rb"]["inj_total"] - 2 * s_a["bp"]) < 1e-9 and any("💉 [حقن] الخانة 0:1 (بيع): أُضيفت 2 عملة" in m for m in inj_lines(b)),
       (s_a.get("sq"), s_b.get("sq"), s_b.get("g"), eo and eo["sz"], bb["rb"], inj_lines(b)))
    s_c = c["slots"]["0:1"]
    cl0 = (s_b.get("o") or {}).get("cl")
    ok("… it sold everything (the 2 injected too) in that one order · books = wallet every loop", s_c.get("n") == 1 and not b.errors
       and any(f[1] == cl0 and f[2] == "sell" and D(str(f[4])) == D(str(round(s_b["sq"], 6))) for f in b.ex.fills),
       (s_c, b.errors[:3], [f for f in b.ex.fills if f[2] == "sell"][:3]))
    bq = [f for f in b.ex.fills if f[2] == "buy" and f[3] == D("1")]
    ok("… its next buy at OKX = base + growth (the 2 injected + its profit turned to coins)", s_c.get("g", 0) > 2 and bq
       and abs(float(bq[0][4]) - b.m.fmt_qty(s_c["q"] + s_c["g"])) < 1e-12 and abs(float(s_c.get("bq") or 0) - (s_c["q"] + s_c["g"])) < 1e-9,
       (bq[:2], s_c))

# ── coins into a sell in memory · too many coins · into a buy
if want("coin_mem"):
    b = bot(100, {"step_window": 2})
    M = {}
    b.run(walk([1.0, 1.0], W) + [snap(M, "a"), inject([{"k": "1:1", "coin": 3.0}, {"k": "1:2", "coin": 500.0}, {"k": "-1:1", "coin": 1.0},
                                                      {"k": "1:3", "coin": 0.0000001}]), ("wait", 10), snap(M, "b")])
    a, bb = M["a"], M["b"]
    lg = inj_lines(b)
    ok("coins → a sell in memory: in the state at once (the free coins cover it) · no order touched · growth 3",
       not (a["slots"]["1:1"].get("o")) and abs(bb["slots"]["1:1"]["sq"] - a["slots"]["1:1"]["sq"] - 3) < 1e-12 and not b.ex.amends
       and any("الخانة 1:1 (بيع): أُضيفت 3 عملة من محفظتك إلى أمر البيع في الذاكرة" in m for m in lg), (bb["slots"]["1:1"], lg))
    ok("refused, nothing changed: 500 coins (more than the free coins) · coins into a buy · under one lot",
       bb["slots"]["1:2"]["sq"] == a["slots"]["1:2"]["sq"] and bb["slots"]["-1:1"] == a["slots"]["-1:1"]
       and any("الخانة 1:2: رصيد العملة الحر لا يكفي" in m for m in lg) and any("الخانة -1:1 ليس لها أمر بيع" in m for m in lg)
       and any("الخانة 1:3: الكمية" in m for m in lg) and not b.errors, (lg, b.errors[:2]))
    b.steps = []
    b.run(walk([1.0, 1.03, 1.035, 1.04, 1.045, 1.05, 1.06, 1.07, 1.0], W))
    ok("… when it is published its order carries the injected coins · sold · books = wallet",
       b.st["slots"]["1:1"].get("n", 0) >= 1 and any(f[2] == "sell" and D(str(f[4])) == D(str(bb["slots"]["1:1"]["sq"])) for f in b.ex.fills)
       and not b.errors, (b.st["slots"]["1:1"], b.errors[:3]))

# ── dollars into a published buy · a buy in memory · a sell (⇒ pot) · OKX refuses (no free dollars ⇒ pot)
if want("usd"):
    b = bot(100)
    M = {}
    b.run(walk([1.0, 1.0], W) + [snap(M, "a"), inject([{"k": "-1:1", "usd": 3.0}, {"k": "-6:2", "usd": 2.0}, {"k": "0:2", "usd": 1.5}]),
                                 ("wait", 10), snap(M, "b")] + walk(DN, W) + walk(UP + [1.02, 1.02, 1.0, 1.0], W) + [snap(M, "c")])
    a, bb, c = M["a"], M["b"], M["c"]
    s1a, s1b = a["slots"]["-1:1"], bb["slots"]["-1:1"]
    add = b.m._lot_floor(3.0 / s1a["bp"])
    eo = b.ex.orders.get(str((s1b.get("o") or {}).get("id")))
    lv = bb["rb"]["levels"]
    ok("dollars → a published buy: OKX's order grew by ⌊3$ ÷ price⌋ (amend) · the change under one lot → its pot · capital 3$",
       eo and abs(float(eo["sz"]) - (s1a["q"] + add)) < 1e-9 and abs(s1b.get("g", 0) - add) < 1e-12
       and abs(lv["-1:1"]["usd_book"] - (3.0 - add * s1a["bp"])) < 1e-9 and abs(lv["-1:1"]["inj_book"] - lv["-1:1"]["usd_book"]) < 1e-12,
       (eo and eo["sz"], s1a["q"], add, s1b.get("g"), lv.get("-1:1")))
    s6a, s6b = a["slots"]["-6:2"], bb["slots"]["-6:2"]
    pv = lambda x: float(x.get("usd_book") or 0) + float(x.get("grown_qty") or 0) * float(x.get("px") or 0)
    ok("dollars → a buy in memory: grows in the state · → a sell: all to its pot («يكبر أمرها في دورته» — the sweep turns it into"
       " its next buy's growth) · total capital 6.5$",
       not s6a.get("o") and abs(s6b.get("g", 0) - b.m._lot_floor(2.0 / s6a["bp"])) < 1e-12 and abs(pv(lv["0:2"]) - 1.5) < 1e-9
       and abs(float(lv["0:2"]["inj_book"]) + float(lv["0:2"]["inj_grown"]) - 1.5) < 1e-9
       and abs(bb["rb"]["inj_total"] - 6.5) < 1e-9 and any("الخانة 0:2: 1.5$ رأس مال إلى حصّالتها" in m for m in inj_lines(b)), (s6b, lv.get("0:2"), bb["rb"]))
    s1c, s2c = c["slots"]["-1:1"], c["slots"]["0:2"]
    ok("… the grown buy bought base + growth and its sale sold all · the sell's pot turned into quantity at its sale (next buy"
       " bigger) · books = wallet every loop", s1c.get("n", 0) >= 1 and s2c.get("n", 0) >= 1 and s2c.get("g", 0) >= b.m._lot_floor(1.5 / s2c["bp"])
       and any(f[2] == "buy" and D(str(f[4])) == D(str(round(s1a["q"] + add, 6))) for f in b.ex.fills) and not b.errors,
       (s1c, s2c, b.errors[:3]))
    b = bot(100, quote=60)                                 # the buys take almost all the dollars ⇒ OKX refuses the bigger size
    M = {}
    b.run(walk([1.0, 1.0], W) + [snap(M, "a"), inject([{"k": "-1:1", "usd": 40.0}]), ("wait", 10), snap(M, "b")])
    lv = M["b"]["rb"]["levels"]["-1:1"]
    ok("dollars → a published buy OKX refuses (no free dollars, 51008) ⇒ the order unchanged · the 40$ in its pot with the reason",
       M["b"]["slots"]["-1:1"].get("g", 0) == 0 and abs(lv["usd_book"] - 40) < 1e-9 and not b.ex.amends
       and any("40$ رأس مال إلى حصّالتها" in m and "تعذّر تكبير الأمر الآن" in m for m in inj_lines(b)) and not b.errors, (lv, inj_lines(b), b.errors[:2]))

# ── exactly once: OKX applies late · the answer lost · never reached OKX · the same request again
if want("once"):
    bad = []
    for mode in ("lag", "lost", "drop", "late"):
        b = bot(100)
        ex = b.ex
        st_ = {"n": 0}
        if mode == "lag":
            ex.amend_lag = 7.0
        else:
            def fault(op, p, mode=mode):
                if op == "amend" and st_["n"] == 0:
                    st_["n"] += 1
                    return {"lost": "lost", "drop": "drop", "late": ("late", 4.0)}[mode]
                return None
            ex.fault = fault
        M = {}
        b.run(walk([1.0, 1.0], W) + [snap(M, "a"), inject([{"k": "0:1", "coin": 2.0}, {"k": "-1:1", "usd": 3.0}]), ("wait", 90), snap(M, "b"),
                                     inject([{"k": "0:1", "coin": 2.0}, {"k": "-1:1", "usd": 3.0}]), ("wait", 30), snap(M, "c")])
        a, bb, c = M["a"], M["b"], M["c"]
        e0 = b.ex.orders.get(str((bb["slots"]["0:1"].get("o") or {}).get("id")))
        e1 = b.ex.orders.get(str((bb["slots"]["-1:1"].get("o") or {}).get("id")))
        add = b.m._lot_floor(3.0 / a["slots"]["-1:1"]["bp"])
        good = (e0 and abs(float(e0["sz"]) - a["slots"]["0:1"]["sq"] - 2) < 1e-9 and e1 and abs(float(e1["sz"]) - a["slots"]["-1:1"]["q"] - add) < 1e-9
                and abs(bb["slots"]["0:1"]["sq"] - a["slots"]["0:1"]["sq"] - 2) < 1e-12 and abs(bb["slots"]["-1:1"].get("g", 0) - add) < 1e-12
                and c["slots"]["0:1"]["sq"] == bb["slots"]["0:1"]["sq"] and c["rb"].get("inj_total") == bb["rb"].get("inj_total")
                and not any(x.get("am") for x in bb["slots"].values()) and not b.errors
                and not os.path.exists(os.path.join(b.dir, "reinvest_inject.json")))
        if not good:
            bad.append((mode, e0 and e0["sz"], e1 and e1["sz"], bb["slots"]["0:1"].get("sq"), bb["slots"]["-1:1"].get("g"), b.ex.amends,
                        inj_lines(b)[:6], b.errors[:2]))
    ok("exactly once: OKX applies 7 s late · the answer lost · the request never reached OKX · it reaches OKX 4 s late ⇒ each order"
       " grew once · the books once · the same request again ⇒ ignored", not bad, bad[:2])

# ── refusals: an old request · reinvest off · a broken file · an unknown slot · a heavy finger
if want("refuse"):
    b = bot(100)
    M = {}
    b.run(walk([1.0, 1.0], W) + [snap(M, "a"), inject([{"k": "0:1", "coin": 2}], rid="old", ts=1.0), ("wait", 10),
                                 inject(None, raw="{broken"), ("wait", 10),
                                 inject([{"k": "9:9", "usd": 1}, {"k": "-1:1", "usd": 1e9}, {"k": "-1:2", "usd": float("nan")}], rid="x"),
                                 ("wait", 10), snap(M, "b")])
    lg = inj_lines(b)
    same = all(M["a"]["slots"][k]["sq"] == M["b"]["slots"][k]["sq"] and M["a"]["slots"][k].get("g", 0) == M["b"]["slots"][k].get("g", 0)
               for k in M["a"]["slots"])
    ok("refused, nothing changed: older than a day · a broken file · an unknown slot · a heavy finger · NaN — each said once",
       same and not M["b"]["rb"].get("inj_total") and any("الطلب قديم" in m for m in lg) and any("طلب تالف" in m for m in lg)
       and any("الخانة 9:9 غير موجودة" in m for m in lg) and any("مبلغ غير معقول في الخانة -1:1" in m for m in lg) and not b.ex.amends
       and not b.errors, (lg, M["b"]["rb"]))
    b = bot(None)
    b.run(walk([1.0, 1.0], W) + [inject([{"k": "0:1", "coin": 2}]), ("wait", 10)])
    ok("a bot without reinvest: the request refused («غير مفعّلة») · no book made · nothing changed",
       "reinvest" not in b.st and any("إعادة الاستثمار غير مفعّلة" in m for m in b.hist()) and not b.ex.amends and not b.errors, b.hist()[:3])

# ── the order fills before the resize lands ⇒ nothing changed (coins stay in the wallet · dollars to the pot)
if want("race"):
    b = bot(100)
    b.ex.amend_lag = 40.0
    M = {}
    b.run(walk([1.0, 1.0], W) + [snap(M, "a"), inject([{"k": "0:1", "coin": 2.0}]), ("wait", 6), ("px", 1.01, 60), snap(M, "b")]
          + walk([1.0, 1.0], W) + [snap(M, "c"), inject([{"k": "-1:1", "usd": 3.0}], rid="r2"), ("wait", 6), ("px", 0.97, 60), snap(M, "d")])
    s = M["b"]["slots"]["0:1"]
    sold = [f for f in b.ex.fills if f[2] == "sell"]
    lv = (M["d"]["rb"]["levels"].get("-1:1") or {})
    acc_ = [a_ for a_ in b.ex.amends]
    ok("OKX accepted the bigger sell, the sell filled before it applied it ⇒ the 2 coins never left the wallet (no growth, no"
       " capital) · said", len(acc_) >= 1 and s["side"] == "buy" and s.get("g", 0) < 2 and not M["b"]["rb"].get("inj_coin") and sold
       and D(str(sold[0][4])) == D(str(round(M["a"]["slots"]["0:1"]["sq"], 6))) and any("لم تُضف 2 عملة" in m for m in inj_lines(b)),
       (acc_, s, M["b"]["rb"], sold[:2], inj_lines(b)))
    pv = float(lv.get("usd_book") or 0) + float(lv.get("grown_qty") or 0) * float(lv.get("px") or 0)
    ok("… the same with a buy ⇒ the 3$ in its pot (the reason said) · OKX's late resize found the orders done · books = wallet",
       len(acc_) >= 2 and abs(pv - 3.0) < 1e-9 and any("3$ رأس مال إلى حصّالتها" in m and "الأمر اكتمل قبل التعديل" in m for m in inj_lines(b))
       and not b.errors, (lv, acc_, inj_lines(b), b.errors[:3]))

# ── a flaky API: OKX applied the bigger sell, the order filled, and the loop's own check missed it ⇒ the fill itself settles it
if want("flaky"):
    b = bot(100)
    b.ex.amend_lag = 5.0
    fx = {"oid": None, "after": 1, "hit": 0}

    def fault(op, p):
        if op != "order" or not fx["oid"] or str(p.get("ordId")) != fx["oid"]:
            return None
        o = b.ex.orders.get(fx["oid"])
        if o["state"] != "filled":
            fx["hit"] += 1
            return ("code", "50001")                       # OKX busy for this order: the loop can't settle the resize
        if fx["after"] > 0:
            fx["after"] -= 1
            return ("code", "50001")                       # … once more, after the fill (the loop's own check)
        return None
    b.ex.fault = fault

    def arm(bb):
        fx["oid"] = str(bb.st["slots"]["0:1"]["o"]["id"])
    M = {}
    b.run(walk([1.0, 1.0], W) + [snap(M, "a"), ("do", arm), inject([{"k": "0:1", "coin": 2.0}]), ("wait", 8), ("px", 1.01, 30), snap(M, "b")]
          + walk([1.0, 1.0], W))
    s = M["b"]["slots"]["0:1"]
    sold = [f for f in b.ex.fills if f[2] == "sell"]
    ok("flaky API: the bigger sell filled before the loop could check it ⇒ the fill settles the resize first (the 2 coins at their"
       " basis) · one sale of everything · books = wallet", fx["hit"] > 0 and fx["after"] == 0 and sold and D(str(sold[0][4])) == D(str(round(M["a"]["slots"]["0:1"]["sq"] + 2, 6)))
       and abs(float(M["b"]["rb"].get("inj_coin") or 0) - 2) < 1e-12 and s.get("n") == 1 and not s.get("am") and not b.errors,
       (fx, sold[:2], s, M["b"]["rb"].get("inj_coin"), b.errors[:3]))


# ── a power cut at every moment of an injection story (coins into a published sell and a memory sell · dollars into a published
#    buy, a memory buy and a sell · then both sides trade) ⇒ the same orders, sizes, books and log lines as the run with no cut
CUT_ITEMS = [{"k": "0:1", "coin": 2.0}, {"k": "1:3", "coin": 1.5}, {"k": "-1:1", "usd": 3.0}, {"k": "-4:2", "usd": 2.0}, {"k": "0:2", "usd": 1.0}]


def cut_story(cuts=()):
    b = bot(60, {"step_window": 4}, partial=0.5)
    steps = walk([1.0], 150.0) + [inject(CUT_ITEMS), ("wait", 150)] + walk([1.0101, 1.0205, 1.0, 0.97, 0.9705, 0.9806, 0.9903, 1.0, 1.0], 150.0)
    b.run(steps, cuts=cuts)
    st = b.st or {}
    rb = st.get("reinvest") or {}
    out = {"fills": sorted((x[2], str(x[3]), str(x[4])) for x in b.ex.fills),
           "profit": round(float(st.get("total_profit") or 0), 9),
           "slots": sorted((k, x["side"], x["cyc"], x.get("n", 0), round(float(x.get("g") or 0), 9), round(float(x.get("sq") or 0), 9))
                           for k, x in (st.get("slots") or {}).items()),
           "rb": (round(float(rb.get("credited") or 0), 9), round(float(rb.get("inj_total") or 0), 9),
                  sorted((k, round(float(v["usd_book"]), 9), round(float(v["grown_qty"]), 9)) for k, v in (rb.get("levels") or {}).items())),
           "log": sorted(m for m in b.hist() if m.startswith(("🟢", "🔴", "💠", "💉", "⚠️ [حقن]"))),
           "errors": b.errors, "cuts": b.cuts, "moments": b.moments}
    import shutil
    shutil.rmtree(b.dir, ignore_errors=True)
    return out


def _cut_one(k):
    try:
        return k, cut_story((k,)), None
    except BaseException as e:
        return k, None, f"{type(e).__name__}: {e}"


if want("cut"):
    from multiprocessing import Pool
    ref = cut_story()
    every = int(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--every=")), "1"))
    ks = list(range(1, ref["moments"] + 1, every))
    bad = []
    with Pool(4) as pool:
        for k, r, e in pool.imap_unordered(_cut_one, ks, chunksize=4):
            if e or r is None:
                bad.append((k, "crash", e))
            elif r["cuts"] != 1:
                bad.append((k, "no cut"))
            elif r["errors"]:
                bad.append((k, "books", r["errors"][:2]))
            else:
                for key in ("fills", "profit", "slots", "rb", "log"):
                    if r[key] != ref[key]:
                        bad.append((k, key, [x for x in r[key] if x not in ref[key]][:2] if isinstance(r[key], list) else r[key]))
                        break
    inj_ok = ref["rb"][1] > 0 and not ref["errors"] and any(m.startswith("💉") for m in ref["log"])
    ok(f"a power cut at every moment of an injection story ({len(ks)} of {ref['moments']} moments · coins and dollars, published and"
       f" memory, both sides trade): the same as with no cut · books = wallet", inj_ok and not bad, (inj_ok, ref["errors"][:2], sorted(bad, key=str)[:3]))

print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
