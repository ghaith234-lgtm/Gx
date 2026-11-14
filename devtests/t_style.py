# 🧭 the guard of the fixed style (v3.36.43) — the owner (14-11): «اريد هذه الاشياء ثوابت بعد اي اضافة تنضاف ، اللهجة الواجهات شكل الكتابة
#   وغيرها … حتى يصير كله نفس النسق». The written list is HANDOFF §١ «🧭 النسق الثابت»; this test fails when a change breaks the parts a
#   machine can check (the window frame has its own guard: devtests/t_windows.py):
#   ① the language: no dialect word in any text a customer sees — the page (HTML text · attributes · JS strings and templates), the
#      server's Python strings and f-strings (replies · Telegram · reports), the login page, the Android app's texts (android/smali)
#   ② the colours: the page's hard-written colours (#rgb / #rrggbb) outside the theme blocks may only be ones it already had —
#      anything new comes from the theme variables (var(--vio) · rgb(var(--cyan-rgb)/…) · var(--tx) …) so every palette colours it
#   ③ the writing: no new font-family in the page — new elements take the chosen font (numbers: class «num»)
#   ④ the direction: both pages are Arabic right-to-left (lang="ar" dir="rtl")
#   What is allowed today (texts that read the engines' own log lines · scanner leftovers from code comments) is in
#   devtests/style_baseline.json — written once by «--rebase» (only on purpose, when an exception is really needed).
#   python3 devtests/t_style.py [Holy_Dashboard.pyw] [-q] [--rebase]
import json, os, re, sys

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, "tools"))
sys.path.insert(0, os.path.join(H, "..", "android", "tools"))
import msa_scan                     # noqa: E402
from msa22 import CS, dec           # noqa: E402

Q = "-q" in sys.argv
REBASE = "--rebase" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
SMALI = os.path.join(H, "..", "android", "smali")
BASE = os.path.join(H, "style_baseline.json")
# words that are MSA as well (بعد · كله · يعني …) — the scanner flags them, a reader would not
WEAK = {"بعد", "كلها", "كله", "يعني", "ترى", "كلي", "انقطع", "يرجع", "ترجع", "رجعت", "مال", "مالك", "يحسبها", "يحسبه", "يعرفه", "رح"}
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1500]}"), flush=True)


def norm(t):
    return re.sub(r"\s+", " ", t).strip()[:160]


s = open(DASH, encoding="utf-8").read()

# ① the language
hits = set()
segs = msa_scan.scan(DASH)
CMT = re.compile(r"/\*.*?\*/|(?:^|(?<=\s))//[^\n]*", re.S)   # a template the scanner read with code inside it: its comments are not text
for line, kind, text in segs:
    if kind in ("tpl", "js") or text.lstrip().startswith(("/*", "(function")):
        text = CMT.sub(" ", text)
    w = {m.group(0) for m in msa_scan.DRX.finditer(text)} - WEAK
    if w:
        hits.add(kind + "|" + norm(text))
app = set()
for root, _, names in os.walk(SMALI):
    for n in names:
        if n.endswith(".smali"):
            for l in open(os.path.join(root, n), encoding="utf-8"):
                m = CS.match(l.rstrip("\n"))
                if m:
                    t = dec(m.group(2)).encode("utf-16", "surrogatepass").decode("utf-16", "replace")
                    if msa_scan.AR.search(t) and ({x.group(0) for x in msa_scan.DRX.finditer(t)} - WEAK):
                        app.add("app|" + norm(t))

# ② the colours (the main page — outside the theme blocks and the palette lists)
page = s[s.index("<html", s.index("HTML_PAGE = r")):]
page = page[:page.index('"""')]
bare = re.sub(r"html\[data-theme=\"[a-z0-9]+\"\][^{]*\{[^}]*\}", " ", page)
bare = re.sub(r":root\{[^}]*\}", " ", bare)
bare = re.sub(r"const THEMES=\[.*?\];", " ", bare, flags=re.S)
cols = {c.lower() for c in re.findall(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b(?![0-9a-fA-F])", bare)}
fonts = len(re.findall(r"font-family", page))

if REBASE:
    json.dump({"note": "t_style.py --rebase · what the style guard allows today — add to it only on purpose",
               "texts": sorted(hits), "app": sorted(app), "colors": sorted(cols), "font_family": fonts},
              open(BASE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"📝 baseline written: {len(hits)} texts · {len(app)} app texts · {len(cols)} colours · font-family ×{fonts}")
    sys.exit(0)

B = json.load(open(BASE, encoding="utf-8"))
new = sorted(hits - set(B["texts"]))
ok(f"① the language: no new dialect in what a customer sees (page · server · Telegram · reports · login — {len(segs)} texts read)",
   not new, "\n  " + "\n  ".join(new[:25]))
newa = sorted(app - set(B["app"]))
ok("① the language: no dialect in the Android app's texts", not newa, "\n  " + "\n  ".join(newa[:25]))
newc = sorted(cols - set(B["colors"]))
ok(f"② the colours: no new hard-written colour in the page (use the theme variables — {len(cols)} known)", not newc,
   f"new: {newc[:30]} — write them as var(--…) / rgb(var(--…-rgb)/…) so every palette colours them")
ok(f"③ the writing: no new font-family in the page (×{fonts} — new elements take the chosen font · numbers class «num»)",
   fonts <= int(B["font_family"]), f"{fonts} > {B['font_family']}")
login = s[s.index('LOGIN_PAGE = """'):s.index('LOGIN_PAGE = """') + 300]
ok("④ the direction: both pages are Arabic right-to-left", '<html lang="ar" dir="rtl"' in page[:200] and '<html lang="ar" dir="rtl"' in login)
gone = len(set(B["texts"]) - hits)
if gone and not Q:
    print(f"ℹ️ {gone} allowed text(s) no longer in the page (fine — «--rebase» tidies the list)")
print(f"✅ t_style: {sum(res)}/{len(res)}" if all(res) else f"❌ t_style: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
