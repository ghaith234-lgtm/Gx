# devtests — test tools kept in the repository

Since v3.36.15 (6-11: the session machine was replaced and its scratch folder was lost) the test tools for the
work in progress live here, so they survive a lost machine. Only fake keys and a mock exchange are used — no
secrets, no network. The APK signing keystore never goes here.

| Path | What |
|---|---|
| `step/extract_engine.py` | writes the 🪜 graded-grid engine embedded in `Holy_Dashboard.pyw` to `step/eng/main_step.py` (ignored by git) |
| `step/bt3615_test.py` | 🧪 the trial path runs the real graded-grid engine in its box (XRP · SOL · PEPE) — `python3 devtests/step/bt3615_test.py Holy_Dashboard.pyw` |
| `tools/map_remap.py` · `tools/map_fix_bt.py` | MAP.md line remap between two dashboards + the trial-path rows (rebuilt 6-11, checked against git history) |
