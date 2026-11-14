# 📖 patch 79 (dashboard v3.36.47 · one explanation button per deploy form) — the owner (14-11), on p78's 📖 inside each of the grid's
#   three kind buttons: «بالصورة انت وضعت الزر فوق الزر خليه فوق زر واحد وبداخله ثلاث شروحات والباقي كذلك».
#   · every deploy form gets ONE «📖 شرح …» button right under its title (♾️🎚️➕ the grid · 📉📈 DCA · 🟢🔴 the recurring · 🪜 · 💹)
#   · it opens one window holding that form's explanations: tabs for its bots (the grid 3 · DCA 2 · the recurring 2 · 🪜 and 💹 one, no
#     tabs) — it opens on the kind chosen in the form · «↩️ رجوع إلى النموذج» as before (what was typed stays)
#   · the 📖 inside the grid's kind buttons (p78) and the per-kind rows go
#   · switching tabs leaves one moving example running (an old animation frame never draws into the new one)
#   · the form now HIDES in place while the explanation shows beside it (p78 took it out of the page — DCA's table, still loading,
#     then found no box: a page error) — its updates land in it as usual · «↩️» shows it again where it was scrolled
#   python3 devtests/step/patches/p79_tutorial_one_button.py Holy_Dashboard.pyw
import os, sys


def row(set_, txt):
    return f'''  <div class="tutrow"><button type="button" class="tutone" onclick="tutQ(event,'{set_}')">📖 {txt}</button></div>\n'''


R = [
    # ── the grid form: the three kind buttons back to plain · one 📖 above them ──
    ('''  showModal(`<h2>➕ نشر بوت جرد</h2>
  <div class="gtsel" style="display:flex;gap:6px;margin:4px 0 8px">
    <button type="button" data-gt="grid" onclick="gType('grid')" style="flex:1">♾️ لانهائية <span class="tutq" title="شرح الشبكة اللانهائية — مثال متحرك وأسئلة" onclick="tutQ(event,'grid')">📖</span></button>
    <button type="button" data-gt="grid_range" onclick="gType('grid_range')" style="flex:1">🎚️ مدى <span class="tutq" title="شرح المدى — مثال متحرك وأسئلة" onclick="tutQ(event,'grid_range')">📖</span></button>
    <button type="button" data-gt="grid_plus" onclick="gType('grid_plus')" style="flex:1">➕ بلس <span class="tutq" title="شرح البلس — مثال متحرك وأسئلة" onclick="tutQ(event,'grid_plus')">📖</span></button>''',
     '''  showModal(`<h2>➕ نشر بوت جرد</h2>
''' + row('grid', 'شرح البوتات الثلاثة — ♾️ لانهائية · 🎚️ مدى · ➕ بلس') + '''  <div class="gtsel" style="display:flex;gap:6px;margin:4px 0 8px">
    <button type="button" data-gt="grid" onclick="gType('grid')" style="flex:1">♾️ لانهائية</button>
    <button type="button" data-gt="grid_range" onclick="gType('grid_range')" style="flex:1">🎚️ مدى</button>
    <button type="button" data-gt="grid_plus" onclick="gType('grid_plus')" style="flex:1">➕ بلس</button>'''),
    # ── DCA ──
    ('''  </select></div>
  <div class="tutrow"><span>📖 شرح:</span><button type="button" onclick="tutQ(event,'dca')">📉 البيعي</button><button type="button" onclick="tutQ(event,'dca_buy')">📈 الشرائي</button></div>
''', '''  </select></div>
'''),
    ('''  showModal(`<h2 style="color:var(--amber)">📊 نشر بوت DCA</h2>
''', '''  showModal(`<h2 style="color:var(--amber)">📊 نشر بوت DCA</h2>
''' + row('dca', 'شرح البوتين — 📉 البيعي · 📈 الشرائي')),
    # ── the recurring ──
    ('''  </select></div>
  <div class="tutrow"><span>📖 شرح:</span><button type="button" onclick="tutQ(event,'rec_buy')">🟢 الشرائي</button><button type="button" onclick="tutQ(event,'rec_sell')">🔴 البيعي</button></div>
''', '''  </select></div>
'''),
    ('''  showModal(`<h2 style="color:var(--cyan)">🔁 نشر بوت دوري — الشراء والبيع المتكرر</h2>
''', '''  showModal(`<h2 style="color:var(--cyan)">🔁 نشر بوت دوري — الشراء والبيع المتكرر</h2>
''' + row('rec', 'شرح البوتين — 🟢 الشرائي · 🔴 البيعي')),
    # ── 🪜 · 💹 ──
    ('''  <div class="tutrow"><span>📖 شرح:</span><button type="button" onclick="tutQ(event,'grid_step')">🪜 الشبكي المتدرج</button></div>
''', row('step', 'شرح البوت — 🪜 الشبكي المتدرج')),
    ('''  <div class="tutrow"><span>📖 شرح:</span><button type="button" onclick="tutQ(event,'rec_va')">💹 مسار القيمة</button></div>
''', row('va', 'شرح البوت — 💹 مسار القيمة')),
    # ── the window: tabs for the form's bots ──
    ('''  const ico=(b.ico)||({grid:'♾️',grid_plus:'➕',grid_range:'🎚️',grid_step:'🪜',dca_buy:'📈',dca:'📉',rec_buy:'🔁',rec_sell:'🔂',rec_va:'💹'}[k]||'🤖');''',
     '''  const IC={grid:'♾️',grid_plus:'➕',grid_range:'🎚️',grid_step:'🪜',dca_buy:'📈',dca:'📉',rec_buy:'🔁',rec_sell:'🔂',rec_va:'💹'},ico=(b.ico)||IC[k]||'🤖';'''),
    ('''  if(back&&TUT_STASH)h+='<div class="tutbk"><button class="primary" onclick="tutBack()">↩️ رجوع إلى النموذج</button><small>ما كتبته في النموذج باقٍ كما هو</small></div>';''',
     '''  if(back&&TUT_SET&&TUT_SET.length>1)h+=`<div class="tuttabs">${TUT_SET.map(x=>`<button type="button" class="${x===k?'on':''}" onclick="tutTab('${x}')">${IC[x]||'🤖'} ${TUT[x].t}</button>`).join('')}</div>`;   // 📖 p79: شروح النموذج كلها بنافذة وحدة
  if(back&&TUT_STASH)h+='<div class="tutbk"><button class="primary" onclick="tutBack()">↩️ رجوع إلى النموذج</button><small>ما كتبته في النموذج باقٍ كما هو</small></div>';'''),
    ('''let TUT_STASH=null;
function tutQ(ev,k){if(ev){ev.preventDefault();ev.stopPropagation()}const m=$('#modal');TUT_STASH=(m&&m.querySelector('.hwb'))||null;openTutKind(k,true)}
''',
     '''/* 📖 p79: زر واحد بكل نموذج ⇒ نافذة وحدة بشروح بوتاته (المالك: «خليه فوق زر واحد وبداخله ثلاث شروحات والباقي كذلك») */
const TUT_SETS={grid:['grid','grid_range','grid_plus'],dca:['dca','dca_buy'],rec:['rec_buy','rec_sell'],step:['grid_step'],va:['rec_va']};
const TUT_SEL={grid:'#n_gtype',dca:'#dn_type',rec:'#rd_type'};
let TUT_STASH=null,TUT_SET=null;
function tutQ(ev,set){if(ev){ev.preventDefault();ev.stopPropagation()}const L=TUT_SETS[set]||[set],s=TUT_SEL[set]&&$(TUT_SEL[set]);
  const k0=s&&L.includes(s.value)?s.value:L[0];const m=$('#modal'),f=m&&m.querySelector('.hwb:not(.tuthwb)');
  TUT_STASH=f||null;if(f){f._tutY=f.scrollTop;f.style.display='none'}TUT_SET=L;openTutKind(k0,true)}   // النموذج يختفي بمكانه — تحديثاته (الجدول · الحاسبة) تصله عادي
function tutTab(k){TUT_RUN=null;openTutKind(k,true)}
function tutBack(){const m=$('#modal');if(!m||!TUT_STASH)return;TUT_RUN=null;TUT_SET=null;const w=m.querySelector('.tuthwb');if(w)w.remove();
  const f=TUT_STASH;TUT_STASH=null;f.style.display='';if(!f.isConnected)m.appendChild(f);f.scrollTop=f._tutY||0;try{hwSync()}catch(e){}}
'''),
    # p78 took the form out of the page (an async update — DCA's table — then found no box) ⇒ the old tutBack body goes
    ('''function tutBack(){const m=$('#modal');if(!m||!TUT_STASH)return;TUT_RUN=null;const cur=m.querySelector('.hwb');if(cur)m.replaceChild(TUT_STASH,cur);else m.appendChild(TUT_STASH);TUT_STASH=null;try{hwSync()}catch(e){}}
''', ''),
    # the explanation beside the hidden form (not instead of it)
    ('''  showModal(h);
  if(!window._tutHM&&''', '''  const m=$('#modal');
  if(back&&TUT_STASH&&TUT_STASH.isConnected&&m){let w=m.querySelector('.tuthwb');if(!w){w=document.createElement('div');w.className='hwb tuthwb';m.appendChild(w)}w.innerHTML=h;w.scrollTop=0}
  else showModal(h);
  if(!window._tutHM&&'''),
    # one moving example at a time: an old frame never draws into the new one
    ('''function tutLoop(){const R=TUT_RUN;if(!R)return;R.raf=requestAnimationFrame(ts=>{R.raf=0;const svg=''',
     '''function tutLoop(){const R=TUT_RUN;if(!R)return;R.raf=requestAnimationFrame(ts=>{R.raf=0;if(R!==TUT_RUN)return;const svg='''),
    # CSS
    ('''.tutq{display:inline-block;margin-inline-start:4px;padding:1px 6px;border-radius:8px;border:1px solid var(--line2);background:rgb(var(--vio-rgb)/.12);font-size:12px;cursor:help}
.tutq:hover{background:rgb(var(--vio-rgb)/.25)}''',
     '''.tutrow .tutone{font-size:12.5px;padding:6px 14px;border-color:rgb(var(--vio-rgb)/.55);background:rgb(var(--vio-rgb)/.10)}
.tuttabs{display:flex;flex-wrap:wrap;gap:6px;margin:2px 0 8px}.tuttabs button{font-size:12.5px;padding:6px 12px;border-radius:999px}
.tuttabs button.on{background:rgb(var(--vio-rgb)/.22);border-color:var(--vio);color:var(--tx);font-weight:700}'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    for bad in ('class="tutq"', "tutQ(event,'grid_range')", "tutQ(event,'dca_buy')", "tutQ(event,'rec_sell')"):
        if bad in s:
            print(f"❌ left over: {bad}"); sys.exit(1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · one 📖 per deploy form · tabs in the window · compiles · {p}")
