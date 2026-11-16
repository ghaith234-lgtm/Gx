# ⚡ v3.36.57 — the NEW DCA+ (the free ladder: every order its own distance, size and exit %) against the normal sell DCA on REAL OKX
#   prices (GitHub · public market data · no keys · no orders). The owner (15-11): «هدفي ازيد العملات ما اريد ابيع عملات باسعار واطية او
#   اتضل معلقة». For each coin and each of the last three months (5-minute candles — the trial path's own fetch `_bt_hist` and path
#   `_bt_ohlc`), the same ladder (≈10$ base · 10$ first safety · ×1.5 size · ×1.2 step · 1% first step · 6 safety orders), the real
#   engines on the dashboard's paper exchange (`_bt_run`):
#     dca         the normal sell DCA (dca.py) · 1% target
#     dcap_same   DCA+ with exactly the same ladder and 1% on every order — must behave like the normal DCA (the same prices and sizes)
#     dcap_fast   DCA+ · the same ladder · the exit shrinks on the deep orders: 1 · 1 · 1 · 0.8 · 0.6 · 0.45 · 0.3% (get out sooner)
#   Measured: profit (coin and $ at the last price) · closed cycles · mean exposure (coins sold and not bought back, as a share of the
#   whole ladder) · the longest time stuck with more than half the ladder open · the wallet against the books.
#   python3 ci/dcap_real_check.py Holy_Dashboard.pyw            ⇒ lines starting with HOLYDCAP
import importlib.machinery, importlib.util, json, os, shutil, subprocess, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
COINS = ("SOL-USDT", "XRP-USDT", "DOGE-USDT", "ETH-USDT", "BTC-USDT", "ADA-USDT", "LTC-USDT")
VAR = {"dca": None, "dcap_same": [1, 1, 1, 1, 1, 1, 1], "dcap_fast": [1, 1, 1, 0.8, 0.6, 0.45, 0.3]}


def rows_of(p0, xs):
    """the normal DCA's own ladder (dca.py: price = base × (1 + the summed steps)) written as DCA+ rows (each a distance from the one before)"""
    out, cum, prev = [{"d": 0, "q": 10 / p0, "x": xs[0]}], 0.0, 1.0
    for k in range(1, 7):
        cum += 1.0 * 1.2 ** (k - 1)
        cur = 1 + cum / 100
        out.append({"d": (cur / prev - 1) * 100, "q": 10 / p0 * 1.5 ** (k - 1), "x": xs[k]})
        prev = cur
    return out


def P_(*a):
    print("HOLYDCAP", *a, flush=True)


def load(root):
    shutil.copy(DASH, os.path.join(root, "Holy_Dashboard.pyw"))
    json.dump({"port": 8098}, open(os.path.join(root, "dashboard_config.json"), "w"))
    json.dump({"wallets": []}, open(os.path.join(root, "monitor_config.json"), "w"))
    os.chdir(root)
    ld = importlib.machinery.SourceFileLoader("hd", os.path.join(root, "Holy_Dashboard.pyw"))
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
    m.tg_send = lambda *a, **k: True
    m.app_feed_push = lambda *a, **k: True
    m._okx_post = lambda *a, **k: (_ for _ in ()).throw(AssertionError("no orders"))
    return m


# ── one run in its own process: python3 ci/dcap_real_check.py DASH --one PATHFILE VARIANT
if "--one" in sys.argv:
    pf, var = sys.argv[sys.argv.index("--one") + 1], sys.argv[sys.argv.index("--one") + 2]
    W = json.load(open(pf))
    R = tempfile.mkdtemp(prefix="dcap_one_")
    m = load(R)
    px = m._bt_ohlc(W)
    sec = W["sec"]
    p0, spec, sym = px[0], W["spec"], W["sym"]
    body = {"symbol": sym, "wallet": "main", "dca_type": "dca", "base_order_qty": repr(10 / p0), "avg_order_qty": repr(10 / p0),
            "first_deviation": "1", "step_multiplier": "1.2", "size_multiplier": "1.5", "max_safety_orders": "6", "take_profit_pct": "1",
            "exchange_orders": "3", "cycle_wait_sec": "60"}
    if VAR[var]:
        body.update(dca_type="dca_plus", plus_rows=json.dumps(rows_of(p0, VAR[var])))
    keep = {k: m.__dict__.get(k) for k in ("ROOT", "wallet_keys", "launch", "tg_send", "journal", "log_event", "_acc_spec", "_acc_price", "_okx_get", "bot_dirs")}
    cfg, err = m._bt_dry_cfg("dca", body, sym, spec, p0)
    m.__dict__.update(keep)
    if not cfg:
        print(json.dumps({"err": err})); sys.exit(0)
    q0, b0 = m._bt_wallet_def("dca", cfg, body, p0, spec)
    a0 = time.time()
    r = m._bt_run("dca", cfg, sym, px, sec / 4.0, q0, b0, spec, samples=6000)
    ex, st = r["ex"], r.get("state") or {}
    pe = float(r["curve"][-1][1])
    full = (10 / p0) * (1 + sum(1.5 ** k for k in range(6)))
    exp = [(b0 - c[3]) / full for c in r["curve"]]
    dt_h = (len(px) / max(1, len(r["curve"]))) * (sec / 4.0) / 3600.0
    run_, longest = 0, 0
    for e in exp:
        run_ = run_ + 1 if e > 0.5 else 0
        longest = max(longest, run_)
    opn = sum(float(f["qty"]) for f in st.get("filled") or [])
    prof = float(st.get("total_coin_profit") or 0)
    cyc = st.get("cycles_log") or []
    print(json.dumps({"why": r["why"], "profit_coin": prof, "profit_usd": prof * pe, "cycles": int(st.get("cycles_done") or 0), "plus": bool(cfg.get("dca_plus")),
                      "cmin": min([float(c["profit"]) for c in cyc if not c.get("manual")] or [0]), "mean_exp": sum(exp) / max(1, len(exp)),
                      "longest_h": longest * dt_h, "end_open": opn / full, "rej": len(ex.rejects), "rej_codes": sorted({str(c) for _, c in ex.rejects}),
                      "check": (ex.bal[ex.base] - b0) + opn - prof, "secs": time.time() - a0, "p0": p0, "pe": pe}))
    shutil.rmtree(R, ignore_errors=True)
    sys.exit(0)

# ── the candles, then every run
R = tempfile.mkdtemp(prefix="dcap_real_")
m = load(R)
bar, sec = "5m", 300
t_end = int(time.time()) // sec * sec
jobs, FAIL = [], []
for sym in COINS:
    spec = m._bt_spec(sym)
    for k in (0, 1, 2):
        t1 = t_end - k * 30 * 86400
        t0 = t1 - 30 * 86400
        rows = m._bt_hist(sym, bar, sec, t0, t1)
        if len(rows) < 0.9 * (t1 - t0) / sec:
            FAIL.append(f"{sym} month {k + 1}: {len(rows)} candles"); continue
        W = {"sym": sym, "spec": spec, "sec": sec, "bar": bar, "o": [r_[1] for r_ in rows], "h": [r_[2] for r_ in rows],
             "l": [r_[3] for r_ in rows], "c": [r_[4] for r_ in rows]}
        pf = os.path.join(R, f"px_{sym}_{k}.json")
        json.dump(W, open(pf, "w"))
        lo, hi = min(W["l"]), max(W["h"])
        P_(f"path {sym} month {k + 1}: {time.strftime('%Y-%m-%d', time.gmtime(t0))} → {time.strftime('%Y-%m-%d', time.gmtime(t1))} · "
           f"{len(rows)} candles · {W['o'][0]:.5g} → {W['c'][-1]:.5g} · low {lo:.5g} · high {hi:.5g}")
        for v in VAR:
            jobs.append((sym, k, v, pf))

from concurrent.futures import ThreadPoolExecutor


def run(j):
    sym, k, v, pf = j
    p = subprocess.run([sys.executable, os.path.abspath(__file__), DASH, "--one", pf, v], capture_output=True, text=True, timeout=5400)
    try:
        d = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        d = {"err": (p.stdout + p.stderr)[-500:]}
    d.update(sym=sym, k=k, v=v)
    return d


OUT = []
with ThreadPoolExecutor(max(2, os.cpu_count() or 2)) as tp:
    for d in tp.map(run, jobs):
        OUT.append(d)
        if d.get("err"):
            FAIL.append(f"{d['sym']} {d['k']} {d['v']}: {d['err']}")
            P_(f"run {d['sym']} m{d['k'] + 1} {d['v']}: ERROR {d['err'][:300]}"); continue
        P_(f"run {d['sym']} m{d['k'] + 1} {d['v']:10} profit {d['profit_coin']:+.6g} coin ({d['profit_usd']:+.3f}$) · cycles {d['cycles']} · "
           f"mean exposure {d['mean_exp'] * 100:.1f}% · longest >½ ladder {d['longest_h']:.1f}h · open at end "
           f"{d['end_open'] * 100:.0f}% · refused {d['rej']} {','.join(d.get('rej_codes') or [])} · wallet−books {d['check']:+.1e} · {d['secs']:.0f}s · {d['why']}")
        if d["why"] != "end" or set(d.get("rej_codes") or []) - {"51008", "51016"} or abs(d["check"]) > 1e-6 or d["cmin"] < 0 or d["plus"] != (d["v"] != "dca"):   # 51008 the paper wallet ran short · 51016 a client id repeated inside one simulated second (dca.py's own — the normal DCA too; the engine retries)
            FAIL.append(f"{d['sym']} {d['k']} {d['v']}: why {d['why']} rej {d['rej']} check {d['check']} cycle_min {d['cmin']} plus {d['plus']}")

for v in VAR:
    g = [d for d in OUT if d.get("v") == v and not d.get("err")]
    if not g:
        continue
    a = lambda key: sum(float(d[key]) for d in g) / len(g)
    P_(f"SUM {v:10} over {len(g)} paths: profit {a('profit_usd'):+.3f}$ a path · cycles {a('cycles'):.1f} · "
       f"mean exposure {a('mean_exp') * 100:.1f}% · longest >½ ladder {a('longest_h'):.1f}h · open at end {a('end_open') * 100:.0f}%")
P_("RESULT " + ("✅ all runs clean" if not FAIL else "❌ " + " | ".join(FAIL[:8])))
shutil.rmtree(R, ignore_errors=True)
sys.exit(1 if FAIL else 0)
