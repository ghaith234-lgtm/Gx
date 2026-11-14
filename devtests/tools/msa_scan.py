# 🗣️ v3.36.42 (المالك 14-11: «حول المشروع كله عربي فصيح» — كل ما يراه الزبون): يجد النصوص العربية التي يراها الزبون وفيها لهجة
#   الصفحة (نص HTML · قيم الخصائص · نصوص جافاسكربت) + نصوص بايثون (رسائل · تيليغرام · التقارير) — بلا التعليقات وسلاسل التوثيق
#   python3 devtests/tools/msa_scan.py Holy_Dashboard.pyw [--all] [--json out.json]
import io, json, re, sys, tokenize

DIALECT = r"""هسه|هسّه|هسا|هسع|لهسه|ليهسه|شغّال|شغال|شغّالة|شغالة|شغّالين|مطفي|مطفية|مطفّي|ماكو|اكو|أكو|ويّا|ويّاه|ويّاها|ويّاهم|ويّاك|ويا|ليش|شنو|شلون|شكد|اشكد|شگد|هواية|كلش|كلّش|يگول|گال|تگول|يكول|تكول|كال|ما كدر|ما كدرت|ما يكدر|ما تكدر|ما نكدر|ما أكدر|ما اكدر|تكدر|يكدر|نكدر|أكدر|ينضغط|انضغط|سكّر|يسكّر|تسكّر|سكّرت|هذي|هاي|هذولا|هذول|اللي|لسه|لسّه|بس|مو|موب|خوش|خلّي|خلي|يخلي|يخلّي|تخلي|بيه|بيها|بيهم|منو|وين|يسوي|سوّي|تسوي|اسوي|يسوّي|سوّاه|ينسوى|يطلّع|يطلع|تطلع|طلّع|طلعت|طلع|حط|يحط|حطه|ينحط|انحط|نزّله|نزله|يرجّع|ترجّع|رجّع|يرجع|ترجع|رجعت|هيچ|هيج|چان|جان|كاعد|ديروح|يروح|راح|رح|يجي|تجي|اجا|إجا|يصير|صار|صارت|ما يصير|يشوف|تشوف|شوف|ينشاف|يبين|تبين|بيّن|ياخذ|تاخذ|ياخذه|ياخذها|ناخذ|ينكتب|انكتب|ينقرا|انقرا|ينحسب|انحسب|ينحذف|انحذف|ينشال|انشال|انشالت|ينطفي|تنطفي|انطفى|انطفت|يشتغل|تشتغل|اشتغل|يشتغلون|ينضاف|انضاف|ينطي|انطي|نطي|يجيب|ينجاب|يكلك|گلي|كلي|دوّر|يدوّر|ادوّر|لگيت|لكيت|يلگى|لكينا|عشان|علمود|ترا|تره|لعد|مافي|ما بيه|ما بي|اله|الها|الهم|مالته|مالها|مال|مالي|مالك|شي|شويّة|شوية|شوي|بعدين|وبعدين|الحين|اللحين|هنانا|زين|ياريت|يعني|حتى ما|حتى يصير|بالأول|ويّاي|خليه|خليها|ينحفظ|انحفظ|ينحفظت|يتحفظ|ينعاد|انعاد|ينفتح|انفتح|ينسد|انسد|ينسدّ|انسدّت|ينلمس|ينقطع|انقطع|يوصلك|توصلك|يوصله|توصله|نوصل|يصفر|يتصفّر|ينزّل|تنزّل|يحسبها|يحسبه|يعرفه|ينراد|ينسأل|انسأل|ينطلب|انطلب|يتقيّد|ينقيّد|انقيّد|يندفع|ينباع|انباع|انشترى|ينشترى|ينبعت|انبعت|يندز|اندز|دز|يدز|هم|كمان|بعد|لحد|لحدّ|گاع|يمعود|ترى|چم|كم واحد|ما ادري|مدري|عبالك|صدك|خلص|يخلص|خلّص|ينخلص|يكمّل|كمّل|ينحل|انحل|انحلّ|ينسى|ماخذ|ما ياخذ|متروس|كله|كلها|حيل|هواي|بالمرة|بالمرّة|دوم|دايماً|دايم|اوك|أوكي|اوكي"""
DRX = re.compile(r"(?<![ء-ي\w])(" + DIALECT + r")(?![ء-ي\w])")
AR = re.compile(r"[ء-ي]")


def page_segments(text, base_line):
    """(line, kind, segment) for the page: html text · attribute values · js strings (template text) — no js/css comments"""
    out, i, n, line = [], 0, len(text), base_line
    mode = "html"
    def emit(seg, ln, kind):
        if AR.search(seg):
            out.append((ln, kind, seg))
    def advance(j):
        nonlocal line
        line += text.count("\n", i, j)
    while i < n:
        if mode == "html":
            if text.startswith("<script", i):
                j = text.find(">", i) + 1; advance(j); i = j; mode = "js"; continue
            if text.startswith("<style", i):
                j = text.find("</style>", i); j = n if j < 0 else j; advance(j); i = j; continue
            if text.startswith("<!--", i):
                j = text.find("-->", i); j = n if j < 0 else j + 3; advance(j); i = j; continue
            if text[i] == "<":
                j = i + 1
                while j < n and text[j] != ">":
                    if text[j] in "\"'":
                        q = text[j]; k = text.find(q, j + 1); k = n if k < 0 else k
                        emit(text[j + 1:k], line + text.count("\n", i, j), "attr"); j = k
                    j += 1
                advance(j + 1); i = j + 1; continue
            j = text.find("<", i); j = n if j < 0 else j
            emit(text[i:j], line, "html"); advance(j); i = j; continue
        # js
        if text.startswith("</script>", i):
            advance(i + 9); i += 9; mode = "html"; continue
        c = text[i]
        if text.startswith("//", i):
            j = text.find("\n", i); j = n if j < 0 else j; i = j; continue
        if text.startswith("/*", i):
            j = text.find("*/", i); j = n if j < 0 else j + 2; advance(j); i = j; continue
        if c in "'\"":
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            emit(text[i + 1:j], line, "js"); advance(j + 1); i = j + 1; continue
        if c == "`":
            j = i + 1; start = j; depth = 0
            while j < n:
                if text[j] == "\\": j += 2; continue
                if text[j] == "`" and depth == 0: break
                if text.startswith("${", j):
                    emit(text[start:j], line + text.count("\n", i, start), "tpl")
                    d = 1; j += 2
                    while j < n and d:              # the js inside ${ } — strings in it are scanned by a small recursion
                        if text[j] in "'\"":
                            q = text[j]; k = j + 1
                            while k < n and text[k] != q and text[k] != "\n": k += 2 if text[k] == "\\" else 1
                            emit(text[j + 1:k], line + text.count("\n", i, j), "js"); j = k + 1; continue
                        if text[j] == "`":
                            k = j + 1
                            while k < n and text[k] != "`": k += 2 if text[k] == "\\" else 1
                            emit(text[j + 1:k], line + text.count("\n", i, j), "tpl"); j = k + 1; continue
                        if text[j] == "{": d += 1
                        elif text[j] == "}": d -= 1
                        j += 1
                    start = j; continue
                j += 1
            emit(text[start:j], line + text.count("\n", i, start), "tpl"); advance(j + 1); i = j + 1; continue
        if c == "/":                                  # a regex literal (after an operator) — skip it
            k = i - 1
            while k >= 0 and text[k] in " \t": k -= 1
            if k < 0 or text[k] in "(,=:[!&|?{};+-*%<>~^\n":
                j = i + 1
                while j < n and text[j] != "/" and text[j] != "\n":
                    if text[j] == "\\": j += 2; continue
                    if text[j] == "[":
                        while j < n and text[j] != "]": j += 2 if text[j] == "\\" else 1
                    j += 1
                i = j + 1; continue
        i += 1
    return out


def scan(path):
    src = open(path, encoding="utf-8").read()
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    segs = []
    for k, t in enumerate(toks):
        if t.type == getattr(tokenize, "FSTRING_MIDDLE", -9):        # Python 3.12+: the text of an f-string is its own token
            if AR.search(t.string):
                for off, part in enumerate(t.string.split("\n")):
                    if AR.search(part):
                        segs.append((t.start[0] + off, "py", part))
            continue
        if t.type != tokenize.STRING:
            continue
        s = t.string
        body_start = s.find(s.lstrip("rRbBfFuU")[0])
        q = s[body_start:body_start + 3] if s[body_start:body_start + 3] in ('"""', "'''") else s[body_start]
        inner = s[body_start + len(q): len(s) - len(q)]
        line0 = t.start[0]
        prev = toks[k - 1] if k else None
        nxt = toks[k + 1] if k + 1 < len(toks) else None
        if len(inner) > 20000 and ("<script" in inner or "<html" in inner.lower() or "<!DOCTYPE" in inner):
            segs += page_segments(inner, line0)                 # the page / the login page
            continue
        if prev and prev.type in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.NL) and nxt and nxt.type == tokenize.NEWLINE:   # a string alone on a line inside ( … ) ends with NL — it is text, not a docstring
            continue                                            # a docstring — internal
        if AR.search(inner):
            for off, part in enumerate(inner.split("\n")):
                if AR.search(part):
                    segs.append((line0 + off, "py", part))
    return segs


if __name__ == "__main__":
    path = next(a for a in sys.argv[1:] if not a.startswith("--"))
    segs = scan(path)
    allm = "--all" in sys.argv
    hits = [(ln, kd, sg, sorted(set(DRX.findall(sg)))) for ln, kd, sg in segs]
    if not allm:
        hits = [h for h in hits if h[3]]
    if "--json" in sys.argv:
        json.dump([{"line": a, "kind": b, "text": c, "words": d} for a, b, c, d in hits], open(sys.argv[sys.argv.index("--json") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    lines = sorted(set(h[0] for h in hits))
    print(f"{len(segs)} visible Arabic pieces · {len(hits)} with dialect words · on {len(lines)} lines")
    from collections import Counter
    c = Counter(w for h in hits for w in h[3]); print(c.most_common(50))
