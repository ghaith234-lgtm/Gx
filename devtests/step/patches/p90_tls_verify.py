# 🔒 patch 90 (dashboard v3.36.55 · the audit, batch 5) — the dashboard's own connections to OKX and Telegram check the server's
#   certificate. Before: `verify=False` (requests) and `CERT_NONE` + `check_hostname = False` (urllib) — «يتسامح مع جدران الحماية» —
#   so anyone in the middle of the network (a public Wi-Fi, a tampered router) could read the Telegram token (it is in the address of
#   every message) and the OKX key + passphrase headers of the signed calls (balances · the accumulator · the guard), and could feed
#   the dashboard false answers. The bots themselves never did this: their `requests` calls to www.okx.com keep the default check —
#   so on any computer where the bots work, a checked connection works too.
#   · one trusted context `_tls_ctx()`: the system's roots (on Windows that includes the root a security program adds when it scans
#     encrypted traffic) + certifi's (Python builds with no system roots) — for urllib (OKX · Telegram · public files)
#   · requests keeps its default check (certifi). A certificate refused there (a root only the system knows) ⇒ the same call once more
#     through urllib with the system's roots — also for the one-shot order calls (`once=True`), because a refused certificate stops the
#     connection before the request is written, so nothing was sent and nothing can be sent twice
#   · refused by both ⇒ nothing is sent (no key · no token) · one line in the journal (⚙️ النظام, once per 10 min per place) that says
#     what happened and what to do · Telegram's status line says the same
#   python3 devtests/step/patches/p90_tls_verify.py Holy_Dashboard.pyw
import os, sys

TLS = '''import ssl as _ssl2


def _tls_ctx():
    """🔒 v3.36.55: اتصال مشفّر **يتحقّق من شهادة الخادم** — جذور النظام (بويندوز: يشمل جذر برنامج الحماية اللي يفحص الاتصالات المشفّرة)
    + جذور certifi (نسخ بايثون بلا جذور نظام). قبلها كان التحقق مطفأ ⇒ أي وسيط بالشبكة يقرأ توكن تيليغرام ومفتاح OKX."""
    ctx = _ssl2.create_default_context()
    try:
        import certifi as _cf
        ctx.load_verify_locations(_cf.where())
    except Exception:
        pass
    return ctx


def _tls_bad(ex):
    """الخطأ = شهادة الخادم مرفوضة؟ (يحصل وقت المصافحة — قبل ما ينكتب الطلب ⇒ ولا شي انرسل)"""
    seen = 0
    while ex is not None and seen < 8:
        if isinstance(ex, _ssl2.SSLCertVerificationError) or "CERTIFICATE_VERIFY_FAILED" in str(ex):
            return True
        ex = getattr(ex, "reason", None) if isinstance(getattr(ex, "reason", None), BaseException) else (ex.__cause__ or ex.__context__)
        seen += 1
    return False


def _tls_warn(where, host):
    journal("system", f"🔒 لم تُقبل شهادة {where} على هذه الشبكة — لم يُرسل الطلب (حماية لمفاتيحك وتوكن تيليغرام). إذا كان على الحاسوب "
                      f"برنامج حماية يفحص الاتصالات المشفّرة فاستثنِ {host} منه، أو جرّب شبكة أخرى", "warn", rl="tls:" + where)
'''

R = [
    # the OKX context (urllib) — checked
    ('''import ssl as _ssl2
_OKX_CTX = _ssl2.create_default_context()
_OKX_CTX.check_hostname = False
_OKX_CTX.verify_mode = _ssl2.CERT_NONE  # نفس تسامح تيليغرام مع جدران الحماية''',
     TLS + '''

_OKX_CTX = _tls_ctx()                    # 🔒 v3.36.55: كان بلا تحقق من الشهادة'''),
    # requests: its default check (certifi)
    ('''                r = _RQ.get(url, headers=hdr, timeout=timeout, verify=False)
            else:
                hdr.setdefault("Content-Type", "application/json")
                r = _RQ.post(url, headers=hdr, data=json.dumps(payload), timeout=timeout, verify=False)
            return r.json()
        except Exception:
            if once:
                return None''',
     '''                r = _RQ.get(url, headers=hdr, timeout=timeout)
            else:
                hdr.setdefault("Content-Type", "application/json")
                r = _RQ.post(url, headers=hdr, data=json.dumps(payload), timeout=timeout)
            return r.json()
        except Exception as _ex:
            if once and not _tls_bad(_ex):      # 🔒 v3.36.55: شهادة مرفوضة ⇒ الطلب ما انكتب أصلاً ⇒ مرة وحدة بجذور النظام (بلا تكرار)
                return None'''),
    ('''        with urllib.request.urlopen(req, timeout=timeout, context=_OKX_CTX) as rr:
            return json.loads(rr.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read().decode("utf-8"))
        except Exception: return None
    except Exception:
        return None''',
     '''        with urllib.request.urlopen(req, timeout=timeout, context=_OKX_CTX) as rr:
            return json.loads(rr.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read().decode("utf-8"))
        except Exception: return None
    except Exception as _ex:
        if _tls_bad(_ex):
            _tls_warn("OKX", urlparse(url).hostname or "okx.com")
        return None'''),
    # the public files (indicators) — requests' default check
    ('''            r = _RQ.get(url, headers=hdr, timeout=timeout, verify=False)
            return r.content if r.status_code == 200 else None''',
     '''            r = _RQ.get(url, headers=hdr, timeout=timeout)
            return r.content if r.status_code == 200 else None'''),
    # Telegram — checked (the token is in the address of every call)
    ('''_TG_CTX = _ssl.create_default_context()
_TG_CTX.check_hostname = False
_TG_CTX.verify_mode = _ssl.CERT_NONE  # يتسامح مع جدران الحماية/مضادات الفيروسات التي تحقن شهادتها''',
     '''_TG_CTX = _tls_ctx()                     # 🔒 v3.36.55: يتحقّق من الشهادة (كان بلا تحقق ⇒ التوكن مكشوف لأي وسيط بالشبكة)'''),
    ('''    except Exception as ex:
        TG_DIAG["last"] = f"❌ تعذّر الاتصال بتيليغرام: {ex}"
        return False''',
     '''    except Exception as ex:
        if _tls_bad(ex):
            TG_DIAG["last"] = "❌ لم تُقبل شهادة تيليغرام على هذه الشبكة — لم يُرسل شيء (حماية للتوكن)"
            _tls_warn("تيليغرام", "api.telegram.org")
        else:
            TG_DIAG["last"] = f"❌ تعذّر الاتصال بتيليغرام: {ex}"
        return False'''),
    ('''    except Exception as ex:
        return False, f"❌ تعذّر الاتصال بتيليغرام: {type(ex).__name__}"''',
     '''    except Exception as ex:
        if _tls_bad(ex):
            _tls_warn("تيليغرام", "api.telegram.org")
            return False, "❌ لم تُقبل شهادة تيليغرام على هذه الشبكة — لم يُرسل شيء (حماية للتوكن)"
        return False, f"❌ تعذّر الاتصال بتيليغرام: {type(ex).__name__}"'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    for bad in ("verify=False", "CERT_NONE", "check_hostname = False"):
        if bad in s:
            print(f"❌ «{bad}» is still in the file — nothing written"); sys.exit(1)
    s = s.replace('APP_VERSION = "3.36.54"', 'APP_VERSION = "3.36.55"', 1)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · OKX and Telegram connections check the certificate · compiles · {p}")
