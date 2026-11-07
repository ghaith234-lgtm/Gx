# 🪜🎨 patch 24 (dashboard · the 🪜 card's price ruler) — the owner (7-11): «افحص هل هناك خلل في رسم الكرت اقصد الخطوط اريد الخطوط
#   تتداخل». Two drawing defects, found by rendering his two settings on the real dashboard (3 parts 0.45/0.15 · 20 parts 0.3/1 · G 0.6):
#   ① a level's buy price was drawn only while that level had a buy order on the exchange — a level whose parts all bought (they
#      hold coins and sell above) had no line at all ⇒ the overlap was invisible: his 2nd sell of every level sits exactly on the
#      buy price of the level above, the 3rd above it — and that buy price was not on the card. Now every level whose buy price is
#      inside the card's range gets a dotted line in its colour at that price with its price, drawn under the orders, tap ⇒ the
#      level's details and why it has no buy order (key `r:j` — the buy lines with a published buy stay `b:j`).
#   ② the 12 colours had near twins (levels 2 / −2 ΔE2000 5.1 · 1 / −3 7.6 · 3 / −4 10.1): a sell of level 2 looked like level −2's.
#      Now 12 colours picked to be apart (ΔE2000 ≥ 15.9 on the dark themes, levels next to each other ≥ 30), and a darker set for the
#      light theme (the old ones were pale on white) — still no red (red = loss) and none near the price line's cyan.
#   Display only: nothing in the engine, the books or the orders changes.
#   python3 devtests/step/patches/p24_step_lines.py Holy_Dashboard.pyw
import os, sys

R = [
    # ② the colours
    ('''const ST_PAL=['#38bdf8','#c084fc','#fbbf24','#34d399','#f472b6','#60a5fa','#a3e635','#fb923c','#2dd4bf','#e879f9','#facc15','#818cf8'];   // (بلا أحمر: الأحمر خسارة)
function stCol(j){const n=ST_PAL.length;return ST_PAL[((+j%n)+n)%n]}''',
     '''/* 🪜🎨 v3.36.22: 12 لون متباعدة (المستويات المتجاورة أبعد شي) · بلا أحمر (الأحمر خسارة) ولا قريب من سماوي خط السعر · مجموعة أغمق للثيم الفاتح */
const ST_PAL=['#d97706','#0891b2','#d8b4fe','#5eead4','#fdba74','#818cf8','#22c55e','#facc15','#93c5fd','#059669','#a3e635','#d946ef'],
  ST_PAL_L=['#65a30d','#115e59','#86198f','#6366f1','#d97706','#166534','#0284c7','#6d28d9','#059669','#854d0e','#a855f7','#1e40af'];
function stCol(j){const P=document.documentElement.dataset.theme==='light'?ST_PAL_L:ST_PAL,n=P.length;return P[((+j%n)+n)%n]}'''),
    # ① the buy price of every level inside the range
    ('''  const used=[Y(cp)],free=y=>!used.some(u=>Math.abs(u-y)<12);     // (the price badge's place is kept free)
  B.forEach(gr=>{const y=Y(gr.p),c=stCol(gr.j),lab=free(y);if(lab)used.push(y);
    g+=`<g class="stl" data-stl="b:${gr.j}"><rect x="0" y="${y-8}" width="${W}" height="16" fill="transparent"/>`+''',
     '''  const used=[Y(cp)],free=y=>!used.some(u=>Math.abs(u-y)<12);     // (the price badge's place is kept free)
  /* 🪜🎨 v3.36.22: سعر شراء كل مستوى داخل المدى — حتى لو ما عنده أمر شراء الآن (اشترى وبيعاته فوقه / ينتظر بالذاكرة) ⇒ يبين التداخل:
     بيعات المستوى تطلع فوق أسعار شراء المستويات اللي فوقه · خط منقّط بلونه تحت الأوامر */
  const rl={};SL.forEach(x=>{if(!(lv[x[0]]&&lv[x[0]].pub)&&!rl[x[0]])rl[x[0]]={j:x[0],p:+x[6]}});
  (b.sl_far||[]).forEach(f=>{if(!rl[f[0]]&&!(lv[f[0]]&&lv[f[0]].pub))rl[f[0]]={j:f[0],p:+f[1]}});
  const RF=Object.values(rl).filter(e=>e.p>=lo&&e.p<=hi).sort((a,z)=>z.p-a.p);
  let gB='',gR='';
  B.forEach(gr=>{const y=Y(gr.p),c=stCol(gr.j),lab=free(y);if(lab)used.push(y);
    gB+=`<g class="stl" data-stl="b:${gr.j}"><rect x="0" y="${y-8}" width="${W}" height="16" fill="transparent"/>`+'''),
    ('''        skAR(xr-4,y-5,`🛒 ${gr.pub}${gr.mem?` · ${gr.mem} بالذاكرة`:''}`,'r',10.5,c):'')+`</g>`});
  S.forEach(x=>{const y=Y(+x[3]),c=stCol(x[0]),lab=free(y);if(lab)used.push(y);''',
     '''        skAR(xr-4,y-5,`🛒 ${gr.pub}${gr.mem?` · ${gr.mem} بالذاكرة`:''}`,'r',10.5,c):'')+`</g>`});
  RF.forEach(e=>{const y=Y(e.p),c=stCol(e.j),lab=free(y);if(lab)used.push(y);
    gR+=`<g class="stl" data-stl="r:${e.j}"><rect x="0" y="${y-5}" width="${W}" height="10" fill="transparent"/>`+
      `<line x1="${xl}" y1="${y}" x2="${xr}" y2="${y}" stroke="${c}" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="1.5 4" opacity=".9"/>`+
      (lab?`<text x="${W-3}" y="${y+4}" text-anchor="end" font-size="10.5" fill="${c}" direction="ltr">${f4(e.p)}</text>`:'')+`</g>`});
  g+=gR+gB;
  S.forEach(x=>{const y=Y(+x[3]),c=stCol(x[0]),lab=free(y);if(lab)used.push(y);'''),
    ('''  if(!o.mini)g+=skAR(W-4,H-3,'اللون = الشراء وبيعاته الخاصة · اضغط أي خط · 🪜 السلم = كل المستويات والذاكرة','r',9.5,'var(--mut2)');''',
     '''  if(!o.mini)g+=skAR(W-4,H-3,'اللون = الشراء وبيعاته الخاصة · المنقّط = سعر شراء بلا أمر الآن · اضغط أي خط','r',9.5,'var(--mut2)');'''),
    # tap a dotted line ⇒ the level's details (like a buy line) · one line says why there is no buy order
    ('''  if(P[0]==='b'){const j=+P[1],L=SL.filter(x=>x[0]===j).sort((a,z)=>a[1]-z[1]),pb=L.find(x=>x[2]==='b'&&x[5]!=='M'),bp=pb?+pb[3]:(L.length?+L[0][6]:0);
    h=`<b style="color:${stCol(j)}">🛒 المستوى ${j} — شراء ثابت ${f4(bp)}</b><div class="stpd">البعد عن السعر ${d(bp)} · بيعاته الخاصة ${L.map(up).join(' · ')} فوقه</div>`+L.map(x=>''',
     '''  if(P[0]==='b'||P[0]==='r'){const j=+P[1],L=SL.filter(x=>x[0]===j).sort((a,z)=>a[1]-z[1]),pb=L.find(x=>x[2]==='b'&&x[5]!=='M'),bp=pb?+pb[3]:(L.length?+L[0][6]:0);
    const nsl=L.filter(x=>x[2]==='s').length;
    h=`<b style="color:${stCol(j)}">🛒 المستوى ${j} — شراء ثابت ${f4(bp)}</b><div class="stpd">البعد عن السعر ${d(bp)} · بيعاته الخاصة ${L.map(up).join(' · ')} فوقه</div>`+
      (pb?'':`<div class="stpd">لا يوجد له أمر شراء منشور الآن — الخط المنقّط هو سعر شرائه${nsl?` · اشترى ${nsl} جزء وبيعاتها فوقه`:''}</div>`)+L.map(x=>'''),
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
