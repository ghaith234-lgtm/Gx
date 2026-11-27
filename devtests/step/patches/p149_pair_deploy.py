# p149 — v3.36.79 🔀 «شبكة عملتين» · ④ the calculator and the deploy (server)
#   The owner 27-11: «الكمية راح تنحسب بالxrp مثل انفنتي العادي ينحسب بالدولار» · «واحد لكل عملة · يستعمل الي موجود بالمحفظة ·
#   يحسبها مثل الحاسبة · كله للxrp (او حسب العملة الرئيسية)» · «والمهم تحسب كل العمولة والنسبة بين الشراء والبيع».
#   · `pair_plan` (/api/pair_plan — calculation only): the ratio now (the two USDT prices) · the levels by THE ENGINE'S OWN formula
#     (bp = R0×(1+g)^j · sp = bp×(1+g)) · buys below = how many orders the main coin covers · sells above = how many levels the other coin
#     covers («كأنها اشتُريت») · the cycle profit after the FOUR fees (two swaps × two orders) in the main coin and ≈ $ · the smallest step
#     that still profits at the worst price the cap allows · OKX's minimums on both coins · refuses anything that would lose
#   · `deploy_pair` (/api/deploy_pair): the same refusals · one bot per pair · the wallet's FREE coins (OKX free − what your other bots on
#     the same wallet need) must cover both sides · nothing is bought at the deploy (it uses the coins already in the wallet) ·
#     the start ratio is fixed in the config (the table = the engine) · the engine written · launched · a Telegram line
#   python3 devtests/step/patches/p149_pair_deploy.py Holy_Dashboard.pyw
import os, sys

NEW = r'''
# ═══════════ 🔀 v3.36.79: «شبكة عملتين» — الحاسبة والنشر ═══════════
PAIR_MAX_LV = 2000
PAIR_FEE = 0.001                  # كل رجل أمر فوري (آخذ) · كل تبديل أمران · كل دورة أربعة
PAIR_CAP, PAIR_CAP_B = 0.002, 0.0005
PAIR_SPREAD = 0.0002              # فرق السعر لكل أمر (تقدير محافظ بربح الدورة المعروض — المحرك يحسب من التنفيذ نفسه)


def _pair_args(data):
    """قراءة نموذج «شبكة عملتين» (النسب المئوية ⇒ كسور) · (args, None) أو (None, سبب الرفض)"""
    mn = str(data.get("main") or "XRP").strip().upper()
    oth = str(data.get("other") or "").strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{2,12}", mn) or not re.fullmatch(r"[A-Z0-9]{2,12}", oth):
        return None, "اكتب رمزي العملتين (الرئيسية والثانية) مثل XRP و SOL"
    if mn == oth:
        return None, "العملة الرئيسية والثانية يجب أن تكونا مختلفتين"
    if "USDT" in (mn, oth):
        return None, "الدولار وسيط بين العملتين فقط — اختر عملتين غيره"
    try:
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
            "pt": pt if pt in ("main", "other", "half") else "main"}, None


def _pair_min_step(fee=PAIR_FEE, cap=PAIR_CAP):
    """أقل خطوة تربح بأسوأ سعر يسمح به السقف بعد العمولات الأربع"""
    return 1.0 / ((1 - fee) ** 4 * ((1 - cap) / (1 + cap)) ** 2) - 1.0


def pair_plan(data, px=None, _deploy=False):
    """🔀 الحاسبة (حساب فقط — نفس معادلة المحرك `_born`): المستويات · ربح الدورة صافياً · ما يحتاجه من كل عملة · الرفض"""
    a, err = _pair_args(data)
    if err:
        return {"ok": False, "msg": err}
    lo_, lm_ = f"{a['other']}-USDT", f"{a['main']}-USDT"
    po, pm = (px or {}).get("other") or float(_acc_price(lo_) or 0), (px or {}).get("main") or float(_acc_price(lm_) or 0)
    if not (po > 0 and pm > 0):
        return {"ok": False, "msg": f"تعذّر جلب سعر {lo_} أو {lm_} من المنصة — تأكد من الرمزين وأعد المحاولة"}
    r_now = po / pm
    r0 = a["r0"] or r_now
    g, mv = a["g"], a["mv"]
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
    cf = (1 + g) * (1 - PAIR_FEE) ** 4 * (1 - PAIR_SPREAD) ** 4      # العمولات الأربع + فرق السعر بكل أمر
    ms = _pair_min_step()
    errs = []
    if dn + up == 0:
        errs.append("الكميات لا تكفي مستوى واحداً — كبّر الكمية أو صغّر كمية كل شراء")
    if g <= ms + 1e-12:
        errs.append(f"الخطوة {g * 100:.2f}% لا تغطي العمولات الأربع وسقف السعر — أقل خطوة تربح ≈ {ms * 100:.2f}%")
    if sm.get("minSz") and mv < 1.5 * float(sm["minSz"]):
        errs.append(f"كمية كل شراء {mv:g} {a['main']} أقل من 1.5 × أدنى حجم بالمنصة ({float(sm['minSz']):g} {a['main']})")
    q_top = mv / (r0 * (1 + g) ** max(0, up - 1)) if up else mv / r0      # أصغر كمية ثانية بالأمر (أعلى مستوى)
    if so.get("minSz") and q_top < 1.5 * float(so["minSz"]):
        errs.append(f"كمية {a['other']} بأعلى مستوى {q_top:.8g} أقل من 1.5 × أدنى حجم بالمنصة ({float(so['minSz']):g} {a['other']}) — كبّر كمية كل شراء")
    if mv * pm < 2.0:
        errs.append(f"قيمة كل أمر ≈ {mv * pm:.2f}$ — أقل أمر 2$")
    rows = []
    for j in range(up - 1, -dn - 1, -1):
        bp = r0 * (1 + g) ** j
        rows.append({"j": j, "bp": bp, "sp": bp * (1 + g), "side": "sell" if j >= 0 else "buy",
                     "q": (mv / bp) if j >= 0 else None, "main": mv})
    return {"ok": True, "err": errs, "a": {k: a[k] for k in ("main", "other", "sym", "g", "mv", "pt")}, "r_now": r_now, "r0": r0,
            "dn": dn, "up": up, "main_need": round(dn * mv, 10), "other_need": round(need_o, 12),
            "main_left": round(max(0.0, a["am"] - dn * mv), 10), "other_left": round(max(0.0, a["ao"] - need_o), 12),
            "px": {"main": pm, "other": po}, "lo": r0 * (1 + g) ** (-dn), "hi": r0 * (1 + g) ** up,
            "cycle_main": mv * (cf - 1), "cycle_usd": mv * (cf - 1) * pm, "fee": PAIR_FEE, "min_step": ms, "usd_order": mv * pm,
            "worst_main": mv * ((1 + g) * (1 - PAIR_FEE) ** 4 * ((1 - PAIR_CAP) / (1 + PAIR_CAP)) ** 2 - 1),
            "spec": {"main": sm, "other": so}, "rows": rows[:400], "n_rows": len(rows)}


def _pair_taken(sym):
    """🔀 واحد لكل زوج (المالك: «واحد لكل عملة»): مجلد «شبكة عملتين» موجود على هالزوج · None = لا"""
    for b in bot_dirs().values():
        try:
            if str((b.get("cfg") or {}).get("bot_type") or "") == "grid_pair" and str(b.get("symbol") or "").upper() == str(sym).upper() \
                    and not (b.get("cfg") or {}).get("is_demo"):
                return os.path.basename(str(b["dir"]).rstrip("/\\"))
        except Exception:
            continue
    return None


def _pair_free(keys, ccy, need):
    """الحر من عملة بالمحفظة = المتاح بـOKX − ما تحتاجه بوتاتك الأخرى بنفس المحفظة · (الحر, المحجوز للآخرين) أو (None, سبب)"""
    r = _okx_get(f"/api/v5/account/balance?ccy={ccy}", keys["api_key"], keys["secret_key"], keys["passphrase"])
    if not r or str(r.get("code")) != "0" or not isinstance(r.get("data"), list) or not r["data"]:
        return None, "تعذّر قراءة رصيد المحفظة من OKX — أعد المحاولة"
    av = 0.0
    for dd in (r["data"][0].get("details") or []):
        if str(dd.get("ccy")) == ccy:
            av = max(0.0, float(dd.get("availBal") or 0))
    claims = 0.0
    for b in bot_dirs().values():
        try:
            if str((b.get("cfg") or {}).get("api_key") or "").strip() != keys["api_key"]:
                continue
            claims += float((_gd_free_claims(b, load_json(paths_of(b)[0]) or {}) or {}).get(ccy) or 0)
        except Exception:
            continue
    return max(0.0, av - claims), claims


def deploy_pair(data):
    """🔀 نشر «شبكة عملتين»: نفس الحاسبة (يرفض بنفس الأسباب) · واحد لكل زوج · عملاتك الحرة تكفي الجهتين (بلا شراء عند النشر) ·
    نسبة البداية تُثبَّت بالإعداد (الحاسبة = المحرك)"""
    if data.get("demo"):
        return {"ok": False, "msg": "🧪 الديمو لهذا البوت غير متاح بعد"}
    P = pair_plan(data)
    if not P.get("ok"):
        return P
    if P["err"]:
        return {"ok": False, "msg": "⛔ " + P["err"][0]}
    a = P["a"]
    keys = wallet_keys(data.get("wallet", "")) or {
        "api_key": str(data.get("api_key", "")).strip(), "secret_key": str(data.get("secret_key", "")).strip(),
        "passphrase": str(data.get("passphrase", "")).strip()}
    if not keys["api_key"]:
        return {"ok": False, "msg": "اختر محفظة أو أدخل مفاتيح API"}
    tk = _pair_taken(a["sym"])
    if tk:
        return {"ok": False, "msg": f"⛔ يوجد «شبكة عملتين» على {a['other']}/{a['main']} ({tk}) — واحد لكل زوج · احذفه أولاً"}
    for ccy, need, what in ((a["main"], P["main_need"], "الشراءات تحت"), (a["other"], P["other_need"], "البيعات فوق")):
        if need <= 0:
            continue
        fr, cl = _pair_free(keys, ccy, need)
        if fr is None:
            return {"ok": False, "msg": cl}
        if fr + 1e-12 < need:
            return {"ok": False, "msg": f"⛔ {what} تحتاج {need:.8g} {ccy} — الحر بمحفظتك {fr:.8g} (بعد ما تحتاجه بوتاتك الأخرى {cl:.8g}) · قلّل الكمية"}
    folder = _new_bot_folder("pair_" + a["other"].lower())
    full = os.path.join(ROOT, folder)
    os.makedirs(full, exist_ok=True)
    cfg = {**keys, "symbol": a["sym"], "bot_type": "grid_pair", "bridge": "USDT", "main_value": a["mv"], "grid_percentage": a["g"],
           "down_levels": int(P["dn"]), "up_levels": int(P["up"]), "profit_to": a["pt"], "forced_base_ratio": float(P["r0"]),
           "fee_rate": PAIR_FEE, "slip_cap": PAIR_CAP, "slip_cap_b": PAIR_CAP_B, "is_demo": False, "auto_restart": bool(data.get("auto", True))}
    save_json_atomic(os.path.join(full, f"config_{a['sym']}.json"), cfg)
    eng_src, eng_script, _ = engine_for(cfg)
    with open(os.path.join(full, eng_script), "w", encoding="utf-8") as fh:
        fh.write(eng_src)
    b = {"dir": full, "cfg_path": os.path.join(full, f"config_{a['sym']}.json"), "cfg": cfg, "symbol": a["sym"]}
    ok, msg = launch(b)
    if ok:
        tg_send(f"🔀 *تم نشر شبكة عملتين*\nالزوج: `{a['other']}/{a['main']}` (الرئيسية `{a['main']}`)\nالبداية: `1 {a['other']} = {float(P['r0']):.8g} {a['main']}`\n"
                f"الخطوة `{a['g'] * 100:g}%` · كل شراء `{a['mv']:g} {a['main']}` · `{P['dn']}` شراء تحت · `{P['up']}` بيع فوق\n"
                f"ربح الدورة ≈ `{P['cycle_main']:.6g} {a['main']}` بعد العمولات الأربع")
    return {"ok": ok, "msg": (f"🔀 انتشرت «شبكة عملتين» وانطلقت — {a['other']}/{a['main']} · البداية {float(P['r0']):.8g}") if ok else msg, "dir": folder}
'''

R = [
    ('''            out[mn] = max(0.0, m_)
            out[oth] = max(0.0, o_)''', '''            if not isinstance(st.get("pair"), dict):          # 🔀 ما وُلد بعد (انتشر قبل ثوانٍ) ⇒ حاجته من إعداده (لا يُحجز نفس الرصيد مرتين)
                _c = b.get("cfg") or {}
                try:
                    _mv, _g, _r0 = float(_c.get("main_value") or 0), float(_c.get("grid_percentage") or 0), float(_c.get("forced_base_ratio") or 0)
                    m_ = int(float(_c.get("down_levels") or 0)) * _mv
                    o_ = sum(_mv / (_r0 * (1 + _g) ** j) for j in range(int(float(_c.get("up_levels") or 0)))) if _r0 > 0 else 0.0
                except Exception:
                    m_ = o_ = 0.0
            out[mn] = max(0.0, m_)
            out[oth] = max(0.0, o_)'''),
    ('''def deploy_step(data):''', NEW.lstrip("\n") + '''

def deploy_step(data):'''),
    ('''        if path == "/api/step_plan":''', '''        if path == "/api/pair_plan":
            return self._json(_safe(pair_plan, data, default={"ok": False, "msg": "تعذّر الحساب"}))      # 🔀 v3.36.79 (حساب فقط)
        if path == "/api/deploy_pair":
            return self._json(deploy_pair(data))          # 🔀 v3.36.79
        if path == "/api/step_plan":'''),
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
    print(f"✅ {len(R)} replacements · 🔀 the calculator (= the engine) and the deploy from the wallet's free coins · {p}")
