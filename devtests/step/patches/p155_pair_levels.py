# p155 — v3.36.80 🔀 «شبكة عملتين» · the owner 27-11: «صلحه التحديد ضمن الاعداد الاعلى والاسفل ، واذا ما يوجد عملات يتوقف»
#   ① the form: «⬆️ عدد مستويات البيع فوق» and «⬇️ عدد مستويات الشراء تحت» (the owner's most) · the amounts become optional
#   ② the calculator builds within those counts from the coins: above — until the coin amount ends or a level falls under
#      1.5 × OKX's minimum (it stops there: no refusal, the rest stays in the wallet) · below — until the main amount ends ·
#      the lower levels are never squeezed to zero by the upper ones without a note
#   ③ the deploy: what the free wallet lacks ⇒ the levels stop at the last one it covers (was: refused) · none at all ⇒ refused
#   ④ ♻️ the archive re-deploys with its counts · 📖 the tutorial: the counts + «is there a loss?»
#   python3 devtests/step/patches/p155_pair_levels.py Holy_Dashboard.pyw
import os, sys

R = [
    # ── ① the form's numbers: empty = no limit · the counts
    ('''    try:
        g = float(data.get("step_pct") or 0) / 100.0
        mv = float(data.get("main_value") or 0)
        am = float(data.get("main_amount") or 0)
        ao = float(data.get("other_amount") or 0)
        r0 = float(data.get("forced_ratio") or 0)
    except Exception:
        return None, "تأكد من الأرقام (الخطوة · كمية كل شراء · الكميات)"
    if not all(math.isfinite(x) for x in (g, mv, am, ao, r0)):          # 🔢 «nan» / «inf» يمرّ من كل مقارنة ⇒ يُرفض هنا
        return None, "تأكد من الأرقام (الخطوة · كمية كل شراء · الكميات)"
    if g <= 0 or mv <= 0:
        return None, "الخطوة وكمية كل شراء يجب أن تكونا أكبر من صفر"
    if am < 0 or ao < 0 or r0 < 0:
        return None, "الكميات ونسبة البداية لا تكون سالبة"
    if am <= 0 and ao <= 0:
        return None, "ضع كمية من العملة الرئيسية (للشراءات تحت) أو من الثانية (للبيعات فوق) أو كليهما"
    pt = str(data.get("profit_to") or "main")
    return {"main": mn, "other": oth, "sym": f"{oth}-{mn}", "g": g, "mv": mv, "am": am, "ao": ao, "r0": r0,
            "pt": pt if pt in ("main", "other", "half") else "main"}, None''',
     '''    def _opt(k):                                     # 🔀 v3.36.80: حقل فارغ = بلا حد (None)
        x = data.get(k)
        return None if x is None or str(x).strip() == "" else float(x)
    try:
        g = float(data.get("step_pct") or 0) / 100.0
        mv = float(data.get("main_value") or 0)
        am, ao = _opt("main_amount"), _opt("other_amount")
        upx, dnx = _opt("up_max"), _opt("dn_max")
        r0 = float(data.get("forced_ratio") or 0)
    except Exception:
        return None, "تأكد من الأرقام (الخطوة · كمية كل شراء · الكميات · عدد المستويات)"
    if not all(math.isfinite(x) for x in (g, mv, r0) + tuple(v for v in (am, ao, upx, dnx) if v is not None)):   # 🔢 «nan» / «inf» ⇒ يُرفض هنا
        return None, "تأكد من الأرقام (الخطوة · كمية كل شراء · الكميات · عدد المستويات)"
    if g <= 0 or mv <= 0:
        return None, "الخطوة وكمية كل شراء يجب أن تكونا أكبر من صفر"
    if r0 < 0 or any(v is not None and v < 0 for v in (am, ao, upx, dnx)):
        return None, "الكميات وعدد المستويات ونسبة البداية لا تكون سالبة"
    if any(v is not None and (v != int(v) or v > PAIR_MAX_LV) for v in (upx, dnx)):
        return None, f"عدد المستويات عدد صحيح من 0 إلى {PAIR_MAX_LV}"
    if not (am or dnx) and not (ao or upx):
        return None, "ضع كمية أو عدد مستويات للشراءات تحت (العملة الرئيسية) أو للبيعات فوق (العملة الثانية) أو كليهما"
    pt = str(data.get("profit_to") or "main")
    return {"main": mn, "other": oth, "sym": f"{oth}-{mn}", "g": g, "mv": mv, "am": am, "ao": ao, "r0": r0,
            "upx": None if upx is None else int(upx), "dnx": None if dnx is None else int(dnx),
            "pt": pt if pt in ("main", "other", "half") else "main"}, None'''),
    # ── ② the calculator: within the counts · from the coins · stops at OKX's minimum
    ('''    g, mv = a["g"], a["mv"]
    dn = int(math.floor(a["am"] / mv + 1e-9))
    up, need_o = 0, 0.0
    while up < PAIR_MAX_LV:
        q = mv / (r0 * (1 + g) ** up)
        if need_o + q > a["ao"] + 1e-12:
            break
        need_o += q
        up += 1
    dn = max(0, min(dn, PAIR_MAX_LV - up))
    so, sm = _acc_spec(lo_), _acc_spec(lm_)
    cf = (1 + g) * (1 - PAIR_FEE) ** 4 * (1 - PAIR_SPREAD) ** 4      # العمولات الأربع + فرق السعر بكل أمر''',
     '''    g, mv = a["g"], a["mv"]
    so, sm = _acc_spec(lo_), _acc_spec(lm_)
    am, ao, upx, dnx = a["am"], a["ao"], a["upx"], a["dnx"]
    O_, M_ = a["other"], a["main"]
    mn_o = float(so.get("minSz") or 0)
    notes = []
    # ⬆️ v3.36.80: فوق ضمن عدد المالك · بقدر كمية الثانية · ويتوقف حين يصغر المستوى عن 1.5 × أدنى حجم بالمنصة (لا رفض)
    up_lim = 0 if (upx is None and ao is None) else (PAIR_MAX_LV if upx is None else upx)
    up, need_o, up_why = 0, 0.0, ""
    while up < up_lim:
        q = mv / (r0 * (1 + g) ** up)
        if mn_o > 0 and q < 1.5 * mn_o - 1e-15:
            up_why = "min"
            break
        if ao is not None and need_o + q > ao + 1e-12:
            up_why = "coins"
            break
        need_o += q
        up += 1
    # ⬇️ تحت ضمن عدد المالك · بقدر كمية الرئيسية
    dn_c = None if am is None else int(math.floor(am / mv + 1e-9))
    dn = (dn_c or 0) if dnx is None else (dnx if dn_c is None else min(dnx, dn_c))
    dn_why = "coins" if (dnx is not None and dn_c is not None and dn_c < dnx) else ""
    if dn + up > PAIR_MAX_LV:
        dn, dn_why = max(0, PAIR_MAX_LV - up), "max"
    if up_why == "min" and up == 0:
        notes.append(f"⬆️ كمية مستوى البيع الأول أقل من 1.5 × أدنى حجم في المنصة ({mn_o:g} {O_}) — لا بيعات فوق (كبّر كمية كل شراء)")
    elif up_why == "min" and (upx is not None or (ao is not None and ao - need_o > 1e-12)):
        notes.append(f"⬆️ بعد المستوى {up}" + (f" من {upx}" if upx is not None and upx > up else "")
                     + f" تصبح كمية المستوى أقل من 1.5 × أدنى حجم في المنصة ({mn_o:g} {O_}) — يتوقف البوت عنده"
                     + (f"، ويبقى الباقي من {O_} في محفظتك" if ao is not None else ""))
    elif up_why == "coins" and upx is not None:
        notes.append(f"⬆️ كمية {O_} تكفي {up} مستوى فوق من {upx} — يتوقف البوت عند المستوى {up}")
    if dn_why == "coins":
        notes.append(f"⬇️ كمية {M_} تكفي {dn} مستوى تحت من {dnx} — يتوقف البوت عند المستوى {dn}")
    elif dn_why == "max":
        notes.append(f"⬇️ مجموع المستويات {PAIR_MAX_LV} على الأكثر — بقي للشراءات تحت {dn} مستوى")
    if (am is None and dn > 0) or (ao is None and up > 0):
        notes.append("💼 ما لم تحدّد كميته يُؤخذ من الحر في محفظتك عند النشر — وإن لم يكفِ يتوقف البوت عند آخر مستوى يكفيه")
    cf = (1 + g) * (1 - PAIR_FEE) ** 4 * (1 - PAIR_SPREAD) ** 4      # العمولات الأربع + فرق السعر بكل أمر'''),
    ('''    q_top = mv / (r0 * (1 + g) ** max(0, up - 1)) if up else mv / r0      # أصغر كمية ثانية بالأمر (أعلى مستوى)
    if so.get("minSz") and q_top < 1.5 * float(so["minSz"]):
        errs.append(f"كمية {a['other']} بأعلى مستوى {q_top:.8g} أقل من 1.5 × أدنى حجم بالمنصة ({float(so['minSz']):g} {a['other']}) — كبّر كمية كل شراء")
''', ''),
    ('''            "main_left": round(max(0.0, a["am"] - dn * mv), 10), "other_left": round(max(0.0, a["ao"] - need_o), 12),''',
     '''            "main_left": round(max(0.0, am - dn * mv), 10) if am is not None else 0.0,
            "other_left": round(max(0.0, ao - need_o), 12) if ao is not None else 0.0,
            "notes": notes, "up_max": upx, "dn_max": dnx,'''),
    # ── ③ the deploy: what the free wallet lacks ⇒ the levels stop where it ends
    ('''    for ccy, need, what in ((a["main"], P["main_need"], "الشراءات تحت"), (a["other"], P["other_need"], "البيعات فوق")):
        if need <= 0:
            continue
        fr, cl = _pair_free(keys, ccy, need)
        if fr is None:
            return {"ok": False, "msg": cl}
        if fr + 1e-12 < need:
            return {"ok": False, "msg": f"⛔ {what} تحتاج {need:.8g} {ccy} — الحر بمحفظتك {fr:.8g} (بعد ما تحتاجه بوتاتك الأخرى {cl:.8g}) · قلّل الكمية"}
''',
     '''    short = {}
    for ccy, need, key in ((a["main"], P["main_need"], "main_amount"), (a["other"], P["other_need"], "other_amount")):
        if need <= 0:
            continue
        fr, cl = _pair_free(keys, ccy, need)
        if fr is None:
            return {"ok": False, "msg": cl}
        if fr + 1e-12 < need:
            short[key] = (fr, cl, need, ccy)
    capped = []
    if short:                                          # 🔀 v3.36.80: «اذا ما يوجد عملات يتوقف» — يتوقف عند آخر مستوى يكفيه الحر (كان: يرفض)
        d2 = dict(data, forced_ratio=P["r0"])
        for key, (fr, cl, need, ccy) in short.items():
            d2[key] = max(0.0, fr)
        P2 = pair_plan(d2, px=P["px"])
        if not P2.get("ok") or P2["err"] or P2["dn"] + P2["up"] == 0:
            fr, cl, need, ccy = next(iter(short.values()))
            return {"ok": False, "msg": f"⛔ الحر بمحفظتك من {ccy} {fr:.8g} (بعد ما تحتاجه بوتاتك الأخرى {cl:.8g}) لا يكفي مستوى واحداً — المطلوب {need:.8g}"}
        for key, (fr, cl, need, ccy) in short.items():
            side, n0, n1 = ("تحت", P["dn"], P2["dn"]) if key == "main_amount" else ("فوق", P["up"], P2["up"])
            capped.append(f"الحر من {ccy} ({fr:.8g}) يكفي {n1} مستوى {side} من {n0}")
        P = P2
'''),
    ('''    return {"ok": ok, "msg": (f"🔀 انتشرت «شبكة عملتين» وانطلقت — {a['other']}/{a['main']} · البداية {float(P['r0']):.8g}") if ok else msg, "dir": folder}''',
     '''    return {"ok": ok, "msg": (f"🔀 انتشرت «شبكة عملتين» وانطلقت — {a['other']}/{a['main']} · البداية {float(P['r0']):.8g} · {P['dn']} تحت · {P['up']} فوق"
                              + (" · ⚠️ " + " · ".join(capped) + " — يتوقف البوت عند آخر مستوى يكفيه" if capped else "")) if ok else msg,
            "dir": folder, "dn": P["dn"], "up": P["up"]}'''),
    # ── ④ ♻️ the archive: the same counts
    ('''        P.update(main=_m, other=_o, step_pct=round(_g * 100, 6), main_value=_mv, main_amount=round(_mv * int(n("down_levels")), 10),
                 other_amount=float(f"{_ao:.8g}") if _ao > 0 else "", profit_to=str(c.get("profit_to") or "main"))''',
     '''        P.update(main=_m, other=_o, step_pct=round(_g * 100, 6), main_value=_mv, main_amount=round(_mv * int(n("down_levels")), 10),
                 other_amount=float(f"{_ao:.8g}") if _ao > 0 else "", profit_to=str(c.get("profit_to") or "main"),
                 up_max=int(n("up_levels")), dn_max=int(n("down_levels")))      # 🔀 v3.36.80: العدد نفسه'''),
    # ── the form
    ('''  <p class="sthelp">عملة <b>رئيسية</b> (مثل XRP) تؤدي دور الدولار، وعملة <b>ثانية</b> (مثل SOL) تُتداول على سعرها محسوباً بالرئيسية — كم XRP يساوي SOL واحد. كل شراء تحت يدفع <b>الكمية نفسها من الرئيسية</b>، وبيعته فوقه بالخطوة نفسها تعيدها <b>مع الربح</b>. البيعات فوق نسبة البداية من عملاتك الثانية الموجودة في المحفظة — لا يُشترى شيء عند النشر. التحويل عبر الدولار لحظي بأمرين فوريين، ولا تبقى أوامر على المنصة: البوت يراقب النسبة كل ثانيتين.</p>''',
     '''  <p class="sthelp">عملة <b>رئيسية</b> (مثل XRP) تؤدي دور الدولار، وعملة <b>ثانية</b> (مثل SOL) تُتداول على سعرها محسوباً بالرئيسية — كم XRP يساوي SOL واحد. كل شراء تحت يدفع <b>الكمية نفسها من الرئيسية</b>، وبيعته فوقه بالخطوة نفسها تعيدها <b>مع الربح</b>. البيعات فوق نسبة البداية من عملاتك الثانية الموجودة في المحفظة — لا يُشترى شيء عند النشر. التحويل عبر الدولار لحظي بأمرين فوريين، ولا تبقى أوامر على المنصة: البوت يراقب النسبة كل ثانيتين.</p>
  <p class="sthelp">🔢 حدّد <b>عدد المستويات</b> فوق وتحت (أو الكميات): يبني البوت ضمن هذا العدد من عملاتك، وإن لم تكفِ العملة أو صغر المستوى عن أدنى حجم في المنصة <b>يتوقف عند آخر مستوى يكفيه</b>. عدد المستويات تحت هو أقصى ما تضعه من الرئيسية في الثانية إن هبطت ولم تعد.</p>'''),
    ('''    <div class="fld"><label title="كمية الرئيسية التي تخصّصها للشراءات تحت نسبة البداية — عدد المستويات = الكمية ÷ كمية كل شراء">⬇️ كمية الرئيسية للشراءات تحت</label><input id="pa_am" class="num" value="${v('main_amount','')}" oninput="paPreview()"></div>
    <div class="fld"><label title="كمية الثانية من محفظتك للبيعات فوق نسبة البداية — كل مستوى يبيع ما يساوي كمية شراء بنسبته">⬆️ كمية الثانية للبيعات فوق (من محفظتك)</label><input id="pa_ao" class="num" value="${v('other_amount','')}" oninput="paPreview()"></div>''',
     '''    <div class="fld"><label title="أقصى عدد لمستويات الشراء تحت نسبة البداية — فارغ = بقدر الكمية · إن لم تكفِ الرئيسية يتوقف البوت عند آخر مستوى تكفيه">⬇️ عدد مستويات الشراء تحت (الأقصى)</label><input id="pa_dn" class="num" placeholder="بقدر الكمية" value="${v('dn_max','')}" oninput="paPreview()"></div>
    <div class="fld"><label title="أقصى عدد لمستويات البيع فوق نسبة البداية — فارغ = بقدر الكمية · إن لم تكفِ الثانية أو صغر المستوى عن أدنى حجم يتوقف البوت عند آخر مستوى يكفيه">⬆️ عدد مستويات البيع فوق (الأقصى)</label><input id="pa_up" class="num" placeholder="بقدر الكمية" value="${v('up_max','')}" oninput="paPreview()"></div>
    <div class="fld"><label title="كمية الرئيسية للشراءات تحت نسبة البداية — فارغ مع عدد المستويات = ما تحتاجه المستويات من الحر في محفظتك">⬇️ كمية الرئيسية للشراءات تحت (اختياري)</label><input id="pa_am" class="num" value="${v('main_amount','')}" oninput="paPreview()"></div>
    <div class="fld"><label title="كمية الثانية من محفظتك للبيعات فوق نسبة البداية — كل مستوى يبيع ما يساوي كمية شراء بنسبته · فارغ مع عدد المستويات = ما تحتاجه من الحر في محفظتك">⬆️ كمية الثانية للبيعات فوق (اختياري)</label><input id="pa_ao" class="num" value="${v('other_amount','')}" oninput="paPreview()"></div>'''),
    ('''  <div class="sthelp" id="pa_dnote" style="display:none">🧪 الديمو: المحفظة الوهمية = الكميتان أعلاه (الرئيسية للشراءات تحت · الثانية للبيعات فوق) — لا حاجة إلى محفظة OKX، ولا إشعارات، ولا يدخل في أي مجموع.</div>''',
     '''  <div class="sthelp" id="pa_dnote" style="display:none">🧪 الديمو: المحفظة الوهمية = الكميتان أعلاه، أو ما تحتاجه المستويات إن تُركتا فارغتين (الرئيسية للشراءات تحت · الثانية للبيعات فوق) — لا حاجة إلى محفظة OKX، ولا إشعارات، ولا يدخل في أي مجموع.</div>'''),
    ('''    other_amount:g('pa_ao'),forced_ratio:g('pa_r0'),profit_to:g('pa_pt')||'main',wallet:g('pa_wallet'),auto:!!($('#pa_auto')||{}).checked,''',
     '''    other_amount:g('pa_ao'),up_max:g('pa_up'),dn_max:g('pa_dn'),forced_ratio:g('pa_r0'),profit_to:g('pa_pt')||'main',wallet:g('pa_wallet'),auto:!!($('#pa_auto')||{}).checked,'''),
    ('''  (P.err||[]).forEach(e=>h+=`<div class="sterr">⛔ ${gEsc(e)}</div>`);
  h+=`<div class="stsum">
   <span>⚖️ الآن: 1 ${O} = <b dir="ltr">${stN(P.r_now)}</b> ${M}</span>''',
     '''  (P.err||[]).forEach(e=>h+=`<div class="sterr">⛔ ${gEsc(e)}</div>`);
  (P.notes||[]).forEach(t=>h+=`<div class="sthelp pa_note">${gEsc(t)}</div>`);      // 🔀 v3.36.80: أين يتوقف ولماذا
  h+=`<div class="stsum">
   <span>⚖️ الآن: 1 ${O} = <b dir="ltr">${stN(P.r_now)}</b> ${M}</span>'''),
    # ── 📖 the tutorial
    ('''           ['فوق البداية','مستويات تبيع من عملاتك الثانية الموجودة في المحفظة كأنها اشتُريت بنسبة مستواها.'],''',
     '''           ['فوق البداية','مستويات تبيع من عملاتك الثانية الموجودة في المحفظة كأنها اشتُريت بنسبة مستواها.'],
           ['عدد المستويات','تحدد أقصى عدد للمستويات فوق وتحت؛ يبني البوت ضمنه من عملاتك، وإن لم تكفِ العملة أو صغر المستوى عن أدنى حجم في المنصة يتوقف عند آخر مستوى يكفيه.'],'''),
    ('''         ['هل يحمي من نزول السوق كله؟','لا — العملتان تتحركان مع السوق. البوت يزيد عدد العملة الرئيسية من تذبذب النسبة بين العملتين.'],''',
     '''         ['هل يحمي من نزول السوق كله؟','لا — العملتان تتحركان مع السوق. البوت يزيد عدد العملة الرئيسية من تذبذب النسبة بين العملتين.'],
         ['هل فيه خسارة؟','لا يبيع بخسارة أبداً. الخسارة الممكنة على الورق فقط: إن نزلت الثانية مقابل الرئيسية ولم تعد، يبقى معك منها أكثر بقيمة أقل — وعدد المستويات تحت يحدّ أقصاها. وإن صعدت ولم تعد، يكون قد باعها في الطريق بربح فيزيد عدد الرئيسية، لكن يفوتك جزء من صعودها.'],'''),
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
    print(f"✅ {len(R)} replacements · 🔀 the pair levels: within the owner's counts · stop where the coins or OKX's minimum end · {p}")
