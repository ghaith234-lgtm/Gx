# 🔤 patch 40 (dashboard · the writing) — the owner (13-11): «اريد اغير شكل الكتابة او تضع في الاعدادات اشكال من الكتابة».
#   ⚙️ «🔤 خط الكتابة (لهذا الجهاز)»: nine Arabic fonts, each button written in its own font — IBM Plex Sans Arabic (the default, as
#   before) · Cairo · Tajawal · Almarai · Noto Kufi Arabic · Readex Pro · Noto Naskh Arabic · Amiri · the device's own font. The choice
#   is kept on this device (like the theme and the card skin), applied before the page paints (no flash of the old font), the font
#   file loaded only when chosen (Google Fonts, like the default one). The numbers keep their monospace font (columns stay aligned).
#   python3 devtests/step/patches/p40_fonts.py Holy_Dashboard.pyw
import os, sys

FONTS = '''[['plex','IBM Plex Sans Arabic','IBM Plex','IBM+Plex+Sans+Arabic:wght@400;500;600;700'],['cairo','Cairo','القاهرة Cairo','Cairo:wght@400;500;600;700'],
  ['tajawal','Tajawal','تجوال Tajawal','Tajawal:wght@400;500;700'],['almarai','Almarai','المراعي Almarai','Almarai:wght@400;700'],
  ['kufi','Noto Kufi Arabic','كوفي Noto Kufi','Noto+Kufi+Arabic:wght@400;500;600;700'],['readex','Readex Pro','ريدكس Readex','Readex+Pro:wght@400;500;600;700'],
  ['naskh','Noto Naskh Arabic','نسخ Noto Naskh','Noto+Naskh+Arabic:wght@400;500;600;700'],['amiri','Amiri','أميري Amiri','Amiri:wght@400;700'],
  ['sys','system-ui','خط الجهاز','']]'''

HEAD_OLD = '''<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">'''
HEAD_NEW = HEAD_OLD + '''
<script>/* 🔤 v3.36.33: خط الكتابة المختار لهذا الجهاز — قبل الرسم (بلا ومضة الخط القديم) */
var HFONTS=''' + FONTS + ''';
function hFontApply(k){var f=HFONTS.find(function(x){return x[0]===k})||HFONTS[0];
  document.documentElement.style.setProperty('--ff',f[1]==='system-ui'?'system-ui':"'"+f[1]+"'");
  if(f[3]&&f[0]!=='plex'&&!document.getElementById('hfont-'+f[0])){var l=document.createElement('link');l.id='hfont-'+f[0];l.rel='stylesheet';
    l.href='https://fonts.googleapis.com/css2?family='+f[3]+'&display=swap';document.head.appendChild(l)}return f}
try{hFontApply(localStorage.getItem('dash_font')||'plex')}catch(e){}</script>'''

R = [
    (HEAD_OLD, HEAD_NEW),
    ('''body{font-family:'IBM Plex Sans Arabic',system-ui,sans-serif;''',
     '''body{font-family:var(--ff,'IBM Plex Sans Arabic'),system-ui,sans-serif;'''),
    # ⚙️ the row — right under the card skins
    ('''<div class="pollrow" id="skinRow">${[['old','القديم'],['c','ج — الرسمة أولاً'],['b','ب — شريط الأرقام'],['o','OKX']].map(x=>`<button class="${uiSkin()===x[0]?'on':''}" onclick="setSkin('${x[0]}')">${x[1]}</button>`).join('')}</div></div>''',
     '''<div class="pollrow" id="skinRow">${[['old','القديم'],['c','ج — الرسمة أولاً'],['b','ب — شريط الأرقام'],['o','OKX']].map(x=>`<button class="${uiSkin()===x[0]?'on':''}" onclick="setSkin('${x[0]}')">${x[1]}</button>`).join('')}</div></div>
   <div style="margin-top:8px"><div style="font-size:11px;color:var(--mut2);margin-bottom:6px">🔤 خط الكتابة (لهذا الجهاز) — كل زر مكتوب بخطّه · الأرقام تبقى بخطّها الثابت:</div><div class="pollrow" id="fontRow">${HFONTS.map(x=>`<button class="${uiFont()===x[0]?'on':''}" data-font="${x[0]}" style="font-family:${x[1]==='system-ui'?'system-ui':`'${x[1]}'`},system-ui" onmouseenter="hFontPre('${x[0]}')" onclick="setFont('${x[0]}')">${x[2]}</button>`).join('')}</div></div>'''),
    ('''function _ls(k,v){''', '''function uiFont(){const k=_ls('dash_font');return HFONTS.some(x=>x[0]===k)?k:'plex'}       // 🔤 v3.36.33
function hFontPre(k){try{const f=HFONTS.find(x=>x[0]===k);if(f&&f[3]&&!document.getElementById('hfont-'+k)){const l=document.createElement('link');l.id='hfont-'+k;l.rel='stylesheet';
  l.href='https://fonts.googleapis.com/css2?family='+f[3]+'&display=swap';document.head.appendChild(l)}}catch(e){}}
function setFont(k){const f=hFontApply(k);_ls('dash_font',f[0]==='plex'?null:f[0]);
  try{if(typeof rowsFit==='function')setTimeout(rowsFit,300)}catch(e){}openSettings();toast('🔤 خط الكتابة: '+f[2],true)}
function _ls(k,v){'''),
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
