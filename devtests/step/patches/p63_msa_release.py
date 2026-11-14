# 🗣️ patch 63 (dashboard v3.36.42 · the owner 14-11: «حول المشروع كله عربي فصيح» — scope «كل اللي يشوفه الزبون»)
#   The texts themselves were changed by devtests/step/patches/msa/b01…b29.py (msa_apply.py: line-scoped, the line count never changes,
#   regexes that read the engines' log lines left as they are). This patch carries what is left for the release:
#   ① APP_VERSION 3.36.42
#   ② the Android app 2.2 (every text in MSA · code 13 · the same key as 2.0/2.1 ⇒ it updates itself) — APP_APK_* = argv[2]
#   python3 devtests/step/patches/p63_msa_release.py Holy_Dashboard.pyw android/dist/Holy-2.2.apk
import base64, hashlib, os, re, sys, zipfile

if __name__ == "__main__":
    p, apk = sys.argv[1], sys.argv[2]
    raw = open(apk, "rb").read()
    with zipfile.ZipFile(apk) as z:
        assert "classes.dex" in z.namelist() and "AndroidManifest.xml" in z.namelist(), "not an APK"
        dex = z.read("classes.dex")
    assert b"HolyApp/2.2" in dex and b"setNavBar" in dex, "this APK is not 2.2"
    s = open(p, encoding="utf-8").read()
    a = 'APP_VERSION = "3.36.41"'
    if s.count(a) != 1:
        print("❌ APP_VERSION 3.36.41 not found once — nothing written"); sys.exit(1)
    s = s.replace(a, 'APP_VERSION = "3.36.42"')
    APK_RE = re.compile(r'^APP_APK_CODE = \d+\nAPP_APK_NAME = "[^"]*"\n(APP_APK_REKEY = .*\n)APP_APK_B64 = "[A-Za-z0-9+/=]+"$', re.M)
    if len(APK_RE.findall(s)) != 1:
        print("❌ the APP_APK_* block not found exactly once — nothing written"); sys.exit(1)
    s = APK_RE.sub(lambda m: 'APP_APK_CODE = 13\nAPP_APK_NAME = "2.2"\n' + m.group(1) + 'APP_APK_B64 = "' + base64.b64encode(raw).decode() + '"', s)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ v3.36.42 · APK 2.2 {len(raw)} bytes sha256 {hashlib.sha256(raw).hexdigest()[:16]} · compiles · {p}")
