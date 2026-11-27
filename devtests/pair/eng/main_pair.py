# -*- coding: utf-8 -*-
# 🔀 شبكة عملتين (Two-Coin Grid) — محرك جديد مبني على طبقة الحماية نفسها من 🪜/♾️ · اللوحة تنشره بمجلد البوت باسم main.py
"""
═══════════════════════════════════════════════════════════════
  The Holy Two-Coin Grid — شبكة عملتين
═══════════════════════════════════════════════════════════════
  • عملة رئيسية (MAIN · مثل XRP) تلعب دور الدولار، وعملة ثانية (OTHER · مثل SOL) تُتداول على سعرها محسوباً بالرئيسية:
    النسبة R = سعر OTHER ÷ سعر MAIN (كم MAIN تساوي OTHER واحدة)
  • مستوى j: نسبة الشراء bp = R0 × (1+g)^j · نسبة البيع sp = bp × (1+g)   (g = grid_percentage)
  • كل شراء تحت = نفس كمية الرئيسية (main_value) — مثل ♾️: كل شراء نفس الدولار · بيعته = نفس كمية الثانية المشتراة بنسبة أعلى بـg
  • فوق البداية: up_levels مستوى يبيع من عملات المحفظة الثانية «كأنها اشتُريت» بنسبتها · تحت البداية: down_levels شراء
  • الربح بالرئيسية (profit_to = main) — أو بالثانية (other) — أو نصفان (half)
  • ⛔ لا أوامر قاعدة على المنصة: البوت يحفظ «الأمرين التاليين» (الشراء الأقرب تحت والبيع الأقرب فوق) ويراقب النسبة كل ثانيتين
  • التبديل = رجلان بنفس اللحظة عبر الدولار (BRIDGE · USDT): بيع ← دولار ← شراء · كل رجل أمر محدد فوري (IOC) بسقف سعر
    (slip_cap) ⇒ القفزة المفاجئة ما تعطي سعراً سيئاً · ينفّذ جزئياً ⇒ يكمل الباقي بسعر جديد
  • 💵 دولار التبديل محجوز للبوت (usd_booked بالحالة) من لحظة تنفيذ الرجل الأول حتى يُصرف بالرجل الثاني · رُفض ⇒ يعيد ولا يتركه
  • لا يُغلق شراء إلا بربح بعد العمولات الأربع حتى بأسوأ سعر يسمح به السقف
  الحماية من ♾️/🪜 كما هي: حفظ ذري + fsync للملف والمجلد · نسخ احتياطية · ضغطات اللوحة ما تضيع · كل أمر يُقيَّد بالدفتر **قبل** إرساله
  بمعرّف ثابت (ردّ ضاع ⇒ نسأل المنصة بالمعرّف) · كل تبديل يُغلق بحفظة واحدة (مرة واحدة فقط) · أسطر السجل مرة واحدة
═══════════════════════════════════════════════════════════════
"""
import okx.Trade as Trade
import okx.MarketData as Market
import time
import json
import os
import requests
import hmac
import base64
import shutil
import glob
import socket
import math
import hashlib
import sys
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_UP
from datetime import datetime, timezone

socket.setdefaulttimeout(10)

ENGINE_KIND = "grid_pair"
SEND_WAIT = 120.0          # ثواني: أمر ضاع ردّه والمنصة ما تعرفه بعدها ⇒ ما وصلها (رجله ينرسل من جديد)
LOOP_S = 2.0               # فحص النسبة كل ثانيتين
MAX_OPS = 6                # أقصى تبديلات بالدورة الواحدة (كل واحد بأسعار جديدة)
CAP_DEF = 0.002            # سقف سعر الرجل الأول (البيع): أسوأ من السعر بـ0.2% أكثر شي
CAP_B_DEF = 0.0005         # سقف الرجل الثاني (الشراء بالدولار) ضيّق: كميته = الدولار ÷ سعر السقف ⇒ الباقي كسور (0.05%) · ما نفّذ ⇒ يعيد بسعر جديد
RETRY = (2, 5, 10, 20, 30, 60)
CLOSE_WAIT = 600.0         # بيعة رجلها الثاني صار بخسارة (قفزة بين الرجلين) ⇒ ينتظر سعراً أحسن حتى 10 دقائق ثم يكمل
HIST_N = 300


# ================= 🛡️ الذاكرة الفولاذية والملفات (من 🪜/♾️ كما هي) =================
def load_json(file_path):
    if os.path.exists(file_path):
        for _ in range(5):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                time.sleep(0.1)
    return None


_CTL_KEYS = ("pause_buy", "pause_sell", "buy_floor", "sell_ceiling", "status", "self_destruct")
_CTL = {"sig": None, "seen": None}


def _ctl_sig(p):
    try:
        _s = os.stat(p)
        return (_s.st_mtime_ns, _s.st_size)
    except Exception:
        return None


def _ctl_note(d, sig):
    try:
        _CTL["seen"] = {k: d.get(k) for k in _CTL_KEYS}
        _CTL["sig"] = sig
    except Exception:
        pass


def _ctl_merge(file_path, data):
    """🔐 ضغطة اللوحة ما تضيع: ملف الحالة تغيّر من برّا ⇒ حقول التحكم اللي غيّرتها اللوحة تنأخذ قبل ما نكتب فوقها."""
    if _CTL["seen"] is None:
        return
    sig = _ctl_sig(file_path)
    if sig is None or sig == _CTL["sig"]:
        return
    disk = load_json(file_path)
    if not isinstance(disk, dict):
        return
    for k in _CTL_KEYS:
        if k in disk and disk.get(k) != _CTL["seen"].get(k):
            data[k] = disk.get(k)


def _dir_sync(file_path):
    """🔌 تثبيت إعادة التسمية بالقرص (fsync للمجلد) — انقطاع الكهرباء ما يرجّع الملف لنسخة قديمة."""
    if os.name == "nt":
        return
    try:
        _fd = os.open(os.path.dirname(os.path.abspath(file_path)) or ".", os.O_RDONLY)
        try:
            os.fsync(_fd)
        finally:
            os.close(_fd)
    except Exception:
        pass


def save_json(file_path, data):
    _is_st = isinstance(data, dict) and file_path == globals().get("STATE_FILE")
    if _is_st:
        try:
            _ctl_merge(file_path, data)
        except Exception:
            pass
        try:
            _views(data)                      # 🔀 الأمران التاليان والدفاتر للوحة — مشتقة من الخانات بنفس الحفظة
        except Exception:
            pass
    temp_file = file_path + ".tmp"
    for _ in range(5):
        try:
            with open(temp_file, 'w') as f:
                f.write(json.dumps(data, separators=(",", ":")))     # مضغوط · dumps = المشفّر السريع (dump يمشي بالبطيء) — نفس البايتات
                f.flush()
                os.fsync(f.fileno())
            _sig_w = _ctl_sig(temp_file) if _is_st else None
            os.replace(temp_file, file_path)
            if _is_st:
                _dir_sync(file_path)
                _ctl_note(data, _sig_w)
                SAVED["t"] = time.time()
            return True
        except PermissionError:
            time.sleep(0.1)
    return False


SAVED = {"t": 0.0}


def log_trade_history(symbol, message):
    try:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {"time": now_str, "msg": message}
        file_path = os.path.join(os.getcwd(), f"trade_history_{symbol.split('-')[0]}.json")
        data = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except Exception:
                    try:
                        shutil.copy2(file_path, file_path + ".bad")
                    except Exception:
                        pass
        if not isinstance(data, list):
            data = []
        data.insert(0, log_entry)
        data = data[:1000]
        _txt = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        _tmp = file_path + ".tmp"
        for _ in range(5):
            try:
                with open(_tmp, 'w', encoding='utf-8') as f:
                    f.write(_txt)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(_tmp, file_path)
                return
            except PermissionError:
                time.sleep(0.1)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(_txt)
    except Exception:
        pass


def backup_state(state_file, backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    if os.path.exists(state_file):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        shutil.copy2(state_file, os.path.join(backup_dir, f"grid_state_{timestamp}.json"))
        try:                                   # آخر 30 نسخة تكفي
            for _old in sorted(glob.glob(os.path.join(backup_dir, "grid_state_*.json")))[:-30]:
                os.remove(_old)
        except Exception:
            pass


def load_state_with_backup():
    st = load_json(STATE_FILE)
    if st is not None:
        return st
    try:
        for b in reversed(sorted(glob.glob(os.path.join(BACKUP_DIR, "grid_state_*.json")))):
            st = load_json(b)
            if st is not None:
                log_trade_history(SYMBOL, f"🛟 [استرجاع طارئ] ملف الحالة كان تالفاً، استُرجع من النسخة الاحتياطية: {os.path.basename(b)}")
                return st
    except Exception:
        pass
    return None


print("=== 🔀 The Holy Two-Coin Grid ===")

existing_configs = glob.glob("config_*.json")
if existing_configs:
    CONFIG_FILE = existing_configs[0]
    SYMBOL = CONFIG_FILE.replace("config_", "").replace(".json", "")
    config = load_json(CONFIG_FILE)
    IS_NEW_SETUP = False
else:
    SYMBOL = input("Enter the pair OTHER-MAIN for FIRST TIME SETUP (e.g., SOL-XRP): ").upper()
    CONFIG_FILE = f"config_{SYMBOL}.json"
    config = None
    IS_NEW_SETUP = True

if config and "bot_id" in config:
    BOT_ID = config["bot_id"]
else:
    BOT_ID = "HB" + hashlib.md5(os.path.abspath(os.getcwd()).encode('utf-8')).hexdigest()[:10].upper()
    if config:
        config["bot_id"] = BOT_ID
        save_json(CONFIG_FILE, config)


def prevent_duplicate_run(bot_id):
    port = 50000 + int(hashlib.md5(bot_id.encode('utf-8')).hexdigest(), 16) % 10000
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', port))
        return s
    except socket.error:
        print(f"\n❌ [CRITICAL ERROR] BOT {bot_id} IS ALREADY RUNNING!")
        time.sleep(5)
        sys.exit(0)


global_lock_socket = prevent_duplicate_run(BOT_ID)
STATE_FILE = f"grid_state_{SYMBOL}.json"
BACKUP_DIR = f"backups_{SYMBOL}"

if not config and IS_NEW_SETUP:
    config = {
        "api_key": input("API Key: "), "secret_key": input("Secret Key: "), "passphrase": input("Passphrase: "),
        "symbol": SYMBOL, "bot_type": ENGINE_KIND, "bridge": "USDT",
        "main_value": float(input("Main coin per buy (e.g. 20 XRP): ")),
        "grid_percentage": float(input("Step % (e.g. 2): ")) / 100,
        "down_levels": int(input("Buy levels below the start: ") or 0),
        "up_levels": int(input("Sell levels above the start from your coins: ") or 0),
        "profit_to": (input("Profit to: main / other / half [main]: ").strip() or "main"),
        "forced_base_ratio": float(input("Start ratio (empty = market): ").strip() or 0.0),
        "fee_rate": 0.001, "slip_cap": CAP_DEF, "is_demo": False, "bot_id": BOT_ID,
    }
    save_json(CONFIG_FILE, config)

OTHER, MAIN = SYMBOL.split("-")[:2]
BRIDGE = str(config.get("bridge") or "USDT")
INST_O, INST_M = f"{OTHER}-{BRIDGE}", f"{MAIN}-{BRIDGE}"

FLAG = '0'
trade_api = Trade.TradeAPI(config["api_key"], config["secret_key"], config["passphrase"], False, FLAG)
market_api = Market.MarketAPI(flag=FLAG)

SPEC = {INST_O: {"loaded": False}, INST_M: {"loaded": False}}
SPEC_LOG = {"t": 0.0}


def load_instrument_spec(inst):
    """مواصفات العملة من OKX (خطوة السعر · خطوة الكمية · أدنى حجم) — بلاها البوت ما يولد ولا يضع أي أمر (مثل 🪜 F11)"""
    sp = SPEC.setdefault(inst, {"loaded": False})
    if sp.get("loaded"):
        return True

    def _pub():
        import okx.PublicData as _PD
        return _PD.PublicAPI(flag=FLAG).get_instruments(instType="SPOT", instId=inst)
    ways = ([lambda: market_api.get_instruments(instType="SPOT", instId=inst)] if hasattr(market_api, "get_instruments") else []) + [
        _pub, lambda: requests.get(f"https://www.okx.com/api/v5/public/instruments?instType=SPOT&instId={inst}", timeout=8).json()]
    why = ""
    for way in ways:
        try:
            r = way()
            if r and str(r.get("code")) == "0" and r.get("data"):
                d = r["data"][0]
                sp.update(tickSz=float(d.get("tickSz") or 0) or None, lotSz=float(d.get("lotSz") or 0) or None,
                          minSz=float(d.get("minSz") or 0) or None, loaded=True)
                return True
            why = str((r or {}).get("msg") or (r or {}).get("code") or "رد فارغ")
        except Exception as e:
            why = f"{type(e).__name__}"
    if time.time() - SPEC_LOG["t"] > 600:
        SPEC_LOG["t"] = time.time()
        log_trade_history(SYMBOL, f"⏳ [شبكة عملتين] تعذّر جلب مواصفات {inst} من المنصة ({why[:60]}) — ينتظر ولا يضع أي أمر")
    return False


def _dec(x):
    return Decimal(repr(float(x)))


def _step_round(v, step, mode):
    if not step or step <= 0:
        return float(v)
    st = Decimal(str(step))
    return float((_dec(v) / st).quantize(Decimal(1), rounding=mode) * st)


def _num_str(v, step):
    """الرقم كنص مضاعف بالضبط لخطوة المنصة (بلا ضجيج عشري ولا صيغة علمية)"""
    try:
        if step and step > 0:
            st = Decimal(str(step))
            out = format((_dec(v) / st).quantize(Decimal(1), rounding=ROUND_HALF_UP) * st, "f")
        else:
            out = format(_dec(round(float(v), 10)), "f")
        return (out.rstrip("0").rstrip(".") if "." in out else out) or "0"
    except Exception:
        return str(v)


def _sz_str(q, inst):
    return _num_str(q, SPEC[inst].get("lotSz"))


def _px_str(p, inst):
    return _num_str(p, SPEC[inst].get("tickSz"))


def _px_round(p, inst, up=False):
    t = SPEC[inst].get("tickSz")
    if not t:
        return float("%.6g" % float(p))
    return _step_round(p, t, ROUND_CEILING if up else ROUND_FLOOR)


def _lot_floor(q, inst):
    lot = SPEC[inst].get("lotSz") or 1e-6
    return max(0.0, _step_round(float(q) + 1e-12, lot, ROUND_FLOOR))


def fmt_qty(qty, inst):
    """الكمية على خطوة OKX (لتحت) — أصغر من الحد الأدنى ⇒ 0 (ما تنرسل)"""
    q = _lot_floor(qty, inst)
    mn = SPEC[inst].get("minSz")
    if mn and q < mn - 1e-12:
        return 0.0
    return q


def _n(x, nd=10):
    """🔢 رقم بالسجل عشري عادي بلا صيغة علمية"""
    try:
        s = format(Decimal(repr(round(float(x), nd))), "f")
    except Exception:
        return str(x)
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def _b36(n):
    s, n = "", int(n)
    while True:
        n, r = divmod(n, 36)
        s = "0123456789abcdefghijklmnopqrstuvwxyz"[r] + s
        if not n:
            return s


# ================= 🌐 المنصة =================
NET_STATE = {"online": True, "fails": 0, "since": 0.0}


def _net_mark(ok):
    if ok:
        if not NET_STATE["online"]:
            down = time.time() - NET_STATE["since"]
            log_trade_history(SYMBOL, f"🌐 عاد الاتصال بعد {int(down)} ثانية — مزامنة مع المنصة قبل أي أمر")
        NET_STATE["online"] = True
        NET_STATE["fails"] = 0
    else:
        NET_STATE["fails"] += 1
        if NET_STATE["online"] and NET_STATE["fails"] >= 3:
            NET_STATE["online"] = False
            NET_STATE["since"] = time.time()
            try:
                log_trade_history(SYMBOL, "🔌 انقطع الاتصال بالمنصة — توقّف إرسال الأوامر الجديدة حتى يعود")
            except Exception:
                pass


def get_quote(inst):
    """(أفضل شراء · أفضل بيع · آخر سعر) — None إذا ما وصلنا"""
    def _q(d):
        last = float(d.get("last") or 0)
        bid = float(d.get("bidPx") or 0) or last
        ask = float(d.get("askPx") or 0) or last
        return (bid, ask, last) if bid > 0 and ask > 0 and last > 0 else None
    try:
        q = _q(market_api.get_ticker(inst)['data'][0])
        if q:
            _net_mark(True)
            return q
    except Exception:
        pass
    try:
        import urllib.request
        with urllib.request.urlopen(f"https://www.okx.com/api/v5/market/ticker?instId={inst}", timeout=6) as resp:
            q = _q(json.loads(resp.read().decode("utf-8"))["data"][0])
            if q:
                _net_mark(True)
                return q
    except Exception:
        pass
    _net_mark(False)
    return None


def _signed_get(endpoint):
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    mac = hmac.new(bytes(config["secret_key"], encoding='utf8'), bytes(timestamp + "GET" + endpoint, encoding='utf8'), digestmod='sha256')
    headers = {"OK-ACCESS-KEY": config["api_key"], "OK-ACCESS-SIGN": base64.b64encode(mac.digest()).decode('utf-8'),
               "OK-ACCESS-TIMESTAMP": timestamp, "OK-ACCESS-PASSPHRASE": config["passphrase"], "Content-Type": "application/json"}
    return requests.get("https://www.okx.com" + endpoint, headers=headers, timeout=5).json()


def _check(leg):
    """أمر الرجل بمعرّفنا (clOrdId): بيانات الأمر · {} = المنصة ما تعرفه · None = ما وصلنا (نعيد بعدين)"""
    try:
        if leg.get("id"):
            r = _signed_get(f"/api/v5/trade/order?instId={leg['inst']}&ordId={leg['id']}")
        else:
            r = _signed_get(f"/api/v5/trade/order?instId={leg['inst']}&clOrdId={leg['cl']}")
        if str(r.get("code")) == "0" and r.get("data"):
            _net_mark(True)
            return r["data"][0]
        if str(r.get("code")) == "51603":
            return {}
    except Exception:
        _net_mark(False)
    return None


_AMBIG = ("50001", "50004", "50013", "50026")


def _rejected(order):
    """رفض **أكيد** (الأمر ما انفّذ)؟ مهلة/انشغال/خطأ نظام أو رد مجهول = مبهم (ممكن وصل) ⇒ ينحسم بالسؤال بمعرّفنا."""
    try:
        c = str((order or {}).get("code") or "")
        sc = str((((order or {}).get("data") or [{}])[0] or {}).get("sCode") or "")
    except Exception:
        return False
    if c in ("1", "2"):
        return sc not in _AMBIG
    return c.startswith("51") or c.startswith("501") or c in ("50000", "50002", "50006", "50011", "50014", "50015", "50016")


def _rej_code(order):
    try:
        d0 = (order.get("data") or [{}])[0] or {}
        return str(d0.get("sCode") or order.get("code") or ""), str(d0.get("sMsg") or order.get("msg") or "")
    except Exception:
        return "", ""


def balance_direct(ccy, zero_ok=False):
    """الرصيد المتاح لعملة · None = ما وصلنا · zero_ok: رد سليم والعملة مخفية = صفر"""
    try:
        r = _signed_get(f"/api/v5/account/balance?ccy={ccy}")
        for d in ((r.get("data") or [{}])[0].get("details") or []):
            if str(d.get("ccy")) == ccy:
                return float(d.get("availBal") or 0)
        if zero_ok and str(r.get("code")) == "0" and isinstance(r.get("data"), list) and r.get("data"):
            return 0.0
    except Exception:
        pass
    return None


# ================= 🧾 أسطر السجل مرة واحدة (من ♾️/🪜) =================
def _fx_hist(symbol):
    try:
        hp = os.path.join(os.getcwd(), f"trade_history_{str(symbol).split('-')[0]}.json")
        d = load_json(hp) if os.path.exists(hp) else []
        return d if isinstance(d, list) else []
    except Exception:
        return None


def _fx_hist_top(symbol):
    d = _fx_hist(symbol)
    e = (d or [None])[0]
    return [str(e.get("time") or ""), str(e.get("msg") or "")] if isinstance(e, dict) else None


def _fx_log_flush(state):
    """أسطر تنفيذ انحفظت مع الحالة ثم صار انقطاع: مكتوبة بالسجل (فوق علامة الحفظة) ⇒ ما تنعاد · مو مكتوبة ⇒ تنكتب."""
    L = state.get("fx_log")
    if not L:
        return
    lines = [(str(a), str(b)) for a, b in (L.get("lines") or []) if a and b]
    if lines:
        data = _fx_hist(lines[0][0])
        if data is None:
            return
        top = L.get("top")
        k = next((i for i, e in enumerate(data) if isinstance(e, dict) and top and [str(e.get("time") or ""), str(e.get("msg") or "")] == list(top)),
                 len(data))
        rec = [str(e.get("msg") or "") for e in data[:k] if isinstance(e, dict)][::-1]
        ms = [m_ for _, m_ in lines]
        done = next(p for p in range(len(ms), -1, -1)
                    if p == 0 or any(rec[i:i + p] == ms[:p] for i in range(len(rec) - p + 1)))
        for s_, m_ in lines[done:]:
            log_trade_history(s_, m_)
    state.pop("fx_log", None)


def _commit(state, lines):
    """🧾 حفظة واحدة: تغيير الخانة + الربح + أسطر سجلها · بعدين الأسطر تنكتب بالسجل (انقطاع بينهم ⇒ _fx_log_flush)."""
    if lines:
        state["fx_log"] = {"top": _fx_hist_top(SYMBOL), "lines": [[SYMBOL, m] for m in lines]}
    ok = save_json(STATE_FILE, state)
    if ok is True and lines:
        for m in lines:
            log_trade_history(SYMBOL, m)
        state.pop("fx_log", None)
    return ok is True


# ================= 🔀 الإعداد والمستويات =================
def _f(x, d=0.0):
    try:
        v = float(x)
        return v if math.isfinite(v) else d
    except Exception:
        return d


def _cfg():
    """الإعداد المستعمل للولادة (ينحفظ بالحالة ⇒ تعديل الإعداد بعدين ما يغيّر الخانات)"""
    g = _f(config.get("grid_percentage"))
    mv = _f(config.get("main_value"))
    dn = int(_f(config.get("down_levels")))
    up = int(_f(config.get("up_levels")))
    fee = _f(config.get("fee_rate"), 0.001)
    cap = _f(config.get("slip_cap"), CAP_DEF)
    capb = min(cap, _f(config.get("slip_cap_b"), CAP_B_DEF))
    pt = str(config.get("profit_to") or "main")
    return {"g": g, "mv": mv, "dn": dn, "up": up, "fee": fee, "cap": cap, "capb": capb, "pt": pt if pt in ("main", "other", "half") else "main",
            "r0": _f(config.get("forced_base_ratio"))}


def cycle_factor(g, fee, cap):
    """ما يرجع من كل وحدة رئيسية بعد دورة كاملة (4 أوامر) بأسوأ سعر يسمح به السقف — لازم > 1 وإلا ما يولد"""
    return (1 + g) * (1 - fee) ** 4 * ((1 - cap) / (1 + cap)) ** 2


def _cfg_ok(c):
    if not (c["g"] > 0 and c["mv"] > 0 and c["dn"] >= 0 and c["up"] >= 0 and c["dn"] + c["up"] > 0 and 0 <= c["fee"] < 0.05 and 0 <= c["cap"] < 0.05):
        return "إعداد غير صالح (تأكد من الأرقام)"
    if c["dn"] + c["up"] > 2000:
        return "عدد المستويات أكبر من 2000"
    if cycle_factor(c["g"], c["fee"], c["cap"]) <= 1.0:
        return f"الخطوة {c['g'] * 100:.2f}% لا تغطي العمولات الأربع وسقف السعر"
    return ""


def _slots(state):
    return state.setdefault("slots", {})


def _key(j):
    return str(int(j))


def _born(state):
    """الولادة مرة وحدة: المستويات من النسبة الأولى — الشراءات تحت والبيعات فوق من عملات المحفظة «كأنها اشتُريت» بنسبتها"""
    if not (load_instrument_spec(INST_O) and load_instrument_spec(INST_M)):   # 📐 بكل إقلاع قبل أي أمر (درس 🪜 F11)
        return False
    if state.get("pair"):
        return True
    c = _cfg()
    why = _cfg_ok(c)
    if why:
        if time.time() - float(state.get("last_cfg_log") or 0) > 600:
            state["last_cfg_log"] = time.time()
            log_trade_history(SYMBOL, f"⛔ [شبكة عملتين] {why} — البوت لا يبدأ ولا يضع أي أمر")
            save_json(STATE_FILE, state)
        return False
    r0 = c["r0"]
    if r0 <= 0:
        qo, qm = get_quote(INST_O), get_quote(INST_M)
        if not qo or not qm:
            return False
        r0 = qo[2] / qm[2]
    S = {}
    for j in range(-c["dn"], c["up"]):
        bp = r0 * (1 + c["g"]) ** j
        s = {"j": j, "bp": round(bp, 12), "sp": round(bp * (1 + c["g"]), 12), "side": "buy", "q": 0.0, "c": 0.0, "dq": 0.0, "n": 0, "cyc": 0}
        if j >= 0:
            s.update(side="sell", q=round(c["mv"] / bp, 12), c=round(c["mv"], 12), wallet=True)
        S[_key(j)] = s
    state["pair"] = {"other": OTHER, "main": MAIN, "bridge": BRIDGE, "r0": r0, **c, "born": time.time()}
    state["slots"] = S
    state.setdefault("total_profit", 0.0)            # بالعملة الرئيسية
    state.setdefault("profit_other", 0.0)            # بالعملة الثانية (profit_to = other / half)
    state.setdefault("usd_dust", 0.0)
    state["main_book"] = round(c["dn"] * c["mv"], 12)  # الرئيسية الحرة للبوت (للشراءات)
    state["main_start"] = state["main_book"]
    state["other_start"] = round(sum(s["q"] for s in S.values()), 12)
    log_trade_history(SYMBOL, f"🚀 [شبكة عملتين] بدأ {OTHER} مقابل {MAIN}: النسبة {_n(r0)} · الخطوة {_n(c['g'] * 100)}% · "
                              f"كل شراء {_n(c['mv'])} {MAIN} · {c['dn']} مستوى تحت · {c['up']} مستوى فوق من محفظتك")
    save_json(STATE_FILE, state)
    return True


def _views(st):
    """للوحة: الأمران التاليان · الدفاتر · الدولار المحجوز — مشتقة من الخانات (المحرك ما يقراها)"""
    S = st.get("slots") or {}
    if not S:
        return
    bf, sc = _f(st.get("buy_floor")), _f(st.get("sell_ceiling"))
    buys = [s for s in S.values() if s.get("side") == "buy" and not (bf > 0 and s["bp"] < bf - 1e-15)]
    sells = [s for s in S.values() if s.get("side") == "sell" and not (sc > 0 and s["sp"] > sc + 1e-15)]
    nb = max(buys, key=lambda s: s["bp"], default=None)
    ns = min(sells, key=lambda s: s["sp"], default=None)
    pr = st.get("pair") or {}
    st["next_buy"] = {"j": nb["j"], "ratio": nb["bp"], "main": pr.get("mv")} if nb else None
    st["next_sell"] = {"j": ns["j"], "ratio": ns["sp"], "qty": round(ns["q"] + ns.get("dq", 0.0), 12)} if ns else None
    st["n_buy"] = sum(1 for s in S.values() if s.get("side") == "buy")
    st["n_sell"] = sum(1 for s in S.values() if s.get("side") == "sell")
    op = st.get("op") or {}
    st["usd_booked"] = round(_f(st.get("usd_dust")) + (_f(op.get("usd")) if op else 0.0), 10)
    st["other_book"] = round(sum(s.get("q", 0.0) + s.get("dq", 0.0) for s in S.values()) + _f(st.get("profit_other")), 12)


# ================= 🔀 التبديل: رجلان عبر الدولار =================
def _quotes():
    qo, qm = get_quote(INST_O), get_quote(INST_M)
    if not qo or not qm:
        return None
    return {"o": qo, "m": qm, "r_buy": qo[1] / qm[0], "r_sell": qo[0] / qm[1], "r": qo[2] / qm[2]}


def _seq(state):
    seq = int(state.get("seq") or 0) + 1
    state["seq"] = seq
    return seq


def _leg(state, inst, side, sz, px):
    seq = _seq(state)
    cl = f"{BOT_ID}{'x' if side == 'sell' else 'y'}{_b36(seq)}"[:32]
    return {"cl": cl, "inst": inst, "side": side, "sz": sz, "px": px, "st": "send", "ts": time.time()}


def _place(leg):
    """يرسل الرجل · True = وصل وله رقم · False = رفض أكيد (الرجل ألغي) · None = رد مبهم (ينحسم بالسؤال بالمعرّف)"""
    try:
        r = trade_api.place_order(instId=leg["inst"], tdMode='cash', side=leg["side"], ordType='ioc', sz=_sz_str(leg["sz"], leg["inst"]),
                                  px=_px_str(leg["px"], leg["inst"]), clOrdId=leg["cl"])
    except Exception:
        _net_mark(False)
        return None, None
    if str(r.get("code")) == "0" and ((r.get("data") or [{}])[0] or {}).get("ordId"):
        _net_mark(True)
        leg.update(id=str(r["data"][0]["ordId"]), st="live")
        return True, r
    if _rejected(r):
        _net_mark(True)
        return False, r
    return None, r


def _final(d):
    return str((d or {}).get("state") or "") in ("filled", "canceled", "mmp_canceled")


def _fill_of(d, leg):
    """(الكمية المنفذة · متوسط السعر · العمولة بالعملة المستلمة) — عمولة بعملة ثالثة (OKB) ما تنقص المستلم"""
    acc = _f(d.get("accFillSz"))
    avg = _f(d.get("avgPx"))
    fee = abs(_f(d.get("fee")))
    fccy = str(d.get("feeCcy") or "")
    base, quote = leg["inst"].split("-")
    if leg["side"] == "sell":
        return acc, avg, (fee if fccy == quote else 0.0)
    return acc, avg, (fee if fccy == base else 0.0)


def _resolve(state, op, name):
    """رجل معلّق (بالطريق أو حي): نسأل المنصة · True = انحسم وتطبّق · False = ننتظر"""
    leg = op.get(name)
    if not leg or leg.get("st") == "done":
        return True
    d = _check(leg)
    if d is None:
        return False
    if d == {}:
        if leg.get("id"):                                    # له رقم والمنصة تقول ما تعرفه ⇒ نتأكد مرات قبل ما نعتبره ما انفّذ
            leg["gone"] = int(leg.get("gone") or 0) + 1
            if leg["gone"] < 10:
                save_json(STATE_FILE, state)
                return False
            log_trade_history(SYMBOL, f"⚠️ [تبديل] المنصة لا تعرف الأمر {leg['id']} بعد 10 محاولات — يُعتبر غير منفّذ")
            op[name] = None
            save_json(STATE_FILE, state)
            return True
        if time.time() - _f(leg.get("ts")) >= SEND_WAIT:
            op[name] = None                                  # ما وصل المنصة ⇒ ينرسل من جديد (معرّف جديد)
            save_json(STATE_FILE, state)
            return True
        return False
    if not leg.get("id") and d.get("ordId"):
        leg["id"] = str(d.get("ordId"))
        leg["st"] = "live"
    if not _final(d):
        save_json(STATE_FILE, state)
        return False
    _apply(state, op, name, d)
    return True


def _apply(state, op, name, d):
    """رجل خلص ⇒ يتسجّل بالتبديل بحفظة وحدة (بعدها الرجل ما يشير لأمر ⇒ ما ينحسب مرتين)"""
    leg = op[name]
    acc, avg, fee = _fill_of(d, leg)
    leg.update(st="done", acc=acc, avg=avg, fee=fee)
    if name == "a":
        op["sold"] = round(_f(op.get("sold")) + acc, 12)
        op["usd"] = round(_f(op.get("usd")) + acc * avg - fee, 10)
    else:
        op["got"] = round(_f(op.get("got")) + acc - fee, 12)
        op["usd"] = round(_f(op.get("usd")) - acc * avg, 10)
        op.setdefault("bl", []).append({"cl": leg["cl"], "acc": acc, "avg": avg, "fee": fee})
        op["b"] = None
        if acc > 0:
            op["tries"] = 0
    save_json(STATE_FILE, state)


def _start_op(state, key, s, kind, Q):
    """تبديل جديد: الرجل الأول ينقيّد قبل الإرسال · الرصيد يتأكد قبله (ما نرسل أمراً بلا عملة)"""
    pr = state["pair"]
    cap = pr["cap"]
    if kind == "buy":                                         # الرئيسية ⇒ الثانية: بيع MAIN
        inst, side = INST_M, "sell"
        sz = fmt_qty(min(pr["mv"], _f(state.get("main_book"))), INST_M)
        px = _px_round(Q["m"][0] * (1 - cap), INST_M, up=True)
        ccy, keep = MAIN, 0.0
    else:                                                     # الثانية ⇒ الرئيسية: بيع OTHER
        inst, side = INST_O, "sell"
        qt = s["q"] + s.get("dq", 0.0)
        qs = qt
        if pr["pt"] in ("other", "half"):                     # يبيع بقدر الكلفة (+ نصف الربح) ويبقي الباقي بالثانية
            w = _worst_main_per_other(Q, pr)
            if w <= 0:
                return False
            want = s["c"] if pr["pt"] == "other" else s["c"] + 0.5 * max(0.0, qt * w - s["c"])
            qs = min(qt, math.ceil(want / w / (SPEC[INST_O].get("lotSz") or 1e-6) - 1e-9) * (SPEC[INST_O].get("lotSz") or 1e-6))
        sz = fmt_qty(qs, INST_O)
        keep = max(0.0, qt - sz) if pr["pt"] in ("other", "half") else 0.0
        px = _px_round(Q["o"][0] * (1 - cap), INST_O, up=True)
        ccy = OTHER
    if sz <= 0 or px <= 0:
        return False
    wt = state.setdefault("side_wait", {})
    if time.time() < _f(wt.get(kind)):
        return False
    av = balance_direct(ccy, zero_ok=True)
    if av is None:
        return False
    if av < sz - 1e-12:
        wt[kind] = time.time() + 300
        if time.time() - _f(state.get(f"last_bal_log_{kind}")) > 1800:
            state[f"last_bal_log_{kind}"] = time.time()
            log_trade_history(SYMBOL, f"⚠️ [رصيد] المتاح من {ccy} ({_n(av)}) أقل من المطلوب ({_n(sz)}) للمستوى {s['j']} — ينتظر")
        save_json(STATE_FILE, state)
        return False
    op = {"id": _seq(state), "k": key, "kind": kind, "ts": time.time(), "r_at": Q["r_buy"] if kind == "buy" else Q["r_sell"],
          "plan_sz": sz, "keep": round(keep, 12), "a": _leg(state, inst, side, sz, px), "b": None, "usd": 0.0, "sold": 0.0, "got": 0.0, "tries": 0}
    state["op"] = op
    if save_json(STATE_FILE, state) is not True:              # ✋ القيد ما انحفظ ⇒ ما نرسل
        state["op"] = None
        return False
    ok, r = _place(op["a"])
    if ok is False:
        sc, msg = _rej_code(r or {})
        state["op"] = None
        wt[kind] = time.time() + (60 if sc == "51008" else 30)
        if time.time() - _f(state.get(f"last_rej_log_{kind}")) > 300:
            state[f"last_rej_log_{kind}"] = time.time()
            log_trade_history(SYMBOL, f"⚠️ [رفض أمر] {'بيع ' + MAIN if kind == 'buy' else 'بيع ' + OTHER} {_n(sz)} (المستوى {s['j']}): {msg or sc or 'سبب غير معروف'}")
        save_json(STATE_FILE, state)
        return False
    save_json(STATE_FILE, state)
    return True


def _min_usd(Q, tgt):
    """أقل دولار يكفي الرجل الثاني (1.5 × أدنى حجم للعملة اللي يشتريها) — أقل منه ما نبيع (يبقى كسوراً بلا شراء)"""
    ask = Q["o"][1] if tgt == INST_O else Q["m"][1]
    return 1.5 * float(SPEC[tgt].get("minSz") or 0) * ask


def _worst_main_per_other(Q, pr):
    """كم رئيسية يرجع من وحدة ثانية بأسوأ سعر يسمح به السقف بعد عمولتين"""
    f, cap = pr["fee"], pr["cap"]
    return Q["o"][0] * (1 - cap) * (1 - f) / (Q["m"][1] * (1 + cap)) * (1 - f)


def _op_tick(state, Q):
    """يكمّل التبديل المعلّق بنفس اللحظة: الرجل الأول ⇒ الدولار محجوز ⇒ الرجل الثاني (يعيد لحد ما يصرف الدولار) ⇒ إغلاق بحفظة واحدة"""
    for i in range(6):
        if not state.get("op"):
            return True
        if i:
            Q = _quotes() or Q                                 # رجل ثانٍ جديد (باقي الدولار) ⇒ بأسعار جديدة
        r = _op_step(state, Q)
        if r is not True:
            return False
    return not state.get("op")


def _op_step(state, Q):
    """خطوة وحدة من التبديل · True = تقدّم (نكمل بنفس اللحظة) · False = ننتظر الدورة الجاية"""
    op = state.get("op")
    if not op:
        return True
    pr = state["pair"]
    if op.get("a") and op["a"].get("st") != "done":
        if not _resolve(state, op, "a"):
            return False
        if op.get("a") is None:                                # الرجل الأول ما وصل المنصة ⇒ التبديل ما صار
            state["op"] = None
            save_json(STATE_FILE, state)
            return True
        if _f(op.get("sold")) <= 0:                            # ما انفّذ شي (السعر عبر السقف) ⇒ التبديل ما صار
            state["op"] = None
            save_json(STATE_FILE, state)
            return True
    if op.get("b"):
        if not _resolve(state, op, "b"):
            return False
        return True
    tgt = INST_O if op["kind"] == "buy" else INST_M
    if op["kind"] == "sell" and not op.get("dust_in"):           # دولار الكسور السابق يرجع للرئيسية ويّا البيعة (بكلفته)
        op["usd"] = round(_f(op.get("usd")) + _f(state.get("usd_dust")), 10)
        op["dust_cost"] = round(_f(state.get("dust_cost")), 12)
        state["usd_dust"] = 0.0
        state["dust_cost"] = 0.0
        op["dust_in"] = True
        save_json(STATE_FILE, state)
    usd = _f(op.get("usd"))
    if Q is None:
        return False
    ask = Q["o"][1] if tgt == INST_O else Q["m"][1]
    px = _px_round(ask * (1 + _f(pr.get("capb"), pr["cap"])), tgt, up=True)
    qty = fmt_qty(usd / px * (1 - 1e-9), tgt) if px > 0 else 0.0
    if qty <= 0:
        return _close_op(state, op)
    if time.time() < _f(op.get("wait")):
        return False
    if op["kind"] == "sell" and _f(op.get("got")) <= 0:          # بيعة: الرجل الثاني لازم يرجع الكلفة على الأقل
        s = _slots(state).get(op["k"]) or {}
        qt = s.get("q", 0.0) + s.get("dq", 0.0)
        cost = s.get("c", 0.0) * (min(1.0, _f(op.get("sold")) / op["plan_sz"]) if op.get("plan_sz") else 1.0)
        exp = usd / (ask * (1 + pr["cap"])) * (1 - pr["fee"])
        if exp < cost - 1e-12 and time.time() - _f(op.get("ts")) < CLOSE_WAIT:
            if not op.get("waitlog"):
                op["waitlog"] = True
                log_trade_history(SYMBOL, f"⏳ [إكمال التبديل] {MAIN} قفز بين الرجلين — الدولار محجوز ({_n(usd)} {BRIDGE}) ينتظر سعراً لا يخسر (حتى 10 دقائق)")
            op["wait"] = time.time() + 5
            save_json(STATE_FILE, state)
            return False
    op["b"] = _leg(state, tgt, "buy", qty, px)
    if save_json(STATE_FILE, state) is not True:
        op["b"] = None
        return False
    ok, r = _place(op["b"])
    if ok is False:
        sc, msg = _rej_code(r or {})
        op["b"] = None
        op["tries"] = int(op.get("tries") or 0) + 1
        op["wait"] = time.time() + RETRY[min(len(RETRY) - 1, op["tries"] - 1)]
        if op["tries"] in (1, 3) or op["tries"] % 30 == 0:
            log_trade_history(SYMBOL, f"⚠️ [إكمال التبديل] شراء {tgt.split('-')[0]} بالدولار المحجوز ({_n(usd)} {BRIDGE}) رُفض: {msg or sc or 'سبب غير معروف'}"
                                      f" — يعيد المحاولة (المحاولة {op['tries']}) والدولار يبقى محجوزاً للبوت")
        save_json(STATE_FILE, state)
        return False
    if ok is None:
        save_json(STATE_FILE, state)
        return False
    save_json(STATE_FILE, state)
    d = _check(op["b"])
    if d and _final(d):
        _apply(state, op, "b", d)
        return True
    return False


def _close_op(state, op):
    """التبديل خلص ⇒ **حفظة واحدة**: الخانة · الدفاتر · الربح · السطر — وبعدها التبديل ما يبقى بالحالة"""
    pr = state["pair"]
    S = _slots(state)
    s = S.get(op["k"])
    lines = []
    sold, got = _f(op.get("sold")), _f(op.get("got"))
    dust = max(0.0, _f(op.get("usd")))
    state["usd_dust"] = round(_f(state.get("usd_dust")) + dust, 10)
    t = time.time()
    day = datetime.fromtimestamp(t).strftime("%Y-%m-%d")
    if s is None:
        state["op"] = None
        return _commit(state, lines)
    if op["kind"] == "buy":
        state["main_book"] = round(_f(state.get("main_book")) - sold, 12)
        if got > 0:
            s.update(side="sell", q=round(s.get("q", 0.0) + got, 12), c=round(s.get("c", 0.0) + sold + s.get("dc", 0.0), 12), dc=0.0,
                     cyc=int(s.get("cyc") or 0) + 1)
            s.pop("wallet", None)
            r_eff = sold / got
            lines.append(f"🟢 [شراء] {OTHER} مقابل {MAIN}: النسبة {_n(r_eff)} | الكمية: {_n(got)} {OTHER} بـ {_n(sold)} {MAIN}"
                         f" -> تم تجهيز بيع بنسبة: {_n(s['sp'])} · 🔀 المستوى {s['j']}")
            state["last_trade"] = {"side": "buy", "ratio": round(r_eff, 12), "qty": round(got, 12), "main": round(sold, 12), "ts": t, "slot": op["k"],
                                   "n": int((state.get("last_trade") or {}).get("n") or 0) + 1}
        else:                                                   # الرئيسية انباعت والثانية ما انشرت (كسور) ⇒ الدولار يبقى للبوت بكلفته
            state["dust_cost"] = round(_f(state.get("dust_cost")) + sold, 12)
            lines.append(f"🧩 [تبديل ناقص] بيع {_n(sold)} {MAIN} وبقي {_n(dust)} {BRIDGE} محجوزاً للبوت · 🔀 المستوى {s['j']}")
    else:
        qt = s.get("q", 0.0) + s.get("dq", 0.0)
        plan = _f(op.get("plan_sz")) or qt
        lot = SPEC[INST_O].get("lotSz") or 1e-6
        full = sold >= plan - lot * 0.5
        cost = s.get("c", 0.0) if full else s.get("c", 0.0) * (sold / plan if plan > 0 else 1.0)
        if got <= 0:                                            # بيع كسور ما يكفي دولارها أدنى حجم للرئيسية ⇒ الدولار يبقى للبوت بكلفته
            state["dust_cost"] = round(_f(state.get("dust_cost")) + cost, 12)
            s.update(q=round(max(0.0, qt - sold), 12), dq=0.0, c=round(max(0.0, s.get("c", 0.0) - cost), 12))
            if s["q"] <= lot * 0.5:
                s.update(side="buy", q=0.0, c=0.0)
            lines.append(f"🧩 [تبديل ناقص] بيع {_n(sold)} {OTHER} وبقي {_n(dust)} {BRIDGE} محجوزاً للبوت (أقل من أدنى شراء لـ{MAIN}) · 🔀 المستوى {s['j']}")
            state["op"] = None
            return _commit(state, lines)
        cost += _f(op.get("dust_cost"))
        profit = round(got - cost, 12)
        state["main_book"] = round(_f(state.get("main_book")) + got, 12)
        state["total_profit"] = round(_f(state.get("total_profit")) + profit, 12)
        dd = state.setdefault("daily", {})
        dd[day] = round(_f(dd.get(day)) + profit, 12)
        if len(dd) > 400:
            for k_ in sorted(dd)[:-400]:
                dd.pop(k_, None)
        kept = 0.0
        if full:
            left = max(0.0, qt - sold)
            kept = min(left, _f(op.get("keep")))
            if kept > 0:
                state["profit_other"] = round(_f(state.get("profit_other")) + kept, 12)
                dk = state.setdefault("daily_other", {})
                dk[day] = round(_f(dk.get(day)) + kept, 12)
            n_sale = int(s.get("n") or 0) + 1
            s.update(side="buy", q=0.0, c=0.0, dq=round(max(0.0, left - kept), 12), n=n_sale, cyc=int(s.get("cyc") or 0) + 1)
            s.pop("wallet", None)
        else:
            n_sale = int(s.get("n") or 0)
            left, cleft = round(max(0.0, qt - sold), 12), round(max(0.0, s.get("c", 0.0) - (cost - _f(op.get("dust_cost")))), 12)
            px_o, px_m = _f(state.get("px_other")), _f(state.get("px_main"))
            small = px_o > 0 and px_m > 0 and left * px_o < 1.5 * float(SPEC[INST_M].get("minSz") or 0) * px_m
            if small:                                           # الباقي أصغر من بيعة ⇒ يبقى بالمستوى بكلفته (يُباع ويّا البيعة الجاية)
                n_sale += 1
                s.update(side="buy", q=0.0, c=0.0, dq=left, dc=cleft, n=n_sale, cyc=int(s.get("cyc") or 0) + 1)
                s.pop("wallet", None)
                full = True
            else:
                s.update(q=left, dq=0.0, c=cleft)
        r_eff = got / sold if sold > 0 else 0.0
        sgn = "+" if profit >= 0 else "-"
        txt = (f"🔴 [بيع] {OTHER} مقابل {MAIN}: النسبة {_n(r_eff)} | الكمية: {_n(sold)} {OTHER} -> {_n(got)} {MAIN} | الربح: {sgn}{_n(abs(profit))} {MAIN}"
               + (f" + {_n(kept)} {OTHER}" if kept > 0 else ""))
        if full:
            txt += f" -> تم تجهيز شراء بنسبة: {_n(s['bp'])} · 🔀 المستوى {s['j']} · البيعة {n_sale}"
        else:
            txt += f" · 🧩 تنفيذ جزئي — الباقي {_n(s['q'])} {OTHER} ينتظر · 🔀 المستوى {s['j']}"
        lines.append(txt)
        state["last_trade"] = {"side": "sell", "ratio": round(r_eff, 12), "qty": round(sold, 12), "main": round(got, 12), "profit": round(profit, 12),
                               "kept": round(kept, 12), "ts": t, "slot": op["k"], "n": int((state.get("last_trade") or {}).get("n") or 0) + 1}
    h = state.setdefault("swaps", [])
    h.append({"t": round(t, 1), "kind": op["kind"], "j": s["j"], "sold": round(sold, 12), "got": round(got, 12),
              "profit": round(_f(state["last_trade"].get("profit")) if op["kind"] == "sell" else 0.0, 12)})
    del h[:-HIST_N]
    state["op"] = None
    return _commit(state, lines)


def _pick(state, Q):
    """الأمران التاليان: البيع الأقرب فوق (نسبته ≤ نسبة البيع الحالية وربحه مضمون بأسوأ سعر) · الشراء الأقرب تحت"""
    pr = state["pair"]
    S = _slots(state)
    if not state.get("pause_sell"):
        sc = _f(state.get("sell_ceiling"))
        cands = sorted((s for s in S.values() if s["side"] == "sell" and Q["r_sell"] >= s["sp"] - 1e-15 and not (sc > 0 and s["sp"] > sc + 1e-15)),
                       key=lambda s: s["sp"])
        w = _worst_main_per_other(Q, pr)
        for s in cands:
            qt = s["q"] + s.get("dq", 0.0)
            if fmt_qty(qt, INST_O) <= 0 or qt * Q["o"][0] < _min_usd(Q, INST_M):
                continue
            if qt * w <= s["c"] + 1e-12:                         # بأسوأ سعر يخسر ⇒ ينتظر نسبة أعلى
                continue
            return _key(s["j"]), s, "sell"
    if not state.get("pause_buy") and _f(state.get("main_book")) > 0:
        bf = _f(state.get("buy_floor"))
        cands = sorted((s for s in S.values() if s["side"] == "buy" and Q["r_buy"] <= s["bp"] + 1e-15 and not (bf > 0 and s["bp"] < bf - 1e-15)),
                       key=lambda s: -s["bp"])
        for s in cands:
            if fmt_qty(min(pr["mv"], _f(state.get("main_book"))), INST_M) <= 0:
                break
            return _key(s["j"]), s, "buy"
    return None


def destruct_now(state):
    """💣 الحذف: ماكو أوامر قاعدة على المنصة ⇒ يكمّل التبديل المعلّق (الدولار يرجع عملة) وبعدين ينسحب"""
    if state.get("op"):
        Q = _quotes()
        _op_tick(state, Q)
        if state.get("op"):
            if time.time() - _f(state.get("last_destruct_log")) > 300:
                state["last_destruct_log"] = time.time()
                log_trade_history(SYMBOL, "💣 [حذف] ينتظر إكمال التبديل الحالي قبل الانسحاب (الدولار المحجوز يرجع عملة)")
                save_json(STATE_FILE, state)
            return False
    state["destruct_done"] = True
    state["status"] = "stopped"
    lines = [f"💣 [حذف] انسحب البوت — لا أوامر على المنصة · {_n(_f(state.get('main_book')))} {MAIN} · "
             f"{_n(_f(state.get('other_book')))} {OTHER} · {_n(_f(state.get('usd_dust')))} {BRIDGE} بقيت بالمحفظة"]
    _commit(state, lines)
    return True


def monitor_and_recover(state):
    """دورة الفحص: الحذف · الإيقاف ⇒ 📦 · التبديل المعلّق أول · الأمران التاليان (حتى MAX_OPS تبديل بأسعار جديدة)"""
    if state.get("self_destruct") and not state.get("destruct_done"):
        destruct_now(state)
        return
    if not _born(state):
        return
    if state.get("fx_log") and save_json(STATE_FILE, state) is True:   # 🧾 التنفيذ على القرص أول ⇒ بعدين سطره
        _fx_log_flush(state)
        save_json(STATE_FILE, state)
    for _ in range(MAX_OPS):
        Q = _quotes()
        if Q:
            state["ratio"] = round(Q["r"], 12)
            state["current_price"] = Q["o"][2]
            state["px_main"], state["px_other"] = Q["m"][2], Q["o"][2]
            if state.get("pause_buy") and not _f(state.get("buy_floor")):
                state["buy_floor"] = Q["r"]
                state["pause_buy"] = False
                log_trade_history(SYMBOL, f"⏸️→📦 إيقاف الشراء — الأرضية {_n(Q['r'])} (الشراءات تحتها تنتظر)")
            if state.get("pause_sell") and not _f(state.get("sell_ceiling")):
                state["sell_ceiling"] = Q["r"]
                state["pause_sell"] = False
                log_trade_history(SYMBOL, f"⏸️→📦 إيقاف البيع — السقف {_n(Q['r'])} (البيعات فوقه تنتظر)")
        if state.get("op"):
            _op_tick(state, Q)
            if state.get("op"):
                break
            continue
        if not Q or not NET_STATE["online"]:
            break
        p = _pick(state, Q)
        if not p:
            break
        if not _start_op(state, p[0], p[1], p[2], Q):
            break
        _op_tick(state, Q)
        if state.get("op"):
            break
    if time.time() - SAVED["t"] >= 5.0:
        save_json(STATE_FILE, state)                      # نبض: اللوحة تعرف البوت شغّال


def start_bot():
    state = load_state_with_backup() or {"total_profit": 0.0}
    if state.get("destruct_done"):
        print("💣 This bot withdrew (destruct_done) — it does not trade again.")
        sys.exit(0)
    _ctl_note(state, _ctl_sig(STATE_FILE))
    for k, v in (("pause_buy", False), ("pause_sell", False), ("buy_floor", 0), ("sell_ceiling", 0)):
        state.setdefault(k, v)
    backup_state(STATE_FILE, BACKUP_DIR)
    state["seq"] = max(int(state.get("seq") or 0), int(time.time() * 1000))   # معرّفات الأوامر تبقى جديدة حتى بعد نسخة احتياطية
    while not _born(state):
        time.sleep(5)
    print(f"🚀 Two-Coin Grid started for {SYMBOL} | ID: {BOT_ID}")
    last = 0.0
    while True:
        fresh = load_json(CONFIG_FILE)
        if fresh:
            config.update(fresh)
        _sig0 = _ctl_sig(STATE_FILE)
        ext = load_json(STATE_FILE)
        if ext:
            _ctl_note(ext, _sig0)
            state["pause_buy"] = ext.get("pause_buy", state.get("pause_buy", False))
            state["pause_sell"] = ext.get("pause_sell", state.get("pause_sell", False))
            state["status"] = ext.get("status", state.get("status", "running"))
            state["sell_ceiling"] = float(ext.get("sell_ceiling", state.get("sell_ceiling", 0)) or 0)
            state["buy_floor"] = float(ext.get("buy_floor", state.get("buy_floor", 0)) or 0)
            if ext.get("self_destruct"):
                state["self_destruct"] = True
        if time.time() - last >= LOOP_S:
            try:
                monitor_and_recover(state)
            except Exception as e:
                if time.time() - float(state.get("last_recover_err_print") or 0) > 60:
                    state["last_recover_err_print"] = time.time()
                    print(f"\n⚠️ [Recover Warning] {type(e).__name__}: {e}")
            last = time.time()
            if state.get("destruct_done"):
                print("💣 withdrew")
                sys.exit(0)
            print(f"🔀 {SYMBOL} | Profit: {round(float(state.get('total_profit') or 0), 6)} {MAIN}".ljust(80), end="\r")
        time.sleep(0.5)


if __name__ == "__main__":
    try:
        start_bot()
    except Exception as e:
        print(f"❌ Crash: {e}")
