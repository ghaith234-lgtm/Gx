# 🪜🎨 the card's price ruler draws the overlap — the owner (7-11): «افحص هل هناك خلل في رسم الكرت اقصد الخطوط اريد الخطوط تتداخل»
#   the real engine on the mock OKX (his two settings, a fixed price path) · the real dashboard serves the bot (closed folder · fake
#   keys · no network) · a browser draws the card's ruler (dark and light theme) and Python reads every line:
#   ① every level whose buy price is inside the ruler has a line there — a buy line while it has a buy order, else a dotted one
#      (before: a level that bought — all its parts holding coins — had no line, so its sells' overlap with the levels above was
#      invisible) · no dotted line for a level that has a buy order · each at its price
#   ② the overlap as the owner means it: 3 parts 0.45/0.15 · G 0.6 ⇒ level −1's 2nd sell sits exactly on level 0's buy price ·
#      20 parts 0.3/1 ⇒ sells of several levels and the buy prices of the levels above interleave
#   ③ one colour per level (its buy · dotted · sells), two levels on the card never the same · the palettes: any two levels up to 7
#      apart ΔE2000 ≥ 15 (dark) / ≥ 12 (light) · none near red (loss) · the light theme takes the darker set
#   ④ tap a dotted line ⇒ the level's details and why it has no buy order · no page error
#   python3 devtests/step/ui_lines.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import json, math, os, re, shutil, socket, subprocess, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
from okxsim import Clock, Ex, Bot, walk

Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


# ── ΔE2000 (sRGB → Lab D65)
def _lab(h):
    c = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    r, g, b = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    X, Y, Z = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047, 0.2126 * r + 0.7152 * g + 0.0722 * b, (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))


def de(h1, h2):
    (L1, a1, b1), (L2, a2, b2) = _lab(h1), _lab(h2)
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7))); a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p, h2p = math.degrees(math.atan2(b1, a1p)) % 360, math.degrees(math.atan2(b2, a2p)) % 360
    dL, dC, dh = L2 - L1, C2p - C1p, h2p - h1p
    dh = 0 if C1p * C2p == 0 else (dh - 360 if dh > 180 else dh + 360 if dh < -180 else dh)
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2)); Lb, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    hb = (h1p + h2p) / 2 if abs(h1p - h2p) <= 180 else (h1p + h2p + 360) / 2
    T = 1 - 0.17 * math.cos(math.radians(hb - 30)) + 0.24 * math.cos(math.radians(2 * hb)) + 0.32 * math.cos(math.radians(3 * hb + 6)) - 0.2 * math.cos(math.radians(4 * hb - 63))
    dth = 30 * math.exp(-((hb - 275) / 25) ** 2); RC = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7))
    SL = 1 + 0.015 * (Lb - 50) ** 2 / math.sqrt(20 + (Lb - 50) ** 2); SC = 1 + 0.045 * Cbp; SH = 1 + 0.015 * Cbp * T
    RT = -math.sin(math.radians(2 * dth)) * RC
    return math.sqrt((dL / SL) ** 2 + (dC / SC) ** 2 + (dH / SH) ** 2 + RT * (dC / SC) * (dH / SH))


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


P0 = 1.1698
SC = {
    "3 parts 0.45/0.15": ({"usd_value": 25.0, "step_parts": 3, "step_first": 0.0045, "step_sell": 0.0015, "up_groups": 1},
                          [P0, P0, P0 * 1.0046, P0 * 1.0046, P0 * 0.992, P0 * 0.992, P0 * 0.997, P0 * 0.997], 100, 1000),
    "20 parts 0.3/1": ({"usd_value": 100.0, "step_parts": 20, "step_first": 0.003, "step_sell": 0.01, "up_groups": 20},
                       [P0, P0, P0 * 1.004, P0 * 1.004, P0 * 0.985, P0 * 0.985, P0 * 0.994, P0 * 0.994], 4000, 6000),
}
LINE = re.compile(r'<g class="stl" data-stl="(?P<k>[brs]):(?P<j>-?\d+)(?::(?P<p>\d+))?">.*?<line x1="(?P<x1>[\d.]+)" y1="(?P<y>[-\d.]+)"[^>]*?stroke="(?P<c>#[0-9a-fA-F]{6})"'
                  r'(?P<rest>[^>]*)/>', re.S)
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
PAL = None

for name, (cf, path, base, quote) in SC.items():
    R = tempfile.mkdtemp(prefix="ui_lines_")
    shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
    PORT = port()
    json.dump({"port": PORT}, open(os.path.join(R, "dashboard_config.json"), "w"))
    json.dump({"wallets": [{"name": "main", "api": "FAKE-KEY", "sec": "FAKE-SECRET", "pass": "FAKE-PASS"}]}, open(os.path.join(R, "monitor_config.json"), "w"))
    F = os.path.join(R, "step_xrp"); os.makedirs(F)
    ex = Ex(Clock(t0=time.time() - 3 * 3600), sym="XRP-USDT", price=P0, base=base, quote=quote)
    CF = {"grid_percentage": 0.006, "min_price": 0.9, "forced_base_price": P0, "step_window": 8, "fee_rate": 0.0008, "taker_rate": 0.001,
          "reinvest": False}
    CF.update(cf)
    Bot(ex, CF, folder=F).run(walk([round(p, 4) for p in path], 20))
    d = subprocess.Popen([sys.executable, os.path.join(H, "video", "vid_dash.py"), R, str(PORT)], stdout=subprocess.PIPE, text=True, env=env)
    try:
        assert "dashboard up" in d.stdout.readline()
        r = subprocess.run(["node", os.path.join(H, "ui_lines.js"), f"http://127.0.0.1:{PORT}/"], capture_output=True, text=True, timeout=240, cwd="/tmp", env=env)
        out = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"err": r.stderr[-800:]}
    except Exception as e:
        out = {"err": repr(e)}
    finally:
        d.kill()
        shutil.rmtree(R, ignore_errors=True)
    if out.get("err"):
        ok(f"[{name}] the card drew", False, out["err"]); continue
    b, cp = out["b"], float(out["b"]["cp"])
    SL = b.get("sl") or []
    lines = [dict(m.groupdict(), y=float(m.group("y")), j=int(m.group("j"))) for m in LINE.finditer(out["dark"])]
    lv = {}
    for x in SL:
        e = lv.setdefault(x[0], {"bp": float(x[6]), "pub": 0, "s": {}})
        if x[2] == "b" and x[5] != "M":
            e["pub"] += 1; e["bp_live"] = float(x[3])
        if x[2] == "s":
            e["s"][x[1]] = (float(x[3]), x[5])
    px = []                                                      # (price, y) of every order line → the ruler's scale
    for l in lines:
        if l["k"] == "b":
            px.append((lv[l["j"]].get("bp_live", lv[l["j"]]["bp"]), l["y"]))
        elif l["k"] == "s":
            px.append((lv[l["j"]]["s"][int(l["p"])][0], l["y"]))
    (p1, y1), (p2, y2) = max(px), min(px)
    yat = lambda p: y1 + (y2 - y1) * (p - p1) / (p2 - p1)
    lo, hi = min(p for p, _ in px), max(p for p, _ in px)
    need = {j for j, e in lv.items() if not e["pub"] and lo < e["bp"] < hi}
    R_ = {l["j"]: l for l in lines if l["k"] == "r"}
    at = all(abs(R_[j]["y"] - yat(lv[j]["bp"])) < 0.8 for j in R_)
    ok(f"[{name}] ① every level whose buy price is inside the ruler has its line — dotted for the {len(need)} level(s) without a buy order "
       f"(levels {sorted(need, reverse=True)}) · none for a level with a buy order · each at its price",
       need and need <= set(R_) and not any(lv[j]["pub"] for j in R_) and at and all("stroke-dasharray" in R_[j]["rest"] for j in R_),
       {"need": sorted(need), "drawn": sorted(R_), "at": at, "lo": lo, "hi": hi})
    Y = {(l["k"], l["j"], l["p"]): l["y"] for l in lines}
    if name.startswith("3"):
        ys, yr = Y.get(("s", -1, "2")), (R_.get(0) or {}).get("y")
        ok(f"[{name}] ② the overlap: level −1's 2nd sell sits exactly on level 0's buy price (both drawn, same height) · its 3rd sell above it",
           ys is not None and yr is not None and abs(ys - yr) < 0.6 and Y.get(("s", -1, "3"), 1e9) < yr, {"s-1:2": ys, "r0": yr, "s-1:3": Y.get(("s", -1, "3"))})
    else:
        seq = [(l["y"], l["k"], l["j"]) for l in lines if l["k"] in "sr"]; seq.sort()
        between = sum(1 for i in range(1, len(seq) - 1) if seq[i][1] == "r" and seq[i - 1][1] == "s" and seq[i + 1][1] == "s"
                      and seq[i - 1][2] != seq[i][2] and seq[i + 1][2] != seq[i][2])
        mixed = sum(1 for i in range(1, len(seq)) if seq[i][1] == "s" and seq[i - 1][1] == "s" and seq[i][2] != seq[i - 1][2])
        ok(f"[{name}] ② the overlap: {between} buy price(s) of the levels above sit between other levels' sells · {mixed} times two neighbouring sells "
           "are from different levels", between >= 2 and mixed >= 3, seq)
    col = {}
    for l in lines:
        col.setdefault(l["j"], set()).add(l["c"].lower())
    one = all(len(v) == 1 for v in col.values())
    uniq = len({next(iter(v)) for v in col.values()}) == len(col)
    PAL = PAL or out.get("pal")
    lcol = {int(m.group("j")): m.group("c").lower() for m in LINE.finditer(out["light"])}
    ok(f"[{name}] ③ one colour per level on the card (buy · dotted · sells) — {len(col)} levels, {len(col)} different colours · the light theme "
       "draws with its own darker set", one and uniq and PAL and all(c in [x.lower() for x in PAL["L"]] for c in lcol.values())
       and any(c not in [x.lower() for x in PAL["D"]] for c in lcol.values()), {"col": {k: sorted(v) for k, v in col.items()}, "light": lcol})
    t = out.get("pop") or ""
    ok(f"[{name}] ④ tap a dotted line ⇒ the level's details and why it has no buy order · no page error",
       re.search(r"المستوى -?\d+ — شراء ثابت", t) and "لا يوجد له أمر شراء منشور" in t and "اشترى" in t and not out.get("errs"), (t[:400], out.get("errs")))

if PAL:
    def worst(P, D):
        n = len(P); return min((de(P[a % n], P[b % n]), a, b) for a in range(-12, 13) for b in range(-12, 13) if 0 < b - a <= D)
    wd, wl = worst(PAL["D"], 7), worst(PAL["L"], 7)
    reds_d, reds_l = ["#fb7185", "#ef4444", "#ef454a"], ["#be123c", "#ef4444", "#dc2626"]
    nr = min(de(c, r) for c in PAL["D"] for r in reds_d), min(de(c, r) for c in PAL["L"] for r in reds_l)
    ok(f"③ the palettes: any two levels up to 7 apart ΔE2000 ≥ 15 dark ({wd[0]:.1f}, levels {wd[1]}/{wd[2]}) · ≥ 12 light ({wl[0]:.1f}) · "
       f"none near red ({nr[0]:.1f} · {nr[1]:.1f})", wd[0] >= 15 and wl[0] >= 12 and min(nr) >= 22, (wd, wl, nr))
else:
    ok("③ the palettes were read from the page", False)
print(f"{'✅' if all(res) else '❌'} ui_lines: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
