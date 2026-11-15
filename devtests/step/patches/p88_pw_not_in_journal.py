# 🔒 patch 88 (dashboard v3.36.53 · the full audit, batch 4 — protection) — with a password set: no /api path answers without a session
#   (79 paths · GET and POST) · a forged session is refused · 8 wrong passwords ⇒ locked for 5 minutes · no wallet key in any answer —
#   all right. One leak: CHANGING the dashboard's password wrote the new password (and the current one) in clear text in the journal
#   («👤 set_pw» with the request — its fields are «new» and «cur», names the journal's secret filter did not know), so it sat in
#   Holy_Journal/*.jsonl, in the 📜 journal window and in the diagnostic zip.
#   ⇒ the two fields are masked before the request is kept for the journal · «new»/«cur» of a set_pw line already written are masked in
#     the files once at start (the line stays, the secret goes)
#   python3 devtests/step/patches/p88_pw_not_in_journal.py Holy_Dashboard.pyw
import os, sys

R = [
    ('''            self._jpost = (path, data)                     # 📜 v3.22.6: كل أمر منك ينكتب بالسجلات ويّا نتيجته (بلا أسرار)''',
     '''            self._jpost = (path, ({**data, **{k: "***" for k in ("new", "cur") if k in data}} if path == "/api/set_pw" else data))   # 📜 v3.22.6: كل أمر منك ينكتب بالسجلات ويّا نتيجته (بلا أسرار) · 🔒 v3.36.53: كلمة السر الجديدة والحالية كانتا تنكتبان بالسجل'''),
    ('''def _jr_clean(v, depth=0):''',
     '''def _jr_scrub_pw():
    """🔒 v3.36.53: سطور «set_pw» المكتوبة قبل هذه النسخة تحمل كلمة السر بنص واضح ⇒ تُحجب بملفات السجل (السطر يبقى) — مرة عند الإقلاع."""
    try:
        for fn in os.listdir(JOURNAL_DIR):
            if not fn.endswith(".jsonl"):
                continue
            fp = os.path.join(JOURNAL_DIR, fn)
            with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                txt = fh.read()
            if "/api/set_pw" not in txt:
                continue
            out, ch = [], False
            for ln in txt.split("\\n"):
                if "/api/set_pw" in ln:
                    try:
                        e = json.loads(ln)
                        rq = (e.get("d") or {}).get("request") if isinstance(e.get("d"), dict) else None
                        if isinstance(rq, dict) and any(rq.get(k) not in (None, "***") for k in ("new", "cur")):
                            for k in ("new", "cur"):
                                if k in rq:
                                    rq[k] = "***"
                            ln, ch = json.dumps(e, ensure_ascii=False), True
                    except Exception:
                        pass
                out.append(ln)
            if ch:
                tmp = fp + ".tmp"
                with open(tmp, "w", encoding="utf-8") as fh:
                    fh.write("\\n".join(out))
                os.replace(tmp, fp)
    except Exception:
        pass


def _jr_clean(v, depth=0):'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:80]!r}"); sys.exit(1)
        s = s.replace(a, b)
    a = 'def journal(cat, msg, lv="info", bot="", sym="", t=None, rl=None, **data):'
    if s.count(a) != 1:
        print("❌ journal anchor"); sys.exit(1)
    s = s.replace(a, "_safe_scrub = _jr_scrub_pw()                          # 🔒 v3.36.53: مرة عند الإقلاع\n\n\n" + a)
    s = s.replace('APP_VERSION = "3.36.52"', 'APP_VERSION = "3.36.53"', 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements + the start scrub · compiles · {p}")
