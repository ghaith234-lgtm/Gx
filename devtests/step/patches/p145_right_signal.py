# p145 — v3.36.78 🎯 the settings that gave the right signal in check 18 (the owner 27-11: «افحص ولا تتقيد اهم شي يعطيني الاشارة الصحيحه»)
#   Check 18 (run 45939960032 · 38 coins · the 📲 gate decided on the 1st half ⇒ judged on the 2nd half, unseen):
#   · ⏱ the hour graded over the NEXT 4 HOURS (h 4): 📲 69.3% of 433 (the usual 45.6% · z +9.9) — the next hour alone was noise (36.2% vs 33.0%)
#   · 🕓 4 hours with 🤝 the market-state helpers and strict pairs: 📲 48.3% of 2,051 (the usual 37.7% · z +9.9) — today 43.2% vs 35.9%
#   · 📅 the day as it is: 📲 55.4% of 617 (the usual 40.2% · z +7.7) — helpers and longer horizons were worse there
#   · shuffled prices ⇒ at the usual · picking per group on the 1st half did worse on the 2nd ⇒ one rule per frame (GP_PF), not per group
#   Also: every call's path is shown and gates 📲 — for a direction group the average move after the call must be above zero (on ≥ 30 calls)
#   · the notice says the real horizon («خلال الساعات الأربع القادمة» for the hourly signal) and the path («متوسط الحركة · أسوأ عكس قبلها»)
#   · the helpers have plain names (no «S-…» letters reach the page or a notice)
#   python3 devtests/step/patches/p145_right_signal.py Holy_Dashboard.pyw
import sys, os

R = [
    ('GP_TPX = 1.0                                             # «الهدف قبل الوقف»: الهدف والوقف = المعتاد × √المدة\n',
     'GP_TPX = 1.0                                             # «الهدف قبل الوقف»: الهدف والوقف = المعتاد × √المدة\n'
     'GP_PF = {"1H": {"h": 4}, "4H": {"help": 1, "combo": 2}, "1D": {}}   # 🎯 v3.36.78: قواعد كل إطار — الفائزة بفحص 18 على النصف الذي لم تره\n'),
    # the build: each frame its own rule
    ('''        Db = F["BTC-USDT"][0]
        B = {Db["T"][i]: Db["C"][i] for i in range(Db["n"])}
        S = _safe(_gp_states, F, fr, cdb, default=None) if out["p"].get("help") else None     # 🤝 حال السوق (للمساعدين)
        out["f"][fr] = {"coin": gp_pack(gp_walk(F, "coin", fr, B=B, p=p, keep=[s for s in keep if s in F], codes=codes, S=S)),
                        "mkt": gp_pack(gp_walk({"BTC-USDT": F["BTC-USDT"]}, "mkt", fr, p=p, codes=codes, S=S))}''',
     '''        Db = F["BTC-USDT"][0]
        B = {Db["T"][i]: Db["C"][i] for i in range(Db["n"])}
        pf = dict(GP_PF.get(fr) or {}, **(p or {}))           # 🎯 v3.36.78: قاعدة الإطار (فحص 18) — وما يُمرَّر صراحةً يغلبها
        S = _safe(_gp_states, F, fr, cdb, default=None) if dict(GP_P, **pf).get("help") else None     # 🤝 حال السوق (للمساعدين)
        out["f"][fr] = {"coin": gp_pack(gp_walk(F, "coin", fr, B=B, p=pf, keep=[s for s in keep if s in F], codes=codes, S=S)),
                        "mkt": gp_pack(gp_walk({"BTC-USDT": F["BTC-USDT"]}, "mkt", fr, p=pf, codes=codes, S=S))}'''),
    # the live check: the rule each pack was built with
    ('''    p = dict(GP_P, **((G or {}).get("p") or {}), **(p or {}))
    codes = _gp_codes()
    out = {}
    for fr, F in (FF or {}).items():
        Gf = ((G or {}).get("f") or {}).get(fr) or {}
        S = (_safe(_gp_states, F, fr, cdb, default=None) or {}) if p.get("help") else None''',
     '''    p0 = p
    codes = _gp_codes()
    out = {}
    for fr, F in (FF or {}).items():
        Gf = ((G or {}).get("f") or {}).get(fr) or {}
        p = dict(GP_P)                                        # 🎯 قاعدة بناء هذا الإطار (ثم ما يُمرَّر صراحةً)
        for x_ in ((G or {}).get("p"), (Gf.get("coin") or {}).get("p") or GP_PF.get(fr), p0):
            p.update(x_ or {})
        S = (_safe(_gp_states, F, fr, cdb, default=None) or {}) if p.get("help") else None'''),
    # the gate: the group's own record AND (for a direction group) a positive average move after the call
    ('''def gp_proven(rec):
    """📲 للمجموعة على هذا الإطار؟ سجلها نفسه (ما كان سيصل) ≥ العادي + GP_SAY على 30 مرة فأكثر"""
    w, n, b = (list(rec or []) + [0, 0, 0.0])[:3]
    return n >= 30 and w / n >= b / n + GP_SAY''',
     '''def gp_proven(rec, px=None):
    """📲 للمجموعة على هذا الإطار؟ سجلها نفسه (ما كان سيصل) ≥ العادي + GP_SAY على 30 مرة فأكثر · 🎯 v3.36.78: ولمجاميع الجهة —
    متوسط الحركة بعد التنبؤ بجهته فوق الصفر (px من gp_pathst · على 30 تنبؤاً فأكثر)"""
    w, n, b = (list(rec or []) + [0, 0, 0.0])[:3]
    if px and len(px) >= 2 and px[0] >= 30 and px[1] <= 0:
        return False
    return n >= 30 and w / n >= b / n + GP_SAY


def gp_hz(fr, h=1):
    """المدة بكلام واضح: الإطار × عدد الشموع ⇒ «خلال الساعة القادمة» · «خلال الساعات الأربع القادمة» · «خلال اليوم القادم» …"""
    hrs = SG_SEC.get(fr, 3600) * max(1, int(h or 1)) // 3600
    return {1: "خلال الساعة القادمة", 2: "خلال الساعتين القادمتين", 3: "خلال الساعات الثلاث القادمة", 4: "خلال الساعات الأربع القادمة",
            8: "خلال الساعات الثماني القادمة", 12: "خلال الساعات الاثنتي عشرة القادمة", 24: "خلال اليوم القادم", 48: "خلال اليومين القادمين",
            72: "خلال الأيام الثلاثة القادمة", 168: "خلال الأسبوع القادم"}.get(hrs, f"خلال {hrs} ساعة القادمة" if hrs < 24 else f"خلال {hrs // 24} أيام قادمة")


def _gp_pxln(px):
    """سطر المسار: متوسط الحركة بعد المدة · أسوأ عكس قبلها (على 30 تنبؤاً فأكثر)"""
    return f"بعد المدة: متوسط الحركة {px[1]:+.2f}% · أسوأ عكس قبلها {px[2]:+.2f}% (من {px[0]:,})" if px and px[0] >= 30 else ""'''),
    ('''                X, Gg = GP_GROUPS[g], _gp_grp(G, fr, sec, g)
                ok = gp_proven(Gg.get("rec"))''',
     '''                X, Gg = GP_GROUPS[g], _gp_grp(G, fr, sec, g)
                px = Gg.get("px") if X["job"] == "dir" else None
                ok = gp_proven(Gg.get("rec"), px)
                hz = gp_hz(fr, ((((((G or {}).get("f") or {}).get(fr) or {}).get(sec) or {}).get("p") or GP_PF.get(fr) or {}).get("h") or 1))'''),
    ('''                    fi = GP_FRN[fr]
                    ln = (f"{X['ic']} {fi[0]} {X['say'][0 if s > 0 else 1]} {fi[2]}\\n"
                          f"{gp_name(best[0])} — صدق {round(100.0 * best[1] / n_)}% من {n_:,} مرة (العادي {round(100.0 * best[5])}%)")''',
     '''                    fi = GP_FRN[fr]
                    ln = (f"{X['ic']} {fi[0]} {X['say'][0 if s > 0 else 1]} {hz}\\n"
                          f"{gp_name(best[0])} — صدق {round(100.0 * best[1] / n_)}% من {n_:,} مرة (العادي {round(100.0 * best[5])}%)")
                    if _gp_pxln(px):
                        ln += "\\n" + _gp_pxln(px)'''),
    ('''                    out.setdefault(sym, []).append([fr, g, int(x[0]), gp_name(best[0]), best[1], best[1] + best[2], best[5], gp_proven(Gg.get("rec"))])''',
     '''                    out.setdefault(sym, []).append([fr, g, int(x[0]), gp_name(best[0]), best[1], best[1] + best[2], best[5],
                                                    gp_proven(Gg.get("rec"), Gg.get("px") if GP_GROUPS[g]["job"] == "dir" else None)])'''),
    ('''            "say": GP_SAY, "busy": {"phase": _SG.get("phase") or "", "pct": int(_SG.get("pct") or 0), "msg": _SG.get("msg") or ""}, "err": _SG.get("err") or ""}''',
     '''            "say": GP_SAY, "busy": {"phase": _SG.get("phase") or "", "pct": int(_SG.get("pct") or 0), "msg": _SG.get("msg") or ""}, "err": _SG.get("err") or "",
            "hz": {fr: gp_hz(fr, (((((G.get("f") or {}).get(fr) or {}).get("coin") or {}).get("p") or GP_PF.get(fr) or {}).get("h") or 1)) for fr in GP_FR},
            "helpers": {c: GP_NM[c] for c in ("S-comp", "S-brd", "S-btc", "S-vol")}}'''),
    # the helpers' plain names (they appear inside a combo «member + helper»)
    ("    'P-fund': 'رسوم التمويل في العقود',\n",
     "    'P-fund': 'رسوم التمويل في العقود',\n    'S-comp': 'بوصلة السوق بالجهة نفسها',\n    'S-brd': 'أغلب العملات بالجهة نفسها',\n"
     "    'S-btc': 'اتجاه البيتكوين بالجهة نفسها',\n    'S-vol': 'حجم كبير بالجهة نفسها',\n"),
    ('            "names": {c: gp_name(c) for c in codes}, "plain": sg_plain_all(), "mine": sg_coins(cfg), "lv": {g: cfg["alv"].get("g_" + g) for g in GP_GROUPS},\n',
     '            "names": dict({c: gp_name(c) for c in codes}, **{c: GP_NM[c] for c in ("S-comp", "S-brd", "S-btc", "S-vol")}), "plain": sg_plain_all(), "mine": sg_coins(cfg),\n'
     '            "lv": {g: cfg["alv"].get("g_" + g) for g in GP_GROUPS},\n'),
    ('APP_VERSION = "3.36.77"', 'APP_VERSION = "3.36.78"'),
    # 📋 the card: the horizon and the path
    ('''  const [r,own]=gpRec(G,coin),p=r[1]?Math.round(100*r[0]/r[1]):null,b=r[1]?Math.round(100*r[2]/r[1]):null,ok=r[1]>=30&&r[0]/r[1]>=r[2]/r[1]+(+GPV.say||0.03);''',
     '''  const [r,own]=gpRec(G,coin),p=r[1]?Math.round(100*r[0]/r[1]):null,b=r[1]?Math.round(100*r[2]/r[1]):null,X_=(GPV.groups||{})[G.__g]||{},px=X_.job==='dir'?(G.px||[0]):[0];
  const ok=r[1]>=30&&r[0]/r[1]>=r[2]/r[1]+(+GPV.say||0.03)&&!(px[0]>=30&&px[1]<=0);'''),
    ('''    <div class="gp-fh">${F[0]} ${gEsc(F[1])}</div><div class="gp-p">${p!=null?`<b>${p}%</b>`:'—'}${ok?' ✅':''}</div><small>${r[1]?`من ${r[1].toLocaleString('en-US')} · العادي ${b}%`:'لا تنبؤات بعد'}</small></div>`}''',
     '''    <div class="gp-fh">${F[0]} ${gEsc(F[1])}</div><div class="gp-p">${p!=null?`<b>${p}%</b>`:'—'}${ok?' ✅':''}</div><small>${r[1]?`من ${r[1].toLocaleString('en-US')} · العادي ${b}%`:'لا تنبؤات بعد'}</small>
    ${px[0]>=30?`<small class="gp-px" title="بعد المدة ${gEsc(((GPV.hz||{})[fr])||'')}: متوسط الحركة بجهة التنبؤ · أسوأ عكس قبلها">${px[1]>=0?'+':''}${(+px[1]).toFixed(2)}% · عكس ${(+px[2]).toFixed(2)}%</small>`:''}</div>`}'''),
    ("function gpG(fr,sec,g){return (((((GPV&&GPV.f)||{})[fr]||{})[sec]||{}).g||{})[g]||null}",
     "function gpG(fr,sec,g){const x=(((((GPV&&GPV.f)||{})[fr]||{})[sec]||{}).g||{})[g]||null;if(x)x.__g=g;return x}"),
    ('''    <div class="ind-sub">${X.mem.length} مؤشراً في هذه المجموعة + التوليفات (كل اثنين منها انطلقا معاً بالجهة نفسها) · البطل:''',
     '''    <div class="ind-sub">⏳ يُحكم ${gEsc(((GPV.hz||{})[GPF])||'')} · ${X.mem.length} مؤشراً في هذه المجموعة + التوليفات (كل اثنين منها انطلقا معاً بالجهة نفسها${((((GPV.f||{})[GPF]||{}).coin||{}).p||{}).help?' · ومع 🤝 حال السوق: البوصلة · أغلب العملات · اتجاه البيتكوين · الحجم':''}) · البطل:'''),
    ('''    <div>• <b>العادي</b>: ما يصيبه تنبؤ عشوائي بالجهات نفسها على الشموع نفسها — يزيل أثر صعود السوق الطويل. النسبة في الخانة = صدق ما كان سيصل من المجموعة (لا أفضل عضو وحده).</div>''',
     '''    <div>• <b>العادي</b>: ما يصيبه تنبؤ عشوائي بالجهات نفسها على الشموع نفسها — يزيل أثر صعود السوق الطويل. النسبة في الخانة = صدق ما كان سيصل من المجموعة (لا أفضل عضو وحده).</div>
    <div>• <b>المدة</b>: إشارة الساعة تُحكم على الساعات الأربع التالية · الأربع ساعات على الأربع التالية ومعها 🤝 حال السوق · اليوم على اليوم التالي — هكذا صدقت أكثر على تاريخ لم تره (فحص 18) · تحت النسبة: <b>متوسط الحركة</b> بعد المدة بجهة التنبؤ و<b>أسوأ عكس</b> قبلها.</div>'''),
    (".gp-rc{color:var(--mut2);font-weight:400}", ".gp-rc{color:var(--mut2);font-weight:400}.gp-px{display:block;color:var(--mut2);font-size:10px}"),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    try:
        from pyflakes.api import check as _pf
        from pyflakes.reporter import Reporter as _Rp
        import io as _io
        _o = _io.StringIO()
        _pf(s, p, _Rp(_o, _o))
        und = [ln for ln in _o.getvalue().splitlines() if "undefined name" in ln]
        if und:
            print("❌ undefined:", und[:5]); sys.exit(1)
    except ImportError:
        pass
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · the rule per frame (1H over 4 hours · 4H with helpers and strict pairs · 1D as is) · the path in the gate, notice and card · v3.36.78 · {p}")
