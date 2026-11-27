# p144 — v3.36.78 🧩 the group engine gets options to MEASURE what gives the right signal (the owner 27-11: «افحص ولا تتقيد اهم شي يعطيني
#   الاشارة الصحيحه» — after Gemini's review: one candle only · no risk measure · combos by chance · old history = new · cross-group helpers)
#   · the defaults keep today's behaviour exactly (h 1 · all history · combos of two · no helpers · close) — t_groups unchanged
#   · h: a member graded over h candles of its frame (the big-move threshold × √h) · win: only the results of the last N days count (the usual
#     too) · combo 2: a pair only when each member alone is ≥ its usual so far · help: 🤝 helpers from the market's state (S-comp the compass ·
#     S-brd most coins above their 50 · S-btc Bitcoin's trend · S-vol a big-volume candle) — «member + helper» on the same side, graded like
#     any member, never a notice by itself · grade «tp»: right when a target the size of the usual move × √h is touched before the same stop
#   · every sent call keeps its path: the move at the end · the worst move against it before · the best move with it (gp_pathst)
#   · gp_build / gp_now carry the helpers (the same _gp_keys) · gp_pack adds «U2» (the usual of both sides) and «px» (the path averages)
#   python3 devtests/step/patches/p144_engine_options.py Holy_Dashboard.pyw
import sys, os, ast

V2 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "p144_engine_v2.txt"), encoding="utf-8").read()

R = [
    ('GP_P = {"dmin": 30, "lift": 0.05, "gap": 0.02, "cap": 2, "combo": 1}\n',
     'GP_P = {"dmin": 30, "lift": 0.05, "gap": 0.02, "cap": 2, "combo": 1, "h": 1, "win": 0, "help": 0, "grade": "close"}\n'
     'GP_TPX = 1.0                                             # «الهدف قبل الوقف»: الهدف والوقف = المعتاد × √المدة\n'
     'from collections import deque as _GPdq\n'),
    ('''    out = {"sec": W["sec"], "fr": W["fr"], "t": tl, "U": {j: round(u, 4) for j, u in W["U"].items()}, "p": W["p"], "g": {}}
    for g, R in W["rec"].items():
        u = W["U"].get(GP_GROUPS[g]["job"], 0.5)''',
     '''    out = {"sec": W["sec"], "fr": W["fr"], "t": tl, "U": {j: round(u, 4) for j, u in W["U"].items()}, "p": W["p"], "g": {},
           "U2": {j: [round(x, 4) for x in u] for j, u in (W.get("U2") or {}).items()}}
    for g, R in W["rec"].items():
        u = (W.get("U2") or {}).get(GP_GROUPS[g]["job"]) or W["U"].get(GP_GROUPS[g]["job"], 0.5)'''),
    ('''                       "now": W["now"][g], "nm": len(W["mem"][g]), "nc": len(combos),''',
     '''                       "now": W["now"][g], "nm": len(W["mem"][g]), "nc": len(combos),
                       "px": gp_pathst((W.get("path") or {}).get(g)), "px1": gp_pathst((W.get("path") or {}).get(g), S, tl - span // 4) if span else gp_pathst([]),'''),
    ('''        Db = F["BTC-USDT"][0]
        B = {Db["T"][i]: Db["C"][i] for i in range(Db["n"])}
        out["f"][fr] = {"coin": gp_pack(gp_walk(F, "coin", fr, B=B, p=p, keep=[s for s in keep if s in F], codes=codes)),
                        "mkt": gp_pack(gp_walk({"BTC-USDT": F["BTC-USDT"]}, "mkt", fr, p=p, codes=codes))}''',
     '''        Db = F["BTC-USDT"][0]
        B = {Db["T"][i]: Db["C"][i] for i in range(Db["n"])}
        S = _safe(_gp_states, F, fr, cdb, default=None) if out["p"].get("help") else None     # 🤝 حال السوق (للمساعدين)
        out["f"][fr] = {"coin": gp_pack(gp_walk(F, "coin", fr, B=B, p=p, keep=[s for s in keep if s in F], codes=codes, S=S)),
                        "mkt": gp_pack(gp_walk({"BTC-USDT": F["BTC-USDT"]}, "mkt", fr, p=p, codes=codes, S=S))}'''),
    ('''def gp_now(FF, G, p=None):
    """🔔 الفحص الحي (كل شمعة مغلقة): على آخر شمعة لكل عملة وإطار ⇒ ما انطلق من أبطال كل مجموعة (المحفوظين في آخر بناء) بجهة واحدة
    ⇒ {الإطار: {القسم: {المجموعة: {العملة: [الجهة, الأبطال]}}}} — الدالة نفسها (_gp_keys) التي يُبنى بها السجل"""
    p = dict(GP_P, **(p or {}))
    codes = _gp_codes()
    out = {}
    for fr, F in (FF or {}).items():
        Gf = ((G or {}).get("f") or {}).get(fr) or {}''',
     '''def gp_now(FF, G, p=None, cdb=None):
    """🔔 الفحص الحي (كل شمعة مغلقة): على آخر شمعة لكل عملة وإطار ⇒ ما انطلق من أبطال كل مجموعة (المحفوظين في آخر بناء) بجهة واحدة
    ⇒ {الإطار: {القسم: {المجموعة: {العملة: [الجهة, الأبطال]}}}} — الدالة نفسها (_gp_keys) التي يُبنى بها السجل · بقواعد البناء نفسه (G["p"])"""
    p = dict(GP_P, **((G or {}).get("p") or {}), **(p or {}))
    codes = _gp_codes()
    out = {}
    for fr, F in (FF or {}).items():
        Gf = ((G or {}).get("f") or {}).get(fr) or {}
        S = (_safe(_gp_states, F, fr, cdb, default=None) or {}) if p.get("help") else None'''),
    ('''                mem, job = set(gp_members(g, codes)), GP_GROUPS[g]["job"]
                for sym, (D, E) in F.items():
                    if (sec == "mkt" and sym != "BTC-USDT") or (job == "rs" and sym.startswith("BTC-")):
                        continue
                    keys = _gp_keys(_gp_fires(E, mem), D["n"] - 1, mem, SG_LK.get(fr, 2), job, combo=bool(p["combo"]))''',
     '''                mem, job = set(gp_members(g, codes)), GP_GROUPS[g]["job"]
                ok = {m_[0] for m_ in x.get("m") or [] if "+" not in m_[0] and m_[1] + m_[2] and m_[1] / (m_[1] + m_[2]) >= m_[5]}
                for sym, (D, E) in F.items():
                    if (sec == "mkt" and sym != "BTC-USDT") or (job == "rs" and sym.startswith("BTC-")):
                        continue
                    i = D["n"] - 1
                    st = None
                    if S is not None:
                        st = {c_: (S.get(c_) or {}).get(D["T"][i], 0) for c_ in ("S-comp", "S-brd", "S-btc")}
                        sv = _gp_svol(D).get(i)
                        if sv:
                            st["S-vol"] = sv
                    keys = _gp_keys(_gp_fires(E, mem), i, mem, SG_LK.get(fr, 2), job, combo=p["combo"], st=st, ok=ok)'''),
    ('    gpn = (_safe(gp_now, FF, gsrc, default=None) or {}) if isinstance(gsrc, dict) and gsrc.get("v") == GP_VER else {}\n',
     '    gpn = (_safe(gp_now, FF, gsrc, None, cdb, default=None) or {}) if isinstance(gsrc, dict) and gsrc.get("v") == GP_VER else {}\n'),
]

REPL = ("_gp_keys", "_gp_outs", "_gp_pb", "gp_walk")

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i}: found {s.count(a)} times — nothing written: {a[:90]!r}"); sys.exit(1)
        s = s.replace(a, b)
    new = {n.name: ast.get_source_segment(V2, n) for n in ast.parse(V2).body if isinstance(n, ast.FunctionDef)}
    L = s.split("\n")
    spans = sorted(((n.lineno, n.end_lineno, n.name) for n in ast.parse(s).body if isinstance(n, ast.FunctionDef) and n.name in REPL), reverse=True)
    if sorted(x[2] for x in spans) != sorted(REPL):
        print("❌ functions not found once", spans); sys.exit(1)
    for a0, b0, nm in spans:
        add = new[nm]
        if nm == "gp_walk":
            add += "\n\n\n" + "\n\n\n".join(new[k] for k in ("_gp_path", "gp_pathst"))
        if nm == "_gp_pb":
            add += "\n\n\n" + "\n\n\n".join(new[k] for k in ("_gp_states", "_gp_svol"))
        L[a0 - 1:b0] = add.split("\n")
    s = "\n".join(L)
    compile(s, p, "exec")
    try:
        from pyflakes.api import check as _pf
        from pyflakes.reporter import Reporter as _Rp
        import io as _io
        _o = _io.StringIO()
        _pf(s, p, _Rp(_o, _o))
        und = [ln for ln in _o.getvalue().splitlines() if "undefined name" in ln]
        if und:
            print("❌ undefined:", und[:5]); sys.exit(1)
    except ImportError:
        pass
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · {len(REPL)} engine functions rewritten with options (defaults = today) + states · svol · path · {p}")
