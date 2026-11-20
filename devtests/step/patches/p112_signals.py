# 🎯 patch 112 (dashboard v3.36.66 · the signals — every indicator and its combinations with their record · notifications with the owner's
#   threshold · the market compass · inside 🔮 the forecasts). The owner (20-11): «اني اريد اتضيف كل الاشارات واتسوي فحص واتشوف واتسويه اشارة
#   وحده … خلي الاشارات مو بس ثلاثية حتى اكثر · انا احدد النسبة بالاشعارات … كل المؤشرات تضعها · الثناىية وفوق كذلك على حدى · بدون مستويات ·
#   الاشعارات حسب المؤشر اذا شراء او تجميع او بيع او صعود او نزول حسب كل عملة وكذلك بشكل عام … انا ابحث على التركيبة النادرة … كيف احدد النسبة
#   الاشعارات اخاف يطلع مزعج … افحص وضيف وكذلك التوقعات لا تنسها».
#   · server (p112_signals_server.py): the 36 systems = ci/sig_check6.py's own block (inserted here as _SG_LIB, kept equal by a test) · every
#     other reading through the dashboard's own function · the catalog (singles + combinations 2 … 6 + 💎 rare) built in its own process with no
#     network · a scan at every 4-hour / daily close · the live record · the compass · notifications (Telegram + the app + 🔔) with the owner's
#     threshold, minimum count, better-than-random, rare, types, frames, coins, daily cap, quiet hours, daily summary, results
#   · page: 🎯 window (now · the catalog · the log · ⚙️ notifications with the weekly estimate) · 🔮 shows every coin's signals and the compass ·
#     📊 · ⚙️ · the ticker's settings · a notification tap opens 🎯
#   python3 devtests/step/patches/p112_signals.py Holy_Dashboard.pyw
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def lib_block():
    """the indicators + the 36 systems + mirror + fwd — exactly as ci/sig_check6.py has them"""
    s = open(os.path.join(REPO, "ci", "sig_check6.py"), encoding="utf-8").read()
    a = s.index("# ───────────────────────── indicators")
    b = s.index("\ndef mean(v):")
    blk = s[a:b].rstrip() + "\n"
    assert "'''" not in blk
    return blk


_ns = {}
exec(compile(open(os.path.join(HERE, "p112_signals_server.py"), encoding="utf-8").read(), "p112_signals_server", "exec"), _ns)
PY = _ns["PY"]
PY = PY.replace("SG_DIR = os.path.join(ROOT, \"_signals\")",
                "_SG_LIB = r'''" + lib_block() + "'''   # ⬆️ كتلة ci/sig_check6.py حرفياً (devtests/t_sigs.py يتأكد)\n\nSG_DIR = os.path.join(ROOT, \"_signals\")", 1)

PY_FC = r'''

def _sg_coin_rows(sym, st, cat, cfg, k=6):
    F = (st.get("now") or {}).get(sym) or {}
    out = {}
    for fr, x in F.items():
        rows = [_sg_row(cat["idx"][i], st, cat, cfg) for i in x.get("alive") or [] if i in cat["idx"]]
        rows = [dict(r, new=r["id"] in (x.get("fired") or [])) for r in rows]
        rows.sort(key=lambda r: (not r["ok"], -r["lb"]))
        out[fr] = {"t": x.get("t"), "rows": rows[:k], "nb": sum(1 for r in rows if r["s"] > 0 and r["ok"]),
                   "ns": sum(1 for r in rows if r["s"] < 0 and r["ok"]), "n": len(rows)}
    return out


def sg_fc(rows):
    """🔮 v3.36.66: لكل عملة في التوقعات إشاراتها الشغّالة الآن (يومي · 4 ساعات) + البوصلة — من آخر فحص (قراءة فقط)"""
    st, cat = _sg_st(), _sg_cat()
    if not cat:
        return {"ready": False, "comp": st.get("comp")}
    cfg = sg_cfg()
    nb = ns = 0
    for r in rows:
        x = _sg_coin_rows(r.get("sym"), st, cat, cfg, 4)
        r["sig"] = x
        nb += sum(f["nb"] for f in x.values())
        ns += sum(f["ns"] for f in x.values())
    return {"ready": True, "comp": st.get("comp"), "nb": nb, "ns": ns}


def _sg_cfg_merge(cfg, v):
    """⚙️ إعدادات لم تُحفظ بعد (للتقدير الأسبوعي وأنت تحرّك المؤشر)"""
    c = dict(cfg)
    for k, lo, hi in (("thr", 50, 95), ("min", 3, 200), ("rmin", 3, 50), ("cap", 0, 100)):
        if v.get(k) is not None:
            try:
                c[k] = max(lo, min(hi, int(v[k])))
            except Exception:
                pass
    for k in ("rnd", "rare"):
        if v.get(k) is not None:
            c[k] = bool(v[k])
    if isinstance(v.get("types"), dict):
        c["types"] = dict(c["types"], **{k: bool(x) for k, x in v["types"].items() if k in SG_TY})
    if isinstance(v.get("fr"), dict):
        c["fr"] = dict(c["fr"], **{k: bool(x) for k, x in v["fr"].items() if k in SG_FR})
    if isinstance(v.get("coins"), list):
        c["coins"] = [str(x).upper() for x in v["coins"] if isinstance(x, str)][:40]
    return c


def sg_est(v):
    return {"ok": True, "est": sg_estimate(_sg_cfg_merge(sg_cfg(), v or {}))}
'''

JS = r'''
/* 🎯 v3.36.66: الإشارات — كل المؤشرات وتركيباتها (2 … 6 معاً · 💎 النادرة) بسجلها على الأسعار الحقيقية · 🧭 البوصلة · إشعارات بنسبتك ·
   عرض وإشعارات فقط: لا أمر ولا إلغاء ولا لمس لأي بوت */
let SGV=null,SGT=null,SGTAB='now',SGC=null,SGP={},SGET=null;const SGO={},SGF={fr:'',side:'1',size:'',rare:'',ty:'',q:'',sort:''};
const SGCOMP={up:['صاعد','🟢','p'],flat:['مختلط','🟡','z'],down:['نازل','🔴','n']};
async function openSig(tab){if(tab)SGTAB=tab;
  showModal(`<h2>🎯 الإشارات — كل المؤشرات وتركيباتها بسجلها</h2><div class="sg-tabs" id="sg_tabs"></div><div id="sg_body" style="color:var(--mut);font-size:12.5px;padding:16px;text-align:center">${LDR('جاري التحميل…')}</div>
    <div class="mbtns"><button onclick="openFc()">🔮 التوقعات</button><button onclick="openInd()">📊 المؤشرات</button><button onclick="hideModal()">إغلاق</button></div>`);
  await sgLoad()}
async function sgLoad(){clearTimeout(SGT);try{SGV=await api('/api/signals')}catch(e){SGV=null}sgRender();if(SGTAB==='cat')sgCat();
  if(SGV&&SGV.busy&&SGV.busy.phase&&$('#sg_body'))SGT=setTimeout(sgLoad,4000)}
function sgTab(t){SGTAB=t;sgRender();if(t==='cat')sgCat()}
function sgAr(n,k){const W={day:['يوم واحد','يومين','أيام','يوماً'],time:['مرة واحدة','مرتين','مرات','مرة'],coin:['عملة واحدة','عملتين','عملات','عملة'],min:['دقيقة واحدة','دقيقتين','دقائق','دقيقة']}[k];n=+n||0;   // 55 يوماً · 13 مرة · 9 مرات
  return n===1?W[0]:n===2?W[1]:(n%100>=3&&n%100<=10)?`${n} ${W[2]}`:`${n} ${W[3]}`}
function sgDt(n){n=+n||0;return n===1?'كلها في يوم واحد':n===2?'في يومين مختلفين':(n%100>=3&&n%100<=10)?`في ${n} أيام مختلفة`:`في ${n} يوماً مختلفاً`}
function sgPct(x){x=+x||0;return `<b class="${x>=0?'up':'dn'}" dir="ltr">${x>=0?'+':''}${(x*100).toFixed(1)}%</b>`}
function sgTy(V,t){return ((V&&V.types)||{})[t]||['•','']}
function sgRow(r,V){const T=sgTy(V,r.ty),hz=((V&&V.hzn)||{})[r.f]||'';
  return `<div class="sg-r${r.ok?' ok':''}${r.s<0?' sell':''}"><div class="sg-rh"><span class="sg-ty">${T[0]} ${gEsc(T[1])}</span><span class="sg-fr">${gEsc(((V&&V.fn)||{})[r.f]||r.f)}${r.k.length>1?' · '+r.k.length+' معاً':''}</span>
    ${r.rare?'<span class="sg-b rare">💎 نادرة</span>':''}${r.new?'<span class="sg-b new">🆕 الآن</span>':''}${r.ok?'<span class="sg-b ok">🔔 تصلك</span>':''}</div>
    <div class="sg-k">${r.nm.map(gEsc).join(' <b>+</b> ')}</div>
    <div class="sg-rec">صدقت <b>${r.w}</b> من <b>${sgAr(r.n,'time')}</b> (<b>${(+r.h).toFixed(0)}%</b>)${r.nd&&r.nd<r.nt?` <small>— اختبارها ${sgDt(r.nd)}</small>`:''} · العشوائي ${(+r.rh).toFixed(0)}% · المتوسط بعد ${gEsc(hz)} ${sgPct(r.m)}${r.ln?` · منها حيّة ${r.lw} من ${r.ln}`:''}${r.better?'':' · <span style="color:var(--amber)">⚠️ ليست أفضل من العشوائي</span>'}</div></div>`}
function sgHead(V){const C=V.comp,B=V.busy||{};let h='';
  if(C&&SGCOMP[C.s]){const nm=SGCOMP[C.s];
    h+=`<div class="sg-comp ${nm[2]}"><div><b>🧭 السوق الآن: ${nm[1]} ${nm[0]}</b> <small>منذ ${sgAr(C.days,'day')}</small></div>
      <div class="ind-sub">البيتكوين ${C.btc?'فوق':'تحت'} متوسط 200 يوم · ${C.k} من ${sgAr(C.n,'coin')} فوق متوسطها (50 يوماً)${C.m14!=null?` · تاريخياً متوسط الشراء بعد أسبوعين في هذا الوضع ${sgPct(C.m14)}`:''}${C.s==='flat'?' · تاريخياً أسوأ وضع للشراء':''}</div>
      <div class="sg-hist" title="آخر 60 يوماً — 🟢 صاعد · 🟡 مختلط · 🔴 نازل (منعّمة: لا تتغير إلا إذا ثبتت 3 أيام)">${(C.hist||[]).map(x=>`<i class="${gEsc(x[2])}"></i>`).join('')}</div></div>`}
  if(B.phase)h+=`<div class="sg-busy">${gEsc(B.msg||'…')}<div class="sg-pb"><i style="width:${Math.max(3,+B.pct||0)}%"></i></div></div>`;
  if(V.err)h+=`<div class="ind-sub" style="color:var(--amber)">⚠️ ${gEsc(V.err)}</div>`;
  return h}
function sgCoin(x,V){const op=!!SGO[x.sym],F=x.fr||{};
  const chips=['1D','4H'].filter(f=>F[f]).map(f=>{const z=F[f];return `<span class="ind-chip">${gEsc((V.fn||{})[f]||f)}: <b style="color:var(--green)">🟢 ${z.nb}</b> · <b style="color:var(--red)">🔴 ${z.ns}</b></span>`}).join('');
  let det='';
  if(op){det=`<div class="ind-det" onclick="event.stopPropagation()">${['1D','4H'].filter(f=>F[f]).map(f=>{const z=F[f],R=z.rows||[],ok=R.filter(r=>r.ok),rest=R.filter(r=>!r.ok);
      return `<div class="sg-frh">${gEsc((V.fn||{})[f]||f)} <small>· آخر شمعة ${z.t?new Date(z.t*1000).toLocaleString('ar',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}):'—'} · الشغّالة الآن: ${R.length}</small></div>
        ${ok.map(r=>sgRow(r,V)).join('')||'<div class="ind-sub">لا شيء يمر بإعداداتك الآن</div>'}
        ${rest.length?`<details class="sg-more"><summary>الباقي (${rest.length}) — لا يمر بإعداداتك</summary>${rest.slice(0,30).map(r=>sgRow(r,V)).join('')}</details>`:''}`}).join('')||'<div class="ind-sub">لم تُفحص بعد</div>'}</div>`}
  const px=(F['4H']||F['1D']||{}).px;
  return `<div class="ind-c sg-c${op?' open':''}" onclick="SGO['${gEsc(x.sym)}']=!SGO['${gEsc(x.sym)}'];sgRender()"><div class="ind-h"><span class="cn">${gEsc(x.base)}</span>${px?`<span class="px">${fmtPx(px)}</span>`:''}
    <span class="ind-sub" style="margin-inline-start:auto">${op?'':'اضغط للتفاصيل ←'}</span></div><div class="ind-dots">${chips}</div>${det}</div>`}
function sgNow(V){let h=sgHead(V);
  if(!V.cat)return h+`<div class="sg-empty">🏗️ <b>أول مرة:</b> تُجلب شموع ~${(V.uni||[]).length} عملة (سنتان على 4 ساعات و3 سنوات يومية) ثم تُحسب كل الإشارات وتُبحث تركيباتها — بعملية منفصلة لا تُثقل اللوحة. يأخذ ذلك من ربع ساعة إلى ساعة مرة واحدة، ثم يصبح خفيفاً (فحص عند إغلاق كل شمعة).${V.on?'':'<br>⚠️ المؤشرات وإشعارات الإشارات متوقفة — شغّل أحدهما'}</div>`;
  const N=V.now||[];
  if(!N.length)return h+'<div class="sg-empty">🔍 الدليل جاهز — أول فحص عند إغلاق شمعة 4 ساعات القادمة (3 · 7 · 11 صباحاً ومساءً بتوقيت بغداد) أو اليومية (3 فجراً)</div>';
  const mine=N.filter(x=>x.mine),oth=N.filter(x=>!x.mine);
  h+=`<div class="ind-top"><span class="ind-chip">🔄 آخر فحص ${V.scan_ts?gAgo(V.scan_ts):'—'}</span><span class="ind-chip">📒 ${V.cat.n} إشارة وتركيبة · 💎 ${V.cat.nrare} نادرة</span>${V.est?`<span class="ind-chip">🔔 أسبوعياً ≈ ${V.est.cut}</span>`:''}</div>`;
  h+=`<div class="ind-list">${mine.map(x=>sgCoin(x,V)).join('')||'<div class="ind-sub">لا توجد عملات في إشعاراتك — اخترها من ⚙️ الإشعارات</div>'}</div>`;
  if(oth.length)h+=`<details class="sg-more"><summary>عملات القياس الأخرى (${oth.length}) — تُفحص لتقوية السجل ولا تصلك إشعاراتها</summary><div class="ind-list">${oth.map(x=>sgCoin(x,V)).join('')}</div></details>`;
  h+=`<details class="ind-help"><summary>كيف أقرأ هذه النافذة؟</summary>
    <div>• كل <b>إشارة</b> وكل <b>تركيبة</b> (إشارتان أو أكثر أُطلقت خلال شموع قليلة على العملة نفسها) لها سجلها الخاص: <b>صدقت كم من كم مرة</b> بعد ${gEsc((V.hzn||{})['4H']||'')} (4 ساعات) أو ${gEsc((V.hzn||{})['1D']||'')} (يومي)، صافياً بعد العمولة.</div>
    <div>• السجل من <b>آخر 40% من التاريخ</b> — فترة لم تُختر عليها التركيبة — ثم <b>السجل الحي</b> منذ تشغيل اللوحة (يُحكم وحده). 💎 النادرة: سجلها كل التاريخ لأن حالاتها قليلة.</div>
    <div>• <b>العشوائي</b>: كم مرة كان السعر أعلى (أو أدنى للبيع) بعد المدة نفسها في أي شمعة — للمقارنة. الإشارة الجيدة أعلى منه بوضوح.</div>
    <div>• 🧭 <b>البوصلة</b>: البيتكوين فوق متوسط 200 يوم وأغلب العملات فوق متوسطها = صاعد · العكس = نازل · غير ذلك = مختلط. لا تتغير إلا إذا ثبتت الحالة الجديدة 3 أيام.</div>
    <div style="color:var(--amber);margin-top:6px">⚠️ احتمالات لا ضمانات · اللوحة تقرأ وتنبّه فقط: لا تفتح أمراً ولا تغلقه.</div></details>`;
  return h}
function sgCatUI(V){const b=(k,v,t)=>`<button class="${SGF[k]===v?'on':''}" onclick="SGF['${k}']='${v}';sgRender();sgCat()">${t}</button>`;
  const C=V.cat;if(!C)return sgHead(V)+'<div class="sg-empty">🏗️ الدليل لم يُبنَ بعد — تتابعه في «الآن»</div>';
  const tys=Object.entries(V.types||{}).filter(([k])=>!['mkt','res'].includes(k));
  return `<div class="ind-sub" style="margin-bottom:6px">📒 <b>${C.n}</b> إشارة وتركيبة (منها ${C.ncombo} تركيبة · 💎 ${C.nrare} نادرة) · من تاريخ ${(C.coins||[]).length} عملة · بُني ${C.ts?gAgo(C.ts):'—'}${C.secs?` في ${C.secs<90?'دقيقة أو أقل':sgAr(Math.round(C.secs/60),'min')}`:''} · يُعاد كل أسبوع</div>
    <div class="sg-flt">${b('fr','','الكل')}${b('fr','1D','يومي')}${b('fr','4H','4 ساعات')}</div>
    <div class="sg-flt">${b('side','1','🟢 شراء وصعود')}${b('side','-1','🔴 بيع ونزول')}${b('side','','الكل')}</div>
    <div class="sg-flt">${b('size','','كل الأحجام')}${b('size','1','وحدها')}${b('size','2','2 معاً')}${b('size','3','3 معاً')}${b('size','4','4 فأكثر')}${b('rare','1','💎 النادرة فقط')}${SGF.rare?b('rare','','✕ النادرة'):''}</div>
    <div class="sg-flt"><select onchange="SGF.ty=this.value;sgCat()"><option value="">كل الأنواع</option>${tys.map(([k,t])=>`<option value="${k}"${SGF.ty===k?' selected':''}>${t[0]} ${gEsc(t[1])}</option>`).join('')}</select>
      <select onchange="SGF.sort=this.value;sgCat()"><option value="">الأصدق أولاً (مع عدد المرات)</option><option value="n"${SGF.sort==='n'?' selected':''}>الأكثر حالات</option><option value="m"${SGF.sort==='m'?' selected':''}>الأكبر حركة</option><option value="live"${SGF.sort==='live'?' selected':''}>الأكثر سجلاً حياً</option></select>
      <input type="search" placeholder="🔍 ابحث: MACD · بولنجر · Supertrend…" value="${gEsc(SGF.q)}" oninput="SGF.q=this.value;clearTimeout(SGET);SGET=setTimeout(sgCat,350)"></div>
    <div id="sg_cat">${LDR('…')}</div>`}
async function sgCat(){const el=$('#sg_cat');if(!el)return;try{SGC=await api('/api/signals_cat?'+new URLSearchParams(SGF).toString())}catch(e){SGC=null}
  const e2=$('#sg_cat');if(!e2)return;if(!SGC||!SGC.ok){e2.innerHTML='<div class="ind-sub">⚠️ '+gEsc((SGC&&SGC.msg)||'تعذّر التحميل')+'</div>';return}
  e2.innerHTML=`<div class="ind-sub">النتائج: ${SGC.total}${SGC.total>SGC.rows.length?` · تُعرض أول ${SGC.rows.length}`:''}</div>`+(SGC.rows.map(r=>sgRow(r,SGV)).join('')||'<div class="ind-sub">لا شيء بهذه الفلاتر</div>')}
function sgLog(V){const L=V.log||[],R=((V.live||{}).recent)||[],lv=V.live||{};
  const dt=t=>new Date(t*1000).toLocaleString('ar',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'});
  return `<div class="ind-sub">📒 السجل الحي: حُكم عليها ${lv.done||0} · تنتظر وقتها ${lv.pend||0} (كل ما أُطلق على عملات القياس — لا ما وصلك فقط)</div>
    <div class="sg-frh">✅ نتائج ما وصلك إشعاره</div>${R.map(x=>`<div class="sg-lg"><b class="${x.x>0?'up':'dn'}">${x.x>0?'✅':'❌'} ${(x.x*100).toFixed(1)}%</b> · ${gEsc(sgTy(V,x.ty)[0]+' '+sgTy(V,x.ty)[1])} ${gEsc((x.sym||'').split('-')[0])} · ${gEsc(x.nm||'')} <small>· ${dt(x.ts)}</small></div>`).join('')||'<div class="ind-sub">لا نتائج بعد — تُحكم كل إشارة بعد وقتها (3 أيام أو أسبوع)</div>'}
    <div class="sg-frh">🔔 آخر الإشعارات (${L.length})</div>${L.map(x=>`<div class="sg-lg"><b>${gEsc(x.t)}</b> <small>· ${dt(x.ts)}</small><div class="ind-sub" style="white-space:pre-line">${gEsc(x.b)}</div></div>`).join('')||'<div class="ind-sub">لا إشعارات بعد</div>'}`}
function sgEstTxt(E){if(!E)return 'التقدير يظهر بعد بناء الدليل';
  return `بهذه الإعدادات كان سيصلك أسبوعياً نحو <b>${E.cut}</b> من الإشعارات على عملاتك${E.capped?` (بلا حدك اليومي ${E.wk})`:''} · الإشارات والتركيبات التي تمر: ${E.n}${E.cut>25?' · <span style="color:var(--amber)">⚠️ كثير — ارفع النسبة أو عدد المرات</span>':''}`}
function sgEst(v){Object.assign(SGP,v);const lb=$('#sg_thr_v');if(lb&&v.thr!=null)lb.textContent=v.thr+'%';const lm=$('#sg_min_v');if(lm&&v.min!=null)lm.textContent=v.min;
  const lr=$('#sg_rmin_v');if(lr&&v.rmin!=null)lr.textContent=v.rmin;
  clearTimeout(SGET);SGET=setTimeout(async()=>{try{const r=await api('/api/control',{action:'sg_est',value:SGP});const el=$('#sg_est');if(el)el.innerHTML=sgEstTxt(r&&r.est)}catch(e){}},250)}
async function sgSet(v){try{const r=await api('/api/control',{action:'sg_set',value:v});toast(r&&r.msg?r.msg:'تم',!!(r&&r.ok));
    if(r&&r.cfg&&SGV){SGV.cfg=r.cfg;SGV.est=r.est;SGV.mine=r.cfg.coins||SGV.tick;SGP={}}}catch(e){toast('تعذر الاتصال',false)}if(SGTAB==='cfg')sgRender()}
function sgCoinTog(s){const c=SGV.cfg,cur=(c.coins||SGV.tick||[]).slice(),i=cur.indexOf(s);if(i>=0)cur.splice(i,1);else cur.push(s);sgSet({coins:cur})}
function sgCfg(V){const c=V.cfg||{},T=c.types||{},ty=V.types||{},hrs=[...Array(24).keys()];
  const tg=(on,fn,a,b)=>`<button class="${on?'on':''}" onclick="${fn}">${on?a:b}</button>`;
  const hsel=(id,val,fn,off)=>`<select id="${id}" onchange="${fn}">${off?`<option value="">${off}</option>`:''}${hrs.map(h=>`<option value="${h}"${val===h?' selected':''}>${String(h).padStart(2,'0')}:00</option>`).join('')}</select>`;
  const q=c.quiet||null,mine=c.coins||V.tick||[];
  return `<div class="ind-al${c.on?'':' off'}"><div class="ind-al-h"><b>🎯 إشعارات الإشارات <small style="color:var(--mut2);font-weight:400">${c.on?gEsc((V.ch||{})[c.ch]||''):'متوقفة'}</small></b>
      <span style="display:flex;gap:6px"><button id="sg_on" class="${c.on?'on':''}" onclick="sgSet({on:${c.on?'false':'true'}})">${c.on?'✅ مفعّلة':'⏸️ متوقفة'}</button></span></div>
    <div class="sg-set"><div class="sg-sh">🎚️ أقل نسبة صدق: <b id="sg_thr_v">${c.thr}%</b></div><input type="range" id="sg_thr" min="50" max="95" step="1" value="${c.thr}" oninput="sgEst({thr:+this.value})" onchange="sgSet({thr:+this.value})">
      <div class="ind-sub" id="sg_est">${sgEstTxt(V.est)}</div></div>
    <div class="sg-set"><div class="sg-sh">🔢 أقل عدد مرات حتى تُحسب نسبتها: <b id="sg_min_v">${c.min}</b></div><input type="range" id="sg_min" min="3" max="100" step="1" value="${c.min}" oninput="sgEst({min:+this.value})" onchange="sgSet({min:+this.value})">
      <div class="ind-sub">إشارة ظهرت مرتين وصدقت مرتين = 100% — صدفة. الحد يمنع ذلك.</div></div>
    <div class="sg-set">${tg(c.rnd,`sgSet({rnd:${!c.rnd}})`,'✅ أفضل من العشوائي فقط','⬜ أفضل من العشوائي فقط')}<div class="ind-sub">نسبة 55% في سوق نازل قد تكون مثل البيع العشوائي — هذا الشرط يشترط أن تكون أعلى منه بوضوح.</div></div>
    <div class="sg-set">${tg(c.rare,`sgSet({rare:${!c.rare}})`,'💎 النادرة: تصلك','💎 النادرة: لا تصلك')} <span class="sg-sh">أقل عدد لها: <b id="sg_rmin_v">${c.rmin}</b></span>
      <input type="range" min="3" max="30" step="1" value="${c.rmin}" oninput="sgEst({rmin:+this.value})" onchange="sgSet({rmin:+this.value})"><div class="ind-sub">تركيبات ظهرت مرات قليلة بصدق عالٍ وصمدت على الفترة الجديدة — تصلك بعلامة 💎 وتحذير.</div></div>
    <div class="sg-set"><div class="sg-sh">✅ الأنواع</div><div class="sg-flt">${Object.entries(ty).map(([k,t])=>`<button class="${T[k]!==false?'on':''}" onclick="sgSet({types:{${k}:${T[k]===false}}})">${t[0]} ${gEsc(t[1])}</button>`).join('')}</div>
      <div class="ind-sub">🧭 السوق: حين يثبت وضع جديد · 🌊 يصلك من «📊 تنبيهات المؤشرات» حين تكون مفعّلة (لا يتكرر) · ✅ النتائج: بعد وقت كل إشارة وصلتك</div></div>
    <div class="sg-set"><div class="sg-sh">🕯️ الفريم</div><div class="sg-flt">${['1D','4H'].map(f=>`<button class="${(c.fr||{})[f]!==false?'on':''}" onclick="sgSet({fr:{'${f}':${(c.fr||{})[f]===false}}})">${gEsc((V.fn||{})[f]||f)}</button>`).join('')}</div></div>
    <div class="sg-set"><div class="sg-sh">🪙 العملات <small>(${mine.length})</small> ${c.coins?`<button onclick="sgSet({coins:null})">↩️ مثل الشريط</button>`:'<small>· مثل الشريط (📊)</small>'}</div>
      <div class="sg-flt">${(V.uni||[]).map(s=>`<button class="${mine.includes(s)?'on':''}" onclick="sgCoinTog('${gEsc(s)}')">${gEsc(s.split('-')[0])}</button>`).join('')}</div></div>
    <div class="sg-set"><div class="sg-sh">📮 الحد اليومي <small>(الزائد يبقى في اللوحة بلا رنّة)</small></div><div class="sg-flt">${[3,5,8,12,20,0].map(n=>`<button class="${c.cap===n?'on':''}" onclick="sgSet({cap:${n}})">${n||'بلا حد'}</button>`).join('')}</div></div>
    <div class="sg-set"><div class="sg-sh">🌙 ساعات الهدوء <small>(تنتظر ثم تصلك برسالة واحدة)</small></div>
      ${tg(!!q,q?'sgSet({quiet:null})':'sgSet({quiet:[0,8]})','مفعّلة','متوقفة')} ${q?`من ${hsel('sg_q0',q[0],`sgSet({quiet:[+this.value,${q[1]}]})`)} إلى ${hsel('sg_q1',q[1],`sgSet({quiet:[${q[0]},+this.value]})`)}`:''}</div>
    <div class="sg-set"><div class="sg-sh">🗓️ ملخص يومي بدل الإشعارات المتفرقة</div>${hsel('sg_sum',c.sum,`sgSet({sum:this.value===''?null:+this.value})`,'لا — كل إشعار بوقته')}</div>
    <div class="sg-set"><div class="sg-sh">📨 أين تصل</div><div class="sg-flt">${Object.entries(V.ch||{}).map(([k,t])=>`<button class="${c.ch===k?'on':''}" onclick="sgSet({ch:'${k}'})">${gEsc(t)}</button>`).join('')}</div></div>
    <div class="sg-set sg-flt"><button onclick="sgTest()">🧪 جرّب إشعاراً</button><button onclick="sgRebuild()">🏗️ أعد البحث عن التركيبات الآن</button></div>
    <div class="ind-sub">إشعار واحد لكل عملة يجمع كل ما اتفق · نفس العملة ونفس النوع لا يتكرر (يوم على 4 ساعات · 3 أيام على اليومي) إلا إذا طلعت أقوى بوضوح · الضغط على الإشعار في الهاتف يفتح هذه النافذة.</div></div>`}
async function sgTest(){try{const r=await api('/api/control',{action:'sg_test'});toast(r&&r.msg?r.msg:'تم',!!(r&&r.ok))}catch(e){toast('تعذر الاتصال',false)}}
async function sgRebuild(){try{const r=await api('/api/control',{action:'sg_rebuild'});toast(r&&r.msg?r.msg:'تم',!!(r&&r.ok))}catch(e){toast('تعذر الاتصال',false)}SGTAB='now';setTimeout(sgLoad,1500)}
function sgRender(){const el=$('#sg_body'),tb=$('#sg_tabs');if(!el)return;const V=SGV;
  if(tb)tb.innerHTML=[['now','🎯 الآن'],['cat','📒 الدليل'],['log','🧾 السجل'],['cfg','⚙️ الإشعارات']].map(([k,t])=>`<button class="${SGTAB===k?'on':''}" onclick="sgTab('${k}')">${t}</button>`).join('');
  if(!V||V.ok===false){el.innerHTML='⚠️ تعذّر تحميل الإشارات';return}
  el.style.cssText='text-align:right';
  el.innerHTML=SGTAB==='cat'?sgCatUI(V):SGTAB==='log'?sgLog(V):SGTAB==='cfg'?sgCfg(V):sgNow(V)}
function sgFcTop(S){if(!S)return '';const C=S.comp,nm=C&&SGCOMP[C.s];               // 🔮 v3.36.66: الإشارات داخل التوقعات
  return `<button class="sg-go" onclick="openSig('now')">🎯 <b>الإشارات الآن</b>${S.ready?` · <b style="color:var(--green)">🟢 ${S.nb}</b> · <b style="color:var(--red)">🔴 ${S.ns}</b> تمر بإعداداتك`:' · 🏗️ الدليل يُبنى'}${nm?` · 🧭 السوق ${nm[1]} ${nm[0]}`:''} ←</button>`}
function sgFc(r){const S=r.sig;if(!S)return '';const fs=['1D','4H'].filter(f=>S[f]&&(S[f].rows||[]).length);if(!fs.length)return '';
  const best=fs.map(f=>S[f].rows[0]).filter(Boolean).sort((a,b)=>(b.ok-a.ok)||(b.h-a.h))[0];
  return `<div class="sg-fc" onclick="event.stopPropagation();SGO['${gEsc(r.sym)}']=true;openSig('now')">🎯 ${fs.map(f=>`${f==='1D'?'يومي':'4 ساعات'}: <b style="color:var(--green)">🟢 ${S[f].nb}</b> · <b style="color:var(--red)">🔴 ${S[f].ns}</b>`).join(' · ')}
    ${best?`<small> — أقواها: ${gEsc(best.nm.join(' + '))} (صدقت ${best.w} من ${sgAr(best.n,'time')} · ${(+best.h).toFixed(0)}%)</small>`:''}</div>`}
function sgMini(){return `<div class="ind-al" style="margin-top:10px"><div class="ind-al-h"><b>🎯 إشعارات الإشارات — شراء · بيع · تجميع · تصريف · صعود · نزول · السوق</b>
  <span style="display:flex;gap:6px"><button onclick="openSig('cfg')">⚙️ الإعدادات</button><button onclick="openSig('now')">🎯 الآن</button></span></div>
  <div class="ind-sub" style="margin-top:6px">كل إشارة وكل تركيبة (2 … 6 معاً) بسجلها على الأسعار الحقيقية · تصلك بالنسبة وعدد المرات اللي تختارهما · مع تقدير كم إشعاراً بالأسبوع قبل أن تختار</div></div>`}
'''

CSS = r'''
.sg-tabs{display:flex;gap:6px;flex-wrap:wrap;margin:2px 0 8px}.sg-tabs button{flex:1;min-width:84px;padding:7px 8px;border-radius:10px;font-size:12.5px}
.sg-tabs button.on,.sg-flt button.on{border-color:var(--vio);color:var(--vio);background:rgb(var(--vio-rgb)/.12)}
.sg-flt{display:flex;gap:5px;flex-wrap:wrap;margin:4px 0}.sg-flt button{font-size:11.5px;padding:4px 10px;border-radius:999px}
.sg-flt select,.sg-flt input{font-size:12px;padding:5px 8px;border-radius:9px;border:1px solid var(--line2);background:var(--bg1);color:var(--tx);min-width:0}
.sg-flt input{flex:1;min-width:150px}
.sg-r{border:1px solid var(--line);border-radius:11px;padding:7px 9px;margin:6px 0;background:rgb(var(--ov-rgb)/.025);font-size:12px;text-align:start}
.sg-r.ok{border-color:rgb(var(--green-rgb)/.45)}.sg-r.ok.sell{border-color:rgb(var(--red-rgb)/.45)}
.sg-rh{display:flex;gap:6px;align-items:center;flex-wrap:wrap}.sg-ty{font-weight:700}.sg-fr{font-size:11px;color:var(--mut2)}
.sg-b{font-size:10.5px;padding:0 7px;border-radius:999px;border:1px solid var(--line)}.sg-b.rare{color:var(--cyan);border-color:rgb(var(--cyan-rgb)/.5)}
.sg-b.new{color:var(--amber);border-color:rgb(var(--amber-rgb)/.5)}.sg-b.ok{color:var(--green);border-color:rgb(var(--green-rgb)/.5)}
.sg-k{margin:4px 0 2px;line-height:1.65;color:var(--tx)}.sg-k b{color:var(--vio)}
.sg-rec{font-size:11px;color:var(--mut2);line-height:1.7}.sg-rec .up,.sg-lg .up{color:var(--green)}.sg-rec .dn,.sg-lg .dn{color:var(--red)}
.sg-comp{border:1px solid var(--line2);border-radius:13px;padding:9px 12px;margin-bottom:8px;background:var(--bg1)}
.sg-comp.p{border-color:rgb(var(--green-rgb)/.5)}.sg-comp.n{border-color:rgb(var(--red-rgb)/.5)}.sg-comp.z{border-color:rgb(var(--amber-rgb)/.5)}
.sg-hist{display:flex;gap:2px;margin-top:6px;direction:ltr}.sg-hist i{flex:1;height:8px;border-radius:2px;background:var(--line2)}
.sg-hist i.up{background:rgb(var(--green-rgb)/.75)}.sg-hist i.down{background:rgb(var(--red-rgb)/.75)}.sg-hist i.flat{background:rgb(var(--amber-rgb)/.7)}
.sg-busy{font-size:12px;color:var(--mut);margin:6px 0}.sg-pb{height:5px;border-radius:9px;background:var(--line);margin-top:4px;overflow:hidden}
.sg-pb i{display:block;height:100%;background:var(--vio);transition:width .6s}
.sg-empty{font-size:12.5px;color:var(--mut);line-height:1.9;padding:10px 4px}
.sg-frh{font-weight:700;margin:10px 0 2px;font-size:12.5px}.sg-more summary{cursor:pointer;font-size:12px;color:var(--mut);margin:8px 0}
.sg-lg{border-bottom:1px dashed var(--line2);padding:6px 0;font-size:12px}
.sg-set{margin:10px 0;padding-top:8px;border-top:1px dashed var(--line2)}.sg-sh{font-size:12.5px;margin-bottom:4px}
.sg-set input[type=range]{width:100%;accent-color:var(--vio)}.sg-set select{font-size:12px;padding:4px 6px;border-radius:8px;background:var(--bg1);color:var(--tx);border:1px solid var(--line2)}
.sg-go{display:block;width:100%;text-align:start;margin:0 0 8px;padding:8px 11px;border-radius:12px;font-size:12.5px;border-color:rgb(var(--vio-rgb)/.45)}
.sg-fc{font-size:11.5px;color:var(--mut);margin:6px 0 2px;padding:5px 8px;border-radius:9px;background:rgb(var(--vio-rgb)/.07);cursor:pointer;line-height:1.7}
'''

R = [
    # server: the signals after the forecasts' loop
    ("""# ═══════════════ 🔔 v3.26.6: إشعارات الأسعار — مثل إشعارات البرامج""",
     PY.lstrip("\n") + PY_FC + "\n\n# ═══════════════ 🔔 v3.26.6: إشعارات الأسعار — مثل إشعارات البرامج"),
    # routes (GET)
    ("""        if u.path == "/api/forecast":                     # 🔮 v3.29.0: التوقعات (نفس مؤشرات 📊 على شموع أطول · قراءة عامة · عرض بس · ولا إشعار)""",
     """        if u.path == "/api/signals":                      # 🎯 v3.36.66: الإشارات (من الملفات · لا تنتظر الحساب أبداً)
            return self._json(_safe(sg_api, default={"ok": False, "msg": "تعذّر تحميل الإشارات"}))
        if u.path == "/api/signals_cat":                  # 📒 دليل الإشارات للتصفّح
            return self._json(_safe(sg_catlist, q, default={"ok": False, "rows": [], "msg": "تعذّر تحميل الدليل"}))
        if u.path == "/api/forecast":                     # 🔮 v3.29.0: التوقعات (نفس مؤشرات 📊 على شموع أطول · قراءة عامة · عرض بس · ولا إشعار)"""),
    # control actions (POST)
    ("""            if act == "ina_set":                          # 📊 v3.31.0: تنبيهات المؤشرات — تشغيل/إطفاء · الحساسية · وين توصل""",
     """            if act == "sg_set":                           # 🎯 v3.36.66: إشعارات الإشارات
                return self._json(sg_set((data.get("value") if isinstance(data.get("value"), dict) else {})))
            if act == "sg_est":
                return self._json(_safe(sg_est, (data.get("value") if isinstance(data.get("value"), dict) else {}), default={"ok": False, "est": None}))
            if act == "sg_test":
                return self._json(sg_test())
            if act == "sg_rebuild":
                return self._json(sg_rebuild())
            if act == "ina_set":                          # 📊 v3.31.0: تنبيهات المؤشرات — تشغيل/إطفاء · الحساسية · وين توصل"""),
    # 🔮 every coin gets its signals
    ("""    v = fc_view()
    if not v["rows"] and v["on"] and ticker_cfg()["coins"] and not _FC_RUN["busy"]:""",
     """    v = fc_view()
    v["rows"] = [dict(r) for r in v["rows"]]
    v["sig"] = _safe(sg_fc, v["rows"], default=None)          # 🎯 v3.36.66: إشارات كل عملة الآن + البوصلة
    if not v["rows"] and v["on"] and ticker_cfg()["coins"] and not _FC_RUN["busy"]:"""),
    # the loop thread
    ("""        threading.Thread(target=pro_loop, daemon=True).start()      # 🏦🗞️ v3.33.0: المحترفون والاقتصاد (حلقة مستقلة)""",
     """        threading.Thread(target=pro_loop, daemon=True).start()      # 🏦🗞️ v3.33.0: المحترفون والاقتصاد (حلقة مستقلة)
        threading.Thread(target=sg_loop, daemon=True).start()       # 🎯 v3.36.66: الإشارات (الحساب الثقيل بعملية منفصلة)"""),
    # the worker entry
    ("""    if len(sys.argv) >= 3 and sys.argv[1] == "--holy-demo-cfg":   # 🧪 v3.36.46: إعداد الديمو (دالة النشر نفسها · بلا شبكة)""",
     """    if len(sys.argv) >= 3 and sys.argv[1] == "--holy-sig":        # 🎯 v3.36.66: عامل الإشارات (عملية منفصلة بلا شبكة · أولوية منخفضة)
        sys.exit(sg_child(sys.argv[2], proc=True))
    if len(sys.argv) >= 3 and sys.argv[1] == "--holy-demo-cfg":   # 🧪 v3.36.46: إعداد الديمو (دالة النشر نفسها · بلا شبكة)"""),
    # page: JS before the forecasts' block
    ("""/* 🔮 v3.29.0: التوقعات — نفس مؤشرات 📊 على شموع أطول""", JS.lstrip("\n") + """/* 🔮 v3.29.0: التوقعات — نفس مؤشرات 📊 على شموع أطول"""),
    # 🔮 window: the signals on top and on every coin
    ("""  let h=`<div class="ind-top"><span class="ind-chip">📊 نفس مؤشرات «المؤشرات» + 4 إضافات</span>""",
     """  let h=sgFcTop(V.sig)+`<div class="ind-top"><span class="ind-chip">📊 نفس مؤشرات «المؤشرات» + 4 إضافات</span>"""),
    ("""      ${fcBot(r)}<div class="fc-rows"><div class="fc-r fc-hd">""", """      ${fcBot(r)}${sgFc(r)}<div class="fc-rows"><div class="fc-r fc-hd">"""),
    # 📊 window: a button
    ("""    <div class="mbtns"><button onclick="openGuide('','ind')">📖 الدليل</button><button onclick="openTicker()">⚙️ العملات</button><button onclick="hideModal()">إغلاق</button></div>`);
  await indLoad()}""",
     """    <div class="mbtns"><button onclick="openSig()">🎯 الإشارات</button><button onclick="openGuide('','ind')">📖 الدليل</button><button onclick="openTicker()">⚙️ العملات</button><button onclick="hideModal()">إغلاق</button></div>`);
  await indLoad()}"""),
    # 🔮 window: a button
    ("""    <div class="mbtns"><button onclick="openGuide('','fc')">📖 الدليل</button><button onclick="openTicker()">⚙️ العملات</button><button onclick="hideModal()">إغلاق</button></div>`);
  await fcLoad()}""",
     """    <div class="mbtns"><button onclick="openSig()">🎯 الإشارات</button><button onclick="openGuide('','fc')">📖 الدليل</button><button onclick="openTicker()">⚙️ العملات</button><button onclick="hideModal()">إغلاق</button></div>`);
  await fcLoad()}"""),
    # the ticker's settings: a panel
    ("""function pxaRender(){const el=$('#tk_pxa');if(el)el.innerHTML=(PXAV?pxaPanel(PXAV):'')+(INAV?inaPanel(INAV):'')}""",
     """function pxaRender(){const el=$('#tk_pxa');if(el)el.innerHTML=(PXAV?pxaPanel(PXAV):'')+(INAV?inaPanel(INAV):'')+sgMini()}"""),
    # ⚙️: a row
    ("""     +L('📈','شريط الأسعار وإشعاراته','openTicker()','العملات في الشريط · إشعارات الأسعار'))}""",
     """     +L('📈','شريط الأسعار وإشعاراته','openTicker()','العملات في الشريط · إشعارات الأسعار')
     +L('🎯','الإشارات وإشعاراتها',"openSig('cfg')",'شراء · بيع · تجميع · صعود · نزول · السوق — بنسبتك'))}"""),
    # a notification tap opens 🎯
    ("""  if(k==='ind')return openInd();""", """  if(k==='ind')return openInd();
  if(k==='sig')return openSig('now');                            // 🎯 v3.36.66"""),
    # css
    (""".fc-tabs{display:flex;gap:5px;flex-wrap:wrap;margin:2px 0 8px}""", CSS.strip("\n") + "\n.fc-tabs{display:flex;gap:5px;flex-wrap:wrap;margin:2px 0 8px}"),
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
    print(f"✅ {len(R)} replacements · 🎯 the signals (catalog · scans · live record · compass · notifications · 🔮) · compiles · {p}")
