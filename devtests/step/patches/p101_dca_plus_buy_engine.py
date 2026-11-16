# ⚡ patch 101 (dashboard v3.36.59 · DCA+ الشرائي — the owner 16-11: «Dca + خليه زر بالخارج وضيف معه الشرائية»). The free ladder of
#   patch 94 on the BUY DCA: the engine `dca_plus_buy.py` is made from the buy DCA `dca_buy.py` (which stays byte for byte) with the
#   very same replacements as patch 94 (taken from it — one source), mirrored where the direction matters:
#   · the ladder from the owner's rows `plus_rows` = [{d: distance % BELOW the order before, q: its size (coins), x: its exit %}, …]
#   · the cycle's target = the weighted average × (1 + x of the DEEPEST order filled) — sells everything at once there (dollar profit)
#   · edits from the table or the chart while it runs (`plus_edit`) — exactly as DCA+ (the sell one)
#   python3 devtests/step/patches/p101_dca_plus_buy_engine.py devtests/step/eng/dca_buy.py devtests/step/eng/dca_plus_buy.py
import importlib.util, os, sys

_sp = importlib.util.spec_from_file_location("p94", os.path.join(os.path.dirname(os.path.abspath(__file__)), "p94_dca_plus_ladder.py"))
p94 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(p94)

ROWS = p94.ROWS
for a, b in (
        ('''# ═══════════ ⚡ DCA+ (v3.36.57): السلّم الحر — كل أمر بمسافته وكميته ونسبة خروجه (الجدول أو الرسم البياني) ═══════════''',
         '''# ═══════════ ⚡ DCA+ الشرائي (v3.36.59): السلّم الحر — كل أمر بمسافته (تحت الذي قبله) وكميته ونسبة خروجه (فوق المتوسط) ═══════════'''),
        ('''    """مستويات السلّم من الصفوف: كل أمر = الذي قبله × (1 + مسافته) — البيعي: فوق"""''',
         '''    """مستويات السلّم من الصفوف: كل أمر = الذي قبله × (1 − مسافته) — الشرائي: تحت"""'''),
        ('''            p = p * (1 + float(r["d"]) / 100.0)''', '''            p = p * (1 - float(r["d"]) / 100.0)'''),
        ('''        state.pop("plus_edit_err", None)
        log_history(symbol, f"✏️ حُفظت الأوامر الجديدة''', '''        state.pop("plus_edit_err", None)
        log_history(symbol, f"✏️ حُفظت الأوامر الجديدة'''),
):
    if ROWS.count(a) != 1:
        print(f"❌ the DCA+ rows of patch 94 changed — {a[:80]!r} found {ROWS.count(a)} times"); sys.exit(1)
    ROWS = ROWS.replace(a, b)

R = []
for a, b in p94.R:
    if a.startswith('''  The Holy DCA Bot'''):
        b = '''  The Holy DCA+ Bot — الشرائي بسلّم حر: كل أمر بمسافته وكميته ونسبة خروجه (v3.36.59 · نسخة من محرك DCA الشرائي — الأصل ما تغيّر)'''
    elif a.startswith('''def compute_sell_levels'''):
        a = '''def compute_sell_levels(cfg, base_price):
    """يحسب مستويات الشراء التدريجي من الإعدادات — شرائي (تحت)"""'''
        b = '''def compute_sell_levels(cfg, base_price):
    """يحسب مستويات الشراء التدريجي من الإعدادات — شرائي (تحت) · ⚡ DCA+: من صفوف المالك (plus_rows) لو موجودة"""
    if isinstance(cfg.get("plus_rows"), list) and cfg.get("plus_rows"):
        return plus_levels(cfg["plus_rows"], base_price)'''
    elif a.startswith('''def run_cycle'''):
        b = ROWS.lstrip("\n") + '''

def run_cycle(trade_api, market_api, cfg, state):'''
    elif a.startswith('''    print("  The Holy DCA Bot'''):
        b = '''    print("  The Holy DCA+ Bot — الشرائي بسلّم حر")'''
    elif a.startswith('''    log_history(SYMBOL, "⚡ بوت DCA انطلق")'''):
        b = '''    log_history(SYMBOL, "⚡ بوت DCA+ الشرائي انطلق (سلّم حر: كل أمر بمسافته وكميته ونسبة خروجه)")'''
    elif "tp_raw = plus_tp" in b:
        b = '''    tp_raw = plus_tp(cfg, filled)                    # ⚡ DCA+: نسبة خروج أعمق أمر منفّذ (فوق المتوسط)'''
    R.append((a, b))

if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    s = open(src, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    if "p * (1 - float(r[\"d\"]) / 100.0)" not in s or "target = avg * (1 + tp_pct)" not in s:
        print("❌ the buy direction is not there"); sys.exit(1)
    compile(s, out, "exec")
    open(out, "w", encoding="utf-8").write(s)
    print(f"✅ {len(R)} replacements · {out} ({len(s.splitlines())} lines) from {src} (unchanged)")
