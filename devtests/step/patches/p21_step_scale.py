# 🪜📦 patch 21 (dashboard · a 🪜 bot with thousands of parts stays light on the card) — found by t_deep.py «scale»: 20 parts ×
#   243 levels = 4,860 parts ⇒ the card still carried 197 KB every refresh: the grid's generic price lists (`ladder.vsells` /
#   `ladder.vbuys` = every order in memory). For 🪜 with more than STEP_SL_MAX parts they carry the nearest 40 each way (all the card
#   reads from them: the lowest sell · the highest buy · the drawer's 14 nearest) and the dollars of every buy waiting in memory go
#   as one number (`vbuy_usd`, what «need» per wallet adds up). «🪜 السلم» for 🪜 = the full ladder (p20), not these lists.
#   python3 devtests/step/patches/p21_step_scale.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''            "ladder": {"sells": pack_levels(st.get("limit_sells"), "s"),
                       "buys": (_step_merge_lv if _bt == "grid_step" else (lambda x: x))(pack_levels(st.get("limit_buys"), "b")),
                       "vsells": pack_levels(st.get("virtual_sells"), "vs"),
                       "vbuys": (_step_merge_lv if _bt == "grid_step" else (lambda x: x))(pack_levels(st.get("virtual_buys"), "vb")),''',
     '''            "ladder": {"sells": pack_levels(st.get("limit_sells"), "s"),
                       "buys": (_step_merge_lv if _bt == "grid_step" else (lambda x: x))(pack_levels(st.get("limit_buys"), "b")),
                       "vsells": _step_near(pack_levels(st.get("virtual_sells"), "vs"), st, False, _bt),
                       "vbuys": _step_near((_step_merge_lv if _bt == "grid_step" else (lambda x: x))(pack_levels(st.get("virtual_buys"), "vb")), st, True, _bt),'''),
    ('''            "sl_far": (_safe(_step_sl_far, st, default=None) if _bt == "grid_step" else None),     # 🪜 v3.36.20: الباقي مختصر
''',
     '''            "sl_far": (_safe(_step_sl_far, st, default=None) if _bt == "grid_step" else None),     # 🪜 v3.36.20: الباقي مختصر
            "vbuy_usd": (round(sum(float(v.get("target_price") or 0) * float(v.get("locked_qty") or 0)
                                   for v in (st.get("virtual_buys") or {}).values()), 6) if _bt == "grid_step" else None),
'''),
    ('''def _step_sl_far(st):''',
     '''def _step_near(lst, st, buy, bt, n=40):
    """🪜 v3.36.20: قائمة الشبكة العامة (ذاكرة بيع/شراء) لبوت متدرج كبير — الأقرب `n` بس (أدنى بيع · أعلى شراء · أقرب 14 بالدرج)"""
    if bt != "grid_step" or len(st.get("slots") or {}) <= STEP_SL_MAX or len(lst) <= n:
        return lst
    return sorted(lst, key=lambda x: -float(x.get("p") or 0) if buy else float(x.get("p") or 0))[:n]


def _step_sl_far(st):'''),
    ('''function vbuyCost(b){let v=0;''', '''function vbuyCost(b){if(b.vbuy_usd!=null)return +b.vbuy_usd||0;let v=0;'''),
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
