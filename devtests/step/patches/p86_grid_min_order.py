# ⚠️ patch 86 (dashboard v3.36.51 · the grid deploy form warns before deploying) — the owner (14-11): «صلح الاثنين ويا تحذير النموذج».
#   With p84 the grid engines size every order on the coin's own step, so the one case left where a grid bot would never trade is an
#   order smaller than the exchange's minimum for that coin (minSz). The deploy now checks it with the coin's live price and rules
#   and refuses with the amount needed: «قيمة الأمر 3$ أصغر من الحد الأدنى للمنصة لهذه العملة (≈ 6.40$) …» (before, the bot was
#   deployed, never placed an order and wrote «زِد قيمة الأمر» in its log). Price or rules unknown ⇒ no check (as before).
#   python3 devtests/step/patches/p86_grid_min_order.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''    if g_type == "grid_range" and lower_p > 0 and upper_p > 0 and lower_p >= upper_p:
        return {"ok": False, "msg": "يجب أن يكون الحد الأدنى للنطاق أقل من الحد الأعلى"}
    cfg = {**keys, "symbol": sym, "grid_percentage": grid, "usd_value": usd, "min_price": minp,''',
     '''    if g_type == "grid_range" and lower_p > 0 and upper_p > 0 and lower_p >= upper_p:
        return {"ok": False, "msg": "يجب أن يكون الحد الأدنى للنطاق أقل من الحد الأعلى"}
    try:                                           # ⚠️ v3.36.51: أمر أصغر من حد المنصة لهذه العملة ⇒ البوت لا يتداول أبداً — يُرفض هنا بالمبلغ اللازم
        _p0 = float(base or 0) or float(PX.get(sym) or 0) or float(_acc_price(sym) or 0)
        _mn = float((_acc_spec(sym) or {}).get("minSz") or 0)
        if _p0 > 0 and _mn > 0 and math.isfinite(_p0) and usd / (_p0 * (1 + grid) ** 4) < _mn:
            _need = _mn * _p0 * (1 + grid) ** 4
            return {"ok": False, "msg": f"قيمة الأمر {usd:g}$ أصغر من الحد الأدنى للمنصة لهذه العملة (≈ {_need:.2f}$ بالسعر الحالي) — "
                                        f"اجعلها {math.ceil(_need * 1.05 * 100) / 100:g}$ على الأقل، وإلا لن يضع البوت أي أمر"}
    except Exception:
        pass
    cfg = {**keys, "symbol": sym, "grid_percentage": grid, "usd_value": usd, "min_price": minp,'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written"); sys.exit(1)
        s = s.replace(a, b)
    s = s.replace('APP_VERSION = "3.36.50"', 'APP_VERSION = "3.36.51"', 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacement · compiles · {p}")
