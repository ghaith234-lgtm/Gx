# 🪜⚡ patch 22 (engine · the state is written with the fast encoder) — found by t_deep.py «scale» + a profile: with 4,860 parts
#   the 3-second cycle took 350–410 ms and ~95% of it was save_json: `json.dump(data, f)` streams through Python's PURE-PYTHON encoder
#   (json.dump never uses the C one) · `json.dumps(data)` uses the C encoder — the same bytes, about 4× faster (1 MB: 56 ⇒ 15 ms).
#   The file is still written to a temporary name, flushed, fsync'ed and renamed (a power cut never leaves half a file).
#   python3 devtests/step/patches/p22_save_fast.py ENGINE.py
import os, sys

R = [
    ('''                json.dump(data, f, separators=(",", ":"))     # مضغوط: بوت بمئات الخانات يحفظ كل ثواني
''',
     '''                f.write(json.dumps(data, separators=(",", ":")))     # مضغوط · dumps = المشفّر السريع (dump يمشي بالبطيء) — نفس البايتات
'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
