# 🪜 patch 02 (F7) — «nan» / «inf» typed in the form passed every «> 0» check (NaN compares false both ways):
#   the table showed no refusal, deploy wrote NaN into the config and the engine failed on every order of those slots.
#   Now: the form refuses any number that is not finite · the engine's layout (and the dashboard's copy) treats it as
#   an invalid setting (no slot, no order — the «invalid settings» log line)
#   python3 devtests/step/patches/p02_finite.py ENGINE.py Holy_Dashboard.pyw   (in place, after patch 01 · each old text once)
import ast, os, sys

ENG = [
    ("    if P0 <= 0 or G <= 0 or d <= 0 or d1 <= 0 or Q <= 0:\n        return out\n    m = 0\n",
     "    if not all(math.isfinite(x) for x in (P0, G, d, d1, Q, floor, fee)) or P0 <= 0 or G <= 0 or d <= 0 or d1 <= 0 or Q <= 0:\n"
     "        return out                                  # 🔢 nan / inf ⇒ إعداد غير صالح (بلا أي أمر)\n    m = 0\n"),
]
DASH = ENG + [
    ('    if Q <= 0 or G <= 0 or d <= 0 or d1 <= 0:\n',
     '    if not all(math.isfinite(x) for x in (Q, d, d1, G, floor, p0)):       # 🔢 «nan» / «inf» يمرّ من كل مقارنة ⇒ يُرفض هنا\n'
     '        return None, "تأكد من الأرقام (المبلغ · عدد البيعات · المسافات · الأرضية)"\n'
     '    if Q <= 0 or G <= 0 or d <= 0 or d1 <= 0:\n'),
]
ALLOWED = {"_step_layout", "_step_args"}


def tops(src):
    out, cnt = {}, {}
    for n in ast.parse(src).body:
        nm = getattr(n, "name", None)
        if nm is None and isinstance(n, ast.Assign) and len(n.targets) == 1:
            nm = ast.unparse(n.targets[0])
        if nm is None:
            cnt[type(n).__name__] = cnt.get(type(n).__name__, 0) + 1
            nm = f"<{type(n).__name__}#{cnt[type(n).__name__]}>"
        out.setdefault(nm, []).append(ast.dump(n))
    return out


def patch(path, R, allowed=None):
    src0 = open(path, encoding="utf-8").read()
    src = src0
    for i, (a, b) in enumerate(R):
        n = src.count(a)
        if n != 1:
            print(f"❌ {os.path.basename(path)} replacement {i}: the old text is found {n} times (must be once) — nothing written")
            sys.exit(1)
        src = src.replace(a, b)
    compile(src, path, "exec")
    if allowed is not None:
        t0, t1 = tops(src0), tops(src)
        changed = {k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k)}
        if changed - allowed or set(t0) != set(t1):
            print(f"❌ unexpected top-level changes: {sorted(changed - allowed)} — nothing written"); sys.exit(1)
    return src


if __name__ == "__main__":
    e, d = sys.argv[1], sys.argv[2]
    se, sd = patch(e, ENG), patch(d, DASH, ALLOWED)          # both checked before either is written
    for p, s in ((e, se), (d, sd)):
        with open(p + ".tmp", "w", encoding="utf-8") as fh:
            fh.write(s)
        os.replace(p + ".tmp", p)
    print(f"✅ engine {len(ENG)} · dashboard {len(DASH)} replacements · compile · {e} · {d}")
