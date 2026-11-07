# 🧩 patch 17 (dashboard · the owner's requests 7-11 — all bot types, not only 🪜)
#   ① ⏱️ the run time on every card (bots of every kind · DCA · the accumulator) from a start date the dashboard saves ONCE the first
#      time it sees the card (or at deploy) and never changes — no file dates (a copied / rewritten config moved it before) · a
#      card from before this version starts from now (the owner: «حتى لو كل الكروت الحالية تقرأ من الصفر») · shown as the time
#      and the day it started (the full date and hour in its tip) · the rates (/day /month /year) keep the profit's own period
#   ② 🗄️ «الأرشيف» between 🛡️ الرقابة and 📉 الخسائر: every deleted bot (its folder already goes to _archive) — its settings
#      (no keys), when it started, when it was deleted, how long it ran, its profit (trading · released · 💠 inside) — recorded
#      at the deletion · bots deleted before this version from their folder and the gone book (their start «تقريبي»)
#   ③ «👛 المحافظ» ⇒ «🔗 الارتباط» (the button, its page and the messages that point to it)
#   ④ 📱 the widget counts the TRADING profit (ربح التداول: ordinary + 💠 reinvested) in every cell — today · this month · total ·
#      and each USD bot's today / total (was the released profit)
#   python3 devtests/step/patches/p17_owner_misc.py Holy_Dashboard.pyw
import os, sys

R = [
    # ① the fixed start date
    ('''    if not cands: return 0.0
    fs = min(cands)
    if abs(fs - saved) > 60:      # ثبّته لو تغيّر فعلياً
        meta.setdefault(key, {})["first_seen"] = fs
        try: save_json_atomic(BOT_META, meta); _META_CACHE["t"] = 0
        except Exception: pass
    return fs
''',
     '''    if not cands: return 0.0
    fs = min(cands)
    if abs(fs - saved) > 60:      # ثبّته لو تغيّر فعلياً
        meta.setdefault(key, {})["first_seen"] = fs
        try: save_json_atomic(BOT_META, meta); _META_CACHE["t"] = 0
        except Exception: pass
    return fs


def started_of(key):
    """⏱️ v3.36.18 (طلب المالك): تاريخ تشغيل الكرت — ينحفظ مرة وحدة أول ما تشوفه اللوحة (لحظة النشر للجديد) وما يتغيّر أبداً ·
    مستقل عن تواريخ الملفات (ملف إعدادات انكتب أو انسخ كان يغيّر الزمن) · كرت من قبل هذي النسخة يبدي من أول ما شافته ·
    الحذف ينقله للأرشيف (ومجلد جديد بنفس الاسم يبدي من جديد) · المفتاح: مجلد البوت · «acc:<id>» للمُراكِم"""
    meta = bot_meta()
    e = meta.get(key) if isinstance(meta.get(key), dict) else None
    t = float((e or {}).get("started") or 0)
    if t > 0:
        return t
    t = time.time()
    meta.setdefault(key, {})["started"] = t
    try:
        save_json_atomic(BOT_META, meta)
        _META_CACHE["t"] = 0
    except Exception:
        pass
    return t
'''),
    ('''    # ⏱️ زمن التشغيل: من أقدم ظهور مثبّت (يبقى صحيحاً رغم تقليم ملف السجل)
    age_days = 0.0
    try:
        _fs = first_seen_of(b, hist)
        if _fs > 0:
            age_days = max(0.0, (time.time() - _fs) / 86400.0)
    except Exception:
        age_days = 0.0''',
     '''    # ⏱️ v3.36.18: زمن التشغيل من تاريخ التشغيل الثابت (started_of) · المعدلات تبقى على مدة الربح نفسه (أقدم ظهور)
    age_days = rate_days = 0.0
    _started = 0.0
    try:
        _fs = first_seen_of(b, hist)
        if _fs > 0:
            rate_days = max(0.0, (time.time() - _fs) / 86400.0)
    except Exception:
        rate_days = 0.0
    try:
        _started = started_of(os.path.relpath(b["dir"], ROOT))
        age_days = max(0.0, (time.time() - _started) / 86400.0)
    except Exception:
        age_days = 0.0'''),
    ('''            "age_days": round(age_days, 2),
            "rate_daily": (round(float(st.get("total_coin_profit") or 0) / age_days, 8) if _bt in ("dca", "dca_buy")   # 🔧 v3.25.3: DCA ربحه هنا (كان +0)
                           else round((float(st.get("total_profit") or 0) * _safe(net_factor, b, default=1.0) / age_days), 4))
            if age_days >= 0.5 else None,''',
     '''            "age_days": round(age_days, 4), "started": round(_started, 1),
            "rate_daily": (round(float(st.get("total_coin_profit") or 0) / rate_days, 8) if _bt in ("dca", "dca_buy")   # 🔧 v3.25.3: DCA ربحه هنا (كان +0)
                           else round((float(st.get("total_profit") or 0) * _safe(net_factor, b, default=1.0) / rate_days), 4))
            if rate_days >= 0.5 else None,'''),
    ('''            "id": a["id"], "name": a.get("name") or sym, "start": a.get("start"), "symbol": sym,''',
     '''            "id": a["id"], "name": a.get("name") or sym, "start": a.get("start"), "symbol": sym,
            "started": round(_safe(started_of, "acc:" + str(a["id"]), default=0.0) or 0.0, 1),     # ⏱️ v3.36.18'''),
    # ② the archive: recorded at the deletion
    ('''    arch = os.path.join(ROOT, "_archive")
    os.makedirs(arch, exist_ok=True)
    dest = os.path.join(arch, f"{time.strftime('%Y%m%d_%H%M%S')}_{os.path.basename(b['dir'])}")
    try:
        shutil.move(b["dir"], dest)
    except Exception as ex:
        return {"ok": False, "msg": f"أوقفته بس فشل النقل: {ex}"}''',
     '''    _arec = _safe(_arch_record, b, default=None)          # 🗄️ v3.36.18: الأرشيف (تاريخ التشغيل · الربح) — قبل النقل
    arch = os.path.join(ROOT, "_archive")
    os.makedirs(arch, exist_ok=True)
    dest = os.path.join(arch, f"{time.strftime('%Y%m%d_%H%M%S')}_{os.path.basename(b['dir'])}")
    try:
        shutil.move(b["dir"], dest)
    except Exception as ex:
        return {"ok": False, "msg": f"أوقفته بس فشل النقل: {ex}"}
    try:
        if _arec is not None:
            am = load_json(ARCHIVE_META) or {}
            if not isinstance(am, dict):
                am = {}
            am.setdefault("items", {})[os.path.basename(dest)] = _arec
            save_json_atomic(ARCHIVE_META, am)
        _mk, _mt = os.path.relpath(b["dir"], ROOT), bot_meta()   # ⏱️ مجلد جديد بنفس الاسم يبدي تشغيله من جديد
        if _mk in _mt:
            _mt.pop(_mk, None)
            save_json_atomic(BOT_META, _mt)
            _META_CACHE["t"] = 0
    except Exception:
        pass'''),
    ('''def delete_bot(b):
''',
     '''ARCHIVE_META = os.path.join(ROOT, "Holy_Archive.json")   # 🗄️ v3.36.18: لكل بوت محذوف (مجلده بـ_archive) — تشغيله · حذفه · ربحه
_ARCH_SECRET = re.compile(r"key|secret|pass|token|wallet", re.I)


def _arch_record(b):
    """🗄️ لحظة الحذف (قبل نقل المجلد): تاريخ التشغيل الثابت · ربح التداول بكل أيامه (عادي + 💠) · المحرر · 💠 داخل الأوامر ·
    ربح العملة (نفس أرقام دفتر المحذوف GONE اللي سجّلها _gone_archive قبلها)"""
    key = os.path.relpath(b["dir"], ROOT)
    meta = bot_meta().get(key) or {}
    started = float(meta.get("started") or 0)
    approx = False
    if started <= 0:
        started, approx = float(meta.get("first_seen") or 0), True
    today = datetime.now().strftime("%Y-%m-%d")
    trade = None
    try:
        led = load_json(LEDGER) or {}
        days = sorted(d for d in ((led.get(key) or {}).get("daily") or {}) if isinstance(d, str) and len(d) == 10)
        d0 = min([days[0]] if days else [today] + ([datetime.fromtimestamp(started).strftime("%Y-%m-%d")] if started > 0 else []))
        tb = (trade_period(d0, today).get("by_bot") or {}).get(key) or {}
        trade = round(float(tb.get("n") or 0) + float(tb.get("r") or 0), 8)
    except Exception:
        trade = None
    g = [e for e in (((load_json(GONE) or {}).get("bots") or {}).values()) if isinstance(e, dict) and e.get("key") == key]
    ge = max(g, key=lambda e: float(e.get("ts") or 0)) if g else {}
    return {"key": key, "sym": b["symbol"], "type": str((b.get("cfg") or {}).get("bot_type") or "grid"), "started": started or None,
            "approx": approx, "deleted": time.time(), "trade": trade, "rel": float(ge.get("rel") or 0), "held": float(ge.get("held") or 0),
            "handoff": float(ge.get("handoff") or 0), "coin": ge.get("coin") or {}}


def archive_view():
    """🗄️ الأرشيف (للعرض): كل مجلد بـ_archive = بوت محذوف — إعداداته (بلا مفاتيح) · تشغيله · حذفه · مدته · ربحه ·
    المحذوف قبل v3.36.18: من مجلده ودفتر المحذوف (بداية تشغيله تقريبية من أقدم ظهور لو محفوظ)"""
    root = os.path.join(ROOT, "_archive")
    am = (load_json(ARCHIVE_META) or {}).get("items") or {}
    gone = [e for e in (((load_json(GONE) or {}).get("bots") or {}).values()) if isinstance(e, dict)]
    meta = bot_meta()
    out = []
    for name in (sorted(os.listdir(root), reverse=True) if os.path.isdir(root) else []):
        d = os.path.join(root, name)
        if not os.path.isdir(d):
            continue
        cfgs = sorted(glob.glob(os.path.join(d, "config_*.json")))
        cfg = _safe(load_json, cfgs[0], default=None) if cfgs else None
        if not isinstance(cfg, dict):
            continue
        m = re.match(r"^(\\d{8}_\\d{6})_(.+)$", name)
        try:
            deleted = time.mktime(time.strptime(m.group(1), "%Y%m%d_%H%M%S")) if m else os.path.getmtime(d)
        except Exception:
            deleted = os.path.getmtime(d)
        orig = m.group(2) if m else name
        it = am.get(name) if isinstance(am.get(name), dict) else None
        if it is None:                                    # (حُذف قبل الأرشيف)
            g = [e for e in gone if e.get("key") == orig and abs(float(e.get("ts") or 0) - deleted) < 2 * 86400]
            ge = max(g, key=lambda e: float(e.get("ts") or 0)) if g else {}
            fs = float((meta.get(orig) or {}).get("first_seen") or 0)
            it = {"started": fs if 0 < fs < deleted else None, "approx": True, "deleted": deleted, "trade": None,
                  "rel": float(ge.get("rel") or 0), "held": float(ge.get("held") or 0), "handoff": float(ge.get("handoff") or 0),
                  "coin": ge.get("coin") or {}}
            if not ge and str(cfg.get("bot_type") or "grid") not in ("dca", "dca_buy") and not cfg.get("is_demo"):
                stx = _safe(load_json, os.path.join(d, f"grid_state_{cfg.get('symbol')}.json"), default={}) or {}
                it["rel"] = round(float(stx.get("total_profit") or 0), 8)
        bt = str(cfg.get("bot_type") or "grid")
        out.append({"name": name, "folder": orig, "sym": str(cfg.get("symbol") or ""), "type": bt, "ico": _WD_E.get(bt, "🤖"),
                    "lbl": _PV_TYPE_ALL.get(bt, bt), "demo": bool(cfg.get("is_demo")),
                    "started": it.get("started"), "approx": bool(it.get("approx")), "deleted": float(it.get("deleted") or deleted),
                    "trade": it.get("trade"), "rel": round(float(it.get("rel") or 0), 8), "held": round(float(it.get("held") or 0), 8),
                    "handoff": round(float(it.get("handoff") or 0), 8), "coin": it.get("coin") or {},
                    "cfg_txt": _safe(_pv_cfg_txt, cfg, default="") or "",
                    "cfg": {k: v for k, v in cfg.items() if not _ARCH_SECRET.search(str(k))}})
    return {"ok": True, "n": len(out), "items": out[:300]}


def delete_bot(b):
'''),
    ('''        if u.path == "/api/losses":                       # 📉 v3.25.4: سجل الخسائر (يحسب بس)''',
     '''        if u.path == "/api/archive":                      # 🗄️ v3.36.18: البوتات المحذوفة (للعرض)
            return self._json(_safe(archive_view, default={"ok": False, "items": []}))
        if u.path == "/api/losses":                       # 📉 v3.25.4: سجل الخسائر (يحسب بس)'''),
    # ④ the widget: trading profit in every cell
    ('''    o = overview()
    st = o.get("stats") or {}
    rows = []
    for b in o.get("bots") or []:
        if b.get("demo"):
            continue
        t = b.get("bot_type") or "grid"
        if t in ("rec_buy", "rec_sell", "rec_va"):
            r = b.get("rec") or {}
            u, pt, td = ((r.get("base") or "") if t == "rec_sell" else "$"), r.get("profit"), r.get("today")
        elif t in ("dca", "dca_buy"):
            d = b.get("dca") or {}
            u, pt, td = ("$" if (t == "dca_buy" or d.get("is_buy")) else (d.get("base_coin") or "")), d.get("coin_profit"), None
        else:
            u, pt, td = "$", b.get("profit"), b.get("today")''',
     '''    o = overview()
    st = o.get("stats") or {}
    today = datetime.now().strftime("%Y-%m-%d")
    TN = _safe(trade_now, default={}) or {}               # 🔄 v3.36.18 (طلب المالك): ربح التداول (عادي + 💠) بكل الخانات
    _bt0 = (_safe(trade_period, today, today, default=None) or {}).get("by_bot") or {}
    _bta = (_safe(trade_period, str(st.get("first") or "") or today, today, default=None) or {}).get("by_bot") or {}
    rows = []
    for b in o.get("bots") or []:
        if b.get("demo"):
            continue
        t = b.get("bot_type") or "grid"
        if t in ("rec_buy", "rec_sell", "rec_va"):
            r = b.get("rec") or {}
            u, pt, td = ((r.get("base") or "") if t == "rec_sell" else "$"), r.get("profit"), r.get("today")
        elif t in ("dca", "dca_buy"):
            d = b.get("dca") or {}
            u, pt, td = ("$" if (t == "dca_buy" or d.get("is_buy")) else (d.get("base_coin") or "")), d.get("coin_profit"), None
        else:
            u, pt, td = "$", b.get("profit"), b.get("today")
        _k = b.get("dir")
        if u == "$" and (_k in _bta or _k in _bt0):         # ربح التداول للبوت: اليوم · كل أيامه
            _x0, _xa = _bt0.get(_k) or {}, _bta.get(_k) or {}
            td = float(_x0.get("n") or 0) + float(_x0.get("r") or 0)
            pt = float(_xa.get("n") or 0) + float(_xa.get("r") or 0)'''),
    ('''            "k": [k("ربح اليوم", o.get("today_profit")), k("هذا الشهر", st.get("mtd")), k("الإجمالي", o.get("total_profit"), False)],''',
     '''            "k": [k("ربح اليوم", TN.get("today", o.get("today_profit"))), k("هذا الشهر", st.get("mtd")),
                  k("الإجمالي", TN.get("trade_all", o.get("total_profit")), False)],'''),
    # ③ «المحافظ» ⇒ «الارتباط» · ② the archive button between 🛡️ الرقابة and 📉 الخسائر
    ('''      <button onclick="openWallets()">👛 المحافظ</button>''',
     '''      <button onclick="openWallets()" title="الارتباط: المحافظ (مفاتيح OKX) وتيليغرام">🔗 الارتباط</button>'''),
    ('''      <button id="bGuard" onclick="openGuard()" title="الرقابة: مطابقة الأرصدة والأوامر مع المنصة وكشف البوت الميت">🛡️ الرقابة</button>''',
     '''      <button id="bGuard" onclick="openGuard()" title="الرقابة: مطابقة الأرصدة والأوامر مع المنصة وكشف البوت الميت">🛡️ الرقابة</button>
      <button id="bArch" onclick="openArchive()" title="الأرشيف: البوتات المحذوفة — إعداداتها ووقت تشغيلها وربحها">🗄️ الأرشيف</button>'''),
    ('''  <div class="phead"><h2>👛 المحافظ وتيليغرام</h2><button class="x" onclick="closePage('wallets')">✕</button></div>''',
     '''  <div class="phead"><h2>🔗 الارتباط — المحافظ وتيليغرام</h2><button class="x" onclick="closePage('wallets')">✕</button></div>'''),
    ('''سوِّ مفتاح جديد، اربطه بـIP السيرفر، وحدّثه من 👛 المحافظ ✏️''', '''سوِّ مفتاح جديد، اربطه بـIP السيرفر، وحدّثه من 🔗 الارتباط ✏️'''),
    ('''        TG_DIAG["last"] = "❌ ما كو توكن أو Chat ID محفوظ — افتح 👛 المحافظ واحفظهما"''',
     '''        TG_DIAG["last"] = "❌ ما كو توكن أو Chat ID محفوظ — افتح 🔗 الارتباط واحفظهما"'''),
    ('''        return False, "❌ ما كو توكن أو Chat ID محفوظ — افتح 👛 المحافظ واحفظهما"''',
     '''        return False, "❌ ما كو توكن أو Chat ID محفوظ — افتح 🔗 الارتباط واحفظهما"'''),
    ('''"👛 المحفظة مو موجودة — أضفها من 👛 المحافظ أو اختر غيرها"''', '''"👛 المحفظة مو موجودة — أضفها من 🔗 الارتباط أو اختر غيرها"'''),
    ('''ماكو محفظة — أضف محفظة من 👛 المحافظ أو انشر بوت حقيقي''', '''ماكو محفظة — أضف محفظة من 🔗 الارتباط أو انشر بوت حقيقي'''),
    ('''ماكو محافظ بعد — أضفها من 👛 المحافظ''', '''ماكو محافظ بعد — أضفها من 🔗 الارتباط'''),
    ('''أضفه من 👛 المحافظ حتى تشوف كل عملاته.''', '''أضفه من 🔗 الارتباط حتى تشوف كل عملاته.'''),
    # ① the cards: the run time + the day it started (bots · DCA · the accumulator)
    ('''  // ⏱️ زمن التشغيل + المعدلات (بالدولار للجرد)
  if(R.age){
    const ad=b.age_days||0;
    R.age.textContent=ad>=1?(ad>=30?(ad/30).toFixed(1)+' شهر':ad.toFixed(1)+' يوم'):(ad>0?Math.round(ad*24)+' ساعة':'—');''',
     '''  // ⏱️ زمن التشغيل (من تاريخ التشغيل الثابت — v3.36.18) + المعدلات (بالدولار للجرد)
  if(R.age){
    R.age.textContent=stAge(b);R.age.title=stAgeT(b);'''),
    ('''  // ⏱️ زمن التشغيل + معدلات الربح (يومي/شهري/سنوي)
  if(R.age){
    const ad=b.age_days||0;
    R.age.textContent=ad>=1?(ad>=30?(ad/30).toFixed(1)+' شهر':ad.toFixed(1)+' يوم'):(ad>0?Math.round(ad*24)+' ساعة':'—');''',
     '''  // ⏱️ زمن التشغيل (من تاريخ التشغيل الثابت — v3.36.18) + معدلات الربح (يومي/شهري/سنوي)
  if(R.age){
    R.age.textContent=stAge(b);R.age.title=stAgeT(b);'''),
    ('''        <div class="row"><span class="ic">🕒</span><span class="nm">آخر شراء</span><b class="num" data-k="alast" style="font-size:10.5px">—</b></div>''',
     '''        <div class="row"><span class="ic">🕒</span><span class="nm">آخر شراء</span><b class="num" data-k="alast" style="font-size:10.5px">—</b></div>
        <div class="row"><span class="ic">⏱️</span><span class="nm">التشغيل</span><b class="num" data-k="aage" style="font-size:10.5px">—</b></div>'''),
    ('''    R.acnt.textContent=`${a.n_buys||0} شراء · ${a.n_sells||0} بيع`;''',
     '''    R.acnt.textContent=`${a.n_buys||0} شراء · ${a.n_sells||0} بيع`;
    if(R.aage){R.aage.textContent=stAge(a);R.aage.title=stAgeT(a)}'''),
    # the helpers + the archive page
    ('''async function openLosses(){''',
     '''/* ⏱️ v3.36.18: زمن التشغيل من تاريخ ثابت (started — تحفظه اللوحة مرة وحدة) · المدة + يوم البداية · التلميح: التاريخ والساعة */
function stAge(x){const t=+(x&&x.started)||0;if(!t)return '—';const s=Math.max(0,Date.now()/1000-t),d=s/86400,
  dur=d>=30?(d/30).toFixed(1)+' شهر':d>=1?d.toFixed(1)+' يوم':s>=3600?Math.floor(s/3600)+' ساعة':Math.max(1,Math.floor(s/60))+' دقيقة',
  D=new Date(t*1000),p=n=>String(n).padStart(2,'0');
  return dur+' · منذ '+(D.getFullYear()!==new Date().getFullYear()?D.getFullYear()+'-':'')+p(D.getMonth()+1)+'-'+p(D.getDate())}
function stAgeT(x){const t=+(x&&x.started)||0;if(!t)return '';const D=new Date(t*1000),p=n=>String(n).padStart(2,'0');
  return '⏱️ بدأ التشغيل: '+D.getFullYear()+'-'+p(D.getMonth()+1)+'-'+p(D.getDate())+' '+p(D.getHours())+':'+p(D.getMinutes())+' — تاريخ ثابت تحفظه اللوحة (لا يعتمد على الملفات)'}
/* 🗄️ v3.36.18: الأرشيف — البوتات المحذوفة (إعداداتها · تشغيلها · حذفها · مدتها · ربحها) · للعرض فقط */
async function openArchive(){
  showModal(`<h2>🗄️ الأرشيف — البوتات المحذوفة</h2><div id="ar_body" style="color:var(--mut);font-size:12.5px;padding:18px;text-align:center">${LDR('جاري التحميل…')}</div>
    <div class="mbtns"><button onclick="hideModal()">إغلاق</button></div>`);
  let V=null;try{V=await api('/api/archive')}catch(e){V=null}
  const el=$('#ar_body');if(!el)return;
  if(!V||!V.ok){el.innerHTML='⚠️ تعذّر تحميل الأرشيف';return}
  if(!(V.items||[]).length){el.innerHTML='ماكو بوت محذوف بعد.';return}
  el.style.textAlign='start';el.style.padding='0';el.style.color='var(--tx)';
  const box='background:var(--bg1);border:1px solid var(--line2);border-radius:11px;padding:10px;margin-top:9px';
  const p=n=>String(n).padStart(2,'0'),dt=t=>{if(!t)return '—';const D=new Date(t*1000);return D.getFullYear()+'-'+p(D.getMonth()+1)+'-'+p(D.getDate())+' '+p(D.getHours())+':'+p(D.getMinutes())};
  const dur=s=>{const d=s/86400;return d>=30?(d/30).toFixed(1)+' شهر':d>=1?d.toFixed(1)+' يوم':s>=3600?Math.floor(s/3600)+' ساعة':Math.max(1,Math.floor(s/60))+' دقيقة'};
  el.innerHTML=`<div style="${box};font-size:11.5px;color:var(--mut);line-height:1.8">🗄️ <b style="color:var(--tx)">${V.n}</b> بوت محذوف — مجلد كل واحد محفوظ بـ<b>_archive</b> (إعداداته وسجله) · للعرض فقط</div>`
   +V.items.map(x=>{const pr=[];
     if(x.trade!=null)pr.push(`🔄 ربح التداول <b class="bidi">${(+x.trade).toFixed(4)}$</b>`);
     if(+x.rel)pr.push(`💵 المحرر <b class="bidi">${(+x.rel).toFixed(4)}$</b>`);
     if(+x.held)pr.push(`💠 كان داخل الأوامر <b class="bidi">${(+x.held).toFixed(4)}$</b>`);
     if(+x.handoff)pr.push(`🪙 للمُراكِم <b class="bidi">${(+x.handoff).toFixed(4)}$</b>`);
     for(const[c,v]of Object.entries(x.coin||{}))if(+v)pr.push(`🪙 <b class="bidi">${(+v).toFixed(8)} ${gEsc(c)}</b>`);
     return `<div class="arch" style="${box}">
       <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap"><b>${x.ico||'🤖'} ${gEsc(x.sym)} <span style="color:var(--mut2);font-weight:400;font-size:11.5px">${gEsc(x.lbl||x.type)}${x.demo?' · 🧪 تجريبي':''}</span></b>
         <span style="font-size:11px;color:var(--mut2)">📁 ${gEsc(x.folder)}</span></div>
       <div style="font-size:11.5px;line-height:1.9;margin-top:4px">▶️ بدأ: <b class="bidi">${x.started?dt(x.started)+(x.approx?' (تقريبي)':''):'—'}</b> · ⏹ حُذف: <b class="bidi">${dt(x.deleted)}</b>${x.started?` · ⏱️ اشتغل <b>${dur(x.deleted-x.started)}</b>`:''}</div>
       <div style="font-size:11.5px;line-height:1.9">${pr.length?pr.join(' · '):'<span style="color:var(--mut2)">بلا ربح مسجّل</span>'}</div>
       <details style="margin-top:4px"><summary style="cursor:pointer;font-size:11.5px;color:var(--cyan)">⚙️ الإعدادات</summary>
         <div style="font-size:11px;color:var(--mut);margin:4px 0">${gEsc(x.cfg_txt||'')}</div>
         <pre style="font-size:10.5px;white-space:pre-wrap;direction:ltr;text-align:left;margin:0">${gEsc(JSON.stringify(x.cfg||{},null,1))}</pre></details></div>`}).join('');
}
async function openLosses(){'''),
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
