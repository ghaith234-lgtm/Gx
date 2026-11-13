# 🌌 patch 52 (dashboard · animated backgrounds) — the owner (13-11): «اريد اتضيف خلفية متحركه (البنفسجية) … وتضاف مع المظهر … اريدها مثل
#   خلفية الps4» ⇒ the examples page (https://claude.ai/artifact/Jk3VkzUHKRg3puucNnd4o8) ⇒ «خلي الخلفيات والنغمات كلهن · الالوان على حدى
#   والخلفيات على حدى حتى الخلفيات متحركه تتلون وخلي اختيار الاصلي مافيه انميشن يعني الوضع الاعتيادي , وبالمستقبل انضيف بعد».
#   ① ⚙️ 🖌️: «🎨 الألوان» (the themes, was «المظهر») and «🌌 الخلفية» apart — الأصلية (the background as it was) + أمواج · غبار نجمي ·
#      شفق · أشعة · كوكبة · حرير — each drawn in the colours of the chosen theme (a live little preview on every choice)
#   ② one drawing surface behind everything (#hbg) · 30 frames a second at most · below the screen's resolution · it stops behind every
#      window and page, while scrolling, with the screen off · «⚡ الوضع الخفيف» / the phone's «reduce motion» ⇒ one still frame
#   ③ with a moving background the top bar keeps no blur (it would be blurred again every frame) and the orbs of «الأصلية» rest
#   ④ a new background later = one line in HBG + its painter in HBG_MAKE (it is given the theme's colours)
#   python3 devtests/step/patches/p52_backgrounds.py Holy_Dashboard.pyw
import os, sys

JS = r'''/* 🌌 v3.36.37 (المالك 13-11): خلفيات متحركة — «الأصلية» (كما كانت) + ست تتلوّن بألوان «🎨 الألوان» المختارة · لهذا الجهاز ·
   لوحة رسم واحدة خلف كل شي (#hbg) · 30 إطاراً بالثانية أقصى شي · بدقة أقل من الشاشة · تتوقف خلف النوافذ والصفحات ووقت التمرير والشاشة مطفية ·
   الوضع الخفيف / تقليل الحركة ⇒ إطار ثابت · خلفية جديدة = سطر بـHBG + رسّامها بـHBG_MAKE (ياخذ ألوان المظهر) */
const HBG=[['orig','الأصلية','كما كانت — بلا حركة جديدة'],['waves','أمواج','خيوط ضوء تتموّج ببطء — أقرب شيء لخلفية PS4'],
  ['dust','غبار نجمي','ذرّات ضوء تصعد ببطء وتلمع'],['aurora','شفق','غيوم ضوء كبيرة تسبح وتمتزج'],['beams','أشعة','حزم ضوء مائلة تمرّ ببطء'],
  ['stars','كوكبة','نقاط ضوء تتصل بخيوط حين تقترب'],['silk','حرير','شريطان عريضان من الضوء يلتفّان ببطء']];
const HB={c:null,x:null,k:'orig',draw:null,raf:0,last:0,col:null,rt:0,spr:{}};
function uiBg(){const v=_ls('dash_bg');return HBG.some(x=>x[0]===v)?v:'orig'}
function setBg(v){if(!HBG.some(x=>x[0]===v))v='orig';_ls('dash_bg',v==='orig'?null:v);hbgApply();openSettings();
  toast('🌌 الخلفية: '+HBG.find(x=>x[0]===v)[1],true)}
function hbStill(){try{return uiLite()||!!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)}catch(e){return false}}
function hbRgb(v){v=String(v||'').trim();if(v[0]==='#'){let h=v.slice(1);if(h.length===3)h=h.split('').map(c=>c+c).join('');const n=parseInt(h.slice(0,6),16);
  return [(n>>16)&255,(n>>8)&255,n&255].join(',')}const m=v.match(/[\d.]+/g);return m&&m.length>=3?m.slice(0,3).map(x=>Math.round(+x)).join(','):'167,139,250'}
function hbCol(){const cs=getComputedStyle(document.documentElement),g=n=>cs.getPropertyValue(n).trim();const bg0=g('--bg0')||'#070210';
  const [r,gg,b]=hbRgb(bg0).split(',').map(Number),light=(.2126*r+.7152*gg+.0722*b)/255>.5;
  return{bg0,bg1:g('--bg1')||bg0,A:g('--bgA')||bg0,B:g('--bgB')||bg0,o1:hbRgb(g('--orb1')||'#7c3aed'),o2:hbRgb(g('--orb2')||'#0891b2'),
    o3:hbRgb(g('--orb3')||'#db2777'),v:hbRgb(g('--vio-rgb')||'167 139 250'),light,K:light?'source-over':'lighter',am:light?.55:1}}
function hbSpr(col,size){const k=col+'|'+size;if(HB.spr[k])return HB.spr[k];const s=document.createElement('canvas');s.width=s.height=size;const c=s.getContext('2d');
  const g=c.createRadialGradient(size/2,size/2,0,size/2,size/2,size/2);g.addColorStop(0,`rgba(${col},1)`);g.addColorStop(.35,`rgba(${col},.45)`);g.addColorStop(1,`rgba(${col},0)`);
  c.fillStyle=g;c.fillRect(0,0,size,size);return HB.spr[k]=s}
function hbBase(c,w,h,C){const g=c.createLinearGradient(0,0,w*.3,h);g.addColorStop(0,C.A);g.addColorStop(.55,C.bg1);g.addColorStop(1,C.bg0);c.fillStyle=g;c.fillRect(0,0,w,h);
  const r=c.createRadialGradient(w*.85,0,0,w*.85,0,Math.max(w,h)*.75);r.addColorStop(0,`rgba(${C.o1},${C.light?.12:.26})`);r.addColorStop(1,`rgba(${C.o1},0)`);c.fillStyle=r;c.fillRect(0,0,w,h)}
const HRND=(a,b)=>a+Math.random()*(b-a),HTAU=Math.PI*2;
const HBG_MAKE={
  orig(c,w,h,C){return()=>{hbBase(c,w,h,C);c.globalAlpha=.32*C.am;const m=Math.max(w,h);
    c.drawImage(hbSpr(C.o1,128),-m*.25,-m*.25,m*.8,m*.8);c.drawImage(hbSpr(C.o2,128),w-m*.5,h-m*.5,m*.75,m*.75);c.globalAlpha=1}},
  waves(c,w,h,C){const R=[{y:.6,a:.1,f:1.25,s:.11,col:C.v,n:18},{y:.67,a:.07,f:1.9,s:-.08,col:C.o1,n:14},{y:.52,a:.05,f:2.6,s:.06,col:C.o2,n:10}];
    return t=>{hbBase(c,w,h,C);c.globalCompositeOperation=C.K;c.lineWidth=Math.max(1,w/900);
      for(const r of R)for(let i=0;i<r.n;i++){const k=i/(r.n-1);c.beginPath();
        for(let j=0;j<=56;j++){const u=j/56,x=u*w,y=h*(r.y+r.a*Math.sin(u*Math.PI*r.f+t*r.s+k*.85)+.028*Math.sin(u*Math.PI*4.3-t*r.s*1.6+k*2.2)+(k-.5)*.06);j?c.lineTo(x,y):c.moveTo(x,y)}
        c.strokeStyle=`rgba(${r.col},${((.05+.13*Math.sin(k*Math.PI))*C.am).toFixed(3)})`;c.stroke()}
      c.globalCompositeOperation='source-over'}},
  dust(c,w,h,C){const n=Math.max(24,Math.round(Math.min(90,w*h/9000))),P=[];
    for(let i=0;i<n;i++)P.push({x:Math.random(),y:Math.random(),r:HRND(.6,2.2),v:HRND(.006,.022),ph:HRND(0,HTAU),sw:HRND(.004,.016),c:Math.random()<.75?C.v:C.o2});
    return t=>{hbBase(c,w,h,C);c.globalCompositeOperation=C.K;const sc=Math.max(1,w/500);
      for(const p of P){const y=((p.y-t*p.v)%1+1)%1,x=p.x+Math.sin(t*.4+p.ph)*p.sw,tw=.45+.55*Math.sin(t*1.3+p.ph*3),d=p.r*7*sc;
        c.globalAlpha=Math.max(0,tw)*.8*C.am;c.drawImage(hbSpr(p.c,32),x*w-d/2,y*h-d/2,d,d)}
      c.globalAlpha=1;c.globalCompositeOperation='source-over'}},
  aurora(c,w,h,C){const B=[{c:C.o1,r:.75,ax:.32,ay:.22,fx:.05,fy:.07,ox:.3,oy:.3},{c:C.v,r:.55,ax:.28,ay:.2,fx:.07,fy:.045,ox:.7,oy:.55},
      {c:C.o2,r:.45,ax:.3,ay:.18,fx:.04,fy:.06,ox:.55,oy:.85},{c:C.o3,r:.4,ax:.25,ay:.25,fx:.06,fy:.05,ox:.15,oy:.75}];
    return t=>{hbBase(c,w,h,C);c.globalCompositeOperation=C.K;const m=Math.max(w,h);
      for(const b of B){const x=(b.ox+b.ax*Math.sin(t*b.fx*HTAU*.25))*w,y=(b.oy+b.ay*Math.cos(t*b.fy*HTAU*.25))*h,d=b.r*m*1.45;c.globalAlpha=.26*C.am;c.drawImage(hbSpr(b.c,128),x-d/2,y-d/2,d,d)}
      c.globalAlpha=1;c.globalCompositeOperation='source-over'}},
  beams(c,w,h,C){const L=[0,1,2,3,4].map(i=>({p:i/5,s:HRND(.012,.024),wd:HRND(.06,.14),a:HRND(.05,.11)})),O=[...Array(12)].map(()=>({x:Math.random(),y:Math.random(),r:HRND(.03,.09),v:HRND(.004,.01),ph:HRND(0,HTAU)}));
    return t=>{hbBase(c,w,h,C);c.globalCompositeOperation=C.K;const m=Math.max(w,h);c.save();c.translate(w/2,h/2);c.rotate(-.5);
      for(const l of L){const x=(((l.p+t*l.s)%1)-.5)*m*2.2,bw=l.wd*m,g=c.createLinearGradient(x-bw,0,x+bw,0);
        g.addColorStop(0,`rgba(${C.v},0)`);g.addColorStop(.5,`rgba(${C.v},${(l.a*C.am).toFixed(3)})`);g.addColorStop(1,`rgba(${C.v},0)`);c.fillStyle=g;c.fillRect(x-bw,-m,bw*2,m*2)}
      c.restore();for(const o of O){const y=((o.y-t*o.v)%1+1)%1,d=o.r*m;c.globalAlpha=(.16+.08*Math.sin(t*.7+o.ph))*C.am;c.drawImage(hbSpr(C.o1,64),o.x*w-d/2,y*h-d/2,d,d)}
      c.globalAlpha=1;c.globalCompositeOperation='source-over'}},
  stars(c,w,h,C){const sc=Math.max(1,w/600),n=Math.max(16,Math.round(Math.min(60,w*h/(12000*sc*sc)))),P=[...Array(n)].map(()=>({x:Math.random()*w,y:Math.random()*h,vx:HRND(-6,6)*sc,vy:HRND(-6,6)*sc,ph:HRND(0,HTAU)}));
    let lt=null;const D=Math.min(150*sc,Math.max(w,h)*.2);
    return t=>{const dt=lt==null?0:Math.min(.1,t-lt);lt=t;hbBase(c,w,h,C);
      for(const p of P){p.x+=p.vx*dt;p.y+=p.vy*dt;if(p.x<0)p.x+=w;if(p.x>w)p.x-=w;if(p.y<0)p.y+=h;if(p.y>h)p.y-=h}
      c.lineWidth=Math.max(1,sc*.8);
      for(let i=0;i<P.length;i++)for(let j=i+1;j<P.length;j++){const a=P[i],b=P[j],dx=a.x-b.x,dy=a.y-b.y,d2=dx*dx+dy*dy;
        if(d2<D*D){c.strokeStyle=`rgba(${C.v},${(.22*(1-Math.sqrt(d2)/D)*C.am).toFixed(3)})`;c.beginPath();c.moveTo(a.x,a.y);c.lineTo(b.x,b.y);c.stroke()}}
      c.globalCompositeOperation=C.K;for(const p of P){const s=(8+3*Math.sin(t*1.5+p.ph))*sc;c.globalAlpha=.85*C.am;c.drawImage(hbSpr(C.v,32),p.x-s,p.y-s,s*2,s*2)}
      c.globalAlpha=1;c.globalCompositeOperation='source-over'}},
  silk(c,w,h,C){return t=>{hbBase(c,w,h,C);c.globalCompositeOperation=C.K;
    for(const [k,col,amp,sp] of [[0,C.v,.13,.07],[1,C.o2,.09,-.05]]){const yb=h*(.58+k*.12);c.beginPath();
      for(let j=0;j<=40;j++){const u=j/40,x=u*w,y=yb+h*amp*Math.sin(u*Math.PI*1.4+t*sp+k*1.7);j?c.lineTo(x,y):c.moveTo(x,y)}
      for(let j=40;j>=0;j--){const u=j/40,x=u*w,y=yb+h*.07+h*amp*.85*Math.sin(u*Math.PI*1.4+t*sp*1.15+k*1.7+.5);c.lineTo(x,y)}
      c.closePath();const g=c.createLinearGradient(0,yb-h*.2,0,yb+h*.25);g.addColorStop(0,`rgba(${col},0)`);g.addColorStop(.5,`rgba(${col},${(.18*C.am).toFixed(3)})`);g.addColorStop(1,`rgba(${col},0)`);c.fillStyle=g;c.fill()}
    c.globalCompositeOperation='source-over'}},
};
function hbLoop(now){HB.raf=0;if(HB.k==='orig'||!HB.draw)return;const r=document.documentElement;
  if(!(document.hidden||r.classList.contains('covered')||r.classList.contains('scrolling'))&&now-HB.last>=32){HB.last=now;try{HB.draw(now/1000)}catch(e){}}
  HB.raf=requestAnimationFrame(hbLoop)}
function hbgApply(){const k=uiBg(),r=document.documentElement;HB.k=k;r.classList.toggle('abg',k!=='orig');
  if(HB.raf){cancelAnimationFrame(HB.raf);HB.raf=0}HB.spr={};if(k==='orig'){HB.draw=null;return}
  if(!HB.c){HB.c=document.getElementById('hbg');if(!HB.c)return;HB.x=HB.c.getContext('2d');
    addEventListener('resize',()=>{clearTimeout(HB.rt);HB.rt=setTimeout(()=>{if(HB.k!=='orig')hbgApply()},250)})}
  const d=Math.min(window.devicePixelRatio||1,1.5);HB.c.width=Math.max(1,Math.round(innerWidth*d));HB.c.height=Math.max(1,Math.round(innerHeight*d));
  HB.col=hbCol();HB.draw=HBG_MAKE[k](HB.x,HB.c.width,HB.c.height,HB.col);try{HB.draw(12.3)}catch(e){}
  if(!hbStill())HB.raf=requestAnimationFrame(hbLoop)}
function hbPrev(){const C=hbCol();document.querySelectorAll('#bgRow canvas[data-bg]').forEach(cv=>{try{const c=cv.getContext('2d');HBG_MAKE[cv.dataset.bg](c,cv.width,cv.height,C)(12.3)}catch(e){}})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',hbgApply);else setTimeout(hbgApply,0);
'''

CSS = '''.sfoot{color:var(--mut2);font-size:11px;margin:14px 6px 0;line-height:1.7}
/* ═══ 🌌 v3.36.37: الخلفية المتحركة — لوحة رسم واحدة خلف كل شي · «الأصلية» = الأجرام كما كانت ═══ */
#hbg{position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;display:none}
html.abg #hbg{display:block}
html.abg .orb{display:none}
html.abg body{background-image:none}
html.abg header{backdrop-filter:none;-webkit-backdrop-filter:none;background:rgb(var(--surf2-rgb)/.94)}
.bgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(98px,1fr));gap:8px}
.bgb{display:flex;flex-direction:column;align-items:center;gap:6px;padding:7px 6px 8px;border-radius:12px;font-size:11.5px;min-width:0}
.bgb canvas{width:100%;max-width:132px;aspect-ratio:5/3;height:auto;border-radius:8px;display:block;background:var(--bg0)}
'''

R = [
    ('''<div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>''',
     '''<div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div><canvas id="hbg" aria-hidden="true"></canvas>'''),
    ('''.sfoot{color:var(--mut2);font-size:11px;margin:14px 6px 0;line-height:1.7}
''', CSS),
    ('''function uiTheme(){const t=_ls('dash_theme');return THEMES.some(x=>x[0]===t)?t:'holy'}''',
     JS + '''function uiTheme(){const t=_ls('dash_theme');return THEMES.some(x=>x[0]===t)?t:'holy'}'''),
    # the theme also recolours the moving background
    ('''  if(typeof PV!=='undefined'&&PV){try{pcBars(PV);pcDonut(PV)}catch(e){}}}''',
     '''  if(typeof PV!=='undefined'&&PV){try{pcBars(PV);pcDonut(PV)}catch(e){}}
  try{if(typeof HB!=='undefined'&&HB.k!=='orig')hbgApply()}catch(e){}}   // 🌌 v3.36.37: الخلفية تاخذ الألوان الجديدة'''),
    # the light mode stops / restarts it
    ('''function uiLiteToggle(){const on=!uiLite();_ls('dash_lite',on?'on':null);document.documentElement.classList.toggle('lite',on);tapesKick();''',
     '''function uiLiteToggle(){const on=!uiLite();_ls('dash_lite',on?'on':null);document.documentElement.classList.toggle('lite',on);tapesKick();try{hbgApply()}catch(e){}'''),
    # ⚙️ 🖌️: «الألوان» + «الخلفية»
    ('''      X('theme','🎨','المظهر',`<i class="sdot" style="background:${thT[3]}"></i>${thT[1]}`,`<div class="thgrid">${TB}</div>`)''',
     '''      X('theme','🎨','الألوان',`<i class="sdot" style="background:${thT[3]}"></i>${thT[1]}`,`<div class="thgrid">${TB}</div>`)
     +X('bg','🌌','الخلفية',(HBG.find(x=>x[0]===uiBg())||HBG[0])[1]+(uiBg()!=='orig'&&hbStill()?' · متوقفة':''),
        `<div class="snote">تتلوّن بـ«🎨 الألوان» المختارة · تتوقف وحدها خلف النوافذ وفي «⚡ الوضع الخفيف» · «الأصلية» كما كانت.</div><div class="bgrid" id="bgRow">${HBG.map(x=>
        `<button class="bgb ${uiBg()===x[0]?'on':''}" data-bg="${x[0]}" title="${x[2]}" onclick="setBg('${x[0]}')"><canvas data-bg="${x[0]}" width="132" height="80"></canvas><span>${x[1]}${uiBg()===x[0]?' ✓':''}</span></button>`).join('')}</div>`)'''),
    # the little previews are drawn when the row is open
    ('''  if(on&&k==='fps')try{gpuFill()}catch(e){}}''',
     '''  if(on&&k==='fps')try{gpuFill()}catch(e){}
  if(on&&k==='bg')try{hbPrev()}catch(e){}}'''),
    ('''  clearTimeout(STT);STT=setTimeout(()=>{try{tick()}catch(e){}try{gpuFill()}catch(e){}},(HW_MS[hwStyle()]||0)+120);''',
     '''  if(STO.has('bg'))try{hbPrev()}catch(e){}                           // 🌌 v3.36.37
  clearTimeout(STT);STT=setTimeout(()=>{try{tick()}catch(e){}try{gpuFill()}catch(e){}},(HW_MS[hwStyle()]||0)+120);'''),
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
