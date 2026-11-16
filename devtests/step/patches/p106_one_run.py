# 🔒 patch 106 (dashboard v3.36.62 · ONE engine per bot folder). The owner (16-11) — his demo DCA+ bot: «البوت ما يكتب ربح … السجل
#   شوفه بالصور» (the log: «⚡ بوت DCA+ انطلق» TWICE in the same second, then «⚠️ تعذّر التأكد من إلغاء بعض أوامر البيع (شبكة) — إعادة
#   المحاولة قبل الشراء» every 5 minutes for hours) · «اهم شي ضاىعات لا يوجد … ولكل البوتات … نفس الكروت ونفس المحركات الاصلية».
#   Read and reproduced: two copies of the same engine ran on the same folder (here: the cycle closed TWICE — the coins bought back
#   twice · his demo: the two copies fought over the paper wallet and one stayed stuck). How: at start the watchdog's first pass and
#   «start all» launch the bots at the same moment, and on Windows the dashboard cannot see a bot's process (bot_pids is Linux-only:
#   /proc) — so neither the check in launch() nor the orphan cleanup could stop the second copy. For a REAL bot that is double orders.
#   ⇒ every bot (real and demo · every kind) starts through `holy_one.py` — a tiny runner the dashboard writes into the folder (like
#     holy_demo.py): it takes an operating-system lock on `.holy_run.lock` for its whole life (fcntl · msvcrt) and writes its pid; a
#     second copy finds the lock held and leaves at once, touching nothing. Then it runs the very same engine file in the same process.
#     The engines are NOT changed. The same lock tells the dashboard — on Windows too — that a bot runs (is_alive · bot_pids from the pid
#     file ⇒ ⏹/🗑 can stop an orphan) · launch() is serialized per folder and does not start a bot this dashboard already runs.
#   python3 devtests/step/patches/p106_one_run.py Holy_Dashboard.pyw
import os, sys

ONE = '''ONE_RUNNER = "holy_one.py"
ONE_LOCK, ONE_PID = ".holy_run.lock", ".holy_run.pid"
_ONE_SRC = r"""# 🔒 Holy one-copy runner — written by the dashboard into the bot's folder (rewritten at every start). ONE engine per folder:
#   an operating-system lock on .holy_run.lock held for the life of this process; a second copy finds it held and leaves at once
#   (it touches nothing). Then the bot's own engine file runs, unchanged, in this same process.
import os, sys, time, runpy

def _take(f):
    if os.name == "nt":
        import msvcrt
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    f = open(".holy_run.lock", "a+")
    for _i in range(10):                      # the dashboard only peeks at the lock (microseconds) — a short wait covers that
        try:
            _take(f)
            break
        except OSError:
            time.sleep(0.2)
    else:
        print("HOLY-ONE: another copy of this bot already runs in this folder — this one stops and touches nothing", flush=True)
        sys.exit(3)
    try:
        with open(".holy_run.pid", "w") as p:
            p.write(str(os.getpid()))
    except Exception:
        pass
    sys.argv = sys.argv[1:]
    sys.path.insert(0, os.getcwd())
    runpy.run_path(sys.argv[0], run_name="__main__")
"""


def _one_write(d):
    """🔒 v3.36.62: مشغّل «نسخة وحدة» بمجلد البوت (يُكتب من جديد بكل إقلاع)"""
    p = os.path.join(d, ONE_RUNNER)
    try:
        if os.path.exists(p) and open(p, encoding="utf-8").read() == _ONE_SRC:
            return True
    except Exception:
        pass
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        f.write(_ONE_SRC)
    os.replace(p + ".tmp", p)
    return True


def _one_held(d):
    """🔒 v3.36.62: نسخة من المحرك تمسك قفل المجلد الآن؟ (نطلّ على القفل بلحظة ونتركه — يشتغل على ويندوز ولينكس)"""
    lp = os.path.join(d, ONE_LOCK)
    if not os.path.exists(lp):
        return False
    try:
        f = open(lp, "a+")
    except Exception:
        return False
    try:
        if os.name == "nt":
            import msvcrt
            f.seek(0)
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                return True
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
            return False
        import fcntl
        try:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return True
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return False
    finally:
        f.close()


def _one_pid(d):
    try:
        return int(open(os.path.join(d, ONE_PID), encoding="utf-8").read().strip() or 0) or None
    except Exception:
        return None


_LAUNCH_LOCKS = {}
'''

R = [
    ('''def _demo_write_runner(d):''', ONE + '''

def _demo_write_runner(d):'''),
    # ── liveness: the lock (Windows included)
    ('''    p = PROCS.get(d)
    if p is not None and p.poll() is None:
        return True, "dash"
    try:
        if time.time() - os.path.getmtime(state_path) < ALIVE_WINDOW:''', '''    p = PROCS.get(d)
    if p is not None and p.poll() is None:
        return True, "dash"
    try:
        if _one_held(d):                                   # 🔒 v3.36.62: قفل «نسخة وحدة» ممسوك ⇒ المحرك يعمل (ويندوز كمان)
            return True, "lock"
    except Exception:
        pass
    try:
        if time.time() - os.path.getmtime(state_path) < ALIVE_WINDOW:'''),
    ('''    out = []
    try:
        if os.name == "nt":
            pass
        else:
            real = os.path.realpath(full)''', '''    out = []
    try:
        if os.name == "nt":
            if _one_held(full) and _one_pid(full):          # 🔒 v3.36.62: ويندوز — عملية المحرك من ملف القفل (كانت ما تنشاف أبداً)
                out.append(_one_pid(full))
        else:
            real = os.path.realpath(full)'''),
    ('''_ENG_SCRIPTS = ("main.py", "reinvest.py", "demo.py", "recur.py", "dca.py", "vpath.py")''',
     '''_ENG_SCRIPTS = ("main.py", "reinvest.py", "demo.py", "recur.py", "dca.py", "vpath.py", "holy_one.py")'''),
    ('''def kill_external(full):
    try:
        if os.name == "nt":''', '''def kill_external(full):
    try:
        if os.name == "nt" and _one_held(full) and _one_pid(full):     # 🔒 v3.36.62: ويندوز — من ملف القفل
            subprocess.run(["taskkill", "/PID", str(_one_pid(full)), "/F", "/T"], capture_output=True, timeout=10, creationflags=0x08000000)
            return True
        if os.name == "nt":'''),
    # ── launch: serialized per folder · not twice · through the runner
    ('''def launch(b):
    sp, hp, lp = paths_of(b)''', '''def launch(b):
    """🔒 v3.36.62: إطلاق واحد بنفس اللحظة لكل مجلد · بوت تشغّله هذي اللوحة ما ينطلق مرة ثانية · كل بوت عبر holy_one.py (نسخة وحدة)"""
    with LOCK:
        lk = _LAUNCH_LOCKS.setdefault(os.path.realpath(b["dir"]), threading.Lock())
    with lk:
        p0 = PROCS.get(b["dir"])
        if p0 is not None and p0.poll() is None:
            return True, "يعمل أصلاً ✅"
        return _launch_do(b)


def _launch_do(b):
    sp, hp, lp = paths_of(b)'''),
    ('''    p = subprocess.Popen([PYTHON_EXE, "-u"] + ([DEMO_RUNNER, script, eng_script] if _demo else [script]), cwd=b["dir"], creationflags=flags,
                         stdout=log_f, stderr=log_f, env=env)''', '''    try:
        _one_write(b["dir"])                              # 🔒 v3.36.62: نسخة وحدة لكل مجلد (قفل نظام التشغيل)
    except Exception as _oe:
        log_f.close()
        return False, f"تعذّر كتابة مشغّل البوت: {type(_oe).__name__}"
    p = subprocess.Popen([PYTHON_EXE, "-u", os.path.join(os.path.abspath(b["dir"]), ONE_RUNNER)]
                         + ([DEMO_RUNNER, script, eng_script] if _demo else [script]), cwd=b["dir"], creationflags=flags,
                         stdout=log_f, stderr=log_f, env=env)'''),
    ('''    time.sleep(2.5)
    if p.poll() is not None:
        reason = _tail_reason(lp)''', '''    time.sleep(2.5)
    if p.poll() is not None:
        try:
            if "HOLY-ONE:" in open(lp, encoding="utf-8", errors="ignore").read():
                LAUNCH_ERR.pop(b["dir"], None)
                return True, "يعمل أصلاً (نسخة أخرى تمسك المجلد) ✅"    # نسخة ثانية رفضت تشتغل — الأولى هي البوت
        except Exception:
            pass
        reason = _tail_reason(lp)'''),
]

if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    for i, (a, b) in enumerate(R):
        if s.count(a) != 1:
            print(f"❌ replacement {i} found {s.count(a)} times — nothing written: {a[:100]!r}"); sys.exit(1)
        s = s.replace(a, b)
    compile(s, p, "exec")
    open(p + ".tmp", "w", encoding="utf-8").write(s)
    os.replace(p + ".tmp", p)
    print(f"✅ {len(R)} replacements · 🔒 one engine per bot folder (holy_one.py · OS lock) · launch serialized · Windows liveness · compiles · {p}")
