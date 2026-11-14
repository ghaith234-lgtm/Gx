# 📖 patch 78 (dashboard v3.36.47 · the tutorial inside the deploy forms) — the owner (14-11), after v3.36.46: «لم اجد زر التعليم · وانا
#   اريده مكان نشر البوتات» ⇒ «لا داخل كل بوت قبل النشر يعني عندما اضغط على الشبكي داخل يوجد زر لكل شبكي اله شرحه» ⇒ (asked how to lay it
#   out) «عند الدخول الى زر الشبكي فيه ثلاث بوتات كل بوت فيه زر اضغط عليه يخرج لي شرح» · the bar button and the card button: «أشيل الاثنين».
#   · the grid form: «📖» inside each of its three kind buttons (♾️ لانهائية · 🎚️ مدى · ➕ بلس) — it explains that kind and does not change
#     the kind chosen · DCA: «📖 شرح: 📉 البيعي · 📈 الشرائي» under its kind · the recurring: «📖 شرح: 🟢 الشرائي · 🔴 البيعي» · 🪜 and 💹
#     (one kind each): «📖 شرح …» under the title
#   · the form waits as it is while the explanation is open (what was typed stays) — «↩️ رجوع إلى النموذج» brings it back
#   · the card's 📖 (v3.36.46) is gone, as the owner asked
#   python3 devtests/step/patches/p78_tutorial_deploy.py Holy_Dashboard.pyw
import os, sys

JS = r'''/* 📖 v3.36.47: الشرح داخل نماذج النشر — زر لكل نوع (المالك: «عند الدخول الى زر الشبكي فيه ثلاث بوتات كل بوت فيه زر اضغط عليه يخرج لي شرح») */
let TUT_STASH=null;
function tutQ(ev,k){if(ev){ev.preventDefault();ev.stopPropagation()}const m=$('#modal');TUT_STASH=(m&&m.querySelector('.hwb'))||null;openTutKind(k,true)}
function tutBack(){const m=$('#modal');if(!m||!TUT_STASH)return;TUT_RUN=null;const cur=m.querySelector('.hwb');if(cur)m.replaceChild(TUT_STASH,cur);else m.appendChild(TUT_STASH);TUT_STASH=null;try{hwSync()}catch(e){}}
'''

TUTROW = '<div class="tutrow"><span>📖 شرح:</span>%s</div>'

R = [
    # openTut(dir) on the card ⇒ openTutKind(kind, back) from the forms
    ('''function openTut(dir){
  const b=(typeof botOf==='function'&&botOf(dir))||{};const k=TUT[b.bot_type]?b.bot_type:'grid',T=TUT[k];''',
     '''function openTutKind(kind,back){
  const b={};const k=TUT[kind]?kind:'grid',T=TUT[k];'''),
    ('''  let h=`<h2>📖 كيف يعمل بوت ${ico} ${T.t}${b.symbol?` — <span class="num">${b.symbol}</span>`:''}</h2>`;''',
     '''  let h=`<h2>📖 كيف يعمل بوت ${ico} ${T.t}</h2>`;
  if(back&&TUT_STASH)h+='<div class="tutbk"><button class="primary" onclick="tutBack()">↩️ رجوع إلى النموذج</button><small>ما كتبته في النموذج باقٍ كما هو</small></div>';'''),
    # the card's 📖 goes (the owner: «أشيل الاثنين»)
    ('''    updCard(el,b,bench);skinUpd(el,b);caNumChk(el,b);demoMark(el,b);tutMark(el,b)});   // 📖 v3.36.46''',
     '''    updCard(el,b,bench);skinUpd(el,b);caNumChk(el,b);demoMark(el,b)});'''),
    ('''function tutMark(el,b){if(el._tut)return;const s=el.querySelector('.cset');if(!s)return;
  const t=document.createElement('button');t.className='ctut';t.textContent='📖';t.title='📖 كيف يعمل هذا البوت — شرح ومثال متحرك وأسئلة';
  t.onclick=e=>{e.stopPropagation();openTut(b.dir)};s.parentNode.insertBefore(t,s);el._tut=1}
''', ''),
    # ── the grid form: 📖 inside each kind button ──
    ('''    <button type="button" data-gt="grid" onclick="gType('grid')" style="flex:1">♾️ لانهائية</button>
    <button type="button" data-gt="grid_range" onclick="gType('grid_range')" style="flex:1">🎚️ مدى</button>
    <button type="button" data-gt="grid_plus" onclick="gType('grid_plus')" style="flex:1">➕ بلس</button>''',
     '''    <button type="button" data-gt="grid" onclick="gType('grid')" style="flex:1">♾️ لانهائية <span class="tutq" title="شرح الشبكة اللانهائية — مثال متحرك وأسئلة" onclick="tutQ(event,'grid')">📖</span></button>
    <button type="button" data-gt="grid_range" onclick="gType('grid_range')" style="flex:1">🎚️ مدى <span class="tutq" title="شرح المدى — مثال متحرك وأسئلة" onclick="tutQ(event,'grid_range')">📖</span></button>
    <button type="button" data-gt="grid_plus" onclick="gType('grid_plus')" style="flex:1">➕ بلس <span class="tutq" title="شرح البلس — مثال متحرك وأسئلة" onclick="tutQ(event,'grid_plus')">📖</span></button>'''),
    # ── DCA ──
    ('''    <option value="dca_buy">📈 شرائي — يشتري عند النزول، يجمّع الدولار (الربح بالدولار)</option>
  </select></div>''',
     '''    <option value="dca_buy">📈 شرائي — يشتري عند النزول، يجمّع الدولار (الربح بالدولار)</option>
  </select></div>
  ''' + TUTROW % '''<button type="button" onclick="tutQ(event,'dca')">📉 البيعي</button><button type="button" onclick="tutQ(event,'dca_buy')">📈 الشرائي</button>'''),
    # ── the recurring ──
    ('''    <option value="rec_sell">🔴 بيعي — يبيع عملات كل فترة ويرجع يشتري أكثر (الربح عملة)</option>
  </select></div>''',
     '''    <option value="rec_sell">🔴 بيعي — يبيع عملات كل فترة ويرجع يشتري أكثر (الربح عملة)</option>
  </select></div>
  ''' + TUTROW % '''<button type="button" onclick="tutQ(event,'rec_buy')">🟢 الشرائي</button><button type="button" onclick="tutQ(event,'rec_sell')">🔴 البيعي</button>'''),
    # ── 🪜 · 💹 ──
    ('''  showModal(`<h2 style="color:var(--cyan)">🪜 نشر «الشبكي المتدرج»</h2>''',
     '''  showModal(`<h2 style="color:var(--cyan)">🪜 نشر «الشبكي المتدرج»</h2>
  ''' + TUTROW % '''<button type="button" onclick="tutQ(event,'grid_step')">🪜 الشبكي المتدرج</button>'''),
    ('''  showModal(`<h2 style="color:var(--cyan)">💹 نشر بوت «مسار القيمة»</h2>''',
     '''  showModal(`<h2 style="color:var(--cyan)">💹 نشر بوت «مسار القيمة»</h2>
  ''' + TUTROW % '''<button type="button" onclick="tutQ(event,'rec_va')">💹 مسار القيمة</button>'''),
]

CSS = r'''.tutq{display:inline-block;margin-inline-start:4px;padding:1px 6px;border-radius:8px;border:1px solid var(--line2);background:rgb(var(--vio-rgb)/.12);font-size:12px;cursor:help}
.tutq:hover{background:rgb(var(--vio-rgb)/.25)}
.tutrow{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:6px 0 10px}.tutrow span{color:var(--mut);font-size:12.5px}
.tutrow button{font-size:12px;padding:5px 11px}
.tutbk{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:4px 0 6px}.tutbk small{color:var(--mut2);font-size:11.5px}
'''

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    a = "function walletKey(b){"
    if s.count(a) != 1:
        print("❌ JS anchor"); sys.exit(1)
    s = s.replace(a, JS + a)
    a = ".chip.demo{color:var(--cyan);border-color:var(--line2)}"
    if s.count(a) != 1:
        print("❌ CSS anchor"); sys.exit(1)
    s = s.replace(a, a + "\n" + CSS.strip())
    s = s.replace('APP_VERSION = "3.36.46"', 'APP_VERSION = "3.36.47"', 1)
    if '"""' in JS or '"""' in CSS:
        print("❌ triple quotes"); sys.exit(1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · the explanations inside the five deploy forms · compiles · {p}")
