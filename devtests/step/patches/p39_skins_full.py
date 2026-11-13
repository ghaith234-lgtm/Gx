# 🃏 patch 39 (dashboard · card skins ج · ب · OKX) — the owner (13-11): «اريد الكروت ج ب و okx تظهر كلشي مثل القديم واتزيل (كل التفاصيل
#   الشكل القديم) وتظهر كل الكتابات لان كلها مو ظاهرة».
#   ① everything the old card shows is on the new skins: after each skin's own six-or-so numbers, EVERY other label/value row of the
#      card (♾️ «📡 أوامر المنصة» · «📊 متوسط البوتات» · 🏦 «النطاق · النسبة» · «المحفظة» · «التشغيل» … and any row added later) is
#      appended by itself — read from the card itself (rows hidden on the old card stay hidden) · every button of the old card is
#      reachable (the ones the skin had no place for go into «⋯», before the delete)
#   ② «🗂️ كل التفاصيل (الشكل القديم)» removed from every «⋯» (nothing is left behind it)
#   ③ every text shows in full: no «…» cut on the skins — titles, labels, numbers, the caption, buttons wrap to a second line · the
#      buttons on ب / OKX carry their full label (were cut to two words) · ج's icon buttons get their label next to the icon
#   python3 devtests/step/patches/p39_skins_full.py Holy_Dashboard.pyw
import os, sys

JS_REST = '''/* 🃏 v3.36.33 (المالك 13-11 «تظهر كلشي مثل القديم»): كل صف بالبطاقة القديمة ما ظهر بالشكل ⇐ ينضاف وحده (من البطاقة نفسها · المخفي يبقى مخفي) ·
   وكل زر بالقديمة ما إله مكان ⇐ داخل «⋯» */
let SK_SEEN=null;
function skHidden(n,el){for(let p=n;p&&p!==el;p=p.parentElement)if(p.style&&p.style.display==='none')return true;return false}
function skRest(el,seen){const out=[];
  el.querySelectorAll('.row,.dcacell,.rcrow,.dcacyclbl,.rcri,.blbl').forEach(r=>{
    if(r.closest('.skin')||skHidden(r,el))return;
    const v=[...r.querySelectorAll('[data-k]')].find(n=>n.tagName!=='BUTTON'&&!/(fill|bar|row)$/.test(n.dataset.k));
    if(!v||seen.has(v.dataset.k))return;
    const lb=r.querySelector('.nm,.dl')||r.firstElementChild;if(!lb||lb===v||lb.contains(v))return;
    const t=(v.textContent||'').replace(/\\s+/g,' ').trim(),l=(lb.textContent||'').replace(/\\s+/g,' ').trim();if(!l)return;
    seen.add(v.dataset.k);out.push([l,t||'—',v.dataset.k])});
  return out}
function skBtnRest(el,M){const have=new Set([(M.main||{}).k].concat(M.ic.map(x=>x&&x.k),M.menu.map(x=>x&&x.k)));
  el.querySelectorAll('button[data-k]').forEach(n=>{const k=n.dataset.k;if(have.has(k)||n.closest('.skin')||skHidden(n,el))return;
    const t=(n.textContent||'').replace(/\\s+/g,' ').trim()||n.title||'';if(!t||t==='—')return;
    have.add(k);const it={k,t,dis:!!n.disabled};if(n.classList.contains('danger'))it.dz=1;
    const dl=M.menu.findIndex(x=>x&&x.dz);M.menu.splice(dl<0?M.menu.length:dl,0,it)})}
'''

R = [
    # ① every row · every button
    ('''function skText(el,k){const R=el._r||{},n=R[k];''', JS_REST + '''function skText(el,k){if(SK_SEEN)SK_SEEN.add(k);const R=el._r||{},n=R[k];'''),
    ('''function skModel(el,b,kd){
  const R=el._r||{},''', '''function skModel(el,b,kd){
  SK_SEEN=new Set(['cp','profit','today','delta','apl','pill','apill','hb','ptrend']);   // 🃏 v3.36.33: ما يظهر بمكان ثاني بالشكل (الربح الكبير · اليوم · السعر)
  const R=el._r||{},'''),
    ('''  M.ic=M.ic.filter(Boolean);M.menu=M.menu.filter(x=>x&&!x.hide);
  return M}''', '''  M.ic=M.ic.filter(Boolean);M.menu=M.menu.filter(x=>x&&!x.hide);
  try{M.m=M.m.concat(skRest(el,SK_SEEN||new Set()));skBtnRest(el,M)}catch(e){console.error('skin rest',e)}SK_SEEN=null;
  return M}'''),
    # 💹 the value path's status line («خطوات · بيعات · أوامر») under its hint, like the old card
    ('''    M.note=R.hint?R.hint.innerHTML:''}''',
     '''    M.note=(R.hint?R.hint.innerHTML:'')+(skText(el,'status')&&skText(el,'status')!=='—'?`<div>${SKN(skText(el,'status'))}</div>`:'')}'''),
    # ② no «🗂️ كل التفاصيل (الشكل القديم)»
    ('''   «⋯» فيها باقي الأزرار · «🗂️ كل التفاصيل» تفتح البطاقة القديمة كاملة لهذه البطاقة */''',
     '''   «⋯» فيها باقي الأزرار · v3.36.33: كل صف وكل زر بالقديمة ظاهر بالشكل نفسه ⇒ انشال «🗂️ كل التفاصيل (الشكل القديم)» */'''),
    # ③ full labels on the buttons
    ('''data-sk="${x.k}" title="${SKE(x.t)}" aria-label="${SKE(x.t)}" ${x.dis?'disabled':''}>${skIcon(x)}</button>''',
     '''data-sk="${x.k}" title="${SKE(x.t)}" aria-label="${SKE(x.t)}" ${x.dis?'disabled':''}>${SKE(x.t)}</button>'''),
]
# the two «skShort» button labels (ب · OKX) — full labels
SHORT = ('''SKE(skShort(x.t))''', '''SKE(x.t)''')
FULL_MENU = '''{k:'full',t:'🗂️ كل التفاصيل (الشكل القديم)'},'''

CSS_ANCHOR = '''.sk-seg button:first-child{border:0;flex:2}.sk-seg button:disabled{opacity:.45}'''
CSS_ADD = CSS_ANCHOR + '''
/* 🃏 v3.36.33 (المالك 13-11 «تظهر كل الكتابات»): لا قصّ «…» بالأشكال الجديدة — كل نص يلتف لسطر ثانٍ · الأزرار بكامل كلامها */
.card.sk .skin :is(.sk-top .t b,.sk-top .t small,.sk-two .cap,.sk-m3 small,.sk-m3 b,.sk-kpi small,.sk-kpi b,.sk-meta span,.ok-tag){white-space:normal;overflow:visible;text-overflow:clip;overflow-wrap:anywhere}
.card.sk .skin .sk-meta span{max-width:none}
.card.sk .skin :is(.sk-ft .main,.ok-ft>button,.sk-seg button){white-space:normal;overflow:visible;text-overflow:clip;height:auto;min-height:34px;line-height:1.3;padding-block:5px;overflow-wrap:anywhere}
.card.sk .skin .sk-ft{flex-wrap:wrap}.card.sk .skin .sk-ft .main{flex:1 1 100%}
.card.sk .skin .sk-ft .ic{width:auto;height:auto;min-height:34px;flex:1 1 auto;padding:5px 9px;font-size:12px;line-height:1.3}
.card.sk .skin .sk-seg{flex-wrap:wrap}.card.sk .skin .sk-seg button{flex:1 1 auto}'''

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    if s.count(SHORT[0]) != 2:
        print(f"❌ «skShort» button labels: found {s.count(SHORT[0])} (want 2) — nothing written"); sys.exit(1)
    s = s.replace(*SHORT)
    if s.count(FULL_MENU) != 5:
        print(f"❌ «كل التفاصيل»: found {s.count(FULL_MENU)} (want 5) — nothing written"); sys.exit(1)
    s = s.replace(FULL_MENU, "")
    if s.count(CSS_ANCHOR) != 1:
        print("❌ CSS anchor not found once — nothing written"); sys.exit(1)
    s = s.replace(CSS_ANCHOR, CSS_ADD)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 2 full button labels · 5 «كل التفاصيل» removed · the wrap CSS · compiles · {p}")
