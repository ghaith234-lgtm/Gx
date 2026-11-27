# p153 — v3.36.79 🔀 «شبكة عملتين» · ⑧ the demo (the owner 27-11: «لعد خليه بدون نشر على المنصه ، ابدي»)
#   · the REAL engine (main.py = main_pair.py) on a paper exchange with TWO instruments (OTHER-USDT · MAIN-USDT) — each leg is the
#     closed-box paper exchange itself (`_BtEx` — the same source, not a copy, not changed) and the two share ONE wallet (one balance ·
#     one frozen · one fee book) · an instId router in front (the engine names the instrument in every call) · the live OKX price of both
#     legs (public · no keys) · the tests feed a local price file instead (HOLY_DEMO_FEED · no network)
#   · the deploy = the real calculator to the letter (`pair_plan`) · the paper wallet = the two amounts of the form (the main coin for the
#     buys below · the second coin for the sells above) · no keys · one demo per pair · outside every total and every notice (as every demo)
#   · the form: «🧪 ديمو» — no OKX wallet needed · ♻️ the archive re-deploys a demo as a demo
#   python3 devtests/step/patches/p153_pair_demo.py Holy_Dashboard.pyw
import os, sys

TAIL = '''

_DEMO_PAIR_TAIL = """


# ═══════════ 🔀 «شبكة عملتين»: منصة وهمية برجلين (OTHER-USDT · MAIN-USDT) · محفظة واحدة · سعر OKX الحي للرجلين ═══════════
MAKER, TAKER, SLIP = 0.0008, 0.001, 0.0003
FEED = os.environ.get("HOLY_DEMO_FEED") or ""          # the tests: a local price file {instId: {last · tickSz · lotSz · minSz}} (no network)


def _pub(path):
    if FEED:
        try:
            f = json.load(open(FEED, encoding="utf-8"))
        except Exception:
            f = {}
        inst = ({k: v[0] for k, v in _bt_up.parse_qs(_bt_up.urlparse(path).query).items()}).get("instId") or ""
        g = f.get(inst) or {}
        if "/market/ticker" in path:
            p = repr(float(g.get("last") or 0))
            return {"code": "0", "data": [{"instId": inst, "last": p, "bidPx": p, "askPx": p, "ts": str(int(time.time() * 1000))}]}
        if "/public/instruments" in path:
            return {"code": "0", "data": [{k: str(g.get(k) or "") for k in ("tickSz", "lotSz", "minSz")}]}
        return {"code": "0", "data": []}
    rq = _ur.Request("https://www.okx.com" + path, headers={"User-Agent": "Holy-demo"})
    with _ur.urlopen(rq, timeout=8) as r:
        return json.loads(r.read().decode("utf-8"))


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


class _PairPaper:                                         # رجلان كلٌّ بمنصته الوهمية (_BtEx نفسه) — والرصيد والمحجوز والعمولات مشتركة = محفظة واحدة
    KEEP = 3000

    def __init__(self, insts, px, spec, w, path):
        self.path, self.w0 = path, w
        self.bal = {k: float(v) for k, v in (w.get("bal") or {}).items()}
        self.frz = {k: float(v) for k, v in (w.get("frz") or {}).items()}
        self.fees = {k: float(v) for k, v in (w.get("fees") or {}).items()}
        self.lk = threading.RLock()
        self.clock = _Clock()
        self.ex = {}
        O, C, N = w.get("orders") or {}, w.get("by_cl") or {}, w.get("next_id") or {}
        for i, inst in enumerate(insts):
            s = spec[inst]
            e = _BtEx(inst, px[inst], 0.0, 0.0, float(s["tickSz"]), float(s["lotSz"]), float(s["minSz"]), MAKER, TAKER, SLIP)
            for c in inst.split("-"):
                self.bal.setdefault(c, 0.0)
                self.frz.setdefault(c, 0.0)
                self.fees.setdefault(c, 0.0)
            e.bal, e.frz, e.fees, e.lk, e.clock = self.bal, self.frz, self.fees, self.lk, self.clock
            e.orders, e.by_cl = dict(O.get(inst) or {}), dict(C.get(inst) or {})
            e.ids = _bt_it.count(max([int(k) for k in e.orders if str(k).isdigit()] + [int(N.get(inst) or (100000 + 400000 * i))]) + 1)
            self.ex[inst] = e
        self.saved = None

    def sig(self):
        return (tuple(sorted((k, round(v, 12)) for k, v in self.bal.items())),
                tuple(max([int(k) for k in e.orders if str(k).isdigit()] + [0]) for e in self.ex.values()))

    def save(self, force=False):
        with self.lk:
            sg = self.sig()
            if sg == self.saved and not force:
                return
            for e in self.ex.values():
                closed = sorted((o for o in e.orders.values() if o.get("state") != "live"), key=lambda o: float(o.get("cTime") or 0))
                for o in closed[:max(0, len(closed) - self.KEEP)]:
                    e.orders.pop(o["id"], None)
                    if o.get("cl"):
                        e.by_cl.pop(o["cl"], None)
                del e.rejects[:-200]
            nx0 = self.w0.get("next_id") or {}
            w = {"v": 2, "pair": True, "sym": self.w0.get("sym"), "insts": list(self.ex), "px": {k: e.p for k, e in self.ex.items()},
                 "ts": time.time(), "bal": dict(self.bal), "frz": dict(self.frz), "fees": dict(self.fees),
                 "orders": {k: e.orders for k, e in self.ex.items()}, "by_cl": {k: e.by_cl for k, e in self.ex.items()},
                 "fills": {k: [list(x) for x in e.fills[-300:]] for k, e in self.ex.items()},
                 "next_id": {k: max([int(x) for x in e.orders if str(x).isdigit()] + [int(nx0.get(k) or 0)]) for k, e in self.ex.items()},
                 "start": self.w0.get("start") or {}, "start_px": self.w0.get("start_px") or {}, "spec": self.w0.get("spec") or {}}
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(w, f)
            os.replace(tmp, self.path)
            self.saved = sg


def _nope(sc="51001", msg="Instrument ID does not exist"):
    return {"code": "1", "msg": "", "data": [{"sCode": sc, "sMsg": msg, "ordId": "", "clOrdId": ""}]}


def _pair_route(P, method, url, body=None):
    u = _bt_up.urlparse(url)
    q = {k: v[0] for k, v in _bt_up.parse_qs(u.query).items()}
    p = u.path
    if method == "GET":
        e = P.ex.get(q.get("instId") or "")
        if p == "/api/v5/trade/order":
            return e.query(q.get("ordId"), q.get("clOrdId")) if e else {"code": "51001", "msg": "Instrument ID does not exist", "data": []}
        if p == "/api/v5/trade/orders-pending":
            return {"code": "0", "msg": "", "data": [o for x in ([e] if e else list(P.ex.values())) for o in x.pending()["data"]]}
        if p == "/api/v5/account/balance":
            return next(iter(P.ex.values())).balance(q.get("ccy"))
        if p == "/api/v5/market/ticker" and e:
            return e.ticker()
        if p == "/api/v5/public/instruments" and e:
            return e.instrument()
        if p.startswith("/api/v5/market/") or p.startswith("/api/v5/public/"):
            return _pub(p + ("?" + u.query if u.query else ""))
    else:
        b = json.loads(body or "{}") if isinstance(body, (str, bytes)) else (body or {})
        e = P.ex.get(b.get("instId") or "")
        if p == "/api/v5/trade/order":
            return e.place(b.get("side"), b.get("ordType"), b.get("sz"), b.get("px"), b.get("clOrdId") or "", b.get("tgtCcy")) if e else _nope()
        if p == "/api/v5/trade/cancel-order":
            return e.cancel(b.get("ordId"), b.get("clOrdId")) if e else _nope()
    raise ConnectionError("demo: no network (" + method + " " + p + ")")


def _pair_fakes(P):
    class TradeAPI:
        def __init__(self, *a, **k):
            pass

        def place_order(self, instId=None, tdMode=None, side=None, ordType=None, sz=None, px=None, clOrdId="", tgtCcy=None, **k):
            e = P.ex.get(instId or "")
            return e.place(side, ordType, sz, px, clOrdId or "", tgtCcy) if e else _nope()

        def get_order(self, instId=None, ordId=None, clOrdId=None, **k):
            e = P.ex.get(instId or "")
            return e.query(ordId, clOrdId) if e else {"code": "51001", "msg": "Instrument ID does not exist", "data": []}

        def get_order_list(self, instId=None, **k):
            return _pair_route(P, "GET", "https://www.okx.com/api/v5/trade/orders-pending" + ("?instId=" + instId if instId else ""))

        def cancel_order(self, instId=None, ordId=None, clOrdId=None, **k):
            e = P.ex.get(instId or "")
            return e.cancel(ordId, clOrdId) if e else _nope()

    class MarketAPI:
        def __init__(self, *a, **k):
            pass

        def get_ticker(self, instId=None, **k):
            e = P.ex.get(instId or "")
            return e.ticker() if e else _pub("/api/v5/market/ticker?instId=" + str(instId))

        def get_instruments(self, instType=None, instId=None, **k):
            e = P.ex.get(instId or "")
            return e.instrument() if e else _pub("/api/v5/public/instruments?instType=SPOT&instId=" + str(instId))

    class PublicAPI(MarketAPI):
        pass

    okx = _bt_mod("okx")
    okx.Trade = _bt_mod("okx.Trade", TradeAPI=TradeAPI)
    okx.MarketData = _bt_mod("okx.MarketData", MarketAPI=MarketAPI)
    okx.PublicData = _bt_mod("okx.PublicData", PublicAPI=PublicAPI)

    def _get(url, headers=None, timeout=None, params=None, **k):
        if params:
            url = url + ("&" if "?" in url else "?") + _bt_up.urlencode(params)
        return _BtResp(_pair_route(P, "GET", url))

    def _post(url, headers=None, data=None, timeout=None, **k):
        return _BtResp(_pair_route(P, "POST", url, data if data is not None else k.get("json")))

    requests = _bt_mod("requests", get=_get, post=_post,
                       exceptions=_bt_mod("requests.exceptions", RequestException=Exception, Timeout=TimeoutError, ConnectionError=ConnectionError))

    def _urlopen(url, data=None, timeout=None, **k):
        url = getattr(url, "full_url", url)
        return _BtResp(_pair_route(P, "GET" if data is None else "POST", url, data))

    class _Req:
        def __init__(self, url, data=None, headers=None, method=None, **k):
            self.full_url, self.data = url, data

    urllib_ = _bt_mod("urllib", parse=_bt_up)
    urllib_.request = _bt_mod("urllib.request", urlopen=_urlopen, Request=_Req)
    urllib_.error = _bt_mod("urllib.error", URLError=OSError, HTTPError=OSError)
    return {"okx": okx, "okx.Trade": okx.Trade, "okx.MarketData": okx.MarketData, "okx.PublicData": okx.PublicData, "requests": requests,
            "urllib": urllib_, "urllib.request": urllib_.request, "urllib.error": urllib_.error}


def _feed_loop(P):
    while True:
        for inst, e in list(P.ex.items()):
            try:
                d = _pub("/api/v5/market/ticker?instId=" + inst)
                p = float(((d.get("data") or [{}])[0] or {}).get("last") or 0)
                if p > 0:
                    e.set_price(p)
            except Exception:
                pass
        try:
            P.save()
        except Exception:
            pass
        time.sleep(1.0 if FEED else 2.0)


def _main():
    script = sys.argv[1]
    folder = os.getcwd()
    cfgp = next((n for n in os.listdir(folder) if n.startswith("config_") and n.endswith(".json")), None)
    cfg = json.load(open(os.path.join(folder, cfgp), encoding="utf-8"))
    sym = cfg["symbol"]
    oth, mn = sym.split("-")
    br = str(cfg.get("bridge") or "USDT")
    insts = [oth + "-" + br, mn + "-" + br]
    wp = os.path.join(folder, "demo_wallet.json")
    try:
        w = json.load(open(wp, encoding="utf-8"))
    except Exception:
        w = {"bal": {}, "start": {}}
    spec, px = dict(w.get("spec") or {}), {}
    while True:
        try:
            for i in insts:
                if not (spec.get(i) or {}).get("tickSz"):
                    d = (_pub("/api/v5/public/instruments?instType=SPOT&instId=" + i).get("data") or [{}])[0]
                    spec[i] = {k: float(d.get(k) or 0) for k in ("tickSz", "lotSz", "minSz")}
                px[i] = float(((_pub("/api/v5/market/ticker?instId=" + i).get("data") or [{}])[0] or {}).get("last") or 0)
        except Exception:
            pass
        if all((spec.get(i) or {}).get("tickSz") and (spec.get(i) or {}).get("lotSz") and px.get(i, 0) > 0 for i in insts):
            break
        print("🧪 demo: waiting for the OKX prices…", flush=True)
        time.sleep(5)
    w["spec"] = spec
    P = _PairPaper(insts, px, spec, w, wp)
    P.save(force=True)
    threading.Thread(target=_feed_loop, args=(P,), daemon=True).start()
    mods = _pair_fakes(P)
    real_import = _bt_bi.__import__
    bi = dict(_bt_bi.__dict__)

    def _imp(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0:
            if name in mods:
                return mods[name] if (fromlist or "." not in name) else mods[name.split(".")[0]]
            top = name.split(".")[0]
            if top in mods and not fromlist:
                return mods[top]
        return real_import(name, globals, locals, fromlist, level)

    bi["__import__"] = _imp
    print(f"🧪 demo · {oth}/{mn} · the real engine ({script}) on a two-leg paper exchange · live prices {px}", flush=True)
    sys.argv = [script]
    g = {"__name__": "__main__", "__file__": os.path.join(folder, script), "__builtins__": bi}
    try:
        exec(compile(open(os.path.join(folder, script), encoding="utf-8").read(), os.path.join(folder, script), "exec"), g)
    finally:
        try:
            P.save(force=True)
        except Exception:
            pass


if __name__ == "__main__":
    _main()
"""
'''

R = [
    # ── the runner: the pair tail beside the single one (the same closed-box pieces) ─────────────────────────────────────────
    (r'''def demo_runner_src():
    """🧪 مصدر holy_demo.py: منصة الصندوق المغلق نفسها (_BtEx · _bt_route · _bt_fakes — نفس المصدر، مو نسخة) + المحفظة والسعر الحي"""''',
     r'''def demo_runner_src(pair=False):
    """🧪 مصدر holy_demo.py: منصة الصندوق المغلق نفسها (_BtEx · _bt_route · _bt_fakes — نفس المصدر، مو نسخة) + المحفظة والسعر الحي ·
    🔀 v3.36.79 pair=True: الأجزاء نفسها + رجلان بمحفظة واحدة («شبكة عملتين»)"""'''),
    (r'''        _DEMO_SRC["s"] = _DEMO_HEAD + "\n\n\n".join(got[k] for k in want) + _DEMO_TAIL
    return _DEMO_SRC["s"]''', r'''        _DEMO_SRC["body"] = _DEMO_HEAD + "\n\n\n".join(got[k] for k in want)
        _DEMO_SRC["s"] = _DEMO_SRC["body"] + _DEMO_TAIL
    return (_DEMO_SRC["body"] + _DEMO_PAIR_TAIL) if pair else _DEMO_SRC["s"]'''),
    ('''def _demo_write_runner(d):
    p = os.path.join(d, DEMO_RUNNER)
    src = demo_runner_src()''', '''def _demo_write_runner(d, pair=False):
    p = os.path.join(d, DEMO_RUNNER)
    src = demo_runner_src(pair)'''),
    ('''            _demo_write_runner(b["dir"])                  # 🧪 يُكتب من جديد بكل إقلاع (نفس منصة الصندوق المغلق)''',
     '''            _demo_write_runner(b["dir"], pair=str(b["cfg"].get("bot_type") or "") == "grid_pair")   # 🧪 يُكتب من جديد بكل إقلاع · 🔀 برجلين'''),
    ('''    w = demo_wallet(b)
    if not w:
        return
    sym = b["symbol"]; base = sym.split("-")[0]''', '''    w = demo_wallet(b)
    if not w or w.get("pair"):                       # 🔀 v3.36.79: محفظة «شبكة عملتين» برجلين — بطاقتها تقرأ دفاتر محركها
        return
    sym = b["symbol"]; base = sym.split("-")[0]'''),
    # ── the deploy ──────────────────────────────────────────────────────────────────────────────────────────────────────────
    ('''    if data.get("demo"):
        return {"ok": False, "msg": "🧪 الديمو لهذا البوت غير متاح بعد"}
    P = pair_plan(data)''', '''    if data.get("demo"):
        return deploy_demo_pair(data)                  # 🧪 v3.36.79: منصة وهمية برجلين بسعر OKX الحي
    P = pair_plan(data)'''),
    ('''def deploy_pair(data):''', '''def deploy_demo_pair(data):
    """🧪 v3.36.79 «شبكة عملتين» ديمو: المحرك الحقيقي نفسه على منصة وهمية برجلين (الثانية-USDT · الرئيسية-USDT) بسعر OKX الحي ·
    الإعداد = حاسبة النشر الحقيقي بالحرف · المحفظة الوهمية = كميتا النموذج · بلا مفاتيح · ديمو واحد لكل زوج · خارج كل المجاميع والإشعارات"""
    if getattr(sys, "frozen", False):
        return {"ok": False, "msg": "الديمو يحتاج نسخة بايثون من اللوحة"}
    P = pair_plan(data)
    if not P.get("ok"):
        return P
    if P["err"]:
        return {"ok": False, "msg": "⛔ " + P["err"][0]}
    a = P["a"]
    for b0 in bot_dirs().values():
        try:
            c0 = b0.get("cfg") or {}
            if c0.get("is_demo") and str(c0.get("bot_type") or "") == "grid_pair" and str(b0.get("symbol") or "").upper() == a["sym"].upper():
                return {"ok": False, "msg": f"⛔ يوجد ديمو «شبكة عملتين» على {a['other']}/{a['main']} — واحد لكل زوج · احذفه أولاً"}
        except Exception:
            continue
    try:
        am, ao = max(float(data.get("main_amount") or 0), P["main_need"]), max(float(data.get("other_amount") or 0), P["other_need"])
    except Exception:
        return {"ok": False, "msg": "تأكد من الأرقام (الكميات)"}
    lo_, lm_ = f"{a['other']}-USDT", f"{a['main']}-USDT"
    sp = {}
    for inst, s in ((lo_, P["spec"].get("other") or {}), (lm_, P["spec"].get("main") or {})):
        if float(s.get("tickSz") or 0) > 0 and float(s.get("lotSz") or 0) > 0:
            sp[inst] = {k: float(s.get(k) or 0) for k in ("tickSz", "lotSz", "minSz")}     # وإلا يجلبها المشغّل من OKX (عام بلا مفاتيح)
    cfg = {"api_key": "", "secret_key": "", "passphrase": "", "symbol": a["sym"], "bot_type": "grid_pair", "bridge": "USDT", "main_value": a["mv"],
           "grid_percentage": a["g"], "down_levels": int(P["dn"]), "up_levels": int(P["up"]), "profit_to": a["pt"], "forced_base_ratio": float(P["r0"]),
           "fee_rate": PAIR_FEE, "slip_cap": PAIR_CAP, "slip_cap_b": PAIR_CAP_B, "is_demo": True, "auto_restart": bool(data.get("auto", True))}
    folder = _new_bot_folder("demo_pair_" + a["other"].lower())
    full = os.path.join(ROOT, folder)
    os.makedirs(full, exist_ok=True)
    save_json_atomic(os.path.join(full, f"config_{a['sym']}.json"), cfg)
    eng_src, eng_script, _ = engine_for(cfg)
    with open(os.path.join(full, eng_script), "w", encoding="utf-8") as fh:
        fh.write(eng_src)                                  # 🧬 المحرك الحقيقي نفسه
    start = {a["main"]: round(am, 10), a["other"]: round(ao, 12), "USDT": 0.0}
    save_json_atomic(os.path.join(full, DEMO_WALLET), {"v": 2, "pair": True, "sym": a["sym"], "insts": [lo_, lm_], "bal": dict(start), "start": dict(start),
                                                        "start_px": {lo_: P["px"]["other"], lm_: P["px"]["main"]}, "spec": sp, "orders": {}, "by_cl": {},
                                                        "ts": time.time()})
    b = {"dir": full, "cfg_path": os.path.join(full, f"config_{a['sym']}.json"), "cfg": cfg, "symbol": a["sym"]}
    ok, msg = launch(b)
    return {"ok": ok, "dir": folder, "msg": (f"🧪 انطلق ديمو «شبكة عملتين» — {a['other']}/{a['main']} · بالمحرك الحقيقي على منصة وهمية برجلين بسعر OKX الحي · "
                                             f"المحفظة الوهمية {am:g} {a['main']}" + (f" + {ao:g} {a['other']}" if ao > 0 else "")) if ok else msg}


def deploy_pair(data):'''),
    # ── the form ────────────────────────────────────────────────────────────────────────────────────────────────────────────
    ('''  <div class="cklist" style="margin-top:10px"><label class="ck"><input type="checkbox" id="pa_auto" checked>🤖 يشمله الحارس</label></div>''',
     '''  <div class="cklist" style="margin-top:10px"><label class="ck"><input type="checkbox" id="pa_auto" checked>🤖 يشمله الحارس</label>
    <label class="ck" title="المحرك الحقيقي نفسه على منصة وهمية برجلين بسعر OKX الحي — لا أوامر حقيقية ولا يدخل في أي مجموع"><input type="checkbox" id="pa_demo" ${pre.demo?'checked':''} onchange="paDemo()">🧪 ديمو</label></div>
  <div class="sthelp" id="pa_dnote" style="display:none">🧪 الديمو: المحفظة الوهمية = الكميتان أعلاه (الرئيسية للشراءات تحت · الثانية للبيعات فوق) — لا حاجة إلى محفظة OKX، ولا إشعارات، ولا يدخل في أي مجموع.</div>'''),
    ('''    other_amount:g('pa_ao'),forced_ratio:g('pa_r0'),profit_to:g('pa_pt')||'main',wallet:g('pa_wallet'),auto:!!($('#pa_auto')||{}).checked}}''',
     '''    other_amount:g('pa_ao'),forced_ratio:g('pa_r0'),profit_to:g('pa_pt')||'main',wallet:g('pa_wallet'),auto:!!($('#pa_auto')||{}).checked,
    demo:!!($('#pa_demo')||{}).checked}}
function paDemo(){const on=!!($('#pa_demo')||{}).checked,n=$('#pa_dnote'),w=$('#pa_wallet');if(n)n.style.display=on?'':'none';if(w)w.disabled=on}   // 🧪 v3.36.79'''),
    ("""  const pt=$('#pa_pt');if(pt)pt.value=['main','other','half'].includes(pre.profit_to)?pre.profit_to:'main';""",
     """  const pt=$('#pa_pt');if(pt)pt.value=['main','other','half'].includes(pre.profit_to)?pre.profit_to:'main';paDemo();"""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    anc = '''\n\ndef demo_runner_src(pair=False):'''
    if s.count(anc) != 1 or "_DEMO_PAIR_TAIL = " in s:
        print("❌ the runner's anchor is not unique (or the pair tail is already there) — nothing written"); sys.exit(1)
    s = s.replace(anc, TAIL + anc)
    compile(s, p, "exec")
    try:
        from pyflakes.api import check as _pf
        from pyflakes.reporter import Reporter as _Rp
        import io as _io
        _o = _io.StringIO()
        _pf(s, p, _Rp(_o, _o))
        und = [ln for ln in _o.getvalue().splitlines() if "undefined name" in ln]
        if und:
            print("❌ undefined:", und[:5]); sys.exit(1)
    except ImportError:
        pass
    ns = {}
    exec(compile("_DEMO_PAIR_TAIL = " + s.split("_DEMO_PAIR_TAIL = ", 1)[1].split('\n"""\n', 1)[0] + '\n"""\n', "tail", "exec"), ns)
    compile(ns["_DEMO_PAIR_TAIL"], "holy_demo_pair_tail", "exec")                     # the runner's own code compiles
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements + the two-leg runner · 🧪 «شبكة عملتين» demo on the real engine · {p}")
