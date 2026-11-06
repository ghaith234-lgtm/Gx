# refill the 🧪 trial-path rows of the MAP's function index whose functions carry no docstring (map_remap leaves them empty)
#   (rebuilt 2026-11-06 after the scratchpad was lost — same texts as before)   python3 map_fix_bt.py [MAP.md]
import re, sys
D = {'bt_status': 'تقدّم الاختبار: المسارات المنتهية وملخصاتها · الأخطاء · هل العامل ما زال يعمل', 'bt_path': 'تفاصيل مسار واحد للإعادة داخل الصفحة: نقاط السعر والمحفظة · الصفقات · نوافذ الربح', 'bt_stop': '⏹ يوقف الاختبار الجاري (علامة إيقاف للعمال) ويحتفظ بما انتهى من المسارات'}
p = sys.argv[1] if len(sys.argv) > 1 else "MAP.md"; s = open(p, encoding="utf-8").read(); n = 0
for nm, txt in D.items():
    s, k = re.subn(r"^(\| \d+ \| `" + nm + r"` \|)  \|$", lambda m: m.group(1) + " " + txt + " |", s, flags=re.M); n += k
open(p, "w", encoding="utf-8").write(s); print("refilled", n)
