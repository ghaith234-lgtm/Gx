# 🔒 v3.36.55 — the dashboard's connections to OKX and Telegram check the server's certificate (p90). Everything on this computer:
#   two HTTPS servers on 127.0.0.1 — «good» (a certificate from a test authority the system trusts here) and «middle» (a certificate
#   it does not: what a man in the middle shows) — they record every request that reaches them. Nothing leaves this computer
#   (any name except localhost is refused before a connection opens).
#   · the signed OKX call reaches the good server with its key · a root only the system knows (requests refuses it) ⇒ the same call
#     once more through urllib — also a one-shot order call, and it arrives exactly once
#   · the middle server receives nothing: no key · no passphrase · no Telegram token · one 🔒 line in the journal (not repeated)
#   · Telegram: the message reaches the good server · not the middle one · its status line says why · the photo call too
#   python3 devtests/t_tls.py [Holy_Dashboard.pyw] [-q]
import datetime as _dt, http.server, importlib.machinery, importlib.util, ipaddress, json, os, shutil, socket, ssl, sys, tempfile, threading
import urllib.request

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1200]}"), flush=True)


try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
except Exception:
    print("⏭️ t_tls: the «cryptography» package is needed to make the test certificates"); sys.exit(0)

# ── nothing but localhost (before the dashboard loads)
_gai = socket.getaddrinfo


def _local_only(host, *a, **k):
    if str(host) not in ("localhost", "127.0.0.1", "::1"):
        raise OSError(f"devtests: no network ({host})")
    return _gai(host, *a, **k)


socket.getaddrinfo = _local_only

R = tempfile.mkdtemp(prefix="t_tls_")
now = _dt.datetime.now(_dt.timezone.utc)


def _key():
    return ec.generate_private_key(ec.SECP256R1())


def _pem(path, obj, key=False):
    with open(path, "wb") as f:
        f.write(obj.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()) if key
                else obj.public_bytes(serialization.Encoding.PEM))


def _cert(subj, pub, issuer, ikey, ca=False, ski_of=None):
    b = (x509.CertificateBuilder().subject_name(subj).issuer_name(issuer).public_key(pub).serial_number(x509.random_serial_number())
         .not_valid_before(now - _dt.timedelta(minutes=5)).not_valid_after(now + _dt.timedelta(days=2))
         .add_extension(x509.SubjectKeyIdentifier.from_public_key(pub), critical=False)
         .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ski_of or pub), critical=False))
    if ca:
        b = (b.add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
             .add_extension(x509.KeyUsage(False, False, False, False, False, True, True, False, False), critical=True))
    else:
        b = (b.add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
             .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]), critical=False)
             .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
             .add_extension(x509.KeyUsage(True, False, False, False, False, False, False, False, False), critical=True))
    return b.sign(ikey, hashes.SHA256())


cak = _key(); can = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Holy devtests CA")])
ca = _cert(can, cak.public_key(), can, cak, ca=True)
sk = _key(); sn = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
good = _cert(sn, sk.public_key(), can, cak, ski_of=cak.public_key())
mk = _key(); mn = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
mid = _cert(mn, mk.public_key(), mn, mk, ca=True)                     # self-signed: nobody here trusts it
P = {n: os.path.join(R, n) for n in ("ca.pem", "good.pem", "good.key", "mid.pem", "mid.key")}
_pem(P["ca.pem"], ca); _pem(P["good.pem"], good); _pem(P["good.key"], sk, key=True); _pem(P["mid.pem"], mid); _pem(P["mid.key"], mk, key=True)

os.environ["SSL_CERT_FILE"] = P["ca.pem"]          # «the system's roots» on this computer = the test authority (urllib)
os.environ.pop("SSL_CERT_DIR", None)
os.environ.pop("REQUESTS_CA_BUNDLE", None)          # requests: certifi only (does not know the test authority) unless a step sets it
os.environ.pop("CURL_CA_BUNDLE", None)


class Rec(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _do(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""
        self.server.log.append({"m": self.command, "p": self.path, "h": dict(self.headers), "b": body.decode("utf-8", "replace")})
        out = json.dumps({"ok": True, "result": {}} if self.path.startswith("/bot") else {"code": "0", "data": [{"echo": self.path}]}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(out)))
        self.end_headers(); self.wfile.write(out)

    do_GET = do_POST = _do


def serve(cert, key):
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Rec)
    c = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); c.load_cert_chain(cert, key)
    s.socket = c.wrap_socket(s.socket, server_side=True); s.log = []
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"https://localhost:{s.server_address[1]}"


G, GU = serve(P["good.pem"], P["good.key"])
M, MU = serve(P["mid.pem"], P["mid.key"])

shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd_tls", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd_tls", ld)); a0 = sys.argv; sys.argv = ["x"]; ld.exec_module(m); sys.argv = a0

src = open(DASH, encoding="utf-8").read()
ok("the source has no unchecked connection left (verify=False · CERT_NONE · check_hostname = False)",
   not any(x in src for x in ("verify=False", "CERT_NONE", "check_hostname = False")))
ok("the OKX and Telegram contexts check the certificate and the name", all(c.verify_mode == ssl.CERT_REQUIRED and c.check_hostname for c in (m._OKX_CTX, m._TG_CTX)))

KEYS = {"OK-ACCESS-KEY": "devtests-KEY-0123456789", "OK-ACCESS-PASSPHRASE": "devtests-PASS-xyz", "OK-ACCESS-SIGN": "c2lnbg==", "OK-ACCESS-TIMESTAMP": "2026-11-15T00:00:00.000Z"}


def jlines():
    out = []
    for f in sorted(os.listdir(m.JOURNAL_DIR)) if os.path.isdir(m.JOURNAL_DIR) else []:
        out += [json.loads(x) for x in open(os.path.join(m.JOURNAL_DIR, f), encoding="utf-8") if x.strip()]
    return out


# 1 · the good server, requests knows its authority ⇒ the signed call arrives (with its key)
os.environ["REQUESTS_CA_BUNDLE"] = P["ca.pem"]
r1 = m._http_json(GU + "/api/v5/account/balance", headers=KEYS)
ok("🟢 a signed OKX call to a server with a trusted certificate works (requests' own check) — the key arrives",
   r1 and r1.get("code") == "0" and len(G.log) == 1 and G.log[0]["h"].get("OK-ACCESS-KEY") == KEYS["OK-ACCESS-KEY"], (r1, G.log))
# 2 · a root only the system knows (a security program's) ⇒ requests refuses it ⇒ urllib with the system's roots — a one-shot order call, once
os.environ.pop("REQUESTS_CA_BUNDLE", None)
G.log.clear()
r2 = m._http_json(GU + "/api/v5/trade/order", headers=KEYS, payload={"instId": "SOL-USDT", "side": "buy", "sz": "1"}, once=True)
ok("🟢 a root only the system knows: the one-shot order call goes once more through the system's roots — and arrives exactly ONCE",
   r2 and r2.get("code") == "0" and [x["m"] for x in G.log] == ["POST"] and '"side": "buy"' in G.log[0]["b"], (r2, G.log))

# 3 · the man in the middle ⇒ nothing reaches it
r3 = m._http_json(MU + "/api/v5/account/balance", headers=KEYS)
r4 = m._http_json(MU + "/api/v5/trade/order", headers=KEYS, payload={"instId": "SOL-USDT", "side": "sell", "sz": "1"}, once=True)
ok("🔴 a certificate nobody trusts (a man in the middle): the balance call and the one-shot order call both stop — nothing returned",
   r3 is None and r4 is None, (r3, r4))
ok("… and the middle server received NOTHING: no key · no passphrase · no order (the connection stops before the request is written)",
   M.log == [], M.log)
j = [e for e in jlines() if e.get("m", "").startswith("🔒")]
ok("… one 🔒 line in the journal (⚙️ النظام · warn) says what happened and what to do — not repeated for the second call",
   len(j) == 1 and j[0]["c"] == "system" and j[0]["lv"] == "warn" and "OKX" in j[0]["m"] and "localhost" in j[0]["m"], j)

# 4 · Telegram: the token is in the address of every call
TOKEN = "123456789:devtests-TELEGRAM-TOKEN-abcdef"
m.dash_cfg = lambda: {"tg_token": TOKEN, "tg_chat_id": "4242"}
m.TG_MUTED["v"] = False
_real = urllib.request.urlopen
TG_TO = {"u": MU}


def _redir(req, *a, **k):                           # api.telegram.org ⇒ one of the two local servers (the dashboard's own context stays)
    u = req.full_url if isinstance(req, urllib.request.Request) else str(req)
    if u.startswith("https://api.telegram.org"):
        n = urllib.request.Request(u.replace("https://api.telegram.org", TG_TO["u"]), data=req.data, headers=dict(req.header_items()), method=req.get_method())
        return _real(n, *a, **k)
    raise OSError("devtests: no network")


urllib.request.urlopen = _redir
s1 = m.tg_send("🔒 devtests — رسالة اختبار")
ok("🔴 Telegram through a man in the middle: not sent · the middle server received nothing (so not the token)",
   s1 is False and M.log == [] and "شهادة" in m.TG_DIAG["last"], (s1, m.TG_DIAG, M.log))
p1 = m.tg_photo(b"\x89PNG devtests", "caption")
ok("… the profit-card photo too: not sent · its message says why", p1[0] is False and "شهادة" in p1[1] and M.log == [], (p1, M.log))
TG_TO["u"] = GU
G.log.clear()
s2 = m.tg_send("🔒 devtests — رسالة اختبار ٢")
ok("🟢 Telegram to a server with a trusted certificate: sent (the checked connection works)",
   s2 is True and len(G.log) == 1 and G.log[0]["p"] == f"/bot{TOKEN}/sendMessage" and m.TG_DIAG["last"].startswith("✅"), (s2, m.TG_DIAG, G.log))
urllib.request.urlopen = _real

jt = [e for e in jlines() if e.get("m", "").startswith("🔒")]
ok("… one 🔒 line for Telegram as well (the message and the photo together = one line)", sum("شهادة تيليغرام" in e["m"] for e in jt) == 1 and len(jt) == 2, jt)
allj = json.dumps(jlines(), ensure_ascii=False)
ok("the journal holds no key, passphrase or token", not any(x in allj for x in (TOKEN, KEYS["OK-ACCESS-KEY"], KEYS["OK-ACCESS-PASSPHRASE"])))

G.shutdown(); M.shutdown()
print(f"✅ t_tls: {sum(res)}/{len(res)}" if all(res) else f"❌ t_tls: {sum(res)}/{len(res)}")
shutil.rmtree(R, ignore_errors=True)
sys.exit(0 if all(res) else 1)
