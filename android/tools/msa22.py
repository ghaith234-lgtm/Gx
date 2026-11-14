# 🗣️ app 2.2 (the owner 14-11: «حول المشروع كله عربي فصيح»): every text the app shows in MSA + the version 2.1 (12) ⇒ 2.2 (13)
#   The texts live as const-string lines in android/smali (\uXXXX escapes). Each entry below is a WHOLE decoded string (\n = a new
#   line). All or nothing: a string not found ⇒ nothing is written. Runs once (a second run finds nothing to change and says so).
#   python3 android/tools/msa22.py            (from the repo root)
import json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SMALI = os.path.join(ROOT, "smali")
OLD_V, NEW_V, OLD_C, NEW_C = "2.1", "2.2", 12, 13

T = {
    "رمز الموبايل": "رمز الهاتف",
    "افتح Holy واضغط تحديث مرة ثانية": "افتح Holy واضغط تحديث مرة أخرى",
    "ما وصلت للوحة على هذا العنوان — تأكد إنها شغّالة والموبايل متصل بالإنترنت.\nاضغط مطوّلاً على «اتصال» حتى تحفظه بكل الأحوال.":
        "تعذّر الوصول إلى اللوحة على هذا العنوان — تأكد أنها تعمل وأن الهاتف متصل بالإنترنت.\nاضغط مطوّلاً على «اتصال» لحفظه في كل الأحوال.",
    "📋 انتسخ": "📋 نُسخ",
    "🔐 فعّل قفل الشاشة بالموبايل أول (بصمة أو رمز) — من إعدادات الأمان": "🔐 فعّل قفل الشاشة في الهاتف أولاً (بصمة أو رمز) — من إعدادات الأمان",
    "تمام": "حسناً",
    "تأكيد إطفاء القفل بالبصمة": "تأكيد إيقاف القفل بالبصمة",
    "🔋 حتى توصلك الإشعارات بوقتها": "🔋 لتصلك الإشعارات في وقتها",
    "اسمح لـ Holy يشتغل بالخلفية بدون تقييد البطارية — حتى والشاشة مطفية توصلك الصفقات والتنبيهات فوراً.\nاستهلاكه قليل: طلب وحد ينتظر اللوحة.":
        "اسمح لـ Holy بالعمل في الخلفية دون تقييد البطارية — لتصلك الصفقات والتنبيهات فوراً حتى والشاشة مطفأة.\nاستهلاكه قليل: طلب واحد ينتظر اللوحة.",
    "بعدين": "لاحقاً",
    "🚀 حتى توصلك الإشعارات والتطبيق مسكّر": "🚀 لتصلك الإشعارات والتطبيق مغلق",
    "موبايلك (": "هاتفك (",
    ") يسكّر التطبيقات بالخلفية لحاله.\nبالصفحة الجاية فعّل لـ Holy: «التشغيل التلقائي» (Autostart) أو «بلا قيود» للبطارية.\nوإذا تگدر: قفّل Holy بقائمة التطبيقات الأخيرة 🔒 حتى ما ينسكّر لما تمسحها.":
        ") يغلق التطبيقات في الخلفية تلقائياً.\nفي الصفحة التالية فعّل لـ Holy: «التشغيل التلقائي» (Autostart) أو «بلا قيود» للبطارية.\nوإن أمكن: اقفل Holy في قائمة التطبيقات الأخيرة 🔒 كي لا يُغلق حين تمسحها.",
    "اضغط الزر حتى تفتح بالبصمة": "اضغط الزر لتفتح بالبصمة",
    "🔐 القفل بالبصمة شغّال": "🔐 القفل بالبصمة مفعّل",
    "🔓 القفل بالبصمة انطفى": "🔓 أُوقف القفل بالبصمة",
    "🔐 البصمة ما عادت تفتح اللوحة — اكتب كلمة السر مرة وحدة وبعدها ترجع البصمة تكفي": "🔐 لم تعد البصمة تفتح اللوحة — اكتب كلمة السر مرة واحدة ثم تعود البصمة كافية",
    "📡 ما وصلت اللوحة — جرّب مرة ثانية أو اكتب كلمة السر": "📡 تعذّر الوصول إلى اللوحة — أعد المحاولة أو اكتب كلمة السر",
    "العنوان مو صحيح — مثال: http://1.2.3.4:8099": "العنوان غير صحيح — مثال: http://1.2.3.4:8099",
    "⏳ أتأكد من اللوحة…": "⏳ جارٍ التحقق من اللوحة…",
    "ما كدرت أفتح شاشة القفل": "تعذّر فتح شاشة القفل",
    "اضغط رجوع مرة ثانية للخروج": "اضغط رجوع مرة أخرى للخروج",
    "🔐 ما بقى قفل شاشة بالموبايل — انطفى قفل Holy بالبصمة": "🔐 لم يعد في الهاتف قفل شاشة — أُوقف قفل Holy بالبصمة",
    "ما انفتح — جرّب مرة ثانية": "لم يُفتح — أعد المحاولة",
    "بدون إذن التخزين ما أكدر أحفظ — جرّب «مشاركة»": "لا يمكن الحفظ دون إذن التخزين — جرّب «مشاركة»",
    "⬇️ انحفظ بالتنزيلات/Holy: ": "⬇️ حُفظ في التنزيلات/Holy: ",
    "📡 ما وصلت للوحة": "📡 تعذّر الوصول إلى اللوحة",
    "🔄 حاول هسه": "🔄 أعد المحاولة",
    "\nإذا اللوحة تتحدث أو تعيد التشغيل، ترجع وحدها خلال ثواني.\n(": "\nإذا كانت اللوحة تتحدث أو تعيد التشغيل، تعود تلقائياً خلال ثوانٍ.\n(",
    "Holy مقفول 🔐": "Holy مقفل 🔐",
    "افتح بالبصمة حتى تشوف لوحتك": "افتح بالبصمة لترى لوحتك",
    "اكتب عنوان لوحتك (نفس اللي تفتحه بالمتصفح)": "اكتب عنوان لوحتك (نفس الذي تفتحه في المتصفح)",
    "بعد الاتصال ادخل بكلمة السر — والإشعارات تنربط وحدها.": "بعد الاتصال ادخل بكلمة السر — وتُربط الإشعارات تلقائياً.",
    "اللوحة تحتاج «Android System WebView» أحدث حتى تشتغل أزرارها وأرقامها — حدّثه من المتجر وارجع افتح Holy.":
        "تحتاج اللوحة «Android System WebView» أحدث لتعمل أزرارها وأرقامها — حدّثه من المتجر ثم افتح Holy من جديد.",
    "🙈 سطر المراقبة (تكدر تطفيه)": "🙈 سطر المراقبة (يمكنك إيقافه)",
    "السطر الصغير اللي يخلي Holy يشتغل بالخلفية — إذا طفيته الإشعارات تبقى توصل (أندرويد 13 وأحدث)":
        "السطر الصغير الذي يبقي Holy يعمل في الخلفية — إذا أوقفته تبقى الإشعارات تصل (أندرويد 13 وأحدث)",
    "صعود أو نزول قوي لعملات شريط الأسعار — بنغمة Holy": "صعود أو هبوط قوي لعملات شريط الأسعار — بنغمة Holy",
    "⬇️ انحفظ بالتنزيلات": "⬇️ حُفظ في التنزيلات",
    "🔗 انفصل هذا الموبايل عن اللوحة": "🔗 فُصل هذا الهاتف عن اللوحة",
    "افتح Holy وادخل اللوحة حتى ترجع الإشعارات": "افتح Holy وادخل اللوحة لتعود الإشعارات",
    "✅ عندك آخر نسخة (%s)" % OLD_V: "✅ لديك آخر نسخة (%s)" % NEW_V,
    "تعذّر فحص التحديث — ادخل اللوحة وحاول": "تعذّر فحص التحديث — ادخل اللوحة وأعد المحاولة",
    "الملف وصل ناقص أو مختلف — ما ينثبت": "وصل الملف ناقصاً أو مختلفاً — لن يُثبَّت",
    "اسمح لـ Holy يثبّت تحديثاته، وارجع اضغط تحديث": "اسمح لـ Holy بتثبيت تحديثاته، ثم عد واضغط تحديث",
    "⏳ ينزل التحديث…": "⏳ جارٍ تنزيل التحديث…",
    ")\nعندك: ": ")\nلديك: ",
    "\n\nيتحدث الحين؟": "\n\nالتحديث الآن؟",
    "ما متصل باللوحة — أحاول من جديد…": "غير متصل باللوحة — جارٍ إعادة المحاولة…",
}

CS = re.compile(r'^(\s*const-string(?:/jumbo)? [vp]\d+, ")(.*)("\s*)$')


def dec(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            if n == "u":
                out.append(chr(int(s[i + 2:i + 6], 16))); i += 6; continue
            out.append({"n": "\n", "t": "\t", "r": "\r", '"': '"', "'": "'", "\\": "\\"}.get(n, n)); i += 2; continue
        out.append(c); i += 1
    return "".join(out)


def enc(s):
    o = []
    for ch in s:
        if ch == "\\": o.append("\\\\")
        elif ch == '"': o.append('\\"')
        elif ch == "\n": o.append("\\n")
        elif ch == "\t": o.append("\\t")
        elif ord(ch) < 128: o.append(ch)
        elif ord(ch) > 0xFFFF:
            v = ord(ch) - 0x10000
            o.append("\\u%04x\\u%04x" % (0xD800 + (v >> 10), 0xDC00 + (v & 0x3FF)))
        else: o.append("\\u%04x" % ord(ch))
    return "".join(o)


def main():
    files, hit, ver_n = {}, {k: 0 for k in T}, 0
    num = re.compile(r"(?<![\d.])%s(?![\d.])" % re.escape(OLD_V))
    for root, _, names in os.walk(SMALI):
        for n in names:
            if not n.endswith(".smali"):
                continue
            p = os.path.join(root, n)
            L = open(p, encoding="utf-8").read().split("\n")
            ch = False
            for i, l in enumerate(L):
                m = CS.match(l)
                if m:
                    t = dec(m.group(2).replace("\\ud83d", "\\ud83d"))
                    t = t.encode("utf-16", "surrogatepass").decode("utf-16")
                    nt = T.get(t)
                    if nt is not None:
                        hit[t] += 1
                    else:
                        nt = num.sub(NEW_V, t) if num.search(t) else t          # «2.1» and «HolyApp/2.1»
                        if nt != t:
                            ver_n += 1
                    if nt != t:
                        L[i] = m.group(1) + enc(nt) + m.group(3); ch = True
                s = l.strip()
                if s == ".field static final VERSION_CODE:I = 0x%x" % OLD_C:
                    L[i] = l.replace("0x%x" % OLD_C, "0x%x" % NEW_C); ch = True; ver_n += 1
                if s == '.field static final VERSION_NAME:Ljava/lang/String; = "%s"' % OLD_V:
                    L[i] = l.replace('"%s"' % OLD_V, '"%s"' % NEW_V); ch = True; ver_n += 1
            # the code number: «const/16 vN, 0xc» right after «"code"» or after «->val$code:I» (skipping .line lines) — as build.py checks it
            for i, l in enumerate(L):
                s = l.strip()
                trig = (CS.match(l) and dec(CS.match(l).group(2)) == "code") or s.endswith("->val$code:I")
                if trig:
                    j = i + 1
                    while j < len(L) and (not L[j].strip() or L[j].strip().startswith(".line")):
                        j += 1
                    if j < len(L) and re.match(r"\s*const/16 [vp]\d+, 0x%x$" % OLD_C, L[j]):
                        L[j] = L[j].replace("0x%x" % OLD_C, "0x%x" % NEW_C); ch = True; ver_n += 1
            if ch:
                files[p] = "\n".join(L)
    miss = [k for k, v in hit.items() if not v]
    if miss:
        print("❌ not found (nothing written):\n  " + "\n  ".join(repr(k) for k in miss)); sys.exit(1)
    for p, s in files.items():
        open(p, "w", encoding="utf-8").write(s)
    vj = os.path.join(ROOT, "version.json")
    v = json.load(open(vj, encoding="utf-8")); v["code"], v["name"] = NEW_C, NEW_V
    open(vj, "w", encoding="utf-8").write(json.dumps(v, indent=2, ensure_ascii=False) + "\n")
    print("✅ %d texts in MSA (%d places) · version %s (%d) in %d places · %d files" % (len(T), sum(hit.values()), NEW_V, NEW_C, ver_n, len(files)))


if __name__ == "__main__":
    main()
