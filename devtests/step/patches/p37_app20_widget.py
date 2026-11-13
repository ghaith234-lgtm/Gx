# 📱 patch 37 (dashboard · the Android app 2.0) — the owner (13-11): «نجي الان على widget اريد اتغير شكله اتسويه مثل الكروت وافضل
#   كرت b واتضيف عليه ربح البارحه واخر اسبوع واخر شهر · لا خلي اخر اسبوع واخر شهر · خلي لون الويدجيت مثل لون البنفسجي الي بالواجهة»
#   ① /api/app/widget adds «kb» = six numbers of TRADING profit (normal + 💠, like every widget box since v3.36.18): today · yesterday ·
#      the last 7 days · the last 30 days (both counting today) · this month · total — and «t» = each bot's type (its colour on the
#      widget). The 1.9 «k» (three numbers) stays for the 1.9 app.
#   ② the app 2.0 is signed with a NEW key (the 1.9 key was lost) ⇒ Android refuses to update 1.x to it in place:
#      · /api/app/info answers a 1.x app (User-Agent «HolyApp/1.») with code 0 ⇒ it never downloads a file it cannot install
#      · the 📱 panel inside a 1.x app: «⬇️ احفظها» (saved to Downloads/Holy) + the four one-time steps (remove the old app · install
#        2.0 · log in · add the widget) — opened by itself once every two days until the phone runs 2.0
#      · the 📱 panel in the browser: «have Holy 1.x? remove it first»
#   ③ APP_APK_CODE 11 · APP_APK_NAME «2.0» · APP_APK_REKEY 11 (the first code signed with the new key) · APP_APK_B64 = argv[2]
#      (android/build.py --key … — the key never enters the repository)
#   python3 devtests/step/patches/p37_app20_widget.py Holy_Dashboard.pyw android/dist/Holy-2.0.apk
import base64, hashlib, os, re, sys, zipfile

R = [
    # ── ① the widget's numbers
    ('''    rows.sort(key=lambda x: x[0])
    k = lambda lbl, v, sg=True: [lbl] + list(_wd_n(v, "$", sg))
    return {"ok": True, "run": int(o.get("running") or 0), "n": len(rows),
            "k": [k("ربح اليوم", TN.get("today", o.get("today_profit"))), k("هذا الشهر", st.get("mtd")),
                  k("الإجمالي", TN.get("trade_all", o.get("total_profit")), False)],
            "bots": [r for _k, r in rows[:12]], "server": APP_VERSION}''',
     '''    rows.sort(key=lambda x: x[0])
    k = lambda lbl, v, sg=True: [lbl] + list(_wd_n(v, "$", sg))
    # 📱 v3.36.32 (تطبيق 2.0): ستة أرقام من ربح التداول (عادي + 💠) — اليوم · أمس · آخر 7 أيام · آخر 30 يوماً (كلاهما مع اليوم) ·
    #    هذا الشهر · الإجمالي — بطلب واحد يغطي آخر 30 يوماً وبداية الشهر
    _n0 = datetime.now()
    _dy = lambda i: (_n0 - timedelta(days=i)).strftime("%Y-%m-%d")
    _m1 = _n0.strftime("%Y-%m-01")
    _pd = (_safe(trade_period, min(_m1, _dy(29)), today, default=None) or {}).get("per_day")
    _sm = (lambda ds: sum(float((_pd.get(x) or {}).get("n") or 0) + float((_pd.get(x) or {}).get("r") or 0) for x in ds)) if _pd else (lambda ds: None)
    return {"ok": True, "run": int(o.get("running") or 0), "n": len(rows),
            "k": [k("ربح اليوم", TN.get("today", o.get("today_profit"))), k("هذا الشهر", st.get("mtd")),
                  k("الإجمالي", TN.get("trade_all", o.get("total_profit")), False)],
            "kb": [k("اليوم", _sm([today])), k("أمس", _sm([_dy(1)])), k("آخر 7 أيام", _sm([_dy(i) for i in range(7)])),
                   k("آخر 30 يوماً", _sm([_dy(i) for i in range(30)])), k("هذا الشهر", _sm([x for x in (_pd or {}) if x >= _m1])),
                   k("الإجمالي", TN.get("trade_all", o.get("total_profit")), False)],
            "bots": [r for _k, r in rows[:12]], "server": APP_VERSION}'''),
    ('''                     {"e": _WD_E.get(t, "🤖"), "s": str(b.get("symbol") or "").split("-")[0], "on": 1 if b.get("alive") else 0,
                      "a": a, "b": _wd_n(pt, u, False)[0], "c": c}))''',
     '''                     {"e": _WD_E.get(t, "🤖"), "s": str(b.get("symbol") or "").split("-")[0], "on": 1 if b.get("alive") else 0,
                      "a": a, "b": _wd_n(pt, u, False)[0], "c": c, "t": t}))'''),
    ('''    """📱 v3.36.13: ويدجت الشاشة الرئيسية (تطبيق 1.9) — للعرض فقط: ربح اليوم · هذا الشهر · الإجمالي · وكل بوت (رمزه · نوعه · يعمل؟ ·
    ربح اليوم · الإجمالي) — بلا مفاتيح ولا أرصدة ولا أوامر · بمفتاح الجهاز المربوط فقط"""''',
     '''    """📱 v3.36.13: ويدجت الشاشة الرئيسية (تطبيق 1.9) — للعرض فقط: ربح اليوم · هذا الشهر · الإجمالي · وكل بوت (رمزه · نوعه · يعمل؟ ·
    ربح اليوم · الإجمالي) — بلا مفاتيح ولا أرصدة ولا أوامر · بمفتاح الجهاز المربوط فقط
    · v3.36.32 (تطبيق 2.0): «kb» ستة أرقام · «t» نوع كل بوت (لونه على الويدجت) · «k» الثلاثة تبقى لتطبيق 1.9"""'''),
    # ── ② a 1.x app is never offered a file it cannot install
    ('''        if u.path == "/api/app/info":
            _w = win_exe()
            return self._json({"ok": True, "apk": {"code": APP_APK_CODE, "name": APP_APK_NAME, "size": a["size"], "sha256": a["sha256"]},''',
     '''        if u.path == "/api/app/info":
            _w = win_exe()
            # 🔐 v3.36.32: تطبيق 1.x موقّع بالمفتاح القديم ⇒ أندرويد يرفض تحديثه إلى 2.0 ⇒ لا يُعرض عليه تحديث (الانتقال يدوي مرة واحدة من 📱)
            _old = bool(re.search(r"(?:^|\\s)HolyApp/1\\.", str(self.headers.get("User-Agent") or "")))
            return self._json({"ok": True, "apk": {"code": 0 if _old else APP_APK_CODE, "name": APP_APK_NAME, "size": a["size"], "sha256": a["sha256"],
                                                   "rekey": APP_APK_REKEY},'''),
    ('''            info = {"code": APP_APK_CODE, "name": APP_APK_NAME, "size": a["size"]}''',
     '''            info = {"code": APP_APK_CODE, "name": APP_APK_NAME, "size": a["size"], "rekey": APP_APK_REKEY}'''),
    # the 📱 panel inside the app: a 1.x phone gets the one-time move to 2.0
    ('''  if(IN_APP){
    const s=appStat();
    const row=(ic,t,st,btn)=>`<div class="ap-row"><span>${ic} ${t}<small>${st}</small></span>${btn||''}</div>`;''',
     '''  if(IN_APP){
    const s=appStat();
    const OLDKEY=(+A.rekey||0)>(+s.code||0);   // 🔐 v3.36.32: تطبيق 1.x بالمفتاح القديم ⇒ 2.0 تُثبَّت يدوياً مرة واحدة
    const row=(ic,t,st,btn)=>`<div class="ap-row"><span>${ic} ${t}<small>${st}</small></span>${btn||''}</div>`;'''),
    ('''      ${row('⬆️','نسخة التطبيق',`${gEsc(s.name||'?')} · باللوحة: ${gEsc(A.name||'?')}`+((+A.code||0)>(+s.code||0)?' — <b style="color:var(--green)">في تحديث</b>':' — آخر نسخة'),
          `<button onclick="HolyApp.checkUpdate()">${(+A.code||0)>(+s.code||0)?'حدّث':'افحص'}</button>`)}''',
     '''      ${OLDKEY?row('⬆️','نسخة التطبيق',`${gEsc(s.name||'?')} · في اللوحة: ${gEsc(A.name||'?')} — <b style="color:var(--amber)">نسخة جديدة بتوقيع جديد: تُثبَّت يدوياً مرة واحدة</b> (الخطوات أدناه)`,
          `<button class="primary" onclick="appRekeySave()">⬇️ احفظها</button>`):
       row('⬆️','نسخة التطبيق',`${gEsc(s.name||'?')} · باللوحة: ${gEsc(A.name||'?')}`+((+A.code||0)>(+s.code||0)?' — <b style="color:var(--green)">في تحديث</b>':' — آخر نسخة'),
          `<button onclick="HolyApp.checkUpdate()">${(+A.code||0)>(+s.code||0)?'حدّث':'افحص'}</button>`)}'''),
    ('''          ((+s.widget||0)>0?'مضاف إلى الشاشة الرئيسية ✓ — يعرض بوتاتك وأرباحك ويتحدّث كل دقيقة':'بوتاتك وأرباحك على الشاشة الرئيسية')''',
     '''          ((+s.widget||0)>0?'مضاف إلى الشاشة الرئيسية ✓ — يعرض بوتاتك وأرباحك ويتحدّث كل دقيقة':'بوتاتك وأرباحك على الشاشة الرئيسية')
          +(OLDKEY?` · <b>في النسخة ${gEsc(A.name||'')}: ويدجت جديد بلون اللوحة البنفسجي وستة أرقام</b> (اليوم · أمس · آخر 7 أيام · آخر 30 يوماً · هذا الشهر · الإجمالي)`:'')'''),
    ('''    <div class="ap-note">اللوحة نفسها تفتح بالتطبيق — فكل تحديث للوحة يوصلك فوراً. التطبيق يتحدث وحده لما تنزل له نسخة جديدة.</div>`;''',
     '''    ${OLDKEY?`<div class="ap-h">⬆️ الانتقال إلى Holy ${gEsc(A.name||'')} — مرة واحدة</div>
      <ol class="ap-steps"><li>اضغط <b>«⬇️ احفظها»</b> أعلاه — تُحفظ <b dir="ltr">Holy-${gEsc(A.name||'')}.apk</b> في «التنزيلات ← Holy»، وينسخ عنوان لوحتك.</li>
        <li>احذف تطبيق Holy الحالي: اضغط مطوّلاً على أيقونته ثم «إلغاء التثبيت». لوحتك وبوتاتك لا تتأثر — كلها على الخادم.</li>
        <li>افتح تطبيق «الملفات» ← التنزيلات ← Holy ← <b dir="ltr">Holy-${gEsc(A.name||'')}.apk</b> وثبّته (إذا سأل أندرويد: اسمح بالتثبيت من هذا المصدر).</li>
        <li>افتح Holy والصق عنوان لوحتك <code dir="ltr">${gEsc(location.origin)}</code> وادخل — تُربط الإشعارات وحدها. ثم أضف الويدجت الجديد، وافصل الجهاز القديم من القائمة أدناه.</li></ol>
      <div class="ap-note">لماذا يدوياً؟ النسخة ${gEsc(A.name||'')} موقّعة بمفتاح جديد، وأندرويد لا يحدّث تطبيقاً بتوقيع مختلف. هذا مرة واحدة فقط — بعدها يعود التحديث التلقائي.
        إذا تعذّر الحفظ: افتح عنوان لوحتك في متصفح الموبايل ونزّلها من «📱 تطبيق أندرويد».</div>`:''}
    <div class="ap-note">اللوحة نفسها تفتح بالتطبيق — فكل تحديث للوحة يوصلك فوراً. التطبيق يتحدث وحده لما تنزل له نسخة جديدة.</div>`;'''),
    # the 📱 panel in the browser
    ('''      <ol class="ap-steps"><li>نزّله <b>من الموبايل نفسه</b> (افتح هذي الصفحة بمتصفح الموبايل).</li>''',
     '''      ${(+A.rekey||0)>0?`<div class="ap-warn">🔐 عندك Holy 1.x على الموبايل؟ احذفه أولاً (اضغط مطوّلاً على أيقونته ثم «إلغاء التثبيت») ثم ثبّت ${gEsc(A.name||'')} — النسخة الجديدة موقّعة بمفتاح جديد، وهذا مرة واحدة فقط. لوحتك وبوتاتك لا تتأثر.</div>`:''}
      <ol class="ap-steps"><li>نزّله <b>من الموبايل نفسه</b> (افتح هذي الصفحة بمتصفح الموبايل).</li>'''),
    ('''async function appDownload(){try{await holyCopy(location.origin)}catch(e){}
  return dlFile('/app/holy.apk','Holy.apk')}''',
     '''async function appDownload(){try{await holyCopy(location.origin)}catch(e){}
  return dlFile('/app/holy.apk','Holy.apk')}
async function appRekeySave(){try{await holyCopy(location.origin)}catch(e){}   // 🔐 v3.36.32: من داخل تطبيق 1.x ⇒ ملف 2.0 إلى «التنزيلات ← Holy»
  if(await dlFile('/app/holy.apk','Holy.apk'))toast('✅ حُفظت في التنزيلات ← Holy — الآن احذف التطبيق الحالي ثم ثبّتها',true)}'''),
    # opened by itself once every two days while the phone still runs 1.x
    ('''async function appAuto(){                               // 🔗 أول ما تدخل من التطبيق: يربط الجهاز بالإشعارات وحده (مرة وحدة)
  if(!IN_APP||APP_AUTO)return;APP_AUTO=1;appBg();
  try{if(HolyApp.needPair())await appPair(true)}catch(e){}}''',
     '''async function appAuto(){                               // 🔗 أول ما تدخل من التطبيق: يربط الجهاز بالإشعارات وحده (مرة وحدة)
  if(!IN_APP||APP_AUTO)return;APP_AUTO=1;appBg();
  try{if(HolyApp.needPair())await appPair(true)}catch(e){}
  try{const r=await api('/api/app/devices',{act:'list'}),A=(r&&r.apk)||{};          // 🔐 v3.36.32: تطبيق 1.x ⇒ نافذة الانتقال إلى 2.0 كل يومين
    if((+A.rekey||0)>(+appStat().code||0)&&Date.now()-(+localStorage.getItem('holy_rekey_seen')||0)>2*86400e3){
      localStorage.setItem('holy_rekey_seen',String(Date.now()));setTimeout(openAppPanel,2500)}}catch(e){}}'''),
    # ── ③ the app itself
    ('''# 📱 v3.24.0: تطبيق أندرويد المدمج (APK موقّع · يتولّد ويتحدّث بـ android/tools/embed_apk.py — لا تعدّله يدوياً)''',
     '''# 📱 v3.24.0: تطبيق أندرويد المدمج (APK موقّع) — v3.36.32: يُبنى بـ android/build.py ويوضع هنا بـ devtests/step/patches/p37 (لا تعدّله يدوياً)'''),
]

if __name__ == "__main__":
    p, apk = sys.argv[1], sys.argv[2]
    raw = open(apk, "rb").read()
    with zipfile.ZipFile(apk) as z:
        assert "classes.dex" in z.namelist() and "AndroidManifest.xml" in z.namelist(), "not an APK"
        dex = z.read("classes.dex")
    assert b"Lcom/holy/dash/WidgetArt;" in dex, "this APK has no 2.0 widget"
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    APK_RE = re.compile(r'^APP_APK_CODE = \d+\nAPP_APK_NAME = "[^"]*"\nAPP_APK_B64 = "[A-Za-z0-9+/=]+"$', re.M)
    if len(APK_RE.findall(s)) != 1:
        print("❌ the APP_APK_* block not found exactly once — nothing written"); sys.exit(1)
    blk = ('APP_APK_CODE = 11\nAPP_APK_NAME = "2.0"\n'
           'APP_APK_REKEY = 11     # 🔐 v3.36.32: أول رمز موقّع بالمفتاح الجديد — ما قبله (1.x) لا يتحدّث إليه ذاتياً\n'
           'APP_APK_B64 = "' + base64.b64encode(raw).decode() + '"')
    s = APK_RE.sub(lambda m: blk, s)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · APK {len(raw)} bytes sha256 {hashlib.sha256(raw).hexdigest()[:16]} · compiles · {p}")
