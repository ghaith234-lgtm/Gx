# 🗣️ v3.36.42 — apply one batch of MSA rewrites to the dashboard: each edit = (line, the phrase as it is there, its MSA form).
#   The phrase must be on that line (or within the next 40 lines — a multi-line text); every occurrence on that line changes;
#   nothing else is touched (the code around it stays byte for byte) · the whole batch or nothing · the file must still compile.
#   python3 devtests/step/patches/msa/msa_apply.py Holy_Dashboard.pyw devtests/step/patches/msa/b01.py
import importlib.util, os, sys

def load(p):
    sp = importlib.util.spec_from_file_location("batch", p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m.E

if __name__ == "__main__":
    dash, bat = sys.argv[1], sys.argv[2]
    L = open(dash, encoding="utf-8").read().split("\n")
    E = load(bat); bad = []; n = 0
    for ln, old, new in E:
        if old == new:
            continue
        k = next((j for j in range(ln - 1, min(len(L), ln + 40)) if old in L[j]), None)
        if k is None:
            bad.append((ln, old)); continue
        L[k] = L[k].replace(old, new); n += 1
    if bad:
        for b in bad: print("❌ not found:", b)
        sys.exit(1)
    s = "\n".join(L)
    compile(s, dash, "exec")
    open(dash + ".tmp", "w", encoding="utf-8").write(s); os.replace(dash + ".tmp", dash)
    print(f"✅ {os.path.basename(bat)}: {n} phrases in MSA · compiles")
