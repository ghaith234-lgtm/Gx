# p143 — v3.36.77 🏷️ the version number and the words that still said «no direction forecast»
#   · APP_VERSION 3.36.77
#   · the test notice, the ⚙️ row and the small notices panel now name the groups (their calls come only from a group whose own record is
#     proven) and the US releases — «احتمالات لا ضمانات · لا أوامر» instead of «لا توقّع اتجاه»
#   python3 devtests/step/patches/p143_version_words.py Holy_Dashboard.pyw
import sys, os

R = [
    ('APP_VERSION = "3.36.76"', 'APP_VERSION = "3.36.77"'),
    ('            f"بطاقة واحدة لكل عملة · والطارئ فوراً حتى في ساعات الهدوء — لا توقّع اتجاه ولا أوامر\\n⚙️ {SG_CH[cfg[\'ch\']]}")',
     '            f"بطاقة واحدة لكل عملة · والطارئ فوراً حتى في ساعات الهدوء — احتمالات لا ضمانات · لا أوامر\\n⚙️ {SG_CH[cfg[\'ch\']]}")'),
    ("+L('📈','تنبيهات السوق',\"openSig('cfg')\",'الاتجاه · الحجم · كسر المستويات · الحركة خارج المدى · السوق'))}",
     "+L('📈','تنبيهات السوق',\"openSig('cfg')\",'المجاميع · الاتجاه · الحجم · كسر المستويات · الحركة خارج المدى · الأخبار الأمريكية'))}"),
    ('<b>🔔 تنبيهات السوق — الاتجاه · الحجم · كسر المستويات · الحركة خارج المدى · السوق</b>',
     '<b>🔔 تنبيهات السوق — المجاميع · الاتجاه · الحجم · كسر المستويات · الحركة خارج المدى · الأخبار الأمريكية</b>'),
    ('<div class="ind-sub" style="margin-top:6px">تنبيهات بما يحدث فعلاً بالأرقام — لا توقّع اتجاه ولا أوامر · كل حدث مرة واحدة · لعملاتك وللسوق كله</div>',
     '<div class="ind-sub" style="margin-top:6px">حقائق الآن بالأرقام · وتنبؤات المجاميع التي ثبت سجلها على التاريخ — احتمالات لا ضمانات · لا أوامر · كل حدث مرة واحدة · لعملاتك وللسوق كله</div>'),
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
    print(f"✅ {len(R)} replacements · v3.36.77 · the words name the groups · {p}")
