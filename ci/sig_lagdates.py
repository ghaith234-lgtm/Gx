# 🔬 how late each macro reading is published: the newest day each source gives NOW (the dashboard's own fetchers, public data, no keys)
#   python3 ci/sig_lagdates.py Holy_Dashboard.pyw  ⇒ lines starting with HOLYLAG
import importlib.util, importlib.machinery, os, sys, tempfile, time

DASH = os.path.abspath(sys.argv[1])
R = tempfile.mkdtemp(prefix="sig_lag_")
ld = importlib.machinery.SourceFileLoader("hd", DASH)
sys.argv = ["x"]
os.chdir(R)
m = importlib.util.module_from_spec(importlib.util.spec_from_loader("hd", ld))
ld.exec_module(m)
NOW = time.time()
DB = {}
for k, fn in (("vix", "_pro_vix"), ("dxy", "_pro_dxy"), ("us10", "_pro_us10"), ("epu", "_pro_epu"), ("gpr", "_pro_gpr"), ("tone", "_pro_tone")):
    try:
        getattr(m, fn)(DB, NOW)
        ks, vs = m._pro_sorted(DB.get(k))
        print("HOLYLAG", k, "newest day:", time.strftime("%Y-%m-%d", time.gmtime(ks[-1])) if ks else "—",
              f"· {(NOW - ks[-1]) / 86400:.1f} days before now" if ks else "", f"· {len(ks)} days", flush=True)
    except Exception as ex:
        print("HOLYLAG", k, "error", type(ex).__name__, ex, flush=True)
try:
    r = m._fc_fng(DB)
    print("HOLYLAG fng newest day:", time.strftime("%Y-%m-%d", time.gmtime(r[0][-1])), f"· {(NOW - r[0][-1]) / 86400:.1f} days before now", flush=True)
except Exception as ex:
    print("HOLYLAG fng error", ex)
print("HOLYLAG now:", time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(NOW)))
