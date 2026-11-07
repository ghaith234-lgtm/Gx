# 🪜🔓 reinvest phase D — the release and the unwind, the grid's release / _unwind_step (REINVEST_PLAN.md ١٠ · ١١ · ج)
#   the release (the flag · or the setting off): every pot released now — dollars ⇒ total_profit · coins ⇒ one handoff to the
#   accumulator at their real cost · capital ⇒ the wallet · the grown published orders shrink to their base at OKX (amend) ·
#   memory at once · OKX refuses ⇒ unwind (retried every minute · the grown buy filled ⇒ a grown sell · the grown sell filled ⇒
#   its growth released at that sale · moved to memory ⇒ released there) · after it: ordinary profit, base buys · on again ⇒
#   reinvesting again · exactly once (the flag again · a power cut at every moment) · books = wallet every loop
#   python3 devtests/step/t_rel.py [-q] [--only=name,...] [--every=K]          (STEP_ENGINE=… tests another engine copy)
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, walk, D

Q = "-q" in sys.argv
ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


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


def req(fname, items, rid):
    def f(b):
        with open(os.path.join(b.dir, fname), "w", encoding="utf-8") as fh:
            json.dump({"id": rid, "ts": b.clock.t, "items": items}, fh)
    return ("do", f)


def flag(off=True):
    """the dashboard's switch off: the setting off + the flag (the grid's way) · off=False: the flag alone"""
    def f(b):
        if off:
            p = os.path.join(b.dir, f"config_{b.ex.sym}.json")
            c = json.load(open(p)); c["reinvest"] = False; json.dump(c, open(p, "w"))
        open(os.path.join(b.dir, "reinvest_release.flag"), "w").close()
    return ("do", f)


def cfg(**kv):
    def f(b):
        p = os.path.join(b.dir, f"config_{b.ex.sym}.json")
        c = json.load(open(p)); c.update(kv); json.dump(c, open(p, "w"))
    return ("do", f)


def snap(store, name):
    def f(b):
        st = b.st
        store[name] = {"slots": json.loads(json.dumps(st["slots"])), "rb": json.loads(json.dumps(st.get("reinvest") or {})),
                       "tp": float(st.get("total_profit") or 0), "lt": dict(st.get("last_trade") or {}),
                       "orders": {o["ordId"]: str(o["sz"]) for o in b.mine_open()}}
    return ("do", f)


def pv(lv):
    return float(lv.get("usd_book") or 0) + float(lv.get("grown_qty") or 0) * float(lv.get("px") or 0)


def pots(rb):
    return sum(pv(lv) for lv in (rb.get("levels") or {}).values())


def rel_lines(b):
    return [m for m in b.hist() if m.startswith(("🔄", "🔓", "🪙", "⏳", "🔁"))]


def eo_of(b, snapshot, key):
    oid = str((snapshot["slots"][key].get("o") or {}).get("id"))
    return b.ex.orders.get(oid)


W = 20.0
DN = [1.0, 0.99, 0.98, 0.9709, 0.97, 0.9806, 0.9903, 1.0, 1.0]
BUILD = (walk(DN * 3, W) + [req("reinvest_inject.json", [{"k": "0:1", "coin": 2.0}, {"k": "-6:1", "usd": 2.0}], "i1"), ("wait", 10)]
         + walk([0.99, 0.98, 0.9709, 0.97, 0.97], W))   # level −1's grown buys fill ⇒ grown sells · 0:1 a sell with 2 injected coins
BASE_F = 1 - 0.0008

# ── the release: everything now
if want("release"):
    b = bot(100)
    M = {}
    b.run(BUILD + [snap(M, "a"), flag(), ("wait", 10), snap(M, "b")])
    a, bb = M["a"], M["b"]
    sl = [k for k in ("-1:1", "-1:2", "-1:3") if a["slots"][k]["side"] == "sell" and a["slots"][k].get("g", 0) > 0]
    shr = all(abs(float(eo_of(b, bb, k)["sz"]) - b.m._lot_floor(a["slots"][k]["q"] * BASE_F)) < 1e-9 for k in sl)
    e01 = eo_of(b, bb, "0:1")
    ho = (bb["rb"].get("handoffs") or [])
    coin_in = sum(a["slots"][k]["sq"] - bb["slots"][k]["sq"] for k in sl)
    ok("release: the grown sells shrink to their base at OKX (amend — the same orders) · their grown coins → ONE handoff to the"
       " accumulator at their real cost · the 2 injected coins back to the wallet (0:1 back to its base)",
       len(sl) == 3 and shr and e01 and abs(float(e01["sz"]) - b.m._lot_floor(5.0 * BASE_F)) < 1e-9 and len(ho) == 1 and abs(ho[0]["coin"] - coin_in) < 1e-9
       and abs(float(bb["rb"].get("cap_coin_out") or 0) - 2) < 1e-12, (sl, shr, e01 and e01["sz"], ho, coin_in, bb["rb"].get("cap_coin_out")))
    ok("… the memory buy's growth (injected 2$) back to the wallet · the pots' dollars → total_profit · every pot empty · on = off ·"
       " «🔄 [تحرير ربح داخلي]» once · the dashboard's last_trade", not bb["rb"].get("on") and pots(bb["rb"]) < 1e-9
       and bb["slots"]["-6:1"].get("g", 0) == 0 and abs(float(bb["rb"].get("inj_total") or 0)) < 1e-6 and bb["lt"].get("reinvest_release")
       and len([m for m in b.hist() if m.startswith("🔄 [تحرير ربح داخلي]")]) == 1 and not bb["rb"].get("unwind")
       and "4 أمر منشور تصغّر فوراً" in next((m for m in b.hist() if m.startswith("🔄")), "") and not b.errors,
       (bb["rb"], rel_lines(b), b.errors[:3]))
    b.steps = []
    M2 = {}
    n0 = len(b.fill_lines)
    b.run(walk(DN * 2, W) + [snap(M2, "c")])
    c = M2["c"]
    after = b.fill_lines[n0:]
    buys = [f for f in b.ex.fills if f[2] == "buy" and f[3] == D("0.9708")][-3:]
    ok("after the release: every sale ordinary (sale lines, no 💠) · the buys back to their base · total_profit grows · books = wallet",
       not any(m.startswith("💠") for m in after) and sum(m.startswith("🔴") for m in after) >= 6 and c["tp"] > bb["tp"] and all(abs(float(f[4]) - c["slots"]["-1:1"]["q"]) < 1e-9 for f in buys)
       and pots(c["rb"]) < 1e-9 and not b.errors, (buys, c["tp"], bb["tp"], b.errors[:3]))

# ── the setting switched off (no flag) ⇒ the same release · on again ⇒ reinvesting again
if want("onoff"):
    b = bot(100)
    M = {}
    b.run(walk(DN * 2, W) + [snap(M, "a"), cfg(reinvest=False), ("wait", 10), snap(M, "b"), cfg(reinvest=True), ("wait", 10)] + walk(DN, W) + [snap(M, "c")])
    a, bb, c = M["a"], M["b"], M["c"]
    ok("the setting off ⇒ released (dollars → total_profit, the pots empty) · on again ⇒ «🔁» · reinvesting again (💠, pots grow)",
       pots(a["rb"]) > 0 and not bb["rb"].get("on") and pots(bb["rb"]) < 1e-9 and bb["tp"] > a["tp"] + pots(a["rb"]) - 1e-6
       and c["rb"].get("on") and pots(c["rb"]) > 0 and any(m.startswith("🔁") for m in b.hist()) and any(m.startswith("💠") for m in b.hist()[:20])
       and not b.errors, (a["rb"].get("credited"), bb["tp"] - a["tp"], pots(a["rb"]), rel_lines(b), b.errors[:3]))

# ── the flag alone (the setting still on) ⇒ released now, then reinvesting again from nothing (as the grid)
if want("flagonly"):
    b = bot(100)
    M = {}
    b.run(walk(DN * 2, W) + [snap(M, "a"), flag(off=False), ("wait", 10), snap(M, "b")] + walk(DN, W) + [snap(M, "c")])
    a, bb, c = M["a"], M["b"], M["c"]
    ok("the flag alone: everything released (total_profit + the pots) · on again at once («🔁») · new sales reinvest from nothing",
       pots(a["rb"]) > 0 and bb["tp"] >= a["tp"] + pots(a["rb"]) - 1e-6 and bb["rb"].get("on") and pots(c["rb"]) > 0
       and len([m for m in b.hist() if m.startswith("🔄")]) == 1 and any(m.startswith("🔁") for m in b.hist()) and not b.errors,
       (a["tp"], bb["tp"], pots(a["rb"]), rel_lines(b), b.errors[:2]))


# ── OKX refuses to shrink ⇒ unwind: retried every minute until it shrinks
if want("refused"):
    b = bot(100)
    st_ = {"on": False}
    b.ex.fault = lambda op, p: ("code", "51000") if op == "amend" and st_["on"] else None

    def arm(v):
        return ("do", lambda bb: st_.__setitem__("on", v))
    M = {}
    b.run(BUILD + [arm(True), flag(), ("wait", 10), snap(M, "a"), ("wait", 70), arm(False), ("wait", 70), snap(M, "b")])
    a, bb = M["a"], M["b"]
    sl = [k for k in ("-1:1", "-1:2", "-1:3")]
    ok("OKX refused every shrink ⇒ the release takes what is outside the orders now · the grown orders wait (unwind) · said",
       len(a["rb"].get("unwind") or {}) >= 4 and "رفضت المنصة تصغيره فينتظر مصيره" in next((m for m in reversed(b.hist()) if m.startswith("🔄")), ""),
       (a["rb"].get("unwind"), rel_lines(b)))
    ok("… once OKX accepts: retried within a minute ⇒ shrunk to the base · «🔓 [تفكيك]» · coins handed · nothing left · books = wallet",
       not bb["rb"].get("unwind") and pots(bb["rb"]) < 1e-9 and all(abs(float(eo_of(b, bb, k)["sz"]) - b.m._lot_floor(bb["slots"][k]["q"] * BASE_F)) < 1e-9 for k in sl)
       and any(m.startswith("🔓 [تفكيك]") for m in b.hist()) and len(bb["rb"].get("handoffs") or []) >= 1 and not b.errors,
       (bb["rb"].get("unwind"), rel_lines(b), b.errors[:3]))

# ── the grown order fills before it shrinks ⇒ its growth released at its sale · the grown buy ⇒ a grown sell
if want("fate"):
    b = bot(100)
    st_ = {"on": False}
    b.ex.fault = lambda op, p: ("code", "51000") if op == "amend" and st_["on"] else None
    M = {}
    b.run(walk(DN * 3, W) + [snap(M, "a"), ("do", lambda bb: st_.__setitem__("on", True)), flag(), ("wait", 10), snap(M, "b")]
          + walk([0.99, 0.98, 0.97, 0.97], W) + [snap(M, "c")] + walk([0.9806, 0.9903, 1.0, 1.0], W) + [snap(M, "d")])
    a, bb, c, d = M["a"], M["b"], M["c"], M["d"]
    ok("the grown buys couldn't shrink (OKX refused) and filled ⇒ grown sells (unwind follows them)",
       all(c["slots"][k]["side"] == "sell" for k in ("-1:1", "-1:2", "-1:3")) and all((c["rb"].get("unwind") or {}).get(k, {}).get("side") == "sell"
                                                                                for k in ("-1:1", "-1:2", "-1:3")), (c["rb"].get("unwind"), [c["slots"][k]["side"] for k in ("-1:1", "-1:2", "-1:3")]))
    sold = [m for m in b.hist() if m.startswith("🔓 [تفكيك]") and "بيع مكبّر نفّذ" in m]
    ok("… they sold (still refused) ⇒ each sale ordinary profit + its growth released as dollars at that sale · the next buy its base ·"
       " nothing left · books = wallet", len(sold) == 3 and not d["rb"].get("unwind") and pots(d["rb"]) < 1e-9 and d["tp"] > c["tp"]
       and all(d["slots"][k].get("g", 0) == 0 for k in ("-1:1", "-1:2", "-1:3")) and not b.errors, (sold, d["rb"].get("unwind"), b.errors[:3]))

# ── exactly once: the flag written again after the release · a power cut at every moment of a release story
if want("once"):
    b = bot(100)
    M = {}
    b.run(BUILD + [flag(), ("wait", 10), snap(M, "a"), flag(), ("wait", 10), snap(M, "b")])
    ok("the flag again after the release ⇒ nothing released twice (one «🔄» · total_profit the same · one handoff)",
       M["a"]["tp"] == M["b"]["tp"] and len([m for m in b.hist() if m.startswith("🔄")]) == 1 and len(M["b"]["rb"].get("handoffs") or []) == 1
       and not os.path.exists(os.path.join(b.dir, "reinvest_release.flag")) and not b.errors, (rel_lines(b), b.errors[:2]))


def cut_story(cuts=()):
    b = bot(60, {"step_window": 4}, partial=0.5)
    steps = (walk(DN * 2, 150.0) + [req("reinvest_inject.json", [{"k": "0:1", "coin": 2.0}, {"k": "-4:1", "usd": 2.0}], "i1"), ("wait", 150)]
             + walk([0.99, 0.97, 0.97], 150.0) + [flag(), ("wait", 150)] + walk([0.9806, 1.0, 1.0101, 1.0, 0.97, 1.0], 150.0))
    b.run(steps, cuts=cuts)
    st = b.st or {}
    rb = st.get("reinvest") or {}
    out = {"fills": sorted((x[2], str(x[3]), str(x[4])) for x in b.ex.fills), "profit": round(float(st.get("total_profit") or 0), 9),
           "slots": sorted((k, x["side"], x["cyc"], x.get("n", 0), round(float(x.get("g") or 0), 9), round(float(x.get("sq") or 0), 9))
                           for k, x in (st.get("slots") or {}).items()),
           "rb": (bool(rb.get("on")), len(rb.get("unwind") or {}), len(rb.get("handoffs") or []))
           + tuple(round(float(rb.get(f) or 0), 9) for f in ("credited", "inj_total", "out_usd", "out_gain", "out_coin", "cap_coin_out")),
           "log": sorted(m for m in b.hist() if m.startswith(("🟢", "🔴", "💠", "💉", "🔄", "🔓", "🪙", "⏳"))),
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
                        bad.append((k, key, [x for x in r[key] if x not in ref[key]][:2] if isinstance(r[key], list) else (r[key], ref[key])))
                        break
    rel_ok = not ref["rb"][0] and ref["rb"][2] >= 1 and not ref["errors"] and any(m.startswith("🔄") for m in ref["log"])
    ok(f"a power cut at every moment of a release story ({len(ks)} of {ref['moments']} moments · injected coins and dollars, grown"
       f" sells, partial fills, then trading on): the same as with no cut · books = wallet", rel_ok and not bad, (rel_ok, ref["rb"], ref["errors"][:2], sorted(bad, key=str)[:3]))

print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
