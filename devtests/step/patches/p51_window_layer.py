# 🎬 patch 51 (dashboard · the window motions on a fast phone) — the owner (13-11): «موبايلي سريع لكن من افتح نافذة فيها ستتر».
#   A window that starts moving becomes its own layer on the graphics chip — made and drawn (the whole screen, at the phone's full
#   resolution) in the very first frame of the motion ⇒ a hitch at the start even on a fast phone.
#   Now the window is marked «will move» (will-change) the moment it opens, so its layer is made and drawn during the frames the motion
#   already waits (until the window is drawn once) · the mark is removed when the motion ends (no memory kept) · the closing copy too.
#   python3 devtests/step/patches/p51_window_layer.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''    if(kf.o){o=panel.style.transformOrigin;panel.style.transformOrigin=kf.o}
    const a=panel.animate(kf,{duration:HW_MS[s],easing:s==='spring'?'cubic-bezier(.34,1.56,.64,1)':'cubic-bezier(.2,.8,.2,1)',fill:'backwards'});''',
     '''    if(kf.o){o=panel.style.transformOrigin;panel.style.transformOrigin=kf.o}
    const wc=panel.style.willChange;panel.style.willChange=s==='blur'?'transform,opacity,filter':'transform,opacity';   // 🎬 v3.36.37: طبقتها تنجهّز قبل الحركة
    const a=panel.animate(kf,{duration:HW_MS[s],easing:s==='spring'?'cubic-bezier(.34,1.56,.64,1)':'cubic-bezier(.2,.8,.2,1)',fill:'backwards'});
    const un=()=>{try{panel.style.willChange=wc}catch(e){}};a.addEventListener('finish',un);a.addEventListener('cancel',un);'''),
    ('''    if(kf&&kf.o)p.style.transformOrigin=kf.o;''',
     '''    if(kf&&kf.o)p.style.transformOrigin=kf.o;
    p.style.willChange=s==='blur'?'transform,opacity,filter':'transform,opacity';if(p!==c)c.style.willChange='opacity';   // 🎬 v3.36.37'''),
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
