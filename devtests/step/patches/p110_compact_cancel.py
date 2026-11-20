# 📏 patch 110 (dashboard v3.36.64 · a compact card always ends its motion). Found by the regression under load (ui_compact ⑥ 33/34):
#   a tap closes an open card · the page re-sorts the cards while it shrinks (it moves cards in the page — e.g. a bot's state changed) ⇒
#   the browser drops the height animation without «finish» ⇒ the card stayed open, clipped (`cmpa`), half-closed in memory (`_cmC`) —
#   until the next tap. Now the end runs whatever happens to the animation:
#   · «finish» · a «cancel» from outside (the page moved/hid the card) · and a timer at the animation's length + a margin (a phone that
#     paused the page) — the first one wins, the others do nothing
#   python3 devtests/step/patches/p110_compact_cancel.py Holy_Dashboard.pyw
import os, sys

R = [
    ("""  a.onfinish=()=>{if(el._cmA!==a)return;el._cmA=null;el.classList.remove('cmpa');if(!open){el._cmC=0;el._cmO=0;cmpApply(el,el._cmM,el._cmS)}};
  a.oncancel=()=>{if(!el._cmA)el.classList.remove('cmpa')}}""",
     """  const fin=()=>{if(el._cmA!==a)return;el._cmA=null;clearTimeout(el._cmT);el.classList.remove('cmpa');if(!open){el._cmC=0;el._cmO=0;cmpApply(el,el._cmM,el._cmS)}};
  a.onfinish=fin;
  a.oncancel=()=>{if(el._cmA===a)fin();else if(!el._cmA)el.classList.remove('cmpa')};   // 📏 v3.36.64: ألغاها غيرنا (الصفحة نقلت البطاقة) ⇒ النهاية نفسها
  clearTimeout(el._cmT);el._cmT=setTimeout(fin,340+400)}             // ولو ما وصل حدث أصلاً ⇒ النهاية بعد مدتها"""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacement · 📏 a compact card always ends its motion (finish · cancel · timer) · compiles · {p}")
