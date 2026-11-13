# 🎬 patch 43 (dashboard · the window motions) — the owner (13-11): «بعض الانميشن يقطع افحصهم كلهم».
#   Measured on a phone screen with the CPU slowed ×4 (devtests/ui_smooth.py): opening ⚙️ costs ~110–136 ms of building before the first
#   frame ⇒ the motion was already running and its first part was skipped (it «jumped») · «تلاشٍ مع ضبابية» the worst (6 frames > 34 ms),
#   then the bounce and the side slide · the scrim's colour was animated on the main thread · the background kept its blur behind a window
#   that covers the whole phone screen.
#   ① every motion (open and close) waits, at its first pose, until the window has been drawn once — then plays whole, from its start
#   ② «تتوسّع من الزر»: a scale from the tapped point (the compositor moves it) instead of a growing clip (repainted every frame)
#   ③ «تلاشٍ مع ضبابية»: a lighter blur (6 px, was 14) · the closing copy carries no background blur
#   ④ no colour animation of the scrim (it simply appears; the window moves)
#   ⑤ a phone (≤ 720 px): no background blur behind a full window, a page or the trial window (nothing of it is visible)
#   ⑥ the background's ambient motion also pauses behind the trial window (it already did behind the other windows)
#   ⑦ the refresh from the server (every 3 s) redraws the cards after a running motion, not in its middle (it landed there now and then:
#      ~90 ms of drawing at ×4 = a visible hitch) — it waits at most the rest of the motion (≤ 0.7 s); the dashboard is behind the window anyway
#   python3 devtests/step/patches/p43_smooth.py Holy_Dashboard.pyw
import os, sys

R = [
    # ②③ the keyframes
    ('''  if(s==='blur')return [{opacity:0,filter:'blur(14px)',transform:'scale(1.04)'},{opacity:1,filter:'blur(0px)',transform:'none'}];''',
     '''  if(s==='blur')return [{opacity:0,filter:'blur(6px)',transform:'scale(1.03)'},{opacity:1,filter:'blur(0px)',transform:'none'}];   // 🎬 v3.36.35: أخف (كان 14px)'''),
    ('''  if(s==='btn'){const r=el.getBoundingClientRect(),p=pt||{x:innerWidth/2,y:innerHeight/2},cx=Math.round(p.x-r.left),cy=Math.round(p.y-r.top),
    R=Math.ceil(Math.hypot(Math.max(Math.abs(cx),Math.abs(r.width-cx)),Math.max(Math.abs(cy),Math.abs(r.height-cy))))+2;
    return [{clipPath:`circle(0px at ${cx}px ${cy}px)`},{clipPath:`circle(${R}px at ${cx}px ${cy}px)`}]}''',
     '''  if(s==='btn'){const r=el.getBoundingClientRect(),p=pt||{x:innerWidth/2,y:innerHeight/2};   // 🎬 v3.36.35: تكبير من نقطة الضغط (يحرّكه كرت الشاشة) بدل قصّ يُعاد رسمه كل إطار
    const kf=[{opacity:0,transform:'scale(.06)'},{opacity:1,offset:.3},{opacity:1,transform:'none'}];kf.o=Math.round(p.x-r.left)+'px '+Math.round(p.y-r.top)+'px';return kf}'''),
    # ①④ open: wait for the first drawn frame · no scrim colour animation
    ('''function hwIn(panel,scrim,small,pt){const s=hwStyle();if(s==='none'||!panel||!panel.animate)return;
  try{const kf=hwKF(s,panel,small,pt||hwPt());if(!kf)return;
    panel.animate(kf,{duration:HW_MS[s],easing:s==='spring'?'cubic-bezier(.34,1.56,.64,1)':'cubic-bezier(.2,.8,.2,1)'});
    if(scrim&&scrim!==panel){const bc=getComputedStyle(scrim).backgroundColor;
      scrim.animate([{backgroundColor:'rgba(0,0,0,0)'},{backgroundColor:bc}],{duration:Math.round(HW_MS[s]*.8),easing:'linear'})}}catch(e){}}''',
     '''function hwPlay(a,el,o){                                         // 🎬 v3.36.35: تبدأ من أولها بعد ما تنرسم النافذة مرة (كانت تقفز فوق أولها)
  a.pause();let go=0;const play=()=>{if(go)return;go=1;try{a.play()}catch(e){}};
  try{HW.busy=Math.max(HW.busy||0,performance.now()+(+a.effect.getTiming().duration||0)+200)}catch(e){}
  requestAnimationFrame(()=>requestAnimationFrame(play));setTimeout(play,180);
  if(o!=null){const back=()=>{try{el.style.transformOrigin=o}catch(e){}};a.addEventListener('finish',back);a.addEventListener('cancel',back)}}
function hwIn(panel,scrim,small,pt){const s=hwStyle();if(s==='none'||!panel||!panel.animate)return;
  try{const kf=hwKF(s,panel,small,pt||hwPt());if(!kf)return;let o=null;
    if(kf.o){o=panel.style.transformOrigin;panel.style.transformOrigin=kf.o}
    const a=panel.animate(kf,{duration:HW_MS[s],easing:s==='spring'?'cubic-bezier(.34,1.56,.64,1)':'cubic-bezier(.2,.8,.2,1)',fill:'backwards'});
    hwPlay(a,panel,o)}catch(e){}}
function hwIdle(){const w=(HW.busy||0)-performance.now();return w>0?new Promise(r=>setTimeout(r,Math.min(w,700))):null}   // 🎬 v3.36.35: حركة شغّالة ⇒ انتظر نهايتها'''),
    # ⑦ the refresh from the server (every 3 s) draws the cards after a running motion, not in its middle
    ('''  try{const d=await api('/api/overview',0,1);DATA=d;$('#pulse').classList.remove('off');pulseBeat();''',
     '''  try{const d=await api('/api/overview',0,1);const hw=hwIdle();if(hw)await hw;DATA=d;$('#pulse').classList.remove('off');pulseBeat();   // 🎬 v3.36.35'''),
    # ① close: the copy also waits for its first frame · ③ without the background blur
    ('''    const p=(panelSel&&c.querySelector(panelSel))||c,kf=hwKF(s,p,small,pt||hwPt()),d=Math.round(HW_MS[s]*.75);
    if(kf)p.animate(kf.slice().reverse(),{duration:d,easing:'cubic-bezier(.4,0,.7,.2)',fill:'forwards'});
    if(p!==c)c.animate([{opacity:1},{opacity:0}],{duration:d,easing:'linear',fill:'forwards'});
    setTimeout(()=>{try{c.remove()}catch(e){}},d+80)}catch(e){}}''',
     '''    c.style.backdropFilter='none';c.style.webkitBackdropFilter='none';                    // 🎬 v3.36.35: النسخة بلا ضبابية خلفية (ثقيلة كل إطار)
    const p=(panelSel&&c.querySelector(panelSel))||c,kf=hwKF(s,p,small,pt||hwPt()),d=Math.round(HW_MS[s]*.75);
    if(kf&&kf.o)p.style.transformOrigin=kf.o;
    if(kf)hwPlay(p.animate(kf.slice().reverse(),{duration:d,easing:'cubic-bezier(.4,0,.7,.2)',fill:'both'}),p,null);
    if(p!==c)hwPlay(c.animate([{opacity:1},{opacity:0}],{duration:d,easing:'linear',fill:'both'}),c,null);
    setTimeout(()=>{try{c.remove()}catch(e){}},d+260)}catch(e){}}'''),
    # ⑥ the background pauses behind every layer (the trial window too)
    ('''function hwSync(){for(const x of hwLayers()){const i=HW.st.findIndex(s=>s.k===x.k);if(x.on&&i<0)hwPush(x);else if(!x.on&&i>=0)hwPop(x.k)}}''',
     '''function hwSync(){for(const x of hwLayers()){const i=HW.st.findIndex(s=>s.k===x.k);if(x.on&&i<0)hwPush(x);else if(!x.on&&i>=0)hwPop(x.k)}
  try{coverSync()}catch(e){}}'''),
    ('''function coverSync(){const m=$('#mbg'),c=!!document.querySelector('.page.on,#drawer.on,#notifPanel.on')||!!(m&&!m.hidden);''',
     '''function coverSync(){const m=$('#mbg'),c=!!document.querySelector('.page.on,#drawer.on,#notifPanel.on,#btov')||!!(m&&!m.hidden);   // 🎬 v3.36.35: + الاختبار التجريبي'''),
    # ⑤ the phone: no background blur behind what covers the whole screen
    ('''  #drawer,#notifPanel{inset:0;border-radius:0;border:0}
}''', '''  #drawer,#notifPanel{inset:0;border-radius:0;border:0}
  .mbg.full,.btov,.page{backdrop-filter:none;-webkit-backdrop-filter:none}   /* 🎬 v3.36.35: الشاشة كلها مغطّاة ⇒ الضبابية خلفها شغل بلا فائدة كل إطار */
}'''),
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
