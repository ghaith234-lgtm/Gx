# 🔤 v3.36.40 — the owner's own fonts (a «fonts» folder beside the dashboard · upload · delete) without a browser:
#   the font functions are taken from the dashboard itself and run against a temporary folder · a free system font (DejaVu / Liberation)
#   stands in for the owner's files (those never enter the repository) · no network
#   python3 devtests/t_fonts.py [Holy_Dashboard.pyw] [-q]
import base64, glob, hashlib, os, re, shutil, sys, tempfile

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {det}"))


src = open(DASH, encoding="utf-8").read()
i = src.index("# 🔤 v3.36.40 (المالك 13-11: أرسل خط خالد وأرسلان وسام)")
j = src.index("def _overview_cached(max_age=1.0):")
R = tempfile.mkdtemp(prefix="t_fonts_")
ns = {"os": os, "re": re, "_hl": hashlib, "_b64s": base64, "ROOT": R}
exec(src[i:j], ns)
FONT = next((p for p in glob.glob("/usr/share/fonts/truetype/*/*.ttf") if os.path.getsize(p) < 900_000), None)
try:
    ok("no «fonts» folder ⇒ an empty list (nothing breaks)", ns["user_fonts"]() == [])
    os.makedirs(os.path.join(R, "fonts"))
    shutil.copy(FONT, os.path.join(R, "fonts", "My Font.ttf"))
    open(os.path.join(R, "fonts", "notes.txt"), "w").write("not a font")
    L = ns["user_fonts"]()
    ok(f"a .ttf placed in the folder shows under its file name ({L and L[0]['name']}) · other files ignored",
       len(L) == 1 and L[0]["name"] == "My Font" and re.fullmatch(r"u[0-9a-f]{10}", L[0]["k"]) and re.fullmatch(r"[0-9a-f]{8}", L[0]["v"]), L)
    p, ct = ns["user_font_path"](L[0]["k"])
    ok("its file and type are found by its key only (not by a path)", p and p.endswith("My Font.ttf") and ct == "font/ttf"
       and ns["user_font_path"]("../My Font.ttf") == (None, None), (p, ct))
    raw = open(FONT, "rb").read()
    r = ns["user_font_add"]("../../evil name<script>.ttf", base64.b64encode(raw).decode())
    files = sorted(os.listdir(os.path.join(R, "fonts")))
    ok(f"an upload with a tricky name lands inside the folder with a clean name ({[f for f in files if f.startswith('evil')]})",
       r["ok"] and "evil namescript.ttf" in files and not os.path.exists(os.path.join(R, "evil name.ttf")) and len(r["fonts"]) == 2, (r.get("msg"), files))
    r2 = ns["user_font_add"]("x.ttf", "data:font/ttf;base64," + base64.b64encode(b"<html>not a font</html>").decode())
    ok(f"not a font ⇒ refused («{r2['msg']}»), nothing written", not r2["ok"] and len(ns["user_fonts"]()) == 2, r2)
    r3 = ns["user_font_add"]("big.ttf", base64.b64encode(b"\x00\x01\x00\x00" + b"\0" * (12 * 1024 * 1024)).decode())
    ok(f"over 12 MB ⇒ refused («{r3['msg']}»)", not r3["ok"] and "12" in r3["msg"], r3)
    r4 = ns["user_font_add"]("خالد.ttf", base64.b64encode(raw).decode())
    ok("an Arabic file name stays readable («خالد»)", r4["ok"] and any(f["name"] == "خالد" for f in r4["fonts"]), r4.get("fonts"))
    r6 = ns["user_font_add"]("alfont_com_ArbFONTS-Khalid-Art-Bold.ttf", base64.b64encode(raw).decode())
    ok(f"a downloaded file's long name is cleaned («{r6.get('msg')}»)", r6["ok"] and any(f["name"] == "Khalid Art Bold" for f in r6["fonts"])
       and os.path.exists(os.path.join(R, "fonts", "Khalid Art Bold.ttf")), r6.get("fonts"))
    r5 = ns["user_font_del"](r4["k"])
    ok("delete by key ⇒ the file is gone", r5["ok"] and not any(f["name"] == "خالد" for f in ns["user_fonts"]()), r5)
    ok("delete an unknown key ⇒ refused", not ns["user_font_del"]("u0000000000")["ok"])
finally:
    shutil.rmtree(R, ignore_errors=True)
print(f"{'✅' if all(res) else '❌'} t_fonts: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
