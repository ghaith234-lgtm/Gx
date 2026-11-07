# 🪜➖ reinvest phase C — partial withdrawal from one slot by its side, the grid's apply_withdrawals (REINVEST_PLAN.md ٩)
#   buy side (dollars): the pot first, then the growth inside the buy (published ⇒ amend · memory ⇒ the state) — profit → the
#   released profit (total_profit) · capital → wallet · the base never touched ·
#   sell side: coins above the base inside the sell — profit → the accumulator at their real cost (the handoff queue) · capital →
#   the wallet as coins · dollars (the pot + growth not inside the sell) — as on the buy side, no order touched ·
#   refusals · exactly once (OKX late · answer lost · never reached · the same request again · a power cut at every moment) ·
#   the order fills before the shrink ⇒ nothing changed · books = wallet every loop (okxsim: real profit = total_profit −
#   out_usd + credited · coins handed / given back · pots = credited + injected − taken out)
#   python3 devtests/step/t_wd.py [-q] [--only=name,...] [--every=K]          (STEP_ENGINE=… tests another engine copy)
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


def req(fname, items, rid="r1", ts=None, raw=None):
    def f(b):
        with open(os.path.join(b.dir, fname), "w", encoding="utf-8") as fh:
            fh.write(raw if raw is not None else json.dumps({"id": rid, "ts": b.clock.t if ts is None else ts, "items": items}))
    return ("do", f)


def inject(items, rid="i1"):
    return req("reinvest_inject.json", items, rid)


def withdraw(items, rid="w1", ts=None, raw=None):
    return req("reinvest_withdraw.json", items, rid, ts, raw)


def snap(store, name):
    def f(b):
        st = b.st
        store[name] = {"slots": json.loads(json.dumps(st["slots"])), "rb": json.loads(json.dumps(st.get("reinvest") or {})),
                       "tp": float(st.get("total_profit") or 0), "lt": dict(st.get("last_trade") or {})}
    return ("do", f)


def wd_lines(b):
    return [m for m in b.hist() if m.startswith(("➖", "⚠️ [سحب]", "🪙"))]


def pv(lv):
    return float(lv.get("usd_book") or 0) + float(lv.get("grown_qty") or 0) * float(lv.get("px") or 0)


W = 20.0
DN = [1.0, 0.99, 0.98, 0.9709, 0.97, 0.9806, 0.9903, 1.0, 1.0]  # level −1 (0.97087) buys · its 3 parts sell
GROW = walk(DN * 3, W)                                         # three rounds at 100% ⇒ level −1's parts carry growth

# ── buy side: the reinvested profit → the released profit · the base never touched
if want("buy_gain"):
    b = bot(100)
    M = {}
    b.run(GROW + [snap(M, "a"), withdraw([{"k": "-1:1", "gain": 0.05}]), ("wait", 10), snap(M, "b"),
                  withdraw([{"k": "-1:2", "gain": 1000.0, "cap": 1000.0}], rid="w2"), ("wait", 10), snap(M, "c")])
    a, bb, c = M["a"], M["b"], M["c"]
    la, lb = a["rb"]["levels"]["-1:1"], bb["rb"]["levels"]["-1:1"]
    sa, sb = a["slots"]["-1:1"], bb["slots"]["-1:1"]
    eo = b.ex.orders.get(str((sb.get("o") or {}).get("id")))
    took = pv(la) - pv(lb)
    ok("buy side, 0.05$ of profit: the pot's cents first, then the growth inside the published buy (amend · OKX's order smaller) ·"
       " total_profit + what was taken · «➖» line", sa["side"] == "buy" and 0.05 - sa["bp"] * 1e-6 - 1e-9 <= took <= 0.05 + 1e-9
       and abs((bb["tp"] - a["tp"]) - took) < 1e-9 and eo and abs(float(eo["sz"]) - (sa["q"] + sb["g"])) < 1e-9 and sb["g"] < sa["g"]
       and bb["lt"].get("withdraw") and any("➖ [سحب] الخانة -1:1 (شراء)" in m for m in wd_lines(b)),
       (took, bb["tp"] - a["tp"], la, lb, eo and eo["sz"], sa.get("g"), sb.get("g"), wd_lines(b)))
    l2a, l2c = a["rb"]["levels"]["-1:2"], c["rb"]["levels"]["-1:2"]
    s2c = c["slots"]["-1:2"]
    e2 = b.ex.orders.get(str((s2c.get("o") or {}).get("id")))
    ok("buy side, «take 1000$»: only what is really there (the pot's whole value, to the lot) · no capital invented · the buy back"
       " to its base · books = wallet every loop", pv(l2c) < s2c["bp"] * 1e-6 + 1e-9 and abs((c["tp"] - bb["tp"]) - (pv(l2a) - pv(l2c))) < 1e-9
       and e2 and abs(float(e2["sz"]) - s2c["q"] - s2c.get("g", 0)) < 1e-9 and s2c.get("g", 0) < 1e-6 + 1e-12 and not b.errors,
       (l2a, l2c, s2c.get("g"), e2 and e2["sz"], b.errors[:3]))

# ── buy side: the capital back to the wallet (not profit)
if want("buy_cap"):
    b = bot(100)
    M = {}
    b.run(walk([1.0, 1.0], W) + [inject([{"k": "-1:1", "usd": 3.0}]), ("wait", 10), snap(M, "a"),
                                 withdraw([{"k": "-1:1", "cap": 3.0}]), ("wait", 10), snap(M, "b")])
    a, bb = M["a"], M["b"]
    lb = bb["rb"]["levels"]["-1:1"]
    eo = b.ex.orders.get(str((bb["slots"]["-1:1"].get("o") or {}).get("id")))
    ok("buy side, the 3$ capital: back to the wallet — total_profit untouched · the injected total back to 0 · the buy back to its"
       " base at OKX · books = wallet", abs(bb["tp"] - a["tp"]) < 1e-12 and abs(float(bb["rb"].get("inj_total") or 0)) < 1e-9
       and pv(lb) < 1e-9 and eo and abs(float(eo["sz"]) - bb["slots"]["-1:1"]["q"]) < 1e-9 and not b.errors
       and any("رأس مال 3$ → محفظتك" in m for m in wd_lines(b)), (a["rb"], bb["rb"], eo and eo["sz"], wd_lines(b), b.errors[:2]))

# ── sell side: coins above the base — profit to the accumulator · capital coins to the wallet
if want("sell"):
    b = bot(100)
    M = {}
    b.run(walk(DN * 2 + [1.0, 0.99, 0.98, 0.9709, 0.97, 0.97], W) + [snap(M, "a"),
          withdraw([{"k": "-1:1", "gain_q": 1000.0}]), ("wait", 10), snap(M, "b")])
    a, bb = M["a"], M["b"]
    sa, sb = a["slots"]["-1:1"], bb["slots"]["-1:1"]
    eo = b.ex.orders.get(str((sb.get("o") or {}).get("id")))
    tot = sa["sq"] - sb["sq"]
    ho = bb["rb"].get("handoffs") or []
    ok("sell side, the profit as coins: the coins above the base leave the published sell (amend) → one handoff to the accumulator"
       " at their real cost · the base's coins stay (what a base buy leaves after its fee) · «🪙» line", sa["side"] == "sell" and sa.get("g", 0) > 0 and tot > 0
       and abs(sb["sq"] - b.m._lot_floor(sa["q"] * (1 - 0.0008))) < 1e-12 and eo and abs(float(eo["sz"]) - sb["sq"]) < 1e-9 and len(ho) == 1 and abs(ho[0]["coin"] - tot) < 1e-12
       and abs(ho[0]["usd"] - sa["spent"] * tot / sa["sq"]) < 1e-8 and any(m.startswith("🪙 [تسليم للمُراكِم]") for m in b.hist()),
       (sa, sb, eo and eo["sz"], ho, wd_lines(b)))
    ok("… total_profit untouched (coins, not dollars) · the sale of what is left still at its true cost · books = wallet",
       abs(bb["tp"] - a["tp"]) < 1e-12 and sb["sq"] > 0 and sa["sq"] > 0 and abs(sb["spent"] / sb["sq"] - sa["spent"] / sa["sq"]) < 1e-9
       and not b.errors, (a["tp"], bb["tp"], b.errors[:3]))
    b = bot(100)
    M = {}
    b.run(walk([1.0, 1.0], W) + [inject([{"k": "0:1", "coin": 2.0}]), ("wait", 10), snap(M, "a"),
                                 withdraw([{"k": "0:1", "cap_q": 2.0}]), ("wait", 10), snap(M, "b")])
    a, bb = M["a"], M["b"]
    eo = b.ex.orders.get(str((bb["slots"]["0:1"].get("o") or {}).get("id")))
    ok("sell side, the 2 capital coins: out of the published sell back to the wallet (not the accumulator, not profit) · books = wallet",
       abs(a["slots"]["0:1"]["sq"] - bb["slots"]["0:1"]["sq"] - 2) < 1e-12 and eo and abs(float(eo["sz"]) - bb["slots"]["0:1"]["sq"]) < 1e-9
       and not bb["rb"].get("handoffs") and abs(float(bb["rb"].get("cap_coin_out") or 0) - 2) < 1e-12 and abs(bb["tp"] - a["tp"]) < 1e-12
       and abs(float(bb["rb"].get("inj_total") or 0)) < 1e-9 and not b.errors, (a["slots"]["0:1"], bb["slots"]["0:1"], bb["rb"], b.errors[:2]))

# ── sell side dollars (the pot + growth not inside the sell) · a buy in memory
if want("dollars"):
    b = bot(100, {"step_window": 2})
    M = {}
    b.run(walk([1.0, 1.0], W) + [inject([{"k": "0:2", "usd": 1.5}, {"k": "-5:1", "usd": 2.0}]), ("wait", 10), snap(M, "a"),
                                 withdraw([{"k": "0:2", "cap_d": 1.0}, {"k": "-5:1", "cap": 2.0}]), ("wait", 10), snap(M, "b")])
    a, bb = M["a"], M["b"]
    ok("sell side, 1$ of capital from the pot / growth not in the sell: no order touched · its sell unchanged · a buy in memory:"
       " smaller in the state · capital to the wallet, not profit · books = wallet",
       a["slots"]["0:2"]["sq"] == bb["slots"]["0:2"]["sq"] and abs(pv(a["rb"]["levels"]["0:2"]) - pv(bb["rb"]["levels"]["0:2"]) - 1.0) < 1e-6 + 1e-9
       and not a["slots"]["-5:1"].get("o") and bb["slots"]["-5:1"].get("g", 0) < a["slots"]["-5:1"].get("g", 0) and abs(bb["tp"] - a["tp"]) < 1e-12
       and not b.ex.amends and not b.errors, (a["rb"]["levels"], bb["rb"]["levels"], b.ex.amends, wd_lines(b), b.errors[:2]))

# ── the slot changed side after the request was written (it sold / it bought meanwhile) ⇒ taken on its side now · nothing ⇒ said
if want("flip"):
    b = bot(100)
    M = {}
    b.run(GROW + [snap(M, "a"), withdraw([{"k": "-1:1", "px": 0.970873786408, "cap_q": 0, "gain_q": 0.03}, {"k": "-1:3", "cap": 1.0}]),
                  ("wait", 10), snap(M, "b")])
    a, bb = M["a"], M["b"]
    took = pv(a["rb"]["levels"]["-1:1"]) - pv(bb["rb"]["levels"]["-1:1"])
    lg = wd_lines(b)
    ok("a coins request for a slot that is a buy now ⇒ its dollars at the slot's price (0.03 coin ≈ 0.0291$) · a request for capital"
       " that isn't there ⇒ «لا يوجد ما يُسحب» · books = wallet", a["slots"]["-1:1"]["side"] == "buy" and abs(took - 0.03 * 0.970873786408) < 1e-6 + 1e-9
       and abs((bb["tp"] - a["tp"]) - took) < 1e-9 and any("الخانة -1:3: لا يوجد ما يُسحب" in m for m in lg) and not b.errors, (took, lg, b.errors[:2]))


# ── a shrink bigger than what is left of a partly filled order ⇒ OKX completes it: only the unfilled part comes off (booked so)
if want("partial"):
    b = bot(100, partial=0.9)
    M = {}
    b.run(walk([1.0, 1.0], W) + [inject([{"k": "-1:1", "usd": 3.0}]), ("wait", 10), ("px", 0.9708, 20), snap(M, "a"),
                                 withdraw([{"k": "-1:1", "cap": 3.0}]), ("wait", 10), snap(M, "b")])
    a, bb = M["a"], M["b"]
    eo = b.ex.orders.get(str((a["slots"]["-1:1"].get("o") or {}).get("id")))
    left = float(eo["sz"]) if eo else 0
    back = float(a["rb"].get("inj_total") or 0) - float(bb["rb"].get("inj_total") or 0)
    acc0 = float(next((x for x in b.ex.fills if x[0] == (eo or {}).get("ordId")), (0, 0, 0, 0, 0))[4]) if eo else 0
    ok("the buy was 90% filled, then «take the 3$ capital»: OKX completed the order ⇒ only its unfilled part came back (≈0.8$, not"
       " 3$) · the rest of the capital stays in the slot's coins · books = wallet", eo and eo["state"] == "filled"
       and 0.5 < back < 1.0 and abs(back - (float(a["slots"]["-1:1"]["o"]["sz"]) - acc0) * a["slots"]["-1:1"]["bp"]) < 1e-5
       and bb["slots"]["-1:1"]["side"] == "sell" and not b.errors, (back, eo and (eo["state"], str(eo["sz"]), str(eo["acc"])), acc0, b.errors[:3]))


# ── exactly once
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
        b.run(GROW + [snap(M, "a"), withdraw([{"k": "-1:1", "gain": 0.05}]), ("wait", 90), snap(M, "b"),
                      withdraw([{"k": "-1:1", "gain": 0.05}]), ("wait", 30), snap(M, "c")])
        a, bb, c = M["a"], M["b"], M["c"]
        took = pv(a["rb"]["levels"]["-1:1"]) - pv(bb["rb"]["levels"]["-1:1"])
        eo = b.ex.orders.get(str((bb["slots"]["-1:1"].get("o") or {}).get("id")))
        good = (0.05 - 1e-6 - 1e-9 <= took <= 0.05 + 1e-9 and abs((bb["tp"] - a["tp"]) - took) < 1e-9 and eo
                and abs(float(eo["sz"]) - bb["slots"]["-1:1"]["q"] - bb["slots"]["-1:1"]["g"]) < 1e-9 and c["tp"] == bb["tp"]
                and not any(x.get("am") for x in bb["slots"].values()) and not b.errors)
        if not good:
            bad.append((mode, took, bb["tp"] - a["tp"], eo and eo["sz"], b.ex.amends, wd_lines(b)[:5], b.errors[:2]))
    ok("exactly once: OKX applies 7 s late · the answer lost · never reached OKX · reaches OKX 4 s late ⇒ shrunk once · booked once"
       " · the same request again ⇒ ignored", not bad, bad[:2])

# ── refusals
if want("refuse"):
    b = bot(100)
    M = {}
    b.run(GROW + [snap(M, "a"), withdraw([{"k": "-1:1", "gain": 0.05}], rid="old", ts=1.0), ("wait", 10), withdraw(None, raw="[1,"),
                  ("wait", 10), withdraw([{"k": "9:9", "gain": 1}, {"k": "-1:2", "gain": float("nan")}, {"k": "-1:3", "gain": -5}], rid="x"),
                  ("wait", 10), snap(M, "b")])
    lg = wd_lines(b)
    ok("refused, nothing changed: older than a day · a broken file · a slot with nothing reinvested · NaN · negative",
       M["a"]["tp"] == M["b"]["tp"] and M["a"]["rb"]["levels"] == M["b"]["rb"]["levels"] and any("الطلب قديم" in m for m in lg)
       and any("طلب تالف" in m for m in lg) and any("الخانة 9:9: لا يوجد فيها شيء" in m for m in lg) and not b.ex.amends and not b.errors,
       (lg, b.errors[:2]))

# ── the order fills before the shrink lands
if want("race"):
    b = bot(100)
    M = {}
    b.run(GROW + [snap(M, "a"), ("do", lambda bb: setattr(bb.ex, "amend_lag", 40.0)), withdraw([{"k": "-1:1", "gain": 0.05}]),
                  ("wait", 6), ("px", 0.97, 60), snap(M, "b")])
    a, bb = M["a"], M["b"]
    ub0 = float(a["rb"]["levels"]["-1:1"]["usd_book"])
    ok("OKX accepted the smaller buy, the buy filled first ⇒ only the pot's cents taken (at once, as the grid) · the growth inside the"
       " order stays (no amount invented) · said · books = wallet", b.ex.amends and abs((bb["tp"] - a["tp"]) - ub0) < 1e-12
       and abs(float(bb["slots"]["-1:1"].get("g") or 0) - float(a["slots"]["-1:1"].get("g") or 0)) < 1e-12
       and any("لم يصغر أمر الشراء" in m for m in wd_lines(b)) and not b.errors, (b.ex.amends, ub0, a["tp"], bb["tp"], wd_lines(b), b.errors[:2]))

# ── a power cut at every moment of a withdrawal story
CUT_ITEMS = [{"k": "-1:1", "gain": 0.03}, {"k": "-1:2", "gain": 1000, "cap": 1000}, {"k": "0:1", "cap_q": 2.0}, {"k": "0:2", "gain_d": 0.5, "cap_d": 1.0}]


def cut_story(cuts=()):
    b = bot(60, {"step_window": 4}, partial=0.5)
    steps = (walk(DN * 2, 150.0) + [inject([{"k": "0:1", "coin": 2.0}, {"k": "0:2", "usd": 1.5}]), ("wait", 150), withdraw(CUT_ITEMS), ("wait", 150)]
             + walk([1.0101, 1.0205, 1.0, 0.97, 0.9705, 0.9806, 1.0], 150.0))
    b.run(steps, cuts=cuts)
    st = b.st or {}
    rb = st.get("reinvest") or {}
    out = {"fills": sorted((x[2], str(x[3]), str(x[4])) for x in b.ex.fills), "profit": round(float(st.get("total_profit") or 0), 9),
           "slots": sorted((k, x["side"], x["cyc"], x.get("n", 0), round(float(x.get("g") or 0), 9), round(float(x.get("sq") or 0), 9))
                           for k, x in (st.get("slots") or {}).items()),
           "rb": tuple(round(float(rb.get(f) or 0), 9) for f in ("credited", "inj_total", "out_usd", "out_gain", "out_coin", "cap_coin_out")),
           "log": sorted(m for m in b.hist() if m.startswith(("🟢", "🔴", "💠", "💉", "➖", "🪙", "⚠️ [حقن]", "⚠️ [سحب]"))),
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
    wd_ok = ref["rb"][2] > 0 and ref["rb"][5] > 0 and not ref["errors"] and any(m.startswith("➖") for m in ref["log"])
    ok(f"a power cut at every moment of a withdrawal story ({len(ks)} of {ref['moments']} moments · both sides, coins and dollars,"
       f" capital and profit): the same as with no cut · books = wallet", wd_ok and not bad, (wd_ok, ref["rb"], ref["errors"][:2], sorted(bad, key=str)[:3]))

print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
