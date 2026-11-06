# 🪜 writes the graded-grid engine embedded in the dashboard (_GRIDS_B64) to a plain file for reading and testing.
#   The dashboard stays the only source of truth — this file is never edited by hand.
#   python3 devtests/step/extract_engine.py [Holy_Dashboard.pyw] [out.py]
import ast, base64, hashlib, os, sys, zlib
H = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, "..", "..", "Holy_Dashboard.pyw")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(H, "eng", "main_step.py")
src = open(D, encoding="utf-8").read()
b64 = next(ast.literal_eval(n.value) for n in ast.parse(src).body
           if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "_GRIDS_B64" for t in n.targets))
eng = zlib.decompress(base64.b64decode(b64)).decode("utf-8")
os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(eng)
norm = "\n".join(l.rstrip() for l in eng.replace("\r\n", "\n").split("\n")).strip()
print(OUT, eng.count("\n"), "lines · fingerprint", hashlib.sha1(norm.encode("utf-8")).hexdigest()[:8])
