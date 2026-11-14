# 🎨 patch 64 (dashboard v3.36.43 · two new colour sets) — the owner (14-11), after 8 sets shown on his own dashboard: «5 و 8 … اريدها
#   هادئة مو صارخه» ⇒ ❄️ «جليدي» (dark · ice blue + silver) and 🩵 «سماوي نهاري» (light · sky blue + violet) join ⚙️ «🎨 الألوان».
#   Every colour comes from the theme variables (rule 15 «🧭 النسق الثابت») — a set is one block of variables + one THEMES row + the
#   login page's six colours; a light set also joins the light-only rules (shadows · white button text · the gradient numbers) and
#   lightThemes() (the chart palette · the TradingView chart · the 🪜 line colours). add_theme() is reused for the next sets.
#   python3 devtests/step/patches/p64_themes_calm.py Holy_Dashboard.pyw
import os, re, sys

THEMES_NEW = [
    # key, name, light?, THEMES row swatches (bg, c1, c2, c3), login six (bg, surface, border, text, muted, accent), the variables
    ("arctic", "جليدي", False, ("#0d141c", "#bae6fd", "#e2e8f0", "#7dd3fc"), ("#0d141c", "#121c27", "#253546", "#f1f7fc", "#9fb1c2", "#bae6fd"),
     """--bg0:#070b10;--bg1:#0d141c;--tx:#f1f7fc;--mut:#9fb1c2;--mut2:#6a7c8d;
  --vio-rgb:186 230 253;--vio2-rgb:125 190 230;--vio3-rgb:160 214 245;--cyan-rgb:226 232 240;--cyan2-rgb:160 175 195;--cyan3-rgb:130 145 165;
  --surf-rgb:16 24 33;--surf2-rgb:12 18 26;--surf3-rgb:9 13 19;--surf4-rgb:23 34 46;--scrim-rgb:4 7 10;
  --big-a:#f5fbff;--tx2:#dce7f0;--bgA:#12304a;--bgB:#1f2a36;--orb1:#38bdf8;--orb2:#94a3b8;--orb3:#e0f2fe;
  --modal-bg:linear-gradient(165deg,#15212e,#080d13);--tip-bg:#121c27;--coin-bg:#16222f;--chart-bg:#080d13;--card2:#101923;--bd:#253546;--on-acc:#08131c""", None),
    ("sky", "سماوي نهاري", True, ("#eef5fb", "#0369a1", "#7c3aed", "#0f1d2e"), ("#eef5fb", "#ffffff", "#d9e6f2", "#0f1d2e", "#4d5f73", "#0369a1"),
     """color-scheme:light;--bg0:#eef5fb;--bg1:#ffffff;--tx:#0f1d2e;--mut:#4d5f73;--mut2:#5f7186;
  --vio-rgb:3 105 161;--vio2-rgb:7 89 133;--vio3-rgb:2 132 199;--cyan-rgb:124 58 237;--cyan2-rgb:109 40 217;--cyan3-rgb:124 58 237;
  --green-rgb:4 120 87;--green2-rgb:22 163 74;--red-rgb:190 18 60;--red2-rgb:220 38 38;--amber-rgb:180 83 9;--amber2-rgb:217 119 6;--amber3-rgb:180 83 9;
  --blue-rgb:37 99 235;--ov-rgb:15 29 46;--sh-rgb:70 95 125;--surf-rgb:255 255 255;--surf2-rgb:255 255 255;--surf3-rgb:248 251 254;--surf4-rgb:255 255 255;--scrim-rgb:228 238 247;
  --hi:#0f1d2e;--on-acc:#ffffff;--on-green:#ffffff;--red-soft:#9f1239;--green-soft:#065f46;--big-a:#12304a;--tx2:#233b52;
  --bgA:#d6ecfb;--bgB:#e9ddff;--orb1:#7dd3fc;--orb2:#c4b5fd;--orb3:#a5f3fc;
  --glass:linear-gradient(160deg,rgb(255 255 255/.95),rgb(255 255 255/.82));--line:rgb(3 105 161/.15);--line2:rgb(124 58 237/.28);
  --modal-bg:linear-gradient(165deg,#ffffff,#f3f8fc);--tip-bg:#ffffff;--coin-bg:#e3eef8;--chart-bg:#ffffff;--card2:#f5f9fd;--bd:#d9e6f2""",
     ("#0284c7", "linear-gradient(92deg,#7c3aed,#0369a1)", "rgb(3 105 161/.22)")),
]
AFTER = {"arctic": "graphite", "sky": "light"}       # where each row sits in ⚙️ «🎨 الألوان»


def once(s, a, b, what):
    if s.count(a) != 1:
        print(f"❌ {what}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
    return s.replace(a, b)


def add_theme(s, key, name, light, sw, login, vars_, lt):
    if f'html[data-theme="{key}"]{{' in s:
        print(f"❌ {key} is already there — nothing written"); sys.exit(1)
    # ① the variables — before the OKX block
    s = once(s, 'html[data-theme="okx"]{--bg0:', f'html[data-theme="{key}"]{{{vars_}}}\nhtml[data-theme="okx"]{{--bg0:', f"{key} variables")
    # ② the THEMES row after its neighbour
    m = re.search(r"\['%s','[^']*','#[0-9a-f]{6}','#[0-9a-f]{6}','#[0-9a-f]{6}','#[0-9a-f]{6}'\]," % AFTER[key], s)
    if not m:
        print(f"❌ THEMES row {AFTER[key]} not found — nothing written"); sys.exit(1)
    s = s[:m.end()] + f"\n  ['{key}','{name}','{sw[0]}','{sw[1]}','{sw[2]}','{sw[3]}']," + s[m.end():]
    # ③ the login page's six colours
    s = once(s, "']}[_t];", f"'],{key}:[{','.join(repr(c) for c in login)}]}}[_t];", "login palette (its last row)")
    if light:
        glint, grad, thumb = lt
        # ④ the light-only rules: every «html[data-theme="light"] X» selector gets its twin (the gradient numbers and the scrollbar take the set's own colours)
        def twin(mm):
            sel, body = mm.group(1), mm.group(2)
            if "background:linear-gradient(92deg" in body:
                return mm.group(0) + "\n" + re.sub(r'html\[data-theme="light"\]', f'html[data-theme="{key}"]', sel) + "{" + re.sub(r"linear-gradient\(92deg,[^)]*\)", grad, body) + "}"
            if "::-webkit-scrollbar-thumb" in sel:
                return mm.group(0) + "\n" + sel.replace('html[data-theme="light"]', f'html[data-theme="{key}"]') + "{background:" + thumb + "}"
            parts = [p.strip() for p in sel.split(",")]
            parts += [p.replace('html[data-theme="light"]', f'html[data-theme="{key}"]') for p in parts if 'html[data-theme="light"]' in p]
            return ",".join(parts) + "{" + body + "}"
        s, n = re.subn(r'(?m)^(html\[data-theme="light"\] [^{\n]+)\{([^}\n]*)\}', twin, s)
        if n < 12:
            print(f"❌ light rules: {n} found (12 expected) — nothing written"); sys.exit(1)
        s = once(s, 'html[data-theme="light"]{--glint:#c58a00}', f'html[data-theme="light"]{{--glint:#c58a00}}\nhtml[data-theme="{key}"]{{--glint:{glint}}}', "glint")
        s = s.replace("function lightThemes(){return ['light'", f"function lightThemes(){{return ['light','{key}'", 1)
    return s


R_LIGHT = [   # the four places that asked «light?» ask the list
    ("function pcPal(){return document.documentElement.dataset.theme==='light'", "function pcPal(){return lightThemes().includes(document.documentElement.dataset.theme)"),
    ("function tvTheme(){return uiTheme()==='light'?'light':'dark'}", "function tvTheme(){return lightThemes().includes(uiTheme())?'light':'dark'}"),
    ("function tvBg(){return uiTheme()==='light'?", "function tvBg(){return lightThemes().includes(uiTheme())?"),
    ("function stCol(j){const P=document.documentElement.dataset.theme==='light'?ST_PAL_L:ST_PAL", "function stCol(j){const P=lightThemes().includes(document.documentElement.dataset.theme)?ST_PAL_L:ST_PAL"),
    ("const THEMES=[['holy','بنفسجي ليلي'", "function lightThemes(){return ['light']}   // 🎨 v3.36.43: the light sets (the light-only rules · the chart palette · TradingView · the 🪜 lines) — a function: pcPal() runs before this line\nconst THEMES=[['holy','بنفسجي ليلي'"),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    if "function lightThemes()" not in s:
        for i, (a, b) in enumerate(R_LIGHT):
            s = once(s, a, b, f"light check {i}")
    for t in THEMES_NEW:
        s = add_theme(s, *t)
    s = once(s, 'APP_VERSION = "3.36.42"', 'APP_VERSION = "3.36.43"', "APP_VERSION")
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(THEMES_NEW)} colour sets ({', '.join(t[0] for t in THEMES_NEW)}) · compiles · {p}")
