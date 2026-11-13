# 📲 patch 56 (dashboard · the Android app 2.1 · the phone's own buttons) — the owner (13-11): «الازرار الي تحت الخاصة بالموبايل غير ظاهرة
#   خليها كذلك اختيارة اظهارها اما لا».
#   The app hides the phone's bars (status + navigation: back · home · recent) on purpose — they show for a moment on a swipe from the
#   edge. App 2.1 (android/ — Prefs.nav_bar · MainActivity.navShown · the insets listener pads the page above them · HolyApp.setNavBar /
#   HolyApp.navBar) lets the owner keep the navigation buttons on screen.
#   ① ⚙️ 📱 «📲 أزرار الهاتف» (inside the app 2.1+): a switch · hidden (as before) / shown · an older app ⇒ a row that says to update
#   ② APP_APK_CODE 12 · APP_APK_NAME «2.1» · APP_APK_B64 = argv[2] (android/build.py --key … — the same key as 2.0 ⇒ the app updates
#      itself from 2.0 · the key never enters the repository)
#   python3 devtests/step/patches/p56_app21_navbar.py Holy_Dashboard.pyw android/dist/Holy-2.1.apk
import base64, hashlib, os, re, sys, zipfile

R = [
    ('''     +L('💻','برنامج ويندوز','openWinPanel()',IN_WIN?'أنت داخل من البرنامج الآن':'نافذة خاصة على الحاسوب','bWin'))}''',
     '''     +(IN_APP?(navOk()?T('📲','أزرار الهاتف','uiNavToggle()','bNav',uiNavOn(),'ظاهرة — رجوع · الرئيسية أسفل الشاشة','مخفية — تظهر لحظة بالسحب من أسفل الشاشة')
        :L('📲','أزرار الهاتف','openAppPanel()','حدّث التطبيق إلى 2.1 لتختار ظهورها','bNav')):'')
     +L('💻','برنامج ويندوز','openWinPanel()',IN_WIN?'أنت داخل من البرنامج الآن':'نافذة خاصة على الحاسوب','bWin'))}'''),
    ('''function uiMbar(){''',
     '''function navOk(){try{return IN_APP&&typeof HolyApp.setNavBar==='function'}catch(e){return false}}   // 📲 v3.36.38: التطبيق 2.1+
function uiNavOn(){try{return !!HolyApp.navBar()}catch(e){return false}}
function uiNavToggle(){if(!navOk())return openAppPanel();const on=!uiNavOn();try{HolyApp.setNavBar(on)}catch(e){}setTimeout(openSettings,250);
  toast(on?'📲 أزرار الهاتف ظاهرة أسفل الشاشة':'📲 أزرار الهاتف مخفية — تظهر لحظة بالسحب من أسفل الشاشة',true)}
function uiMbar(){'''),
]

if __name__ == "__main__":
    p, apk = sys.argv[1], sys.argv[2]
    raw = open(apk, "rb").read()
    with zipfile.ZipFile(apk) as z:
        assert "classes.dex" in z.namelist() and "AndroidManifest.xml" in z.namelist(), "not an APK"
        dex = z.read("classes.dex")
    assert b"setNavBar" in dex and b"nav_bar" in dex and b"HolyApp/2.1" in dex, "this APK is not 2.1 (no setNavBar)"
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    APK_RE = re.compile(r'^APP_APK_CODE = \d+\nAPP_APK_NAME = "[^"]*"\n(APP_APK_REKEY = .*\n)APP_APK_B64 = "[A-Za-z0-9+/=]+"$', re.M)
    if len(APK_RE.findall(s)) != 1:
        print("❌ the APP_APK_* block not found exactly once — nothing written"); sys.exit(1)
    s = APK_RE.sub(lambda m: 'APP_APK_CODE = 12\nAPP_APK_NAME = "2.1"\n' + m.group(1) + 'APP_APK_B64 = "' + base64.b64encode(raw).decode() + '"', s)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · APK 2.1 {len(raw)} bytes sha256 {hashlib.sha256(raw).hexdigest()[:16]} · compiles · {p}")
