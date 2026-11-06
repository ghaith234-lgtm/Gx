# 🪜 ⏳ the long run — one graded-grid bot for hours · days · or open-ended (simulated time on the mock OKX), with everything
#   at once: power cuts at random moments (the bot off 0 s … 5 min, sometimes the price moves while it is off) · a flaky API
#   (answers lost · sends dropped · late · rate-limited · ambiguous) · the internet down for minutes · very fast oscillation and
#   jumps. Audited at EVERY loop: books = wallet (coins and dollars) · no order twice · no stray order · no self-cross · one log
#   line per fill. At the end (the market held, the network clean): every sell paid · never bought over / sold under its price ·
#   the log's profit = the books · and a report of how the bot recovered (resent · found by its id · strays swept · reconnects).
#   python3 devtests/step/t_soak.py [--hours=48 | --forever] [--profile=fast|osc|wild|calm] [--seed=1] [--first=0.005]
#                                   [--sell=0.005] [--parts=3] [--usd=15] [--cuts=6 (per hour)] [--faults=0.03] [-q]
import math, os, random, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from okxsim import Clock, Ex, Bot, D

LINE = re.compile(r"^(🟢|🔴) \[(?:شراء|بيع) فوري\] السعر: ([0-9.]+) \| الكمية: ([0-9.]+)(?: \| الربح: ([+-][0-9.]+)\$)?.* المستوى (-?\d+) · الجزء (\d+)/")


def arg(name, default, cast=float):
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), None)
    return default if v is None else cast(v)


def price_path(rng, profile, p0, seconds, step_s, lo, hi, state):
    """the market for `seconds`: one price every `step_s` (the bot sees each) — fast: big random moves and jumps · osc: a wave
    around a drifting centre crossing the levels again and again · wild: both, jumps up to ±10% · calm: small moves"""
    out, p = [], state.get("p", p0)
    t = state.get("t", 0.0)
    for _ in range(max(1, int(seconds / step_s))):
        t += step_s
        if profile == "calm":
            r = rng.gauss(0, 0.002)
        elif profile == "fast":
            r = rng.gauss(0, 0.007) + (rng.choice([-1, 1]) * rng.uniform(0.02, 0.06) if rng.random() < 0.04 else 0)
        elif profile == "osc":
            c = state.setdefault("c", p0)
            state["c"] = c = min(hi, max(lo, c * math.exp(rng.gauss(0, 0.001))))
            A, T = state.setdefault("A", rng.uniform(0.01, 0.04)), state.setdefault("T", rng.uniform(20, 240))
            if rng.random() < 0.01:
                state["A"], state["T"] = rng.uniform(0.005, 0.05), rng.uniform(15, 300)
            target = c * (1 + A * math.sin(2 * math.pi * t / T)) * math.exp(rng.gauss(0, 0.002))
            r = math.log(target / p)
        else:                                       # wild
            c = state.setdefault("c", p0)
            state["c"] = c = min(hi, max(lo, c * math.exp(rng.gauss(0, 0.003))))
            target = c * (1 + 0.03 * math.sin(2 * math.pi * t / state.setdefault("T", rng.uniform(20, 120))))
            r = math.log(target / p) * 0.7 + rng.gauss(0, 0.008) + (rng.choice([-1, 1]) * rng.uniform(0.03, 0.10) if rng.random() < 0.03 else 0)
        p = min(hi, max(lo, p * math.exp(r)))
        out.append(p)
    state["p"], state["t"] = p, t
    return out


def soak(hours=48.0, profile="fast", seed=1, cfg=None, cuts_per_hour=6.0, faults=0.03, sym=("XRP-USDT", "0.0001", "0.000001", "0.1", 1.0),
         base=None, quote=None, partial=0.4, step_s=3.0, on_hour=None, forever=False, storage=False):
    rng = random.Random(seed)
    sym_, tick, lot, mn, p0 = sym
    cfg = dict({"forced_base_price": p0, "min_price": p0 * 0.6, "up_groups": 2}, **(cfg or {}))
    c = Clock()
    Qv = float(cfg.get("usd_value") or 15)
    ex = Ex(c, sym=sym_, price=p0, tick=tick, lot=lot, mn=mn, base=base if base is not None else round(Qv * 8 / p0, 6),
            quote=quote if quote is not None else Qv * 40, partial=partial, seed=seed)
    b = Bot(ex, cfg)
    W = int(cfg.get("step_window") or 8)
    rep = {"hours": 0, "cuts": 0, "moved_off": 0, "down_min": 0, "fault_calls": 0, "peak_live": [0, 0], "peak_mem": [0, 0],
           "peak_state_kb": 0.0, "window_over": 0, "streak": [0, 0], "max_streak": 0, "slots": 0, "level_view": None}
    st_ = {}
    lo, hi = p0 * 0.45, p0 * 2.2
    calls0 = {"n": 0}

    def flaky(op, p):
        if rng.random() > faults:
            return None
        calls0["n"] += 1
        if op == "place":
            return rng.choice(["drop", "lost", ("late", rng.uniform(2, 25)), ("code", "50011"), ("ambig", rng.random() < 0.5)])
        return rng.choice(["drop", "lost"]) if op == "cancel" else "drop"

    def watch(bb):
        S = (bb.st or {}).get("slots") or {}
        live = bb.mine_open()
        for i, side in enumerate(("buy", "sell")):
            nl = sum(1 for o in live if o["side"] == side and o["acc"] == 0)
            rep["peak_live"][i] = max(rep["peak_live"][i], sum(1 for o in live if o["side"] == side))
            rep["peak_mem"][i] = max(rep["peak_mem"][i], sum(1 for s in S.values() if s["side"] == side and not s.get("o")))
            if nl > W + 2:                          # more fresh orders on OKX than the window — for a moment it is expected (a lost
                rep["window_over"] += 1             # cancel is re-checked · a late order lands) · for long it would be a fault
                rep["streak"][i] += 1
                rep["max_streak"] = max(rep["max_streak"], rep["streak"][i])
            else:
                rep["streak"][i] = 0
        if storage and S:                          # the moment a bought level shows the window best (most of its sells on OKX)
            lv = {}
            for s in S.values():
                if s["side"] == "sell" and s["j"] < 0:
                    lv.setdefault(s["j"], []).append(s)
            for j, ss in lv.items():
                if len(ss) != int(cfg.get("step_parts") or 3):
                    continue
                on = sum(1 for s in ss if s.get("o"))
                if rep["level_view"] is None or on > rep["level_view"]["on"] or (on == rep["level_view"]["on"] and len(ss) > 3 and on < len(ss)):
                    ss = sorted(ss, key=lambda s: s["k"])
                    rep["level_view"] = {"level": j, "buy": ss[0]["bp"], "on": on, "px": float(bb.ex.price),
                                         "sells": [(s["k"], s["sp"], "OKX" if s.get("o") else "memory") for s in ss]}
        try:
            rep["peak_state_kb"] = max(rep["peak_state_kb"], os.path.getsize(os.path.join(bb.dir, f"grid_state_{bb.ex.sym}.json")) / 1024)
        except OSError:
            pass
    b.on_loop = watch
    t0 = time.time()
    h = 0
    while forever or h < hours:
        seg = 3600.0
        prices = price_path(rng, profile, p0, seg, step_s, lo, hi, st_)
        steps = [("px", p, step_s) for p in prices]
        ex.fault = flaky if faults > 0 else None
        if rng.random() < 0.15:                      # the internet down for 1–8 minutes somewhere in this hour
            at, mins = rng.randrange(len(steps)), rng.randint(1, 8)
            steps.insert(at, ("do", lambda bb: setattr(bb.ex, "down", True)))
            steps.insert(min(len(steps), at + 1 + int(mins * 60 / step_s)), ("do", lambda bb: setattr(bb.ex, "down", False)))
            rep["down_min"] += mins
        n_cut = sum(1 for _ in range(int(cuts_per_hour * 3)) if rng.random() < 1 / 3)
        m0 = b.moments
        cuts = sorted(m0 + rng.randint(50, 6500) for _ in range(n_cut))
        off = rng.choice([0.0, 0.0, 5.0, 30.0, 120.0, 300.0])
        off_steps = [("px", prices[rng.randrange(len(prices))] * rng.uniform(0.97, 1.03), 0)] if rng.random() < 0.4 else []
        rep["moved_off"] += bool(off_steps) * n_cut
        cut0 = b.cuts
        b.run(steps, cuts=cuts, off=off, off_steps=off_steps)
        ex.down = False
        rep["cuts"] += b.cuts - cut0
        h += 1
        rep["hours"] = h
        if on_hour:
            on_hour(h, b, rep, time.time() - t0)
        if b.errors:
            break
    ex.fault, ex.down = None, False                   # settle: the market held, the network clean
    b.run([("px", float(ex.price), 0), ("wait", 600)])
    rep["fault_calls"] = calls0["n"]
    S = (b.st or {}).get("slots") or {}
    rep["slots"] = len(S)
    hist = b.hist()
    trades = []
    for msg in b.fill_lines:                     # every fill line written (the log file keeps its newest 1000)
        x = LINE.match(msg)
        if x:
            trades.append((x.group(1), float(x.group(2)), float(x.group(4)) if x.group(4) else None, f"{x.group(5)}:{x.group(6)}"))
    bad = []
    for kind, px, pr, key in trades:
        s = S.get(key)
        if not s:
            bad.append(("unknown slot", key)); continue
        if kind == "🟢" and px > s["bp"] * (1 + 1e-9):
            bad.append(("bought over", key, px, s["bp"]))
        if kind == "🔴" and px < s["sp"] * (1 - 1e-9):
            bad.append(("sold under", key, px, s["sp"]))
        if kind == "🔴" and (pr is None or pr <= 0):
            bad.append(("sell without profit", key, pr))
    logp = sum(pr for k_, _, pr, _ in trades if k_ == "🔴" and pr is not None)
    tp = float((b.st or {}).get("total_profit") or 0)
    rep.update(errors=b.errors[:3], bad=bad[:3], buys=sum(1 for t in trades if t[0] == "🟢"), sells=sum(1 for t in trades if t[0] == "🔴"),
               profit=round(tp, 6), log_vs_books=abs(logp - tp), restarts=b.restarts, audits=b.audits,
               orphans=sum(1 for m in hist if m.startswith("🧹")), reconnects=sum(1 for m in hist if "عاد الاتصال" in m),
               rejections=sum(1 for m in hist if m.startswith("⚠️ [رفض")), secs=round(time.time() - t0, 1),
               fills_on_okx=len(ex.fills))
    rep["ok"] = not b.errors and not bad and rep["log_vs_books"] < 1e-8 and rep["max_streak"] <= 40     # ≤ 2 min over the window
    return rep, b, ex


def say(rep, title):
    v = rep.get("level_view")
    print(f"{'✅' if rep['ok'] else '❌'} {title}: {rep['hours']} h simulated in {rep['secs']} s · {rep['audits']} loops audited · "
          f"{rep['fills_on_okx']} fills on OKX · {rep['buys']} buys / {rep['sells']} sells · profit {rep['profit']}$ (log = books, Δ {rep['log_vs_books']:.1e}) · "
          f"{rep['cuts']} power cuts ({rep['moved_off']} with the price moving while off) · internet down {rep['down_min']} min · "
          f"{rep['fault_calls']} broken API calls · recovered: {rep['reconnects']} reconnects · {rep['orphans']} stray sweeps · "
          f"{rep['rejections']} rejection lines · peak on OKX {rep['peak_live'][0]} buys / {rep['peak_live'][1]} sells · peak in memory "
          f"{rep['peak_mem'][0]} / {rep['peak_mem'][1]} · over the window {rep['window_over']} loops (longest {rep['max_streak'] * 3} s) · "
          f"{rep['slots']} slots · state file ≤ {rep['peak_state_kb']:.0f} KB"
          + (f" — {rep['errors'] or rep['bad']}" if not rep["ok"] else ""), flush=True)
    if v:
        print(f"   🗂 how one level is kept (level {v['level']}, buy {v['buy']}, the price {v['px']:.6g}: {v['on']} sells on OKX · "
              f"{len(v['sells']) - v['on']} in the bot's memory): " +
              " · ".join(f"{k}:{sp}→{where}" for k, sp, where in v["sells"]), flush=True)


if __name__ == "__main__":
    prof = arg("profile", "fast", str)
    cfg = {"step_parts": arg("parts", 3, int), "step_sell": arg("sell", 0.005), "usd_value": arg("usd", 15.0), "grid_percentage": arg("grid", 0.03)}
    if arg("first", None) is not None:
        cfg["step_first"] = arg("first", None)
    forever = "--forever" in sys.argv
    hours = arg("hours", 48.0)

    def tick(h, b, rep, secs):
        if h % 6 == 0 or forever:
            print(f"   … {h} h · {secs:.0f} s · {b.audits} loops · {len(b.ex.fills)} fills · {b.cuts} cuts · errors {len(b.errors)}", flush=True)
    rep, b, ex = soak(hours=hours, profile=prof, seed=arg("seed", 1, int), cfg=cfg, cuts_per_hour=arg("cuts", 6.0),
                      faults=arg("faults", 0.03), on_hour=tick, forever=forever, storage=True)
    say(rep, f"t_soak {prof} · first sell {cfg.get('step_first', cfg['step_sell'])} · between {cfg['step_sell']} · {cfg['step_parts']} sells × {cfg['usd_value']}$")
    sys.exit(0 if rep["ok"] else 1)
