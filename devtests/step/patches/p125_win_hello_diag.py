# 💻 patch 125 (dashboard v3.36.72 · the Windows program's «hello», what stops it). The Windows check of 2.1 (run 44891504489): on the
#   program's very first start the page still did not say where it drew — ☐ ✕ (every later start does, three times) · when it cannot, it now
#   says why («hello-fail …» ⇒ the program's log «page: hello failed — …»), so the check shows the reason · the brand is found by its own box
#   too (#top .brand · #top) · nothing for the customer changes
#   python3 devtests/step/patches/p125_win_hello_diag.py Holy_Dashboard.pyw
import os, sys

R = [
    ("""function winHello(){try{const c=i=>{const r=document.getElementById(i).getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]};
  const w=['#top .hword','#top .brand .hwd','#top .brand'].map(q=>document.querySelector(q)).find(e=>e&&e.getBoundingClientRect().width>0),r=w.getBoundingClientRect();
  chrome.webview.postMessage('hello '+[...c('wMin'),...c('wMax'),...c('wCls'),r.left+Math.min(40,r.width/2),r.top+r.height/2].map(v=>v.toFixed(1)).join(','))}catch(e){}}""",
     """function winHello(){try{const c=i=>{const r=document.getElementById(i).getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]};
  const w=['#top .hword','#top .brand .hwd','#top .brand','#top'].map(q=>document.querySelector(q)).find(e=>e&&e.getBoundingClientRect().width>0);
  if(!w)throw new Error('no top bar yet ('+(document.getElementById('splash')?'splash':'no splash')+' · '+innerWidth+'x'+innerHeight+')');
  const r=w.getBoundingClientRect(),v=[...c('wMin'),...c('wMax'),...c('wCls'),r.left+Math.min(40,r.width/2),r.top+r.height/2];
  if(v.some(x=>!isFinite(x)))throw new Error('buttons not laid out');
  chrome.webview.postMessage('hello '+v.map(x=>x.toFixed(1)).join(','))}catch(e){try{chrome.webview.postMessage('hello-fail '+String(e&&e.message||e).slice(0,120))}catch(x){}}}"""),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacement · 💻 the program's «hello» says why it could not · compiles · {p}")
