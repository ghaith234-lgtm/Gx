# 🧪 patch 41 (dashboard · the trial path) — found by the v3.36.33 regression (t_bt_real ⑦, 19/20 once): every file is written through
#   «<name>.dash_tmp» then renamed (save_json_atomic). The status read ANY «err_*» file ⇒ it reported «error» from «err_f.json.dash_tmp»
#   before the rename, while «finished?» looked for «err_f.json» itself ⇒ a new test started in that instant was refused as «a test is
#   running». The same for «s_*» (a path counted done while its result was still being written). Only the final «.json» files count now.
#   python3 devtests/step/patches/p41_bt_tmp.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''        return n > 0 and sum(1 for f in os.listdir(jd) if f.startswith("s_")) >= n''',
     '''        return n > 0 and sum(1 for f in os.listdir(jd) if f.startswith("s_") and f.endswith(".json")) >= n   # 🧪 v3.36.33: لا «.dash_tmp»'''),
    ('''    for fn in sorted(os.listdir(jd)):
        if fn.startswith("err_"):''',
     '''    for fn in sorted(os.listdir(jd)):
        if fn.startswith("err_") and fn.endswith(".json"):      # 🧪 v3.36.33: ملف «.dash_tmp» قبل اسمه النهائي ما ينقرا (كان يسبق «انتهى؟»)'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
