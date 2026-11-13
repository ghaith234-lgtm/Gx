# 🔤 patch 61 (dashboard · the owner's own fonts) — the owner (13-11) sent «Khalid Art Bold» and «Arslan Wessam B» (.ttf) to add to
#   ⚙️ «خط الكتابة».
#   They are NOT written into the dashboard: the repository is public (anything inside the code is published) and Khalid Art carries the
#   «restricted licence embedding» flag (fsType 2 — no embedding or passing on without its owner's permission). Instead:
#   ① a «fonts» folder beside the dashboard on the server — every .ttf / .otf / .woff / .woff2 there shows in «خط الكتابة» under its
#      file name (on every device · loaded only when shown)
#   ② ⚙️ «خط الكتابة» ⇒ «➕ أضف خطاً من جهازك» (upload ≤ 12 MB · checked to be a font · saved in that folder · picked at once) ·
#      🗑 beside each of your fonts
#   GET /api/fonts · GET /font/<k>?v=… (behind the login · cached by the browser) · POST /api/fonts {act: add|del} (not written to the
#   journal — the file would be megabytes of text there)
#   python3 devtests/step/patches/p61_owner_fonts.py Holy_Dashboard.pyw
import os, sys

PY = '''# 🔤 v3.36.40 (المالك 13-11: أرسل خط خالد وأرسلان وسام): خطوط المالك من مجلد fonts جنب اللوحة — ما تنكتب بالكود (المستودع عام ·
#   خط خالد مكتوب داخله «تضمين مقيّد») · كل ملف ‎.ttf .otf .woff .woff2‎ هناك يطلع بـ⚙️ «خط الكتابة» باسم ملفه · يُرفع ويُحذف من ⚙️ كمان
FONT_DIR = os.path.join(ROOT, "fonts")
_FONT_CT = {".ttf": "font/ttf", ".otf": "font/otf", ".woff": "font/woff", ".woff2": "font/woff2"}
_FONT_MAGIC = ((b"\\x00\\x01\\x00\\x00", ".ttf"), (b"true", ".ttf"), (b"OTTO", ".otf"), (b"wOFF", ".woff"), (b"wOF2", ".woff2"))
_FONT_MAX = 12 * 1024 * 1024


def _font_label(stem):                                  # «alfont_com_ArbFONTS-Khalid-Art-Bold» ⇒ «Khalid Art Bold»
    s = re.sub(r"(?i)^(?:[a-z0-9]+_com_)+", "", str(stem or ""))
    s = re.sub(r"(?i)^arbfonts[-_ ]+", "", s)
    s = re.sub(r"[_\\-]+", " ", s)
    s = re.sub(r"[^\\w\\s.()]", "", s)
    return re.sub(r"\\s+", " ", s).strip(" .")[:40]


def user_fonts():
    out = []
    try:
        names = sorted(os.listdir(FONT_DIR))
    except Exception:
        return out
    for fn in names:
        ext = os.path.splitext(fn)[1].lower()
        p = os.path.join(FONT_DIR, fn)
        if ext not in _FONT_CT or fn.startswith(".") or not os.path.isfile(p):
            continue
        try:
            st = os.stat(p)
        except Exception:
            continue
        if not 0 < st.st_size <= _FONT_MAX:
            continue
        name = _font_label(os.path.splitext(fn)[0]) or "خط"
        out.append({"k": "u" + _hl.sha256(fn.encode("utf-8")).hexdigest()[:10], "name": name, "file": fn, "size": st.st_size,
                    "v": _hl.sha256(f"{fn}|{st.st_size}|{int(st.st_mtime)}".encode("utf-8")).hexdigest()[:8]})
        if len(out) >= 24:
            break
    return out


def user_font_path(k):
    for f in user_fonts():
        if f["k"] == k:
            return os.path.join(FONT_DIR, f["file"]), _FONT_CT[os.path.splitext(f["file"])[1].lower()]
    return None, None


def user_font_add(name, b64):
    try:
        raw = _b64s.b64decode(str(b64 or "").split(",")[-1], validate=False)
    except Exception:
        return {"ok": False, "msg": "الملف تالف"}
    if not 0 < len(raw) <= _FONT_MAX:
        return {"ok": False, "msg": "الخط أكبر من 12 ميغابايت" if raw else "الملف فارغ"}
    ext = next((e for m, e in _FONT_MAGIC if raw[:4] == m), "")
    if not ext:
        return {"ok": False, "msg": "هذا ليس ملف خط (المقبول: ttf · otf · woff · woff2)"}
    stem = _font_label(os.path.splitext(os.path.basename(str(name or "").replace("\\\\", "/")))[0]) or "خط"
    if len(user_fonts()) >= 24:
        return {"ok": False, "msg": "وصلت 24 خطاً — احذف واحداً أولاً"}
    os.makedirs(FONT_DIR, exist_ok=True)
    fn = stem + ext
    tmp = os.path.join(FONT_DIR, "." + fn + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(raw)
    os.replace(tmp, os.path.join(FONT_DIR, fn))
    k = "u" + _hl.sha256(fn.encode("utf-8")).hexdigest()[:10]
    return {"ok": True, "k": k, "msg": f"🔤 أُضيف الخط «{stem}»", "fonts": user_fonts()}


def user_font_del(k):
    p, _ct = user_font_path(str(k or ""))
    if not p:
        return {"ok": False, "msg": "الخط غير موجود"}
    os.remove(p)
    return {"ok": True, "msg": "🗑 حُذف الخط", "fonts": user_fonts()}


def _overview_cached(max_age=1.0):'''

HEAD_OLD = '''    l.href='https://fonts.googleapis.com/css2?family='+f[3]+'&display=swap';document.head.appendChild(l)}return f}
try{hFontApply(localStorage.getItem('dash_font')||'plex')}catch(e){}</script>'''
HEAD_NEW = '''    l.href='https://fonts.googleapis.com/css2?family='+f[3]+'&display=swap';document.head.appendChild(l)}return f}
/* 🔤 v3.36.40: خطوط المالك (مجلد fonts جنب اللوحة) — قائمتها محفوظة بهذا الجهاز من آخر مرة ⇒ الخط المختار يطلع قبل الرسم */
function hUFonts(L){HFONTS=HFONTS.filter(function(x){return !/^u[0-9a-f]{10}$/.test(x[0])});var c='';
  (L||[]).forEach(function(x){if(!x||!/^u[0-9a-f]{10}$/.test(x.k))return;var fam='HolyU'+x.k,nm=String(x.name||'').replace(/[<>"'&`$\\\\{}]/g,'');
    HFONTS.splice(HFONTS.length-1,0,[x.k,fam,nm,'','/font/'+x.k+'?v='+String(x.v||'').replace(/[^0-9a-f]/g,''),1]);
    c+="@font-face{font-family:'"+fam+"';src:url('/font/"+x.k+"?v="+String(x.v||'').replace(/[^0-9a-f]/g,'')+"');font-display:swap}"});
  var s=document.getElementById('hufonts');if(!s){s=document.createElement('style');s.id='hufonts';document.head.appendChild(s)}s.textContent=c}
try{hUFonts(JSON.parse(localStorage.getItem('dash_ufonts')||'[]'))}catch(e){}
try{hFontApply(localStorage.getItem('dash_font')||'plex')}catch(e){}</script>'''

JS = '''function _ls(k,v){try{if(v===undefined)return localStorage.getItem(k);if(v===null)localStorage.removeItem(k);else localStorage.setItem(k,v)}catch(e){return null}}
/* 🔤 v3.36.40: خطوط المالك — القائمة من الخادم (مجلد fonts) · ➕ رفع خط من الجهاز · 🗑 حذف */
async function ufontsLoad(){try{const r=await api('/api/fonts',0,1);if(!r||!r.ok)return;const L=(r.fonts||[]).map(x=>({k:x.k,name:x.name,v:x.v}));
  _ls('dash_ufonts',L.length?JSON.stringify(L):null);hUFonts(L);const k=_ls('dash_font');if(k&&/^u/.test(k)&&!L.some(x=>x.k===k)){_ls('dash_font',null)}hFontApply(uiFont());
  const row=document.getElementById('fontRow');if(row&&document.querySelector('#modal .sx[data-k="font"]'))openSettings()}catch(e){}}
function ufontPick(){const i=document.getElementById('ufIn');if(i){i.value='';i.click()}}
function ufontUp(inp){const f=inp&&inp.files&&inp.files[0];if(!f)return;if(f.size>12*1024*1024){toast('الخط أكبر من 12 ميغابايت',false);return}
  const rd=new FileReader();toast('🔤 أرفع الخط…',true);
  rd.onload=async()=>{try{const r=await api('/api/fonts',{act:'add',name:f.name,b64:String(rd.result||'')});toast(r.msg,r.ok);if(!r.ok)return;
      const L=(r.fonts||[]).map(x=>({k:x.k,name:x.name,v:x.v}));_ls('dash_ufonts',JSON.stringify(L));hUFonts(L);setFont(r.k)}catch(e){toast('تعذّر رفع الخط',false)}};
  rd.onerror=()=>toast('تعذّر قراءة الملف',false);rd.readAsDataURL(f)}
function ufontDel(k){const f=HFONTS.find(x=>x[0]===k);if(!f)return;
  askConfirm('🗑 حذف الخط «'+gEsc(f[2])+'»؟','يُحذف من مجلد الخطوط على الخادم ومن كل أجهزتك. الأجهزة التي اختارته ترجع إلى IBM Plex.',async()=>{
    try{const r=await api('/api/fonts',{act:'del',k});toast(r.msg,r.ok);if(uiFont()===k)_ls('dash_font',null);await ufontsLoad();hFontApply(uiFont());openSettings()}catch(e){toast('تعذّر الحذف',false)}})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(ufontsLoad,1500));else setTimeout(ufontsLoad,1500);'''

R = [
    ('''def _overview_cached(max_age=1.0):''', PY),
    ('''        if u.path == "/api/sys":                          # 🖥️ v3.36.39: حاسوب البوتات للشريط المصغّر (قراءة فقط)''',
     '''        if u.path == "/api/fonts":                        # 🔤 v3.36.40: خطوط المالك (مجلد fonts)
            return self._json({"ok": True, "fonts": [{k: f[k] for k in ("k", "name", "v", "size")} for f in user_fonts()]})
        if u.path.startswith("/font/"):
            p, ct = user_font_path(u.path[6:])
            if not p:
                return self._json({"ok": False}, 404)
            try:
                with open(p, "rb") as fh:
                    body = fh.read()
            except Exception:
                return self._json({"ok": False}, 404)
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_header("Cache-Control", "private, max-age=31536000, immutable")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except Exception:
                pass
            return
        if u.path == "/api/sys":                          # 🖥️ v3.36.39: حاسوب البوتات للشريط المصغّر (قراءة فقط)'''),
    ('''        if not ("preview" in path or str(data.get("act") or "") == "preview" or path in ("/api/journal", "/api/card_tg")):''',
     '''        if path == "/api/fonts":                          # 🔤 v3.36.40: ما ينكتب بالسجلات (الملف ميغابايتات نص)
            a = str(data.get("act") or "")
            try:
                return self._json(user_font_add(data.get("name"), data.get("b64")) if a == "add" else user_font_del(data.get("k")) if a == "del"
                                  else {"ok": False, "msg": "طلب غير صالح"})
            except Exception as ex:
                return self._json({"ok": False, "msg": f"تعذّر: {type(ex).__name__}"})
        if not ("preview" in path or str(data.get("act") or "") == "preview" or path in ("/api/journal", "/api/card_tg")):'''),
    (HEAD_OLD, HEAD_NEW),
    ('''onclick="setFont('${x[0]}')">${x[2]}</button>`).join('');''',
     '''onclick="setFont('${x[0]}')">${x[2]}${x[5]?' · أبجد هوز':''}</button>`).join('');'''),
    ('''function _ls(k,v){try{if(v===undefined)return localStorage.getItem(k);if(v===null)localStorage.removeItem(k);else localStorage.setItem(k,v)}catch(e){return null}}''', JS),
    ('''<div class="snote">كل زر مكتوب بخطّه · الكلمات والأرقام كلها تأخذه («IBM Plex» = الأرقام بخطّها الثابت القديم).</div><div class="pollrow" id="fontRow">${FN}</div>`)''',
     '''<div class="snote">كل زر مكتوب بخطّه · الكلمات والأرقام كلها تأخذه («IBM Plex» = الأرقام بخطّها الثابت القديم).</div><div class="pollrow" id="fontRow">${FN}</div>
       <div class="snote" style="margin-top:10px">➕ خطوطك: ملف ‎.ttf · .otf‎ من جهازك (أو ضعه في مجلد «fonts» بجانب اللوحة على الخادم) — يظهر هنا في كل أجهزتك.</div>
       <div class="pollrow" id="ufRow"><button type="button" id="ufAdd" onclick="ufontPick()">➕ أضف خطاً من جهازك</button>${HFONTS.filter(x=>x[5]).map(x=>`<button type="button" class="ufDel" data-uf="${x[0]}" title="حذف الخط" onclick="ufontDel('${x[0]}')">🗑 ${gEsc(x[2])}</button>`).join('')}</div>
       <input type="file" id="ufIn" accept=".ttf,.otf,.woff,.woff2,font/ttf,font/otf,font/woff,font/woff2" hidden onchange="ufontUp(this)">`)'''),
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
