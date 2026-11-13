# 🪟 the guard of the one window frame (v3.36.34) — the owner (13-11): «اهم شي عند اضافة تصميم جديد في المستقبل يصير نفس النمط».
#   Reads the dashboard's page and fails when a future change builds a window outside the frame:
#   ① a new full-screen overlay in the CSS (position:fixed over the whole screen) other than the known layers — the splash · the trial
#      window · the pages · the window/dialog layer · the notifications (+ its scrim)
#   ② a new element added straight onto the page body other than the known ones (the trial window · a download link · the closing copy ·
#      a line's popover · the stick man's canvas)
#   ③ every window written in place opens with its title (<h2…>) — the frame makes it the header that stays on top
#   ④ the frame itself is intact: showModal puts the ✕ and the body · showDialog exists · hideModal plays the closing · holyBack walks the
#      stack first · the browser's back is watched · ⚙️ has «حركة فتح النوافذ» · Esc is the back button · every confirmation helper keeps
#      the dialog size (askConfirm → showDialog)
#   python3 devtests/t_windows.py [Holy_Dashboard.pyw] [-q]
import os, re, sys

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
DASH = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "Holy_Dashboard.pyw")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:900]}"), flush=True)


s = open(DASH, encoding="utf-8").read()
page = s[s.index("<html", s.index("HTML_PAGE")):]
css = "".join(re.findall(r"<style>(.*?)</style>", page, re.S))
js = "".join(re.findall(r"<script>(.*?)</script>", page, re.S))

FULL_OK = {"#splash", ".btov", ".page", ".mbg", "#notifPanel", "#npScrim", "#hbg"}   # #hbg (v3.36.37) = the moving background, behind everything — not a window
over = set()
for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
    b = body.replace(" ", "")
    if "position:fixed" in b and ("inset:0" in b or ("top:0" in b and "bottom:0" in b and ("left:0" in b or "right:0" in b))):
        over.add(re.sub(r"/\*.*?\*/", "", sel, flags=re.S).strip())
ok(f"① full-screen layers in the CSS = the known ones ({' · '.join(sorted(over))}) — a new window goes through showModal / showDialog",
   over <= FULL_OK, sorted(over - FULL_OK))

APPEND_OK = {"o": "btov", "a": "download", "c": "hwclone", "e": "stpop", "cv": "stick man"}
apps = [m.group(1) for m in re.finditer(r"document\.body\.appendChild\((\w+)\)", js)]
ok(f"② elements added straight onto the page = the known {len(APPEND_OK)} ({' · '.join(APPEND_OK.values())})",
   sorted(apps) == sorted(APPEND_OK), apps)

lit = re.findall(r"show(?:Modal|Dialog)\(\s*([`'\"])\s*(<?\w{0,3})", js)
bad = [x[1] for x in lit if not x[1].startswith("<h2")]
ok(f"③ every window written in place starts with its title (<h2…>): {len(lit)} of them", lit and not bad, bad)

frame = {
    "showModal puts ✕ and the body": re.search(r"function showModal\(html,o\)\{[\s\S]{0,600}?class=\"hwx\"[^\n]*class=\"hwb\"", js),
    "showDialog = the small size": "function showDialog(html){showModal(html,{small:true})}" in js,
    "hideModal plays the closing": re.search(r"function hideModal\(\)\{[^\n]*hwOut\(", js),
    "holyBack walks the stack": re.search(r"function holyBack\(\)\{[\s\S]{0,600}HW\.st\[HW\.st\.length-1\]", js),
    "the browser back is watched": "window.addEventListener('popstate'" in js,
    "⚙️ «حركة فتح النوافذ»": 'id="animRow"' in js and "حركة فتح النوافذ" in js,
    "Esc = back": "if(e.key==='Escape')holyBack()" in js,
    "askConfirm keeps the dialog size": re.search(r"function askConfirm\([^)]*\)\{showDialog\(", js),
    "every layer is watched (any code that opens it)": "HW.mo=new MutationObserver" in js,
}
ok("④ the frame is intact: " + " · ".join(frame), all(frame.values()), [k for k, v in frame.items() if not v])
print(f"{'✅' if all(res) else '❌'} t_windows: {sum(res)}/{len(res)}")
sys.exit(0 if res and all(res) else 1)
