# devtests — test tools kept in the repository

Since v3.36.15 (6-11: the session machine was replaced and its scratch folder was lost) the test tools for the
work in progress live here, so they survive a lost machine. Only fake keys and a mock exchange are used — no
secrets, no network. The APK signing keystore never goes here.

| Path | What |
|---|---|
| `step/extract_engine.py` | writes the 🪜 graded-grid engine embedded in `Holy_Dashboard.pyw` to `step/eng/main_step.py` (ignored by git) |
| `step/embed_engine.py` | the only way a changed engine goes back into the dashboard: replaces just the `_GRIDS_B64` text, refuses unless the engine compiles, decodes back exactly, and nothing else in the dashboard changed (AST) — proven on a copy 6-11 |
| `step/bt3615_test.py` | 🧪 the trial path runs the real graded-grid engine in its box (XRP · SOL · PEPE) — `python3 devtests/step/bt3615_test.py Holy_Dashboard.pyw` |
| `step/okxsim.py` | the mock OKX (fake clock · fills · partial fills · STP · rejections · latency · faults · power cuts) and the runner that drives the real engine's `start_bot()` and audits books = wallet at every loop · `STEP_ENGINE=…` tests another engine copy · `STEP_CFG='{…}'` changes the default settings of every suite |
| `step/t_core.py` | the owner's example step by step · random markets on 4 coin kinds · chase · floor · short coins · buttons · orphans (17) |
| `step/t_faults.py` | lost answers · dropped and late sends · internet down · rejections · lost cancels · manual cancels · a flaky API (10) |
| `step/t_ping.py` | high ping 0.3 · 1 · 3 · 4.9 s and spiky (5) |
| `step/t_cut.py` | a power cut at every moment of a story (4546 moments) — the same fills, profit, slots and log as with no cut · `--move` the price moves while off · `-jN` · `--every=K` |
| `step/t_findings.py` | probes of suspected weaknesses (F1–F6) — they print, they do not pass or fail |
| `step/t_first.py` | v3.36.16 the first sell distance: layout · table = engine · no sell that loses · the engine on the mock OKX (22) |
| `step/ui_first.py` + `ui_first.js` | v3.36.16 in a real browser (Playwright · only 127.0.0.1): the two fields · the body sent · the table 1.01 · 1.015 · 1.02 · the refusals · the card's line (9) · `--shot=/abs/path.png` · run with `unset TMPDIR` |
| `step/t_inputs.py` | v3.36.16 F7: nan / inf in the form or a hand-written config are refused (5) |
| `step/patches/` | every engine/dashboard change as an exact-text replacement script (each old text found once · AST scope check) |
| `step/STATE.md` | the work state — read it first in a new session |
| `tools/map_remap.py` · `tools/map_fix_bt.py` | MAP.md line remap between two dashboards + the trial-path rows (rebuilt 6-11, checked against git history) |
