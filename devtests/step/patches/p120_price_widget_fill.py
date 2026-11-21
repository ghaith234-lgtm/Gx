# 🪙 patch 120 (dashboard v3.36.70 · the prices widget fills its height). The first look on a real Android 14 (emulator run 156, the
#   default 4 ticker coins in a 3×3 widget) left a quarter of the widget empty under two rows of tiles — WidgetArt.renderPx now lets the
#   tiles grow up to 96 dp (was 72) when there are fewer coins than room, so the lines are taller and the widget stays full.
#   Only the embedded app changes (still 2.3 · code 14 — not delivered yet): APP_APK_B64 = argv[2]
#   python3 devtests/step/patches/p120_price_widget_fill.py Holy_Dashboard.pyw android/dist/Holy-2.3.apk
import base64, hashlib, os, re, sys, zipfile

if __name__ == "__main__":
    p, apk = sys.argv[1], sys.argv[2]
    raw = open(apk, "rb").read()
    with zipfile.ZipFile(apk) as z:
        dex = z.read("classes.dex")
    assert b"HolyPxWidget" in dex and b"HolyApp/2.3" in dex, "this APK is not 2.3"
    s = open(p, encoding="utf-8").read()
    APK_RE = re.compile(r'^(APP_APK_CODE = 14\nAPP_APK_NAME = "2\.3"\nAPP_APK_REKEY = .*\n)APP_APK_B64 = "[A-Za-z0-9+/=]+"$', re.M)
    if len(APK_RE.findall(s)) != 1:
        print("❌ the 2.3 APP_APK_* block not found exactly once — nothing written"); sys.exit(1)
    s = APK_RE.sub(lambda m: m.group(1) + 'APP_APK_B64 = "' + base64.b64encode(raw).decode() + '"', s)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ APK 2.3 (taller tiles) {len(raw)} bytes sha256 {hashlib.sha256(raw).hexdigest()[:16]} · compiles · {p}")
