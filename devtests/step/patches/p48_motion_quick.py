# 🎬 patch 48 (dashboard · the window motions, again) — the owner (13-11, after v3.36.35): «الانميشن فيه بعده مشكلة يقطع وشوي بطئة».
#   ① quicker: every motion ~25 % shorter (zoom 260 → 200 ms · up 320 → 240 · side 300 → 230 · from the button 420 → 300 ·
#      blur 300 → 230 · bounce 440 → 340) · the closing 0.6 of it (was 0.75)
#   ③ the closing starts one frame sooner (only the opening waits two frames — its window must be drawn first)
#   ② a lighter closing copy: the copy that plays the closing kept the WHOLE window (a long report = thousands of elements styled and laid
#      out again in the first frame of the closing) — now everything of it that is off the screen is emptied (its box keeps its size, so
#      what is on the screen stays exactly where it was)
#   python3 devtests/step/patches/p48_motion_quick.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''const HW_MS={up:320,zoom:260,side:300,btn:420,blur:300,spring:440};''',
     '''const HW_MS={up:240,zoom:200,side:230,btn:300,blur:230,spring:340};   // 🎬 v3.36.36: أسرع (كانت 320 · 260 · 300 · 420 · 300 · 440)'''),
    ('''  hideModal();setTimeout(()=>{openSettings();toast('🎬 حركة النوافذ: '+n,true)},v==='none'?0:Math.round((HW_MS[v]||0)*.75)+80)}''',
     '''  hideModal();setTimeout(()=>{openSettings();toast('🎬 حركة النوافذ: '+n,true)},v==='none'?0:Math.round((HW_MS[v]||0)*.6)+80)}'''),
    ('''    const z=getComputedStyle(box).zIndex,c=box.cloneNode(true);''',
     '''    const z=getComputedStyle(box).zIndex,c=box.cloneNode(true);hwLight(box,c);   // 🎬 v3.36.36: اللي برّا الشاشة ينفرغ'''),
    ('''    const p=(panelSel&&c.querySelector(panelSel))||c,kf=hwKF(s,p,small,pt||hwPt()),d=Math.round(HW_MS[s]*.75);''',
     '''    const p=(panelSel&&c.querySelector(panelSel))||c,kf=hwKF(s,p,small,pt||hwPt()),d=Math.round(HW_MS[s]*.6);'''),
    # ③ the closing starts one frame sooner (the copy is drawn as it was · only the opening must wait for its window to be drawn first)
    ('''function hwPlay(a,el,o){                                         // 🎬 v3.36.35: تبدأ من أولها بعد ما تنرسم النافذة مرة (كانت تقفز فوق أولها)''',
     '''function hwPlay(a,el,o,q){                                       // 🎬 v3.36.35: تبدأ من أولها بعد ما تنرسم النافذة مرة (كانت تقفز فوق أولها) · q = الإغلاق: إطار واحد'''),
    ('''  requestAnimationFrame(()=>requestAnimationFrame(play));setTimeout(play,180);''',
     '''  requestAnimationFrame(q?play:()=>requestAnimationFrame(play));setTimeout(play,q?120:180);'''),
    ('''    if(kf)hwPlay(p.animate(kf.slice().reverse(),{duration:d,easing:'cubic-bezier(.4,0,.7,.2)',fill:'both'}),p,null);
    if(p!==c)hwPlay(c.animate([{opacity:1},{opacity:0}],{duration:d,easing:'linear',fill:'both'}),c,null);''',
     '''    if(kf)hwPlay(p.animate(kf.slice().reverse(),{duration:d,easing:'cubic-bezier(.4,0,.7,.2)',fill:'both'}),p,null,1);
    if(p!==c)hwPlay(c.animate([{opacity:1},{opacity:0}],{duration:d,easing:'linear',fill:'both'}),c,null,1);'''),
    ('''function hwIdle(){''',
     '''function hwLight(o,c){                                            // 🎬 v3.36.36: نسخة الإغلاق خفيفة — كل صندوق برّا الشاشة ينفرغ ويبقى بحجمه
  try{const O=o.getElementsByTagName('*'),C=c.getElementsByTagName('*');if(O.length!==C.length||O.length<60)return;
    const H=innerHeight,BL=/^(block|flex|grid|table|list-item|flow-root|table-row|table-row-group)$/;const cut=[];
    for(let i=0;i<O.length;i++){const e=O[i],r=e.getBoundingClientRect();
      if((r.bottom<-40||r.top>H+40)&&r.height>0&&e.children.length){const cs=getComputedStyle(e);
        if(BL.test(cs.display)&&cs.position!=='fixed'){cut.push([C[i],r.height]);i+=e.getElementsByTagName('*').length}}}
    for(const [n,h] of cut){n.replaceChildren();Object.assign(n.style,{height:h+'px',minHeight:h+'px',maxHeight:h+'px',boxSizing:'border-box',overflow:'hidden'})}
  }catch(e){}}
function hwIdle(){'''),
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
