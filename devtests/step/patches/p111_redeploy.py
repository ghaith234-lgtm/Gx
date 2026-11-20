# ♻️ patch 111 (dashboard v3.36.65 · a deleted bot comes back through its deploy form). The owner (20-11): «اريد عند مسح بوت اقدر ارجعه
#   يعني انسخ اعداداته ويبدي من جديد واقدر اعدل عليه قبل ما انشره ، يعني حولني تلقائيا وكانما نشر البوت».
#   · 🗄️ الأرشيف: every deleted bot has «♻️ انشره من جديد» · and right after a delete (🗑 · 💣) the page offers the same
#   · it opens THAT bot's own deploy form (♾️🎚️➕ · 🪜 · 📉📈 DCA · ⚡ DCA+ sell/buy with its rows · 🔁🔂 periodic · 💹 value path) filled
#     with its settings as they were when it was deleted (card edits included) · its wallet chosen (by name — no key leaves the server) ·
#     🧪 a demo stays a demo with its starting balances · a line on top says where it came from · edit anything, then «🚀 انشر وشغّل»:
#     a NEW bot (new folder, fresh start) — the archived one stays as it is
#   · 🪜 the start price is left empty (= the market now — a fresh start, not the old price)
#   · server: redeploy_info(name) — read only, the archived config → the form's own field names (the deploy functions read in reverse) ·
#     GET /api/archive_redeploy?name= · delete_bot returns the archive folder's name
#   python3 devtests/step/patches/p111_redeploy.py Holy_Dashboard.pyw
import os, sys

PY = r'''

_RD_FORM = {"grid": "grid", "grid_range": "grid", "grid_plus": "grid", "grid_step": "step", "dca": "dca", "dca_buy": "dca",
            "rec_buy": "rec", "rec_sell": "rec", "rec_va": "va"}


def redeploy_info(name):
    """♻️ v3.36.65: نموذج نشر بوت محذوف — إعداداته (بلا مفاتيح) بأسماء حقول نموذج النشر نفسه (دوال النشر بالعكس) · قراءة فقط ·
    المحفظة باسمها (يطابق مفتاحها هنا ولا يخرج) · الديمو بأرصدة بدايته"""
    name = os.path.basename(str(name or "").strip())
    d = os.path.join(ROOT, "_archive", name)
    if not name or name.startswith(".") or not os.path.isdir(d):
        return {"ok": False, "msg": "لم يُعثر على هذا البوت في الأرشيف"}
    cfgs = sorted(glob.glob(os.path.join(d, "config_*.json")))
    c = _safe(load_json, cfgs[0], default=None) if cfgs else None
    if not isinstance(c, dict) or not str(c.get("symbol") or "").strip():
        return {"ok": False, "msg": "إعدادات هذا البوت غير مقروءة"}
    bt = str(c.get("bot_type") or "grid")
    form = _RD_FORM.get(bt)
    if not form:
        return {"ok": False, "msg": "نوع هذا البوت لا يُنشر من جديد من هنا"}
    sym = str(c.get("symbol")).strip().upper()

    def n(k, dflt=0.0):
        try:
            v = float(c.get(k) if c.get(k) not in (None, "") else dflt)
            return v if v == v and abs(v) != float("inf") else dflt
        except Exception:
            return dflt

    pct = lambda k: round(n(k) * 100, 6)
    P = {"symbol": sym, "auto": bool(c.get("auto_restart", True))}
    if form == "grid":
        P.update(bot_type=bt, grid_pct=pct("grid_percentage"), usd_value=n("usd_value"), min_price=n("min_price"),
                 forced_base=n("forced_base_price"), lower_price=n("lower_price"), upper_price=n("upper_price"),
                 buy_offset=pct("buy_offset"), guard=bool(c.get("knife_guard")), reinvest=bool(c.get("reinvest")),
                 reinvest_pct=n("reinvest_pct", 100.0) if c.get("reinvest_pct") is not None else 100.0)
    elif form == "step":
        P.update(usd_value=n("usd_value"), step_parts=int(n("step_parts", 3)), step_sell_pct=pct("step_sell"),
                 step_first_pct=round((n("step_first") or n("step_sell")) * 100, 6), grid_pct=pct("grid_percentage"),
                 min_price=n("min_price"), up_groups=int(n("up_groups")), forced_base="", reinvest=bool(c.get("reinvest")),
                 reinvest_pct=n("reinvest_pct", 100.0) if c.get("reinvest_pct") is not None else 100.0)
    elif form == "dca":
        if c.get("dca_plus"):
            form = "dcap"
            rows, _w = _plus_rows_ok(c.get("plus_rows"))
            P.update(dca_type="dca_plus_buy" if bt == "dca_buy" else "dca_plus", plus_rows=rows or [])
        else:
            P.update(dca_type=bt, base_order_qty=n("base_order_qty"), avg_order_qty=n("avg_order_qty"), first_deviation=n("first_deviation"),
                     step_multiplier=n("step_multiplier", 1.0), size_multiplier=n("size_multiplier", 1.0),
                     max_safety_orders=int(n("max_safety_orders")), take_profit_pct=n("take_profit_pct"))
        P.update(exchange_orders=int(n("exchange_orders", 3)), cycle_wait_sec=n("cycle_wait_sec", 30.0), trail_on=bool(c.get("trail_on")),
                 trail_pct=n("trail_pct", 0.3))
    elif form == "rec":
        P.update(rec_type=bt, mode="avg" if str(c.get("mode")) == "avg" else "lots", amount=n("amount"), every=int(n("every", 1)),
                 unit=str(c.get("unit") or "d"), at=str(c.get("at") or ""), start_now=bool(c.get("start_now", True)), tp_pct=n("tp_pct"),
                 cap=n("cap"), ri_pct=n("ri_pct"), lo=n("lo"), hi=n("hi"))
    else:                                                             # 💹 مسار القيمة
        pm = str(c.get("trigger") or "time") == "price"
        hg = bool(c.get("guard_on")) and (n("hg_pct") > 0 or n("hg_usd") > 0)
        P.update(va_mode="grow" if n("step_usd") > 0 else "fixed", trigger="price" if pm else "time", start_usd=n("start_usd"),
                 step_usd=n("step_usd"), every=int(n("every", 1)), unit=str(c.get("unit") or "d"), at=str(c.get("at") or ""),
                 band_pct=n("band_pct", 4.0), max_order=n("max_order"), cap=n("cap"), brake_pct=n("brake_pct"),
                 floor_on=bool(c.get("floor_on", True)), start_now=bool(c.get("start_now", True)), guard_on=hg,
                 first_src="wallet" if str(c.get("first_src") or "") == "wallet" else "buy")
        if pm:
            P.update(drop_pct=n("drop_pct", 5.0), rise_pct=n("rise_pct", n("drop_pct", 5.0)))
        if hg:
            P.update(hg_pct=n("hg_pct"), hg_usd=n("hg_usd"), hg_ri=bool(c.get("hg_ri")), hg_ri_pct=n("hg_ri_pct", 100.0),
                     hg_wallet=bool(c.get("hg_wallet")))
    demo = bool(c.get("is_demo"))
    wname, dusd, dcoin = "", "", ""
    if demo:
        st = ((_safe(load_json, os.path.join(d, DEMO_WALLET), default=None) or {}).get("start") or {})
        base, quote = (sym.split("-") + ["USDT"])[:2]
        try:
            dusd = f"{float(st.get(quote)):.10g}" if st.get(quote) is not None else ""
            dcoin = f"{float(st.get(base)):.10g}" if st.get(base) is not None else ""
        except Exception:
            dusd = dcoin = ""
    else:
        k = str(c.get("api_key") or "").strip()
        if k:
            for w in (app_cfg().get("wallets") or []):
                if str(w.get("api") or "").strip() == k:
                    wname = str(w.get("name") or "")
                    break
    return {"ok": True, "name": name, "form": form, "type": bt, "lbl": _PV_TYPE_ALL.get(bt, bt), "ico": _WD_E.get(bt, "🤖"), "sym": sym,
            "pre": P, "wallet": wname, "demo": demo, "demo_usd": dusd, "demo_coin": dcoin}
'''

JS = r'''/* ♻️ v3.36.65: البوت المحذوف يرجع بنموذج نشره — معبّأ بإعداداته (من 🗄️ الأرشيف أو بعد الحذف مباشرة) · تعدّل ثم تنشره بوتاً جديداً */
function rdSet(id,v){const e=$('#'+id);if(!e||v===undefined||v===null)return false;
  if(e.type==='checkbox'){if(e.checked!==!!v){e.checked=!!v;e.dispatchEvent(new Event('change',{bubbles:true}))}return true}
  if(e.tagName==='SELECT'&&![...e.options].some(o=>o.value===String(v)))return false;
  e.value=String(v);e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}));return true}
function rdOffer(name,sym){
  showModal(`<h2>♻️ حُذف البوت — هل تنشره من جديد؟</h2>
    <p style="font-size:13px;color:var(--mut);line-height:1.9;margin:0 0 10px">مجلد <b dir="ltr">${gEsc(sym||'')}</b> محفوظ في 🗄️ الأرشيف. يمكنك فتح نموذج نشره معبّأً بإعداداته نفسها، فتعدّل ما تريد ثم تنشره بوتاً جديداً يبدأ من جديد — والخيار نفسه يبقى متاحاً لاحقاً من 🗄️ الأرشيف.</p>
    <div class="mbtns"><button class="primary" onclick="rdOpen('${gEsc(name)}')">♻️ افتح نموذج النشر بإعداداته</button><button onclick="hideModal()">لا</button></div>`)}
async function rdOpen(name){let r=null;try{r=await api('/api/archive_redeploy?name='+encodeURIComponent(name))}catch(e){r=null}
  if(!r||!r.ok){toast((r&&r.msg)||'تعذّر قراءة إعدادات البوت',false);return null}
  hideModal();await new Promise(z=>setTimeout(z,40));
  const P=r.pre||{},F=r.form,X={grid:'n',step:'st',dca:'dn',dcap:'dn',rec:'rd',va:'vd'}[F];
  if(F==='grid')await openDeploy(Object.assign({},P,{demo:r.demo}));
  else if(F==='step')await openDeployStep(Object.assign({},P,{demo:r.demo}));
  else if(F==='dca'||F==='dcap'){if(F==='dcap'){window._plxKeep=(P.plus_rows||[]).map(x=>({d:+x.d,q:+x.q,x:+x.x}));PLX=null}
    await openDeployDca(F==='dcap'?'plus':undefined);
    rdSet('dn_sym',r.sym);rdSet('dn_type',P.dca_type);dcaTypeSwitch();
    if(F==='dca')[['dn_base','base_order_qty'],['dn_avg','avg_order_qty'],['dn_dev','first_deviation'],['dn_step','step_multiplier'],['dn_size','size_multiplier'],
      ['dn_n','max_safety_orders'],['dn_tp','take_profit_pct']].forEach(([i,k])=>rdSet(i,P[k]));
    rdSet('dn_ex',P.exchange_orders);rdSet('dn_wait',P.cycle_wait_sec);rdSet('dn_trail_pct',P.trail_pct);rdSet('dn_trail',P.trail_on);
    window._plxKeep=null}
  else if(F==='rec'){await openDeployRec();rdSet('rd_sym',r.sym);rdSet('rd_type',P.rec_type);recFormSync();recMode(P.mode);
    [['rd_amt','amount'],['rd_every','every'],['rd_unit','unit'],['rd_tp','tp_pct'],['rd_cap','cap'],['rd_ri','ri_pct'],['rd_lo','lo'],['rd_hi','hi']].forEach(([i,k])=>rdSet(i,P[k]));
    rdSet('rd_at',P.at||'');rdSet('rd_now',P.start_now);recFormSync()}   // الساعة كما كانت (فارغة = كما كانت)
  else if(F==='va'){await openDeployVa();rdSet('vd_sym',r.sym);vaTrig(P.trigger);vaMode(P.va_mode);vaW0(P.first_src);
    [['vd_start','start_usd'],['vd_step','step_usd'],['vd_drop','drop_pct'],['vd_rise','rise_pct'],['vd_every','every'],['vd_unit','unit'],['vd_band','band_pct'],
     ['vd_mo','max_order'],['vd_cap','cap'],['vd_brake','brake_pct'],['vd_hgp','hg_pct'],['vd_hgu','hg_usd'],['vd_hgrp','hg_ri_pct']].forEach(([i,k])=>rdSet(i,P[k]));
    rdSet('vd_at',P.at||'');rdSet('vd_floor',P.floor_on);rdSet('vd_now',P.start_now);rdSet('vd_hgr',P.hg_ri);rdSet('vd_hgw',P.hg_wallet);rdSet('vd_guard',P.guard_on);
    vaGuardSync();vaSync()}
  else return null;
  rdSet(X+'_sym',r.sym);
  let wOk=true;
  if(r.demo){rdSet(X+'_demo',true);demoTgl(X);rdSet(X+'_dusd',r.demo_usd);rdSet(X+'_dcoin',r.demo_coin)}
  else{wOk=!!r.wallet&&rdSet(X+'_wallet',r.wallet)}
  rdSet(X+'_auto',P.auto);
  const h=document.querySelector('#modal h2');
  if(h){const n=document.createElement('div');n.className='rdnote';
    n.innerHTML=`♻️ من الأرشيف: <b dir="ltr">${gEsc(r.sym)}</b> · ${gEsc(r.ico||'')} ${gEsc(r.lbl||r.type||'')}${r.demo?' · 🧪 ديمو':''} — إعداداته معبّأة كما كانت عند حذفه. عدّل ما تريد ثم «🚀 انشر وشغّل» فيُنشأ بوت جديد يبدأ من جديد.`
      +(F==='step'?'<br>🎯 سعر البداية فارغ = سعر السوق الآن.':'')+(!r.demo&&!wOk?'<br>⚠️ محفظته غير محفوظة في 🔗 الارتباط — اختر المحفظة.':'');
    h.insertAdjacentElement('afterend',n)}
  toast('♻️ نموذج النشر معبّأ بإعدادات '+r.sym+' — عدّل ثم انشر',true);
  return r}
'''

CSS = """
.rdnote{margin:0 0 10px;padding:9px 11px;border:1px solid rgb(var(--cyan-rgb)/.45);border-radius:10px;background:rgb(var(--cyan-rgb)/.08);font-size:12px;line-height:1.85;color:var(--tx)}   /* ♻️ v3.36.65 */"""

R = [
    # server — the reader, after archive_view
    ("""    return {"ok": True, "n": len(out), "items": out[:300]}


def delete_bot(b):""", """    return {"ok": True, "n": len(out), "items": out[:300]}
""" + PY + """

def delete_bot(b):"""),
    # delete returns the archive folder's name
    ("""    tg_send(f"🗑 *حذف (أرشفة)* — `{b['symbol']}` انتقل إلى `_archive`")
    return {"ok": True, "msg": "⏹ حُذف بأمان — مجلده محفوظ داخل _archive إن احتجته"}""",
     """    tg_send(f"🗑 *حذف (أرشفة)* — `{b['symbol']}` انتقل إلى `_archive`")
    return {"ok": True, "msg": "⏹ حُذف بأمان — مجلده محفوظ داخل _archive إن احتجته", "arch": os.path.basename(dest), "sym": b["symbol"]}   # ♻️ v3.36.65"""),
    # route
    ("""        if u.path == "/api/archive":                      # 🗄️ v3.36.18: البوتات المحذوفة (للعرض)
            return self._json(_safe(archive_view, default={"ok": False, "items": []}))""",
     """        if u.path == "/api/archive":                      # 🗄️ v3.36.18: البوتات المحذوفة (للعرض)
            return self._json(_safe(archive_view, default={"ok": False, "items": []}))
        if u.path == "/api/archive_redeploy":             # ♻️ v3.36.65: نموذج نشر بوت محذوف (قراءة فقط · بلا مفاتيح)
            return self._json(_safe(redeploy_info, q.get("name", [""])[0], default={"ok": False, "msg": "تعذّر قراءة إعدادات البوت"}))"""),
    # page: ctl offers it right after a delete
    ("""async function ctl(dir,action,value){try{const r=await api('/api/control',{dir,action,value});toast(r.msg,r.ok);tick()}catch(e){toast('تعذر الاتصال','0')}}""",
     JS + """async function ctl(dir,action,value){try{const r=await api('/api/control',{dir,action,value});toast(r.msg,r.ok);tick();
  if(r&&r.ok&&r.arch&&(action==='delete'||action==='delete_purge'))setTimeout(()=>rdOffer(r.arch,r.sym),450)}catch(e){toast('تعذر الاتصال','0')}}   // ♻️ v3.36.65"""),
    # archive rows: the button
    ("""       <div style="font-size:11.5px;line-height:1.9">${pr.length?pr.join(' · '):'<span style="color:var(--mut2)">بلا ربح مسجّل</span>'}</div>
       <details style="margin-top:4px">""",
     """       <div style="font-size:11.5px;line-height:1.9">${pr.length?pr.join(' · '):'<span style="color:var(--mut2)">بلا ربح مسجّل</span>'}</div>
       <button type="button" class="rdbtn" onclick="rdOpen('${gEsc(x.name)}')" style="margin-top:7px;width:100%;font-size:12px;padding:8px">♻️ انشره من جديد — نموذج النشر بإعداداته</button>
       <details style="margin-top:4px">"""),
    ("""مجلد كل واحد محفوظ بـ<b>_archive</b> (إعداداته وسجله) · للعرض فقط</div>`""",
     """مجلد كل واحد محفوظ بـ<b>_archive</b> (إعداداته وسجله) · «♻️ انشره من جديد» يفتح نموذج نشره معبّأً بإعداداته لتعدّلها ثم تنشره بوتاً جديداً</div>`"""),
    # step form keeps the demo choice
    ("""<select id="st_wallet">${ws.map(w=>`<option>${gEsc(w.name)}</option>`).join('')||'<option value="">— أضف محفظة أولاً —</option>'}</select></div>${demoFld('st',false)}""",
     """<select id="st_wallet">${ws.map(w=>`<option>${gEsc(w.name)}</option>`).join('')||'<option value="">— أضف محفظة أولاً —</option>'}</select></div>${demoFld('st',!!pre.demo)}"""),
    # css
    (""".card.cmp{content-visibility:visible}""", """.card.cmp{content-visibility:visible}""" + CSS),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · ♻️ a deleted bot comes back through its own deploy form (archive · right after a delete) · compiles · {p}")
