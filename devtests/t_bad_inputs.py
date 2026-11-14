# 🩺 v3.36.50 — the full audit, batch 1: bad inputs must get an answer, never take the dashboard down. The owner (14-11): «سوي فحص لكل
#   البوت واكتشف ان هناك اخطاء بكل شي». Found by sending every server request bad inputs (25,601 requests in a closed folder); this
#   keeps the ones that broke: ① DCA safety-order count without a limit (the table filled the memory — the dashboard went down)
#   ② a JSON body that is not an object ③ the app's version not a number ④ control without «dir» ⑤ settings «value» not an object
#   ⑥ two divisions by zero (DCA table · levels-above calculator) ⑦ the leftover «shutdown_beacon» that stopped everything
#   python3 devtests/t_bad_inputs.py [Holy_Dashboard.pyw] [-q]        (run with `unset TMPDIR`)
import http.client, json, os, resource, shutil, socket, subprocess, sys, tempfile, time

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
sys.path.insert(0, H)
_a = sys.argv; sys.argv = [_a[0], tempfile.gettempdir()]
import seed_cards                                             # noqa: E402
sys.argv = _a
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


s = socket.socket(); s.bind(("127.0.0.1", 0)); P = s.getsockname()[1]; s.close()
R = tempfile.mkdtemp(prefix="t_badin_")
env = {k: v for k, v in os.environ.items() if k != "TMPDIR"}
seed_cards.seed(R, DASH)
err = open(os.path.join(R, "_stderr.txt"), "w")
d = subprocess.Popen([sys.executable, os.path.join(H, "step", "video", "vid_dash.py"), R, str(P)], stdout=subprocess.PIPE, stderr=err, text=True, env=env,
                     preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_AS, (3 * 2**30, 3 * 2**30)))   # a runaway table fails here, not the machine
assert "dashboard up" in d.stdout.readline()


def post(path, body=None, raw=None, t=20):
    t0 = time.time()
    try:
        c = http.client.HTTPConnection("127.0.0.1", P, timeout=t)
        c.request("POST", path, body=raw if raw is not None else json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        r = c.getresponse(); x = r.read().decode("utf-8", "replace"); c.close()
        try:
            j = json.loads(x)
        except Exception:
            j = None
        return {"st": r.status, "j": j, "sec": round(time.time() - t0, 2)}
    except Exception as e:
        return {"st": None, "j": None, "err": f"{type(e).__name__}", "sec": round(time.time() - t0, 2), "dead": d.poll() is not None}


try:
    DCA = {"symbol": "SOL-USDT", "base_price": 100, "base_order_qty": 1, "avg_order_qty": 1, "first_deviation": 1, "step_multiplier": 1,
           "size_multiplier": 1, "take_profit_pct": 1, "max_safety_orders": 4, "dca_type": "dca_buy"}
    a = post("/api/dca_preview", DCA)
    ok("the DCA table answers a normal plan (5 rows)", a["st"] == 200 and isinstance(a["j"], dict) and len(a["j"].get("rows") or []) == 5, a)
    b = post("/api/dca_preview", {**DCA, "max_safety_orders": 99999999})
    ok(f"① DCA «عدد أوامر الأمان» = 99,999,999 ⇒ an answer in {b['sec']} s saying the limit (it filled the memory and the dashboard went down)",
       b["st"] == 200 and b["sec"] < 3 and "الحد" in str((b["j"] or {}).get("msg")) and d.poll() is None, b)
    c = post("/api/deploy_dca", {**DCA, "max_safety_orders": 5000, "wallet": "main"})
    ok("① … and a DCA bot cannot be deployed with more than the limit (a clear message)", c["st"] == 200 and (c["j"] or {}).get("ok") is False and "الحد" in str((c["j"] or {}).get("msg")), c)
    bad = [post("/api/control", raw=x) for x in (b"[]", b'"text"', b"null", b"7")]
    ok("② a body that is JSON but not an object ⇒ «طلب غير صالح» (it cut the connection)", all(x["st"] == 400 and (x["j"] or {}).get("ok") is False for x in bad), bad)
    e = post("/api/app/pair", {"name": "phone", "iid": "x1", "code": "abc"})
    ok("③ pairing the app with a version that is not a number ⇒ an answer", e["st"] is not None and e["j"] is not None, e)
    f = [post("/api/control", {"action": "stop"}), post("/api/control", {"action": "stop", "dir": None}), post("/api/control", {"action": "stop", "dir": 5}),
         post("/api/control", {"action": "edit", "dir": ["x"], "value": "abc"})]
    ok("④ a control request without «dir» (or not text) ⇒ an answer, nothing done", all(x["st"] is not None and x["j"] is not None and x["j"].get("ok") is False for x in f), f)
    g = [post("/api/control", {"action": a_, "value": v}) for a_ in ("guard_ack", "ticker_set", "pxa_set", "ina_set", "guard_cfg") for v in ("abc", 5, [1])]
    ok("⑤ the five settings actions with «value» not an object ⇒ an answer", all(x["st"] is not None and x["j"] is not None for x in g), [x for x in g if x["j"] is None][:3])
    h = post("/api/dca_preview", {**DCA, "dca_type": "dca", "take_profit_pct": 100})
    i = post("/api/grid_up_calc", {"symbol": "SOL-USDT", "grid_pct": 1e-15, "usd_value": 10, "forced_base": 100, "top": 200})
    ok("⑥ no division by zero: a sell-DCA target of 100% · a grid step too small to count ⇒ a message each", h["j"] is not None and i["j"] is not None and i["j"].get("ok") is False, (h, i))
    k = post("/api/control", {"action": "shutdown_beacon"})
    time.sleep(1.2)
    ok("⑦ the leftover «shutdown_beacon» no longer stops the bots and closes the dashboard", d.poll() is None and k["st"] is not None and post("/api/control", {"action": "mute"})["st"] == 200, k)
    err.flush()
    tb = open(err.name, encoding="utf-8", errors="replace").read().count("Traceback")
    ok("the server wrote no error trace through all of it and is still up", tb == 0 and d.poll() is None, tb)
finally:
    d.kill(); err.close()
    shutil.rmtree(R, ignore_errors=True)
print(f"✅ t_bad_inputs: {sum(res)}/{len(res)}" if all(res) else f"❌ t_bad_inputs: {sum(res)}/{len(res)}")
sys.exit(0 if all(res) else 1)
