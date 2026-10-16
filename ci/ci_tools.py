# helpers for ci/apk_check.sh: on-screen texts · tap by text · tiny screenshot in the log · our notifications
import base64, io, re, sys
import xml.etree.ElementTree as ET


def nodes(path):
    try:
        return list(ET.parse(path).iter("node"))
    except Exception:
        return []


def center(b):
    x1, y1, x2, y2 = map(int, re.findall(r"\d+", b))
    return (x1 + x2) // 2, (y1 + y2) // 2


cmd = sys.argv[1]
if cmd == "texts":
    seen = []
    for n in nodes(sys.argv[2]):
        for t in (n.get("text"), n.get("content-desc")):
            t = (t or "").strip()
            if t and t not in seen:
                seen.append(t)
    print(f"HOLYUI {sys.argv[3]}: " + " | ".join(seen)[:2500])
elif cmd == "find":
    want = sys.argv[3]
    best = None
    for n in nodes(sys.argv[2]):
        t = (n.get("text") or n.get("content-desc") or "").strip()
        x1, y1, x2, y2 = map(int, re.findall(r"\d+", n.get("bounds") or "[0,0][0,0]"))
        if x2 <= x1 or y2 <= y1:          # zero-size (e.g. a window the old WebView can't lay out) — not tappable
            continue
        if t == want:
            best = n
            break
        if want in t and best is None:
            best = n
    if best is not None:
        print("%d %d" % center(best.get("bounds")))
elif cmd == "switch":            # the first switch that is ON (Android's notification-channel page: the channel's own toggle)
    for n in nodes(sys.argv[2]):
        if "Switch" in (n.get("class") or "") and n.get("checked") == "true":
            print("%d %d" % center(n.get("bounds")))
            break
elif cmd == "img":
    from PIL import Image
    try:
        im = Image.open(sys.argv[2]).convert("RGB")
        w = 300 if im.width < im.height else 480
        im = im.resize((w, int(im.height * w / im.width)))
        bo = io.BytesIO()
        im.save(bo, "JPEG", quality=50)
        print(f"HOLYIMG {sys.argv[3]} " + base64.b64encode(bo.getvalue()).decode())
    except Exception as e:
        print(f"HOLYIMG {sys.argv[3]} ERROR {e}")
elif cmd == "apk":               # 1.4: the APK embedded in a dashboard source (stdin) ⇒ stdout (to install the previous app first)
    m = re.search(r'^APP_APK_B64 = "([A-Za-z0-9+/=]+)"', sys.stdin.read(), re.M)
    if m:
        sys.stdout.buffer.write(base64.b64decode(m.group(1)))
elif cmd == "notif":
    pkg = sys.argv[2]
    txt = sys.stdin.read()
    blocks = re.split(r"\n\s*NotificationRecord\(", txt)
    n = 0
    for b in blocks[1:]:
        if f"pkg={pkg}" not in b.split("\n", 1)[0]:
            continue
        n += 1
        head = b.split("\n", 1)[0]
        keep = [re.search(r"id=\d+", head).group(0) if re.search(r"id=\d+", head) else ""]
        for key in ("channel=NotificationChannel{mId='", "groupKey=", "android.title=", "android.text=", "android.subText=", "android.largeIcon=", "flags=", "vis="):
            for line in b.split("\n"):
                if key in line:
                    keep.append(line.strip()[:160])
                    break
        print("HOLYNOTIF " + " ‖ ".join(k for k in keep if k))
    print(f"HOLYCI notifications from {pkg}: {n}")
