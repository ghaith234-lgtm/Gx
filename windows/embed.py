# 💻 put a built Windows program 2.0 into the dashboard (used by ci/win_build.ps1 and by hand):
#   the page part not there yet ⇒ patch 62 with the program · already there ⇒ only the program (WIN_EXE_CODE 4 · NAME «2.0» · B64)
#   python3 windows/embed.py Holy_Dashboard.pyw TheHolyDashboard.exe
import base64, hashlib, os, re, subprocess, sys

dash, exe = sys.argv[1], sys.argv[2]
s = open(dash, encoding="utf-8").read()
if "function winInit(){" not in s:
    h = os.path.dirname(os.path.abspath(__file__))
    sys.exit(subprocess.call([sys.executable, os.path.join(h, "..", "devtests", "step", "patches", "p62_win20.py"), dash, exe]))
raw = open(exe, "rb").read()
tag = raw.find(b"HOLY-URL-SLOT:")
assert raw[:2] == b"MZ" and tag > 0 and raw.count(b"HOLY-URL-SLOT:") == 1 and raw[tag + 14:tag + 14 + 560] == b"\0" * 560, "not the 2.0 program (its address slot)"
assert "HolyTray2".encode("utf-16-le") in raw, "not the 2.0 program (HolyTray2)"
RE = re.compile(r'^WIN_EXE_CODE = \d+\nWIN_EXE_NAME = "[^"]*"\nWIN_EXE_B64 = "[A-Za-z0-9+/=]+"$', re.M)
assert len(RE.findall(s)) == 1, "the WIN_EXE_* block not found exactly once"
s = RE.sub(lambda m: 'WIN_EXE_CODE = 4\nWIN_EXE_NAME = "2.0"\nWIN_EXE_B64 = "' + base64.b64encode(raw).decode() + '"', s)
compile(s, dash, "exec")
open(dash + ".tmp", "w", encoding="utf-8").write(s)
os.replace(dash + ".tmp", dash)
print(f"✅ the Windows program 2.0 in {dash}: {len(raw)} bytes · sha256 {hashlib.sha256(raw).hexdigest()}")
