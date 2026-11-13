# 📈 the trial path on REAL prices (v3.36.29) — the owner (8-11): «ضعه داخل المسار التجريبي ، ولكل البوتات مع الهادئ ، عادي والعنيف واضف
#   الحقيقي ، زيد خيارات المدة ثلاث اشهر و6 … ومن اين اتجيب بيانات الاصلية وهل يقرا الجارتات بالمليم حتى يعطيني ارباح حقيقية».
#   A closed folder · fake keys · NO network (OKX's public candles are served by a local stand-in: every candle a known price of its
#   time; the trial worker seals itself as always):
#   ① each candle walked open → low → high → close (a rising one) or open → high → low → close (a falling one)
#   ② the candles come back oldest first, contiguous, exactly the window, each its own price · kept in Holy_Backtest/candles: the same
#      window again = no new page · half a new window = only the missing pages
#   ③ a real trial (bt_start → the dashboard fetches in the background, status «prep» with its progress → the sealed worker): a ♾️ grid
#      on 5 real weeks — path 1 = the last week, path 2 = the one before it … · each path: its start = the window's first open, its end =
#      the last close, it walked every candle's high and low · the dollar value of the coins as written · the floor moved with the price ·
#      real profit = what the wallet is worth at the end price − what it was worth at the start · holding = the coins × the move ·
#      bot vs holding = the difference (= the bot's own result + its extra coins × the move) · the median line over the paths · no key
#      anywhere in the job's files
#   ④ every bot kind (9) runs on a real day the same way (the worker as the dashboard starts it) — real fields, the same identities ·
#      the range of 🎚️ and the periodic bot's lo/hi moved to the window's price
#   ⑤ a running bot's own settings (its folder): its base price → the window's first price, its floor by the same ratio
#   ⑥ a coin younger than the paths asked → only the windows it has, with a note · a coin with no candles → a clear error
#   ⑦ stop while fetching → stopped, no worker started, the box free again · ⑦b a half-written «.dash_tmp» file counts for nothing
#   ⑧ 3 months · 6 months: for every market (calm/normal/wild/real) · ~8,700 price points each, ending at their start price (synthetic)
#   ⑨ a real browser: the period and market buttons · the real note · the fetch line · a real run's end card (real profit · holding ·
#      bot vs holding · its dates) · the median line · the table column · no page error
#   python3 devtests/t_bt_real.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR` for ⑨ · BT_SHOT=dir saves screenshots)
import importlib.machinery, importlib.util, json, math, os, shutil, socket, subprocess, sys, tempfile, threading, time, urllib.request

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


def _no_net(*a, **k):
    raise OSError("devtests: no network")


import requests
requests.get = requests.post = requests.request = _no_net
requests.Session.request = lambda self, *a, **k: _no_net()
_urlopen = urllib.request.urlopen
urllib.request.urlopen = lambda u, *a, **k: (_urlopen(u, *a, **k) if str(getattr(u, "full_url", u)).startswith("http://127.0.0.1:") else _no_net())


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="t_btreal_")
P1 = port()
json.dump({"port": P1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": [{"name": "main", "api": "KEYA-btreal", "sec": "SECA-btreal", "pass": "PASA-btreal"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_btreal", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_btreal", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]} if "instruments" in p else None)
m._okx_get = lambda *a, **k: None
m.tg_send = lambda *a, **k: True

# ── OKX's public candles, a local stand-in: every candle = a known price of its time (a trend + two waves + its wicks)
NOW = int(time.time())
YR = 365 * 86400
SECS = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1H": 3600}
LIST = {"XRP-USDT": NOW - 800 * 86400, "NEW-USDT": NOW - 10 * 86400}          # NONE-USDT: none at all


def P(t):
    return 1.17 * math.exp(1.5 * (t - NOW) / YR) * (1 + 0.025 * math.sin(t / 21600.0) + 0.006 * math.sin(t / 1700.0))


def candle(ts, sec):
    o, c = P(ts), P(ts + sec)
    return [ts, o, max(o, c) * 1.0015, min(o, c) * 0.9985, c]


CALLS = []


def rows(sym, bar, after=None, hist=True, limit=100):
    CALLS.append((sym, bar, after))
    sec, lst, now = SECS[bar], LIST.get(sym), int(time.time())
    if lst is None or not hist:
        return []
    ts = (min(int(after // 1000) if after else now, now) - 1) // sec * sec       # «after» = older than this moment
    out = []
    while len(out) < min(int(limit), 100) and ts >= lst:
        out.append(candle(ts, sec) + [1000.0, ts + sec <= now])
        ts -= sec
    return out


m._fc_okx_rows = rows
for s_ in ("XRP-USDT", "NEW-USDT", "NONE-USDT"):
    m.PX[s_] = 1.17
P0 = 1.17
COMMON = {"seed": "7", "maker": "0.08", "taker": "0.1", "slip": "0.05"}
BODY_G = {"symbol": "XRP-USDT", "grid_pct": "0.6", "usd_value": "25", "min_price": "0.9", "wallet": "main", "g_type": "grid"}


def wait(jid, until=("done", "error", "stopped", "lost"), tmo=600, every=0.25, seen=None):
    t0, s = time.time(), {}
    while time.time() - t0 < tmo:
        s = m.bt_status({"id": jid})
        if seen is not None:
            seen.append({k: s.get(k) for k in ("state", "fetch", "done", "total", "prog")})
        if s.get("state") in until:
            return s
        time.sleep(every)
    return s


def close(a, b, rel=1e-9, ab=1e-9):
    return abs(float(a) - float(b)) <= ab + rel * max(abs(float(a)), abs(float(b)))


def files_have(jd, *needles):
    hit = []
    for fn in os.listdir(jd):
        try:
            t = open(os.path.join(jd, fn), encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        hit += [(fn, n) for n in needles if n in t]
    return hit


def ident(S, tol=1e-6):
    """the real fields against the wallet itself"""
    v0 = S["q0"] + S["b0"] * S["p0"]
    pnl = S["q1"] + S["b1"] * S["p_end"] - v0
    hold = S["b0"] * (S["p_end"] - S["p0"])
    return (S.get("real") is True and close(S["pnl"], pnl, 1e-8, tol) and close(S["hold"], hold, 1e-8, tol) and close(S["vs"], S["pnl"] - S["hold"], 1e-8, tol)
            and close(S["vs"], S["result"] + (S["b1"] - S["b0"]) * (S["p_end"] - S["p0"]), 1e-8, tol)
            and close(S["pnl_pct"], S["pnl"] / v0 * 100, 1e-6, 1e-4))


try:
    # ── ① the candle walk
    w1 = m._bt_ohlc({"o": [1.0, 1.0], "h": [1.2, 1.1], "l": [0.9, 0.8], "c": [1.1, 0.85]})
    ok(f"① each candle walked: a rising one open → low → high → close · a falling one open → high → low → close — {w1}",
       w1 == [1.0, 0.9, 1.2, 1.1, 1.0, 1.1, 0.8, 0.85], w1)

    # ── ② the history and its cache
    t1 = NOW // 60 * 60 - 3 * 86400
    t0 = t1 - 86400
    CALLS.clear()
    h1 = m._bt_hist("XRP-USDT", "1m", 60, t0, t1)
    n1 = len(CALLS)
    fp = os.path.join(m.BT_CANDLES, "XRP-USDT_1m.json")
    good = (len(h1) == 1440 and [r_[0] for r_ in h1] == list(range(t0, t1, 60))
            and all(close(r_[1], candle(r_[0], 60)[1], 1e-12, 0) and close(r_[4], candle(r_[0], 60)[4], 1e-12, 0)
                    and close(r_[2], candle(r_[0], 60)[2], 1e-12, 0) and close(r_[3], candle(r_[0], 60)[3], 1e-12, 0) for r_ in h1))
    CALLS.clear()
    h2 = m._bt_hist("XRP-USDT", "1m", 60, t0, t1)
    n2 = len(CALLS)
    CALLS.clear()
    h3 = m._bt_hist("XRP-USDT", "1m", 60, t0 + 43200, t1 + 43200)
    n3 = len(CALLS)
    ok(f"② a real day of 1-minute candles: {len(h1)} candles oldest first, contiguous, exactly the window, each its own open/high/low/close "
       f"({n1} pages) · kept in Holy_Backtest/candles · the same day again: {n2} new pages · half a new day: {n3} pages",
       good and os.path.exists(fp) and n1 == 15 and h2 == h1 and n2 == 0 and len(h3) == 1440 and 1 <= n3 <= 8
       and [r_[0] for r_ in h3] == list(range(t0 + 43200, t1 + 43200, 60)), (len(h1), n1, n2, n3, h1[:2]))

    # ── ③ a real trial: ♾️ grid · 2 real weeks
    PREP = m.bt_prep({"kind": "grid", "body": BODY_G})
    q_def, b_def = float(PREP["quote_def"]), float(PREP["base_def"])
    CALLS.clear()
    S = m.bt_start(dict(COMMON, kind="grid", body=BODY_G, period="week", mood="real", paths=5, p0=P0, quote=q_def, base=b_def))
    seen = []
    st = wait(S.get("id"), seen=seen) if S.get("ok") else {}
    jd = os.path.join(m.BT_DIR, str(S.get("id")))
    pre = [x for x in seen if x["state"] == "prep" and x.get("fetch")]
    ok(f"③ the dashboard fetches the real candles first (status «prep»: {pre[-1]['fetch'] if pre else '—'}) · then the sealed worker · {st.get('state')}",
       S.get("ok") and pre and pre[-1]["fetch"]["total"] == 5 and int(pre[-1]["fetch"].get("pg") or 0) > 0 and st.get("state") == "done"
       and st.get("total") == 5 and len(st.get("paths") or []) == 5, (S, seen[-3:], st.get("err")))
    W = [json.load(open(os.path.join(jd, f"px_{k}.json"))) for k in range(5)] if st.get("state") == "done" else []
    t_end = W[0]["t1"] if W else 0
    ok(f"… path 1 = the last week, path 2 = the one before it … path 5 = 5 weeks back: {[(w['t0'], w['t1'], len(w['o'])) for w in W][:2]}… · "
       f"each 10,080 one-minute candles of its own time · 1m · real",
       len(W) == 5 and abs(t_end - time.time()) < 600 and all(w["t1"] - w["t0"] == 7 * 86400 for w in W)
       and all(W[k + 1]["t1"] == W[k]["t0"] for k in range(4)) and all(len(w["o"]) == 10080 and w["bar"] == "1m" and w["sec"] == 60 for w in W)
       and all(close(w["o"][i], P(w["t0"] + 60 * i), 1e-12, 0) for w in W for i in (0, 1234, 10079))
       and (st.get("job") or {}).get("real") is True and (st.get("job") or {}).get("bar") == "1m", [(w["t0"], w["t1"]) for w in W])
    PS = sorted(st.get("paths") or [], key=lambda p: p["n"])
    rows_ok, info = [], []
    for p in PS:
        Sm, w = p["sum"], W[p["n"]]
        walk = m._bt_ohlc(w)
        D = json.load(open(os.path.join(jd, f"p_{p['n']}.json")))
        rows_ok.append(close(Sm["p0"], w["o"][0], 1e-12, 0) and close(Sm["p_end"], w["c"][-1], 1e-12, 0) and len(walk) == 40320
                       and len(D["c"]) > 1000 and all(close(c[1], walk[c[0]], 1e-9, 1e-12) for c in D["c"])      # every sample = the walk at its index
                       and min(w["l"]) - 1e-12 <= Sm["pmin"] and Sm["pmax"] <= max(w["h"]) + 1e-12 and close(D["dt"], 15.0)
                       and close(Sm["b0"], b_def * P0 / w["o"][0], 1e-9) and close(Sm["q0"], q_def) and Sm["t0"] == w["t0"] and Sm["t1"] == w["t1"]
                       and Sm["bar"] == "1m" and close(Sm["days"], 7, 0, 0.01) and Sm["buys"] + Sm["sells"] > 20 and ident(Sm))
        info.append(f"path {p['n'] + 1}: {Sm['p0']:.4f}→{Sm['p_end']:.4f} · real {Sm['pnl']:+.2f}$ · hold {Sm['hold']:+.2f}$ · vs {Sm['vs']:+.2f}$ "
                    f"· {Sm['buys']}/{Sm['sells']} trades")
    info = info[:2] + ([f"… {len(info) - 2} more"] if len(info) > 2 else [])
    ok("… each path starts at the window's first open, ends at its last close, walked every candle open/low/high/close (40,320 points · "
       "every recorded point = the walk at its place) · the coins' dollar value as "
       "written · real profit = wallet at the end price − at the start · holding = coins × the move · bot vs holding = its own result + its extra "
       "coins × the move — " + " | ".join(info), len(rows_ok) == 5 and all(rows_ok), [p["sum"] for p in PS][:1])
    A = (st.get("agg") or {}).get("real") or {}
    pn = sorted(p["sum"]["pnl"] for p in PS)
    ok(f"… the median line over the paths: real {A.get('pnl_med')} · hold {A.get('hold_med')} · vs {A.get('vs_med')} (better in {A.get('vs_pos')})",
       A and len(pn) == 5 and close(A["pnl_med"], pn[2]) and close(A["pnl_min"], pn[0]) and close(A["pnl_max"], pn[4])
       and A["vs_pos"] == sum(1 for p in PS if p["sum"]["vs"] > 0), A)
    cfgv = st.get("cfg") or {}
    ok(f"… the floor moved with the price to the window's start (0.9 × {W[0]['o'][0] if W else 0:.4f} / {P0} = {cfgv.get('min_price')}) · no key in any of "
       f"the job's files", W and close(cfgv.get("min_price") or 0, 0.9 * W[0]["o"][0] / P0, 1e-9) and not files_have(jd, "KEYA-btreal", "SECA-btreal", "PASA-btreal"),
       (cfgv, files_have(jd, "KEYA-btreal", "SECA-btreal", "PASA-btreal")))

    # ── ④ every bot kind on a real day (the worker exactly as the dashboard starts it)
    DAY = W[0] if W else {}
    k0 = 3 * 1440
    day = {"t0": DAY["t0"] + k0 * 60, "t1": DAY["t0"] + (k0 + 1440) * 60, "sec": 60, "bar": "1m",
           **{kk: DAY[kk][k0:k0 + 1440] for kk in ("o", "h", "l", "c")}} if DAY else {}
    STEP = {"symbol": "XRP-USDT", "usd_value": "25", "step_parts": "3", "step_sell_pct": "0.15", "step_first_pct": "0.45", "grid_pct": "0.6",
            "min_price": "0.9", "up_groups": "1", "forced_base": "", "wallet": "main", "auto": False}
    KB = {"grid": BODY_G, "grid_range": dict(BODY_G, g_type="grid_range", lower_price="1.0", upper_price="1.4", min_price="0"),
          "grid_plus": dict(BODY_G, g_type="grid_plus", buy_offset="0.5"), "grid_step": STEP,
          "dca": {"symbol": "XRP-USDT", "base_order_qty": "10", "avg_order_qty": "10", "first_deviation": "0.6", "step_multiplier": "1.2",
                  "size_multiplier": "1.2", "max_safety_orders": "5", "take_profit_pct": "0.6", "wallet": "main", "dca_type": "dca"},
          "rec_buy": {"symbol": "XRP-USDT", "rec_type": "rec_buy", "mode": "lots", "amount": "10", "every": "1", "unit": "h", "tp_pct": "0.6",
                      "cap": "300", "lo": "0.9", "hi": "1.6", "wallet": "main"},
          "rec_sell": {"symbol": "XRP-USDT", "rec_type": "rec_sell", "mode": "lots", "amount": "10", "every": "1", "unit": "h", "tp_pct": "0.6",
                       "cap": "300", "wallet": "main"},
          "rec_va": {"symbol": "XRP-USDT", "start_usd": "20", "va_mode": "fixed", "every": "1", "unit": "h", "band_pct": "2", "max_order": "20",
                     "cap": "300", "wallet": "main"}}
    KB["dca_buy"] = dict(KB["dca"], dca_type="dca_buy")
    procs, jds = {}, {}
    for kind, body in KB.items():
        pr = m.bt_prep({"kind": kind, "body": body})
        jdk = os.path.join(R, "k_" + kind)
        os.makedirs(jdk, exist_ok=True)
        job = {"id": "bt_k", "v": 1, "kind": kind, "sym": "XRP-USDT", "cfg": None, "body": body, "period": "week", "mood": "real", "paths": 1,
               "seed": 0, "p0": P0, "quote": float(pr.get("quote_def") or 0), "base": float(pr.get("base_def") or 0), "spec": pr.get("spec"),
               "maker": 0.0008, "taker": 0.001, "slip": 0.0005, "vol": 0.045, "t": time.time(), "real": True, "bar": "1m"}
        json.dump(job, open(os.path.join(jdk, "job.json"), "w"))
        json.dump(day, open(os.path.join(jdk, "px_0.json"), "w"))
        procs[kind] = subprocess.Popen([sys.executable, "-u", os.path.join(R, "Holy_Dashboard.pyw"), "--holy-bt", jdk, "0", "1"], cwd=jdk,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        jds[kind] = jdk
        while sum(1 for p_ in procs.values() if p_.poll() is None) >= 4:
            time.sleep(0.5)
    out, bad = [], {}
    for kind, p_ in procs.items():
        try:
            p_.wait(timeout=900)
        except Exception:
            p_.kill()
        s_ = (json.load(open(os.path.join(jds[kind], "s_0.json"))) if os.path.exists(os.path.join(jds[kind], "s_0.json")) else {}).get("sum") or {}
        er = [json.load(open(os.path.join(jds[kind], f))) for f in os.listdir(jds[kind]) if f.startswith("err_")]
        good = bool(s_) and not er and ident(s_) and close(s_["p0"], day["o"][0], 1e-12, 0) and close(s_["p_end"], day["c"][-1], 1e-12, 0)
        if not good:
            bad[kind] = (er, {k: s_.get(k) for k in ("pnl", "hold", "vs", "result", "p0", "p_end", "why")})
        out.append(f"{kind} {s_.get('buys', 0)}/{s_.get('sells', 0)} · {float(s_.get('pnl') or 0):+.2f}$")
    rt = day["o"][0] / P0 if day else 1
    cr = json.load(open(os.path.join(jds["grid_range"], "cfg.json"))) if os.path.exists(os.path.join(jds["grid_range"], "cfg.json")) else {}
    cb = json.load(open(os.path.join(jds["rec_buy"], "cfg.json"))) if os.path.exists(os.path.join(jds["rec_buy"], "cfg.json")) else {}
    ok("④ every bot kind (9) on a real day, the worker as the dashboard starts it — real fields and the same identities: " + " · ".join(out),
       not bad and len(out) == 9, bad)
    ok(f"… the range of 🎚️ ({cr.get('lower_price')} – {cr.get('upper_price')}) and the periodic bot's lo/hi ({cb.get('lo')} – {cb.get('hi')}) moved to the "
       f"window's price (× {rt:.5f})", close(cr.get("lower_price") or 0, 1.0 * rt, 1e-9) and close(cr.get("upper_price") or 0, 1.4 * rt, 1e-9)
       and close(cb.get("lo") or 0, 0.9 * rt, 1e-9) and close(cb.get("hi") or 0, 1.6 * rt, 1e-9), (cr, cb))

    # ── ⑤ a running bot's own settings
    bd = os.path.join(R, "grid_xrp_t")
    os.makedirs(bd, exist_ok=True)
    json.dump({"symbol": "XRP-USDT", "bot_type": "grid", "grid_percentage": 0.006, "usd_value": 25.0, "min_price": 0.9, "forced_base_price": 1.2,
               "knife_guard": False, "is_demo": False, "lower_price": 0, "upper_price": 0, "buy_offset": 0, "auto_restart": True,
               "api_key": "KEYB-btreal", "secret_key": "SECB-btreal", "passphrase": "PASB-btreal"}, open(os.path.join(bd, "config_XRP-USDT.json"), "w"))
    S5 = m.bt_start(dict(COMMON, dir="grid_xrp_t", period="week", mood="real", paths=1, p0=P0, quote=q_def, base=b_def))
    st5 = wait(S5.get("id")) if S5.get("ok") else {}
    jd5 = os.path.join(m.BT_DIR, str(S5.get("id")))
    c5 = st5.get("cfg") or {}
    p5 = ((st5.get("paths") or [{}])[0].get("sum") or {})
    ok(f"⑤ a running bot's own settings: its base price 1.2 → the window's first price ({c5.get('forced_base_price')}), its floor by the same "
       f"ratio ({c5.get('min_price')}) · real {p5.get('pnl')}$ · no key in the job's files",
       st5.get("state") == "done" and p5 and ident(p5) and close(c5.get("forced_base_price") or 0, p5.get("p0") or -1, 1e-12)
       and close(c5.get("min_price") or 0, 0.9 * p5["p0"] / 1.2, 1e-9) and not files_have(jd5, "KEYB-btreal", "SECB-btreal", "PASB-btreal"),
       (S5, st5.get("err"), c5, files_have(jd5, "KEYB-btreal")))

    # ── ⑥ a young coin · a coin without candles
    S6 = m.bt_start(dict(COMMON, kind="grid", body=dict(BODY_G, symbol="NEW-USDT"), period="week", mood="real", paths=5, p0=P0, quote=q_def, base=b_def))
    st6 = wait(S6.get("id")) if S6.get("ok") else {}
    ok(f"⑥ a coin listed 10 days ago, 5 weeks asked → only the week it has: {st6.get('state')} · {st6.get('done')}/{st6.get('total')} · «{st6.get('note')}»",
       st6.get("state") == "done" and st6.get("total") == 1 and st6.get("done") == 1 and "1 من 5" in str(st6.get("note") or ""), (S6, st6.get("err")))
    S7 = m.bt_start(dict(COMMON, kind="grid", body=dict(BODY_G, symbol="NONE-USDT"), period="month", mood="real", paths=1, p0=P0, quote=q_def, base=b_def))
    st7 = wait(S7.get("id")) if S7.get("ok") else {}
    ok(f"… a coin without candles → a clear error: «{st7.get('err')}»", st7.get("state") == "error" and "أسعار حقيقية" in str(st7.get("err") or ""), st7)

    # ── ⑦ stop while fetching
    S8 = m.bt_start(dict(COMMON, kind="grid", body=BODY_G, period="year", mood="real", paths=20, p0=P0, quote=q_def, base=b_def))
    s8 = wait(S8.get("id"), until=("prep",), tmo=30, every=0.05) if S8.get("ok") else {}
    t8 = time.time()
    while S8.get("ok") and time.time() - t8 < 30 and int(((m.bt_status({"id": S8["id"]}).get("fetch")) or {}).get("pg") or 0) < 3:
        time.sleep(0.05)
    busy = m.bt_start(dict(COMMON, kind="grid", body=BODY_G, period="week", mood="calm", paths=1, p0=P0, quote=q_def, base=b_def))
    m.bt_stop({"id": S8.get("id")})
    st8 = wait(S8.get("id"), tmo=30) if S8.get("ok") else {}
    jd8 = os.path.join(m.BT_DIR, str(S8.get("id")))
    time.sleep(1)
    ok(f"⑦ stop while fetching (a real year × 20): while it fetches a new test is refused («{busy.get('msg')}») · after ⏹ {st8.get('state')} · no worker started · "
       f"{sum(1 for f in os.listdir(jd8) if f.startswith('px_'))} of 20 windows fetched",
       S8.get("ok") and s8.get("state") == "prep" and not busy.get("ok") and st8.get("state") == "stopped"
       and not any(f.startswith("w") and f.endswith(".log") for f in os.listdir(jd8)) and not (m._BT_JOBS.get(S8["id"]) or {}).get("fetch")
       and sum(1 for f in os.listdir(jd8) if f.startswith("px_")) < 20, (S8, s8.get("state"), busy, st8.get("state"), os.listdir(jd8)))

    # ── ⑦b (v3.36.33 · p41): a file half-written («.dash_tmp» before its final name) is not read — the status said «error» from
    #    «err_f.json.dash_tmp» while «finished?» waited for «err_f.json» ⇒ a new test in that instant was refused (⑦ once, 19/20)
    jr = "bt_20990101_000000_777"
    jdr = os.path.join(m.BT_DIR, jr)
    os.makedirs(jdr, exist_ok=True)
    json.dump({"id": jr, "paths": 1, "sym": "XRP-USDT", "period": "week", "kind": "grid"}, open(os.path.join(jdr, "job.json"), "w"))
    json.dump({"msg": "ما وصلت أسعار حقيقية"}, open(os.path.join(jdr, "err_f.json.dash_tmp"), "w"))
    json.dump({"n": 0}, open(os.path.join(jdr, "s_0.json.dash_tmp"), "w"))
    a_st, a_fin = (m._safe(m.bt_status, {"id": jr}, default={}) or {}).get("state"), m._bt_finished(jdr)
    os.replace(os.path.join(jdr, "err_f.json.dash_tmp"), os.path.join(jdr, "err_f.json"))
    b_st, b_fin = (m._safe(m.bt_status, {"id": jr}, default={}) or {}).get("state"), m._bt_finished(jdr)
    os.remove(os.path.join(jdr, "err_f.json"))
    c_fin = m._bt_finished(jdr)
    os.replace(os.path.join(jdr, "s_0.json.dash_tmp"), os.path.join(jdr, "s_0.json"))
    d_fin = m._bt_finished(jdr)
    ok(f"⑦b a half-written file counts for nothing: «err_f.json.dash_tmp» ⇒ state {a_st} · finished {a_fin} — renamed ⇒ {b_st} · {b_fin} · "
       f"«s_0.json.dash_tmp» ⇒ finished {c_fin} — renamed ⇒ {d_fin} (status and «finished?» always agree)",
       a_st != "error" and a_fin is False and b_st == "error" and b_fin is True and c_fin is False and d_fin is True, (a_st, a_fin, b_st, b_fin, c_fin, d_fin))
    shutil.rmtree(jdr, ignore_errors=True)

    # ── ⑧ 3 and 6 months for every market
    per_ok = m._BT_PER.get("q3") == (91, 900) and m._BT_PER.get("h6") == (182, 1800) and m._BT_BAR.get("q3") == ("15m", 900) and m._BT_BAR.get("h6") == ("30m", 1800)
    pq, ph = m._bt_path(P0, 91, 900, 0.045, 11), m._bt_path(P0, 182, 1800, 0.045, 12)
    acc = []
    for per in ("q3", "h6"):
        for mood in ("calm", "normal", "wild"):
            r_ = m.bt_start(dict(COMMON, kind="grid", body=BODY_G, period=per, mood=mood, paths=1, p0=P0, quote=q_def, base=b_def))
            acc.append(bool(r_.get("ok")))
            if r_.get("ok"):
                m.bt_stop({"id": r_["id"]}); wait(r_["id"], tmo=30)
    bad_m = m.bt_start(dict(COMMON, kind="grid", body=BODY_G, period="q3", mood="storm", paths=1, p0=P0, quote=q_def, base=b_def))
    ok(f"⑧ 3 months · 6 months: accepted for calm/normal/wild ({acc}) and real (15-minute · 30-minute candles) · {len(pq)} / {len(ph)} price points "
       f"ending at the start price · an unknown market refused",
       per_ok and all(acc) and len(acc) == 6 and len(pq) == 8737 and len(ph) == 8737 and pq[-1] == P0 == ph[-1] and not bad_m.get("ok"), (per_ok, acc, len(pq), len(ph), bad_m))

    # ── ⑨ a real browser
    srv = m.ThreadingHTTPServer(("127.0.0.1", P1), m.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    JS = r'''
const { chromium } = require('playwright');
(async () => {
  const SHOT = process.argv[4] || '';
  const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 430, height: 1500 }, deviceScaleFactor: SHOT ? 2 : 1 });
  const shot = async (n, sel) => { if (!SHOT) return; const e = await pg.$(sel); if (e) await e.screenshot({ path: `${SHOT}/${n}.png` }) };
  await pg.emulateMedia({ reducedMotion: 'reduce' });
  const errs = []; pg.on('pageerror', e => errs.push(String(e)));
  await pg.route('**/*', rt => (/^https?:\/\/127\.0\.0\.1[:/]/.test(rt.request().url()) ? rt.continue() : rt.abort()));
  await pg.routeWebSocket(/.*/, () => {});
  await pg.goto(process.argv[2], { waitUntil: 'domcontentloaded' });
  await pg.waitForFunction(() => typeof btOpen === 'function', null, { timeout: 40000 });
  await pg.evaluate(() => { const sp = document.getElementById('splash'); if (sp) sp.remove() });
  const body = JSON.parse(process.argv[3]);
  await pg.evaluate(b => btOpen({ kind: 'grid', body: b }), body);
  await pg.waitForSelector('#bt_go', { timeout: 30000 });
  const seg = k => pg.evaluate(k => [...document.querySelectorAll(`#btov .btseg[data-k="${k}"] button`)].map(b => b.innerText.trim()), k);
  const o = { per: await seg('period'), mood: await seg('mood') };
  const click = (k, v) => pg.click(`#btov .btseg[data-k="${k}"] button[data-v="${v}"]`);
  await click('mood', 'real'); o.note_real = await pg.innerText('#bt_note');
  await click('period', 'h6'); o.note_h6 = await pg.innerText('#bt_note');
  await click('mood', 'calm'); o.note_calm = await pg.innerText('#bt_note');
  o.fetch = await pg.evaluate(() => { btProg({ state: 'prep', fetch: { done: 1, total: 3, pg: 12 }, done: 0, total: 3 }); return document.getElementById('bt_prog').innerText });
  await click('mood', 'real'); await click('period', 'week'); await click('paths', '5');
  await shot('1_form_real', '.btbox');
  await pg.click('#bt_go');
  await pg.waitForFunction(() => BT.st && BT.st.state === 'done', null, { timeout: 300000 });
  await pg.waitForFunction(() => { const e = document.getElementById('bt_end'); return e && !e.hidden && e.innerText.length > 50 }, null, { timeout: 60000 });
  o.end = await pg.innerText('#bt_end'); o.head = await pg.innerText('.btplh');
  await shot('2_results', '#bt_res .btagg'); await shot('3_end_card', '#bt_end'); await shot('4_player', '.btpl');
  o.agg = await pg.evaluate(() => (document.querySelector('.btagg') || {}).innerText || '');
  o.th = await pg.evaluate(() => [...document.querySelectorAll('.bttbl thead th')].map(t => t.textContent.trim()));      // (inside a closed <details>)
  o.row1 = await pg.evaluate(() => { const r = document.querySelector('.bttbl tbody tr'); return r ? r.textContent : '' });
  o.st = await pg.evaluate(() => ({ total: BT.st.total, done: BT.st.done, note: BT.st.note, S: BT.st.paths[0].sum }));
  o.errs = errs; console.log(JSON.stringify(o)); await br.close();
})().catch(e => { console.log(JSON.stringify({ err: String(e) })); process.exit(1) });
'''
    jsf = os.path.join(R, "ui.js"); open(jsf, "w").write(JS)
    env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
    rr = subprocess.run(["node", jsf, f"http://127.0.0.1:{P1}/", json.dumps(BODY_G), os.environ.get("BT_SHOT", "")], capture_output=True, text=True, timeout=600, cwd="/tmp", env=env)
    U = json.loads(rr.stdout.strip().splitlines()[-1]) if rr.stdout.strip() else {"err": rr.stderr[-600:]}
    ok(f"⑨ the browser: periods {U.get('per')} · markets {U.get('mood')}",
       U.get("per") == ["أسبوع", "شهر", "3 أشهر", "6 أشهر", "سنة"] and U.get("mood") == ["هادئ", "عادي", "عنيف", "📈 حقيقي"], U)
    ok(f"… the real note: «{str(U.get('note_real'))[:160]}…» · 6 months real = 30-minute candles · calm = the synthetic note",
       "أسعار OKX الحقيقية" in str(U.get("note_real")) and "1 دقيقة" not in str(U.get("note_real")) and "5 دقائق" in str(U.get("note_real"))
       and "30 دقيقة" in str(U.get("note_h6")) and "6 أشهر" in str(U.get("note_h6")) and "تقلّب" in str(U.get("note_calm"))
       and "ينتهي عند السعر نفسه" in str(U.get("note_calm")), (U.get("note_real"), U.get("note_h6"), U.get("note_calm")))
    ok(f"… the fetch line: «{str(U.get('fetch')).strip()}»", "يجلب أسعار OKX الحقيقية" in str(U.get("fetch")) and "1 من 3" in str(U.get("fetch"))
       and "12 صفحة" in str(U.get("fetch")), U.get("fetch"))
    E, S9 = str(U.get("end")), (U.get("st") or {}).get("S") or {}
    ok(f"… a real run (a week · 5 paths — their candles already kept from ③): the end card «{E[:150]}…» · head «{str(U.get('head'))[:60]}»",
       "على الأسعار الحقيقية · السعر من" in E and "📈 الربح الحقيقي بسعر النهاية" in E and "لو مسكت محفظتك بلا بوت" in E and "البوت مقابل المسك" in E
       and "ما صنعه البوت (بسعر البداية" in E and "←" in str(U.get("head")) and "أسعار OKX الحقيقية من" in E and "شمعة كل دقيقة" in E
       and S9.get("real") is True and (U.get("st") or {}).get("total") == 5, (E[:900], U.get("head"), U.get("err")))
    ok(f"… the median line «{str(U.get('agg'))[-200:]}» · the table column {U.get('th')}",
       "📈 على الأسعار الحقيقية" in str(U.get("agg")) and "البوت مقابل المسك" in str(U.get("agg")) and "📈 الحقيقي · المسك" in (U.get("th") or [])
       and "←" in str(U.get("row1")), (U.get("agg"), U.get("th"), U.get("row1")))
    ok("… no page error", not U.get("errs") and not U.get("err"), (U.get("errs"), U.get("err")))
except Exception as ex:
    import traceback
    traceback.print_exc()
    ok("the test ran to its end", False, repr(ex))
finally:
    for j in list(getattr(m, "_BT_JOBS", {}).values()):
        for p_ in j.get("procs") or []:
            if p_.poll() is None:
                p_.kill()
    os.chdir("/")
    shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_bt_real: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
