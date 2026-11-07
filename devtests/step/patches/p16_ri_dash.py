# 🪜💠 patch 16 (dashboard · reinvest phase E — the grid's reinvest screens for the graded grid · REINVEST_PLAN.md rule ١٣)
#   🪜 branches only (♾️ ➕ 🎚️ untouched):
#   · deploy: «💠 إعادة الاستثمار من البداية» + the percentage (as the grid's form) — the engine reinvests from its first sale
#   · the card: the 🔄 chip (on ⇒ the setting · off ⇒ the setting + the release flag — no restart: the engine reads both live)
#   · the snapshot (reinvest_snapshot) from the slots: one row per slot (level · part), kk = "j:k" (the inject / withdraw
#     requests' key) · io = the growth really inside its order · what is unwinding · desync (a live buy ≠ base + growth)
#   · the actions 💉 ➖ ⚖️ open for 🪜 (the same request files as the grid) · the ladder shows «المستوى j · الجزء k/N»
#   · never the grid's reinvest.py wrapper for 🪜 (launch · the trial path) — its engine has reinvest inside
#   · the card's slot view: a buy's size = base + growth · the trial path: the profit = ordinary + reinvested
#   python3 devtests/step/patches/p16_ri_dash.py Holy_Dashboard.pyw
import os, sys

R = [
    # launch: never the grid's wrapper for 🪜
    ('''    if script == eng_script and str(b["cfg"].get("bot_type") or "") not in _NONGRID:   # 💠 الغلاف لبوتات الشبكة بس''',
     '''    if script == eng_script and str(b["cfg"].get("bot_type") or "") not in _NONGRID + ("grid_step",):   # 💠 الغلاف لبوتات الشبكة بس (🪜 إعادة استثماره داخل محركه)'''),
    # the bot report: the script expected
    ('''            _scr = "reinvest.py" if (b["cfg"].get("reinvest") and os.path.exists(_rp2)) else (''',
     '''            _scr = "reinvest.py" if (b["cfg"].get("reinvest") and os.path.exists(_rp2) and bt != "grid_step") else ('''),
    # the snapshot: 🪜 from its slots
    ('''def reinvest_snapshot(b, st):
    """🔄 المتراكم داخل الأوامر: دولار (شراء معلّق) وعملة (ماسك عملة)."""
    ri = st.get("reinvest")
''',
     '''def _step_ri_snapshot(b, st):
    """🪜💠 لقطة إعادة الاستثمار للشبكي المتدرج — نفس شكل reinvest_snapshot (البطاقة · السلّم · الأزرار) لكن من الخانات:
    صف لكل خانة (المستوى · الجزء) · kk = "j:k" مفتاح طلبات الحقن والسحب · io = النمو الموجود فعلاً داخل أمرها (البيع: العملة
    فوق أساسه بعد العمولة · الشراء: كله داخل أمره) · اللي يتفكّك بعد التحرير بقائمته · desync = شراء حي حجمه ≠ الأساس + النمو"""
    cfg = b.get("cfg") or {}
    ri = st.get("reinvest")
    if not isinstance(ri, dict):
        if not cfg.get("reinvest"):
            return None
        return {"on": False, "cfg_on": True, "usd": 0.0, "coin": 0.0, "cycles": 0, "levels": 0, "days": 0.0, "rows": [], "top": [],
                "desync": [], "handoff": None, "released": None, "file": True, "file_old": False, "pending_boot": True, "step": True}
    S = st.get("slots") if isinstance(st.get("slots"), dict) else {}
    lv = ri.get("levels") or {}
    stp = st.get("step") or {}
    N = int(stp.get("N") or cfg.get("step_parts") or 1)
    fr = float(stp.get("f") or cfg.get("fee_rate") or 0.001)
    uw = ri.get("unwind") or {}
    usd = coin = 0.0
    rows, uws, desync = [], [], []
    for key, s in sorted(S.items(), key=lambda kv: (-float(kv[1].get("bp") or 0), int(kv[1].get("k") or 0))):
        try:
            e = lv.get(key) or {}
            px = float(e.get("px") or s.get("bp") or 0)
            gq, bk = float(e.get("grown_qty") or 0), float(e.get("usd_book") or 0)
            bq = float(e.get("base_qty") or s.get("q") or 0)
            sell = s.get("side") == "sell"
            usd += bk
            if gq > 0:
                if sell:
                    coin += gq
                else:
                    usd += gq * px
            if sell:
                io = round(min(gq, max(0.0, float(s.get("sq") or 0) - float(s.get("acc") or 0) - float(s.get("q") or 0) * (1.0 - fr))), 10)
            else:
                io = round(gq, 10)
            tv = bk + gq * px
            row = {"p": round(px, 10), "sp": round(float(s.get("sp") or 0), 10), "b": round(bq, 10), "g": round(gq, 10), "k": round(bk, 8),
                   "s": "sell" if sell else "buy", "v": round(gq * px, 8), "kk": key, "io": io,
                   "j": round(min(float(e.get("inj_book") or 0) + float(e.get("inj_grown") or 0), tv), 8), "tv": round(tv, 8),
                   "c": int(e.get("cycles") or 0), "pct": round((gq / bq * 100) if bq > 0 else 0, 2),
                   "lbl": f"{int(s.get('j') or 0)} · {int(s.get('k') or 0)}/{N}"}
            if key in uw:
                row.update(uw=True, s=str((uw.get(key) or {}).get("side") or row["s"]))
                uws.append(row)
            else:
                rows.append(row)
            o = s.get("o") or {}
            if not sell and o.get("st") == "live" and not s.get("am"):
                want = float(s.get("q") or 0) + gq - float(s.get("acc") or 0)
                got = float(o.get("sz") or 0)
                if want > 0 and abs(got - want) > max(1e-9, want * 0.02):
                    desync.append({"p": float(o.get("px") or px), "want": round(want, 10), "got": round(got, 10), "kk": key})
        except Exception:
            continue
    top = sorted([{"p": float(v.get("px") or 0), "b": float(v.get("base_qty") or 0), "g": float(v.get("grown_qty") or 0),
                   "pct": round(float(v.get("grown_qty") or 0) / float(v.get("base_qty") or 1) * 100, 1)}
                  for v in lv.values() if float(v.get("grown_qty") or 0) > 0], key=lambda x: -x["pct"])[:5]
    started = float(ri.get("started_ts") or 0)
    return {"on": bool(ri.get("on")), "desync": desync[:8], "top": top, "inj_total": round(float(ri.get("inj_total") or 0), 6),
            "pct": 100.0 if ri.get("pct") is None else round(float(ri.get("pct") or 0), 2),
            "pct_cfg": 100.0 if cfg.get("reinvest_pct") is None else round(float(cfg.get("reinvest_pct") or 0), 2),
            "inj_pending": bool(_inj_pending(b.get("dir"))), "unwind": uws[:60], "n_unwind": len(uw),
            "handoff": (_ri_pending_handoffs(st, 0.0) or [None])[0], "handoff_stuck": (_ri_pending_handoffs(st, 1800.0) or [None])[0],
            "usd": round(usd, 4), "coin": round(coin, 8), "rows": rows[:300], "cycles": int(ri.get("cycles") or 0), "levels": len(lv),
            "days": round(max(0.0, (time.time() - started) / 86400.0), 2) if started else 0.0, "file": True, "file_old": False,
            "cfg_on": bool(cfg.get("reinvest")), "released": ri.get("released"), "broken": bool(ri.get("broken")), "step": True,
            "credited": round(float(ri.get("credited") or 0), 8)}


def reinvest_snapshot(b, st):
    """🔄 المتراكم داخل الأوامر: دولار (شراء معلّق) وعملة (ماسك عملة)."""
    if str((b.get("cfg") or {}).get("bot_type") or "") == "grid_step":
        return _step_ri_snapshot(b, st)
    ri = st.get("reinvest")
'''),
    # the card's slot view: a buy = base + growth
    ('''            rem = max(0.0, (float(s.get("q") or 0) if buy else float(s.get("sq") or 0)) - float(s.get("acc") or 0))''',
     '''            rem = max(0.0, (float(s.get("q") or 0) + float(s.get("g") or 0) if buy else float(s.get("sq") or 0)) - float(s.get("acc") or 0))'''),
    # the actions: 🪜 reinvest open (no restart — the engine reads the setting and the flag live)
    ('''        if action in ("reinvest", "ri_inject", "ri_pct", "ri_withdraw"):
            return {"ok": False, "msg": "🪜 إعادة الاستثمار غير متاحة للشبكي المتدرج في هذا الإصدار"}''',
     '''        if action == "reinvest":                                 # 💠 v3.36.18: داخل محركه — بلا غلاف وبلا إعادة تشغيل
            if b["cfg"].get("is_demo"):
                return {"ok": False, "msg": "💠 إعادة الاستثمار لا تعمل مع DEMO"}
            newv = not b["cfg"].get("reinvest", False)
            write_cfg_keys(b["cfg_path"], {"reinvest": newv})
            fl = os.path.join(b["dir"], "reinvest_release.flag")
            if not newv:
                try:
                    open(fl, "w").close()
                except Exception:
                    pass
                tg_send(f"🔓 *تحرير إعادة الاستثمار* — `{b['symbol']}`")
                return {"ok": True, "msg": "🔓 تحرير — الدولار يدخل الربح اليومي · العملة للمُراكِم · رأس مالك لمحفظتك (خلال ثوانٍ)"}
            try:
                os.remove(fl)
            except Exception:
                pass
            tg_send(f"🔄 *إعادة الاستثمار مفعّلة* — `{b['symbol']}` · تبدأ من البيعة القادمة")
            return {"ok": True, "msg": "🔄 مفعّلة — تبدأ من البيعة القادمة (بلا إعادة تشغيل)"}'''),
    # deploy: reinvest from the first sale (as the grid's form)
    ('''    folder = "step_" + a["base"].lower()
    base_folder, c = folder, 1''',
     '''    _ri = None                                    # 💠 v3.36.18: إعادة الاستثمار من أول بيعة (نموذج النشر — والاختبار التجريبي يقرأها منه)
    if data.get("reinvest"):
        try:
            _ri = float(data.get("reinvest_pct") if data.get("reinvest_pct") not in (None, "") else 100)
        except Exception:
            _ri = -1.0
        if not (0 <= _ri <= 100):
            return {"ok": False, "msg": "نسبة إعادة الاستثمار يجب أن تكون من 0 إلى 100%"}
    folder = "step_" + a["base"].lower()
    base_folder, c = folder, 1'''),
    ('''           "auto_restart": bool(data.get("auto", True))}
    save_json_atomic(os.path.join(full, f"config_{a['sym']}.json"), cfg)
    eng_src, eng_script, _ = engine_for(cfg)''',
     '''           "auto_restart": bool(data.get("auto", True))}
    if _ri is not None:
        cfg["reinvest"], cfg["reinvest_pct"] = True, _ri          # 🪜 المحرك يعيد الاستثمار من أول بيعة (بلا غلاف)
    save_json_atomic(os.path.join(full, f"config_{a['sym']}.json"), cfg)
    eng_src, eng_script, _ = engine_for(cfg)'''),
    ('''                f"الشراء `{a['G'] * 100:g}%` · `{a['Q']:g}$` لكل شراء")''',
     '''                f"الشراء `{a['G'] * 100:g}%` · `{a['Q']:g}$` لكل شراء" + (f"\\n💠 إعادة استثمار `{_ri:g}%` من أول بيعة" if _ri is not None else ""))'''),
    # the trial path: the profit = ordinary + reinvested (the 🪜 book) · its reinvested coins · the note
    ('''    v = float((st or {}).get(pk) or 0)
    if rnf is None or not ((st or {}).get("reinvest") or {}).get("on"):
        return v''',
     '''    v = float((st or {}).get(pk) or 0)
    _sb = (st or {}).get("reinvest") if isinstance((st or {}).get("reinvest"), dict) else None
    if rnf is None and _sb and "credited" in _sb:            # 🪜 v3.36.18: الربح الحقيقي = العادي + المعاد استثماره − اللي تحرر منه
        return v + float(_sb.get("credited") or 0) - float(_sb.get("out_usd") or 0)
    if rnf is None or not ((st or {}).get("reinvest") or {}).get("on"):
        return v'''),
    ('''    if kind == "grid_step":                   # 🪜 v3.36.15: دفتر المحرك صافٍ حقيقي (العمولتين من التنفيذ نفسه) ⇒ هو ربح البيع والشراء
        trade = book''',
     '''    if kind == "grid_step":                   # 🪜 v3.36.15: دفتر المحرك صافٍ حقيقي (العمولتين من التنفيذ نفسه) ⇒ هو ربح البيع والشراء
        trade = _bt_cum(st, r.get("pkey") or "total_profit", None)     # 💠 v3.36.18: + المعاد استثماره'''),
    ('''    if kind == "grid_step":
        return None                           # 🪜 بلا 💠 بهذا الإصدار
''',
     '''    if kind == "grid_step":                   # 🪜💠 v3.36.18: نمو الخانات بلا المحقون يدوياً (عملة) + الحصّالات (دولار)
        rb = st.get("reinvest") if isinstance(st.get("reinvest"), dict) else None
        if not rb or not (rb.get("on") or rb.get("levels")):
            return None
        q = u = 0.0
        for lv in (rb.get("levels") or {}).values():
            try:
                px_ = f_(lv.get("px"))
                q += max(0.0, f_(lv.get("grown_qty")) - (f_(lv.get("inj_grown")) / px_ if px_ > 0 else 0.0))
                u += max(0.0, f_(lv.get("usd_book")) - f_(lv.get("inj_book")))
            except Exception:
                continue
        return {"q": round(q, 10), "usd": round(u, 8)}
'''),
    ('''    if kind in ("grid", "grid_range", "grid_plus") and _rsrc.get("reinvest") and not _rsrc.get("demo"):   # 💠 v3.36.7''',
     '''    if kind in ("grid", "grid_range", "grid_plus", "grid_step") and _rsrc.get("reinvest") and not _rsrc.get("demo"):   # 💠 v3.36.7 · 🪜 v3.36.18'''),
    # the trial replay: its curve is the same profit as the card (🪜 + reinvest: ordinary + reinvested) ⇒ scaled by that, not by
    # total_profit alone (it ended at twice the card at 50%) — for the grid _bt_cum(…, None) is total_profit itself (unchanged)
    ('''    elif s and s.get("od", {}).get("k") == "grid" and abs(float(r["realized"] or 0)) > 1e-12:
        k = float(s["trade"]) / float(r["realized"])''',
     '''    elif s and s.get("od", {}).get("k") == "grid" and abs(_bt_cum(r.get("state") or {}, r.get("pkey") or "total_profit", None)) > 1e-12:
        k = float(s["trade"]) / _bt_cum(r.get("state") or {}, r.get("pkey") or "total_profit", None)'''),
    # the orphan-growth repair is the grid's (🪜 has no orphan growth: every slot keeps its own)
    ('''    if not ri or ri.get("on") or usd <= 0:
        return []
    upx = [float(e.get("px") or 0) for e in (ri.get("unwind") or {}).values() if isinstance(e, dict)]''',
     '''    if not ri or ri.get("on") or usd <= 0 or isinstance(st.get("slots"), dict):     # (🪜: كل خانة تحمل نموّها — ما بيه يتيم)
        return []
    upx = [float(e.get("px") or 0) for e in (ri.get("unwind") or {}).values() if isinstance(e, dict)]'''),
    # ── JS: the 🔄 chip for 🪜 (no ⚔️) · its tip without the restart
    ('''  if(b.bot_type!=='dca'&&b.bot_type!=='dca_buy'&&b.bot_type!=='grid_step'){   // 🪜 v3.36.15: بلا 🔄 وبلا ⚔️ للشبكي المتدرج (محركه ما فيه الاثنين)''',
     '''  if(b.bot_type!=='dca'&&b.bot_type!=='dca_buy'){   // 🪜 v3.36.18: 🔄 داخل محركه (بلا ⚔️)'''),
    ('''       🔁 واللوحة راح <b>تعيد تشغيل البوت تلقائياً</b>.<br><br>''',
     '''       ${b.bot_type==='grid_step'?'🪜 تبدأ من <b>البيعة القادمة</b> — بلا إعادة تشغيل.':'🔁 واللوحة راح <b>تعيد تشغيل البوت تلقائياً</b>.'}<br><br>'''),
    ('''       🔒 والأوامر المنشورة <b>ما تنلغى</b> — تتفكّك بدورتها الطبيعية.<br><br>''',
     '''       ${b.bot_type==='grid_step'?'✏️ والأوامر المنشورة المكبّرة <b>تتصغّر فوراً</b> بالمنصة (بلا إلغاء) — اللي ترفض المنصة تصغيره يكمل دورته.':'🔒 والأوامر المنشورة <b>ما تنلغى</b> — تتفكّك بدورتها الطبيعية.'}<br><br>'''),
    # the ladder: «المستوى j · الجزء k/N» under the buy price
    ('''        <td style="${TD};color:var(--tx)">${x.uw?'<span style="color:var(--amber)">⏳</span> ':''}<b>${f4(x.p)}</b></td>''',
     '''        <td style="${TD};color:var(--tx)">${x.uw?'<span style="color:var(--amber)">⏳</span> ':''}<b>${f4(x.p)}</b>${x.lbl?`<div style="color:var(--mut2);font-size:9.5px">🪜 ${x.lbl}</div>`:''}</td>'''),
    # the injection / withdrawal headers: the slot, not just its price (parts of one level share it)
    ('''  showModal(`<h2>💉 حقن رأس مال — الدرجة ${(+px).toFixed(4)}</h2>''',
     '''  const _sl=((b.ri||{}).rows||[]).find(x=>x.kk===String(k));
  showModal(`<h2>💉 حقن رأس مال — ${_sl&&_sl.lbl?'🪜 المستوى '+_sl.lbl.replace(' · ',' · الجزء '):'الدرجة '+(+px).toFixed(4)}</h2>'''),
    ('''  showModal(`<h2>➖ سحب من الدرجة ${p.toFixed(4)} — ${cs?'جهة البيع (عملة)':'جهة الشراء (دولار)'}</h2>''',
     '''  const _sl=((b.ri||{}).rows||[]).find(x=>x.kk===String(k));
  showModal(`<h2>➖ سحب من ${_sl&&_sl.lbl?'🪜 المستوى '+_sl.lbl.replace(' · ',' · الجزء '):'الدرجة '+p.toFixed(4)} — ${cs?'جهة البيع (عملة)':'جهة الشراء (دولار)'}</h2>'''),
    # deploy form: the reinvest box (as the grid's) · its body
    ('''  <div class="cklist" style="margin-top:10px"><label class="ck"><input type="checkbox" id="st_auto" checked>🤖 يشمله الحارس</label></div>''',
     '''  <div class="cklist" style="margin-top:10px"><label class="ck"><input type="checkbox" id="st_auto" checked>🤖 يشمله الحارس</label>
    <label class="ck" title="من أول بيعة: نسبة من ربح كل بيعة تعود إلى خانتها فيكبر شراؤها (تُغيَّر لاحقاً من البطاقة) — والاختبار على مسار تجريبي يعمل بها كذلك"><input type="checkbox" id="st_ri" ${pre.reinvest?'checked':''} onchange="stRiSync()">💠 إعادة الاستثمار من البداية</label></div>
  <div class="frm" id="st_fri" style="display:${pre.reinvest?'':'none'};margin-top:8px"><div class="fld"><label>💠 نسبة ما يعود إلى الخانة من ربح كل بيعة (%)</label><input id="st_rip" class="num" value="${pre.reinvest_pct??100}"><small style="color:var(--mut2);font-size:10px">100% = الربح كله يكبّر شراء الخانة · 50% = نصفه يكبّره ونصفه ربح محرَّر</small></div></div>'''),
    ('''    min_price:g('st_floor'),up_groups:g('st_up'),forced_base:g('st_p0'),wallet:g('st_wallet'),auto:!!($('#st_auto')||{}).checked}}''',
     '''    min_price:g('st_floor'),up_groups:g('st_up'),forced_base:g('st_p0'),wallet:g('st_wallet'),auto:!!($('#st_auto')||{}).checked,
    reinvest:!!($('#st_ri')||{}).checked,reinvest_pct:g('st_rip')}}
function stRiSync(){const c=$('#st_ri'),f=$('#st_fri');if(f)f.style.display=c&&c.checked?'':'none'}'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
