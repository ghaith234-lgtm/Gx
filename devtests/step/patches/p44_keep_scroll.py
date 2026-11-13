# 🪟 patch 44 (dashboard · the window frame) — a fix of v3.36.34: a window drawn again while it is open (⚙️ after choosing a colour,
#   a font, a card look, the frames …) jumped back to its top, because the frame rebuilds its scrolling body every time.
#   Now: the same window drawn again (same size, same title) keeps the place it was scrolled to · a different window starts at its top.
#   python3 devtests/step/patches/p44_keep_scroll.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''function showModal(html,o){const m=$('#modal'),bg=$('#mbg'),small=!!(o&&o.small),was=!bg.hidden,wasSmall=bg.classList.contains('small');
  m.innerHTML=`<button type="button" class="hwx" aria-label="إغلاق" title="إغلاق" onclick="hideModal()">✕</button><div class="hwb">${html}</div>`;''',
     '''function showModal(html,o){const m=$('#modal'),bg=$('#mbg'),small=!!(o&&o.small),was=!bg.hidden,wasSmall=bg.classList.contains('small');
  const ob=was&&m.querySelector('.hwb'),oy=ob?ob.scrollTop:0,oh=ob&&ob.querySelector('h2')?ob.querySelector('h2').textContent:null;   // 🪟 v3.36.35
  m.innerHTML=`<button type="button" class="hwx" aria-label="إغلاق" title="إغلاق" onclick="hideModal()">✕</button><div class="hwb">${html}</div>`;
  if(oy&&wasSmall===small){const nb=m.querySelector('.hwb'),nh=nb.querySelector('h2');if(nh&&nh.textContent===oh)nb.scrollTop=oy}   // نفس النافذة انرسمت من جديد ⇒ بمكانها''')
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
