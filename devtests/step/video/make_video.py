# 🎬 makes the one-minute video of the graded-grid card: the real dashboard (closed folder · no network) + the real engine on the
#   mock OKX (vid_sim.py) + the browser recording (vid_rec.js) ⇒ an .mp4      python3 devtests/step/video/make_video.py OUT.mp4 [PACE]
import glob, os, shutil, socket, subprocess, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1])
PACE = sys.argv[2] if len(sys.argv) > 2 else "0.6"


def port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


R = tempfile.mkdtemp(prefix="vid_")
P1, P2 = port(), port()
shutil.copy(os.path.join(H, "..", "..", "..", "Holy_Dashboard.pyw"), R)
open(os.path.join(R, "dashboard_config.json"), "w").write('{"port": %d}' % P1)
open(os.path.join(R, "monitor_config.json"), "w").write('{"wallets": [{"name": "main", "api": "FAKE-KEY", "sec": "FAKE-SECRET", "pass": "FAKE-PASS"}]}')
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
procs = []
try:
    d = subprocess.Popen([sys.executable, os.path.join(H, "vid_dash.py"), R, str(P1)], stdout=subprocess.PIPE, text=True, env=env); procs.append(d)
    assert "dashboard up" in d.stdout.readline()
    s = subprocess.Popen([sys.executable, os.path.join(H, "vid_sim.py"), R, str(P2), PACE], stdout=subprocess.PIPE, text=True, env=env); procs.append(s)
    assert "sim ready" in s.stdout.readline()
    time.sleep(2.5)                                       # the bot's birth save · the dashboard sees its folder
    vd = tempfile.mkdtemp(prefix="vidrec_")
    r = subprocess.run(["node", os.path.join(H, "vid_rec.js"), f"http://127.0.0.1:{P1}/", f"http://127.0.0.1:{P2}", vd],
                       capture_output=True, text=True, timeout=240, cwd="/tmp", env=env)
    print(r.stdout.strip()[-600:] or r.stderr.strip()[-1500:])
    webm = sorted(glob.glob(os.path.join(vd, "*.webm")))
    assert webm, "no video recorded"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", webm[-1], "-c:v", "libx264", "-preset", "medium", "-crf", "22",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], check=True)
    print("✅", OUT, os.path.getsize(OUT) // 1024, "KB")
finally:
    for p in procs:
        p.kill()
    shutil.rmtree(R, ignore_errors=True)
