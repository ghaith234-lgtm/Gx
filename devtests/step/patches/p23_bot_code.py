# 🆔 patch 23 (dashboard · every bot type) — the owner (7-11): «عند نشر بوت ويربح البوت واعادته يحسب الربح له … اريد اتخلي لكل بوت كود
#   عشوائي ولكل البوتات». A bot's folder is its identity in every book (the daily profit ledger · reinvest · coins · the start date ·
#   the archive · its orders' id prefix). Every deploy named it after the coin only (`step_xrp` · `xrp` · `dca_xrp` · `rec_xrp` ·
#   `va_xrp`), adding `_1` only while that folder existed — so a bot deployed after the old one was deleted (moved to _archive) took
#   the same name and inherited the old bot's history: its profit on the widget, the trade log, the reports.
#   Now every new bot's folder = the old prefix + a random 6-character code (`step_xrp_57d3c8`), never one that existed, is in the
#   ledger or in the archive ⇒ a new bot starts with empty books, always. Bots already running keep their folders (nothing moves).
#   python3 devtests/step/patches/p23_bot_code.py Holy_Dashboard.pyw
import os, sys

HELPER = '''def _new_bot_folder(prefix):
    """🆔 v3.36.20 (طلب المالك 7-11): مجلد بوت جديد = البادئة + كود عشوائي من 6 حروف — المجلد هو هوية البوت بكل الدفاتر (الربح اليومي ·
    إعادة الاستثمار · العملات · تاريخ التشغيل · الأرشيف · بادئة أوامره) ⇒ بوت جديد ما يورث أبداً دفاتر بوت محذوف كان بنفس الاسم
    (قبل: «step_xrp» ينعاد بعد الحذف ⇒ ربح القديم يطلع للجديد بالويدجت والسجل) · ما يكرر مجلد موجود ولا مفتاح بالدفتر ولا مؤرشف"""
    import secrets
    led = _safe(load_json, LEDGER, default={}) or {}
    used = set(led) if isinstance(led, dict) else set()
    try:
        arch = os.listdir(os.path.join(ROOT, "_archive"))
    except Exception:
        arch = []
    for _ in range(200):
        folder = f"{prefix}_{secrets.token_hex(3)}"
        if not os.path.exists(os.path.join(ROOT, folder)) and folder not in used and not any(a.endswith("_" + folder) for a in arch):
            return folder
    return f"{prefix}_{secrets.token_hex(8)}"


'''

R = [
    ('''# ───────────── النشر والاستنساخ والتعديل والحذف ─────────────
def find_script(name):''',
     '''# ───────────── النشر والاستنساخ والتعديل والحذف ─────────────
''' + HELPER + '''def find_script(name):'''),
    ('''    folder = "va_" + base.lower()
    base_folder, c = folder, 1
    while os.path.exists(os.path.join(ROOT, folder)):
        folder = f"{base_folder}_{c}"; c += 1
''', '''    folder = _new_bot_folder("va_" + base.lower())               # 🆔 v3.36.20: كود عشوائي لكل بوت
'''),
    ('''    folder = "dca_" + sym.split("-")[0].lower()
    base_folder, c = folder, 1
    while os.path.exists(os.path.join(ROOT, folder)):
        folder = f"{base_folder}_{c}"; c += 1
''', '''    folder = _new_bot_folder("dca_" + sym.split("-")[0].lower())   # 🆔 v3.36.20: كود عشوائي لكل بوت
'''),
    ('''    folder = "rec_" + base.lower()
    base_folder, c = folder, 1
    while os.path.exists(os.path.join(ROOT, folder)):
        folder = f"{base_folder}_{c}"; c += 1
''', '''    folder = _new_bot_folder("rec_" + base.lower())              # 🆔 v3.36.20: كود عشوائي لكل بوت
'''),
    ('''    folder = "step_" + a["base"].lower()
    base_folder, c = folder, 1
    while os.path.exists(os.path.join(ROOT, folder)):
        folder = f"{base_folder}_{c}"; c += 1
''', '''    folder = _new_bot_folder("step_" + a["base"].lower())        # 🆔 v3.36.20: كود عشوائي لكل بوت
'''),
    ('''    folder = ("demo_" if is_demo else "") + sym.split("-")[0].lower()
    base_folder, c = folder, 1
    while os.path.exists(os.path.join(ROOT, folder)):
        folder = f"{base_folder}_{c}"; c += 1
''', '''    folder = _new_bot_folder(("demo_" if is_demo else "") + sym.split("-")[0].lower())   # 🆔 v3.36.20: كود عشوائي لكل بوت
'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    if "base_folder, c = folder, 1" in s:
        print("❌ a deploy still names its folder after the coin only — nothing written"); sys.exit(1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
