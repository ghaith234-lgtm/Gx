# 📈 v3.36.29 — the trial path on REAL OKX prices, checked against OKX itself (GitHub · public market data · no keys · no orders ·
#   no notifications):
#   A. every period's real candles (week 1m · month 5m · 3 months 15m · 6 months 30m · a year 1H): how many of the expected, the gaps,
#      the pages, the time — and a second, older window (paging further back)
#   B. «does it read the candles to the cent?» — the SAME last week of XRP on 1m / 5m / 15m / 30m / 1H candles, a ♾️ grid of 0.6% and of
#      1.5%: trades · trading profit · real profit — what coarser candles miss · each bar's median candle range
#   C. end to end, the dashboard's own bt_start → its background fetch → the sealed worker → bt_status: a ♾️ grid on 5 real weeks of
#      XRP · a 🪜 graded grid on the last real month of XRP — each path's real profit, holding, bot vs holding, the identities, and the
#      last close against OKX's live ticker
#   python3 ci/bt_real_check.py Holy_Dashboard.pyw [--fake]  ⇒ lines starting with HOLYBT
import importlib.machinery, importlib.util, json, math, os, shutil, statistics, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
FAKE = "--fake" in sys.argv
R = tempfile.mkdtemp(prefix="bt_real_")
json.dump({"port": 8097}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw")); os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); sys.argv = ["x"]; ld.exec_module(m)
m.tg_send = lambda *a, **k: True
m.app_feed_push = lambda *a, **k: True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))
FAIL = []


def P_(*a):
    print("HOLYBT", *a, flush=True)


if FAKE:                                          # offline: the same stand-in as devtests/t_bt_real.py
    NOW = int(time.time())
    SECS = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800, "1H": 3600}

    def _P(t):
        return 1.17 * math.exp(1.5 * (t - NOW) / (365 * 86400)) * (1 + 0.025 * math.sin(t / 21600.0) + 0.006 * math.sin(t / 1700.0))

    def _rows(sym, bar, after=None, hist=True, limit=100):
        sec, now = SECS[bar], int(time.time())
        ts = (min(int(after // 1000) if after else now, now) - 1) // sec * sec
        out = []
        while len(out) < min(int(limit), 100) and ts >= NOW - 800 * 86400:
            o, c = _P(ts), _P(ts + sec)
            out.append([ts, o, max(o, c) * 1.0015, min(o, c) * 0.9985, c, 1000.0, ts + sec <= now])
            ts -= sec
        return out

    m._fc_okx_rows = _rows
    m._okx_pub = lambda p: ({"code": "0", "data": [{"tickSz": "0.0001", "lotSz": "0.000001", "minSz": "0.1"}]} if "instruments" in p
                            else {"code": "0", "data": [{"last": str(_P(time.time()))}]} if "ticker" in p else None)
    m._okx_get = lambda *a, **k: None
SYM = "XRP-USDT"
KEEP = {k: getattr(m, k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")
        if hasattr(m, k)}


def dry(kind, body, spec, p0):
    c, e = m._bt_dry_cfg(kind, body, SYM, spec, p0)            # made for the separate worker: it swaps module globals — put back
    for k, v in KEEP.items():
        setattr(m, k, v)
    return c, e


# ── A. the candles of every period
t_end = int(time.time())
W = {}
for per in ("week", "month", "q3", "h6", "year"):
    bar, sec = m._BT_BAR[per]
    days = m._BT_PER[per][0]
    for k in ((0, 1) if per in ("week", "month") else (0,)):
        t1 = (t_end // sec * sec) - k * days * 86400
        t0 = t1 - days * 86400
        pg = {"n": 0}
        a0 = time.time()
        rows = m._bt_hist(SYM, bar, sec, t0, t1, None, lambda: pg.__setitem__("n", pg["n"] + 1))
        exp = (t1 - t0) // sec
        ts = [r_[0] for r_ in rows]
        gaps = sum(1 for i in range(1, len(ts)) if ts[i] - ts[i - 1] != sec)
        rng = statistics.median([(r_[2] - r_[3]) / r_[1] * 100 for r_ in rows]) if rows else 0
        P_(f"A {per} window {k + 1}: {bar} · {len(rows)} of {exp} candles ({len(rows) / max(1, exp) * 100:.2f}%) · {gaps} gaps · {pg['n']} pages · "
           f"{time.time() - a0:.1f}s · {time.strftime('%Y-%m-%d %H:%M', time.gmtime(t0))} → {time.strftime('%Y-%m-%d %H:%M', time.gmtime(t1))} UTC · "
           f"median candle range {rng:.3f}% · first open {rows[0][1] if rows else '—'} · last close {rows[-1][4] if rows else '—'}")
        if len(rows) < 0.9 * exp:
            FAIL.append(f"A {per} {k + 1}: {len(rows)}/{exp}")
        if k == 0:
            W[per] = {"t0": t0, "t1": t1, "sec": sec, "bar": bar, "o": [r_[1] for r_ in rows], "h": [r_[2] for r_ in rows],
                      "l": [r_[3] for r_ in rows], "c": [r_[4] for r_ in rows]}

# ── B. the same last week on every candle size
spec = m._bt_spec(SYM)
P_(f"B spec {spec}")
wk = W.get("week") or {}
B_t0, B_t1 = wk.get("t0"), wk.get("t1")
for gp in ("0.6", "1.5"):
    base_px = None
    for bar, sec in (("1m", 60), ("5m", 300), ("15m", 900), ("30m", 1800), ("1H", 3600)):
        rows = m._bt_hist(SYM, bar, sec, B_t0 // sec * sec, B_t1 // sec * sec)
        Wb = {"o": [r_[1] for r_ in rows], "h": [r_[2] for r_ in rows], "l": [r_[3] for r_ in rows], "c": [r_[4] for r_ in rows]}
        px = m._bt_ohlc(Wb)
        if not px:
            FAIL.append(f"B {bar}: no candles"); continue
        p0 = px[0]
        q0, b0 = 25 * 25.0, 25 * 15.0 / p0
        cfg, err = dry("grid", {"symbol": SYM, "grid_pct": gp, "usd_value": "25", "min_price": repr(p0 * 0.7), "wallet": "main", "g_type": "grid"}, spec, p0)
        if not cfg:
            FAIL.append(f"B {bar}: {err}"); continue
        a0 = time.time()
        r = m._bt_run("grid", cfg, SYM, px, sec / 4.0, q0, b0, spec)
        S = m._bt_summary("grid", r, q0, b0, p0, sec / 4.0)
        pe = float(r["curve"][-1][1])
        pnl = r["ex"].bal[r["ex"].quote] + r["ex"].bal[r["ex"].base] * pe - (q0 + b0 * p0)
        hold = b0 * (pe - p0)
        rng = statistics.median([(h - l) / o * 100 for o, h, l in zip(Wb["o"], Wb["h"], Wb["l"])])
        if base_px is None:
            base_px = (S["buys"] + S["sells"], float(S["trade"]))
        P_(f"B grid {gp}% · {bar}: {len(rows)} candles · {len(px)} points · median candle range {rng:.3f}% · trades {S['buys']}/{S['sells']} "
           f"({(S['buys'] + S['sells']) / max(1, base_px[0]) * 100:.0f}% of 1m) · trading profit {float(S['trade']):+.2f}$ "
           f"({float(S['trade']) / base_px[1] * 100 if base_px[1] else 0:.0f}% of 1m) · real {pnl:+.2f}$ · hold {hold:+.2f}$ · vs {pnl - hold:+.2f}$ · "
           f"{p0:.4f}→{pe:.4f} · {time.time() - a0:.1f}s · {r['why']}")

# ── C. end to end through the dashboard
live = 0.0
try:                                              # OKX's live ticker itself (not the dashboard's memory)
    live = float(((m._okx_pub(f"/api/v5/market/ticker?instId={SYM}") or {}).get("data") or [{}])[0].get("last") or 0)
except Exception:
    pass
m.PX[SYM] = (W.get("week") or {}).get("c", [0])[-1] or live


def trial(kind, body, per, paths):
    pr = m.bt_prep({"kind": kind, "body": body})
    if not pr.get("ok"):
        FAIL.append(f"C {kind} prep: {pr.get('msg')}"); return
    S = m.bt_start({"kind": kind, "body": body, "period": per, "mood": "real", "paths": paths, "seed": "1", "p0": pr["p0"], "quote": pr["quote_def"],
                    "base": pr["base_def"], "maker": "0.08", "taker": "0.1", "slip": "0.05"})
    if not S.get("ok"):
        FAIL.append(f"C {kind} start: {S.get('msg')}"); return
    a0, st, seen_prep = time.time(), {}, 0
    while time.time() - a0 < 2400:
        st = m.bt_status({"id": S["id"]})
        if st.get("state") == "prep" and st.get("fetch"):
            seen_prep = max(seen_prep, int(st["fetch"].get("pg") or 0))
        if st.get("state") in ("done", "error", "stopped", "lost"):
            break
        time.sleep(1)
    P_(f"C {kind} · {per} · {paths} paths: {st.get('state')} in {time.time() - a0:.0f}s · fetched {seen_prep}+ pages · {st.get('done')}/{st.get('total')} · "
       f"note {st.get('note')} · err {st.get('err')} · wallet {pr['quote_def']}$ + {pr['base_def']} XRP at {pr['p0']}")
    if st.get("state") != "done":
        FAIL.append(f"C {kind}: {st.get('state')} {st.get('err')}"); return
    for p in sorted(st["paths"], key=lambda x: x["n"]):
        s = p["sum"]
        v0 = s["q0"] + s["b0"] * s["p0"]
        ok_ = (abs(s["pnl"] - (s["q1"] + s["b1"] * s["p_end"] - v0)) < 1e-6 and abs(s["hold"] - s["b0"] * (s["p_end"] - s["p0"])) < 1e-6
               and abs(s["vs"] - (s["pnl"] - s["hold"])) < 1e-6)
        if not ok_:
            FAIL.append(f"C {kind} path {p['n'] + 1}: identities")
        P_(f"C {kind} path {p['n'] + 1} {time.strftime('%m-%d', time.gmtime(s['t0']))}→{time.strftime('%m-%d', time.gmtime(s['t1']))}: "
           f"{s['p0']:.4f}→{s['p_end']:.4f} ({(s['p_end'] / s['p0'] - 1) * 100:+.1f}%) · range {s['pmin']:.4f}–{s['pmax']:.4f} · trades {s['buys']}/{s['sells']} · "
           f"bot at the start price {s['result']:+.2f}$ · trading {float(s['trade']):+.2f}$ · REAL {s['pnl']:+.2f}$ ({s['pnl_pct']:+.2f}%) · hold {s['hold']:+.2f}$ · "
           f"vs {s['vs']:+.2f}$ · fees {s['fee_usd']:.2f}$ · {s['secs']:.0f}s · identities {'ok' if ok_ else 'WRONG'}")
    A = (st.get("agg") or {}).get("real") or {}
    P_(f"C {kind} median: real {A.get('pnl_med')} · hold {A.get('hold_med')} · vs {A.get('vs_med')} · bot better than holding in {A.get('vs_pos')} of {st.get('done')}")
    if per == "week":
        last = st["paths"][0]["sum"]["p_end"] if st["paths"] else 0
        P_(f"C the last real close {last} vs OKX's live ticker {live} ({(last / live - 1) * 100 if live else 0:+.2f}%)")
        if live and abs(last / live - 1) > 0.05:
            FAIL.append(f"C last close {last} vs live {live}")


trial("grid", {"symbol": SYM, "grid_pct": "0.6", "usd_value": "25", "min_price": repr(round(m.PX[SYM] * 0.7, 4)), "wallet": "main", "g_type": "grid"}, "week", 5)
trial("grid_step", {"symbol": SYM, "usd_value": "25", "step_parts": "3", "step_sell_pct": "0.15", "step_first_pct": "0.45", "grid_pct": "0.6",
                    "min_price": repr(round(m.PX[SYM] * 0.7, 4)), "up_groups": "1", "forced_base": "", "wallet": "main", "auto": False}, "month", 1)
P_(f"RESULT {'PASS' if not FAIL else 'FAIL'} {FAIL}")
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if not FAIL else 1)
