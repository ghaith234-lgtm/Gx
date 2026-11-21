# 🪙 patch 119 (dashboard v3.36.70 · the prices widget · app 2.3). The owner (21-11): «سوي ويدكيت اخر لاسعار العملات وبيه جارت صغير خطي
#   امام كل عملة … نفس الويدكت الاول · الاول زيل منه الكل» → after the samples: «ب سوي وكلما اكبر يسع اكثر مو بس ٦ وخلي شكل العملة بداخله ·
#   اخر ٢٤ ساعه بس خلي السعر يتحدث ابدي».
#   · /api/app/widget also answers «px»: the ticker's coins (its order · up to 20) = {s: the coin · p: the price for show · ch: its 24-hour
#     change · sp: its line over the last 24 hours (48 half-hour closes + the price now · 0…1000)} — the lines are fetched in the background
#     (public OKX candles, every 5 minutes at most) so the widget's request never waits · the prices follow the ticker's own (fresh within
#     3 minutes — fetched in the background when the ticker is off)
#   · ⚙️ 📱 «🪙 ويدجت الأسعار» with «📌 أضفه» (app 2.3: HolyApp.pinPrices · its count in the status «pxWidget») · an older app ⇒ «حدّث»
#   · the app 2.3 (android/: HolyPxWidget · WidgetArt.renderPx — the tiles: the coin's badge · name · change · price · its line; the bigger
#     the widget the more tiles · the first widget's rows lose «الكل») · APP_APK_CODE 14 · APP_APK_NAME «2.3» · APP_APK_B64 = argv[2]
#     (android/build.py --key … — the same key ⇒ the app updates itself · the key never enters the repository)
#   python3 devtests/step/patches/p119_price_widget.py Holy_Dashboard.pyw android/dist/Holy-2.3.apk
import base64, hashlib, os, re, sys, zipfile

PY = r'''

# ───────────── 🪙 v3.36.70: ويدجت الأسعار (تطبيق 2.3) — عملات الشريط بأسعارها وخط آخر 24 ساعة ─────────────
_WPX = {"sp": {}, "busy": False, "lock": threading.Lock()}
WPX_SP_EVERY = 300                       # خط كل عملة يُجدَّد كل 5 دقائق على الأكثر (شموع نصف ساعة · 48 = 24 ساعة)


def _wpx_s(x):
    """السعر للعرض في الويدجت: 91,240 · 3,105.4 · 138.62 · 0.15214"""
    try:
        x = float(x)
    except Exception:
        return "—"
    if not math.isfinite(x) or x <= 0:
        return "—"
    if x >= 10000:
        return f"{x:,.0f}"
    if x >= 1000:
        return f"{x:,.1f}"
    if x >= 1:
        return f"{x:.4f}".rstrip("0").rstrip(".") if x < 100 else f"{x:.2f}"
    d = min(12, max(4, 4 - int(math.floor(math.log10(x)))))
    return f"{x:.{d}f}".rstrip("0").rstrip(".")


def _wpx_refresh(coins, need_px):
    """(خيط بالخلفية) خطوط آخر 24 ساعة للعملات القديمة خطوطها + أسعار الشريط إذا كان متوقفاً — قراءة عامة بلا مفاتيح"""
    try:
        if need_px:
            _safe(ticker_fetch, default=None)
        now = time.time()
        for sym in coins:
            e = _WPX["sp"].get(sym)
            if e and now - e[0] < WPX_SP_EVERY:
                continue
            r = _safe(_okx_pub, f"/api/v5/market/candles?instId={sym}&bar=30m&limit=48", default=None)
            cl = []
            if r and str(r.get("code")) == "0" and r.get("data"):
                for c in reversed(r["data"]):
                    try:
                        cl.append(float(c[4]))
                    except Exception:
                        pass
            _WPX["sp"][sym] = (time.time(), cl if len(cl) >= 2 else (e[1] if e else []))
            time.sleep(0.12)
    finally:
        _WPX["busy"] = False


def app_widget_px():
    """🪙 عملات الشريط (ترتيبه · 20 على الأكثر) للويدجت: الرمز · السعر · تغير 24 ساعة · الخط (0…1000) — من الذاكرة فوراً، والقديم يُجدَّد بالخلفية"""
    coins = ticker_cfg()["coins"]
    rows = {r["sym"]: r for r in (TICKER.get("rows") or [])}
    now = time.time()
    need_px = now - float(TICKER.get("ts") or 0) > 180
    stale = [s for s in coins if not _WPX["sp"].get(s) or now - _WPX["sp"][s][0] >= WPX_SP_EVERY]
    if (need_px or stale) and not _WPX["busy"]:
        with _WPX["lock"]:
            if not _WPX["busy"]:
                _WPX["busy"] = True
                threading.Thread(target=_wpx_refresh, args=(coins, need_px), daemon=True).start()
    out = []
    for sym in coins:
        r = rows.get(sym)
        if not r or not r.get("px"):
            continue
        cl = list((_WPX["sp"].get(sym) or (0, []))[1]) + [float(r["px"])]
        sp = []
        if len(cl) >= 3:
            lo, hi = min(cl), max(cl)
            sp = [int(round((x - lo) / (hi - lo) * 1000)) if hi > lo else 500 for x in cl]
        out.append({"s": sym.split("-")[0], "p": _wpx_s(r["px"]), "ch": round(float(r.get("chg") or 0), 2), "sp": sp})
    return out
'''

R = [
    ("""            "bots": [r for _k, r in rows[:12]], "server": APP_VERSION}""",
     """            "bots": [r for _k, r in rows[:12]], "server": APP_VERSION,
            "px": _safe(app_widget_px, default=[])}                      # 🪙 v3.36.70: ويدجت الأسعار (تطبيق 2.3)"""),
    ("""

def app_feed_wait(since, wait):""", PY + """

def app_feed_wait(since, wait):"""),
    # ⚙️ 📱 the row
    ("""      ${row('🔗','عنوان اللوحة',`<span dir="ltr">${gEsc(s.origin||location.origin)}</span>`,`<button onclick="HolyApp.changeServer()">تغيير</button>`)}""",
     """      ${row('🪙','ويدجت الأسعار',(+s.code||0)<14?'حدّث التطبيق إلى النسخة 2.3 لتضع أسعار عملاتك بخط آخر 24 ساعة على الشاشة الرئيسية':
          ((+s.pxWidget||0)>0?'مضاف إلى الشاشة الرئيسية ✓ — عملات الشريط بأسعارها وخط آخر 24 ساعة · يتحدّث مع الويدجت الأول':'عملات الشريط بأسعارها وخط آخر 24 ساعة · كلما كبّرته اتسع لعملات أكثر')
          +' · الضغط عليه يفتح Holy'+(s.lock?' بعد البصمة':'')+((+s.pxWidget||0)>0||s.widgetPin?'':' · للإضافة: اضغط مطوّلاً على الشاشة الرئيسية ثم «الأدوات» ثم «Holy · الأسعار»'),
          (+s.code||0)>=14&&!(+s.pxWidget||0)&&s.widgetPin&&typeof HolyApp.pinPrices==='function'?`<button class="primary" onclick="appPinPrices()">📌 أضفه</button>`:'')}
      ${row('🔗','عنوان اللوحة',`<span dir="ltr">${gEsc(s.origin||location.origin)}</span>`,`<button onclick="HolyApp.changeServer()">تغيير</button>`)}"""),
    ("""function appPinWidget(){""",
     """function appPinPrices(){let r=false;try{r=HolyApp.pinPrices()}catch(e){}                 // 🪙 v3.36.70: التطبيق 2.3
  if(!r){toast('تعذّر الطلب — اضغط مطوّلاً على الشاشة الرئيسية ثم «الأدوات» ثم «Holy · الأسعار»',false);return}
  toast('📌 اختر «إضافة» في نافذة أندرويد',true);setTimeout(appRender,4000);setTimeout(appRender,10000)}
function appPinWidget(){"""),
    ("""APP_VERSION = "3.36.69\"""", """APP_VERSION = "3.36.70\""""),
]

if __name__ == "__main__":
    p, apk = sys.argv[1], sys.argv[2]
    raw = open(apk, "rb").read()
    with zipfile.ZipFile(apk) as z:
        assert "classes.dex" in z.namelist() and "AndroidManifest.xml" in z.namelist(), "not an APK"
        dex = z.read("classes.dex")
        man = z.read("AndroidManifest.xml")
    assert b"HolyPxWidget" in dex and b"pinPrices" in dex and b"HolyApp/2.3" in dex, "this APK is not 2.3 (no HolyPxWidget)"
    assert "com.holy.dash.HolyPxWidget".encode("utf-16le") in man, "the manifest has no prices widget receiver"
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    APK_RE = re.compile(r'^APP_APK_CODE = \d+\nAPP_APK_NAME = "[^"]*"\n(APP_APK_REKEY = .*\n)APP_APK_B64 = "[A-Za-z0-9+/=]+"$', re.M)
    if len(APK_RE.findall(s)) != 1:
        print("❌ the APP_APK_* block not found exactly once — nothing written"); sys.exit(1)
    s = APK_RE.sub(lambda m: 'APP_APK_CODE = 14\nAPP_APK_NAME = "2.3"\n' + m.group(1) + 'APP_APK_B64 = "' + base64.b64encode(raw).decode() + '"', s)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 🪙 the prices widget · APK 2.3 {len(raw)} bytes sha256 {hashlib.sha256(raw).hexdigest()[:16]} · compiles · {p}")
