# 📊 patch 59 (dashboard · the small top bar) — the owner (13-11): «ضع معه سعة بطارية الموبايل استخدام المعالج واشياء انت قلي عليها» ⇒
#   the list offered ⇒ «كلهم ضيفهم ، لا تضع سرعة الوصول لokx».
#   A second line under the profits, each item shown or hidden from ⚙️ 🖌️ «📊 عناصر الشريط المصغّر» (this device · all shown at first):
#     📱 this device: 🔋 battery % (⚡ charging) · 📶 the connection · 🕐 the clock · ⏱️ the server's answer time (the overview fetch itself)
#     🖥️ the bots' computer: CPU % · memory % · free disk · how long it has been on — GET /api/sys (read-only · behind the login ·
#        no library: Windows ctypes · Linux /proc · asked every 10 s only while the bar shows and one of them is on)
#     📊 the dashboard: running bots · the live prices (connected or not — NOT OKX's speed, as the owner asked) · the last update
#   A browser that does not give an item (a computer without a battery · no connection info) ⇒ the item is simply not shown.
#   python3 devtests/step/patches/p59_mbar_status.py Holy_Dashboard.pyw
import os, sys

PY_SYS = '''# 🖥️ v3.36.39 (المالك 13-11: «كلهم ضيفهم»): حاسوب البوتات للشريط المصغّر — المعالج % · الذاكرة % · القرص المتاح · مدة التشغيل ·
#   بلا مكتبات (ويندوز: ctypes · لينكس: /proc) · قراءة فقط · ما يلمس البوتات ولا المنصة · المعالج = الفرق بين قراءتين
_SYS = {"cpu": None, "lk": threading.Lock()}


def _sys_cpu_times():
    if os.name == "nt":
        import ctypes

        class _FT(ctypes.Structure):
            _fields_ = [("lo", ctypes.c_uint32), ("hi", ctypes.c_uint32)]
        i, k, u = _FT(), _FT(), _FT()
        if not ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(i), ctypes.byref(k), ctypes.byref(u)):
            return None
        f = lambda x: (x.hi << 32) | x.lo
        return f(k) + f(u), f(i)                                  # وقت النواة يشمل الخمول
    with open("/proc/stat") as fh:
        p = [float(x) for x in fh.readline().split()[1:]]
    return sum(p[:8]), p[3] + (p[4] if len(p) > 4 else 0.0)


def _sys_ram_up():
    ram = up = None
    if os.name == "nt":
        import ctypes

        class _MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_uint32), ("dwMemoryLoad", ctypes.c_uint32), ("ullTotalPhys", ctypes.c_uint64), ("ullAvailPhys", ctypes.c_uint64),
                        ("ullTotalPageFile", ctypes.c_uint64), ("ullAvailPageFile", ctypes.c_uint64), ("ullTotalVirtual", ctypes.c_uint64),
                        ("ullAvailVirtual", ctypes.c_uint64), ("ullAvailExtendedVirtual", ctypes.c_uint64)]
        m = _MS(); m.dwLength = ctypes.sizeof(_MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)) and m.ullTotalPhys:
            ram = round(100.0 * (m.ullTotalPhys - m.ullAvailPhys) / m.ullTotalPhys, 1)
        g = ctypes.windll.kernel32.GetTickCount64; g.restype = ctypes.c_uint64
        up = int(g() // 1000)
        return ram, up
    try:
        mi = {}
        with open("/proc/meminfo") as fh:
            for ln in fh:
                a = ln.split()
                if len(a) >= 2:
                    mi[a[0].rstrip(":")] = float(a[1])
        if mi.get("MemTotal") and "MemAvailable" in mi:
            ram = round(100.0 * (1 - mi["MemAvailable"] / mi["MemTotal"]), 1)
    except Exception:
        pass
    try:
        with open("/proc/uptime") as fh:
            up = int(float(fh.read().split()[0]))
    except Exception:
        pass
    return ram, up


def sys_stats():
    out = {"ok": True, "cpu": None, "ram": None, "disk_free": None, "disk_total": None, "up": None}
    try:
        du = shutil.disk_usage(ROOT)
        out["disk_free"], out["disk_total"] = int(du.free), int(du.total)
    except Exception:
        pass
    try:
        out["ram"], out["up"] = _sys_ram_up()
    except Exception:
        pass
    try:
        with _SYS["lk"]:
            now, a, st = time.time(), _sys_cpu_times(), _SYS["cpu"]       # st = (وقت · الكلي · الخمول · النسبة)
            if a and (not st or now - st[0] > 30):                         # ما في قراءة قريبة ⇒ نظرة ثانية بعد ربع ثانية
                st = (now, a[0], a[1], None)
                time.sleep(0.25)
                now, a = time.time(), _sys_cpu_times()
            if a and st and now - st[0] >= 0.2 and a[0] > st[1]:
                st = (now, a[0], a[1], round(max(0.0, min(100.0, 100.0 * (1 - (a[1] - st[2]) / (a[0] - st[1])))), 1))
            _SYS["cpu"] = st
            out["cpu"] = st[3] if st else None
    except Exception:
        pass
    return out


def _overview_cached(max_age=1.0):'''

MB_JS = r'''/* 📊 v3.36.39 (المالك 13-11: «كلهم ضيفهم ، لا تضع سرعة الوصول لokx»): الشريط المصغّر — سطر ثاني بحالة هذا الجهاز وحاسوب البوتات واللوحة ·
   كل عنصر يظهر ويختفي من ⚙️ (لهذا الجهاز · كلها ظاهرة بالبداية) · حاسوب البوتات يُسأل كل 10 ثواني بس والشريط ظاهر ·
   متصفح ما يعطي عنصر (حاسوب بلا بطارية · بلا معلومات اتصال) ⇒ العنصر ما يظهر */
const MBI=[['bat','📱','🔋','البطارية'],['net','📱','📶','الاتصال'],['clk','📱','🕐','الساعة'],['rtt','📱','⏱️','زمن رد الخادم'],
  ['cpu','🖥️','🖥️','المعالج'],['ram','🖥️','🧠','الذاكرة'],['dsk','🖥️','💽','مساحة القرص'],['up','🖥️','⏳','مدة التشغيل'],
  ['bots','📊','🟢','البوتات العاملة'],['live','📊','📡','الأسعار اللحظية'],['last','📊','🕑','آخر تحديث']];
const MB={rtt:null,last:0,sys:null,sysT:0,sysBusy:0,bat:null,batOk:null};
function MBOFF(){return new Set(String(_ls('dash_mb_off')||'').split(',').filter(k=>MBI.some(x=>x[0]===k)))}
function mbOn(k){return !MBOFF().has(k)}
function mbBytes(n){const G=1024**3;return n>=1024*G?(n/1024/G).toFixed(1)+'TB':n>=10*G?Math.round(n/G)+'GB':n>=G?(n/G).toFixed(1)+'GB':Math.round(n/1024**2)+'MB'}
function mbDur(s){s=Math.max(0,+s||0);const d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);return d?`${d}ي ${h}س`:h?`${h}س ${m}د`:`${m}د`}
function mbAgo(s){return s<60?Math.max(0,Math.round(s))+'ث':s<3600?Math.floor(s/60)+'د':Math.floor(s/3600)+'س'}
function mbNet(){if(navigator.onLine===false)return '📵 بلا اتصال';const c=navigator.connection;if(!c)return '';
  const q={'3g':' · متوسط','2g':' · بطيء','slow-2g':' · بطيء جداً'}[c.effectiveType]||'',t=c.type;
  return '📶 '+(t==='wifi'?'Wi‑Fi':t==='ethernet'?'سلكي':t==='cellular'?'بيانات الهاتف':'متصل')+q}
function mbLive(){const n=Object.values(LIVE.last||{}).filter(x=>Date.now()-x.ts<20000).length;
  if(LIVE.ws&&LIVE.ws.readyState===1)return n?['📡 مباشر','الأسعار تصل لحظياً']:['📡 متصل','القناة اللحظية مفتوحة — بانتظار سعر'];
  return LIVE.ws?['📡 يتصل…','القناة اللحظية تتصل']:['📡 منقطع','الأسعار تتحدّث مع الأرقام كل بضع ثوانٍ']}
function mbItems(){const D=DATA||{},o=[],off=MBOFF(),on=k=>!off.has(k);
  if(on('bat')&&MB.bat)o.push(['bat',`🔋 ${Math.round(MB.bat.level*100)}%${MB.bat.charging?'⚡':''}`,MB.bat.charging?'بطارية هذا الجهاز — يشحن':'بطارية هذا الجهاز']);
  if(on('net')){const t=mbNet();if(t)o.push(['net',t,'اتصال هذا الجهاز'])}
  if(on('clk')){const d=new Date();o.push(['clk','🕐 '+String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0'),'الساعة'])}
  if(on('rtt')&&MB.rtt!=null)o.push(['rtt',`⏱️ ${Math.round(MB.rtt)}ms`,'زمن رد الخادم على اللوحة (آخر تحديث)']);
  const S=MB.sys;if(S){
    if(on('cpu')&&S.cpu!=null)o.push(['cpu',`🖥️ ${Math.round(S.cpu)}%`,'معالج حاسوب البوتات']);
    if(on('ram')&&S.ram!=null)o.push(['ram',`🧠 ${Math.round(S.ram)}%`,'ذاكرة حاسوب البوتات']);
    if(on('dsk')&&S.disk_free!=null)o.push(['dsk',`💽 ${mbBytes(S.disk_free)}`,'المساحة المتاحة بقرص البوتات']);
    if(on('up')&&S.up!=null)o.push(['up',`⏳ ${mbDur(S.up)}`,'مدة تشغيل حاسوب البوتات منذ آخر إقلاع'])}
  if(on('bots')){const B=D.bots||[];if(B.length)o.push(['bots',`🟢 ${B.filter(b=>b.alive).length}/${B.length}`,'البوتات العاملة من الكل'])}
  if(on('live')){const s=mbLive();o.push(['live',s[0],s[1]])}
  if(on('last')&&MB.last)o.push(['last','🕑 '+mbAgo((Date.now()-MB.last)/1000),'آخر تحديث للأرقام']);
  return o}
function mbPrevEl(){return document.querySelector('#modal .sx[data-k="mbi"].open #mbPrev')}
function mbShown(){return document.body.classList.contains('pastTop')&&!document.documentElement.classList.contains('nombar')}
function mbSysPoll(){if(MB.sysBusy||Date.now()-MB.sysT<10000||!['cpu','ram','dsk','up'].some(mbOn))return;MB.sysBusy=1;MB.sysT=Date.now();
  api('/api/sys',0,1).then(d=>{if(d&&d.ok)MB.sys=d}).catch(()=>{}).finally(()=>{MB.sysBusy=0;mbStatPaint()})}
function mbStatPaint(){const el=document.getElementById('mStat'),p=mbPrevEl();if(!el||!(mbShown()||p))return;mbSysPoll();
  const h=mbItems().map(x=>`<span data-mb="${x[0]}" title="${x[2]}">${x[1]}</span>`).join('');
  if(el._h!==h){el.innerHTML=h;el._h=h}if(p&&p._h!==h){p.innerHTML=h||'<span>— لا عناصر —</span>';p._h=h}}
function mbTog(k){const off=MBOFF();if(off.has(k))off.delete(k);else off.add(k);_ls('dash_mb_off',off.size?[...off].join(','):null);
  const b=document.querySelector('#modal button[data-mbi="'+k+'"]');if(b){b.classList.toggle('on',!off.has(k));b.setAttribute('aria-pressed',String(!off.has(k)))}
  const v=document.querySelector('#modal .sx[data-k="mbi"] .sval');if(v)v.textContent=`${MBI.length-off.size} من ${MBI.length}`;
  if(!off.has(k)&&['cpu','ram','dsk','up'].includes(k))MB.sysT=0;mbStatPaint()}
function mbiBody(){const off=MBOFF();
  const na=[MB.batOk===false?'🔋 البطارية: هذا الجهاز لا يعطيها للمتصفح':'',navigator.connection?'':'📶 الاتصال: هذا المتصفح لا يعطي نوعه'].filter(Boolean);
  return `<div class="snote">اضغط أي عنصر لإظهاره أو إخفائه · لهذا الجهاز · يظهر تحت أرقام الربح حين تنزل للأسفل${uiMbar()?'':' · <b style="color:var(--amber)">الشريط المصغّر مخفي الآن — أظهره من السطر الذي قبل هذا</b>'}</div>
   <div class="mb2 mbprev" id="mbPrev"></div>
   ${[['📱','📱 هذا الجهاز'],['🖥️','🖥️ حاسوب البوتات'],['📊','📊 اللوحة']].map(g=>`<div class="cfx-g"><div class="cfx-gt">${g[1]}</div><div class="pollrow">${MBI.filter(x=>x[1]===g[0]).map(x=>
     `<button type="button" data-mbi="${x[0]}" class="${off.has(x[0])?'':'on'}" aria-pressed="${!off.has(x[0])}" onclick="mbTog('${x[0]}')">${x[2]} ${x[3]}</button>`).join('')}</div></div>`).join('')}
   ${na.length?`<div class="cfx-d" style="margin-top:8px">${na.join(' · ')}</div>`:''}`}
try{if(navigator.getBattery)navigator.getBattery().then(b=>{const mob=IN_APP||/Android|iPhone|iPad|Mobile/i.test(navigator.userAgent);
  const f=()=>{const none=!mob&&b.charging&&b.level>=1&&!b.chargingTime&&b.dischargingTime===Infinity;MB.batOk=!none;MB.bat=none?null:{level:b.level,charging:b.charging};mbStatPaint()};
  f();b.addEventListener('levelchange',f);b.addEventListener('chargingchange',f)}).catch(()=>{MB.batOk=false});else MB.batOk=false}catch(e){MB.batOk=false}
setInterval(()=>{if(!document.hidden&&(mbShown()||mbPrevEl()))try{mbStatPaint()}catch(e){}},1000);
addEventListener('online',()=>{try{mbStatPaint()}catch(e){}});addEventListener('offline',()=>{try{mbStatPaint()}catch(e){}});
async function tick(){'''

MB_CSS = '''html.nombar #mbar{display:none!important}
/* 📊 v3.36.39: الشريط المصغّر — الأرباح · وتحتها حالة هذا الجهاز وحاسوب البوتات واللوحة (بالهاتف تنزل لسطر ثاني لو ما وسعت — ما ينخفي شي) */
#mbar{flex-direction:column;gap:3px}
#mbar .mb1{display:flex;align-items:center;justify-content:center;gap:16px;max-width:100%}
.mb2{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;column-gap:11px;row-gap:1px;max-width:100%;white-space:nowrap;font-size:11px;line-height:1.45;color:var(--mut);font-variant-numeric:tabular-nums}
.mb2:empty{display:none}.mb2>span{flex:0 0 auto}
.mbprev{margin:8px 0 2px;padding:7px 10px;border:1px solid var(--line);border-radius:10px;background:rgb(var(--surf2-rgb)/.6)}
@media (max-width:760px){#mbar .mb1{gap:14px}}'''

R = [
    ('''def _overview_cached(max_age=1.0):''', PY_SYS),
    ('''        if u.path == "/api/overview":
            return self._json(_overview_cached())''',
     '''        if u.path == "/api/overview":
            return self._json(_overview_cached())
        if u.path == "/api/sys":                          # 🖥️ v3.36.39: حاسوب البوتات للشريط المصغّر (قراءة فقط)
            return self._json(_safe(sys_stats, default={"ok": False}) or {"ok": False})'''),
    ('''html.nombar #mbar{display:none!important}''', MB_CSS),
    ('''<div id="mbar" onclick="goTop()" title="ارجع للأعلى"><span id="mPulse" class="pulse off"></span>''',
     '''<div id="mbar" onclick="goTop()" title="ارجع للأعلى"><div class="mb1"><span id="mPulse" class="pulse off"></span>'''),
    ('''<span id="mGuard"></span></div>''',
     '''<span id="mGuard"></span></div><div class="mb2" id="mStat"></div></div>'''),
    ('''function mbarSync(){const h=$('#top');if(h)document.body.classList.toggle('pastTop',h.getBoundingClientRect().bottom<0)}''',
     '''function mbarSync(){const h=$('#top');if(!h)return;const p=h.getBoundingClientRect().bottom<0;
  if(p!==document.body.classList.contains('pastTop')){document.body.classList.toggle('pastTop',p);if(p)try{mbStatPaint()}catch(e){}}}   // 📊 v3.36.39: ينزل ⇒ حالته فوراً'''),
    ('''  _sf('#mPulse',x=>{const p=$('#pulse');if(p)x.className=p.className});''',
     '''  _sf('#mPulse',x=>{const p=$('#pulse');if(p)x.className=p.className});try{mbStatPaint()}catch(e){}'''),
    ('''async function tick(){''', MB_JS),
    ('''try{const d=await api('/api/overview',0,1);const hw=hwIdle();''',
     '''try{const t0=performance.now();const d=await api('/api/overview',0,1);MB.rtt=performance.now()-t0;MB.last=Date.now();const hw=hwIdle();'''),
    ('''     +T('📌','الشريط المصغّر','uiMbarToggle()','bMbar',uiMbar(),'يظهر — أرقام اليوم أعلى الشاشة حين تنزل للأسفل','مخفي')''',
     '''     +T('📌','الشريط المصغّر','uiMbarToggle()','bMbar',uiMbar(),'يظهر — أرقام اليوم أعلى الشاشة حين تنزل للأسفل','مخفي')
     +X('mbi','📊','عناصر الشريط المصغّر',`${MBI.length-MBOFF().size} من ${MBI.length}`,mbiBody())'''),
    ('''  if(on&&k==='cfx')setTimeout(()=>{try{cfxRun('enter');cfxRun('bars')}catch(e){}},280)}''',
     '''  if(on&&k==='cfx')setTimeout(()=>{try{cfxRun('enter');cfxRun('bars')}catch(e){}},280)
  if(on&&k==='mbi')setTimeout(()=>{try{MB.sysT=0;mbStatPaint()}catch(e){}},0)}'''),
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
