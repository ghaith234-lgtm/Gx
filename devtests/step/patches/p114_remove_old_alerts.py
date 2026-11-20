# 🗑️ patch 114 (dashboard v3.36.68 · the old «📊 تنبيهات المؤشرات» removed — 🎯 the signals are the one place). The owner (20-11): «زيل
#   القديمة لا اريدها · من الان وصاعدا عندما اقلك حدث اتحدثها نفسها مو تفتح واحد اخر».
#   · gone: the panel in ⚙️ «📈 شريط الأسعار» · the round every 5 minutes (ina_tick) · its sending · its settings and routes (ina_set ·
#     ina_test · pxa_get's «ina») · the 28-coin crash scan it used (mkt_scan — 🎯 computes the crash itself) · dead helpers (_ina_rel ·
#     _ina_levels · _ina_lvtxt) · the indicators and the forecasts no longer run «for the alerts» when the ticker is off
#   · kept: the squeeze reading 📊 uses (_ina_sq · INA_SQ_MIN) · MKT_COINS (🎯's measured coins) · 🟢 the bottom indicator in 🔮
#   · its useful part moves INTO 🎯 (not lost): «🟢 القاع المؤكد بالحجم» (O-botv — the bottom score ≥ 50 with the volume blow-off ≥ 2.5×,
#     ci/sig_check4.py's own measure) is a signal of the catalog like the others (daily · its own record · alone and in combinations) · 🌊 the
#     market crash now always comes from 🎯 (it was skipped there while the old alerts were on)
#   · 🔔 «إشعارات الأسعار» (price moves) stays — a different thing (it tells a move that already happened)
#   python3 devtests/step/patches/p114_remove_old_alerts.py Holy_Dashboard.pyw
import os, re, sys


def cut_block(s):
    """the old alerts' block: from its header up to the next section · keep _ina_sq + INA_SQ_MIN + MKT_COINS"""
    a = s.index("# ═══════════════ 📊 v3.31.0: تنبيهات المؤشرات")
    b = s.index("# ═══════════════ 🪙 المُراكِم تحت الرقابة")
    blk = s[a:b]
    sq_a = blk.index("def _ina_sq(D, S):")
    sq_b = blk.index("\ndef _ina_rel(R):")
    sq = blk[sq_a:sq_b].rstrip() + "\n"
    mc_a = blk.index("MKT_COINS = (")
    mc_b = blk.index(")", blk.index('"SHIB-USDT"')) + 1
    mc = blk[mc_a:mc_b]
    sqmin = re.search(r"^INA_SQ_MIN = .*$", blk, re.M).group(0)
    new = ("# ═══════════════ ⚡ الانضغاط على شموع الساعة (قراءة 📊) · 🪙 عملات القياس ═══════════════\n"
           "#   🗑️ v3.36.68: «📊 تنبيهات المؤشرات» القديمة أُزيلت (المالك 20-11: «زيل القديمة») — الإشعارات كلها من 🎯 الإشارات ·\n"
           "#   بقي هنا ما تستعمله أجزاء أخرى: الانضغاط (📊) · عملات القياس (🎯)\n"
           + sqmin + "\n\n\n" + sq + "\n\n" + mc + "\n\n\n")
    return s[:a] + new + s[b:]


R = [
    ("""            if (indic_cfg()["on"] or ina_cfg()["on"]) and indic_cfg()["coins"]:   # 📊 v3.31.0: تنبيهات المؤشرات تشتغل حتى لو الشريط مطفي
                indic_fetch()
                _ind2_run()
                _safe(ina_tick, default=None)          # 📊 تنبيهات المؤشرات — كل تحديث (5 دقائق)
""", """            if indic_cfg()["on"] and indic_cfg()["coins"]:
                indic_fetch()
                _ind2_run()
"""),
    ("""            if (indic_cfg()["on"] or ina_cfg()["on"]) and ticker_cfg()["coins"]:      # 🟢 v3.36.27: مؤشر القاع للتنبيهات حتى لو الشريط مطفي""",
     """            if indic_cfg()["on"] and ticker_cfg()["coins"]:"""),
    ("""    ina_on = bool((_safe(ina_cfg, default={}) or {}).get("on"))
    for e in cat["e"]:
        if e["ty"] in ("crash", "fng", "eco"):
            if cfg["types"].get(e["ty"], True) and not (e["ty"] == "crash" and ina_on) and (e["ty"] != "crash" or e["f"] == "4H"):""",
     """    for e in cat["e"]:
        if e["ty"] in ("crash", "fng", "eco"):
            if cfg["types"].get(e["ty"], True) and (e["ty"] != "crash" or e["f"] == "4H"):"""),
    ("""        if ty == "crash" and _safe(ina_cfg, default={}).get("on"):
            continue                                          # 🌊 يصلك أصلاً من «📊 تنبيهات المؤشرات»
""", ""),
    ("""                return self._json({"ok": True, "pxa": pxa_view(), "ina": ina_view()})""",
     """                return self._json({"ok": True, "pxa": pxa_view()})"""),
    ("""            if act == "ina_set":                          # 📊 v3.31.0: تنبيهات المؤشرات — تشغيل/إطفاء · الحساسية · وين توصل
                return self._json(ina_set((data.get("value") if isinstance(data.get("value"), dict) else {})))
            if act == "ina_test":
                return self._json(ina_test())
""", ""),
    # 🟢 the bottom with volume becomes a 🎯 signal
    ("""        if daily:
            a = _bot_at(C, S2["rsi"], t)
            cur["O-bottom"] = 1 if a and a[0] >= 50 else 0""",
     """        if daily:
            a = _bot_at(C, S2["rsi"], t)
            cur["O-bottom"] = 1 if a and a[0] >= 50 else 0
            cur["O-botv"] = 1 if a and a[0] >= 50 and _bot_vx(V, t) >= BOT_VOL_X else 0     # 🟢 v3.36.68: القاع المؤكد بالحجم (كان «تنبيهات المؤشرات»)"""),
    ("""    "O-bottom": ("volatility", "🟢 مؤشر القاع", "🟢 مؤشر القاع"),""",
     """    "O-bottom": ("volatility", "🟢 مؤشر القاع", "🟢 مؤشر القاع"),
    "O-botv": ("volume", "🟢 القاع المؤكد بالحجم", "🟢 القاع المؤكد بالحجم"),"""),
    # page
    ("""let PXAO=false, PXAV=null, GLT=0, INAO=false, INAV=null;""", """let PXAO=false, PXAV=null, GLT=0;"""),
    ("""function pxaRender(){const el=$('#tk_pxa');if(el)el.innerHTML=(PXAV?pxaPanel(PXAV):'')+(INAV?inaPanel(INAV):'')+sgMini()}""",
     """function pxaRender(){const el=$('#tk_pxa');if(el)el.innerHTML=(PXAV?pxaPanel(PXAV):'')+sgMini()}"""),
    ("""PXAV=r&&r.pxa||null;INAV=r&&r.ina||null}catch(e){PXAV=null;INAV=null}pxaRender()}""",
     """PXAV=r&&r.pxa||null}catch(e){PXAV=null}pxaRender()}"""),
    ("""حركة السعر فقط (المؤشرات وحدها في الأسفل) · لعملات الشريط نفسها""", """حركة السعر فقط (الإشارات في 🎯 تحت) · لعملات الشريط نفسها"""),
    ("""🧭 السوق: حين يثبت وضع جديد · 🌊 يصلك من «📊 تنبيهات المؤشرات» حين تكون مفعّلة (لا يتكرر) · ✅ النتائج: بعد وقت كل إشارة وصلتك""",
     """🧭 السوق: حين يثبت وضع جديد · 🌊 الانهيار: مرة واحدة في اليوم على الأكثر · ✅ النتائج: بعد وقت كل إشارة وصلتك"""),
    ("""        _safe(app_feed_push, text, go, "ind", default=None)     # 📱 قناة «📊 تنبيهات المؤشرات» · الضغط يفتح 🎯""",
     """        _safe(app_feed_push, text, go, "ind", default=None)     # 📱 قناة التطبيق «ind» · الضغط يفتح 🎯"""),
    # a catalog built by an older code (without O-botv) is rebuilt by itself — not after up to a week
    ("""SG_CAT_AGE = 7 * 86400                     # يُعاد البحث عن التركيبات كل أسبوع (على التاريخ الأحدث)""",
     """SG_CAT_AGE = 7 * 86400                     # يُعاد البحث عن التركيبات كل أسبوع (على التاريخ الأحدث)
SG_CAT_VER = 2                             # 🔄 v3.36.68: نسخة الدليل — دليل بُني بكود أقدم (بلا إشارة جديدة) يُعاد بناؤه وحده"""),
    ("""    cat.update(v=1, ts=time.time(), coins=list(COIN),""", """    cat.update(v=1, cv=SG_CAT_VER, ts=time.time(), coins=list(COIN),"""),
    ("""        need_cat = (not cat or now - float(cat.get("ts") or 0) > SG_CAT_AGE or bool(st.get("cat_force"))""",
     """        need_cat = (not cat or now - float(cat.get("ts") or 0) > SG_CAT_AGE or bool(st.get("cat_force")) or int(cat.get("cv") or 1) != SG_CAT_VER"""),
    ("""APP_VERSION = "3.36.67\"""", """APP_VERSION = "3.36.68\""""),
]


def cut_js(s):
    """inaPanel · inaSet · inaTest — the page functions of the old alerts"""
    for name in ("function inaPanel(P){", "async function inaSet(v){", "async function inaTest(){"):
        a = s.index(name)
        if name.startswith("function inaPanel"):
            b = s.index("\nfunction pxaRender(){", a) + 1
        else:
            b = s.index("\n", a) + 1
        s = s[:a] + s[b:]
    return s


if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    s = cut_block(s)
    s = cut_js(s)
    left = [w for w in ("ina_cfg", "ina_tick", "ina_view", "ina_set", "ina_test", "_ina_send", "mkt_scan", "INA_FILE", "inaPanel", "INAV", "inaSet")
            if re.search(r"\b" + w + r"\b", s)]
    if left:
        print("❌ still referenced:", left); sys.exit(1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements + the old block cut · 🗑️ the old indicator alerts removed · 🟢 the bottom with volume is a 🎯 signal · compiles · {p}")
