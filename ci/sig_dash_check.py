# 🎯 the dashboard's own signals (v3.36.66) end to end on REAL OKX prices — exactly what runs on the owner's computer:
#   the history of ~34 coins fetched by the dashboard (public data) → the catalog built by its own worker process (no network) → a scan at
#   the last close → the notifications it would send (printed here, not sent) · timings · memory · the catalog's best and rare ones ·
#   🧭 the compass now · the weekly estimate for a few thresholds
#   python3 ci/sig_dash_check.py Holy_Dashboard.pyw  ⇒ lines starting with HOLYDASH
import importlib.machinery, importlib.util, json, os, resource, shutil, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="sig_dash_")
shutil.copy(DASH, os.path.join(R, "Holy_Dashboard.pyw"))
os.chdir(R)
ld = importlib.machinery.SourceFileLoader("hd", os.path.join(R, "Holy_Dashboard.pyw"))
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld))
sys.argv = ["x"]
ld.exec_module(m)
T0 = time.time()


def P(*a):
    print("HOLYDASH", *a, flush=True)


SENT = []
m.tg_send = lambda text, *a, **k: SENT.append(text) or True
m.app_feed_push = lambda *a, **k: True
m._okx_post = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no orders"))
json.dump({"ticker_coins": ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "LINK", "SUI"], "sg_thr": 65, "sg_min": 15}, open(m.APP_CFG, "w"))
P("dashboard", m.APP_VERSION, "· universe", len(m._sg_universe()), "coins:", " ".join(s.split("-")[0] for s in m._sg_universe()))
# the macro series and fear & greed — the dashboard's own fetchers into its own files (as pro_loop / fc_loop do)
db, now = {}, time.time()
for fn in ("_pro_vix", "_pro_dxy", "_pro_us10", "_pro_epu", "_pro_gpr", "_pro_tone"):
    try:
        getattr(m, fn)(db, now)
    except Exception as ex:
        P(fn, "error", ex)
try:
    m._pro_ls(db, now, ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "LINK", "SUI"]); m._pro_tk(db, now, ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "LINK", "SUI"])
except Exception as ex:
    P("pro error", ex)
m.save_json_atomic(m.PRO_FILE, db)
fdb = {}
m._fc_fng(fdb)
m.save_json_atomic(m.FC_FILE, fdb)
P("macro:", " · ".join(f"{k} {len((db.get(k) or {}).get('d') or {})}" for k in ("vix", "dxy", "us10", "epu", "gpr", "tone")), "· fng", len((fdb.get("fng") or {}).get("d") or {}))
# ① first tick: history + the catalog worker
t1 = time.time()
m.sg_tick()
P(f"① history fetched in {time.time() - t1:.0f}s · candles file {os.path.getsize(m.SG_CFILE) / 1e6:.1f} MB · bad: {m._sg_st().get('bad')}")
j = m._SG.get("build")
t2 = time.time()
while j and not m._sg_job_done(j):
    time.sleep(10)
    pr = m._sg_job_prog(j)
    if int(time.time() - t2) % 120 < 10:
        P(f"   building … {pr.get('pct')}% {pr.get('msg')}")
P(f"① catalog worker done in {time.time() - t2:.0f}s · its answer {m._sg_job_out(j) if j else None}")
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
P(f"   worker peak memory {ru.ru_maxrss / 1024:.0f} MB · CPU {ru.ru_utime + ru.ru_stime:.0f}s")
# ② second tick: the scan of the last closes (the build's ending is picked up)
st = m._sg_st()
st.pop("t_4H", None); st.pop("t_1D", None)
m._sg_save(st)
t3 = time.time()
m.sg_tick()
P(f"② scan + notify in {time.time() - t3:.0f}s · error: {m._SG.get('err') or '—'}")
cat = m._sg_cat()
st = m._sg_st()
E = cat["e"]
P(f"catalog: {len(E)} entries from {len(cat['coins'])} coins · sizes " + " ".join(f"{k}:{sum(1 for e in E if len(e['k']) == k)}" for k in range(1, 7))
  + f" · rare {sum(1 for e in E if e['rare'])} · weeks of test {cat['wk']} · built in {cat.get('secs')}s")
P("random:", json.dumps(cat["base"]))
for fr in ("4H", "1D"):
    for side in (1, -1):
        b = cat["base"][f"{fr}|{side}"]
        top = [e for e in E if e["f"] == fr and e["s"] == side and e["nt"] >= 15 and len(e["k"]) > 1]
        top.sort(key=lambda e: -(e["wt"] / e["nt"]))
        held = sum(1 for e in top if e["wt"] / e["nt"] * 100 > b["ht"] and e["mt"] > b["mt"])
        P(f"══ {fr} {'BUY ' if side > 0 else 'SELL'} combos with ≥15 test cases: {len(top)} · better than random on the test: {held} (random {b['ht']}%)")
        for e in top[:8]:
            P(f"   {e['wt']}/{e['nt']} ({e['wt'] / e['nt'] * 100:.0f}%) on {e.get('nd')} different days · mean {e['mt'] * 100:+.2f}% · learn {e['wl']}/{e['nl']} · {e['ty']} · "
              + " + ".join(m._sg_name(k, side) for k in e["k"]))
        rr = [e for e in E if e["f"] == fr and e["s"] == side and e["rare"]]
        rh = [e for e in rr if e["nt"] >= 2 and e["wt"] / e["nt"] * 100 > b["ht"] and e["mt"] > b["mt"]]
        P(f"   💎 rare: {len(rr)} · judged (≥2 test cases) {sum(1 for e in rr if e['nt'] >= 2)} · held {len(rh)}")
        for e in sorted(rh, key=lambda e: -e["wt"] / e["nt"])[:4]:
            P(f"   💎 learn {e['wl']}/{e['nl']} · test {e['wt']}/{e['nt']} ({e.get('nd')} days) mean {e['mt'] * 100:+.2f}% · " + " + ".join(m._sg_name(k, side) for k in e["k"]))
c = st.get("comp") or {}
P(f"🧭 compass now: {c.get('s')} since {c.get('days')} days · BTC above 200d {c.get('btc')} · {c.get('k')}/{c.get('n')} above 50d · history {json.dumps(cat.get('compass'))}")
for thr, mn in ((55, 10), (60, 15), (65, 15), (70, 20), (75, 20)):
    e_ = m.sg_estimate(m._sg_cfg_merge(m.sg_cfg(), {"thr": thr, "min": mn}))
    P(f"estimate {thr}% · {mn} cases: ≈ {e_['wk']} a week ({e_['n']} pass) · after the cap {e_['cut']}")
mine = m.sg_coins()
for s in mine:
    F = (st.get("now") or {}).get(s) or {}
    P(f"now {s}: " + " · ".join(f"{fr} alive {len(x.get('alive') or [])} fired {len(x.get('fired') or [])}" for fr, x in F.items()))
P(f"pending in the live record: {len(st.get('pend') or [])} · notifications sent: {len(SENT)}")
for t in SENT[:3]:
    P("── message ──\n" + t)
# with a lower threshold — what would have come at this close
cf = m._sg_cfg_merge(m.sg_cfg(), {"thr": 55, "min": 10})
cf["rnd"] = False
st2 = {k: v for k, v in st.items() if k in ("rec",)}
sc_dir = os.path.join(m.SG_DIR, "job_scan")
sc = m._sg_job_out({"jd": sc_dir}) or {}
if sc.get("ok"):
    bl = m._sg_process(sc, ["4H", "1D"], st2, cf, cat, None, time.time())
    P(f"at 55% · 10 cases (no random rule) this close would send {len(bl)} blocks:")
    for b in bl[:5]:
        P("── block ──\n" + b["t"] + "\n" + b["b"])
P(f"done in {time.time() - T0:.0f}s")
shutil.rmtree(R, ignore_errors=True)
