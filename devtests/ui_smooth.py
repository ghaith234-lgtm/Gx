# 🎬 v3.36.35 — the owner (13-11): «بعض الانميشن يقطع افحصهم كلهم» — every window motion measured and checked on a phone (CPU ×4).
#   Every card kind in a closed folder (devtests/seed_cards.py: fake keys · no network · nothing launched) · the steps in ui_smooth.js
#   python3 devtests/ui_smooth.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import os, shutil, socket, subprocess, sys, tempfile

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
sys.path.insert(0, H)
import seed_cards                                             # noqa: E402


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="ui_smooth_")
P1 = port()
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
rc, d = 1, None
try:
    seed_cards.seed(R, DASH)
    d = subprocess.Popen([sys.executable, os.path.join(H, "step", "video", "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env)
    assert "dashboard up" in d.stdout.readline()
    r = subprocess.run(["node", os.path.join(H, "ui_smooth.js"), f"http://127.0.0.1:{P1}/"] + (["-q"] if Q else []),
                       capture_output=True, text=True, timeout=900, cwd="/tmp", env=env)
    print(r.stdout.strip() or r.stderr.strip()[-1500:])
    rc = r.returncode
finally:
    if d:
        d.kill()
    shutil.rmtree(R, ignore_errors=True)
sys.exit(rc)
