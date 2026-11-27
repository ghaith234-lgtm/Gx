# p152 — v3.36.79 🔀 «شبكة عملتين» · ⑦ its card (the owner 27-11: «سوي البوت وضيفه» · «المهم تحسب كل العمولة»)
#   · the card: profit in the MAIN coin (≈ $ beside it, never «$» on an XRP number) · the ratio now · the next buy / next sell · today ·
#     the levels · what the bot holds (main · other · the dollar between the two legs) · its value in the main coin since the start ·
#     the age · the daily / monthly / yearly rate in the main coin · buttons ⏸ buy · ⏸ sell · 📜 · 🪜 the levels · ⏹/▶️ · ⚙ · 🗑
#   · the four skins read it (skKind «pair» + its skModel branch) · the compact row shows today in the main coin
#   · ⚙ its own details window · 🪜 the nearest 30 levels each side · ⏸/▶️ (resume asks first, with what it will swap)
#   · the control: pause/resume by the RATIO (control fields only — the engine swaps) · the grid-only buttons refused with a clear line
#   · the delete waits for a swap in flight: the bot finishes it (the dollar back to a coin) then withdraws — never deleted mid-swap
#   · it joins every label/icon list (compact row · type names · archive · widgets · re-deploy from 🗄️ the archive)
#   · its XRP profit stays out of the grid cards' dollar bench and out of the dollar «تحتاج» counter
#   python3 devtests/step/patches/p152_pair_card.py Holy_Dashboard.pyw
import os, sys

R = [
    # ── Python: labels / icons ──────────────────────────────────────────────────────────────────────────────────────────────
    ('''"rec_buy": "🔁 دوري شرائي", "rec_sell": "🔁 دوري بيعي", "rec_va": "💹 مسار القيمة", "acc": "🪙 مُراكِم"}''',
     '''"rec_buy": "🔁 دوري شرائي", "rec_sell": "🔁 دوري بيعي", "rec_va": "💹 مسار القيمة", "grid_pair": "🔀 شبكة عملتين", "acc": "🪙 مُراكِم"}'''),
    ('''                "rec_buy": "دوري شرائي", "rec_sell": "دوري بيعي", "rec_va": "مسار القيمة"}''',
     '''                "rec_buy": "دوري شرائي", "rec_sell": "دوري بيعي", "rec_va": "مسار القيمة", "grid_pair": "شبكة عملتين"}'''),
    ('''"rec_buy": "🔁", "rec_sell": "🔂", "rec_va": "💹"}''', '''"rec_buy": "🔁", "rec_sell": "🔂", "rec_va": "💹", "grid_pair": "🔀"}'''),
    ('''"rec_buy": "🟢", "rec_sell": "🔴", "rec_va": "💹"}''', '''"rec_buy": "🟢", "rec_sell": "🔴", "rec_va": "💹", "grid_pair": "🔀"}'''),
    # ── ♻️ re-deploy from the archive ──────────────────────────────────────────────────────────────────────────────────────────
    ('''            "rec_buy": "rec", "rec_sell": "rec", "rec_va": "va"}''',
     '''            "rec_buy": "rec", "rec_sell": "rec", "rec_va": "va", "grid_pair": "pair"}'''),
    ('''    else:                                                             # 💹 مسار القيمة''',
     '''    elif form == "pair":                                              # 🔀 v3.36.79: نسبة البداية فارغة = النسبة لحظة النشر
        _o, _m = (sym.split("-") + [""])[:2]
        _g, _mv, _r0 = n("grid_percentage"), n("main_value"), n("forced_base_ratio")
        _ao = sum(_mv / (_r0 * (1 + _g) ** j) for j in range(int(n("up_levels")))) if _r0 > 0 and _g > 0 else 0.0
        P.update(main=_m, other=_o, step_pct=round(_g * 100, 6), main_value=_mv, main_amount=round(_mv * int(n("down_levels")), 10),
                 other_amount=float(f"{_ao:.8g}") if _ao > 0 else "", profit_to=str(c.get("profit_to") or "main"))
    else:                                                             # 💹 مسار القيمة'''),
    ('''        if str(c.get("bot_type") or "") in ("dca", "dca_buy"):
            return (f"أساس''', '''        if str(c.get("bot_type") or "") == "grid_pair":          # 🔀 v3.36.79
            _o, _m = (str(c.get("symbol") or "").split("-") + [""])[:2]
            return (f"{_o}/{_m} · الخطوة {float(c.get('grid_percentage') or 0) * 100:g}% · {float(c.get('main_value') or 0):g} {_m} لكل شراء · "
                    f"{int(float(c.get('down_levels') or 0))} تحت · {int(float(c.get('up_levels') or 0))} فوق")
        if str(c.get("bot_type") or "") in ("dca", "dca_buy"):
            return (f"أساس'''),
    # ── the card's data: the nearest levels (not all the 2,000 every tick) · the pause state · the sales count ──────────────
    ('''    S = st.get("slots") or {}
    lv = sorted(({"j": s.get("j"), "bp": s.get("bp"), "sp": s.get("sp"), "side": s.get("side"),
                  "q": round(f(s.get("q")) + f(s.get("dq")), 12)} for s in S.values() if isinstance(s, dict)), key=lambda x: int(x["j"] or 0))''',
     '''    S = st.get("slots") or {}
    _sl = [s for s in S.values() if isinstance(s, dict)]
    _lv = lambda s: {"j": s.get("j"), "bp": s.get("bp"), "sp": s.get("sp"), "side": s.get("side"),
                     "q": round(f(s.get("q")) + f(s.get("dq")), 12), "n": int(s.get("n") or 0)}
    _up = sorted((s for s in _sl if s.get("side") == "sell"), key=lambda s: f(s.get("sp")))[:30]     # أقرب 30 بيع فوق
    _dn = sorted((s for s in _sl if s.get("side") == "buy"), key=lambda s: -f(s.get("bp")))[:30]     # أقرب 30 شراء تحت
    lv = sorted((_lv(s) for s in _up + _dn), key=lambda x: int(x["j"] or 0))'''),
    ('''"levels": lv[:600], "n_levels": len(lv),''',
     '''"levels": lv, "n_levels": len(_sl), "sales": sum(int(s.get("n") or 0) for s in _sl),
            "bf": f(st.get("buy_floor")), "sc": f(st.get("sell_ceiling")), "pb": bool(st.get("pause_buy")), "ps": bool(st.get("pause_sell")),'''),
    # ── the control: pause/resume by the ratio · the grid-only buttons refused ──────────────────────────────────────────────
    ('''    if b["cfg"].get("bot_type") == "grid_step":                 # 🪜 v3.36.15
        if action == "reinvest":''', '''    if b["cfg"].get("bot_type") == "grid_pair":                 # 🔀 v3.36.79: الإيقاف/الاستئناف بالنسبة (حقول التحكم فقط — المحرك يبدّل)
        if action in ("pause_buy", "pause_sell", "resume_buy", "resume_sell", "accum_buy", "accum_sell"):
            return _pair_pause(b, action)
        if action in ("guard", "reinvest", "edit", "rebuild", "buy_now", "pause", "resume", "rilad", "reinvest_withdraw", "temp_open", "temp_info"):
            return {"ok": False, "msg": "🔀 هذا الزر غير متاح لـ«شبكة عملتين» — لتغيير إعداداته احذفه وانشره من جديد (🗄️ الأرشيف يعبّئ إعداداته)"}
    if b["cfg"].get("bot_type") == "grid_step":                 # 🪜 v3.36.15
        if action == "reinvest":'''),
    # ── the delete: never mid-swap ──────────────────────────────────────────────────────────────────────────────────────────
    ('''def delete_bot(b):
    with _demo_quiet(b):''', '''def _pair_pause(b, action):
    """🔀 v3.36.79: ⏸ الشراء/البيع من النسبة الآن · ▶️ الاستئناف — حقول التحكم فقط (المحرك يدمجها ويقرّر ويبدّل)"""
    sp, _, _ = paths_of(b)
    st = read_retry(sp)
    if st is None:
        return {"ok": False, "msg": "تعذّرت قراءة ملف الحالة — أعد المحاولة بعد ثانية"}
    buy = action.endswith("_buy")
    lk, fk = ("buy_floor", "pause_buy") if buy else ("sell_ceiling", "pause_sell")
    w = "الشراء" if buy else "البيع"
    on = float(st.get(lk) or 0) > 0 or bool(st.get(fk))
    if action.startswith("accum"):
        action = ("resume_" if on else "pause_") + ("buy" if buy else "sell")
    if action.startswith("pause"):
        if on:
            return {"ok": True, "msg": f"⏸ {w} موقوف أصلاً"}
        try:
            r = float(PX.get(b["symbol"]) or st.get("ratio") or 0)
        except Exception:
            r = 0.0
        upd = {lk: float(f"{r:.10g}"), fk: False} if r > 0 else {fk: True}
        msg = (f"⏸ أُوقف {w} من النسبة {r:.8g}" if r > 0 else f"⏸ أُوقف {w} من النسبة الحالية") \\
            + (" — لا شراء تحتها" if buy else " — لا بيع فوقها") + "، والمستويات تبقى كما هي حتى الاستئناف"
    else:
        if not on:
            return {"ok": True, "msg": f"▶️ {w} يعمل أصلاً"}
        upd = {lk: 0, fk: False}
        msg = f"▶️ استُؤنف {w} — يكمل من حيث وصلت النسبة، مستوى بعد مستوى"
    if not save_state_keys(sp, upd):
        st.update(upd)
        save_json_atomic(sp, st)
    return {"ok": True, "msg": msg}


def _pair_del_wait(b):
    """🔀 v3.36.79: «شبكة عملتين» لا تُحذف وتبديلها بالطريق — الدولار بين الرجلين يعود عملة أولاً (البوت يكمّله بنفسه ثم ينسحب)"""
    sp, _, _ = paths_of(b)
    st = read_retry(sp)
    if st is None:
        return {"ok": False, "msg": "⛔ لم يُحذف: تعذّرت قراءة ملف الحالة — أعد المحاولة بعد ثانية"}
    if is_alive(b["dir"], sp)[0] and not st.get("destruct_done"):
        if not st.get("self_destruct"):
            _write_state_flag(sp, "self_destruct", True)
        for _ in range(14):
            time.sleep(1)
            st = read_retry(sp) or st
            if st.get("destruct_done") or not is_alive(b["dir"], sp)[0]:
                break
    if not st.get("op") or st.get("destruct_done"):
        return None
    usd = float(st.get("usd_booked") or 0)
    if is_alive(b["dir"], sp)[0]:
        return {"ok": False, "msg": f"⏳ لم يُحذف بعد: البوت يُكمل تبديلاً جارياً ({usd:.4f} USDT بين العملتين) ليعود الدولار عملة، "
                                    "ثم ينسحب — أعد الحذف بعد قليل"}
    return {"ok": False, "msg": f"⛔ لم يُحذف: يوجد تبديل غير مكتمل ({usd:.4f} USDT بين العملتين) — شغّل البوت ليُكمله، ثم احذفه"}


def delete_bot(b):
    if str((b.get("cfg") or {}).get("bot_type") or "") == "grid_pair":      # 🔀 v3.36.79: لا حذف وتبديله بالطريق
        _w = _pair_del_wait(b)
        if _w is not None:
            return _w
    with _demo_quiet(b):'''),
    ('''    cfg = b["cfg"]; sym = b["symbol"]; cancelled = 0; via = ""''',
     '''    cfg = b["cfg"]; sym = b["symbol"]; cancelled = 0; via = ""
    if str(cfg.get("bot_type") or "") == "grid_pair":        # 🔀 v3.36.79: لا أوامر قاعدة على المنصة — الحذف ينتظر تبديله الجاري
        return delete_bot(b)'''),
    # ── JS: labels / icons / compact row ────────────────────────────────────────────────────────────────────────────────────
    ("""  rec_sell:'🔂 دوري بيعي',rec_va:'💹 مسار القيمة'};""", """  rec_sell:'🔂 دوري بيعي',rec_va:'💹 مسار القيمة',grid_pair:'🔀 شبكة عملتين'};"""),
    ("""rec_va:'var(--green-rgb)',acc:'var(--green-rgb)'};""", """rec_va:'var(--green-rgb)',grid_pair:'var(--blue-rgb)',acc:'var(--green-rgb)'};"""),
    ("""  if(b.pause_buy||d.paused||r.paused)return ['⏸ موقوف الشراء','tp'];""",
     """  if(b.pause_buy||d.paused||r.paused||(b.pair&&(+b.pair.bf>0||b.pair.pb)))return ['⏸ موقوف الشراء','tp'];"""),
    ("""t==='rec_sell'?((b.rec||{}).base||b.symbol.split('-')[0]):'';""",
     """t==='rec_sell'?((b.rec||{}).base||b.symbol.split('-')[0]):t==='grid_pair'?((b.pair||{}).main||b.symbol.split('-')[1]||''):'';"""),
    ("""rec_sell:'دوري بيعي',rec_va:'💹 مسار القيمة'};""", """rec_sell:'دوري بيعي',rec_va:'💹 مسار القيمة',grid_pair:'🔀 شبكة عملتين'};"""),
    ("""rec_buy:'🔁',rec_sell:'🔂',rec_va:'💹'}[t]||'🤖');""", """rec_buy:'🔁',rec_sell:'🔂',rec_va:'💹',grid_pair:'🔀'}[t]||'🤖');"""),
    ("""  if(t==='grid_step')return '🪜 شبكي متدرج';""", """  if(t==='grid_step')return '🪜 شبكي متدرج';
  if(t==='grid_pair')return '🔀 شبكة عملتين';"""),
    ("""  const gs=(all||[]).filter(b=>b.bot_type!=='dca'&&b.bot_type!=='dca_buy'&&!b.demo""",
     """  const gs=(all||[]).filter(b=>b.bot_type!=='dca'&&b.bot_type!=='dca_buy'&&b.bot_type!=='grid_pair'&&!b.demo"""),
    ("""  let profits=allBots.filter(x=>!x.demo).map(x=>x.profit);""",
     """  let profits=allBots.filter(x=>!x.demo&&x.bot_type!=='grid_pair').map(x=>x.profit);   // 🔀 v3.36.79: ربحه بالرئيسية — خارج مقارنة الدولار"""),
    # ── JS: the card ────────────────────────────────────────────────────────────────────────────────────────────────────────
    ("""  if(b.bot_type==='rec_va')return buildVaCard(b,i);   // 💹 v3.34.0""",
     """  if(b.bot_type==='rec_va')return buildVaCard(b,i);   // 💹 v3.34.0
  if(b.bot_type==='grid_pair')return buildPairCard(b,i);   // 🔀 v3.36.79"""),
    ("""  if(b.bot_type==='rec_va')return updVaCard(el,b);""", """  if(b.bot_type==='rec_va')return updVaCard(el,b);
  if(b.bot_type==='grid_pair')return updPairCard(el,b);"""),
    ("""  if(b&&b.bot_type==='rec_va')return vaDetails(b);   // 💹 v3.34.0""", """  if(b&&b.bot_type==='rec_va')return vaDetails(b);   // 💹 v3.34.0
  if(b&&b.bot_type==='grid_pair')return pairDetails(b);   // 🔀 v3.36.79"""),
    ("""if(t==='grid_plus')return 'plus';if(t==='grid_range')return 'range';if(t==='grid_step')return 'step';return 'grid'}""",
     """if(t==='grid_plus')return 'plus';if(t==='grid_range')return 'range';if(t==='grid_step')return 'step';if(t==='grid_pair')return 'pair';return 'grid'}"""),
    ("""  else if(kd==='va'||kd==='hyb'){""", """  else if(kd==='pair'){                                                     // 🔀 v3.36.79: «شبكة عملتين» — بالعملة الرئيسية
    const P=b.pair||{},MN=pairMN(b),O=pairON(b),pbz=+P.bf>0||!!P.pb,psz=+P.sc>0||!!P.ps;
    M.sym=O+'/'+MN;M.kind='🔀 شبكة عملتين';M.sub=skText(el,'mode');
    M.st=!b.alive?'متوقف':(P.destructing?'ينسحب':(pbz&&psz?'الشراء والبيع موقوفان':pbz?'الشراء موقوف':psz?'البيع موقوف':'نشط'));
    M.stc=!b.alive?'off':((pbz||psz||P.destructing)?'wait':'');
    M.big=pairQ(+P.profit||0);M.unit=MN;M.lbl='💎 الربح بالعملة الرئيسية';
    M.pl=['اليوم',pairS(P.today)+' '+MN];M.pc=sign(P.today);
    M.px=+((window.JPX&&JPX[b.symbol])||P.ratio||0);
    const L=P.levels||[];
    M.gfx=skLadder(L.filter(l=>l.side==='sell').map(l=>({p:+l.sp,q:+l.q||0})),L.filter(l=>l.side==='buy').map(l=>({p:+l.bp,q:(+P.mv||0)/(+l.bp||1)})),M.px,
      {dn:M.dn,empty:'لا مستويات بعد'});
    M.cap=`🔀 المستويات التالية بالنسبة — يراقبها البوت ويبدّل عبر الدولار لحظياً (لا أوامر قاعدة على المنصة) · ${P.n_buy||0} شراء · ${P.n_sell||0} بيع`;
    M.chips=(P.in_flight?'<span class="chip gOn">⏳ تبديل جارٍ عبر الدولار</span>':'')+(pbz?`<span class="chip">⏸ لا شراء تحت ${pairQ(+P.bf||+P.ratio||0,7)}</span>`:'')
      +(psz?`<span class="chip">⏸ لا بيع فوق ${pairQ(+P.sc||+P.ratio||0,7)}</span>`:'')+(P.sales?`<span class="chip">🔴 ${P.sales} بيعة</span>`:'');
    M.m=[['🟢 الشراء القادم',skText(el,'nbuy')],['🔴 البيع القادم',skText(el,'nsell')],['💰 ما يملكه البوت',skText(el,'books')],['👛 قيمته بالرئيسية',skText(el,'wal')],
      ['💵 الربح بالدولار الآن',skText(el,'usd')],['التشغيل',skText(el,'age')],['المعدل يومي / شهري / سنوي',skText(el,'rates')]];
    M.main=pw();M.ic=[skBtn(el,'ab'),skBtn(el,'as'),skBtn(el,'hist','📜 السجل')];
    M.menu=[ME('🪜 المستويات','lddr'),{k:'drawer',t:'⚙ تفاصيل البوت'},ME('🗑 حذف نهائي','del',1)];
    M.note=skText(el,'status')}
  else if(kd==='va'||kd==='hyb'){"""),
    # ── JS: ♻️ re-deploy from the archive ───────────────────────────────────────────────────────────────────────────────────
    ("""X={grid:'n',step:'st',dca:'dn',dcap:'dn',rec:'rd',va:'vd'}[F];""", """X={grid:'n',step:'st',dca:'dn',dcap:'dn',rec:'rd',va:'vd',pair:'pa'}[F];"""),
    ("""    vaGuardSync();vaSync()}
  else return null;""", """    vaGuardSync();vaSync()}
  else if(F==='pair')await openDeployPair(P);          // 🔀 v3.36.79: نسبة البداية فارغة = النسبة لحظة النشر
  else return null;"""),
    # ── CSS ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    (""".dcatag.rectag{background:rgb(var(--cyan-rgb)/.14);color:var(--cyan);border-color:rgb(var(--cyan-rgb)/.35)}""",
     """.dcatag.rectag{background:rgb(var(--cyan-rgb)/.14);color:var(--cyan);border-color:rgb(var(--cyan-rgb)/.35)}
.dcatag.pairtag,.card .dcatag.pairtag{background:rgb(var(--blue-rgb)/.14);color:var(--blue);border-color:rgb(var(--blue-rgb)/.35)}
.pair .dcacell small{display:block;font-size:10.5px;color:var(--mut2);margin-top:2px}
.pair .rcrow small{font-size:10px;color:var(--mut2)}
.pairlv tr.pmid td{color:var(--cyan);font-weight:600;text-align:center;background:rgb(var(--cyan-rgb)/.08)}"""),
]

# the card's own functions — after the periodic card's update (one block)
JS_ANCHOR = """function recSell(b,id){"""
JS = r"""/* 🔀 v3.36.79: بطاقة «شبكة عملتين» — كل الأرقام بالعملة الرئيسية (لا «$» على رقم XRP) · من حالة المحرك فقط (b.pair) */
function pairMN(b){const P=(b&&b.pair)||{};return P.main||String((b&&b.symbol)||'').split('-')[1]||''}
function pairON(b){const P=(b&&b.pair)||{};return P.other||String((b&&b.symbol)||'').split('-')[0]||''}
function pairQ(v,d){v=+v||0;if(!v)return '0';const a=Math.abs(v);if(a>=1e5)return v.toFixed(2);
  const t=v.toPrecision(d||6);return t.indexOf('e')>=0?v.toFixed(10).replace(/0+$/,'').replace(/[.]$/,''):String(+t)}
function pairS(v,d){v=+v||0;return (v>0?'+':v<0?'−':'')+pairQ(Math.abs(v),d)}
function buildPairCard(b,i){
  const el=document.createElement('div');el.className='card dca pair';el.style.setProperty('--i',i);el.dataset.dir=b.dir;
  const MN=gEsc(pairMN(b)),O=gEsc(pairON(b)),ol=O.toLowerCase();
  el.innerHTML=`
  <div class="dcahead">
    <span class="sym"><img class="coin" src="https://assets.coincap.io/assets/icons/${ol}@2x.png" data-alt="https://static.okx.com/cdn/oksupport/asset/currency/icon/${ol}.png" onerror="cfb(this,'${O}')"> ${O}/${MN}</span>
    <span class="dcatag pairtag">🔀 شبكة عملتين</span>
    <span class="pill off" data-k="pill">—</span><span class="hbadge" data-k="hb" style="display:none;cursor:pointer"></span>
    <span class="rcmode" data-k="mode">—</span></div>
  <div class="dcabody">
    <div class="dcatop">
      <div class="dcacell"><span class="dl" title="الربح المحقق من بيعات أُغلقت — صافياً بعد العمولات الأربع (رجلا الشراء ورجلا البيع) وفرق السعر">💎 الربح (${MN})</span><b class="num dcacoin" data-k="profit">—</b></div>
      <div class="dcacell"><span class="dl" title="كم ${MN} يساوي ${O} واحد الآن — من سعري العملتين بالدولار">⚖️ النسبة الآن</span><b class="num dcaprice" data-k="cp">—</b></div>
    </div>
    <div class="dcatop" style="grid-template-columns:1fr 1fr 1fr">
      <div class="dcacell"><span class="dl" title="أقرب مستوى شراء تحت النسبة — حين تنزل إليه يدفع كمية الشراء من ${MN} ويشتري بها ${O}">🟢 الشراء القادم</span><b class="num" data-k="nbuy" style="font-size:12.5px">—</b></div>
      <div class="dcacell"><span class="dl" title="أقرب مستوى بيع فوق النسبة — حين تصعد إليه يبيع ما اشتراه ويعيد ${MN} مع الربح">🔴 البيع القادم</span><b class="num" data-k="nsell" style="font-size:12.5px">—</b></div>
      <div class="dcacell"><span class="dl">📅 اليوم</span><b class="num" data-k="today" style="font-size:12.5px">—</b></div>
    </div>
    <div class="rcrow"><span class="dl" title="مستويات تنتظر الشراء · مستويات تنتظر البيع (اشترت ولم تبع بعد) · البيعات المكتملة">📦 المستويات</span><b data-k="lv">—</b></div>
    <div class="rcrow"><span class="dl" title="الربح محسوباً بسعر ${MN} الآن — للعرض فقط: الربح نفسه بالعملة الرئيسية">💵 الربح بالدولار الآن</span><b data-k="usd">—</b></div>
    <div class="rcrow"><span class="dl" title="ما يحسبه البوت له من محفظتك: الرئيسية والثانية، والدولار بين رجلي تبديل جارٍ (لا يحسبه أي بوت آخر حراً)">💰 ما يملكه البوت</span><b class="num" data-k="books">—</b></div>
    <div class="rcrow"><span class="dl" title="ما يملكه البوت محسوباً كله بالعملة الرئيسية بالنسبة الآن — مقارنة ببدايته (الربح وتذبذب النسبة معاً)">👛 قيمته بالرئيسية</span><b class="num" data-k="wal">—</b></div>
    <div class="rcrow"><span class="dl" title="منذ تاريخ تشغيل البوت">⏱️ التشغيل</span><b data-k="age" style="font-size:11.5px">—</b></div>
    <div class="rcrow"><span class="dl" title="الربح المحقق ÷ أيام التشغيل (بعد نصف يوم) — الشهري ×30 والسنوي ×365 تقديريان · بالعملة الرئيسية">📈 معدل يومي / شهري / سنوي</span><b class="num" data-k="rates">—</b></div>
    <div class="dcaopts"><button class="dcashield" data-k="ab">—</button><button class="dcalast" data-k="as">—</button></div>
    <div class="dcabtns" style="grid-template-columns:1fr 1fr auto auto auto">
      <button data-k="hist">📜 السجل</button>
      <button data-k="lddr">🪜 المستويات</button>
      <button data-k="pw">—</button>
      <button onclick="openDrawer('${b.dir}')" class="cset" title="⚙ تفاصيل البوت">⚙</button>
      <button data-k="del" class="danger" title="حذف نهائي — ينتظر إكمال أي تبديل جارٍ">🗑</button>
    </div>
    <div class="dcastatus" data-k="status">—</div>
  </div>`;
  const R={};el.querySelectorAll('[data-k]').forEach(x=>R[x.dataset.k]=x);el._r=R;el._alive=b.alive;
  const cur=()=>botOf(b.dir)||b;
  R.ab.onclick=()=>pairPause(cur(),'buy');
  R.as.onclick=()=>pairPause(cur(),'sell');
  R.hist.onclick=()=>botHist(cur());
  R.lddr.onclick=()=>pairLevels(cur());
  R.pw.onclick=()=>ctl(b.dir,el._alive?'stop':'start');
  R.del.onclick=()=>confirmPurge(b.dir);
  return el}
function updPairCard(el,b){
  const R=el._r,P=b.pair||{},MN=pairMN(b),O=pairON(b);el._alive=b.alive;
  const cp=+((window.JPX&&JPX[b.symbol])||P.ratio||0),pbz=+P.bf>0||!!P.pb,psz=+P.sc>0||!!P.ps;
  const prevCp=el._lastcp;
  if(prevCp!=null&&cp!==prevCp&&R.cp){R.cp.classList.remove('up','dn');R.cp.classList.add(cp>prevCp?'up':'dn')}
  el._lastcp=cp;
  R.pill.textContent=b.alive?'● نشط':'○ متوقف';R.pill.className='pill '+(b.alive?'on':'off');
  if(R.hb){const H=b.health||{};let s='',c='',t='';
    if(H.state==='bad'){s='🚨';c='bad';t=`${H.fails_1h} أمر مرفوض آخر ساعة`}
    else if(H.state==='warn'){s='⚠️';c='warn';t=`${H.fails_1h} رفض آخر ساعة`}
    if(s){R.hb.style.display='';R.hb.textContent=s;R.hb.className='hbadge '+c;R.hb.title=t;R.hb.onclick=(ev)=>{ev.stopPropagation();showHealth(b)}}
    else R.hb.style.display='none'}
  const PT={main:MN,other:O,half:'نصفان'};
  R.mode.textContent=`📏 ${pairQ((+P.g||0)*100)}% · ${pairQ(P.mv)} ${MN} لكل شراء · 💎 إلى ${PT[P.pt]||MN}`;
  R.profit.innerHTML=`<span dir="ltr">${pairS(P.profit)} ${gEsc(MN)}</span>`;R.profit.className='num '+((+P.profit||0)>=0?'dcacoin':'dcaloss');
  R.usd.innerHTML=P.profit_usd!=null?`<span dir="ltr">≈ ${(+P.profit_usd).toFixed(2)}$${(+P.profit_other||0)>0?` + ${pairQ(P.profit_other)} ${gEsc(O)}`:''}</span>`:'—';
  R.cp.textContent=cp?pairQ(cp,8):'—';R.cp.title=cp?`${O} واحد = ${pairQ(cp,8)} ${MN}`+((+P.px_other||0)>0&&(+P.px_main||0)>0?` · ${O} ${f4(+P.px_other)}$ · ${MN} ${f4(+P.px_main)}$`:''):'';
  const dist=r=>cp>0&&r>0?` <small dir="ltr">${((r/cp-1)*100>0?'+':'')}${((r/cp-1)*100).toFixed(2)}%</small>`:'';
  const nb=P.next_buy,ns=P.next_sell;
  R.nbuy.innerHTML=pbz?'⏸ موقوف':(nb?`<span dir="ltr">${pairQ(nb.ratio,7)}</span>${dist(+nb.ratio)}`:((+P.main_book||0)>0?'—':'لا رئيسية حرّة'));
  R.nsell.innerHTML=psz?'⏸ موقوف':(ns?`<span dir="ltr">${pairQ(ns.ratio,7)}</span>${dist(+ns.ratio)}`:'—');
  R.nbuy.title=nb?`يدفع ${pairQ(nb.main)} ${MN} حين تنزل النسبة إلى ${pairQ(nb.ratio,8)}`:'';
  R.nsell.title=ns?`يبيع ${pairQ(ns.qty)} ${O} حين تصعد النسبة إلى ${pairQ(ns.ratio,8)}`:'';
  R.today.innerHTML=`<span dir="ltr">${pairS(P.today)}</span>`;R.today.className='num '+((+P.today||0)>0?'dcacoin':((+P.today||0)<0?'dcaloss':''));R.today.style.fontSize='12.5px';
  R.lv.innerHTML=`${P.n_buy||0} شراء · ${P.n_sell||0} بيع${P.sales?` · ${P.sales} بيعة مكتملة`:''}`;
  R.books.innerHTML=`<span dir="ltr">${pairQ(P.main_book)} ${gEsc(MN)} · ${pairQ(P.other_book)} ${gEsc(O)}</span>`+((+P.usd_booked||0)>0?` · <span dir="ltr">${(+P.usd_booked).toFixed(4)} USDT</span>`:'');
  R.wal.innerHTML=(+P.wallet_main||0)>0?`<span dir="ltr">${pairQ(P.wallet_main)} ${gEsc(MN)}</span>`+(P.wallet_pct!=null?` <small dir="ltr">· ${(+P.wallet_pct)>=0?'+':''}${(+P.wallet_pct).toFixed(2)}%</small>`:''):'—';
  {const t=stAge(b);if(R.age.textContent!==t)R.age.textContent=t;R.age.title=stAgeT(b)}
  {const pd=P.per_day;R.rates.innerHTML=pd!=null?`<span dir="ltr">${pairS(pd)} / ${pairS(pd*30)} / ${pairS(pd*365)}</span> ${gEsc(MN)}`:'— <small>(بعد نصف يوم)</small>'}
  R.ab.textContent=pbz?'▶️ استئناف الشراء':'⏸ إيقاف الشراء';R.ab.className='dcashield'+(pbz?' on':'');
  R.ab.title=pbz?'يعود للشراء — المستويات التي نزلت إليها النسبة تُشترى مستوى بعد مستوى':'لا شراء تحت النسبة الآن — المستويات تبقى كما هي';
  R.as.textContent=psz?'▶️ استئناف البيع':'⏸ إيقاف البيع';R.as.className='dcalast'+(psz?' on':'');
  R.as.title=psz?'يعود للبيع — ولا يبيع إلا بربح بعد العمولات':'لا بيع فوق النسبة الآن — ما اشتراه يبقى حتى الاستئناف';
  R.ab.disabled=R.as.disabled=!!P.destructing;
  R.pw.textContent=b.alive?'⏹':'▶️';R.pw.title=b.alive?'إيقاف البوت':'تشغيل البوت';
  let st='';
  if(P.destructing)st='💣 ينسحب البوت — يُكمل التبديل الجاري أولاً ليعود الدولار عملة';
  else if(P.in_flight)st=`⏳ تبديل جارٍ عبر الدولار${(+P.usd_booked||0)>0?` (${(+P.usd_booked).toFixed(4)} USDT)`:''} — يكمله البوت خلال ثوانٍ`;
  else{const e=(P.swaps||[]).slice(-1)[0];
    if(e){const w=new Date((+e.t||0)*1000),p=n=>String(n).padStart(2,'0'),ts=`${p(w.getMonth()+1)}-${p(w.getDate())} ${p(w.getHours())}:${p(w.getMinutes())}`;
      st=e.kind==='sell'?`🔴 باع ${pairQ(e.sold)} ${O} ⇐ ${pairQ(e.got)} ${MN} · الربح ${pairS(e.profit)} ${MN} · المستوى ${e.j} · ${ts}`
        :`🟢 اشترى ${pairQ(e.got)} ${O} بـ ${pairQ(e.sold)} ${MN} · المستوى ${e.j} · ${ts}`}
    else st=b.alive?'🔀 يراقب النسبة — ينتظر أول مستوى':'○ متوقف'}
  if(R.status.textContent!==st)R.status.textContent=st}
function pairPause(b,side){if(!b)return;const P=b.pair||{},buy=side==='buy',on=buy?(+P.bf>0||!!P.pb):(+P.sc>0||!!P.ps);
  if(!on){ctl(b.dir,'pause_'+side);return}
  const MN=pairMN(b),O=pairON(b),r=+P.ratio||0,L=P.levels||[],w=buy?'الشراء':'البيع';
  const x=buy?L.filter(l=>l.side==='buy'&&r>0&&+l.bp>=r):L.filter(l=>l.side==='sell'&&r>0&&+l.sp<=r),more=x.length>=30?'+':'';
  const P2='style="color:var(--mut);font-size:13px;line-height:1.9;margin-bottom:12px"';
  showDialog(`<h2>▶️ استئناف ${w} — ${gEsc(O)}/${gEsc(MN)}</h2>
    <p ${P2}>${x.length?(buy?`النسبة الآن ${pairQ(r,8)} — ${x.length}${more} مستوى نزلت إليها النسبة أثناء الإيقاف ⇐ يشتريها البوت الآن مستوى بعد مستوى، كل مستوى ${pairQ(P.mv)} ${gEsc(MN)} (نحو ${pairQ((+P.mv||0)*x.length)} ${gEsc(MN)}${more?' أو أكثر':''})، وكلٌّ يعود بيعاً بنسبة بيعه.`
      :`النسبة الآن ${pairQ(r,8)} — ${x.length}${more} مستوى صعدت إليها النسبة أثناء الإيقاف ⇐ يبيعها البوت الآن مستوى بعد مستوى، ولا يبيع إلا بربح بعد العمولات.`)
      :`لم تقطع النسبة أي مستوى أثناء الإيقاف — يعود ${w} من حيث هو.`}</p>
    <div class="mbtns"><button class="primary" id="pa_rs">✅ نعم، استأنف ${w}</button><button onclick="hideModal()">إلغاء</button></div>`);
  $('#pa_rs').onclick=()=>{hideModal();ctl(b.dir,'resume_'+side)}}
function pairLevels(b){if(!b)return;const P=b.pair||{},MN=gEsc(pairMN(b)),O=gEsc(pairON(b)),r=+P.ratio||0;
  const act=l=>l.side==='sell'?+l.sp:+l.bp,L=(P.levels||[]).slice().sort((a,z)=>act(z)-act(a));let mid=false,h='';
  const midRow=`<tr class="pmid"><td colspan="5">⚖️ النسبة الآن ${pairQ(r,8)}</td></tr>`;
  for(const l of L){if(!mid&&r>0&&act(l)<r){h+=midRow;mid=true}
    const s=l.side==='sell';
    h+=`<tr><td class="num">${+l.j}</td><td>${s?'<span style="color:var(--red)">🔴 بيع</span>':'<span style="color:var(--green)">🟢 شراء</span>'}</td><td class="num" dir="ltr">${pairQ(act(l),8)}</td>`
      +`<td class="num" dir="ltr">${s?pairQ(l.q)+' '+O:pairQ(P.mv)+' '+MN}</td><td class="num">${+l.n||0}</td></tr>`}
  if(!mid&&r>0&&L.length)h+=midRow;
  showModal(`<h2>🪜 مستويات «شبكة عملتين» — ${O}/${MN}</h2>
    <p style="color:var(--mut);font-size:12.5px;line-height:1.9;margin-bottom:10px">كل مستوى ينتظر أمراً واحداً: 🟢 شراء حين تنزل النسبة إليه (يدفع ${pairQ(P.mv)} ${MN}) أو 🔴 بيع حين تصعد إلى نسبة بيعه (يبيع ما اشتراه بربح). لا شيء منها موضوع على المنصة — البوت يراقب ويبدّل عبر الدولار لحظياً.${(+P.n_levels||0)>L.length?` يُعرض أقرب ${L.length} مستوى من ${+P.n_levels}.`:''}</p>
    <div style="max-height:62vh;overflow:auto"><table class="dntbl pairlv"><thead><tr><th>المستوى</th><th>ينتظر</th><th>النسبة</th><th>الكمية</th><th>بيعات</th></tr></thead>
    <tbody>${h||'<tr><td colspan="5">لا مستويات بعد</td></tr>'}</tbody></table></div>
    <div class="mbtns"><button onclick="hideModal()">إغلاق</button></div>`)}
function pairDetails(b){if(!b)return;
  const P=b.pair||{},MN=gEsc(pairMN(b)),O=gEsc(pairON(b)),pbz=+P.bf>0||!!P.pb,psz=+P.sc>0||!!P.ps,PT={main:MN,other:O,half:'نصفان بين العملتين'};
  showModal(`<h2 style="color:var(--blue)">⚙ تفاصيل «شبكة عملتين» — ${O}/${MN}</h2>
    <div class="dnsum" style="margin-bottom:14px">
      <div class="dnstat"><span>الحالة</span><b style="font-size:13px">${P.destructing?'💣 ينسحب':(b.alive?'🟢 نشط':'○ متوقف')}</b></div>
      <div class="dnstat"><span>💎 الربح</span><b class="bidi" style="color:var(--green)" dir="ltr">${pairS(P.profit)} ${MN}</b></div>
      <div class="dnstat"><span>اليوم</span><b dir="ltr">${pairS(P.today)} ${MN}</b></div>
    </div>
    <div class="dnsum" style="margin-bottom:14px">
      <div class="dnstat"><span>⚖️ النسبة الآن</span><b dir="ltr">${pairQ(P.ratio,8)}</b></div>
      <div class="dnstat"><span>البيعات المكتملة</span><b>${P.sales||0}</b></div>
      <div class="dnstat"><span>شراء / بيع</span><b>${P.n_buy||0} / ${P.n_sell||0}</b></div>
    </div>
    <div class="dnsec">⚙ الإعدادات</div>
    <table class="dntbl"><tbody>
      <tr><td style="text-align:right">الرئيسية · الثانية</td><td class="num">${MN} · ${O} (عبر USDT)</td></tr>
      <tr><td style="text-align:right">نسبة البداية</td><td class="num" dir="ltr">${pairQ(P.r0,8)}</td></tr>
      <tr><td style="text-align:right">الخطوة</td><td class="num">${pairQ((+P.g||0)*100)}%</td></tr>
      <tr><td style="text-align:right">كمية كل شراء</td><td class="num">${pairQ(P.mv)} ${MN}</td></tr>
      <tr><td style="text-align:right">مستويات تحت · فوق (من محفظتك)</td><td class="num">${P.dn||0} · ${P.up||0}</td></tr>
      <tr><td style="text-align:right">الربح يذهب إلى</td><td>${PT[P.pt]||MN}</td></tr>
      <tr><td style="text-align:right">💰 ما يملكه البوت</td><td class="num" dir="ltr">${pairQ(P.main_book)} ${MN} · ${pairQ(P.other_book)} ${O}${(+P.usd_booked||0)>0?' · '+(+P.usd_booked).toFixed(4)+' USDT':''}</td></tr>
      <tr><td style="text-align:right">💲 السعران الآن</td><td class="num" dir="ltr">${O} ${f4(+P.px_other||0)}$ · ${MN} ${f4(+P.px_main||0)}$</td></tr>
      <tr><td style="text-align:right">👛 قيمته بالرئيسية</td><td class="num" dir="ltr">${pairQ(P.wallet_main)} ${MN}${P.wallet_pct!=null?' ('+((+P.wallet_pct)>=0?'+':'')+(+P.wallet_pct).toFixed(2)+'%)':''}</td></tr>
    </tbody></table>
    <p style="font-size:11px;color:var(--mut2);margin-top:10px;line-height:1.8">لا يضع البوت أوامر قاعدة على المنصة: يحفظ الشراء والبيع التاليين ويراقب النسبة كل ثانيتين، ثم يبدّل عبر الدولار بأمرين فوريين. لتغيير إعداداته احذفه وانشره من جديد — 🗄️ الأرشيف يعبّئ إعداداته نفسها.</p>
    <div class="dnsec" style="margin-top:14px">🎛 التحكم</div>
    <div class="gdbtns">
      <button id="gd_auto" class="${b.auto?'on':''}">${b.auto?'🤖 الحارس: يشمله':'🤖 الحارس: مستثنى'}</button>
      <button id="gd_pb" class="${pbz?'on':''}">${pbz?'▶️ استئناف الشراء':'⏸ إيقاف الشراء'}</button>
      <button id="gd_ps" class="${psz?'on':''}">${psz?'▶️ استئناف البيع':'⏸ إيقاف البيع'}</button>
    </div>
    <div class="mbtns" style="margin-top:14px"><button class="primary" id="gd_lv">🪜 المستويات</button><button onclick="hideModal()">إغلاق</button></div>`);
  $('#gd_auto').onclick=()=>{ctl(b.dir,'auto');hideModal()};
  $('#gd_pb').onclick=()=>{hideModal();pairPause(botOf(b.dir)||b,'buy')};
  $('#gd_ps').onclick=()=>{hideModal();pairPause(botOf(b.dir)||b,'sell')};
  $('#gd_lv').onclick=()=>{hideModal();pairLevels(botOf(b.dir)||b)}}
"""

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    if s.count(JS_ANCHOR) != 1 or "function buildPairCard" in s.replace(JS, ""):
        print("❌ the card's anchor is not unique (or the card is already there) — nothing written"); sys.exit(1)
    s = s.replace(JS_ANCHOR, JS + JS_ANCHOR)
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
    print(f"✅ {len(R)} replacements + the card · 🔀 the card in the main coin (all skins) · ⚙ details · 🪜 levels · ⏸/▶️ by the ratio · "
          f"no delete mid-swap · every label list · {p}")
