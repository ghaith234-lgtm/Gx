#!/bin/bash
# 📱 Holy APK on a real Android emulator — every result line starts with HOLYCI / HOLYUI / HOLYIMG / HOLYNOTIF
set -u
P=com.holy.dash
OUT=ci_out; mkdir -p $OUT
say(){ echo "HOLYCI $*"; }
dump(){ adb shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1; adb pull /sdcard/ui.xml $OUT/ui_$1.xml >/dev/null 2>&1; python3 ci/ci_tools.py texts $OUT/ui_$1.xml "$1"; }
shot(){ adb exec-out screencap -p > $OUT/$1.png 2>/dev/null; python3 ci/ci_tools.py img $OUT/$1.png "$1"; }
tap(){ xy=$(python3 ci/ci_tools.py find $OUT/ui_$2.xml "$1"); if [ -n "$xy" ]; then adb shell input tap $xy; say "tap «$1» at $xy"; else say "tap «$1» NOT FOUND"; fi; }
api(){ curl -s -X POST "localhost:8099$1" -H 'Content-Type: application/json' -d "$2"; echo; }

API=$(adb shell getprop ro.build.version.sdk | tr -d '\r')
say "android api $API · webview $(adb shell dumpsys package com.google.android.webview 2>/dev/null | grep -m1 versionName | tr -d '\r ')"
adb logcat -c
adb install -r holy.apk 2>&1 | tail -1 | sed 's/^/HOLYCI install: /'
adb shell pm list packages | grep -q "$P" && say "PASS installed" || { say "FAIL install"; exit 1; }
adb shell dumpsys package $P | grep -E "versionCode|versionName|targetSdk|signatures|pkgFlags" | head -6 | sed 's/^/HOLYCI pkg: /'
[ "$API" -ge 33 ] && adb shell pm grant $P android.permission.POST_NOTIFICATIONS
adb shell am start -n $P/.MainActivity --es url http://10.0.2.2:8099 >/dev/null
sleep 7; dump setup; shot setup
tap "اتصال" setup
sleep 18; dump dash1
if grep -q "متصفح النظام قديم" $OUT/ui_dash1.xml; then say "PASS old system WebView ⇒ the app asks to update it"; tap "بعدين" dash1; sleep 2; dump dash1; fi
if grep -q "بعدين" $OUT/ui_dash1.xml; then say "PASS battery dialog shown after linking"; tap "بعدين" dash1; sleep 2; fi
sleep 3; dump dash; shot dash
api /api/app/devices '{"act":"list"}' | sed 's/^/HOLYCI devices: /'
adb shell dumpsys activity services $P | grep -E "ServiceRecord|isForeground|foregroundServiceType|types=" | head -6 | sed 's/^/HOLYCI svc: /'
for i in 1 2 3; do api /api/app/devices '{"act":"test","sample":"trade"}' >/dev/null; sleep 1.2; done
api /api/app/devices '{"act":"test","sample":"alert"}' >/dev/null
sleep 8
adb shell dumpsys notification --noredact | python3 ci/ci_tools.py notif $P
adb shell cmd statusbar expand-notifications; sleep 3; shot shade; dump shade; adb shell cmd statusbar collapse; sleep 1
adb shell am start -n $P/.MainActivity --es go reports >/dev/null; sleep 5; dump reports; shot reports
adb shell input keyevent 4; sleep 2; dump back1
adb shell dumpsys window | grep -E "statusBars|navigationBars|mSystemUiVisibility|InsetsSource type=(ITYPE_)?(STATUS|NAVIGATION)|mCurrentFocus" | head -14 | sed 's/^/HOLYCI win: /'
adb shell settings put system accelerometer_rotation 0; adb shell settings put system user_rotation 1; sleep 4; shot land
adb shell settings put system user_rotation 0; sleep 3
adb shell am start -n $P/.MainActivity --es go guard >/dev/null; sleep 4; dump guard
pid=$(adb shell pidof $P | tr -d '\r'); say "app pid: ${pid:-NONE}"
# ── self-update: the dashboard now carries a «newer» APK (same file, higher code) ⇒ offer · download · sha256 · Android installer ──
t0=$(adb shell dumpsys package $P | grep -m1 lastUpdateTime | tr -d '\r')
pkill -f Holy_Dashboard.pyw; sleep 2
sed -i 's/^APP_APK_CODE = .*/APP_APK_CODE = 99/' /tmp/holy/Holy_Dashboard.pyw
(cd /tmp/holy && setsid nohup python3 Holy_Dashboard.pyw >> dash.log 2>&1 < /dev/null &)   # fully detached (or the CI step never ends)
for i in $(seq 1 40); do curl -sf localhost:8099/ >/dev/null && break; sleep 1; done
curl -s localhost:8099/api/app/info -H "X-Holy-Device: x" | head -c 200; echo
adb shell appops set $P REQUEST_INSTALL_PACKAGES allow
adb shell am force-stop $P; sleep 1
adb shell am start -n $P/.MainActivity >/dev/null; sleep 12; dump upd1; shot upd1
if grep -q "تحديث للتطبيق" $OUT/ui_upd1.xml; then say "PASS update offered"; tap "تحديث" upd1; else say "FAIL no update offer"; fi
sleep 10; dump upd2; shot upd2
for b in "Update" "UPDATE" "Install" "INSTALL" "تحديث" "تثبيت"; do if grep -q "text=\"$b\"" $OUT/ui_upd2.xml; then tap "$b" upd2; say "PASS Android installer asked to confirm («$b»)"; break; fi; done
sleep 15
t1=$(adb shell dumpsys package $P | grep -m1 lastUpdateTime | tr -d '\r')
[ "$t0" != "$t1" ] && say "PASS app updated itself ($t0 → $t1)" || say "FAIL app not updated ($t1)"
sleep 5
adb shell dumpsys activity services $P | grep -E "WatchService|isForeground" | head -3 | sed 's/^/HOLYCI after-update svc: /'
pid=$(adb shell pidof $P | tr -d '\r'); say "app pid after update: ${pid:-NONE}"
# ── unlink from the dashboard ⇒ «انفصل» on the phone at once · no silent re-link next time ──
id=$(curl -s -X POST localhost:8099/api/app/devices -H 'Content-Type: application/json' -d '{"act":"list"}' | python3 -c "import sys,json;d=json.load(sys.stdin)['devs'];print(d[0]['id'] if d else '')")
say "unlinking device ${id:-NONE}"
api /api/app/devices "{\"act\":\"del\",\"id\":\"$id\"}" | head -c 100; echo
sleep 10
adb shell dumpsys notification --noredact | grep -q "انفصل هذا الموبايل" && say "PASS unlinked phone shows «انفصل» at once" || say "FAIL no unlink notice"
adb shell am force-stop $P; adb shell am start -n $P/.MainActivity >/dev/null; sleep 15
n=$(curl -s -X POST localhost:8099/api/app/devices -H 'Content-Type: application/json' -d '{"act":"list"}' | python3 -c "import sys,json;print(len(json.load(sys.stdin)['devs']))")
[ "$n" = "0" ] && say "PASS no silent re-link after unlink" || say "FAIL re-linked by itself ($n)"
say "crash buffer:"; adb logcat -d -b crash | head -40 | sed 's/^/HOLYCI crash: /'
adb logcat -d | grep -E "holy|Holy|AndroidRuntime|chromium.*CONSOLE|ActivityManager.*$P" | grep -v chatty | tail -70 | sed 's/^/HOLYCI log: /'
pkill -f Holy_Dashboard.pyw || true      # the CI step ends only when nothing it started is still running
say "done"
