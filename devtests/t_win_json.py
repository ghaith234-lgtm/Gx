# 💻 v3.36.55 — the Windows program's notification reader (windows/holy_win.c · js_ws · js_str · js_skip · feed_parse) on a reply that
#   arrives cut off. The same C code, taken from the file as it is, compiled here (gcc/clang + AddressSanitizer) and fed:
#   · real replies of /api/app/feed (Arabic as UTF-8 and as \\u escapes · emoji pairs · quotes · backslashes · 50 items)
#   · EVERY cut-off version of them (each length from 0 to the whole) · a few broken shapes
#   Before 2.0.1: a reply cut inside the item list ⇒ feed_parse loops for ever (the watcher thread spins, the notifications stop) ·
#   a reply cut right after a backslash ⇒ js_str reads past the end of the text (heap read overflow).
#   Now: every one returns within the time limit, no read outside the text, and a whole reply still reads the same.
#   python3 devtests/t_win_json.py [holy_win.c] [-q]
import json, os, shutil, subprocess, sys, tempfile

H = os.path.dirname(os.path.abspath(__file__))
Q = "-q" in sys.argv
SRC = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith("-")), os.path.join(H, "..", "windows", "holy_win.c")))
res = []


def ok(name, cond, det=""):
    res.append(bool(cond))
    if not Q or not cond:
        print(("✅ " if cond else "❌ ") + name + ("" if cond else f" — {str(det)[:1500]}"), flush=True)


cc = shutil.which("gcc") or shutil.which("clang")
if not cc:
    print("⏭️ t_win_json: no C compiler here (gcc/clang)"); sys.exit(0)
s = open(SRC, encoding="utf-8").read()
a = s.index("// ───────────────────────────── a small JSON reader")
b = s.index("// ───────────────────────────── notifications")
PART = s[a:b]
HARNESS = r'''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
''' + PART + r'''
static void tmo(int sig) { (void)sig; const char m[] = "HANG\n"; write(1, m, sizeof m - 1); _exit(3); }
int main(int argc, char **argv) {            // argv[1] = a file of replies: 4-byte length + bytes, one after another
    signal(SIGALRM, tmo);
    FILE *f = fopen(argv[1], "rb"); if (!f) return 2;
    unsigned char hd[4]; long i = 0;
    while (fread(hd, 1, 4, f) == 4) {
        size_t n = (size_t)hd[0] | (size_t)hd[1] << 8 | (size_t)hd[2] << 16 | (size_t)hd[3] << 24;
        char *b = (char *)malloc(n + 1); if (!b || fread(b, 1, n, f) != n) return 2; b[n] = 0;   // exactly like http_get: n bytes + 0
        Feed *fd = (Feed *)malloc(sizeof(Feed)); alarm(2);
        int r = feed_parse(b, fd); alarm(0);
        printf("%ld %d %ld %d", i, r, fd->last, fd->n);
        if (fd->n) printf(" %s|%s|%s|%s|%.4f", fd->it[0].k, fd->it[0].t, fd->it[0].b, fd->it[0].go, fd->it[0].usd);
        printf("\n"); fflush(stdout); free(fd); free(b); i++;
    }
    return 0;
}
'''
T = tempfile.mkdtemp(prefix="t_winjson_")
open(os.path.join(T, "h.c"), "w", encoding="utf-8").write(HARNESS)
exe = os.path.join(T, "h")
cp = subprocess.run([cc, "-std=c11", "-O1", "-g", "-fsanitize=address", "-fno-omit-frame-pointer", "-w", "-o", exe, os.path.join(T, "h.c")],
                    capture_output=True, text=True)
ok(f"the reader from {os.path.basename(SRC)} compiles here ({os.path.basename(cc)} + AddressSanitizer)", cp.returncode == 0, cp.stderr[-1500:])
if cp.returncode:
    sys.exit(1)

items = [{"k": "trade", "t": "💰 ربح صفقة SOL-USDT", "b": "ربح الصفقة: +0.0262 USDT · الإجمالي 12.5$", "usd": 0.0262, "go": "bot:bot_sol", "id": 7, "ts": 1763000000},
         {"k": "alert", "t": "🚨 فشل شراء \"BTC\" \\ مسار C:\\bots", "b": "سطر فيه \"اقتباس\" و\\ شرطة", "usd": None, "go": "sym:BTC-USDT", "id": 8, "ts": 1763000001},
         {"k": "info", "t": "📊 تقرير يومي 🧾", "b": "", "go": "reports", "id": 9, "ts": 1763000002}]
whole = [json.dumps({"ok": True, "last": 9, "items": items, "muted": False, "server": "3.36.55"}, ensure_ascii=ea).encode("utf-8") for ea in (False, True)]
many = json.dumps({"ok": True, "last": 120, "items": [dict(items[i % 3], id=i) for i in range(50)], "muted": True}, ensure_ascii=True).encode()
cases = []
for w in whole:
    cases += [w[:n] for n in range(len(w) + 1)]            # every cut-off version · and the whole reply last
cases += [many[:n] for n in range(0, len(many) + 1, 7)] + [many]
cases += [b'{"last":5,"items":[}', b'{"last":5,"items":[1,}', b'{"last":5,"items":[{"k":]}]}', b'{"last":5,"items":[{"t":"\\', b'{"last":5,"items":["\\',
          b'{"last":5,"items":[{"t":"\\u12', b'{"last":5,"items":[{"t":"\\ud83d\\u', b'{"last":', b'[]', b'', b'{"last":5,"items":[{"k":"trade"}]}']
blob = b"".join(len(c).to_bytes(4, "little") + c for c in cases)
open(os.path.join(T, "in.bin"), "wb").write(blob)
r = subprocess.run([exe, os.path.join(T, "in.bin")], capture_output=True, timeout=600,
                   env=dict(os.environ, ASAN_OPTIONS="detect_leaks=0:abort_on_error=0:halt_on_error=1"))
out = r.stdout.decode("utf-8", "replace").splitlines()
err = r.stderr.decode("utf-8", "replace")
done = len([x for x in out if x[:1].isdigit()])
hang = [i for i, x in enumerate(out) if x.startswith("HANG")]
ok(f"every one of the {len(cases)} replies returns within 2 s (no endless loop) — {done} read", not hang and done == len(cases),
   f"hang at reply #{done}: {cases[done][-60:]!r}" if done < len(cases) else hang)
ok("no read outside the text (AddressSanitizer: nothing)", "AddressSanitizer" not in err and r.returncode == 0,
   (err[:1200] + (f" · at reply #{done}: {cases[done][-60:]!r}" if done < len(cases) else "")))
if done == len(cases):
    rows = {int(x.split(" ")[0]): x for x in out}
    i_w0 = len(whole[0])                                    # the whole reply (UTF-8) = the last of its cut-offs
    i_w1 = i_w0 + 1 + len(whole[1])
    exp = "1 9 3 trade|💰 ربح صفقة SOL-USDT|ربح الصفقة: +0.0262 USDT · الإجمالي 12.5$|bot:bot_sol|0.0262"
    ok("a whole reply reads as before — UTF-8 and \\u escapes (Arabic · emoji pairs) give the same first notification",
       rows[i_w0].split(" ", 1)[1] == exp and rows[i_w1].split(" ", 1)[1] == exp, (rows[i_w0], rows[i_w1]))
    nm = len(whole[0]) + 1 + len(whole[1]) + 1 + len(range(0, len(many) + 1, 7))
    ok("50 notifications at once: all 50 read · «muted» read", rows[nm].split(" ")[1:4] == ["1", "120", "50"], rows[nm])
    cut = [rows[i] for i in range(i_w0)]
    ok("a cut-off reply is never taken (its «last» would skip the notifications not read yet) — it is asked again",
       all(x.split(" ")[1] == "0" for x in cut), [x for x in cut if x.split(" ")[1] != "0"][:5])
print(f"✅ t_win_json: {sum(res)}/{len(res)}" if all(res) else f"❌ t_win_json: {sum(res)}/{len(res)}")
shutil.rmtree(T, ignore_errors=True)
sys.exit(0 if all(res) else 1)
