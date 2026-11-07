# 🪜🪟 patch 18 (engine · the window is strict, like ♾️ enforce_max_four)
#   The owner (7-11, live on OKX): «باع وفتح شراء ما مسح الي تحت وصار ٩ منشورات». A live order was pulled to memory only when
#   it was 2 places past the window (HYST = 2) ⇒ a sale that opens a buy at the top made 9 buys on OKX, the next one 10.
#   Now, like the grid: at most step_window orders per side on OKX at any time (live · partly filled · in flight) —
#     ① every live order outside the window goes to memory (rank ≥ W, was ≥ W + 2)
#     ② before a new order is sent the side is counted: full ⇒ the farthest live order goes to memory first (a partly filled one
#        stays — it counts — and the next farthest goes) · nothing could go ⇒ the new one waits (never W + 1 on OKX)
#   python3 devtests/step/patches/p18_window_strict.py ENGINE.py
import os, sys

R = [
    ('''HYST = 2                   # أمر حي يبقى لحد ما يصير أبعد من النافذة بخانتين (ما يرقص مع كل حركة)
''', ''),
    ('''def _window(state, cp, pend):
    """🪟 الأقرب للسعر على المنصة (step_window لكل جهة) والباقي بالذاكرة · الأرضية/السقف (📦 من اللوحة) يمنعون الجهة."""
''',
     '''def _room(state, S, side, W, rank, key):
    """🔢 أوامر هالجهة بالمنصة (حي · منفّذ جزئياً · بالطريق) أقل من النافذة ⇒ True · ممتلئة ⇒ الأبعد (أبعد من هالخانة) للذاكرة أول
    (المنفّذ جزئياً يبقى وينحسب ⇒ اللي بعده) · ما انشال شي ⇒ False (الجديد ينتظر — ما يصير W+1 بالمنصة أبداً)"""
    while True:
        on = [(k, s) for k, s in S.items() if s.get("side") == side and s.get("o")]
        if len(on) < W:
            return True
        far = sorted(((rank.get(k, 1 << 30), k, s) for k, s in on if _o_live(s) and rank.get(k, 1 << 30) > rank[key]),
                     key=lambda t: (-t[0], t[1]))
        for _r, k, s in far:
            _pull(state, k, s)
            if not s.get("o") or s.get("side") != side:  # انلغى (للذاكرة) · أو طلع منفّذ (قلب جهته) ⇒ صار مكان
                break
        else:
            return False


def _window(state, cp, pend):
    """🪟 الأقرب للسعر على المنصة — **بالضبط** step_window لكل جهة مثل ♾️ (أمر جديد قريب ⇒ الأبعد للذاكرة بنفس الدورة) والباقي
    بالذاكرة · المنفّذ جزئياً يبقى وينحسب · الأرضية/السقف (📦 من اللوحة) يمنعون الجهة."""
'''),
    ('''            if _o_live(s) and (k not in rank or rank[k] >= W + HYST):
                _pull(state, k, s)
''',
     '''            if _o_live(s) and (k not in rank or rank[k] >= W):
                _pull(state, k, s)
'''),
    ('''            if _crosses_own(S, side, px):
                continue                                 # 🚫 يلاقي أمر البوت نفسه بالجهة الثانية (نفس السعر/تداخل) ⇒ ينتظر
            if _send(state, k, s, cp):
''',
     '''            if _crosses_own(S, side, px):
                continue                                 # 🚫 يلاقي أمر البوت نفسه بالجهة الثانية (نفس السعر/تداخل) ⇒ ينتظر
            if not _room(state, S, side, W, rank, k):
                break                                    # 🔢 الجهة ممتلئة وما انشال شي (منفّذ جزئياً) ⇒ ينتظر
            if _send(state, k, s, cp):
'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written"); sys.exit(1)
        s = s.replace(a, b)
    if "HYST" in s:
        print("❌ HYST still used — nothing written"); sys.exit(1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
