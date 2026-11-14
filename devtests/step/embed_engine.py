# 🪜 puts a changed graded-grid engine back into the dashboard — the ONLY way the engine is changed in the dashboard.
#   python3 devtests/step/embed_engine.py [engine.py] [Holy_Dashboard.pyw] [--dry] [--var=_GRIDP_B64]
#   (v3.36.44: --var picks another embedded engine — _GRIDP_B64 ➕ plus · _GRIDR_B64 🎚️ range …; the default stays the 🪜 graded grid)
#   Replaces ONE thing: the text of `_GRIDS_B64 = ( … )`. Before it writes anything it checks, and refuses on any failure:
#     ① the engine file compiles
#     ② the new literal decodes back to exactly the engine file
#     ③ every other top-level definition/assignment of the dashboard is identical (AST) — so the 7 other embedded engines,
#        the page, the routes and `step_layout`'s dashboard copy cannot change by accident
#     ④ the lines outside the literal are byte for byte the same
#   The file is written to a temporary name and renamed (never half-written). `GRIDS_VERSION` follows by itself (_eng_fp).
import ast, base64, hashlib, os, re, sys, zlib
H = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
DRY = "--dry" in sys.argv
VAR = next((a[6:] for a in sys.argv[1:] if a.startswith("--var=")), "_GRIDS_B64")
ENG = args[0] if len(args) > 0 else os.path.join(H, "eng", "main_step.py")
DASH = args[1] if len(args) > 1 else os.path.join(H, "..", "..", "Holy_Dashboard.pyw")
WIDTH = 120


def fail(msg):
    print("❌ refused:", msg); sys.exit(1)


def lit_span(lines):                      # (index of the `_GRIDS_B64 = (` line, index of the closing `)` line)
    a = [i for i, l in enumerate(lines) if l.startswith(VAR + " = (")]
    if len(a) != 1: fail(f"`{VAR} = (` found {len(a)} times")
    b = next((i for i in range(a[0] + 1, len(lines)) if lines[i] == ")"), None)
    if b is None: fail("closing `)` of the literal not found")
    return a[0], b


def decode(lines, a, b):
    return zlib.decompress(base64.b64decode("".join(l.strip().strip('"') for l in lines[a + 1:b]))).decode("utf-8")


def tops(src):                            # every top-level node except the engine literal, as comparable text
    out = []
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == VAR for t in n.targets):
            continue
        out.append(ast.dump(n))
    return out


eng = open(ENG, encoding="utf-8").read()
try:
    compile(eng, os.path.basename(ENG), "exec")                                        # ①
except SyntaxError as e:
    fail(f"the engine does not compile: {e}")
raw = open(DASH, encoding="utf-8", newline="").read()
if "\r" in raw: fail("the dashboard has CR line ends — not touching it")
lines = raw.split("\n")
a, b = lit_span(lines)
old = decode(lines, a, b)
if old == eng:
    print("= unchanged: the engine file equals the one embedded —", len(eng), "chars"); sys.exit(0)
packed = base64.b64encode(zlib.compress(eng.encode("utf-8"), 9)).decode("ascii")
new_lit = [VAR + ' = ('] + ['"' + packed[i:i + WIDTH] + '"' for i in range(0, len(packed), WIDTH)] + [")"]
new_lines = lines[:a] + new_lit + lines[b + 1:]
if decode(new_lines, a, a + len(new_lit) - 1) != eng: fail("the new literal does not decode to the engine file")      # ②
new_raw = "\n".join(new_lines)
if tops(new_raw) != tops(raw): fail("something other than the engine literal changed (AST)")                           # ③
if new_lines[:a] != lines[:a] or new_lines[a + len(new_lit):] != lines[b + 1:]: fail("lines outside the literal changed")   # ④
fp = lambda t: hashlib.sha1("\n".join(l.rstrip() for l in t.replace("\r\n", "\n").split("\n")).strip().encode("utf-8")).hexdigest()[:8]
print(f"✅ checks passed · engine {fp(old)} → {fp(eng)} · {len(old.splitlines())} → {len(eng.splitlines())} lines · literal {b - a + 1} → {len(new_lit)} lines")
if DRY: print("(dry run — nothing written)"); sys.exit(0)
tmp = DASH + ".tmp_embed"
open(tmp, "w", encoding="utf-8", newline="").write(new_raw)
os.replace(tmp, DASH)
print("written:", os.path.abspath(DASH))
