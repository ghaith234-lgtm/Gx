# ♾️ patch 72 (engine · the infinite grid main.py — sacred: changed ONLY with the owner's yes) — the owner (14-11), after v3.36.44 fixed
#   ➕ plus and 🎚️ range and said main.py has the same four problems: «1 سويه … واهم شي ماكو مشاكل ويصير خربطه».
#   The same code ⇒ the same four patches, applied as they are (their anchors match main.py exactly — checked):
#   p65 (the resume line after the dollar check · «ما يكفي ولا درجة» once + every 6 hours · a buy refused for dollars rests 1 ⇒ 10 min)
#   p66 (the price step read before the first ladder) · p67 · p69 (clean quantities in the log lines)
#   python3 devtests/step/patches/p72_main_cash.py devtests/step/eng/main.py
import importlib.util, os, sys

H = os.path.dirname(os.path.abspath(__file__))
SEQ = ("p65_grid_cash", "p66_grid_spec_first", "p67_grid_qty_text", "p69_grid_catch_qty_text")

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    n = 0
    for name in SEQ:
        spec = importlib.util.spec_from_file_location(name, os.path.join(H, name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for i, (a, b) in enumerate(mod.R):
            if s.count(a) != 1:
                print(f"❌ {name} replacement {i} found {s.count(a)} times — nothing written"); sys.exit(1)
            s = s.replace(a, b)
            n += 1
    compile(s, p, "exec")
    open(p, "w", encoding="utf-8").write(s)
    print(f"✅ {n} replacements ({' · '.join(SEQ)}) · compiles · {p}")
