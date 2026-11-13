# 📱 the Android app 2.0 (v3.36.32) — the owner (13-11): «اتسويه مثل الكروت وافضل كرت b واتضيف عليه ربح البارحه واخر اسبوع واخر
#   شهر · لا خلي اخر اسبوع واخر شهر · خلي لون الويدجيت مثل لون البنفسجي الي بالواجهة». A closed folder · no network · fake keys:
#   ① /api/app/widget «kb» = six numbers of trading profit (n + r per day): today · yesterday · the last 7 days · the last 30 days ·
#      this month · total — one ledger request that covers both the last 30 days and the month's first day (checked on the 31st, the
#      3rd and mid-month) · each bot carries its type «t» · the 1.9 «k» unchanged · a ledger error ⇒ «—», never a crash
#   ② the app itself (the embedded APK): version 2.0 / code 11 in the manifest · the widget starts 4×3 (180 dp) · its code has the new
#      widget (WidgetArt) · signed (APK signature scheme v2) · the same file /app/holy.apk serves and /api/app/info describes
#   ③ /api/app/info: a 1.x app (its own «HolyApp/1.9» or the WebView's «… HolyApp/1.9») is offered code 0 — never a file it cannot
#      install over itself — while 2.0 and a browser see code 11 · «rekey» 11 · /api/app/widget answers a linked phone with «kb»
#   ④ the page (ui_app20.js, a real browser): inside a 1.x app the 📱 panel opens by itself once (not again within two days) with the
#      move to 2.0: «⬇️ احفظها» saves the very APK as «Holy-2.0.apk» through the app · the four steps · why it is manual · the widget
#      row names the six numbers — inside 2.0 nothing of that, «آخر نسخة» · in a browser: «remove 1.x first»
#   python3 devtests/t_app20.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import hashlib, importlib.machinery, importlib.util, io, json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request, zipfile
from datetime import datetime as _dt, timedelta

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="t_app20_")
P1 = port()
json.dump({"port": P1}, open(os.path.join(R, "dashboard_config.json"), "w"))
json.dump({"wallets": []}, open(os.path.join(R, "monitor_config.json"), "w"))
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
cwd0 = os.getcwd()
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_app20", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_app20", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0
m._okx_pub = lambda p: None
m._okx_get = lambda *a, **k: None
m.tg_send = lambda *a, **k: True
d = None
try:
    # ── ① the six numbers
    m.overview = lambda: {"running": 2, "today_profit": 0.1, "total_profit": 5.0, "stats": {"mtd": 3.3, "first": "2026-01-01"},
                          "bots": [{"dir": "grid_a", "bot_type": "grid", "symbol": "XRP-USDT", "alive": True, "profit": 1.0, "today": 0.1},
                                   {"dir": "step_b", "bot_type": "grid_step", "symbol": "SOL-USDT", "alive": True, "profit": 0.0, "today": 0.0},
                                   {"dir": "rv_c", "bot_type": "rec_va", "symbol": "BTC-USDT", "alive": False, "rec": {"profit": 2.0, "today": 0.0}}]}
    m.trade_now = lambda: {"today": 999.0, "trade_all": 1234.5}

    def day_value(s):                       # a different, recognisable amount every day: n = day of the year / 100 · r = 0.001 on odd days
        t = _dt.strptime(s, "%Y-%m-%d")
        return {"n": t.timetuple().tm_yday / 100.0, "r": 0.001 if t.day % 2 else 0.0, "rel": 0.0, "c": 1}

    CALLS = []

    def fake_tp(a, b):
        CALLS.append((a, b))
        t, e, pd = _dt.strptime(a, "%Y-%m-%d"), _dt.strptime(b, "%Y-%m-%d"), {}
        while t <= e:
            pd[t.strftime("%Y-%m-%d")] = day_value(t.strftime("%Y-%m-%d")); t += timedelta(days=1)
        return {"days": sorted(pd), "per_day": pd, "by_bot": {}, "tot": {}}

    m.trade_period = fake_tp
    real_dt = m.datetime
    for NOW in (_dt(2026, 10, 31, 22, 15), _dt(2026, 11, 3, 9, 0), _dt(2026, 11, 13, 6, 30)):
        class FixedDT(real_dt):
            @classmethod
            def now(cls, tz=None):
                return NOW
        m.datetime = FixedDT
        CALLS.clear()
        W = m.app_widget_view()
        days = lambda n: [(NOW - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(n)]
        tot = lambda ds: sum(day_value(x)["n"] + day_value(x)["r"] for x in ds)
        m1 = NOW.strftime("%Y-%m-01")
        month = [x for x in days(40) if x >= m1]
        want = [["اليوم"] + list(m._wd_n(tot(days(1)), "$")), ["أمس"] + list(m._wd_n(tot([days(2)[1]]), "$")),
                ["آخر 7 أيام"] + list(m._wd_n(tot(days(7)), "$")), ["آخر 30 يوماً"] + list(m._wd_n(tot(days(30)), "$")),
                ["هذا الشهر"] + list(m._wd_n(tot(month), "$")), ["الإجمالي"] + list(m._wd_n(1234.5, "$", False))]
        wide = [c for c in CALLS if c == (min(m1, days(30)[-1]), NOW.strftime("%Y-%m-%d"))]
        ok(f"① {NOW:%Y-%m-%d}: «kb» = today {want[0][1]} · yesterday {want[1][1]} · 7 days {want[2][1]} · 30 days {want[3][1]} · "
           f"this month {want[4][1]} ({len(month)} days) · total {want[5][1]} — every number = the ledger's own days (n + r)",
           W.get("kb") == want, (W.get("kb"), want))
        ok(f"① {NOW:%Y-%m-%d}: one ledger request covers the last 30 days and the 1st of the month ({wide[:1]})", len(wide) == 1, CALLS)
    m.datetime = real_dt
    rows = {x["s"]: x for x in W["bots"]}
    ok("① each bot carries its type «t» (its colour on the widget): grid · grid_step · rec_va",
       rows["XRP"].get("t") == "grid" and rows["SOL"].get("t") == "grid_step" and rows["BTC"].get("t") == "rec_va", rows)
    ok("① the 1.9 «k» unchanged (ربح اليوم · هذا الشهر · الإجمالي) — the 1.9 app keeps working",
       [x[0] for x in W["k"]] == ["ربح اليوم", "هذا الشهر", "الإجمالي"] and W["k"][0][1] == "+999.00$" and W["k"][1][1] == "+3.3000$", W["k"])
    m.trade_period = lambda a, b: (_ for _ in ()).throw(RuntimeError("ledger broken"))
    W2 = m._safe(m.app_widget_view, default=None)
    ok("① the ledger failing ⇒ «—» in the five day boxes · the total still from trade_now · no crash",
       W2 and [x[1] for x in W2["kb"][:5]] == ["—"] * 5 and W2["kb"][5][1] == m._wd_n(1234.5, "$", False)[0], W2 and W2.get("kb"))

    # ── ② the app itself
    raw = __import__("base64").b64decode(m.APP_APK_B64)
    sys.path.insert(0, os.path.join(H, "..", "android"))
    import build as B                       # android/build.py: its binary-XML reader
    z = zipfile.ZipFile(io.BytesIO(raw))
    man = B.axml_read(z.read("AndroidManifest.xml"), "manifest")
    info = B.axml_read(z.read("res/xml/holy_widget_info.xml"), "appwidget-provider")
    NC, NV = m.APP_APK_CODE, m.APP_APK_NAME           # v3.36.38: the embedded version (2.1 · 12 …) — every version from 2.0 on (rekey 11)
    ok(f"② the embedded app: versionCode {NC} · versionName «{NV}» = APP_APK_CODE / APP_APK_NAME (≥ 2.0 · the new key since 11)",
       man[B.A_VERSION_CODE][1] == NC >= 11 and man[B.A_VERSION_NAME][2] == NV and m.APP_APK_REKEY == 11, man)
    ok("② the widget starts 4×3: minHeight 180 dp · targetCellHeight 3 (was 110 dp · 2)",
       info[B.A_MIN_HEIGHT][1] >> 8 == 180 and info[B.A_TARGET_CELL_H][1] == 3, info)
    dex = z.read("classes.dex")
    ok("② its code has the new widget (WidgetArt reading the six numbers «kb»)",
       b"Lcom/holy/dash/WidgetArt;" in dex and b"\x02kb\x00" in dex, len(dex))
    ok("② signed with APK signature scheme v2 («APK Sig Block 42» before the central directory)", b"APK Sig Block 42" in raw, len(raw))
    ok("② resources.arsc stored and 4-byte aligned (Android 11+ refuses it otherwise)",
       next(i for i in z.infolist() if i.filename == "resources.arsc").compress_type == zipfile.ZIP_STORED
       and (lambda zi: (zi.header_offset + 30 + len(zi.filename) + int.from_bytes(raw[zi.header_offset + 28:zi.header_offset + 30], "little")) % 4 == 0)(
           next(i for i in z.infolist() if i.filename == "resources.arsc")), "")

    # ── ③ the server
    env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
    d = subprocess.Popen([sys.executable, os.path.join(H, "step", "video", "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    U = f"http://127.0.0.1:{P1}"

    def get(path, ua=None, hdr=None):
        rq = urllib.request.Request(U + path, headers=dict({"User-Agent": ua} if ua else {}, **(hdr or {})))
        try:
            with urllib.request.urlopen(rq, timeout=20) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    seen = {}
    for name, ua in (("1.9 app", "HolyApp/1.9"), ("1.8 app", "HolyApp/1.8"), ("1.9 WebView", "Mozilla/5.0 (Linux; Android 14) Chrome/120 Mobile Safari/537.36 HolyApp/1.9"),
                     ("2.0 app", "HolyApp/2.0"), ("2.0 WebView", "Mozilla/5.0 (Linux; Android 14) Chrome/120 HolyApp/2.0"), ("browser", "Mozilla/5.0 (X11; Linux) Firefox/130")):   # 2.0 = the same key ⇒ it updates itself
        c, b = get("/api/app/info", ua)
        seen[name] = json.loads(b).get("apk") if c == 200 else c
    ok("③ /api/app/info: a 1.x app (its own call or its WebView) is offered code 0 — never a file it cannot install over itself",
       all(seen[k]["code"] == 0 for k in ("1.9 app", "1.8 app", "1.9 WebView")), seen)
    ok(f"③ … 2.0 and a browser see code {NC} «{NV}» (2.0 updates itself — the same key) · everyone gets «rekey» 11",
       all(seen[k]["code"] == NC and seen[k]["name"] == NV for k in ("2.0 app", "2.0 WebView", "browser"))
       and all(v["rekey"] == 11 for v in seen.values()), seen)
    c, apk = get("/app/holy.apk")
    ok("③ /app/holy.apk = the embedded app, the size and sha256 /api/app/info states",
       c == 200 and apk == raw and seen["browser"]["sha256"] == hashlib.sha256(raw).hexdigest() and seen["browser"]["size"] == len(raw), (c, len(apk)))
    rq = urllib.request.Request(U + "/api/app/pair", data=json.dumps({"name": "Pixel", "iid": "t-app20", "code": 11}).encode(),
                                headers={"Content-Type": "application/json"})
    pr = json.loads(urllib.request.urlopen(rq, timeout=20).read())
    c, b = get("/api/app/widget", "HolyApp/2.0", {"X-Holy-Device": pr.get("token", "")})
    wj = json.loads(b) if c == 200 else {}
    ok("③ /api/app/widget answers the linked phone with «kb» (six labels in order) and the old «k»",
       c == 200 and [x[0] for x in wj.get("kb") or []] == ["اليوم", "أمس", "آخر 7 أيام", "آخر 30 يوماً", "هذا الشهر", "الإجمالي"]
       and len(wj.get("k") or []) == 3, (c, wj))
    c0, _ = get("/api/app/widget", "HolyApp/2.0")
    ok("③ … and nobody without the phone's key (401)", c0 == 401, c0)

    # ── ④ the page
    r = subprocess.run(["node", os.path.join(H, "ui_app20.js"), U + "/", hashlib.sha256(raw).hexdigest(), str(NV), str(NC)] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=300, cwd="/tmp", env=env)
    out = r.stdout.strip() or r.stderr.strip()[-1500:]
    import re
    for line in out.splitlines():
        mm = re.match(r"ui_app20 (\d+)/(\d+)$", line)
        if mm:                                  # the browser's own count (its passes are not printed with -q)
            res.extend([True] * int(mm.group(1)) + [False] * (int(mm.group(2)) - int(mm.group(1))))
        elif not Q or line.startswith("❌"):
            print(line)
    if not re.search(r"^ui_app20 \d+/\d+$", out, re.M):
        ok("④ the browser part ran", False, out[-800:])
finally:
    if d:
        d.kill()
    os.chdir(cwd0)
    shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_app20: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
