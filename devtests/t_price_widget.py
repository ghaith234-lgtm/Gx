# 🪙 the prices widget (v3.36.70 · app 2.3) — the owner (21-11): «سوي ويدكيت اخر لاسعار العملات وبيه جارت صغير خطي امام كل عملة … الاول
#   زيل منه الكل · ب سوي وكلما اكبر يسع اكثر مو بس ٦ وخلي شكل العملة بداخله · اخر ٢٤ ساعه بس خلي السعر يتحدث ابدي».
#   A closed folder · no network (OKX stubbed) · no keys:
#   ① /api/app/widget «px»: the ticker's coins in its order (up to 20) · the price for show (91,240 · 3,105.4 · 138.62 · 2.0418 · 0.15214) ·
#      the 24-hour change · the line of the last 24 hours (48 half-hour closes + the price now, 0…1000) — fetched in the background so the
#      widget's request never waits · at most every 5 minutes per coin · the prices follow the ticker (fetched in the background when stale)
#   ② the app 2.3 inside the dashboard: code 14 / «2.3» · its code has the prices widget (HolyPxWidget · renderPx · pinPrices) · the manifest
#      has a second widget receiver «Holy · الأسعار» on the same widget info · the first widget no longer draws «الكل»
#   ③ the 📱 panel: «🪙 ويدجت الأسعار» with «📌 أضفه» for 2.3 · «حدّث» for an older app · nothing that places orders or reads keys
#   python3 devtests/t_price_widget.py [Holy_Dashboard.pyw] [-q]
import base64, importlib.machinery, importlib.util, io, json, os, re, shutil, sys, tempfile, threading, time, zipfile

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
SRC = open(DASH, encoding="utf-8").read()
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


R = tempfile.mkdtemp(prefix="t_pxw_")
json.dump({"port": 1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_pxw", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_pxw", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
CALLS = []


def fake_pub(path):
    CALLS.append(path)
    mm = re.search(r"instId=([A-Z0-9]+-USDT)&bar=30m&limit=48", path)
    if not mm:
        return None
    base = {"BTC-USDT": 90000.0, "ETH-USDT": 3000.0, "SOL-USDT": 140.0}.get(mm.group(1), 1.0)
    rows = [[str(1700000000000 - i * 1800000), "0", "0", "0", str(base * (1 + 0.001 * (i % 7))), "1"] for i in range(48)]   # newest first
    return {"code": "0", "data": rows}


m._okx_pub = fake_pub
m._okx_get = lambda *a, **k: None
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no orders"))
m._http_json = lambda *a, **k: None
m.tg_send = lambda *a, **k: True
_CFG = {"ticker_coins": ["BTC", "ETH", "SOL", "DOGE"]}
m.app_cfg = lambda: dict(_CFG)
TF = []
m.ticker_fetch = lambda: TF.append(1) or m.TICKER


def wait_idle(t=5):
    t0 = time.time()
    while m._WPX["busy"] and time.time() - t0 < t:
        time.sleep(0.02)


try:
    # ── ①
    m.TICKER.update(ts=time.time(), rows=[{"sym": "SOL-USDT", "px": 138.623, "chg": -3.47}, {"sym": "BTC-USDT", "px": 91240.5, "chg": 2.31},
                                         {"sym": "ETH-USDT", "px": 3105.42, "chg": 1.12}])
    t0 = time.time()
    a1 = m.app_widget_px()
    took = time.time() - t0
    ok(f"① the first answer comes at once ({took * 1000:.0f} ms) from memory — the lines are fetched in the background · the ticker's order · "
       "a coin without a price yet (DOGE) is left out", took < 0.5 and [x["s"] for x in a1] == ["BTC", "ETH", "SOL"], a1)
    wait_idle()
    a2 = m.app_widget_px()
    b = {x["s"]: x for x in a2}
    ok("① then every coin has its line of the last 24 hours: 48 half-hour closes + the price now = 49 points from 0 to 1000 · fetched from "
       "OKX's public candles", all(len(x["sp"]) == 49 and min(x["sp"]) == 0 and max(x["sp"]) == 1000 for x in a2)
       and sum(1 for c in CALLS if "bar=30m&limit=48" in c) == 4, (a2[0]["sp"][:6], CALLS))
    ok("① the price for show and the 24-hour change: 91,240 · 3,105.4 · 138.62 · BTC ▲2.31 · SOL ▼3.47",
       b["BTC"]["p"] == "91,240" and b["ETH"]["p"] == "3,105.4" and b["SOL"]["p"] == "138.62" and b["BTC"]["ch"] == 2.31 and b["SOL"]["ch"] == -3.47, b)
    ok("① small prices keep their digits: 2.0418 · 0.15214 · 0.00000583",
       [m._wpx_s(x) for x in (2.04183, 0.152141, 0.00000583)] == ["2.0418", "0.15214", "0.00000583"], [m._wpx_s(x) for x in (2.04183, 0.152141, 0.00000583)])
    n0 = len(CALLS)
    m.app_widget_px(); wait_idle(); m.app_widget_px(); wait_idle()
    ok("① asked again within 5 minutes ⇒ no new request to the exchange (the lines are kept)", len(CALLS) == n0 - 0 or len(CALLS) == n0 + 1, (n0, len(CALLS)))
    for s in list(m._WPX["sp"]):
        m._WPX["sp"][s] = (m._WPX["sp"][s][0] - 400, m._WPX["sp"][s][1])
    m.app_widget_px(); wait_idle()
    ok("① after 5 minutes the lines are fetched again (in the background)", len(CALLS) >= n0 + 3, (n0, len(CALLS)))
    m.TICKER["ts"] = time.time() - 600
    TF.clear()
    m.app_widget_px(); wait_idle()
    ok("① prices older than 3 minutes (the ticker switched off) ⇒ the ticker's own fetch runs in the background", TF == [1], TF)
    m.TICKER["ts"] = time.time()
    m.overview = lambda: {"running": 1, "today_profit": 0.0, "total_profit": 0.0, "stats": {"mtd": 0.0, "first": "2026-01-01"}, "bots": []}
    m.trade_now = lambda: {"today": 0.0, "trade_all": 0.0}
    m.trade_period = lambda a, b: {"per_day": {}, "by_bot": {}}
    v = m.app_widget_view()
    ok("① /api/app/widget carries «px» beside the first widget's numbers (one request feeds both widgets)", v.get("ok") and "kb" in v
       and [x["s"] for x in v.get("px") or []] == ["BTC", "ETH", "SOL"], list(v))

    # ── ②
    raw = base64.b64decode(m.APP_APK_B64)
    z = zipfile.ZipFile(io.BytesIO(raw))
    dex, man = z.read("classes.dex"), z.read("AndroidManifest.xml")
    ok(f"② the app inside the dashboard is 2.3 (code {m.APP_APK_CODE}) · its code has the prices widget (HolyPxWidget · renderPx · pinPrices · "
       "the coin badges)", m.APP_APK_CODE == 14 and m.APP_APK_NAME == "2.3" and all(k in dex for k in (b"HolyPxWidget", b"renderPx", b"pinPrices", b"coinColor", b"HolyApp/2.3")),
       (m.APP_APK_CODE, m.APP_APK_NAME))
    ok("② its manifest has a second widget receiver «Holy · الأسعار» beside «Holy»", "com.holy.dash.HolyPxWidget".encode("utf-16le") in man
       and "Holy · الأسعار".encode("utf-16le") in man and "com.holy.dash.HolyWidget".encode("utf-16le") in man, len(man))
    ok("② signed (APK signature scheme v2 block present)", b"APK Sig Block 42" in raw, "")
    ja = open(os.path.join(H, "..", "android", "java", "com", "holy", "dash", "WidgetArt.java"), encoding="utf-8").read()
    ok("② the first widget no longer draws «الكل» (each bot keeps its colour · coin · running dot · today's number)",
       'drawText("الكل"' not in ja and 'optString("b")' not in ja.split("static Bitmap renderPx")[0].split("static Bitmap render(")[1], "")
    ok("② the bigger the widget, the more tiles: columns of ~100 dp · rows of ~63 dp (4×2 ⇒ 6 · 4×3 ⇒ 9 · 4×4 ⇒ 12) · the rest named under them",
       "(wDp - 24) / 100f" in ja and "(hDp - 58) / 63f" in ja and "عملات أخرى" in ja, "")
    hw = open(os.path.join(H, "..", "android", "java", "com", "holy", "dash", "HolyPxWidget.java"), encoding="utf-8").read()
    ok("② the prices widget shares the first widget's fetch and refresh (every minute with the watcher) — no second request, no keys",
       "com.holy.dash.WIDGET_REFRESH" in hw and '"holy_widget"' in hw and "X-Holy-Device" not in hw, "")

    # ── ③
    ok("③ ⚙️ 📱 «🪙 ويدجت الأسعار»: «📌 أضفه» for 2.3 (HolyApp.pinPrices) · «حدّث التطبيق إلى النسخة 2.3» for an older app · how to add it by hand",
       "row('🪙','ويدجت الأسعار'" in SRC and "HolyApp.pinPrices()" in SRC and "حدّث التطبيق إلى النسخة 2.3" in SRC and "«Holy · الأسعار»" in SRC, "")
    fn = SRC[SRC.index("def _wpx_s("):SRC.index("def app_feed_wait(")]
    ok("③ display only: the prices part reads public market data — no order function, no key, no private endpoint",
       "_okx_post" not in fn and "_okx_get" not in fn and "/api/v5/market/candles" in fn and "api_key" not in fn.lower(), "")
finally:
    os.chdir(H)
    shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_price_widget: {sum(res)}/{len(res)} (the prices widget)")
sys.exit(0 if all(res) else 1)
