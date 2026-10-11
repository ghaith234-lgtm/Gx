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
say "crash buffer:"; adb logcat -d -b crash | head -40 | sed 's/^/HOLYCI crash: /'
adb logcat -d | grep -E "holy|Holy|AndroidRuntime|chromium.*CONSOLE|ActivityManager.*$P" | grep -v chatty | tail -70 | sed 's/^/HOLYCI log: /'
say "done"
