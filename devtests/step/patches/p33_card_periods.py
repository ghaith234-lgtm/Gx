# 🖼️ patch 33 (dashboard · the profit card) — the owner (8-11): «ضيف على بطاقة الارباح البارحه ، الاسبوع السابق ، الشهر الحالي ، والشهر السابق».
#   The card (🖼️ بطاقة الأرباح) had today · 7 · 30 · 90 days · a year. Now also: yesterday (that day alone) · the previous week (Monday to
#   Sunday, whole) · the current month (from the 1st to today) · the previous month (whole). The numbers come from the same /api/profit
#   the reports use — the month two existed already (per=month · per=prev, v3.36.10/12); yesterday and the previous week are two new
#   «per» keys (an end date + a day count, like the previous month). The card's date line names the period and its days.
#   python3 devtests/step/patches/p33_card_periods.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''            _per = _per if _per in ("month", "prev") else ""''',
     '''            _per = _per if _per in ("month", "prev", "yday", "pweek") else ""'''),
    ('''            elif _per == "prev":                           # ⏮️ v3.36.12: الشهر السابق كاملاً (من 1 لآخر يوم بيه — ما يتغيّر)
                _end, pdays = _prev_month()''',
     '''            elif _per == "prev":                           # ⏮️ v3.36.12: الشهر السابق كاملاً (من 1 لآخر يوم بيه — ما يتغيّر)
                _end, pdays = _prev_month()
            elif _per == "yday":                           # 🖼️ v3.36.28: البارحة (يوم واحد)
                _end, pdays = datetime.now().date() - timedelta(days=1), 1
            elif _per == "pweek":                          # 🖼️ v3.36.28: الأسبوع السابق كاملاً (الاثنين ← الأحد)
                _end, pdays = _prev_week()'''),
    ('''def _prev_month():''',
     '''def _prev_week():
    """🖼️ v3.36.28: الأسبوع السابق — (الأحد آخر يوم بيه · 7 أيام من الاثنين)"""
    t = datetime.now().date()
    return t - timedelta(days=t.weekday() + 1), 7


def _prev_month():'''),
    ('''const CARD_P=[[1,'اليوم'],[7,'آخر 7 أيام'],[30,'آخر 30 يوم'],[90,'آخر 90 يوم'],[365,'آخر سنة']];''',
     '''const CARD_P=[[1,'اليوم'],['yday','البارحة'],[7,'آخر 7 أيام'],['pweek','الأسبوع السابق'],['month','الشهر الحالي'],['prev','الشهر السابق'],[30,'آخر 30 يوم'],[90,'آخر 90 يوم'],[365,'آخر سنة']];   // 🖼️ v3.36.28: + البارحة · الأسبوع السابق · الشهر الحالي · الشهر السابق'''),
    ('''  try{const s=JSON.parse(localStorage.getItem('holy_card')||'null');if(s){if(s.days)CARD.days=s.days;Object.assign(CARD.opt,s.opt||{})}}catch(e){}''',
     '''  try{const s=JSON.parse(localStorage.getItem('holy_card')||'null');if(s){if(s.days&&CARD_P.some(p=>String(p[0])===String(s.days)))CARD.days=s.days;Object.assign(CARD.opt,s.opt||{})}}catch(e){}'''),
    ('''<button data-d="${d}" class="${d===CARD.days?'primary':''}" onclick="cardSet('days',${d})">${l}</button>''',
     '''<button data-d="${d}" class="${String(d)===String(CARD.days)?'primary':''}" onclick="cardSet('days','${d}')">${l}</button>'''),
    ('''function cardSet(k,v){if(k==='days'){CARD.days=v;CARD.v=null;document.querySelectorAll('#cd_p button').forEach(b=>b.className=(+b.dataset.d===v)?'primary':'')}''',
     '''function cardSet(k,v){if(k==='days'){v=/^\\d+$/.test(String(v))?+v:String(v);CARD.days=v;CARD.v=null;document.querySelectorAll('#cd_p button').forEach(b=>b.className=(b.dataset.d===String(v))?'primary':'')}'''),
    ('''CARD.v=await api('/api/profit?days='+CARD.days);''',
     '''CARD.v=await api('/api/profit?'+(typeof CARD.days==='number'?'days='+CARD.days:'per='+CARD.days));'''),
    ('''lab=(CARD_P.find(p=>p[0]===rq)||[0,`آخر ${rq} يوم`])[1];''',
     '''lab=(CARD_P.find(p=>String(p[0])===String(rq))||[0,`آخر ${rq} يوم`])[1];'''),
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
