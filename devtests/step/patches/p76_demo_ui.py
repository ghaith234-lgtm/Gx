# 🧪 patch 76 (dashboard v3.36.46 · the demo — the page) — the owner (14-11): «… وينشرن تحت بعد الحقيقيات يعني خط فاصل بينهم ما فيه مجموع
#   بينهم فقط كل بوت وكرته وينكتب عليه ديمو».
#   · every deploy form (♾️ ➕ 🎚️ · 🪜 · DCA · the recurring · 💹) gets «🧪 ديمو» after its wallet field: a demo needs no wallet, only
#     its paper balances (empty ⇒ the trial path's suggested wallet for that plan) — the request goes to deploy_demo() (p75)
#   · the cards: the real bots first, then a line «🧪 بوتات ديمو …», then the demo bots — each demo card wears «🧪 ديمو» and a dashed
#     border · the profit bar's benchmark and the counter leave the demo out («N بوت · M ديمو»)
#   (the totals · ledgers · Telegram · reports already keep demo bots out — t_demo checks it)
#   python3 devtests/step/patches/p76_demo_ui.py Holy_Dashboard.pyw
import os, re, sys

JS = r'''/* 🧪 v3.36.46: الديمو — المحرك الحقيقي على منصة وهمية بسعر OKX الحي (بلا مفاتيح · لا أوامر حقيقية · خارج كل المجاميع) */
function demoFld(p,on){return `<div class="fld demofld" style="grid-column:1/-1"><label class="ck"><input type="checkbox" id="${p}_demo" ${on?'checked':''} onchange="demoTgl('${p}')">🧪 ديمو — المحرك الحقيقي نفسه على منصة وهمية بسعر OKX الحي (بلا مفاتيح · لا أوامر حقيقية · لا يدخل في أي مجموع)</label>
  <div class="demobox" id="${p}_dbox" style="display:${on?'grid':'none'}"><div class="fld"><label>💵 رصيد الديمو بالدولار</label><input id="${p}_dusd" class="num" inputmode="decimal" placeholder="تلقائي"></div>
  <div class="fld"><label>🪙 رصيد الديمو بالعملة</label><input id="${p}_dcoin" class="num" inputmode="decimal" placeholder="تلقائي"></div>
  <small>فارغ = محفظة مقترحة تكفي خطة هذا البوت (مثل الاختبار التجريبي) · لا حاجة إلى محفظة OKX</small></div></div>`}
function demoTgl(p){const c=$('#'+p+'_demo'),b=$('#'+p+'_dbox');if(c&&b)b.style.display=c.checked?'grid':'none'}
function demoVal(p){const c=$('#'+p+'_demo');if(!c||!c.checked)return {demo:false};
  return {demo:true,demo_usd:(($('#'+p+'_dusd')||{}).value||'').trim(),demo_coin:(($('#'+p+'_dcoin')||{}).value||'').trim()}}
function demoMark(el,b){const on=!!b.demo;if(el.classList.contains('isdemo')!==on)el.classList.toggle('isdemo',on);
  let m=el.querySelector('.demob');
  if(on&&!m){m=document.createElement('span');m.className='demob';m.textContent='🧪 ديمو';
    m.title='بوت ديمو: المحرك الحقيقي نفسه على منصة وهمية بسعر OKX الحي ومحفظة وهمية — لا أوامر حقيقية ولا يدخل في أي مجموع';
    const h=el.querySelector('.chead .sym')||el.querySelector('.chead')||el;h.appendChild(m)}
  else if(!on&&m)m.remove()}
'''

CSS = r'''.demosep{grid-column:1/-1;display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;margin:14px 2px 0;padding:10px 4px 0;border-top:2px dashed rgb(var(--cyan-rgb)/.45);color:var(--cyan)}
.demosep span{font-weight:800;font-size:15px}.demosep small{color:var(--mut);font-size:12px;line-height:1.6}
.card.isdemo{border-style:dashed;border-color:rgb(var(--cyan-rgb)/.55)}
.demob{display:inline-block;margin-inline-start:8px;padding:2px 8px;border-radius:999px;font-size:11.5px;font-weight:700;vertical-align:middle;
  color:var(--cyan);background:rgb(var(--cyan-rgb)/.10);border:1px dashed rgb(var(--cyan-rgb)/.55)}
.demofld .ck{line-height:1.6}.demobox{grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px 12px;margin-top:8px}
.demobox small{grid-column:1/-1;color:var(--mut2);font-size:11.5px}
'''

R = [
    # ── the cards: real first · the line · demo after ──
    ('''  let profits=allBots.map(x=>x.profit);''',
     '''  let profits=allBots.filter(x=>!x.demo).map(x=>x.profit);   // 🧪 v3.36.46: الديمو خارج المقارنة'''),
    ('''  bots=sortBots(bots);
  const shown=new Set(bots.map(b=>b.dir));''',
     '''  bots=sortBots(bots);
  bots=bots.filter(b=>!b.demo).concat(bots.filter(b=>b.demo));   // 🧪 v3.36.46: الحقيقية أولاً ثم الديمو تحت خط فاصل
  const shown=new Set(bots.map(b=>b.dir));'''),
    ('''    updCard(el,b,bench);skinUpd(el,b);caNumChk(el,b)});''',
     '''    updCard(el,b,bench);skinUpd(el,b);caNumChk(el,b);demoMark(el,b)});'''),
    ('''  const wantOrder=bots.map(b=>b.dir).join('|');
  if(grid._lastOrder!==wantOrder){
    grid._lastOrder=wantOrder;
    bots.forEach(b=>{const el=CARDS.get(b.dir);if(el)grid.appendChild(el)});
  }''',
     '''  const wantOrder=bots.map(b=>(b.demo?'d:':'')+b.dir).join('|');
  let dsep=document.getElementById('demoSep');
  const nDemo=bots.filter(b=>b.demo).length;
  if(nDemo&&!dsep){dsep=document.createElement('div');dsep.id='demoSep';dsep.className='demosep';
    dsep.innerHTML='<span>🧪 بوتات ديمو</span><small>المحرك الحقيقي نفسه على منصة وهمية بسعر OKX الحي ومحفظة وهمية — لا أوامر حقيقية · لا تدخل في أي مجموع</small>'}
  if(grid._lastOrder!==wantOrder){
    grid._lastOrder=wantOrder;
    bots.forEach((b,i)=>{if(b.demo&&dsep&&(i===0||!bots[i-1].demo))grid.appendChild(dsep);const el=CARDS.get(b.dir);if(el)grid.appendChild(el)});
  }
  if(!nDemo&&dsep)dsep.remove();'''),
    ('''  if(FILTER.q)fc.textContent=[`${bots.length} من ${allBots.length} بوت`,ac].filter(Boolean).join(' · ');
  else fc.textContent=[allBots.length?`${allBots.length} بوت`:'',ac].filter(Boolean).join(' · ');''',
     '''  const _nd=allBots.filter(b=>b.demo).length,_nr=allBots.length-_nd;          // 🧪 v3.36.46: الديمو يُعدّ وحده
  if(FILTER.q)fc.textContent=[`${bots.length} من ${allBots.length} بوت`,ac].filter(Boolean).join(' · ');
  else fc.textContent=[_nr?`${_nr} بوت`:'',_nd?`${_nd} ديمو`:'',ac].filter(Boolean).join(' · ');'''),
    # ── accumulator cards stay above the demo line ──
    ('''      ACARDS.set(a.id,el); grid.appendChild(el); cardLockDeco(el);''',
     '''      ACARDS.set(a.id,el); grid.insertBefore(el,document.getElementById('demoSep')); cardLockDeco(el);   // 🧪 فوق خط الديمو'''),
    ('''  const tail=[...grid.children].slice(-want.length).map(e=>e.dataset.acc||'');
  if(want.length&&tail.join('|')!==want.join('|'))want.forEach(id=>{const el=ACARDS.get(id);if(el)grid.appendChild(el)});''',
     '''  const _ds=document.getElementById('demoSep'),_kids=[...grid.children],_cut=_ds?_kids.indexOf(_ds):_kids.length;   // 🧪 فوق خط الديمو
  const tail=_kids.slice(0,_cut).slice(-want.length).map(e=>e.dataset.acc||'');
  if(want.length&&tail.join('|')!==want.join('|'))want.forEach(id=>{const el=ACARDS.get(id);if(el)grid.insertBefore(el,_ds)});'''),
    # ── the old «تجريبي» chip in the card head gives way to «🧪 ديمو» (demoMark — every card kind) ──
    ('''${b.demo?'<span class="chip demo">تجريبي</span>':''}''', ''),
    ('''${b.demo?' <span class="chip demo">تجريبي</span>':''}''', '''${b.demo?' <span class="chip demo">🧪 ديمو</span>':''}'''),
    # ── the forms ──
    ('''    <label class="ck"><input type="checkbox" id="n_demo" ${pre.demo?'checked':''}>🧪 تجريبي DEMO</label>
''', ''),
    ('''    const body=vaFormBody();''', '''    const body=Object.assign(vaFormBody(),demoVal('vd'));   // 🧪 v3.36.46'''),
    ('''      if(body.first_src==='wallet'){''', '''      if(body.first_src==='wallet'&&!body.demo){           // 🧪 الديمو بلا محفظة حقيقية'''),
    ('''    const body=recFormBody();''', '''    const body=Object.assign(recFormBody(),demoVal('rd'));   // 🧪 v3.36.46'''),
    ('''    const body=dcaFormBody();
    if(!body.symbol||!body.symbol.includes('-')){toast('اكتب الرمز كاملاً مثل XRP-USDT',false);return}
    $('#dn_go').disabled=true;''',
     '''    const body=Object.assign(dcaFormBody(),demoVal('dn'));   // 🧪 v3.36.46
    if(!body.symbol||!body.symbol.includes('-')){toast('اكتب الرمز كاملاً مثل XRP-USDT',false);return}
    $('#dn_go').disabled=true;'''),
    ('''  $('#st_go').onclick=async()=>{const body=stBody();''', '''  $('#st_go').onclick=async()=>{const body=Object.assign(stBody(),demoVal('st'));   // 🧪 v3.36.46'''),
    ('''    const body=gridFormBody();''', '''    const body=Object.assign(gridFormBody(),demoVal('n'));   // 🧪 v3.36.46'''),
]
WALLETS = (("vd_wallet", "vd", "false"), ("rd_wallet", "rd", "false"), ("dn_wallet", "dn", "false"), ("st_wallet", "st", "false"),
           ("n_wallet", "n", "pre.demo"))

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    for wid, pre, on in WALLETS:                       # the demo field right after each form's wallet field
        m = re.search(r'(?m)^ *<div class="fld"><label>المحفظة</label><select id="%s"[^\n]*</select></div>' % wid, s)
        if not m or s.count('<select id="%s"' % wid) != 1:
            print(f"❌ the wallet field {wid} not found once — nothing written"); sys.exit(1)
        s = s[:m.end()] + "${demoFld('%s',%s)}" % (pre, on) + s[m.end():]
    a = "function walletKey(b){"
    if s.count(a) != 1:
        print("❌ JS anchor"); sys.exit(1)
    s = s.replace(a, JS + a)
    a = ".chip.demo{color:var(--cyan);border-color:var(--line2)}"
    if s.count(a) != 1:
        print("❌ CSS anchor"); sys.exit(1)
    s = s.replace(a, a + "\n" + CSS.strip())
    s = s.replace('APP_VERSION = "3.36.45"', 'APP_VERSION = "3.36.46"', 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements + {len(WALLETS)} demo fields · compiles · {p}")
