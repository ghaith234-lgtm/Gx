#!/usr/bin/env python3
"""📱 Builds the Holy app (APK) from this folder — no Android Studio, no Gradle, no Google servers.

    python3 android/build.py                       # build + check, unsigned (android/build/Holy-unsigned.apk)
    HOLY_KEY_PASS=… python3 android/build.py --key /path/holy-release.p12
                                                   # build + sign + verify → android/dist/Holy-<name>.apk

What it does:
  1. tools from Maven Central only (checked by sha256, kept in android/.tools — never committed)
  2. java/ → javac (Java 8) → dx → baksmali → joined with smali/ (the app's code recovered from 1.9)
  3. smali → classes.dex
  4. the binary manifest and widget info get the numbers from version.json (versionCode · versionName ·
     the widget's height) — every other byte stays as in base/
  5. zip in the original layout (resources.arsc stored and 4-byte aligned, as Android 11+ requires)
  6. with --key: apksig signs (scheme v2 — the app needs Android 7.0+) and verifies; the password comes from HOLY_KEY_PASS only

🔐 The signing key NEVER enters this repository (it is public). Keep it outside, or as a GitHub secret.
"""
import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, ".tools")
BUILD = os.path.join(HERE, "build")
DIST = os.path.join(HERE, "dist")
MAVEN = "https://repo1.maven.org/maven2/"

# (path on Maven Central, sha256) — the exact versions this build was checked with
JARS = {
    "smali": ("org/smali/smali/2.5.2/smali-2.5.2.jar", "136c5c4653d6531bd7b6f10f35f8691cb96432e727d30b4d5579826ee01e9419"),
    "baksmali": ("org/smali/baksmali/2.5.2/baksmali-2.5.2.jar", "1ed236266d7dc4907aade0b19a34f77efac25342b63c8ace52e579039941b389"),
    "dexlib2": ("org/smali/dexlib2/2.5.2/dexlib2-2.5.2.jar", "5a5c8982d8bd7d6e3bb1a0713049e3c78b719ec32b20f6b619885cec30a0dd61"),
    "util": ("org/smali/util/2.5.2/util-2.5.2.jar", "4f580a9cff3ebb83cb3fd20bec88e37e4f183796ca652732992611620282daea"),
    "guava": ("com/google/guava/guava/27.1-android/guava-27.1-android.jar", "686404f2d1d4d221911f96bd627ff60dac2226a5dfa6fb8ba517073eb97ec0ef"),
    "failureaccess": ("com/google/guava/failureaccess/1.0.1/failureaccess-1.0.1.jar", "a171ee4c734dd2da837e4b16be9df4661afab72a41adaf31eb84dfdaf936ca26"),
    "jcommander": ("com/beust/jcommander/1.64/jcommander-1.64.jar", "156be736199c990321d9ff77090b199629cfc9865e2d6c13f7cd291bb1641817"),
    "antlr-runtime": ("org/antlr/antlr-runtime/3.5.2/antlr-runtime-3.5.2.jar", "ce3fc8ecb10f39e9a3cddcbb2ce350d272d9cd3d0b1e18e6fe73c3b9389c8734"),
    "stringtemplate": ("org/antlr/stringtemplate/3.2.1/stringtemplate-3.2.1.jar", "f66ce72e965e5301cb0f020e54d2ba6ad76feb91b3cbfc30dbbf00c06a6df6d7"),
    "antlr": ("antlr/antlr/2.7.7/antlr-2.7.7.jar", "88fbda4b912596b9f56e8e12e580cc954bacfb51776ecfddd3e18fc1cf56dc4c"),
    "dx": ("com/jakewharton/android/repackaged/dalvik-dx/16.0.1/dalvik-dx-16.0.1.jar", "1e4b645628e3bdb097b5331d669e177ef235a551582a8c646dbe36865e541907"),
    "apksig": ("com/android/tools/build/apksig/2.3.0/apksig-2.3.0.jar", "9637078c0016244e4be0941836295365a7e2e5b164c59cb7885783c40460bfee"),
    # compile-only stubs for javac (Android API 16 + org.json): the classes only name these, the phone supplies them
    "android-stubs": ("com/google/android/android/4.1.1.4/android-4.1.1.4.jar", "84072541cbb711eff89f7277100ff854929a446dba7ceb1b195c340e0b4fd3cb"),
    "json-stubs": ("org/json/json/20080701/json-20080701.jar", "03acd6adab2da447f49814751b0e953fb62a6a1023f9d2a705c30a6e3e4638eb"),
}
SMALI_CP = ["smali", "baksmali", "dexlib2", "util", "guava", "failureaccess", "jcommander", "antlr-runtime", "stringtemplate", "antlr"]

# android: attribute resource ids
A_VERSION_CODE, A_VERSION_NAME = 0x0101021B, 0x0101021C
A_MIN_HEIGHT, A_TARGET_CELL_H = 0x01010140, 0x01010635
T_STRING, T_DIMENSION, T_INT_DEC = 0x03, 0x05, 0x10


def say(*a):
    print("📱", *a, flush=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def jar(name):
    rel, want = JARS[name]
    path = os.path.join(TOOLS, os.path.basename(rel))
    if not (os.path.isfile(path) and sha256(path) == want):
        os.makedirs(TOOLS, exist_ok=True)
        say("downloading", os.path.basename(rel))
        tmp = path + ".part"
        with urllib.request.urlopen(MAVEN + rel, timeout=120) as r, open(tmp, "wb") as f:
            shutil.copyfileobj(r, f)
        got = sha256(tmp)
        if got != want:
            os.remove(tmp)
            raise SystemExit("❌ %s: sha256 %s ≠ %s" % (rel, got, want))
        os.replace(tmp, path)
    return path


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "JAVA_TOOL_OPTIONS" not in l)
    if r.returncode != 0:
        raise SystemExit("❌ %s\n%s" % (" ".join(cmd[:4]), out))
    return out


# ---------- binary XML (AXML) ----------

def _pool_strings(d, off):
    count, styles, flags, start, _ = struct.unpack_from("<IIIII", d, off + 8)
    if flags & 0x100 or styles:
        raise SystemExit("❌ unexpected string pool (utf8 or styles)")
    offs = struct.unpack_from("<%dI" % count, d, off + 28)
    out = []
    for o in offs:
        p = off + start + o
        n = struct.unpack_from("<H", d, p)[0]
        if n & 0x8000:
            raise SystemExit("❌ long string in pool")
        out.append(d[p + 2:p + 2 + 2 * n].decode("utf-16le"))
    return out


def _pool_bytes(strings):
    """a UTF-16 string pool chunk (no styles) — same layout aapt writes"""
    offs, body = [], b""
    for s in strings:
        offs.append(len(body))
        u = s.encode("utf-16le")
        body += struct.pack("<H", len(u) // 2) + u + b"\0\0"
    body += b"\0" * (-len(body) % 4)
    start = 28 + 4 * len(strings)
    return struct.pack("<HHIIIIII", 0x0001, 28, start + len(body), len(strings), 0, 0, start, 0) + struct.pack("<%dI" % len(strings), *offs) + body


def axml_patch(data, element, ints=None, strings=None):
    """sets attributes of <element> by android resource id: ints {id: (type, data)} · strings {id: text}.
    New strings are appended to the pool so no existing index moves."""
    ints, strings = ints or {}, strings or {}
    d = bytearray(data)
    t, hs, size = struct.unpack_from("<HHI", d, 0)
    assert t == 0x0003 and size == len(d), "not a binary XML"
    off = hs
    pool_off = resmap = None
    pool = []
    hits = set()
    while off < len(d):
        t, hs, sz = struct.unpack_from("<HHI", d, off)
        if t == 0x0001:
            pool_off, pool = off, _pool_strings(d, off)
        elif t == 0x0180:
            resmap = list(struct.unpack_from("<%dI" % ((sz - 8) // 4), d, off + 8))
        elif t == 0x0102:
            _, name, astart, asize, acount = struct.unpack_from("<iiHHH", d, off + 16)
            if pool[name] == element:
                for i in range(acount):
                    a = off + 16 + astart + i * asize
                    an = struct.unpack_from("<i", d, a + 4)[0]
                    rid = resmap[an] if 0 <= an < len(resmap) else None
                    if rid in ints:
                        typ, val = ints[rid]
                        struct.pack_into("<iHBBI", d, a + 8, -1, 8, 0, typ, val)
                        hits.add(rid)
                    elif rid in strings:
                        txt = strings[rid]
                        if txt not in pool:
                            pool.append(txt)
                        idx = pool.index(txt)
                        struct.pack_into("<iHBBI", d, a + 8, idx, 8, 0, T_STRING, idx)
                        hits.add(rid)
        off += sz
    missing = (set(ints) | set(strings)) - hits
    if missing:
        raise SystemExit("❌ <%s> lacks %s" % (element, ", ".join(hex(m) for m in sorted(missing))))
    old_sz = struct.unpack_from("<I", d, pool_off + 4)[0]
    new_pool = _pool_bytes(pool)
    d[pool_off:pool_off + old_sz] = new_pool
    struct.pack_into("<I", d, 4, len(d))
    return bytes(d)


def axml_read(data, element):
    """{resource id: (type, data, text)} of <element>'s attributes — for the checks"""
    d = data
    off = struct.unpack_from("<HHI", d, 0)[1]
    pool, resmap, out = [], [], {}
    while off < len(d):
        t, hs, sz = struct.unpack_from("<HHI", d, off)
        if t == 0x0001:
            pool = _pool_strings(d, off)
        elif t == 0x0180:
            resmap = list(struct.unpack_from("<%dI" % ((sz - 8) // 4), d, off + 8))
        elif t == 0x0102:
            _, name, astart, asize, acount = struct.unpack_from("<iiHHH", d, off + 16)
            if pool[name] == element:
                for i in range(acount):
                    a = off + 16 + astart + i * asize
                    an, raw, _, _, typ, val = struct.unpack_from("<iiHBBI", d, a + 4)
                    if 0 <= an < len(resmap):
                        out[resmap[an]] = (typ, val, pool[val] if typ == T_STRING else None)
        off += sz
    return out


# ---------- zip ----------

STORED = (".png", ".ogg", ".arsc")


def zip_apk(path, files):
    """files: [(name, bytes)] — stored entries 4-byte aligned (zipalign -p 4), fixed time for a stable build"""
    with zipfile.ZipFile(path, "w") as z:
        for name, body in files:
            zi = zipfile.ZipInfo(name, date_time=(1981, 1, 1, 1, 1, 2))
            zi.create_system = 0
            zi.external_attr = 0
            if name.endswith(STORED):
                zi.compress_type = zipfile.ZIP_STORED
                data_at = z.fp.tell() + 30 + len(name.encode())
                zi.extra = b"\0" * (-data_at % 4)
            else:
                zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, body, compresslevel=9 if zi.compress_type == zipfile.ZIP_DEFLATED else None)


def check_aligned(path):
    with open(path, "rb") as f:
        raw = f.read()
    with zipfile.ZipFile(path) as z:
        for zi in z.infolist():
            if zi.compress_type == zipfile.ZIP_STORED:
                n, e = struct.unpack_from("<HH", raw, zi.header_offset + 26)
                at = zi.header_offset + 30 + n + e
                if at % 4:
                    raise SystemExit("❌ %s is not 4-byte aligned" % zi.filename)


def check_version(smali_dir, ver):
    """the app states its own version in several places (it was built that way) — they must all agree with version.json"""
    import re
    bad = []
    num = re.compile(r"(?<![\d.])\d+\.\d+(?![\d.])")
    for root, _, names in os.walk(smali_dir):
        for n in names:
            path = os.path.join(root, n)
            L = [l.strip() for l in open(path, encoding="utf-8")]
            L = [l for l in L if l and not l.startswith(".line")]
            for i, l in enumerate(L):
                m = re.match(r'const-string(?:/jumbo)? v\d+, "(.*)"$', l)
                if m:
                    txt = re.sub(r"\\u([0-9a-f]{4})", lambda x: chr(int(x.group(1), 16)), m.group(1))
                    for v in num.findall(txt):
                        if v != ver["name"]:
                            bad.append("%s: «%s»" % (n, txt))
                    nxt = L[i + 1] if i + 1 < len(L) else ""
                    if txt == "code" and nxt.startswith("const/16 ") and int(nxt.split(",")[1], 16) != ver["code"]:
                        bad.append("%s: code %s" % (n, nxt))
                if l.endswith("->val$code:I") and i + 1 < len(L) and L[i + 1].startswith("const/16 "):
                    if int(L[i + 1].split(",")[1], 16) != ver["code"]:
                        bad.append("%s: update check %s" % (n, L[i + 1]))
                if l.startswith(".field static final VERSION_CODE:I = ") and int(l.split("= ")[1], 16) != ver["code"]:
                    bad.append("%s: %s" % (n, l))
                if l.startswith(".field static final VERSION_NAME:") and not l.endswith('"%s"' % ver["name"]):
                    bad.append("%s: %s" % (n, l))
    if bad:
        raise SystemExit("❌ the app's code doesn't say version %s (%d) everywhere:\n  " % (ver["name"], ver["code"]) + "\n  ".join(bad))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", help="the signing key (PKCS12) — outside this repository; password in HOLY_KEY_PASS")
    ap.add_argument("--out", help="where the signed app goes (default android/dist/Holy-<name>.apk)")
    args = ap.parse_args()

    ver = json.load(open(os.path.join(HERE, "version.json")))
    say("Holy %s (code %d)" % (ver["name"], ver["code"]))
    if os.path.isdir(BUILD):
        shutil.rmtree(BUILD)
    os.makedirs(BUILD)
    check_version(os.path.join(HERE, "smali"), ver)
    smali_cp = os.pathsep.join(jar(n) for n in SMALI_CP)

    # 2. java → class → dex → smali
    java_files = []
    for root, _, names in os.walk(os.path.join(HERE, "java")):
        java_files += [os.path.join(root, n) for n in sorted(names) if n.endswith(".java")]
    jsmali = os.path.join(BUILD, "smali_java")
    if java_files:
        classes = os.path.join(BUILD, "classes")
        os.makedirs(classes)
        run(["javac", "--release", "8", "-encoding", "UTF-8", "-Xlint:-options", "-nowarn",
             "-cp", os.pathsep.join([jar("android-stubs"), jar("json-stubs")]), "-d", classes] + java_files)
        jdex = os.path.join(BUILD, "java.dex")
        run(["java", "-cp", jar("dx"), "com.android.dx.command.Main", "--dex", "--min-sdk-version=24", "--output=" + jdex, classes])
        run(["java", "-cp", smali_cp, "org.jf.baksmali.Main", "d", "-o", jsmali, jdex])

    # join: the recovered code + the new Java classes (a Java class may not replace a smali one)
    allsmali = os.path.join(BUILD, "smali")
    shutil.copytree(os.path.join(HERE, "smali"), allsmali)
    for root, _, names in os.walk(jsmali):
        for n in names:
            src = os.path.join(root, n)
            dst = os.path.join(allsmali, os.path.relpath(src, jsmali))
            if os.path.exists(dst):
                raise SystemExit("❌ java/ and smali/ both define " + os.path.relpath(src, jsmali))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)

    # 3. smali → classes.dex
    dex = os.path.join(BUILD, "classes.dex")
    run(["java", "-cp", smali_cp, "org.jf.smali.Main", "a", "--api", "24", "-j", "1", "-o", dex, allsmali])  # one thread: the same dex every time

    # 4. manifest + widget info
    base = os.path.join(HERE, "base")
    man = axml_patch(open(os.path.join(base, "AndroidManifest.xml"), "rb").read(), "manifest",
                     ints={A_VERSION_CODE: (T_INT_DEC, ver["code"])}, strings={A_VERSION_NAME: ver["name"]})
    info = axml_patch(open(os.path.join(base, "res/xml/holy_widget_info.xml"), "rb").read(), "appwidget-provider",
                      ints={A_MIN_HEIGHT: (T_DIMENSION, (ver["widget_min_height_dp"] << 8) | 0x01),
                            A_TARGET_CELL_H: (T_INT_DEC, ver["widget_target_cell_height"])})
    m = axml_read(man, "manifest")
    assert m[A_VERSION_CODE][1] == ver["code"] and m[A_VERSION_NAME][2] == ver["name"], m
    w = axml_read(info, "appwidget-provider")
    assert w[A_MIN_HEIGHT][1] >> 8 == ver["widget_min_height_dp"] and w[A_TARGET_CELL_H][1] == ver["widget_target_cell_height"], w

    # 5. zip
    files = [("AndroidManifest.xml", man), ("classes.dex", open(dex, "rb").read()),
             ("resources.arsc", open(os.path.join(base, "resources.arsc"), "rb").read())]
    for root, _, names in os.walk(os.path.join(base, "res")):
        for n in names:
            p = os.path.join(root, n)
            rel = os.path.relpath(p, base).replace(os.sep, "/")
            files.append((rel, info if rel == "res/xml/holy_widget_info.xml" else open(p, "rb").read()))
    files = files[:3] + sorted(files[3:])
    unsigned = os.path.join(BUILD, "Holy-unsigned.apk")
    zip_apk(unsigned, files)
    check_aligned(unsigned)
    say("built", os.path.relpath(unsigned, os.getcwd()), os.path.getsize(unsigned), "bytes")

    if not args.key:
        say("no --key: left unsigned")
        return
    # 6. sign + verify
    tools = os.path.join(BUILD, "tools")
    os.makedirs(tools)
    run(["javac", "--release", "8", "-Xlint:-options", "-nowarn", "-cp", jar("apksig"), "-d", tools, os.path.join(HERE, "tools", "Sign.java")])
    cp = os.pathsep.join([jar("apksig"), tools])
    # apksig 2.3.0 (the only one on Maven Central) touches the JDK's own security classes
    opens = []
    for pkg in ("sun.security.pkcs", "sun.security.util", "sun.security.x509"):
        opens += ["--add-exports", "java.base/%s=ALL-UNNAMED" % pkg]
    out = args.out or os.path.join(DIST, "Holy-%s.apk" % ver["name"])
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    run(["java"] + opens + ["-cp", cp, "Sign", "sign", unsigned, out, args.key])
    check_aligned(out)
    v = run(["java"] + opens + ["-cp", cp, "Sign", "verify", out])
    say(v.strip().replace("\n", " · "))
    say("signed", out, os.path.getsize(out), "bytes · sha256", sha256(out))


if __name__ == "__main__":
    main()
