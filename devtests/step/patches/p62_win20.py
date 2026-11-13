# 💻 patch 62 (dashboard · the Windows program 2.0) — the owner (13-11, with a screenshot of the 1.2 window): «اريد تلغي الرموز الفوق الي
#   بالصورة واتخليهم مع ايقونة الاشعارات · بقت مشكلة وحدة كيف احرك المربع كله اذا انزال الشريط الفوق».
#   The Windows program 2.0 (windows/holy_win.c · WebView2) shows the dashboard in its own window with no title bar and tells the page so
#   (window.HOLYWIN). The page then:
#   ① draws — ☐ ✕ beside 🔔 ⛶ (✕ at the far right as Windows does · red on hover) and the same three on the small top bar
#   ② moves the window: press an empty part of the top bar and move (4 px) ⇒ «win:drag» ⇒ Windows' own move (snaps to the screen's edges ·
#      a maximized window comes down) · double-click the top bar = maximize/restore · a plain click on the small bar still goes to the top
#   ③ ☐ / ❐ follows the window (the program sends its state) · tells the program where its buttons are (for the Windows check)
#   ④ ⚙️ 💻 «برنامج ويندوز» says all this (in MSA)
#   ⑤ WIN_EXE_CODE 4 · WIN_EXE_NAME «2.0» · WIN_EXE_B64 = argv[2] (built and checked on GitHub's Windows machine) — without argv[2] only
#      the page part is applied (the program served stays as it is)
#   python3 devtests/step/patches/p62_win20.py Holy_Dashboard.pyw [TheHolyDashboard.exe]
import base64, hashlib, os, re, sys

OLD_PANEL = '  box.innerHTML=`<div class="ap-hero"><b>لوحتك بنافذتها الخاصة بالحاسوب (بلا شريط متصفح) + إشعاراتها على ويندوز</b>\n      <span>برنامج صغير (<span dir="ltr">${appKB(W.size)}</span>) يفتح اللوحة نفسها (كل تحديث للوحة يوصله فوراً) · أيقونته قرب الساعة توصلك الصفقات والتنبيهات حتى لو سكّرت نافذة اللوحة · يشتغل على كل ويندوز 8/10/11 (32 أو 64 بت) · ما يلمس البوتات.</span></div>\n    ${IN_WIN?`<div class="ap-note">✅ إنت داخل من البرنامج${hv?` (نسخة ${gEsc(hv)})`:\'\'}${newer?\' — <b style="color:var(--green)">في نسخة أحدث: نزّلها وافتحها مرة (تحل محل القديمة)</b>\':\'\'}.</div>`:\'\'}\n    <div class="ap-row" style="margin:8px 0"><span>🔗 عنوان لوحتك داخل البرنامج<small>نفس اللي تفتحه بالمتصفح من الحاسوب</small></span></div>\n    <input id="wn_url" dir="ltr" value="${gEsc(o)}" style="width:100%;margin:0 0 10px">\n    <button class="primary ap-dl" onclick="winDownload()" ${W.size?\'\':\'disabled\'}>⬇️ نزّل البرنامج — The Holy Dashboard ${gEsc(W.name||\'\')}</button>\n    <ol class="ap-steps"><li>نزّله <b>من الحاسوب</b> وحطه بالمكان اللي تريده (مثلاً «المستندات»).</li>\n      <li>افتحه — يسوي اختصار على سطح المكتب وبقائمة ابدأ، يفتح لوحتك بنافذة خاصة بلا شريط متصفح (أزرار تصغير · تكبير · إغلاق — وتسحب أطرافها للحجم اللي تريده)، وتطلع أيقونته قرب الساعة.</li>\n      <li>إذا طلع «Windows protected your PC»: اضغط <b>More info</b> ⇐ <b>Run anyway</b> (البرنامج مو موقّع بشهادة مدفوعة).</li>\n      <li>زر <b>⛶</b> فوق (أو <b>F11</b>) = شاشة كاملة · <b>Esc</b> يرجّع النافذة · <b>Alt+F4</b> يسكّر النافذة (الإشعارات تبقى) · افتحه وإنت ضاغط <b>Shift</b> حتى تغيّر العنوان.</li>\n      <li>🔔 الإشعار ينضغط ⇒ يفتح اللوحة · زر يمين على الأيقونة: إيقاف الإشعارات · «يشتغل ويّا ويندوز» · تغيير العنوان · إغلاق.</li></ol>\n    <div class="ap-note">يحتاج Microsoft Edge (موجود بكل ويندوز 10/11) أو Chrome. يبقى داخل لوحتك بعد أول دخول.</div>\n    ${location.protocol===\'http:\'?`<div class="ap-warn">⚠️ اللوحة على <b>http</b> — إذا تفتحها من برّه البيت ينصح بـ HTTPS.</div>`:\'\'}\n    <div class="ap-h">💻 الحواسيب المربوطة بالإشعارات (${wdevs.length})${wdevs.length?` <button class="ap-cp" onclick="appTest()">🧪 إشعار تجريبي</button>`:\'\'}</div>${devH}`}\n'
NEW_PANEL = '  box.innerHTML=`<div class="ap-hero"><b>لوحتك في نافذتها الخاصة على الحاسوب — بلا شريط عنوان — وإشعاراتها على ويندوز</b>\n      <span>برنامج صغير (<span dir="ltr">${appKB(W.size)}</span>) يفتح اللوحة نفسها (كل تحديث للوحة يصله فوراً) · أيقونته قرب الساعة توصل الصفقات والتنبيهات حتى بعد إغلاق النافذة · يعمل على ويندوز 10/11 (32 أو 64 بت · ويندوز 7/8 بنافذة Edge) · لا يلمس البوتات.</span></div>\n    ${IN_WIN?`<div class="ap-note">✅ أنت داخل من البرنامج${hv?` (نسخة ${gEsc(hv)})`:\'\'}${newer?\' — <b style="color:var(--green)">توجد نسخة أحدث: نزّلها وافتحها مرة (تحل محل القديمة)</b>\':\'\'}.</div>`:\'\'}\n    <div class="ap-row" style="margin:8px 0"><span>🔗 عنوان لوحتك داخل البرنامج<small>نفس العنوان الذي تفتحه في المتصفح من الحاسوب</small></span></div>\n    <input id="wn_url" dir="ltr" value="${gEsc(o)}" style="width:100%;margin:0 0 10px">\n    <button class="primary ap-dl" onclick="winDownload()" ${W.size?\'\':\'disabled\'}>⬇️ نزّل البرنامج — The Holy Dashboard ${gEsc(W.name||\'\')}</button>\n    <ol class="ap-steps"><li>نزّله <b>من الحاسوب</b> وضعه في المكان الذي تريده (مثلاً «المستندات»).</li>\n      <li>افتحه — ينشئ اختصاراً على سطح المكتب وفي قائمة ابدأ، ويفتح لوحتك في نافذة خاصة <b>بلا شريط عنوان</b>: أزرار <b>— ☐ ✕</b> بجانب 🔔 أعلى اللوحة، وتظهر أيقونته قرب الساعة.</li>\n      <li><b>تحريك النافذة:</b> اضغط على مكان فارغ في الشريط العلوي للوحة واسحب · نقرتان = تكبير/إرجاع · اسحب الحواف لتغيير الحجم · اسحبها إلى حافة الشاشة لتلتصق بها.</li>\n      <li>إذا ظهر «Windows protected your PC»: اضغط <b>More info</b> ⇐ <b>Run anyway</b> (البرنامج غير موقّع بشهادة مدفوعة).</li>\n      <li>زر <b>⛶</b> (أو <b>F11</b>) = شاشة كاملة · <b>Esc</b> يرجع النافذة · <b>✕</b> أو <b>Alt+F4</b> يغلق النافذة (الإشعارات تبقى) · افتحه وأنت ضاغط <b>Shift</b> لتغيير العنوان.</li>\n      <li>🔔 الضغط على الإشعار يفتح اللوحة في مكانه · زر الفأرة الأيمن على الأيقونة: فتح اللوحة · عنوان اللوحة · إغلاق البرنامج.</li></ol>\n    <div class="ap-note">يستعمل Microsoft Edge WebView2 (موجود في ويندوز 10/11). تبقى مسجّلاً في لوحتك بعد أول دخول.</div>\n    ${location.protocol===\'http:\'?`<div class="ap-warn">⚠️ اللوحة على <b>http</b> — إذا كنت تفتحها من خارج البيت فيُنصح بـ HTTPS.</div>`:\'\'}\n    <div class="ap-h">💻 الحواسيب المربوطة بالإشعارات (${wdevs.length})${wdevs.length?` <button class="ap-cp" onclick="appTest()">🧪 إشعار تجريبي</button>`:\'\'}</div>${devH}`}\n'

JS = r'''/* 💻 v3.36.41 (المالك 13-11: «اريد تلغي الرموز الفوق … واتخليهم مع ايقونة الاشعارات · كيف احرك المربع كله»): برنامج ويندوز 2.0 —
   نافذة بلا شريط عنوان (WebView2) · — ☐ ✕ جنب 🔔 ⛶ وبالشريط المصغّر · اضغط مكان فاضي بالشريط العلوي واسحب ⇒ Windows يحرّكها ·
   نقرتين = تكبير/إرجاع · البرنامج يقول إنه 2.0 بـwindow.HOLYWIN · الأوامر chrome.webview.postMessage('win:…') */
const WINF=(()=>{try{return !!(IN_WIN&&window.HOLYWIN&&window.chrome&&chrome.webview)}catch(e){return false}})();
function winCmd(c){try{chrome.webview.postMessage('win:'+c)}catch(e){}}
function winFree(t){return !!t&&!t.closest('button,a,input,select,textarea,label,summary,[onclick],[role=button],.st,.click,nav,#stats,.tkw,.ik')}
function winHello(){try{const c=i=>{const r=document.getElementById(i).getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]};
  const w=['#top .hword','#top .brand .hwd','#top .brand'].map(q=>document.querySelector(q)).find(e=>e&&e.getBoundingClientRect().width>0),r=w.getBoundingClientRect();
  chrome.webview.postMessage('hello '+[...c('wMin'),...c('wMax'),...c('wCls'),r.left+Math.min(40,r.width/2),r.top+r.height/2].map(v=>v.toFixed(1)).join(','))}catch(e){}}
function winInit(){if(!WINF)return;const R=document.documentElement;R.classList.add('winf');
  ['wMin','wMax','wCls'].forEach(i=>{const b=document.getElementById(i);if(b)b.hidden=false});
  let dn=null,ht=0;
  addEventListener('pointerdown',e=>{dn=null;if(e.button!==0||!e.target.closest||!e.target.closest('#top,#mbar')||!winFree(e.target))return;
    dn={x:e.screenX,y:e.screenY};if(!e.target.closest('#mbar'))e.preventDefault()},true);
  addEventListener('pointermove',e=>{if(!dn||!(e.buttons&1))return;if(Math.abs(e.screenX-dn.x)+Math.abs(e.screenY-dn.y)>4){dn=null;winCmd('drag')}},true);
  addEventListener('pointerup',()=>{dn=null},true);
  const top=document.getElementById('top');if(top)top.addEventListener('dblclick',e=>{if(winFree(e.target)){e.preventDefault();winCmd('max')}});
  chrome.webview.addEventListener('message',e=>{const d=e.data||{};if(d.t!=='win')return;R.classList.toggle('winmax',!!(d.max||d.fs));
    document.querySelectorAll('#wMax,#mwMax').forEach(b=>{b.textContent=d.max||d.fs?'❐':'☐';b.title=d.max||d.fs?'إرجاع النافذة':'تكبير'})});
  winCmd('state');setTimeout(winHello,1500);addEventListener('resize',()=>{clearTimeout(ht);ht=setTimeout(winHello,600)})}
async function openWinPanel(){'''

R = [
    ('''<button id="bBell" title="سجل الإشعارات" onclick="toggleNotif()">''',
     '''<button id="wCls" class="wbtn wcls" title="إغلاق النافذة — الإشعارات تبقى قرب الساعة" onclick="winCmd('close')" hidden>✕</button><button id="wMax" class="wbtn" title="تكبير" onclick="winCmd('max')" hidden>☐</button><button id="wMin" class="wbtn" title="تصغير" onclick="winCmd('min')" hidden>—</button>
      <button id="bBell" title="سجل الإشعارات" onclick="toggleNotif()">'''),
    ('''<span id="mGuard"></span></div><div class="mb2" id="mStat"></div></div>''',
     '''<span id="mGuard"></span></div><div class="mb2" id="mStat"></div><div class="mbw" id="mbW"><button id="mwCls" class="wcls" title="إغلاق النافذة" onclick="event.stopPropagation();winCmd('close')">✕</button><button id="mwMax" title="تكبير" onclick="event.stopPropagation();winCmd('max')">☐</button><button id="mwMin" title="تصغير" onclick="event.stopPropagation();winCmd('min')">—</button></div></div>'''),
    ('''html.nombar #mbar{display:none!important}   /* 📌 v3.36.38: الشريط المصغّر مطفي بهذا الجهاز */''',
     '''html.nombar #mbar{display:none!important}   /* 📌 v3.36.38: الشريط المصغّر مطفي بهذا الجهاز */
/* 💻 v3.36.41: برنامج ويندوز 2.0 — — ☐ ✕ جنب 🔔 (✕ أقصى اليمين · أحمر عند المرور) · الشريط العلوي يحرّك النافذة */
.wbtn{font-family:'Segoe UI',system-ui,sans-serif!important;min-width:40px}
.wbtn.wcls:hover,.mbw button.wcls:hover{background:#c42b1c!important;border-color:#c42b1c!important;color:#fff!important}
html.winf #top{user-select:none;-webkit-user-select:none}
.mbw{display:none}
html.winf .mbw{display:flex;gap:4px;position:absolute;inset-inline-start:8px;top:6px}
.mbw button{border:1px solid var(--line);background:rgb(var(--ov-rgb)/.06);color:var(--tx);border-radius:8px;width:32px;height:26px;font:13px 'Segoe UI',system-ui,sans-serif;cursor:pointer;padding:0}
html.winf #mbar .mb1,html.winf #mbar .mb2{padding-inline-start:116px}'''),
    ('''async function openWinPanel(){''', JS),
    (OLD_PANEL, NEW_PANEL),
    ('''tick();schedPoll();applyTheme(uiTheme());STK.boot();setTimeout(rmBoot,3600);''',
     '''tick();schedPoll();applyTheme(uiTheme());STK.boot();setTimeout(rmBoot,3600);try{winInit()}catch(e){}'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    if len(sys.argv) > 2:
        raw = open(sys.argv[2], "rb").read()
        tag = raw.find(b"HOLY-URL-SLOT:")
        assert raw[:2] == b"MZ" and tag > 0 and raw.count(b"HOLY-URL-SLOT:") == 1 and raw[tag + 14:tag + 14 + 560] == b"\0" * 560, "not the 2.0 program (its address slot)"
        assert "HolyTray2".encode("utf-16-le") in raw, "not the 2.0 program (HolyTray2)"
        RE = re.compile(r'^WIN_EXE_CODE = \d+\nWIN_EXE_NAME = "[^"]*"\nWIN_EXE_B64 = "[A-Za-z0-9+/=]+"$', re.M)
        if len(RE.findall(s)) != 1:
            print("❌ the WIN_EXE_* block not found exactly once — nothing written"); sys.exit(1)
        s = RE.sub(lambda m: 'WIN_EXE_CODE = 4\nWIN_EXE_NAME = "2.0"\nWIN_EXE_B64 = "' + base64.b64encode(raw).decode() + '"', s)
        print(f"   + the Windows program 2.0: {len(raw)} bytes · sha256 {hashlib.sha256(raw).hexdigest()[:16]}")
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · compiles · {p}")
