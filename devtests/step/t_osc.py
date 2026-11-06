# 🪜 🌊 the owner's scenarios (6-11) on top of t_soak: very fast oscillation · wild swings with jumps · a first sell of 0.5% ·
#   0.3% · 0.2% · a 100$ buy split into 20 sells (and how it is kept: on OKX / in the bot's memory · the state file) · a coin
#   with whole-coin quantities — every one with power cuts at random moments and a flaky API, audited at every loop
#   (books = wallet · nothing twice · nothing lost · every sell paid · never over / under its price · log = books)
#   python3 devtests/step/t_osc.py [-q] [--only=name,...] [--hours=K (each scenario, default 6)]
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t_soak import soak, say

Q = "-q" in sys.argv
ONLY = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
H = float(next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--hours=")), "6"))
DOGE = ("DOGE-USDT", "0.00001", "1", "10", 0.15)
SCEN = [
    ("fast_osc", "very fast oscillation (a wave crossing the levels every 20 s–4 min · a new price every 3 s)",
     dict(profile="osc", seed=11, cfg={"step_parts": 3, "step_sell": 0.005})),
    ("wild", "wild swings + jumps up to ±10% every few minutes",
     dict(profile="wild", seed=12, cfg={"step_parts": 3, "step_sell": 0.005})),
    ("first_05", "first sell 0.5% · between sells 0.5% · fast oscillation",
     dict(profile="osc", seed=13, cfg={"step_parts": 4, "step_sell": 0.005, "step_first": 0.005})),
    ("first_03", "first sell 0.3% · between sells 0.2% · fast oscillation",
     dict(profile="osc", seed=14, cfg={"step_parts": 5, "step_sell": 0.002, "step_first": 0.003})),
    ("first_02", "first sell 0.2% (just above the two fees 0.16%) · between sells 0.3% · wild",
     dict(profile="wild", seed=15, cfg={"step_parts": 4, "step_sell": 0.003, "step_first": 0.002})),
    ("big_20", "100$ per buy split into 20 sells (5$ each) · first sell 0.5% · between 0.25% · wild swings",
     dict(profile="wild", seed=16, cfg={"usd_value": 100.0, "step_parts": 20, "step_sell": 0.0025, "step_first": 0.005,
                                        "grid_percentage": 0.03}, storage=True)),
    ("doge", "DOGE (whole coins) · first sell 0.3% · between 0.4% · fast oscillation",
     dict(profile="osc", seed=17, sym=DOGE, cfg={"step_parts": 4, "step_sell": 0.004, "step_first": 0.003, "usd_value": 30.0})),
]
res = []
for name, title, kw in SCEN:
    if ONLY and name not in ONLY:
        continue
    st = kw.pop("storage", False)
    rep, b, ex = soak(hours=H, storage=True, **kw)
    res.append(rep["ok"])
    if not Q or not rep["ok"]:
        say(rep, f"{name}: {title}")
    if name == "big_20" and (not Q or not rep["ok"]):
        S = b.st["slots"]
        levels = {}
        for s in S.values():
            levels.setdefault(s["j"], []).append(s)
        sep = all(len(v) == 20 for v in levels.values())
        print(f"   🗂 100$ × 20: {len(levels)} levels × 20 slots = {len(S)} separate slots (one order each, never merged: {sep}) · "
              f"on OKX at most {rep['peak_live'][0]} buys / {rep['peak_live'][1]} sells (window 8 per side) · the rest waits in the "
              f"bot's memory (peak {rep['peak_mem'][0]} buys / {rep['peak_mem'][1]} sells) · state file ≤ {rep['peak_state_kb']:.0f} KB", flush=True)
        res[-1] = res[-1] and sep
print(f"{sum(res)} ok · {len(res) - sum(res)} failed")
sys.exit(0 if all(res) else 1)
