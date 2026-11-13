// 💻 The Holy Dashboard — Windows program 2.0 (dashboard v3.36.40)
//   The owner (13-11, screenshot of the 1.2 window): «اريد تلغي الرموز الفوق … واتخليهم مع ايقونة الاشعارات · كيف احرك المربع كله اذا انزال
//   الشريط الفوق». 1.2 opened the dashboard in an Edge app window, and that title bar (— □ ✕) belongs to Edge. 2.0 shows the dashboard in its
//   own window through WebView2 (the engine inside Edge) with no title bar: the dashboard draws — □ ✕ beside 🔔 ⛶, its top bar moves the
//   window (CSS app-region: drag — Windows treats it as the title bar: drag · double-click = maximize · snap to the screen's edges · right
//   click = the window menu), the edges resize it.
//   Everything 1.2 did stays (its source was lost with the old machine — rebuilt here from its behaviour, ci/win_check.ps1):
//   the address + device key written into the download (HOLY-URL-SLOT) · %APPDATA%\HolyDashboard\holy.ini + holy.log (never the key) ·
//   Desktop + Start shortcuts · starts with Windows (--tray) · the notifications icon near the clock (the dashboard's feed, long poll) ·
//   one watcher (a second start hands over) · --setup / Shift = the address window (Arabic, right to left) · an address that doesn't answer
//   ⇒ ask · 401 ⇒ «this computer was unlinked». No WebView2 runtime (Windows 7/8) ⇒ the Edge/Chrome app window as in 1.2.
//   Built on GitHub's Windows machine (.github/workflows/holy-win-check.yml): MSVC x86 · /MT (no runtime DLL) · Microsoft's static
//   WebView2 loader (NuGet Microsoft.Web.WebView2).
#define WIN32_LEAN_AND_MEAN
#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#define COBJMACROS
#define CINTERFACE
#include <windows.h>
#include <windowsx.h>
#include <shellapi.h>
#include <shlobj.h>
#include <winhttp.h>
#include <commctrl.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include "WebView2.h"

#ifdef _MSC_VER
#pragma comment(lib, "kernel32.lib")
#pragma comment(lib, "user32.lib")
#pragma comment(lib, "gdi32.lib")
#pragma comment(lib, "shell32.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "oleaut32.lib")
#pragma comment(lib, "advapi32.lib")
#pragma comment(lib, "winhttp.lib")
#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "shlwapi.lib")
#pragma comment(lib, "version.lib")
#endif

#define APP_VER   L"2.0"
#define APP_BUILD 200                       // a watcher with a lower build steps aside for a newer copy
#define APP_TITLE L"The Holy Dashboard"
#define UA_STR    L"TheHolyDashboard/2.0"
#define WM_TRAY   (WM_APP + 1)
#define WM_FEED   (WM_APP + 2)
#define CMD_MAGIC 0x484F4C59                // 'HOLY' — WM_COPYDATA between two copies of the program
#define BG_RGB    RGB(7, 2, 16)
#define EDGE_RGB  RGB(52, 36, 98)

// the address + device key are written here when the dashboard serves the download (`address \0 key \0` · 560 bytes)
static volatile const char g_slot[14 + 560] = "HOLY-URL-SLOT:";

static WCHAR g_exe[MAX_PATH], g_dir[MAX_PATH], g_ini[MAX_PATH], g_log[MAX_PATH], g_udf[MAX_PATH], g_prof[MAX_PATH];
static WCHAR g_url[640];
static char g_tok[128];
static CRITICAL_SECTION g_cs;
static volatile LONG g_gen;
static HINSTANCE g_hi;
static HICON g_icon, g_iconSm;
static HWND g_tray, g_win;
static HANDLE g_mutex;
static UINT g_taskbarCreated;
static int g_noWv2 = -1;                    // -1 unknown · 0 WebView2 here · 1 not here (the Edge window instead)
static ICoreWebView2Environment *g_env;
static ICoreWebView2Controller *g_ctl;
static ICoreWebView2 *g_wv;
static BOOL g_ncr, g_fs, g_lastMax = -1;
static WINDOWPLACEMENT g_wpFs;
static LONG g_styleFs;
static WCHAR g_go[200];
static HBRUSH g_bgBrush;

// ───────────────────────────── small helpers
static void u8w(const char *s, WCHAR *out, int n) { if (!MultiByteToWideChar(CP_UTF8, 0, s, -1, out, n)) out[0] = 0; out[n - 1] = 0; }
static void w8(const WCHAR *s, char *out, int n) { if (!WideCharToMultiByte(CP_UTF8, 0, s, -1, out, n, NULL, NULL)) out[0] = 0; out[n - 1] = 0; }

static void hlog(const char *fmt, ...) {
    char msg[1400], line[1500]; va_list ap; SYSTEMTIME t;
    va_start(ap, fmt); _vsnprintf_s(msg, sizeof msg, _TRUNCATE, fmt, ap); va_end(ap);
    GetLocalTime(&t);
    int n = _snprintf_s(line, sizeof line, _TRUNCATE, "%04d-%02d-%02d %02d:%02d:%02d  %s\r\n", t.wYear, t.wMonth, t.wDay, t.wHour, t.wMinute, t.wSecond, msg);
    if (n < 0) n = (int)strlen(line);
    HANDLE f = CreateFileW(g_log, FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (f != INVALID_HANDLE_VALUE) {
        LARGE_INTEGER sz; if (GetFileSizeEx(f, &sz) && sz.QuadPart > 2 * 1024 * 1024) { CloseHandle(f); DeleteFileW(g_log);
            f = CreateFileW(g_log, FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL); }
        if (f != INVALID_HANDLE_VALUE) { DWORD w; WriteFile(f, line, (DWORD)n, &w, NULL); CloseHandle(f); }
    }
}

static int wstarts(const WCHAR *s, const WCHAR *p) { return _wcsnicmp(s, p, wcslen(p)) == 0; }
static int url_ok(const WCHAR *u) {
    if (!(wstarts(u, L"http://") || wstarts(u, L"https://")) || wcslen(u) < 10 || wcslen(u) > 540) return 0;
    for (const WCHAR *p = u; *p; p++) if (*p <= 32 || *p == L'"' || *p == L'\'' || *p == L'<' || *p == L'>' || *p == L'\\') return 0;
    return 1;
}
static void url_trim(WCHAR *u) { size_t n = wcslen(u); while (n && (u[n - 1] == L'/' || u[n - 1] == L' ')) u[--n] = 0; }

// ───────────────────────────── holy.ini (UTF-8 · key=value lines · the same file 1.2 wrote)
typedef struct { char k[16]; char v[700]; } KV;
static KV g_kv[16]; static int g_nkv;
static void ini_load(void) {
    g_nkv = 0; HANDLE f = CreateFileW(g_ini, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL); if (f == INVALID_HANDLE_VALUE) return;
    char buf[8192]; DWORD r = 0; ReadFile(f, buf, sizeof buf - 1, &r, NULL); CloseHandle(f); buf[r] = 0;
    char *p = buf; if ((unsigned char)p[0] == 0xEF && (unsigned char)p[1] == 0xBB && (unsigned char)p[2] == 0xBF) p += 3;
    while (*p && g_nkv < 16) {
        char *e = p; while (*e && *e != '\n' && *e != '\r') e++;
        char save = *e; *e = 0; char *eq = strchr(p, '=');
        if (eq && eq - p < 15) { memcpy(g_kv[g_nkv].k, p, eq - p); g_kv[g_nkv].k[eq - p] = 0; strncpy_s(g_kv[g_nkv].v, sizeof g_kv[0].v, eq + 1, _TRUNCATE); g_nkv++; }
        *e = save; p = e; while (*p == '\n' || *p == '\r') p++;
    }
}
static const char *ini_get(const char *k) { for (int i = 0; i < g_nkv; i++) if (!strcmp(g_kv[i].k, k)) return g_kv[i].v; return ""; }
static void ini_set(const char *k, const char *v) {
    for (int i = 0; i < g_nkv; i++) if (!strcmp(g_kv[i].k, k)) { strncpy_s(g_kv[i].v, sizeof g_kv[0].v, v, _TRUNCATE); return; }
    if (g_nkv < 16) { strncpy_s(g_kv[g_nkv].k, 16, k, _TRUNCATE); strncpy_s(g_kv[g_nkv].v, sizeof g_kv[0].v, v, _TRUNCATE); g_nkv++; }
}
static void ini_save(void) {
    char out[12000]; int n = 0;
    for (int i = 0; i < g_nkv; i++) if (g_kv[i].v[0]) n += _snprintf_s(out + n, sizeof out - n, _TRUNCATE, "%s=%s\r\n", g_kv[i].k, g_kv[i].v);
    WCHAR tmp[MAX_PATH]; _snwprintf_s(tmp, MAX_PATH, _TRUNCATE, L"%s.tmp", g_ini);
    HANDLE f = CreateFileW(tmp, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL); if (f == INVALID_HANDLE_VALUE) return;
    DWORD w; WriteFile(f, out, (DWORD)n, &w, NULL); CloseHandle(f); MoveFileExW(tmp, g_ini, MOVEFILE_REPLACE_EXISTING);
}

// the download's address + key · or what holy.ini holds (a new download wins · an address changed in the window stays)
static void config_load(void) {
    char su[600] = "", st[128] = ""; int i = 0;
    for (; i < 559 && g_slot[14 + i]; i++) su[i] = g_slot[14 + i]; su[i] = 0;
    if (su[0]) { int j = i + 1, k = 0; for (; j < 560 && g_slot[14 + j] && k < 120; j++) st[k++] = g_slot[14 + j]; st[k] = 0; }
    ini_load();
    char sig[40] = ""; unsigned h = 2166136261u; for (const char *p = su; *p; p++) h = (h ^ (unsigned char)*p) * 16777619u;
    for (const char *p = st; *p; p++) h = (h ^ (unsigned char)*p) * 16777619u; _snprintf_s(sig, sizeof sig, _TRUNCATE, "%08x", h);
    if (su[0] && strcmp(ini_get("slot"), sig)) {                     // a new download ⇒ its address and key
        ini_set("url", su); if (st[0]) ini_set("token", st); ini_set("slot", sig); ini_save();
    }
    WCHAR u[640]; u8w(ini_get("url"), u, 640); url_trim(u);
    EnterCriticalSection(&g_cs); wcscpy_s(g_url, 640, url_ok(u) ? u : L""); strncpy_s(g_tok, sizeof g_tok, ini_get("token"), _TRUNCATE); LeaveCriticalSection(&g_cs);
}

// ───────────────────────────── HTTP (WinHTTP · the system's own · https and proxies as Windows has them)
static int http_get(const WCHAR *url, const char *tok, DWORD timeout, char **body, DWORD *blen) {
    *body = NULL; *blen = 0; int status = -1;
    URL_COMPONENTS uc; memset(&uc, 0, sizeof uc); uc.dwStructSize = sizeof uc;
    WCHAR host[256], path[2048]; uc.lpszHostName = host; uc.dwHostNameLength = 256; uc.lpszUrlPath = path; uc.dwUrlPathLength = 2048;
    WCHAR extra[1024]; uc.lpszExtraInfo = extra; uc.dwExtraInfoLength = 1024;
    if (!WinHttpCrackUrl(url, 0, 0, &uc)) return -1;
    WCHAR full[3072]; _snwprintf_s(full, 3072, _TRUNCATE, L"%s%s", path[0] ? path : L"/", extra);
    HINTERNET s = WinHttpOpen(UA_STR, 4 /* WINHTTP_ACCESS_TYPE_AUTOMATIC_PROXY (8.1+) */, NULL, NULL, 0);
    if (!s) s = WinHttpOpen(UA_STR, WINHTTP_ACCESS_TYPE_DEFAULT_PROXY, NULL, NULL, 0);
    if (!s) return -1;
    WinHttpSetTimeouts(s, timeout, timeout, timeout, timeout);
    HINTERNET c = WinHttpConnect(s, host, uc.nPort, 0);
    HINTERNET r = c ? WinHttpOpenRequest(c, L"GET", full, NULL, NULL, NULL, uc.nScheme == INTERNET_SCHEME_HTTPS ? WINHTTP_FLAG_SECURE : 0) : NULL;
    if (r) {
        WCHAR hd[300] = L""; if (tok && tok[0]) { WCHAR wt[130]; u8w(tok, wt, 130); _snwprintf_s(hd, 300, _TRUNCATE, L"X-Holy-Device: %s\r\n", wt); }
        if (WinHttpSendRequest(r, hd[0] ? hd : WINHTTP_NO_ADDITIONAL_HEADERS, hd[0] ? (DWORD)-1 : 0, NULL, 0, 0, 0) && WinHttpReceiveResponse(r, NULL)) {
            DWORD sc = 0, l = sizeof sc; WinHttpQueryHeaders(r, WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER, NULL, &sc, &l, NULL); status = (int)sc;
            DWORD cap = 16384, n = 0; char *b = (char *)malloc(cap + 1);
            for (;;) { DWORD av = 0, rd = 0; if (!WinHttpQueryDataAvailable(r, &av) || !av) break;
                if (n + av > cap) { if (cap > 8 * 1024 * 1024) break; while (n + av > cap) cap *= 2; char *nb = (char *)realloc(b, cap + 1); if (!nb) break; b = nb; }
                if (!WinHttpReadData(r, b + n, av, &rd) || !rd) break; n += rd; }
            if (b) { b[n] = 0; *body = b; *blen = n; }
        }
    }
    if (r) WinHttpCloseHandle(r); if (c) WinHttpCloseHandle(c); WinHttpCloseHandle(s);
    return status;
}

// ───────────────────────────── a small JSON reader for the feed ({"last":N,"items":[{"k":…,"t":…,"b":…,"go":…},…],"muted":…})
static const char *js_ws(const char *p) { while (*p == ' ' || *p == '\n' || *p == '\r' || *p == '\t') p++; return p; }
static const char *js_str(const char *p, char *out, int n) {           // p at the opening quote ⇒ after the closing one
    int k = 0; p++;
    while (*p && *p != '"') {
        unsigned c = (unsigned char)*p++;
        if (c == '\\') { char e = *p++; if (!e) break;
            if (e == 'u') { unsigned v = 0; for (int i = 0; i < 4 && *p; i++, p++) v = v * 16 + (unsigned)((*p >= '0' && *p <= '9') ? *p - '0' : ((*p | 32) - 'a' + 10));
                if (v >= 0xD800 && v <= 0xDBFF && p[0] == '\\' && p[1] == 'u') { unsigned lo = 0; p += 2; for (int i = 0; i < 4 && *p; i++, p++) lo = lo * 16 + (unsigned)((*p >= '0' && *p <= '9') ? *p - '0' : ((*p | 32) - 'a' + 10));
                    v = 0x10000 + ((v - 0xD800) << 10) + (lo - 0xDC00); }
                char t[4]; int m = 0; if (v < 0x80) t[m++] = (char)v; else if (v < 0x800) { t[m++] = (char)(0xC0 | v >> 6); t[m++] = (char)(0x80 | (v & 63)); }
                else if (v < 0x10000) { t[m++] = (char)(0xE0 | v >> 12); t[m++] = (char)(0x80 | ((v >> 6) & 63)); t[m++] = (char)(0x80 | (v & 63)); }
                else { t[m++] = (char)(0xF0 | v >> 18); t[m++] = (char)(0x80 | ((v >> 12) & 63)); t[m++] = (char)(0x80 | ((v >> 6) & 63)); t[m++] = (char)(0x80 | (v & 63)); }
                for (int i = 0; i < m; i++) if (k < n - 1) out[k++] = t[i];
                continue; }
            c = (unsigned char)(e == 'n' ? ' ' : e == 't' ? ' ' : e == 'r' ? ' ' : e == 'b' || e == 'f' ? ' ' : e); }
        if (k < n - 1) out[k++] = (char)c;
    }
    out[k] = 0; return *p ? p + 1 : p;
}
static const char *js_skip(const char *p) {
    p = js_ws(p); if (*p == '"') { char t[2]; return js_str(p, t, 1); }
    if (*p == '{' || *p == '[') { int d = 0; while (*p) { if (*p == '"') { char t[2]; p = js_str(p, t, 1); continue; }
            if (*p == '{' || *p == '[') d++; else if (*p == '}' || *p == ']') { d--; if (!d) return p + 1; } p++; } return p; }
    while (*p && *p != ',' && *p != '}' && *p != ']') p++; return p;
}
typedef struct { char k[16], t[260], b[400], go[160]; double usd; } FeedItem;
typedef struct { long last; int muted, n; FeedItem it[50]; } Feed;
static int feed_parse(const char *s, Feed *f) {
    memset(f, 0, sizeof *f); f->last = -1; const char *p = js_ws(s); if (*p != '{') return 0; p++;
    while (*p) { p = js_ws(p); if (*p == '}') break; if (*p == ',') { p++; continue; } if (*p != '"') return 0;
        char key[32]; p = js_str(p, key, sizeof key); p = js_ws(p); if (*p != ':') return 0; p = js_ws(p + 1);
        if (!strcmp(key, "last")) f->last = strtol(p, NULL, 10);
        else if (!strcmp(key, "muted")) f->muted = !strncmp(p, "true", 4);
        if (!strcmp(key, "items") && *p == '[') { p++;
            for (;;) { p = js_ws(p); if (*p == ']') { p++; break; } if (*p == ',') { p++; continue; } if (*p != '{') { p = js_skip(p); continue; }
                FeedItem *it = f->n < 50 ? &f->it[f->n] : NULL; if (it) memset(it, 0, sizeof *it); p++;
                for (;;) { p = js_ws(p); if (*p == '}') { p++; break; } if (*p == ',') { p++; continue; } if (*p != '"') return 0;
                    char ik[16]; p = js_str(p, ik, sizeof ik); p = js_ws(p); if (*p != ':') return 0; p = js_ws(p + 1);
                    if (it && *p == '"' && !strcmp(ik, "k")) p = js_str(p, it->k, sizeof it->k);
                    else if (it && *p == '"' && !strcmp(ik, "t")) p = js_str(p, it->t, sizeof it->t);
                    else if (it && *p == '"' && !strcmp(ik, "b")) p = js_str(p, it->b, sizeof it->b);
                    else if (it && *p == '"' && !strcmp(ik, "go")) p = js_str(p, it->go, sizeof it->go);
                    else if (it && !strcmp(ik, "usd") && (*p == '-' || (*p >= '0' && *p <= '9'))) { it->usd = strtod(p, NULL); p = js_skip(p); }
                    else p = js_skip(p); }
                if (it) f->n++; }
        } else p = js_skip(p);
    }
    return f->last >= 0;
}

// ───────────────────────────── notifications (near the clock · Windows 10/11 turn them into its own notifications)
typedef struct { WCHAR title[64], text[256], go[160]; char kind[16]; } Note;
static Note g_q[24]; static int g_qn, g_showing; static WCHAR g_curGo[160];
static void tray_icon(DWORD op) {
    NOTIFYICONDATAW n; memset(&n, 0, sizeof n); n.cbSize = sizeof n; n.hWnd = g_tray; n.uID = 1;
    n.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP; n.uCallbackMessage = WM_TRAY; n.hIcon = g_iconSm;
    wcscpy_s(n.szTip, 128, L"The Holy Dashboard — الإشعارات"); Shell_NotifyIconW(op, &n);
    if (op == NIM_ADD) { n.uVersion = NOTIFYICON_VERSION_4; Shell_NotifyIconW(NIM_SETVERSION, &n); }
}
static void note_next(void) {
    if (g_showing || !g_qn) return;
    Note x = g_q[0]; memmove(g_q, g_q + 1, sizeof(Note) * (--g_qn));
    NOTIFYICONDATAW n; memset(&n, 0, sizeof n); n.cbSize = sizeof n; n.hWnd = g_tray; n.uID = 1; n.uFlags = NIF_INFO;
    wcscpy_s(n.szInfoTitle, 64, x.title); wcscpy_s(n.szInfo, 256, x.text[0] ? x.text : L" ");
    n.dwInfoFlags = NIIF_USER | NIIF_LARGE_ICON; n.hBalloonIcon = g_icon;
    if (Shell_NotifyIconW(NIM_MODIFY, &n)) { g_showing = 1; wcscpy_s(g_curGo, 160, x.go); hlog("shown 1 notification (%s)", x.kind[0] ? x.kind : "info"); SetTimer(g_tray, 2, 9000, NULL); }
    else hlog("notification refused by Windows");
}
static void note_push(const char *kind, const char *t, const char *b, const char *go) {
    if (g_qn >= 24) { memmove(g_q, g_q + 1, sizeof(Note) * 23); g_qn = 23; }
    Note *x = &g_q[g_qn++]; memset(x, 0, sizeof *x); strncpy_s(x->kind, 16, kind, _TRUNCATE);
    char tt[260]; strncpy_s(tt, sizeof tt, t, _TRUNCATE); u8w(tt, x->title, 64); u8w(b, x->text, 256); u8w(go, x->go, 160);
    note_next();
}

// ───────────────────────────── the feed watcher (long poll · never logs the key)
static DWORD WINAPI feed_thread(LPVOID unused) {
    (void)unused;
    for (;;) {
        LONG gen = g_gen; WCHAR base[640]; char tok[128];
        EnterCriticalSection(&g_cs); wcscpy_s(base, 640, g_url); strcpy_s(tok, sizeof tok, g_tok); LeaveCriticalSection(&g_cs);
        if (!base[0] || !tok[0]) {
            hlog(!base[0] ? "no address — notifications off" : "no device key in this download — notifications off (download it again from ⚙️ ⇐ 💻)");
            while (gen == g_gen) Sleep(1000); continue;
        }
        long since = -1; int okLog = 0, fails = 0, unlinked = 0;
        while (gen == g_gen) {
            WCHAR u[900]; _snwprintf_s(u, 900, _TRUNCATE, L"%s/api/app/feed?since=%ld&wait=%d", base, since < 0 ? 0 : since, since < 0 ? 0 : 50);
            char *body = NULL; DWORD bl = 0; int st = http_get(u, tok, since < 0 ? 15000 : 65000, &body, &bl);
            if (gen != g_gen) { free(body); break; }
            if (st == 200 && body) {
                Feed *f = (Feed *)malloc(sizeof(Feed));
                if (f && feed_parse(body, f)) {
                    fails = 0; unlinked = 0; if (!okLog) { hlog("feed ok (last %ld)", f->last); okLog = 1; }
                    if (since >= 0 && f->n) {
                        int tr = 0, al = 0, in = 0; for (int i = 0; i < f->n; i++) { if (!strcmp(f->it[i].k, "trade")) tr++; else if (!strcmp(f->it[i].k, "alert")) al++; else in++; }
                        hlog("feed: %d new (trades %d · alerts %d · info %d)%s", f->n, tr, al, in, f->muted ? " · muted" : " · queued");
                        if (!f->muted) { Feed *cp = (Feed *)malloc(sizeof(Feed)); if (cp) { *cp = *f; if (!PostMessageW(g_tray, WM_FEED, 0, (LPARAM)cp)) free(cp); } }
                    }
                    since = f->last;
                }
                free(f);
            } else if (st == 401) {
                if (!unlinked) { unlinked = 1; hlog("401 — this computer was unlinked (download the program again from ⚙️ ⇐ 💻 to link it)");
                    Feed *cp = (Feed *)calloc(1, sizeof(Feed)); if (cp) { cp->n = 1; strcpy_s(cp->it[0].k, 16, "alert");
                        strcpy_s(cp->it[0].t, 260, "🔗 انفصل هذا الحاسوب عن اللوحة"); strcpy_s(cp->it[0].b, 400, "الإشعارات متوقفة — نزّل البرنامج من جديد من ⚙️ ⇐ 💻 لتعود.");
                        if (!PostMessageW(g_tray, WM_FEED, 1, (LPARAM)cp)) free(cp); } }
                for (int i = 0; i < 120 && gen == g_gen; i++) Sleep(500);
            } else {
                if (fails++ % 10 == 0) hlog("can't reach the dashboard (status %d) — retrying", st);
                int w = fails < 6 ? 5 * fails : 30; for (int i = 0; i < w * 2 && gen == g_gen; i++) Sleep(500);
            }
            free(body);
        }
    }
    return 0;
}

// ───────────────────────────── the Edge/Chrome app window (no WebView2 runtime here · as in 1.2)
static int find_browser(WCHAR *out) {
    const WCHAR *envs[] = { L"ProgramFiles(x86)", L"ProgramW6432", L"ProgramFiles", L"LOCALAPPDATA" };
    const WCHAR *rel[] = { L"\\Microsoft\\Edge\\Application\\msedge.exe", L"\\Google\\Chrome\\Application\\chrome.exe", L"\\BraveSoftware\\Brave-Browser\\Application\\brave.exe" };
    for (int r = 0; r < 3; r++) for (int e = 0; e < 4; e++) { WCHAR b[MAX_PATH]; if (!GetEnvironmentVariableW(envs[e], b, MAX_PATH)) continue;
        _snwprintf_s(out, MAX_PATH, _TRUNCATE, L"%s%s", b, rel[r]); if (GetFileAttributesW(out) != INVALID_FILE_ATTRIBUTES) return 1; }
    const WCHAR *names[] = { L"msedge.exe", L"chrome.exe", L"brave.exe" };
    for (int i = 0; i < 3; i++) { WCHAR k[200]; _snwprintf_s(k, 200, _TRUNCATE, L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\%s", names[i]);
        DWORD sz = MAX_PATH * sizeof(WCHAR); if (RegGetValueW(HKEY_LOCAL_MACHINE, k, NULL, RRF_RT_REG_SZ, NULL, out, &sz) == ERROR_SUCCESS && GetFileAttributesW(out) != INVALID_FILE_ATTRIBUTES) return 1; }
    return 0;
}
static void open_url_of(const WCHAR *go, WCHAR *u, int n) {
    WCHAR base[640]; EnterCriticalSection(&g_cs); wcscpy_s(base, 640, g_url); LeaveCriticalSection(&g_cs);
    _snwprintf_s(u, n, _TRUNCATE, L"%s/?holyapp=win&hv=" APP_VER L"%s%s", base, go && go[0] ? L"&go=" : L"", go && go[0] ? go : L"");
}
static void open_edge(const WCHAR *go) {
    WCHAR u[1100], exe[MAX_PATH], cmd[2600]; open_url_of(go, u, 1100);
    if (find_browser(exe)) {
        _snwprintf_s(cmd, 2600, _TRUNCATE, L"\"%s\" --app=\"%s\" --start-maximized --user-data-dir=\"%s\" --no-first-run --no-default-browser-check --disable-features=Translate", exe, u, g_prof);
        STARTUPINFOW si; PROCESS_INFORMATION pi; memset(&si, 0, sizeof si); si.cb = sizeof si;
        if (CreateProcessW(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) { CloseHandle(pi.hThread); CloseHandle(pi.hProcess); hlog("opened the dashboard in the Edge/Chrome app window (no WebView2 here)"); return; }
        hlog("CreateProcess failed (%lu)", GetLastError());
    }
    ShellExecuteW(NULL, L"open", u, NULL, NULL, SW_SHOWNORMAL); hlog("no Edge/Chrome — opened the default browser");
}

// ───────────────────────────── the window: no title bar · the dashboard draws — □ ✕ and its top bar moves the window
static int dpi_of(HWND h) {
    typedef UINT (WINAPI *F)(HWND); static F f; static int tried; if (!tried) { tried = 1; f = (F)GetProcAddress(GetModuleHandleW(L"user32.dll"), "GetDpiForWindow"); }
    UINT d = f && h ? f(h) : 0; if (!d) { HDC dc = GetDC(NULL); d = (UINT)GetDeviceCaps(dc, LOGPIXELSX); ReleaseDC(NULL, dc); } return (int)d;
}
static int border_px(HWND h) { return g_fs || IsZoomed(h) ? 0 : MulDiv(5, dpi_of(h), 96); }
static void post_state(void) {
    if (!g_wv || !g_win) return; BOOL mx = IsZoomed(g_win);
    WCHAR j[120]; _snwprintf_s(j, 120, _TRUNCATE, L"{\"t\":\"win\",\"max\":%s,\"fs\":%s,\"ncr\":%s}", mx ? L"true" : L"false", g_fs ? L"true" : L"false", g_ncr ? L"true" : L"false");
    ICoreWebView2_PostWebMessageAsJson(g_wv, j); g_lastMax = mx;
}
static void fit_view(void) {
    if (!g_ctl || !g_win) return; RECT r; GetClientRect(g_win, &r); int b = border_px(g_win);
    r.left += b; r.top += b; r.right -= b; r.bottom -= b; ICoreWebView2Controller_put_Bounds(g_ctl, r);
}
static void set_fs(BOOL on) {
    if (!g_win || on == g_fs) return;
    if (on) { g_wpFs.length = sizeof g_wpFs; GetWindowPlacement(g_win, &g_wpFs); g_styleFs = GetWindowLongW(g_win, GWL_STYLE);
        MONITORINFO mi; mi.cbSize = sizeof mi; GetMonitorInfoW(MonitorFromWindow(g_win, MONITOR_DEFAULTTONEAREST), &mi); g_fs = TRUE;
        SetWindowLongW(g_win, GWL_STYLE, (g_styleFs & ~(WS_CAPTION | WS_THICKFRAME | WS_MAXIMIZE)) | WS_POPUP);
        SetWindowPos(g_win, HWND_TOP, mi.rcMonitor.left, mi.rcMonitor.top, mi.rcMonitor.right - mi.rcMonitor.left, mi.rcMonitor.bottom - mi.rcMonitor.top, SWP_FRAMECHANGED | SWP_SHOWWINDOW); }
    else { g_fs = FALSE; SetWindowLongW(g_win, GWL_STYLE, g_styleFs); SetWindowPlacement(g_win, &g_wpFs);
        SetWindowPos(g_win, NULL, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED); }
    fit_view(); post_state(); hlog(on ? "full screen" : "back to the window");
}
static void win_place_save(void) {
    if (!g_win || g_fs) return; WINDOWPLACEMENT wp; wp.length = sizeof wp; if (!GetWindowPlacement(g_win, &wp)) return;
    char v[80]; RECT r = wp.rcNormalPosition; _snprintf_s(v, sizeof v, _TRUNCATE, "%ld,%ld,%ld,%ld,%d", r.left, r.top, r.right, r.bottom, wp.showCmd == SW_SHOWMAXIMIZED || IsZoomed(g_win) ? 1 : 0);
    ini_load(); ini_set("win", v); ini_save();
}
static void open_external(const WCHAR *u) { if (u && (wstarts(u, L"http://") || wstarts(u, L"https://") || wstarts(u, L"mailto:"))) ShellExecuteW(NULL, L"open", u, NULL, NULL, SW_SHOWNORMAL); }
static int same_origin(const WCHAR *u) { WCHAR base[640]; EnterCriticalSection(&g_cs); wcscpy_s(base, 640, g_url); LeaveCriticalSection(&g_cs);
    size_t n = wcslen(base); return n && !_wcsnicmp(u, base, n) && (u[n] == 0 || u[n] == L'/' || u[n] == L'?' || u[n] == L'#'); }

// COM handlers (C: a vtable each · one static object each — they live as long as the program)
#define QI_BODY(IID_X) if (IsEqualIID(riid, &IID_IUnknown) || IsEqualIID(riid, &IID_X)) { *ppv = This; return S_OK; } *ppv = NULL; return E_NOINTERFACE;
#define REF_FNS(T) static ULONG STDMETHODCALLTYPE T##_AddRef(T *This) { (void)This; return 2; } static ULONG STDMETHODCALLTYPE T##_Release(T *This) { (void)This; return 1; }

typedef ICoreWebView2CreateCoreWebView2ControllerCompletedHandler CtlH;
typedef ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler EnvH;
typedef ICoreWebView2WebMessageReceivedEventHandler MsgH;
typedef ICoreWebView2NewWindowRequestedEventHandler NewH;
typedef ICoreWebView2NavigationStartingEventHandler NavH;
typedef ICoreWebView2ContainsFullScreenElementChangedEventHandler FsH;
typedef ICoreWebView2AcceleratorKeyPressedEventHandler KeyH;
typedef ICoreWebView2ProcessFailedEventHandler FailH;

static HRESULT STDMETHODCALLTYPE EnvH_QI(EnvH *This, REFIID riid, void **ppv) { QI_BODY(IID_ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler) }
static HRESULT STDMETHODCALLTYPE CtlH_QI(CtlH *This, REFIID riid, void **ppv) { QI_BODY(IID_ICoreWebView2CreateCoreWebView2ControllerCompletedHandler) }
static HRESULT STDMETHODCALLTYPE MsgH_QI(MsgH *This, REFIID riid, void **ppv) { QI_BODY(IID_ICoreWebView2WebMessageReceivedEventHandler) }
static HRESULT STDMETHODCALLTYPE NewH_QI(NewH *This, REFIID riid, void **ppv) { QI_BODY(IID_ICoreWebView2NewWindowRequestedEventHandler) }
static HRESULT STDMETHODCALLTYPE NavH_QI(NavH *This, REFIID riid, void **ppv) { QI_BODY(IID_ICoreWebView2NavigationStartingEventHandler) }
static HRESULT STDMETHODCALLTYPE FsH_QI(FsH *This, REFIID riid, void **ppv) { QI_BODY(IID_ICoreWebView2ContainsFullScreenElementChangedEventHandler) }
static HRESULT STDMETHODCALLTYPE KeyH_QI(KeyH *This, REFIID riid, void **ppv) { QI_BODY(IID_ICoreWebView2AcceleratorKeyPressedEventHandler) }
static HRESULT STDMETHODCALLTYPE FailH_QI(FailH *This, REFIID riid, void **ppv) { QI_BODY(IID_ICoreWebView2ProcessFailedEventHandler) }
REF_FNS(EnvH) REF_FNS(CtlH) REF_FNS(MsgH) REF_FNS(NewH) REF_FNS(NavH) REF_FNS(FsH) REF_FNS(KeyH) REF_FNS(FailH)

static void wv_fallback(const char *why, HRESULT hr) {
    hlog("WebView2 unavailable (%s 0x%08lx) — the Edge/Chrome window instead", why, (unsigned long)hr); g_noWv2 = 1;
    WCHAR go[200]; wcscpy_s(go, 200, g_go); if (g_win) { HWND w = g_win; g_win = NULL; DestroyWindow(w); } open_edge(go);
}

static HRESULT STDMETHODCALLTYPE MsgH_Invoke(MsgH *This, ICoreWebView2 *sender, ICoreWebView2WebMessageReceivedEventArgs *args) {
    (void)This; (void)sender; LPWSTR s = NULL;
    if (FAILED(ICoreWebView2WebMessageReceivedEventArgs_TryGetWebMessageAsString(args, &s)) || !s) return S_OK;
    if (!wcscmp(s, L"win:min")) ShowWindow(g_win, SW_MINIMIZE);
    else if (!wcscmp(s, L"win:max")) { if (g_fs) set_fs(FALSE); else ShowWindow(g_win, IsZoomed(g_win) ? SW_RESTORE : SW_MAXIMIZE); }
    else if (!wcscmp(s, L"win:close")) PostMessageW(g_win, WM_CLOSE, 0, 0);
    else if (!wcscmp(s, L"win:fs")) set_fs(!g_fs);
    else if (!wcscmp(s, L"win:drag")) { if (!g_fs) { POINT pt; GetCursorPos(&pt); ReleaseCapture();     // Windows moves it (snaps to the edges · a maximized one comes down) —
            PostMessageW(g_win, WM_NCLBUTTONDOWN, HTCAPTION, MAKELPARAM(pt.x, pt.y)); } }                     // posted: its move loop must not run inside WebView2's handler
    else if (!wcscmp(s, L"win:state")) post_state();
    else if (wstarts(s, L"hello ")) {            // the dashboard says it drew the buttons (where they are · for the Windows check)
        double v[8] = {0}; char a[400]; w8(s + 6, a, sizeof a);
        if (sscanf_s(a, "%lf,%lf,%lf,%lf,%lf,%lf,%lf,%lf", &v[0], &v[1], &v[2], &v[3], &v[4], &v[5], &v[6], &v[7]) == 8) {
            RECT r; GetWindowRect(g_win, &r); int b = border_px(g_win); double z = dpi_of(g_win) / 96.0; long P[8];
            double zoom = 1.0; if (g_ctl) ICoreWebView2Controller_get_ZoomFactor(g_ctl, &zoom); z *= zoom;
            for (int i = 0; i < 8; i += 2) { P[i] = r.left + b + (long)(v[i] * z); P[i + 1] = r.top + b + (long)(v[i + 1] * z); }
            hlog("page: buttons drawn · min=%ld,%ld max=%ld,%ld close=%ld,%ld drag=%ld,%ld · title-bar drag %s", P[0], P[1], P[2], P[3], P[4], P[5], P[6], P[7], g_ncr ? "native" : "by message");
        } else hlog("page: hello");
    }
    CoTaskMemFree(s); return S_OK;
}
static HRESULT STDMETHODCALLTYPE NewH_Invoke(NewH *This, ICoreWebView2 *sender, ICoreWebView2NewWindowRequestedEventArgs *args) {
    (void)This; (void)sender; LPWSTR u = NULL;
    if (SUCCEEDED(ICoreWebView2NewWindowRequestedEventArgs_get_Uri(args, &u)) && u) {
        if (same_origin(u) && g_wv) ICoreWebView2_Navigate(g_wv, u); else open_external(u); CoTaskMemFree(u); }
    ICoreWebView2NewWindowRequestedEventArgs_put_Handled(args, TRUE); return S_OK;
}
static HRESULT STDMETHODCALLTYPE NavH_Invoke(NavH *This, ICoreWebView2 *sender, ICoreWebView2NavigationStartingEventArgs *args) {
    (void)This; (void)sender; LPWSTR u = NULL;
    if (SUCCEEDED(ICoreWebView2NavigationStartingEventArgs_get_Uri(args, &u)) && u) {
        if (!same_origin(u) && !wstarts(u, L"about:") && !wstarts(u, L"data:")) { ICoreWebView2NavigationStartingEventArgs_put_Cancel(args, TRUE); open_external(u); }
        CoTaskMemFree(u); }
    return S_OK;
}
static HRESULT STDMETHODCALLTYPE FsH_Invoke(FsH *This, ICoreWebView2 *sender, IUnknown *args) {
    (void)This; (void)args; BOOL b = FALSE; ICoreWebView2_get_ContainsFullScreenElement(sender, &b); set_fs(b); return S_OK;
}
static HRESULT STDMETHODCALLTYPE KeyH_Invoke(KeyH *This, ICoreWebView2Controller *sender, ICoreWebView2AcceleratorKeyPressedEventArgs *args) {
    (void)This; (void)sender; COREWEBVIEW2_KEY_EVENT_KIND k; UINT key = 0;
    ICoreWebView2AcceleratorKeyPressedEventArgs_get_KeyEventKind(args, &k); ICoreWebView2AcceleratorKeyPressedEventArgs_get_VirtualKey(args, &key);
    if (k == COREWEBVIEW2_KEY_EVENT_KIND_KEY_DOWN && key == VK_F11) { set_fs(!g_fs); ICoreWebView2AcceleratorKeyPressedEventArgs_put_Handled(args, TRUE); }
    return S_OK;
}
static HRESULT STDMETHODCALLTYPE FailH_Invoke(FailH *This, ICoreWebView2 *sender, ICoreWebView2ProcessFailedEventArgs *args) {
    (void)This; COREWEBVIEW2_PROCESS_FAILED_KIND k; ICoreWebView2ProcessFailedEventArgs_get_ProcessFailedKind(args, &k);
    hlog("WebView2 process failed (%d) — reloading", (int)k); if (k != COREWEBVIEW2_PROCESS_FAILED_KIND_BROWSER_PROCESS_EXITED) ICoreWebView2_Reload(sender);
    else if (g_win) PostMessageW(g_win, WM_CLOSE, 0, 0);
    return S_OK;
}
static MsgH  g_msgH;  static ICoreWebView2WebMessageReceivedEventHandlerVtbl g_msgV = { MsgH_QI, MsgH_AddRef, MsgH_Release, MsgH_Invoke };
static NewH  g_newH;  static ICoreWebView2NewWindowRequestedEventHandlerVtbl g_newV = { NewH_QI, NewH_AddRef, NewH_Release, NewH_Invoke };
static NavH  g_navH;  static ICoreWebView2NavigationStartingEventHandlerVtbl g_navV = { NavH_QI, NavH_AddRef, NavH_Release, NavH_Invoke };
static FsH   g_fsH;   static ICoreWebView2ContainsFullScreenElementChangedEventHandlerVtbl g_fsV = { FsH_QI, FsH_AddRef, FsH_Release, FsH_Invoke };
static KeyH  g_keyH;  static ICoreWebView2AcceleratorKeyPressedEventHandlerVtbl g_keyV = { KeyH_QI, KeyH_AddRef, KeyH_Release, KeyH_Invoke };
static FailH g_failH; static ICoreWebView2ProcessFailedEventHandlerVtbl g_failV = { FailH_QI, FailH_AddRef, FailH_Release, FailH_Invoke };

static HRESULT STDMETHODCALLTYPE CtlH_Invoke(CtlH *This, HRESULT hr, ICoreWebView2Controller *ctl) {
    (void)This;
    if (FAILED(hr) || !ctl) { wv_fallback("controller", hr); return S_OK; }
    if (!g_win) { ICoreWebView2Controller_Close(ctl); return S_OK; }                  // the window closed while it was starting
    g_ctl = ctl; ICoreWebView2Controller_AddRef(ctl); ICoreWebView2Controller_get_CoreWebView2(ctl, &g_wv);
    ICoreWebView2Controller2 *c2 = NULL;
    if (SUCCEEDED(ICoreWebView2Controller_QueryInterface(ctl, &IID_ICoreWebView2Controller2, (void **)&c2)) && c2) {
        COREWEBVIEW2_COLOR bg = { 255, 7, 2, 16 }; ICoreWebView2Controller2_put_DefaultBackgroundColor(c2, bg); ICoreWebView2Controller2_Release(c2); }
    ICoreWebView2Settings *st = NULL;
    if (SUCCEEDED(ICoreWebView2_get_Settings(g_wv, &st)) && st) {
        ICoreWebView2Settings_put_AreDevToolsEnabled(st, FALSE); ICoreWebView2Settings_put_IsStatusBarEnabled(st, FALSE);
        ICoreWebView2Settings_put_IsZoomControlEnabled(st, TRUE); ICoreWebView2Settings_put_AreDefaultContextMenusEnabled(st, TRUE);
        // the dashboard's top bar moves the window by a message («win:drag» on a press ⇒ Windows' own move · snap · drag down from maximized) —
        // WebView2's app-region support is left off: in a window like this one it isn't certain, and it would swallow the page's own clicks there
        ICoreWebView2Settings_Release(st);
    }
    EventRegistrationToken t;
    g_msgH.lpVtbl = &g_msgV; ICoreWebView2_add_WebMessageReceived(g_wv, &g_msgH, &t);
    g_newH.lpVtbl = &g_newV; ICoreWebView2_add_NewWindowRequested(g_wv, &g_newH, &t);
    g_navH.lpVtbl = &g_navV; ICoreWebView2_add_NavigationStarting(g_wv, &g_navH, &t);
    g_fsH.lpVtbl = &g_fsV;   ICoreWebView2_add_ContainsFullScreenElementChanged(g_wv, &g_fsH, &t);
    g_failH.lpVtbl = &g_failV; ICoreWebView2_add_ProcessFailed(g_wv, &g_failH, &t);
    g_keyH.lpVtbl = &g_keyV; ICoreWebView2Controller_add_AcceleratorKeyPressed(ctl, &g_keyH, &t);
    WCHAR js[200]; _snwprintf_s(js, 200, _TRUNCATE, L"window.HOLYWIN={v:'" APP_VER L"',ncr:%s};", g_ncr ? L"true" : L"false");
    ICoreWebView2_AddScriptToExecuteOnDocumentCreated(g_wv, js, NULL);
    fit_view(); ICoreWebView2Controller_put_IsVisible(ctl, TRUE);
    WCHAR u[1100]; open_url_of(g_go, u, 1100); ICoreWebView2_Navigate(g_wv, u);
    hlog("opened the dashboard window%s · title bar from the dashboard (%s)", g_go[0] ? " (from a notification)" : "", g_ncr ? "native drag" : "drag by message");
    return S_OK;
}
static CtlH g_ctlH; static ICoreWebView2CreateCoreWebView2ControllerCompletedHandlerVtbl g_ctlV = { CtlH_QI, CtlH_AddRef, CtlH_Release, CtlH_Invoke };
static HRESULT STDMETHODCALLTYPE EnvH_Invoke(EnvH *This, HRESULT hr, ICoreWebView2Environment *env) {
    (void)This;
    if (FAILED(hr) || !env) { wv_fallback("environment", hr); return S_OK; }
    if (!g_env) { g_env = env; ICoreWebView2Environment_AddRef(env); }
    if (!g_win) return S_OK;
    g_ctlH.lpVtbl = &g_ctlV; hr = ICoreWebView2Environment_CreateCoreWebView2Controller(g_env, g_win, &g_ctlH);
    if (FAILED(hr)) wv_fallback("create", hr);
    return S_OK;
}
static EnvH g_envH; static ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandlerVtbl g_envV = { EnvH_QI, EnvH_AddRef, EnvH_Release, EnvH_Invoke };

static LRESULT CALLBACK WinProc(HWND h, UINT m, WPARAM wp, LPARAM lp) {
    switch (m) {
    case WM_NCCALCSIZE:                                       // the whole window is the page (no title bar · no visible frame)
        if (wp && !g_fs && IsZoomed(h)) {                     // maximized: Windows pushes the frame off screen ⇒ keep the page inside the screen
            NCCALCSIZE_PARAMS *p = (NCCALCSIZE_PARAMS *)lp; MONITORINFO mi; mi.cbSize = sizeof mi;
            if (GetMonitorInfoW(MonitorFromWindow(h, MONITOR_DEFAULTTONEAREST), &mi)) { p->rgrc[0] = mi.rcWork;
                if (EqualRect(&mi.rcWork, &mi.rcMonitor)) p->rgrc[0].bottom -= 1; } }   // a taskbar that hides itself can still come up
        if (wp) return 0; break;
    case WM_NCHITTEST: {                                      // the edges (5 px) resize · the dashboard's top bar moves (WebView2 · app-region)
        if (g_fs || IsZoomed(h)) return HTCLIENT;
        POINT pt = { GET_X_LPARAM(lp), GET_Y_LPARAM(lp) }; RECT r; GetWindowRect(h, &r); int b = MulDiv(6, dpi_of(h), 96);
        int L = pt.x < r.left + b, R = pt.x >= r.right - b, T = pt.y < r.top + b, B = pt.y >= r.bottom - b;
        if (T && L) return HTTOPLEFT; if (T && R) return HTTOPRIGHT; if (B && L) return HTBOTTOMLEFT; if (B && R) return HTBOTTOMRIGHT;
        if (L) return HTLEFT; if (R) return HTRIGHT; if (T) return HTTOP; if (B) return HTBOTTOM; return HTCLIENT; }
    case WM_NCACTIVATE: return DefWindowProcW(h, m, wp, -1);  // no frame repainted over the page when focus moves
    case WM_ERASEBKGND: return 1;
    case WM_PAINT: { PAINTSTRUCT ps; HDC dc = BeginPaint(h, &ps); RECT r; GetClientRect(h, &r); FillRect(dc, &r, g_bgBrush);
        if (!g_fs && !IsZoomed(h)) { HBRUSH e = CreateSolidBrush(EDGE_RGB); FrameRect(dc, &r, e); DeleteObject(e); } EndPaint(h, &ps); return 0; }
    case WM_SIZE:
        if (g_ctl) { ICoreWebView2Controller_put_IsVisible(g_ctl, wp != SIZE_MINIMIZED); fit_view(); }
        if (wp != SIZE_MINIMIZED && g_lastMax != IsZoomed(h)) post_state();
        InvalidateRect(h, NULL, FALSE); return 0;
    case WM_MOVE: case WM_MOVING: if (g_ctl) ICoreWebView2Controller_NotifyParentWindowPositionChanged(g_ctl); break;
    case WM_GETMINMAXINFO: { MINMAXINFO *mm = (MINMAXINFO *)lp; int d = dpi_of(h); mm->ptMinTrackSize.x = MulDiv(420, d, 96); mm->ptMinTrackSize.y = MulDiv(360, d, 96); return 0; }
    case WM_DPICHANGED: { RECT *r = (RECT *)lp; SetWindowPos(h, NULL, r->left, r->top, r->right - r->left, r->bottom - r->top, SWP_NOZORDER | SWP_NOACTIVATE); fit_view(); return 0; }
    case WM_SETFOCUS: if (g_ctl) ICoreWebView2Controller_MoveFocus(g_ctl, COREWEBVIEW2_MOVE_FOCUS_REASON_PROGRAMMATIC); return 0;
    case WM_CLOSE: win_place_save(); DestroyWindow(h); return 0;
    case WM_DESTROY:
        if (g_ctl) { ICoreWebView2Controller_Close(g_ctl); ICoreWebView2Controller_Release(g_ctl); g_ctl = NULL; }
        if (g_wv) { ICoreWebView2_Release(g_wv); g_wv = NULL; }
        if (g_win == h) g_win = NULL; g_fs = FALSE; g_lastMax = -1; hlog("window closed (the notifications icon stays)"); return 0;
    }
    return DefWindowProcW(h, m, wp, lp);
}

static void open_window(const WCHAR *go) {
    wcscpy_s(g_go, 200, go ? go : L"");
    if (g_noWv2 < 0) { LPWSTR v = NULL; HRESULT hr = GetAvailableCoreWebView2BrowserVersionString(NULL, &v);
        g_noWv2 = FAILED(hr) || !v; if (v) { char a[64]; w8(v, a, 64); hlog("WebView2 %s", a); CoTaskMemFree(v); } }
    if (g_noWv2 == 1) { open_edge(go); return; }
    if (g_win) {                                              // already open ⇒ to the front (and to the notification's place)
        if (IsIconic(g_win)) ShowWindow(g_win, SW_RESTORE); SetForegroundWindow(g_win);
        if (go && go[0] && g_wv) { WCHAR u[1100]; open_url_of(go, u, 1100); ICoreWebView2_Navigate(g_wv, u); }
        return; }
    ini_load(); long x = CW_USEDEFAULT, y = CW_USEDEFAULT, w = CW_USEDEFAULT, hh = CW_USEDEFAULT; int mx = 1; long a, b, c, d; int e;
    if (sscanf_s(ini_get("win"), "%ld,%ld,%ld,%ld,%d", &a, &b, &c, &d, &e) == 5 && c - a > 300 && d - b > 250) {
        RECT rr = { a, b, c, d }; if (MonitorFromRect(&rr, MONITOR_DEFAULTTONULL)) { x = a; y = b; w = c - a; hh = d - b; mx = e; } }
    g_win = CreateWindowExW(0, L"HolyDash", APP_TITLE, WS_OVERLAPPEDWINDOW | WS_CLIPCHILDREN, x, y, w, hh, NULL, NULL, g_hi, NULL);
    if (!g_win) { hlog("CreateWindow failed (%lu)", GetLastError()); open_edge(go); return; }
    typedef HRESULT (WINAPI *DwmSet)(HWND, DWORD, LPCVOID, DWORD); HMODULE dw = LoadLibraryW(L"dwmapi.dll");
    if (dw) { DwmSet f = (DwmSet)GetProcAddress(dw, "DwmSetWindowAttribute"); if (f) { int dark = 1, round = 2; f(g_win, 20, &dark, sizeof dark); f(g_win, 33, &round, sizeof round); } }
    SetWindowPos(g_win, NULL, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED);
    ShowWindow(g_win, mx ? SW_SHOWMAXIMIZED : SW_SHOWNORMAL); UpdateWindow(g_win); SetForegroundWindow(g_win);
    if (g_env) { EnvH_Invoke(&g_envH, S_OK, g_env); return; }
    g_envH.lpVtbl = &g_envV;
    HRESULT hr = CreateCoreWebView2EnvironmentWithOptions(NULL, g_udf, NULL, &g_envH);
    if (FAILED(hr)) wv_fallback("start", hr);
}

// ───────────────────────────── the watcher (near the clock) · one per user · a second start hands over
static void tray_menu(void) {
    HMENU m = CreatePopupMenu();
    AppendMenuW(m, MF_STRING, 1, L"🖥️ افتح اللوحة"); AppendMenuW(m, MF_STRING, 2, L"🔗 عنوان اللوحة…"); AppendMenuW(m, MF_SEPARATOR, 0, NULL);
    AppendMenuW(m, MF_STRING, 3, L"✕ إغلاق البرنامج (تتوقف الإشعارات)");
    POINT p; GetCursorPos(&p); SetForegroundWindow(g_tray);
    int c = TrackPopupMenu(m, TPM_RETURNCMD | TPM_RIGHTBUTTON | TPM_LAYOUTRTL, p.x, p.y, 0, g_tray, NULL); DestroyMenu(m);
    if (c == 1) open_window(NULL);
    else if (c == 2) { WCHAR cmd[MAX_PATH + 20]; _snwprintf_s(cmd, MAX_PATH + 20, _TRUNCATE, L"\"%s\" --setup", g_exe); STARTUPINFOW si; PROCESS_INFORMATION pi;
        memset(&si, 0, sizeof si); si.cb = sizeof si; if (CreateProcessW(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) { CloseHandle(pi.hThread); CloseHandle(pi.hProcess); } }
    else if (c == 3) { if (g_win) SendMessageW(g_win, WM_CLOSE, 0, 0); DestroyWindow(g_tray); }
}
static LRESULT CALLBACK TrayProc(HWND h, UINT m, WPARAM wp, LPARAM lp) {
    if (m == g_taskbarCreated && m) { tray_icon(NIM_ADD); return 0; }
    switch (m) {
    case WM_TRAY:
        switch (LOWORD(lp)) {
        case NIN_SELECT: case NIN_KEYSELECT: case WM_LBUTTONUP: open_window(NULL); break;
        case WM_CONTEXTMENU: case WM_RBUTTONUP: tray_menu(); break;
        case NIN_BALLOONUSERCLICK: g_showing = 0; KillTimer(h, 2); open_window(g_curGo); note_next(); break;
        case NIN_BALLOONTIMEOUT: case NIN_BALLOONHIDE: g_showing = 0; KillTimer(h, 2); note_next(); break;
        }
        return 0;
    case WM_TIMER: if (wp == 2) { KillTimer(h, 2); g_showing = 0; note_next(); } return 0;
    case WM_FEED: {
        Feed *f = (Feed *)lp;
        if (f->n > 4) {                                       // many at once ⇒ one notification that adds them up
            double usd = 0; int tr = 0; for (int i = 0; i < f->n; i++) if (!strcmp(f->it[i].k, "trade")) { tr++; usd += f->it[i].usd; }
            char t[120], b[200]; _snprintf_s(t, sizeof t, _TRUNCATE, "🔔 %d إشعارات جديدة", f->n);
            if (tr) _snprintf_s(b, sizeof b, _TRUNCATE, "💰 %d صفقة · %s%.2f$ — افتح اللوحة للتفاصيل", tr, usd >= 0 ? "+" : "", usd);
            else _snprintf_s(b, sizeof b, _TRUNCATE, "افتح اللوحة للتفاصيل");
            note_push(tr ? "trade" : "info", t, b, "");
        } else for (int i = 0; i < f->n; i++) note_push(f->it[i].k[0] ? f->it[i].k : "info", f->it[i].t, f->it[i].b, f->it[i].go);
        free(f); return 0; }
    case WM_COPYDATA: {
        COPYDATASTRUCT *cd = (COPYDATASTRUCT *)lp; if (cd->dwData != CMD_MAGIC || !cd->lpData) return 0;
        WCHAR c[300]; size_t n = cd->cbData / sizeof(WCHAR); if (n > 299) n = 299; memcpy(c, cd->lpData, n * sizeof(WCHAR)); c[n] = 0;
        if (!wcscmp(c, L"ver")) return APP_BUILD;
        if (!wcscmp(c, L"quit")) { hlog("a newer copy takes over"); if (g_win) SendMessageW(g_win, WM_CLOSE, 0, 0); DestroyWindow(h); return 1; }
        if (!wcscmp(c, L"cfg")) { config_load(); InterlockedIncrement(&g_gen); hlog("address changed — restarting the notifications"); return 1; }
        if (wstarts(c, L"open")) { open_window(c[4] == L'\t' ? c + 5 : NULL); return 1; }
        return 0; }
    case WM_DESTROY: { NOTIFYICONDATAW n; memset(&n, 0, sizeof n); n.cbSize = sizeof n; n.hWnd = h; n.uID = 1; Shell_NotifyIconW(NIM_DELETE, &n); PostQuitMessage(0); return 0; }
    }
    return DefWindowProcW(h, m, wp, lp);
}
static LRESULT send_cmd(HWND to, const WCHAR *cmd) {
    COPYDATASTRUCT cd; cd.dwData = CMD_MAGIC; cd.cbData = (DWORD)(wcslen(cmd) * sizeof(WCHAR)); cd.lpData = (PVOID)cmd; DWORD_PTR r = 0;
    if (!SendMessageTimeoutW(to, WM_COPYDATA, 0, (LPARAM)&cd, SMTO_ABORTIFHUNG, 8000, &r)) return 0; return (LRESULT)r;
}
static void retire_old(void) {                               // 1.2 (or older 1.x) still running ⇒ it would open the old Edge window — stop it
    HWND o = FindWindowW(L"HolyTray", NULL); if (!o) return;
    DWORD pid = 0; GetWindowThreadProcessId(o, &pid); HANDLE p = pid ? OpenProcess(PROCESS_TERMINATE | SYNCHRONIZE, FALSE, pid) : NULL;
    if (p) { TerminateProcess(p, 0); WaitForSingleObject(p, 4000); CloseHandle(p); hlog("stopped the older 1.x copy (pid %lu)", pid); }
}

// ───────────────────────────── the address window (--setup · Shift) — Arabic, right to left
static WCHAR g_setupUrl[640]; static int g_setupDone;
static LRESULT CALLBACK SetupProc(HWND h, UINT m, WPARAM wp, LPARAM lp) {
    switch (m) {
    case WM_COMMAND:
        if (LOWORD(wp) == 1) { WCHAR u[640]; GetDlgItemTextW(h, 10, u, 640); while (u[0] == L' ') memmove(u, u + 1, wcslen(u) * sizeof(WCHAR)); url_trim(u);
            if (!url_ok(u)) { MessageBoxW(h, L"اكتب العنوان كاملاً كما تفتحه في المتصفح — يبدأ بـ http:// أو https://", APP_TITLE, MB_OK | MB_ICONWARNING | MB_RTLREADING | MB_RIGHT); return 0; }
            wcscpy_s(g_setupUrl, 640, u); g_setupDone = 1; DestroyWindow(h); return 0; }
        if (LOWORD(wp) == 2) { DestroyWindow(h); return 0; }
        break;
    case WM_CTLCOLORSTATIC: SetBkMode((HDC)wp, TRANSPARENT); return (LRESULT)GetSysColorBrush(COLOR_WINDOW);
    case WM_CLOSE: DestroyWindow(h); return 0;
    case WM_DESTROY: PostQuitMessage(0); return 0;
    }
    return DefWindowProcW(h, m, wp, lp);
}
static int setup_dialog(void) {
    g_setupDone = 0; int d = 96; { HDC dc = GetDC(NULL); d = GetDeviceCaps(dc, LOGPIXELSX); ReleaseDC(NULL, dc); }
#define S(v) MulDiv(v, d, 96)
    int W = S(520), H = S(250); RECT wa; SystemParametersInfoW(SPI_GETWORKAREA, 0, &wa, 0);
    HWND h = CreateWindowExW(WS_EX_LAYOUTRTL | WS_EX_DLGMODALFRAME | WS_EX_TOPMOST, L"HolySetup", L"The Holy Dashboard — عنوان اللوحة", WS_CAPTION | WS_SYSMENU | WS_VISIBLE,
                             (wa.left + wa.right - W) / 2, (wa.top + wa.bottom - H) / 2, W, H, NULL, NULL, g_hi, NULL);
    if (!h) return 0;
    NONCLIENTMETRICSW nm; nm.cbSize = sizeof nm; SystemParametersInfoW(SPI_GETNONCLIENTMETRICS, sizeof nm, &nm, 0); nm.lfMessageFont.lfHeight = -S(15);
    HFONT f = CreateFontIndirectW(&nm.lfMessageFont);
    HWND c1 = CreateWindowExW(0, L"STATIC", L"اكتب عنوان لوحتك كما تفتحه في المتصفح (الحاسوب أو الخادم الذي تعمل عليه البوتات):", WS_CHILD | WS_VISIBLE, S(18), S(16), W - S(50), S(44), h, NULL, g_hi, NULL);
    WCHAR cur[640]; EnterCriticalSection(&g_cs); wcscpy_s(cur, 640, g_url); LeaveCriticalSection(&g_cs);
    HWND e = CreateWindowExW(WS_EX_CLIENTEDGE | WS_EX_NOINHERITLAYOUT, L"EDIT", cur, WS_CHILD | WS_VISIBLE | WS_TABSTOP | ES_AUTOHSCROLL | ES_LEFT, S(18), S(66), W - S(50), S(30), h, (HMENU)10, g_hi, NULL);
    HWND c2 = CreateWindowExW(0, L"STATIC", L"مثال:  http://192.168.1.10:8099  (يُحفظ لهذا الحاسوب)", WS_CHILD | WS_VISIBLE, S(18), S(102), W - S(50), S(22), h, NULL, g_hi, NULL);
    HWND b1 = CreateWindowExW(0, L"BUTTON", L"حفظ وفتح", WS_CHILD | WS_VISIBLE | WS_TABSTOP | BS_DEFPUSHBUTTON, S(18), S(150), S(130), S(34), h, (HMENU)1, g_hi, NULL);
    HWND b2 = CreateWindowExW(0, L"BUTTON", L"إلغاء", WS_CHILD | WS_VISIBLE | WS_TABSTOP, S(158), S(150), S(110), S(34), h, (HMENU)2, g_hi, NULL);
    HWND all[] = { c1, e, c2, b1, b2 }; for (int i = 0; i < 5; i++) SendMessageW(all[i], WM_SETFONT, (WPARAM)f, TRUE);
#undef S
    SetForegroundWindow(h); SetFocus(e); SendMessageW(e, EM_SETSEL, 0, -1);
    MSG msg; while (GetMessageW(&msg, NULL, 0, 0) > 0) { if (!IsDialogMessageW(h, &msg)) { TranslateMessage(&msg); DispatchMessageW(&msg); } }
    DeleteObject(f);
    if (g_setupDone) { char a[700]; w8(g_setupUrl, a, sizeof a); ini_load(); ini_set("url", a); ini_save();
        EnterCriticalSection(&g_cs); wcscpy_s(g_url, 640, g_setupUrl); LeaveCriticalSection(&g_cs); hlog("address set in the window"); }
    return g_setupDone;
}

// ───────────────────────────── shortcuts · start with Windows
static int in_temp(void) { WCHAR l[MAX_PATH]; wcscpy_s(l, MAX_PATH, g_exe); _wcslwr_s(l, MAX_PATH);
    return wcsstr(l, L"\\temp\\") || wcsstr(l, L"\\inetcache\\") || wcsstr(l, L"\\temporary internet files\\"); }
static void shortcut(int csidl, int create) {
    WCHAR p[MAX_PATH]; if (FAILED(SHGetFolderPathW(NULL, csidl, NULL, 0, p))) return; wcscat_s(p, MAX_PATH, L"\\The Holy Dashboard.lnk");
    int exists = GetFileAttributesW(p) != INVALID_FILE_ATTRIBUTES; if (!exists && !create) return;
    IShellLinkW *sl = NULL; if (FAILED(CoCreateInstance(&CLSID_ShellLink, NULL, CLSCTX_INPROC_SERVER, &IID_IShellLinkW, (void **)&sl)) || !sl) return;
    if (exists) { IPersistFile *pf0 = NULL; if (SUCCEEDED(IShellLinkW_QueryInterface(sl, &IID_IPersistFile, (void **)&pf0)) && pf0) {
            WCHAR t[MAX_PATH] = L""; if (SUCCEEDED(IPersistFile_Load(pf0, p, STGM_READ))) IShellLinkW_GetPath(sl, t, MAX_PATH, NULL, 0); IPersistFile_Release(pf0);
            if (!_wcsicmp(t, g_exe)) { IShellLinkW_Release(sl); return; } } }
    IShellLinkW_SetPath(sl, g_exe); IShellLinkW_SetArguments(sl, L""); IShellLinkW_SetIconLocation(sl, g_exe, 0);
    IShellLinkW_SetDescription(sl, L"The Holy Dashboard — لوحتك بنافذتها الخاصة");
    WCHAR wd[MAX_PATH]; wcscpy_s(wd, MAX_PATH, g_exe); WCHAR *sl2 = wcsrchr(wd, L'\\'); if (sl2) *sl2 = 0; IShellLinkW_SetWorkingDirectory(sl, wd);
    IPersistFile *pf = NULL; if (SUCCEEDED(IShellLinkW_QueryInterface(sl, &IID_IPersistFile, (void **)&pf)) && pf) { IPersistFile_Save(pf, p, TRUE); IPersistFile_Release(pf); }
    IShellLinkW_Release(sl);
}
static void with_windows(void) {
    HKEY k; if (RegCreateKeyExW(HKEY_CURRENT_USER, L"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, NULL, 0, KEY_SET_VALUE, NULL, &k, NULL) != ERROR_SUCCESS) return;
    WCHAR v[MAX_PATH + 20]; _snwprintf_s(v, MAX_PATH + 20, _TRUNCATE, L"\"%s\" --tray", g_exe);
    LONG r = RegSetValueExW(k, L"TheHolyDashboard", 0, REG_SZ, (const BYTE *)v, (DWORD)((wcslen(v) + 1) * sizeof(WCHAR))); RegCloseKey(k);
    if (r != ERROR_SUCCESS) hlog("start with Windows: registry refused (%ld)", r);
}

static int reachable(void) {
    WCHAR u[800]; EnterCriticalSection(&g_cs); _snwprintf_s(u, 800, _TRUNCATE, L"%s/api/app/info", g_url); LeaveCriticalSection(&g_cs);
    char *b = NULL; DWORD n = 0; int st = http_get(u, NULL, 5000, &b, &n); free(b); return st > 0 && st < 500;
}

int WINAPI wWinMain(HINSTANCE hi, HINSTANCE prev, LPWSTR cmdline, int show) {
    (void)prev; (void)show; g_hi = hi; InitializeCriticalSection(&g_cs);
    { typedef BOOL (WINAPI *F)(HANDLE); F f = (F)GetProcAddress(GetModuleHandleW(L"user32.dll"), "SetProcessDpiAwarenessContext"); if (f) f((HANDLE)-4); }
    CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);
    INITCOMMONCONTROLSEX ic = { sizeof ic, ICC_STANDARD_CLASSES }; InitCommonControlsEx(&ic);
    GetModuleFileNameW(NULL, g_exe, MAX_PATH);
    WCHAR ad[MAX_PATH], la[MAX_PATH];
    if (FAILED(SHGetFolderPathW(NULL, CSIDL_APPDATA, NULL, 0, ad))) GetTempPathW(MAX_PATH, ad);
    if (FAILED(SHGetFolderPathW(NULL, CSIDL_LOCAL_APPDATA, NULL, 0, la))) wcscpy_s(la, MAX_PATH, ad);
    _snwprintf_s(g_dir, MAX_PATH, _TRUNCATE, L"%s\\HolyDashboard", ad); CreateDirectoryW(g_dir, NULL);
    _snwprintf_s(g_ini, MAX_PATH, _TRUNCATE, L"%s\\holy.ini", g_dir); _snwprintf_s(g_log, MAX_PATH, _TRUNCATE, L"%s\\holy.log", g_dir);
    WCHAR ld[MAX_PATH]; _snwprintf_s(ld, MAX_PATH, _TRUNCATE, L"%s\\HolyDashboard", la); CreateDirectoryW(ld, NULL);
    _snwprintf_s(g_udf, MAX_PATH, _TRUNCATE, L"%s\\WebView2", ld); _snwprintf_s(g_prof, MAX_PATH, _TRUNCATE, L"%s\\Browser", ld);
    int argc = 0; LPWSTR *argv = CommandLineToArgvW(cmdline && cmdline[0] ? GetCommandLineW() : L"x", &argc);
    int a_setup = 0, a_tray = 0, a_restart = 0;
    for (int i = 1; argv && i < argc; i++) { if (!_wcsicmp(argv[i], L"--setup")) a_setup = 1; else if (!_wcsicmp(argv[i], L"--tray")) a_tray = 1; else if (!_wcsicmp(argv[i], L"--restart")) a_restart = 1; }
    if (!a_tray && (GetKeyState(VK_SHIFT) & 0x8000)) a_setup = 1;
    g_icon = (HICON)LoadImageW(hi, MAKEINTRESOURCEW(1), IMAGE_ICON, GetSystemMetrics(SM_CXICON) * 2, GetSystemMetrics(SM_CYICON) * 2, LR_DEFAULTCOLOR);
    g_iconSm = (HICON)LoadImageW(hi, MAKEINTRESOURCEW(1), IMAGE_ICON, GetSystemMetrics(SM_CXSMICON), GetSystemMetrics(SM_CYSMICON), LR_DEFAULTCOLOR);
    if (!g_icon) g_icon = LoadIconW(NULL, IDI_APPLICATION); if (!g_iconSm) g_iconSm = g_icon;
    g_bgBrush = CreateSolidBrush(BG_RGB);
    WNDCLASSEXW wc; memset(&wc, 0, sizeof wc); wc.cbSize = sizeof wc; wc.hInstance = hi; wc.hIcon = g_icon; wc.hIconSm = g_iconSm; wc.hCursor = LoadCursorW(NULL, IDC_ARROW);
    wc.lpfnWndProc = SetupProc; wc.lpszClassName = L"HolySetup"; wc.hbrBackground = GetSysColorBrush(COLOR_WINDOW); RegisterClassExW(&wc);
    wc.lpfnWndProc = WinProc; wc.lpszClassName = L"HolyDash"; wc.hbrBackground = NULL; wc.style = CS_HREDRAW | CS_VREDRAW; RegisterClassExW(&wc);
    wc.lpfnWndProc = TrayProc; wc.lpszClassName = L"HolyTray2"; wc.style = 0; RegisterClassExW(&wc);
    config_load();
    { char a[200]; w8(g_url, a, sizeof a); hlog("start v2.0%s%s%s · %s", a_tray ? " (with Windows)" : "", a_setup ? " (setup)" : "", a_restart ? " (restart)" : "", a[0] ? "address set" : "no address"); }

    HWND run = FindWindowW(L"HolyTray2", NULL);
    if (a_tray && run) return 0;                                  // Windows started it while one is running
    if (!a_tray) {
        int changed = 0;
        if (a_setup || !g_url[0]) { if (!setup_dialog()) { hlog("address window closed — nothing opened"); return 0; } changed = 1; }
        while (!reachable()) {
            WCHAR t[900]; EnterCriticalSection(&g_cs);
            _snwprintf_s(t, 900, _TRUNCATE, L"تعذّر الوصول إلى اللوحة على:\n%s\n\nنعم = غيّر العنوان\nلا = افتحها على كل حال\nإلغاء = لا شيء", g_url); LeaveCriticalSection(&g_cs);
            int r = MessageBoxW(NULL, t, APP_TITLE, MB_YESNOCANCEL | MB_ICONWARNING | MB_RTLREADING | MB_RIGHT | MB_SETFOREGROUND);
            hlog("bad address — %s", r == IDYES ? "change" : r == IDNO ? "open anyway" : "cancel");
            if (r == IDYES) { if (!setup_dialog()) return 0; changed = 1; continue; }
            if (r == IDNO) break;
            return 0;
        }
        if (run) {                                                // one watcher: the running copy opens the window
            AllowSetForegroundWindow(ASFW_ANY);
            if ((int)send_cmd(run, L"ver") >= APP_BUILD) { if (changed) send_cmd(run, L"cfg"); send_cmd(run, L"open"); hlog("handed over to the running copy"); return 0; }
            send_cmd(run, L"quit"); for (int i = 0; i < 40 && FindWindowW(L"HolyTray2", NULL); i++) Sleep(100);
        }
        if (!in_temp()) { ini_load(); int first = strcmp(ini_get("v"), "2"); shortcut(CSIDL_DESKTOPDIRECTORY, first); shortcut(CSIDL_PROGRAMS, first);
            if (first) { ini_set("v", "2"); ini_save(); } }
        else hlog("running from a temporary folder — no shortcuts (save the program somewhere first)");
    }
    if (a_restart) for (int i = 0; i < 50 && FindWindowW(L"HolyTray2", NULL); i++) Sleep(100);
    g_mutex = CreateMutexW(NULL, TRUE, L"Local\\TheHolyDashboard.Watcher2");
    if (GetLastError() == ERROR_ALREADY_EXISTS) { HWND r2 = FindWindowW(L"HolyTray2", NULL); if (r2 && !a_tray) send_cmd(r2, L"open"); return 0; }
    retire_old();
    if (!in_temp()) with_windows();
    g_taskbarCreated = RegisterWindowMessageW(L"TaskbarCreated");
    g_tray = CreateWindowExW(0, L"HolyTray2", L"The Holy Dashboard (notifications)", 0, 0, 0, 0, 0, NULL, NULL, hi, NULL);
    { typedef BOOL (WINAPI *F)(HWND, UINT, DWORD, void *); F f = (F)GetProcAddress(GetModuleHandleW(L"user32.dll"), "ChangeWindowMessageFilterEx");
      if (f) { f(g_tray, WM_COPYDATA, 1, NULL); if (g_taskbarCreated) f(g_tray, g_taskbarCreated, 1, NULL); } }
    tray_icon(NIM_ADD);
    hlog("notifications watcher running");
    CreateThread(NULL, 0, feed_thread, NULL, 0, NULL);
    if (!a_tray) open_window(NULL);
    MSG msg; while (GetMessageW(&msg, NULL, 0, 0) > 0) { TranslateMessage(&msg); DispatchMessageW(&msg); }
    if (g_env) ICoreWebView2Environment_Release(g_env);
    CoUninitialize(); return 0;
}
