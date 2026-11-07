# devtests — test tools kept in the repository

Since v3.36.15 (6-11: the session machine was replaced and its scratch folder was lost) the test tools for the
work in progress live here, so they survive a lost machine. Only fake keys and a mock exchange are used — no
secrets, no network. The APK signing keystore never goes here.

| Path | What |
|---|---|
| `step/extract_engine.py` | writes the 🪜 graded-grid engine embedded in `Holy_Dashboard.pyw` to `step/eng/main_step.py` (ignored by git) |
| `step/embed_engine.py` | the only way a changed engine goes back into the dashboard: replaces just the `_GRIDS_B64` text, refuses unless the engine compiles, decodes back exactly, and nothing else in the dashboard changed (AST) — proven on a copy 6-11 |
| `step/bt3615_test.py` | 🧪 the trial path runs the real graded-grid engine in its box (XRP · SOL · PEPE · v3.36.18: + 💠 reinvest 100% / 50% from the form) — `python3 devtests/step/bt3615_test.py Holy_Dashboard.pyw` |
| `step/okxsim.py` | the mock OKX (fake clock · fills · partial fills · STP · rejections · latency · faults · power cuts) and the runner that drives the real engine's `start_bot()` and audits books = wallet at every loop · `STEP_ENGINE=…` tests another engine copy · `STEP_CFG='{…}'` changes the default settings of every suite |
| `step/t_core.py` | the owner's example step by step · random markets on 4 coin kinds · chase · floor · short coins · buttons · orphans (17) |
| `step/t_faults.py` | lost answers · dropped and late sends · internet down · rejections · lost cancels · manual cancels · a flaky API (10) |
| `step/t_ping.py` | high ping 0.3 · 1 · 3 · 4.9 s and spiky (5) |
| `step/t_cut.py` | a power cut at every moment of a story (4546 moments) — the same fills, profit, slots and log as with no cut · `--move` the price moves while off · `-jN` · `--every=K` |
| `step/t_findings.py` | probes of suspected weaknesses (F1–F6 · F8 · F9) — they print, they do not pass or fail |
| `step/REVIEW.md` | the chunk-by-chunk review of the engine: every finding, its proof and the proposed fix (waiting for the owner) |
| `step/t_first.py` | v3.36.16 the first sell distance: layout · table = engine · no sell that loses · the engine on the mock OKX (22) |
| `step/ui_first.py` + `ui_first.js` | v3.36.16 in a real browser (Playwright · only 127.0.0.1): the two fields · the body sent · the table 1.01 · 1.015 · 1.02 · the refusals · the card's line (9) · `--shot=/abs/path.png` · run with `unset TMPDIR` |
| `step/t_inputs.py` | v3.36.16 F7: nan / inf in the form or a hand-written config are refused (5) |
| `step/t_fixes.py` | v3.36.17 the owner-approved fixes as must-pass tests: F9 · F10 · F8 (engine + the dashboard's delete) · F2 — each fails on the engine before its fix |
| `step/t_soak.py` | the long run: hours · days · `--forever` — random power cuts (off 0 s…5 min, the price moving while off) · a flaky API · the internet down · fast oscillation / wild jumps · audited every loop · a report of how the bot recovered and how it stores its orders |
| `step/t_osc.py` | the owner's scenarios on t_soak (6 h each): very fast oscillation · wild swings · first sell 0.5 / 0.3 / 0.2% · 100$ × 20 sells (storage) · DOGE (7) |
| `step/video/` | 🎬 the one-minute video of the 🪜 card: the real dashboard (closed folder · no network) + the real engine on the mock OKX (an «OKX side» panel: the bot's open orders by level and part · the price · its fills · profit · books = wallet) · an order deleted by hand · a power cut while the price moves · a −5% jump · oscillation — `python3 devtests/step/video/make_video.py OUT.mp4` (run with `unset TMPDIR`) |
| `step/ui_card.py` + `ui_card.js` | v3.36.18 the 🪜 card in a real browser, every skin (old · ج · ب · OKX), the real engine trading on the mock OKX: the vertical price ruler = the bot's slots (a line per buy level with its count · a line per published sell · each at its price · one colour per level) · a tap ⇒ the details · a ♾️ grid card next to it unchanged (17) — `unset TMPDIR` |
| `step/t_ri.py` | v3.36.18 💠 reinvest on the 🪜 engine (the grid's rules, per slot): 100% (💠 line · no sale line · total_profit untouched · whole lots at the slot's buy price · the buy OKX gets = base + growth · bigger profit each round) · 50% (both lines, the halves add up) · 0% = no reinvest · the percentage changed live · DOGE whole coins (cents carried) · a power cut between a sale's two lines · random markets (16) — the audit: real profit = total_profit + credited · pots = credited · each sale's lines once |
| `step/t_inj.py` | v3.36.18 💉 injection into one slot by its side (the grid's apply_injections): coins into a published sell (amend-order) / a memory sell · dollars into a published buy / a memory buy / a sell (⇒ its pot) · refusals · exactly once (OKX applies late · its answer lost · never reached · the same request again) · the order fills before the resize · a flaky API · a shrink of a partly filled order · a power cut at every moment (`--every=K`) (17) |
| `step/t_wd.py` | v3.36.18 ➖ withdrawal from one slot by its side (the grid's apply_withdrawals): buy side dollars (profit → total_profit · capital → wallet) · sell side coins (profit → the accumulator's handoff at their real cost · capital → wallet) · dollars not inside an order · the slot changed side meanwhile · a partly filled order · refusals · exactly once · the race · a power cut at every moment (13) |
| `step/t_rel.py` | v3.36.18 🔓 the release and the unwind (the grid's release / _unwind_step): everything now (the grown published orders shrink to their base at OKX · one handoff · capital back) · the setting off / on again · the flag alone · OKX refuses ⇒ retried every minute · the grown order filled first ⇒ released at its sale · exactly once · a power cut at every moment (11) |
| `step/t_ri_dash.py` | v3.36.18 💠 the dashboard's side for 🪜: deploy with reinvest · the trial path · the 🔄 / 💉 / ➖ / ⚖️ actions write what the engine reads · the snapshot from the slots (io · desync) · launch never wraps 🪜 in the grid's reinvest.py (16) |
| `step/ui_ri.py` + `ui_ri.js` + `ri_sim.py` | v3.36.18 💠 in a real browser: the real dashboard + the real engine with reinvest on the mock OKX (paced in real time, in the dashboard's folder): the 🔄 chip · «💠 سلّم الإعادة» by level and part · ＋ / ➖ / ⚖️ / 🔄 off reach the engine and it applies them · the deploy form's 💠 box (10) — `unset TMPDIR` |
| `step/run_all.py` | v3.36.18 the comprehensive test: every 🪜 suite without reinvest and again with it (`STEP_CFG` reinvest 60%) + the reinvest suites + the power cuts + the browser + the long runs · a results table (`--only=off,ri,reinvest,cut,ui,soak` · `--soak=HOURS` · `--out=FILE`) |
| `step/patches/` | every engine/dashboard change as an exact-text replacement script (each old text found once · AST scope check) |
| `step/STATE.md` | the work state — read it first in a new session |
| `tools/map_remap.py` · `tools/map_fix_bt.py` | MAP.md line remap between two dashboards + the trial-path rows (rebuilt 6-11, checked against git history) |
