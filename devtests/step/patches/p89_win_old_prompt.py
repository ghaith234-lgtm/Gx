# 💻 patch 89 (dashboard v3.36.54 · the old Windows program is told plainly) — the owner (15-11): «تطبيق الحاسوب المفروض يصير x#- (حسب الترتيب)
#   يصير بالداخل مع الاشعارارت وينزال الشريط الفوق (طلبتها سابقا)». That is the Windows program 2.0 (v3.36.41: no title bar · — ☐ ✕ beside
#   🔔 · the top bar moves the window) — but it only reaches a computer when it is downloaded again from ⚙️ «💻 برنامج ويندوز»; the 1.2
#   program already installed keeps opening the Edge window with its title bar, and the page said «a newer version» only inside that panel.
#   ⇒ inside an older program (IN_WIN without window.HOLYWIN · its version below the one in the dashboard) a bar at the top of the page:
#     «💻 برنامج ويندوز 2.0 جاهز — بلا شريط عنوان …» [⬇️ نزّله وافتحه مرة] [لاحقاً] · one click downloads it with this dashboard's address
#     (opened once it replaces the old copy · its shortcuts · its start with Windows) · «لاحقاً» = 3 days on this computer
#   · inside 2.0 that had to fall back to the Edge window (no WebView2 runtime) ⇒ the bar says to install Microsoft Edge WebView2 instead
#   python3 devtests/step/patches/p89_win_old_prompt.py Holy_Dashboard.pyw
import os, sys

JS = r'''/* 💻 v3.36.54: برنامج ويندوز قديم (1.x — بشريط عنوان) ⇒ شريط واضح أعلى اللوحة بتنزيل 2.0 بضغطة · 2.0 بلا WebView2 ⇒ تنصيبه */
async function winOldBar(){
  if(!IN_WIN||WINF||document.getElementById('winOld'))return;
  try{if(+localStorage.getItem('holy_winold_later')>Date.now())return}catch(e){}
  let W={};try{W=(await api('/api/app/info')).win||{}}catch(e){return}
  const hv=(()=>{try{return sessionStorage.getItem('holy_win')||''}catch(e){return ''}})();
  const cur=parseFloat(hv)||1,nv=parseFloat(W.name)||0;if(!nv)return;
  const old=cur<nv,b=document.createElement('div');b.id='winOld';b.className='winold';
  b.innerHTML=old?`<span>💻 <b>برنامج ويندوز ${gEsc(W.name)} جاهز</b> — بلا شريط عنوان: أزرار <b dir="ltr">— ☐ ✕</b> بجانب 🔔 داخل اللوحة، وتحريك النافذة من شريطها العلوي. نسختك الحالية ${gEsc(hv||'1')}.</span>
    <button class="primary" onclick="winOldGet()">⬇️ نزّله وافتحه مرة</button><button onclick="winOldLater()">لاحقاً</button>`
    :`<span>💻 يعمل البرنامج الآن داخل نافذة Edge (بشريط عنوان) لأن <b>Microsoft Edge WebView2</b> غير منصّب على هذا الحاسوب — نصّبه من موقع Microsoft ثم افتح البرنامج من جديد لتظهر النافذة بلا شريط عنوان.</span>
    <button onclick="winOldLater()">حسناً</button>`;
  document.body.insertBefore(b,document.body.firstChild)}
function winOldGet(){dlFile('/app/holy.exe?u='+encodeURIComponent(location.origin),'TheHolyDashboard.exe');
  toast('⬇️ افتح الملف المنزّل مرة واحدة — يحل محل البرنامج القديم واختصاراته، ثم أغلق هذه النافذة',true)}
function winOldLater(){try{localStorage.setItem('holy_winold_later',String(Date.now()+3*864e5))}catch(e){}const b=document.getElementById('winOld');if(b)b.remove()}
'''
CSS = r'''.winold{position:relative;z-index:60;display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:8px 12px 0;padding:10px 14px;border-radius:14px;
  background:linear-gradient(135deg,rgb(var(--cyan-rgb)/.14),rgb(var(--vio3-rgb)/.16));border:1px solid rgb(var(--cyan-rgb)/.45);color:var(--tx);font-size:13px;line-height:1.7}
.winold span{flex:1 1 320px}.winold button{font-size:12.5px;padding:6px 14px}
'''

R = [
    ('''async function openWinPanel(){''', JS + '''async function openWinPanel(){'''),
    ('''setTimeout(rmBoot,3600);try{winInit()}catch(e){}''', '''setTimeout(rmBoot,3600);try{winInit()}catch(e){}setTimeout(()=>{try{winOldBar()}catch(e){}},2500);'''),
    ('''.ap-hero b{font-size:13px;color:var(--tx)}''', CSS.strip() + "\n" + '''.ap-hero b{font-size:13px;color:var(--tx)}'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:80]!r}"); sys.exit(1)
        s = s.replace(a, b, 1)
    s = s.replace('APP_VERSION = "3.36.53"', 'APP_VERSION = "3.36.54"', 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
