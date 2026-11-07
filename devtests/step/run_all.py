# 🪜 the comprehensive test of the graded grid — every suite, once without reinvest and once with it (STEP_CFG reinvest 60%),
#   plus the reinvest suites · one line per suite · a table at the end (also written to --out=FILE)
#   python3 devtests/step/run_all.py [Holy_Dashboard.pyw] [--only=group,...] [--names=suite,...] [--soak=HOURS] [--every=K] [--out=FILE]
#     groups: off (no reinvest) · ri (the same suites with reinvest 60%) · reinvest (t_ri · t_inj · t_wd · t_rel · t_ri_dash) ·
#             cut (t_cut · --move, without and with reinvest) · ui (the browser: ui_first · ui_card · ui_ri) · soak (t_soak · t_osc) ·
#             win (t_win: the strict window · the dashboard's real guard on the 🪜 · the accumulator receiving 🪜 handoffs — v3.36.19)
#   STEP_ENGINE=… tests another engine copy (default: the one extracted from the dashboard) · the browser tests need `unset TMPDIR`
import json, os, subprocess, sys, time

H = os.path.dirname(os.path.abspath(__file__))
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "..", "Holy_Dashboard.pyw")))
ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
NAMES = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--names=")), None)   # suites by name (the 2-h chunks)
SOAK = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--soak=")), "12")
EVERY = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--every=")), "3")
OUT = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--out=")), None)
RI = json.dumps({"reinvest": True, "reinvest_pct": 60})
P = sys.executable

SUITES = [   # (group, name, argv, env)
    ("off", "t_fixes", ["t_fixes.py", DASH, "-q"], {}),
    ("off", "t_inputs", ["t_inputs.py", DASH, "-q"], {}),
    ("off", "t_core", ["t_core.py", "-q"], {}),
    ("off", "t_faults", ["t_faults.py", "-q"], {}),
    ("off", "t_ping", ["t_ping.py", "-q"], {}),
    ("off", "t_first", ["t_first.py", DASH, "-q"], {}),
    ("off", "bt3615_test", ["bt3615_test.py", DASH], {}),
    ("ri", "t_core 💠60%", ["t_core.py", "-q"], {"STEP_CFG": RI}),
    ("ri", "t_faults 💠60%", ["t_faults.py", "-q"], {"STEP_CFG": RI}),
    ("ri", "t_ping 💠60%", ["t_ping.py", "-q"], {"STEP_CFG": RI}),
    ("reinvest", "t_ri", ["t_ri.py", "-q"], {}),
    ("reinvest", "t_inj", ["t_inj.py", "-q"], {}),
    ("reinvest", "t_wd", ["t_wd.py", "-q", f"--every={EVERY}"], {}),
    ("reinvest", "t_rel", ["t_rel.py", "-q", f"--every={EVERY}"], {}),
    ("reinvest", "t_ri_dash", ["t_ri_dash.py", DASH, "-q"], {}),
    ("win", "t_win", ["t_win.py", DASH, "-q"], {}),
    ("cut", "t_cut", ["t_cut.py", "-q"], {}),
    ("cut", "t_cut --move", ["t_cut.py", "--move", "-q"], {}),
    ("cut", "t_cut 💠60%", ["t_cut.py", "-q"], {"STEP_CFG": RI}),
    ("cut", "t_cut --move 💠60%", ["t_cut.py", "--move", "-q"], {"STEP_CFG": RI}),
    ("ui", "ui_first", ["ui_first.py", DASH, "-q"], {}),
    ("ui", "ui_card", ["ui_card.py", DASH, "-q"], {}),
    ("ui", "ui_ri", ["ui_ri.py", DASH, "-q"], {}),
    ("soak", "t_osc", ["t_osc.py", "-q"], {}),
    ("soak", "t_osc 💠60%", ["t_osc.py", "-q"], {"STEP_CFG": RI}),
    ("soak", f"t_soak {SOAK}h", ["t_soak.py", f"--hours={SOAK}", "-q"], {}),
    ("soak", f"t_soak {SOAK}h 💠60%", ["t_soak.py", f"--hours={SOAK}", "-q"], {"STEP_CFG": RI}),
]
rows = []
for grp, name, argv, env in SUITES:
    if (ONLY and grp not in ONLY) or (NAMES and name not in NAMES):
        continue
    e = dict(os.environ, **env)
    if grp == "ui":
        e.pop("TMPDIR", None)
    t0 = time.time()
    try:
        r = subprocess.run([P, os.path.join(H, argv[0])] + argv[1:], capture_output=True, text=True, env=e, timeout=6 * 3600)
        out = (r.stdout.strip().splitlines() or [""])[-1] if r.stdout.strip() else r.stderr.strip()[-300:]
        bad = [ln for ln in r.stdout.splitlines() if ln.startswith("❌")]
        rc = r.returncode
    except subprocess.TimeoutExpired:
        out, bad, rc = "timeout", [], -1
    rows.append((grp, name, rc == 0, round(time.time() - t0), out, bad[:3]))
    print(f"{'✅' if rc == 0 else '❌'} {name}: {out[:220]}  ({round(time.time() - t0)} s)", flush=True)
    for ln in bad[:3]:
        print("     " + ln[:400], flush=True)
txt = "| group | suite | result | seconds |\n|---|---|---|---|\n" + "\n".join(f"| {g} | {n} | {'✅' if okk else '❌'} {o[:120]} | {s} |" for g, n, okk, s, o, _ in rows)
print("\n" + txt)
if OUT:
    open(OUT, "w", encoding="utf-8").write(txt + "\n")
sys.exit(0 if all(r[2] for r in rows) else 1)
