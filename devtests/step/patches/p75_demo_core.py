# 🧪 patch 75 (dashboard v3.36.46 · the demo — the server side) — the owner (14-11): «اريد اسوي نشر demo بنفس المحركات وينشرن تحت بعد
#   الحقيقيات يعني خط فاصل بينهم ما فيه مجموع بينهم فقط كل بوت وكرته وينكتب عليه ديمو» · «البوت الديمو يتحدث مع المحرك يعني هو نفسه».
#   A demo bot = the REAL engine file of its kind (the very one a real bot runs), started by a small runner (holy_demo.py, written by
#   the dashboard) that gives it a paper exchange instead of OKX: the trial sandbox's own exchange (_BtEx — the same source, not a copy)
#   on the live OKX price (the public ticker — no keys) and a paper wallet kept in the bot's folder (demo_wallet.json: balances ·
#   frozen · orders · fills — it survives a restart). Nothing reaches OKX's private side: no keys, no orders.
#   · deploy_demo(kind, body): the settings are the real deploy's own, to the letter — the deploy function itself runs in a separate
#     process on a temporary root (the trial's _bt_dry_cfg) — so the five deploy functions are not touched at all
#   · launch(): a demo bot starts through the runner (the reinvest wrapper too, like a real bot)
#   · balances_once(): a demo card's balances and open orders come from its paper wallet
#   · every place that already keeps demo bots out (totals · ledgers · Telegram · the guard · reports) stays as it is
#   python3 devtests/step/patches/p75_demo_core.py Holy_Dashboard.pyw
import os, sys

DEMO_BLOCK = r'''
# ═══════════════ 🧪 v3.36.46: الديمو بالمحرك الحقيقي — منصة وهمية بأسعار OKX الحية ومحفظة وهمية بمجلد البوت ═══════════════
#   المالك (14-11): «نشر demo بنفس المحركات … كل بوت وكرته وينكتب عليه ديمو» · «البوت الديمو يتحدث مع المحرك يعني هو نفسه».
#   ملف المحرك نفسه (اللي يشغّله البوت الحقيقي) يشتغل عبر holy_demo.py: منصة الصندوق المغلق (_BtEx — نفس المصدر) على سعر OKX الحي
#   (الشريط العام — بلا مفاتيح) ومحفظة وهمية (demo_wallet.json) · ولا مفاتيح ولا أوامر حقيقية.
DEMO_RUNNER = "holy_demo.py"
DEMO_WALLET = "demo_wallet.json"
_DEMO_SRC = {"s": None}
_DEMO_HEAD = """# 🧪 Holy demo runner — the REAL engine of this bot on a paper exchange: the live OKX price (public · no keys) and a paper wallet
#   (demo_wallet.json). Written by the dashboard — do not edit (it is rewritten at every start).
import builtins as _bt_bi, datetime as _bt_dtm, itertools as _bt_it, json, math, os, sys, threading, time, types as _bt_types
import urllib.parse as _bt_up, urllib.request as _ur
from decimal import Decimal as _BtD, InvalidOperation as _BtDI

"""
_DEMO_TAIL = """


# ═══════════ the paper exchange · the price feed · the engine ═══════════
MAKER, TAKER, SLIP = 0.0008, 0.001, 0.0003
FEED = os.environ.get("HOLY_DEMO_FEED") or ""          # the tests: a local price file instead of OKX (no network in tests)


def _pub(path):
    if FEED:
        try:
            f = json.load(open(FEED, encoding="utf-8"))
        except Exception:
            f = {}
        if "/market/ticker" in path:
            p = repr(float(f.get("last") or 0))
            return {"code": "0", "data": [{"last": p, "bidPx": p, "askPx": p, "ts": str(int(time.time() * 1000))}]}
        if "/public/instruments" in path:
            return {"code": "0", "data": [{k: str(f.get(k) or "") for k in ("tickSz", "lotSz", "minSz")}]}
        return {"code": "0", "data": []}
    rq = _ur.Request("https://www.okx.com" + path, headers={"User-Agent": "Holy-demo"})
    with _ur.urlopen(rq, timeout=8) as r:
        return json.loads(r.read().decode("utf-8"))


_bt_route_paper = _bt_route


def _bt_route(ex, method, url, body=None):              # the paper side first · public market data from OKX itself
    try:
        return _bt_route_paper(ex, method, url, body)
    except ConnectionError:
        u = _bt_up.urlparse(url)
        if method == "GET" and (u.path.startswith("/api/v5/market/") or u.path.startswith("/api/v5/public/")):
            return _pub(u.path + ("?" + u.query if u.query else ""))
        raise


class _Clock:
    @property
    def t(self):
        return time.time()

    def lat(self, s=0.05):
        pass

    def idle(self, s):
        time.sleep(max(0.0, float(s or 0)))

    def sleep(self, s):
        time.sleep(max(0.0, float(s or 0)))


class _Paper(_BtEx):
    KEEP = 3000

    def __init__(self, sym, price, spec, w, path):
        base, quote = sym.split("-")
        bal = w.get("bal") or {}
        super().__init__(sym, price, float(bal.get(quote) or 0), float(bal.get(base) or 0),
                         float(spec["tickSz"]), float(spec["lotSz"]), float(spec["minSz"]), MAKER, TAKER, SLIP)
        self.path = path
        frz = w.get("frz") or {}
        self.frz = {base: float(frz.get(base) or 0), quote: float(frz.get(quote) or 0)}
        self.orders = dict(w.get("orders") or {})
        self.by_cl = dict(w.get("by_cl") or {})
        self.fills = [tuple(x) for x in (w.get("fills") or [])]
        self.fees.update({k: float(v) for k, v in (w.get("fees") or {}).items()})
        nxt = max([int(k) for k in self.orders if str(k).isdigit()] + [int(w.get("next_id") or 100000)]) + 1
        self.ids = _bt_it.count(nxt)
        self.clock = _Clock()
        self.w0 = w
        self.ver, self.saved = 0, -1

    def _fill(self, o, px, maker):
        _BtEx._fill(self, o, px, maker)
        self.ver += 1

    def place(self, *a, **k):
        r = _BtEx.place(self, *a, **k)
        self.ver += 1
        return r

    def cancel(self, *a, **k):
        r = _BtEx.cancel(self, *a, **k)
        self.ver += 1
        return r

    def amend(self, *a, **k):
        r = _BtEx.amend(self, *a, **k)
        self.ver += 1
        return r

    def save(self, force=False):
        with self.lk:
            if self.saved == self.ver and not force:
                return
            closed = sorted((o for o in self.orders.values() if o.get("state") != "live"), key=lambda o: float(o.get("cTime") or 0))
            for o in closed[:max(0, len(closed) - self.KEEP)]:
                self.orders.pop(o["id"], None)
                if o.get("cl"):
                    self.by_cl.pop(o["cl"], None)
            del self.rejects[:-200]
            w = {"v": 1, "sym": self.sym, "px": self.p, "ts": time.time(), "bal": dict(self.bal), "frz": dict(self.frz),
                 "orders": self.orders, "by_cl": self.by_cl, "fills": [list(x) for x in self.fills[-500:]], "fees": dict(self.fees),
                 "next_id": max([int(k) for k in self.orders if str(k).isdigit()] + [int(self.w0.get("next_id") or 100000)]),
                 "start": self.w0.get("start") or {}}
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(w, f)
            os.replace(tmp, self.path)
            self.saved = self.ver


def _feed_loop(ex, sym):
    while True:
        try:
            d = _pub("/api/v5/market/ticker?instId=" + sym)
            p = float(((d.get("data") or [{}])[0] or {}).get("last") or 0)
            if p > 0:
                ex.set_price(p)
        except Exception:
            pass
        try:
            ex.save()
        except Exception:
            pass
        time.sleep(1.0 if FEED else 2.0)


def _main():
    script = sys.argv[1]
    main_script = sys.argv[2] if len(sys.argv) > 2 else script
    folder = os.getcwd()
    cfgp = next((n for n in os.listdir(folder) if n.startswith("config_") and n.endswith(".json")), None)
    cfg = json.load(open(os.path.join(folder, cfgp), encoding="utf-8"))
    sym = cfg["symbol"]
    wp = os.path.join(folder, "demo_wallet.json")
    try:
        w = json.load(open(wp, encoding="utf-8"))
    except Exception:
        w = {"bal": {sym.split("-")[1]: 1000.0}, "start": {sym.split("-")[1]: 1000.0}}
    spec, px = w.get("spec") or {}, 0.0
    while not (spec.get("tickSz") and spec.get("lotSz") and px > 0):
        try:
            if not spec.get("tickSz"):
                d = (_pub("/api/v5/public/instruments?instType=SPOT&instId=" + sym).get("data") or [{}])[0]
                spec = {k: float(d.get(k) or 0) for k in ("tickSz", "lotSz", "minSz")}
            px = float(((_pub("/api/v5/market/ticker?instId=" + sym).get("data") or [{}])[0] or {}).get("last") or 0)
        except Exception:
            pass
        if not (spec.get("tickSz") and px > 0):
            print("🧪 demo: waiting for the OKX price…", flush=True)
            time.sleep(5)
    w["spec"] = spec
    ex = _Paper(sym, px, spec, w, wp)
    ex.save(force=True)
    threading.Thread(target=_feed_loop, args=(ex, sym), daemon=True).start()
    F = _bt_fakes(ex, ex.clock)
    mods = {k: F[k] for k in ("okx", "okx.Trade", "okx.MarketData", "requests", "urllib", "urllib.request", "urllib.error", "websocket")}
    real_import = _bt_bi.__import__
    bi = dict(_bt_bi.__dict__)
    main_src = open(os.path.join(folder, main_script), encoding="utf-8").read() if main_script != script else None

    def _imp(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0:
            if name == "main" and main_src is not None:
                if "main" not in mods:
                    m = _bt_types.ModuleType("main")
                    m.__dict__.update({"__file__": os.path.join(folder, main_script), "__builtins__": bi})
                    mods["main"] = m
                    exec(compile(main_src, os.path.join(folder, main_script), "exec"), m.__dict__)
                return mods["main"]
            if name in mods:
                return mods[name] if (fromlist or "." not in name) else mods[name.split(".")[0]]
            top = name.split(".")[0]
            if top in mods and not fromlist and top != "main":
                return mods[top]
        return real_import(name, globals, locals, fromlist, level)

    bi["__import__"] = _imp
    print(f"🧪 demo · {sym} · the real engine ({script}) on a paper exchange · live price {px}", flush=True)
    sys.argv = [script]
    g = {"__name__": "__main__", "__file__": os.path.join(folder, script), "__builtins__": bi}
    try:
        exec(compile(open(os.path.join(folder, script), encoding="utf-8").read(), os.path.join(folder, script), "exec"), g)
    finally:
        try:
            ex.save(force=True)
        except Exception:
            pass


if __name__ == "__main__":
    _main()
"""


def demo_runner_src():
    """🧪 مصدر holy_demo.py: منصة الصندوق المغلق نفسها (_BtEx · _bt_route · _bt_fakes — نفس المصدر، مو نسخة) + المحفظة والسعر الحي"""
    if _DEMO_SRC["s"] is None:
        import ast as _ast
        src = open(os.path.abspath(__file__), encoding="utf-8").read()
        want = ("_bt_dec", "_bt_on", "_bt_num", "_BtEx", "_BtResp", "_bt_mod", "_bt_route", "_bt_fakes")
        got = {}
        for n in _ast.parse(src).body:
            if isinstance(n, (_ast.FunctionDef, _ast.ClassDef)) and n.name in want and n.name not in got:
                got[n.name] = _ast.get_source_segment(src, n)
        miss = [k for k in want if not got.get(k)]
        if miss:
            raise RuntimeError("demo runner: missing " + ", ".join(miss))
        _DEMO_SRC["s"] = _DEMO_HEAD + "\n\n\n".join(got[k] for k in want) + _DEMO_TAIL
    return _DEMO_SRC["s"]


def _demo_write_runner(d):
    p = os.path.join(d, DEMO_RUNNER)
    src = demo_runner_src()
    try:
        if os.path.exists(p) and open(p, encoding="utf-8").read() == src:
            return True
    except Exception:
        pass
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(src)
    os.replace(tmp, p)
    return True


def demo_wallet(b):
    """المحفظة الوهمية لبوت ديمو (للبطاقة) — أو None"""
    w = load_json(os.path.join(b["dir"], DEMO_WALLET))
    return w if isinstance(w, dict) else None


def deploy_demo(kind, data):
    """🧪 v3.36.46: بوت ديمو بالمحرك الحقيقي نفسه — الإعداد = إعداد النشر الحقيقي بالحرف (دالة النشر نفسها بعملية منفصلة على جذر مؤقت ·
    بلا مفاتيح) · يتداول على منصة وهمية بسعر OKX الحي ومحفظة وهمية · خارج كل المجاميع والإشعارات"""
    if getattr(sys, "frozen", False):
        return {"ok": False, "msg": "الديمو يحتاج نسخة بايثون من اللوحة"}
    if kind not in _BT_KINDS:
        return {"ok": False, "msg": "نوع بوت غير معروف للديمو"}
    body = {k: v for k, v in dict(data or {}).items() if k not in ("demo", "demo_usd", "demo_coin", "wallet", "api_key", "secret_key", "passphrase")}
    P = bt_prep({"kind": kind, "body": body})
    if not P.get("ok"):
        return {"ok": False, "msg": P.get("msg") or "تعذّر تجهيز الديمو"}
    sym, base, quote = P["sym"], P["base"], (P["sym"].split("-") + ["USDT"])[1]
    if float(P.get("p0") or 0) <= 0:
        return {"ok": False, "msg": "سعر العملة غير معروف الآن — أعد المحاولة بعد ثوانٍ"}
    try:
        usd = float(data.get("demo_usd")) if data.get("demo_usd") not in (None, "") else float(P.get("quote_def") or 0)
        coin = float(data.get("demo_coin")) if data.get("demo_coin") not in (None, "") else float(P.get("base_def") or 0)
    except Exception:
        return {"ok": False, "msg": "اكتب رصيد الديمو أرقاماً"}
    if not (usd == usd and coin == coin) or usd < 0 or coin < 0 or (usd <= 0 and coin <= 0) or usd > 1e9 or coin > 1e15:
        return {"ok": False, "msg": "رصيد الديمو: دولار أو عملة أكبر من صفر"}
    jd = _bt_tmp.mkdtemp(prefix="holy_democfg_")
    try:
        jp = os.path.join(jd, "job.json")
        save_json_atomic(jp, {"kind": kind, "body": body, "sym": sym, "spec": P["spec"], "p0": float(P["p0"])})
        try:
            subprocess.run([PYTHON_EXE, "-u", os.path.abspath(__file__), "--holy-demo-cfg", jp], cwd=jd, timeout=120,
                           capture_output=True, creationflags=(subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0))
        except Exception as e:
            return {"ok": False, "msg": f"تعذّر تجهيز إعداد الديمو: {type(e).__name__}"}
        out = load_json(jp + ".out") or {}
    finally:
        shutil.rmtree(jd, ignore_errors=True)
    cfg = out.get("cfg")
    if not isinstance(cfg, dict) or not cfg:
        return {"ok": False, "msg": str(out.get("err") or "إعدادات الديمو غير صالحة")}
    cfg.update({"api_key": "", "secret_key": "", "passphrase": "", "is_demo": True, "symbol": sym,
                "auto_restart": bool(data.get("auto", True))})
    cfg.pop("bot_id", None)
    folder = _new_bot_folder("demo_" + base.lower())
    full = os.path.join(ROOT, folder)
    os.makedirs(full, exist_ok=True)
    save_json_atomic(os.path.join(full, f"config_{sym}.json"), cfg)
    eng_src, eng_script, _ = engine_for(cfg)
    with open(os.path.join(full, eng_script), "w", encoding="utf-8") as f:
        f.write(eng_src)                                  # 🧬 المحرك الحقيقي نفسه
    start = {quote: round(usd, 8), base: round(coin, 12)}
    save_json_atomic(os.path.join(full, DEMO_WALLET), {"v": 1, "sym": sym, "bal": dict(start), "start": dict(start), "start_px": float(P["p0"]),
                                                        "spec": P["spec"], "orders": {}, "by_cl": {}, "fills": [], "ts": time.time()})
    _drop_reinvest(full)
    b = {"dir": full, "cfg_path": os.path.join(full, f"config_{sym}.json"), "cfg": cfg, "symbol": sym}
    ok, msg = launch(b)
    _lbl = (_BOT_KINDS.get(kind) or {}).get("ico", "") + " " + (_BOT_KINDS.get(kind) or {}).get("lbl", kind)
    return {"ok": ok, "dir": folder, "msg": (f"🧪 انطلق بوت ديمو ({_lbl.strip()}) — {sym} · بالمحرك الحقيقي على منصة وهمية بسعر OKX الحي · "
                                             f"المحفظة الوهمية {usd:g} {quote}" + (f" + {coin:g} {base}" if coin > 0 else "")) if ok else msg}


def _demo_cfg_child(jp):
    """عملية منفصلة بلا شبكة: إعداد النشر الحقيقي بالحرف (دالة النشر نفسها على جذر مؤقت)"""
    _bt_seal()
    job = load_json(jp) or {}
    try:
        cfg, err = _bt_dry_cfg(job["kind"], job.get("body") or {}, job["sym"], job["spec"], float(job["p0"]))
    except Exception as e:
        cfg, err = None, f"{type(e).__name__}: {e}"
    save_json_atomic(jp + ".out", {"cfg": cfg, "err": err})
    return 0

'''

R = [
    ('''def launch(b):
    sp, hp, lp = paths_of(b)
    eng_src, eng_script, _ = engine_for(b["cfg"])
    script = "demo.py" if b["cfg"].get("is_demo") and os.path.exists(os.path.join(b["dir"], "demo.py")) else eng_script''',
     DEMO_BLOCK + '''
def launch(b):
    sp, hp, lp = paths_of(b)
    eng_src, eng_script, _ = engine_for(b["cfg"])
    script = eng_script                                   # 🧪 v3.36.46: الديمو كمان = المحرك الحقيقي (عبر holy_demo.py) — مو demo.py
    _demo = bool(b["cfg"].get("is_demo"))'''),
    ('''    p = subprocess.Popen([PYTHON_EXE, "-u", script], cwd=b["dir"], creationflags=flags,
                         stdout=log_f, stderr=log_f, env=env)''',
     '''    if _demo:
        try:
            _demo_write_runner(b["dir"])                  # 🧪 يُكتب من جديد بكل إقلاع (نفس منصة الصندوق المغلق)
        except Exception as _de:
            log_f.close()
            return False, f"تعذّر كتابة مشغّل الديمو: {type(_de).__name__}"
    p = subprocess.Popen([PYTHON_EXE, "-u"] + ([DEMO_RUNNER, script, eng_script] if _demo else [script]), cwd=b["dir"], creationflags=flags,
                         stdout=log_f, stderr=log_f, env=env)'''),
    ('''def balances_once():
    for b in bot_dirs().values():
        cfg = b["cfg"]
        if cfg.get("is_demo"):
            continue''',
     '''def balances_once():
    for b in bot_dirs().values():
        cfg = b["cfg"]
        if cfg.get("is_demo"):
            _safe(_demo_bal, b, default=None)             # 🧪 v3.36.46: من محفظته الوهمية
            continue'''),
    ('''def _demo_cfg_child(jp):''',
     '''def _demo_bal(b):
    """🧪 أرصدة بطاقة الديمو وأوامرها المفتوحة — من محفظته الوهمية (نفس حقول BAL)"""
    w = demo_wallet(b)
    if not w:
        return
    sym = b["symbol"]; base = sym.split("-")[0]
    quote = (sym.split("-") + ["USDT"])[1] or "USDT"
    bal, frz = w.get("bal") or {}, w.get("frz") or {}
    px = float(PX.get(sym) or w.get("px") or 0)
    ent = BAL.setdefault(b["dir"], {})
    live = [o for o in (w.get("orders") or {}).values() if o.get("state") == "live"]
    ent.update(usdt=round(float(bal.get(quote) or 0) - float(frz.get(quote) or 0), 2),
               q_av=round(float(bal.get(quote) or 0) - float(frz.get(quote) or 0), 6),
               base=round(float(bal.get(base) or 0) - float(frz.get(base) or 0), 4),
               base_eq=round(float(bal.get(base) or 0), 8), base_usd=round(float(bal.get(base) or 0) * px, 2),
               ob=sum(1 for o in live if o.get("side") == "buy"), os=sum(1 for o in live if o.get("side") == "sell"),
               oid_b=[str(o.get("id")) for o in live if o.get("side") == "buy"], oid_s=[str(o.get("id")) for o in live if o.get("side") == "sell"],
               ords=[{"id": str(o.get("id")), "cl": str(o.get("cl") or ""), "side": str(o.get("side")), "px": float(o.get("px") or 0),
                      "sz": float(o.get("sz") or 0), "fill": float(o.get("acc") or 0), "t": float(o.get("cTime") or 0),
                      "type": str(o.get("type") or ""), "sym": sym} for o in live[:400]],
               ord_t=time.time(), demo=True)


def _demo_cfg_child(jp):'''),
    ('''        if path == "/api/deploy":
            return self._json(deploy(data))
        if path == "/api/deploy_dca":
            return self._json(deploy_dca(data))
        if path == "/api/deploy_rec":
            return self._json(deploy_rec(data))
        if path == "/api/deploy_va":
            return self._json(deploy_va(data))         # 💹 v3.34.0''',
     '''        if path in ("/api/deploy", "/api/deploy_dca", "/api/deploy_rec", "/api/deploy_va", "/api/deploy_step") and data.get("demo"):
            _dk = {"/api/deploy": str(data.get("g_type") or "grid"), "/api/deploy_dca": str(data.get("dca_type") or "dca"),
                   "/api/deploy_rec": str(data.get("rec_type") or "rec_buy"), "/api/deploy_va": "rec_va", "/api/deploy_step": "grid_step"}[path]
            return self._json(deploy_demo(_dk, data))    # 🧪 v3.36.46: الديمو بالمحرك الحقيقي (نفس إعداد النشر بالحرف)
        if path == "/api/deploy":
            return self._json(deploy(data))
        if path == "/api/deploy_dca":
            return self._json(deploy_dca(data))
        if path == "/api/deploy_rec":
            return self._json(deploy_rec(data))
        if path == "/api/deploy_va":
            return self._json(deploy_va(data))         # 💹 v3.34.0'''),
    ('''    if len(sys.argv) >= 5 and sys.argv[1] == "--holy-bt":      # 🧪 v3.36.0: عامل الاختبار التجريبي (عملية منفصلة بلا شبكة)
        sys.exit(_bt_child(sys.argv[2], sys.argv[3], sys.argv[4]))''',
     '''    if len(sys.argv) >= 5 and sys.argv[1] == "--holy-bt":      # 🧪 v3.36.0: عامل الاختبار التجريبي (عملية منفصلة بلا شبكة)
        sys.exit(_bt_child(sys.argv[2], sys.argv[3], sys.argv[4]))
    if len(sys.argv) >= 3 and sys.argv[1] == "--holy-demo-cfg":   # 🧪 v3.36.46: إعداد الديمو (دالة النشر نفسها · بلا شبكة)
        sys.exit(_demo_cfg_child(sys.argv[2]))'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
