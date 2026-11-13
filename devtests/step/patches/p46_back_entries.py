# ↩️ patch 46 (dashboard · the window stack and the browser's back) — a fix of v3.36.34, found by the ⚙️ test of v3.36.35:
#   a window closed and another opened at once (a confirmation whose «تأكيد» opens a result window · any close-then-open in one step) ⇒
#   the closing asked the browser to go back (it happens a moment later) while the new window had already added its entry ⇒ the back
#   took the new window's entry, and closing that window later went back once more — OUT of the dashboard (to the page before it).
#   Only in a browser (the Android app keeps no history entries — holyBack).
#   Now: ① a close followed by an open in the same step reuses the closed window's entry (replaceState) — no back, no new entry
#        ② the backs of one step go together, after it (history.go(-n), once)
#        ③ while a back of ours is on its way, a newly opened window waits for it to land before adding its entry
#   python3 devtests/step/patches/p46_back_entries.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''const HW={st:[],pt:null,skip:0,popping:0};''',
     '''const HW={st:[],pt:null,skip:0,popping:0,pend:0,q:[]};   // ↩️ v3.36.35: pend = رجوعات هذه الخطوة · q = نوافذ تنتظر وصول رجوعنا'''),
    ('''  if(!IN_APP){try{history.pushState({hw:x.k,n:HW.st.length},'');it.h=1}catch(e){}}   // 📱 رجوع المتصفح يسكّرها (التطبيق: holyBack)''',
     '''  if(!IN_APP){if(HW.pend>0){HW.pend--;try{history.replaceState({hw:x.k,n:HW.st.length},'');it.h=1}catch(e){}}   // ↩️ v3.36.35: سكّرت وانفتحت بنفس الخطوة ⇒ نفس الخانة
    else if(HW.skip>0)HW.q.push(it);                                  // رجوع منّا بالطريق ⇒ خانتها بعد ما يوصل
    else{try{history.pushState({hw:x.k,n:HW.st.length},'');it.h=1}catch(e){}}}   // 📱 رجوع المتصفح يسكّرها (التطبيق: holyBack)'''),
    ('''  if(it.h&&!HW.popping){HW.skip++;try{history.back()}catch(e){HW.skip--}}}''',
     '''  const qi=HW.q.indexOf(it);if(qi>=0)HW.q.splice(qi,1);
  if(it.h&&!HW.popping){HW.pend++;if(HW.pend===1)setTimeout(hwFlush,0)}}   // ↩️ v3.36.35: الرجوع بعد الخطوة (لو انفتحت نافذة بنفس الخطوة تاخذ الخانة)
function hwFlush(){const n=HW.pend;HW.pend=0;if(n<=0)return;HW.skip++;
  try{history.go(-n)}catch(e){HW.skip--;hwDrain();return}
  clearTimeout(HW.sto);HW.sto=setTimeout(()=>{if(HW.skip>0){HW.skip=0;hwDrain()}},2500)}   // احتياط: متصفح ما بلّغ بوصوله
function hwDrain(){const q=HW.q.splice(0);for(const it of q)if(HW.st.includes(it)&&!it.h){try{history.pushState({hw:it.k,n:HW.st.length},'');it.h=1}catch(e){}}}'''),
    ('''window.addEventListener('popstate',()=>{if(HW.skip>0){HW.skip--;return}''',
     '''window.addEventListener('popstate',()=>{if(HW.skip>0){HW.skip--;if(!HW.skip){clearTimeout(HW.sto);hwDrain()}return}'''),
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
