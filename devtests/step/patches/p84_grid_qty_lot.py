# 🔢 patch 84 (engines ♾️ main.py — sacred · ➕ grid_plus · 🎚️ grid_range — changed with the owner's yes, 14-11: «صلح الاثنين ويا تحذير
#   النموذج») — the full audit, batch 2: the grid engines rounded every order's quantity to TWO decimals (`round(usd / price, 2)`), so the
#   smallest order was 0.01 coin: BTC with a 10$ order ⇒ quantity 0 ⇒ the bot never traded (and said «زِد قيمة الأمر») · a 3,000$ coin
#   with a 20$ order ⇒ 0.01 = 30$ (half more than asked) · SOL with 3$ ⇒ 0.04 = 3.2$.
#   ⇒ `_q_lot(q)`: the quantity on the coin's own step at the exchange (lotSz — read before the first ladder since p66); without the
#     step (not loaded) it is two decimals as before.
#   · it still calls round(q, 2) first: reinvest.py swaps `round` for its one armed order (its exact quantity) — respected as it was
#   · `_floor_qty` (sells never exceed what the bot holds) floors on the coin's step too when it is finer than its 0.01 unit
#     (otherwise a 0.0375 buy would be sold as 0.03)
#   · found once BTC could trade at all: `fmt_price` counted the decimals of the price step from f"{t:.18f}" — for a step of 0.1 (BTC) or
#     0.05 that is 18 decimals ⇒ the price went out as 63618.200000000004 ⇒ «Parameter px error» on every order ⇒ counted from the
#     number's own text now (0.1 ⇒ 1 · 1e-05 ⇒ 5)
#   · only new orders change; what is already in the books (levels · memory · store) keeps its quantities
#   python3 devtests/step/patches/p84_grid_qty_lot.py devtests/step/eng/main.py     (the same for grid_plus.py · grid_range.py)
import os, sys

HELPER = '''def _q_lot(q):
    """🔢 v3.36.51: كمية الأمر على خطوة العملة بالمنصة (lotSz) — كانت خانتين ثابتتين ⇒ عملة غالية بأمر صغير = صفر أو أكبر من المطلوب.
    round(q, 2) يبقى يُستدعى أولاً: غلاف إعادة الاستثمار يبدّله لأمره المسلّح (كميته الدقيقة) ⇒ نحترمه كما كان."""
    import builtins as _b
    r2 = round(q, 2)
    try:
        if r2 != _b.round(float(q), 2):
            return r2
        lot = INSTRUMENT_SPEC.get("lotSz")
        if not lot or lot <= 0:
            return r2
        v = float(_sz_str(q))
        return v if math.isfinite(v) and v >= 0 else r2
    except Exception:
        return r2

'''
A_HELP = "def fmt_qty(qty):\n"
FLOOR_A = '''    st = float(QTY_FLOOR.get("step") or 0.01)
    return round(math.floor(float(q) / st + 1e-9) * st, 10)'''
FLOOR_B = '''    st = float(QTY_FLOOR.get("step") or 0.01)
    _lot = INSTRUMENT_SPEC.get("lotSz")
    if _lot and 0 < _lot < st:
        st = float(_lot)                               # 🔢 v3.36.51: خطوة العملة أدق من 0.01 ⇒ البيع يُدوَّر عليها (شراء 0.0375 لا يُباع 0.03)
    return round(math.floor(float(q) / st + 1e-9) * st, 10)'''
TICK_A = '''        _s = f"{t:.18f}".rstrip("0")
        dec = len(_s.split(".")[1]) if "." in _s else 0'''
TICK_B = '''        from decimal import Decimal as _D             # 🔢 v3.36.51: f"{0.1:.18f}" = 0.100000000000000006 ⇒ كان يعدّ 18 خانة لخطوة 0.1 (و0.05)
        dec = max(0, -_D(repr(float(t))).normalize().as_tuple().exponent)   #    ⇒ السعر يطلع 63618.200000000004 والمنصة ترفضه «Parameter px error»'''
MARKS = ('usd_value"] /', "exact_qty if exact_qty", "_usd / _anchor", 'float(_v["locked_qty"])', "float(rebuy)")
WANT = {"main.py": 11, "grid_plus.py": 11, "grid_range.py": 13}


def swap(line):
    i = line.find("round(")
    if i < 0 or not any(m in line for m in MARKS):
        return line, 0
    d, j = 0, i + 5
    while j < len(line):
        if line[j] == "(":
            d += 1
        elif line[j] == ")":
            d -= 1
            if d == 0:
                break
        j += 1
    inner = line[i + 6:j]
    if not inner.endswith(", 2"):
        return line, 0
    return line[:i] + "_q_lot(" + inner[:-3] + ")" + line[j + 1:], 1


if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    if "_q_lot(" in s:
        print("❌ already applied"); sys.exit(1)
    if s.count(A_HELP) != 1 or s.count(FLOOR_A) != 1 or s.count(TICK_A) != 1:
        print(f"❌ anchors: helper {s.count(A_HELP)} · floor {s.count(FLOOR_A)} · tick {s.count(TICK_A)}"); sys.exit(1)
    out, n = [], 0
    for line in s.split("\n"):
        l2, k = swap(line)
        out.append(l2); n += k
    want = WANT.get(os.path.basename(p))
    if want is not None and n != want:
        print(f"❌ {n} quantity sites changed, expected {want} — nothing written"); sys.exit(1)
    s = "\n".join(out).replace(A_HELP, HELPER + A_HELP).replace(FLOOR_A, FLOOR_B).replace(TICK_A, TICK_B)
    left = [l.strip()[:90] for l in s.split("\n") if "round(" in l and ", 2)" in l and any(m in l for m in MARKS) and "def _q_lot" not in l]
    if left:
        print("❌ left:", left[:3]); sys.exit(1)
    compile(s, p, "exec")
    open(p, "w", encoding="utf-8").write(s)
    print(f"✅ {n} quantity sites on the coin's step · _floor_qty · compiles · {p}")
