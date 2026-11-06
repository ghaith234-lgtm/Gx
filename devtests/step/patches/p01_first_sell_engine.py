# 🪜 patch 01 (engine) — the first sell's distance apart from the distance between sells + no birth if a sell would lose
#   sp_k = bp × (1 + d1 + (k−1)·d)   d1 = step_first (buy → first sell) · d = step_sell (sell → sell, equal between every two)
#   no step_first ⇒ d1 = d ⇒ the old expression bp × (1 + k·d) itself (same floats, same slots, same orders as before)
#   birth refused (no order) while any sell would not cover the two fees: sp·(1−f)² ≤ bp — the dashboard's table refuses it first
#   python3 devtests/step/patches/p01_first_sell_engine.py ENGINE.py      (patches in place · every old text must be found once)
import sys

R = [
    # ── the docstring
    ("  • الجزء k يبيع بسعر: القاعدة × (1 + k·d)                          (d = step_sell — نفس المسافة بين الشراء وأول بيع وبين بيع وبيع)\n",
     "  • الجزء k يبيع بسعر: القاعدة × (1 + d1 + (k−1)·d)   (d1 = step_first — مسافة أول بيعة عن الشراء · d = step_sell — المسافة بين\n"
     "    بيعة وبيعة، متساوية بين كل بيعتين · بلا step_first ⇒ d1 = d ⇒ القاعدة × (1 + k·d) كما كان) · كل بيعة تربح بعد العمولتين وإلا ما يبدأ\n"),
    # ── first-time setup (no dashboard)
    ('        "step_sell": float(input("Sell spacing % (buy → first sell = sell → sell): ")) / 100,\n',
     '        "step_sell": float(input("Sell spacing % (sell → sell): ")) / 100,\n'
     '        "step_first": (lambda s: float(s) / 100 if s else None)(input("First sell distance % (buy → first sell, empty = the sell spacing): ").strip()),\n'),
    # ── step_layout
    ("def step_layout(P0, G, d, N, Q, floor, up, fee, lot=None, mn=None, max_down=400):\n",
     "def step_layout(P0, G, d, N, Q, floor, up, fee, lot=None, mn=None, max_down=400, d1=None):\n"),
    ("    مجموعة j: القاعدة bp = P0·(1+G)^j · الجزء k (1..N) يبيع بسعر sp = bp·(1 + k·d) · كميته q = (Q/N)/bp بالعملة (لتحت لخطوة المنصة)\n",
     "    مجموعة j: القاعدة bp = P0·(1+G)^j · الجزء k (1..N) يبيع بسعر sp = bp·(1 + d1 + (k−1)·d) (d1 = مسافة أول بيعة · بلاها d1 = d ⇒\n"
     "    sp = bp·(1 + k·d) بالضبط) · كميته q = (Q/N)/bp بالعملة (لتحت لخطوة المنصة)\n"),
    ("    P0, G, d, Q, floor, fee = float(P0), float(G), float(d), float(Q), float(floor or 0), float(fee or 0)\n"
     "    N, up = max(1, int(N)), max(0, int(up or 0))\n",
     "    P0, G, d, Q, floor, fee = float(P0), float(G), float(d), float(Q), float(floor or 0), float(fee or 0)\n"
     "    d1 = d if d1 is None or d1 == \"\" else float(d1)\n"
     "    N, up = max(1, int(N)), max(0, int(up or 0))\n"),
    ("    if P0 <= 0 or G <= 0 or d <= 0 or Q <= 0:\n        return out\n    m = 0\n",
     "    if P0 <= 0 or G <= 0 or d <= 0 or d1 <= 0 or Q <= 0:\n        return out\n    m = 0\n"),
    ("            sp = _sig(bp * (1.0 + k * d))\n",
     "            sp = _sig(bp * (1.0 + k * d)) if d1 == d else _sig(bp * (1.0 + d1 + (k - 1) * d))\n"),
    # ── birth: d1 saved with the settings (before any order) · passed to the layout
    ('               "f": float(config.get("fee_rate") or 0.001), "v": 1, "born": time.time()}\n',
     '               "f": float(config.get("fee_rate") or 0.001), "v": 1, "born": time.time()}\n'
     '        if config.get("step_first") not in (None, ""):          # 📈 مسافة أول بيعة (بلاها = مسافة البيع نفسها)\n'
     '            stp["d1"] = float(config.get("step_first"))\n'),
    ('    lay = step_layout(stp["P0"], stp["G"], stp["d"], stp["N"], stp["Q"], stp["floor"], stp["up"], stp["f"],\n'
     '                      INSTRUMENT_SPEC.get("lotSz"), INSTRUMENT_SPEC.get("minSz"))\n',
     '    lay = step_layout(stp["P0"], stp["G"], stp["d"], stp["N"], stp["Q"], stp["floor"], stp["up"], stp["f"],\n'
     '                      INSTRUMENT_SPEC.get("lotSz"), INSTRUMENT_SPEC.get("minSz"), d1=stp.get("d1"))\n'),
    # ── birth: no sell may lose (after the two fees) — else nothing is placed
    ('            log_trade_history(SYMBOL, "❌ [الشبكي المتدرج] الإعداد غير صالح (المبلغ أو المسافات صفر) — ما انوضع أي أمر")\n'
     '        return False\n'
     '    skipped = [r for r in lay if r.get("skip")]\n',
     '            log_trade_history(SYMBOL, "❌ [الشبكي المتدرج] الإعداد غير صالح (المبلغ أو المسافات صفر) — ما انوضع أي أمر")\n'
     '        return False\n'
     '    fr = float(stp["f"])\n'
     '    if any(not r.get("skip") and r["sp"] * (1.0 - fr) * (1.0 - fr) <= r["bp"] for r in lay):   # 💰 بيعة تخسر ⇒ ما يبدأ\n'
     '        if time.time() - float(state.get("last_bad_cfg_log") or 0) > 600:\n'
     '            state["last_bad_cfg_log"] = time.time()\n'
     '            log_trade_history(SYMBOL, f"❌ [الشبكي المتدرج] مسافة أول بيعة {round(float(stp.get(\'d1\') or stp[\'d\']) * 100, 4)}% "\n'
     '                                      f"لا تغطي العمولتين ({round(2 * fr * 100, 4)}%) — البيعة الأولى تخسر · لم يُوضع أي أمر")\n'
     '        return False\n'
     '    skipped = [r for r in lay if r.get("skip")]\n'),
    # ── birth log line: both distances when they differ
    ('             f"{stp[\'N\']} بيعات لكل شراء · مسافة البيع {round(stp[\'d\'] * 100, 4)}% · مسافة الشراء {round(stp[\'G\'] * 100, 4)}%"]\n',
     '             f"{stp[\'N\']} بيعات لكل شراء · "\n'
     '             + (f"مسافة أول بيعة {round(float(stp[\'d1\']) * 100, 4)}% · بين البيعات {round(stp[\'d\'] * 100, 4)}%"\n'
     '                if stp.get("d1") not in (None, stp["d"]) else f"مسافة البيع {round(stp[\'d\'] * 100, 4)}%")\n'
     '             + f" · مسافة الشراء {round(stp[\'G\'] * 100, 4)}%"]\n'),
]


def main(path):
    src = open(path, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        n = src.count(a)
        if n != 1:
            print(f"❌ replacement {i}: the old text is found {n} times (must be once) — nothing written:\n{a[:160]}")
            sys.exit(1)
        src = src.replace(a, b)
    compile(src, path, "exec")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(src)
    import os
    os.replace(tmp, path)
    print(f"✅ {len(R)} replacements · compiles · {path}")


if __name__ == "__main__":
    main(sys.argv[1])
