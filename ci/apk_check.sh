#!/bin/bash
# 📱 Holy APK on a real Android emulator — every result line starts with HOLYCI / HOLYUI / HOLYIMG / HOLYNOTIF
set -u
P=com.holy.dash
OUT=ci_out; mkdir -p $OUT
say(){ echo "HOLYCI $*"; }
# uiautomator can die once (e.g. right after «adb root» restarts adbd) ⇒ an empty screen ⇒ try again
dump(){ for t in 1 2 3 4 5 6; do rm -f $OUT/ui_$1.xml; adb shell rm -f /sdcard/ui.xml >/dev/null 2>&1; adb shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1; adb pull /sdcard/ui.xml $OUT/ui_$1.xml >/dev/null 2>&1
  grep -q "<node" $OUT/ui_$1.xml 2>/dev/null && break; sleep 3; done; python3 ci/ci_tools.py texts $OUT/ui_$1.xml "$1"; }
shot(){ adb exec-out screencap -p > $OUT/$1.png 2>/dev/null; python3 ci/ci_tools.py img $OUT/$1.png "$1"; }
tap(){ xy=$(python3 ci/ci_tools.py find $OUT/ui_$2.xml "$1"); if [ -n "$xy" ]; then adb shell input tap $xy; say "tap «$1» at $xy"; else say "tap «$1» NOT FOUND"; fi; }
api(){ curl -s -X POST "localhost:8099$1" -H 'Content-Type: application/json' -d "$2"; echo; }

API=$(adb shell getprop ro.build.version.sdk | tr -d '\r')
say "android api $API · webview $(adb shell dumpsys package com.google.android.webview 2>/dev/null | grep -m1 versionName | tr -d '\r ')"
adb logcat -c
# ── 1.4: start from the previous app (1.3 — taken from the v3.26.6 release commit) ⇒ the real update path: old channels go · the Holy-tone channels come ──
OLDC=cbfbf7c03a3b465c77a86b2da09f36e9cb27cd0f
if git fetch -q --depth=1 origin $OLDC 2>/dev/null && git show FETCH_HEAD:Holy_Dashboard.pyw | python3 ci/ci_tools.py apk > old.apk 2>/dev/null && [ -s old.apk ]; then
  adb install old.apk 2>&1 | tail -1 | sed 's/^/HOLYCI install 1.3: /'
  adb shell dumpsys package $P | grep -m1 versionName | tr -d '\r' | sed 's/^/HOLYCI before update: /'
  adb shell am start -n $P/.MainActivity >/dev/null; sleep 8
  adb shell dumpsys notification --noredact | grep -oE "mId='(trade|alert|info|watch)'[^}]{0,40}" | sort -u | head -4 | sed 's/^/HOLYCI 1.3 channel: /'
  adb shell am force-stop $P
else say "INFO couldn't fetch the 1.3 app ⇒ fresh install only"; fi
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
# ── 1.1: notifications with the app CLOSED — swiped away · process killed (what phone «cleaners» do) · deep sleep (Doze) ──
linked=$(curl -s -X POST localhost:8099/api/app/devices -H 'Content-Type: application/json' -d '{"act":"list"}' | python3 -c "import sys,json;print(len(json.load(sys.stdin)['devs']))")
if [ "$linked" = "0" ]; then say "SKIP app-closed tests — this phone never linked (its system WebView cannot run the page)"; else
note(){ api /api/app/devices "{\"act\":\"test\",\"tag\":\"$1\"}" >/dev/null; }
got(){ for i in $(seq 1 ${2:-25}); do adb shell dumpsys notification --noredact | grep -q "$1" && return 0; sleep 1; done; return 1; }
svc(){ adb shell dumpsys activity services $P | grep -c "WatchService" | tr -d '\r'; }
adb shell dumpsys jobscheduler | grep -q "$P/.KeepJob" && say "PASS backup check scheduled (every 15 min · survives reboot)" || say "FAIL backup check not scheduled"
adb shell input keyevent KEYCODE_HOME; sleep 2
note HOME1; got HOME1 && say "PASS app in background ⇒ notification arrives" || say "FAIL app in background ⇒ no notification"
sz=$(adb shell wm size | grep -oE "[0-9]+x[0-9]+" | tail -1); W_=${sz%x*}; H_=${sz#*x}
adb shell input keyevent KEYCODE_APP_SWITCH; sleep 3
adb shell input swipe $((W_/2)) $((H_*6/10)) $((W_/2)) $((H_/20)) 250; sleep 2
adb shell input keyevent KEYCODE_HOME; sleep 4
adb shell dumpsys activity recents | grep -q "A=[0-9]*:$P" && say "INFO swipe-away gesture didn't remove the task on this emulator" || say "INFO task swiped away from recents"
say "after swipe: watcher services $(svc) · pid $(adb shell pidof $P | tr -d '\r')"
note SWIPE1; got SWIPE1 40 && say "PASS swiped away ⇒ notification still arrives" || say "FAIL swiped away ⇒ no notification"
adb root >/dev/null 2>&1; sleep 3
pid=$(adb shell pidof $P | tr -d '\r')
if [ -n "$pid" ]; then adb shell kill -9 $pid; say "killed app process $pid (like a phone cleaner)"; else say "INFO no app process to kill"; fi
sleep 3
note KILL1
if got KILL1 30; then say "PASS process killed ⇒ watcher came back by itself ⇒ notification arrives"
else
  say "INFO not back by itself within 30 s ⇒ run the 15-minute backup check now"
  adb shell cmd jobscheduler run -f $P 7311 | sed 's/^/HOLYCI job: /'
  got KILL1 40 && say "PASS process killed ⇒ backup check delivered the notification" || say "FAIL process killed ⇒ notification never arrived"
fi
say "after kill: watcher services $(svc) · pid $(adb shell pidof $P | tr -d '\r')"
adb shell dumpsys deviceidle force-idle | sed 's/^/HOLYCI doze: /'
note DOZE1; got DOZE1 40 && say "PASS deep sleep (Doze) ⇒ notification arrives" || say "FAIL deep sleep (Doze) ⇒ no notification"
adb shell dumpsys deviceidle unforce >/dev/null
adb shell am start -n $P/.MainActivity >/dev/null; sleep 6
# ── 1.3 (1.4: no big picture any more): the notifications · the watcher line (no «يراقب» · secret on the lock screen) can be turned off ⇒ alerts keep coming ──
adb shell dumpsys notification --noredact > $OUT/n13.txt
nl=$(grep -c "android.largeIcon=Icon" $OUT/n13.txt | tr -d '\r'); say "notifications carrying a big picture: $nl"
[ "${nl:-0}" -eq 0 ] && say "PASS 1.4: no big picture (large icon) inside the notifications" || say "FAIL 1.4: a large icon is still inside the notifications"
# ── 1.4: the Holy tone on trades · alerts · prices (channel sound = the app's own raw file) · the 1.3 channels deleted · price kind on its own channel ──
api /api/app/devices '{"act":"test","sample":"price","tag":"PRICE1"}' >/dev/null
got PRICE1 30 && say "PASS price test notification arrived" || say "FAIL price test notification never arrived"
adb shell dumpsys notification --noredact > $OUT/n14.txt
for ch in trade2 alert2 price; do
  line=$(grep -oE "mId='$ch'.{0,700}" $OUT/n14.txt | head -1)
  echo "$line" | grep -q "mSound=android.resource://$P/" && say "PASS channel $ch rings the Holy tone ($(echo "$line" | grep -oE "mSound=[^,]+"))" || say "FAIL channel $ch: no Holy tone — $(echo "$line" | cut -c1-220)"
done
for ch in trade alert; do
  line=$(grep -oE "mId='$ch'.{0,900}" $OUT/n14.txt | head -1)
  if [ -z "$line" ] || echo "$line" | grep -q "mDeleted=true"; then say "PASS old 1.3 channel «$ch» removed"; else say "FAIL old 1.3 channel «$ch» still live — $(echo "$line" | cut -c1-160)"; fi
done
grep -B2 -A30 "PRICE1" $OUT/n14.txt | grep -oE "channel=[a-z0-9]+|mId='[a-z0-9]+'" | head -2 | sed 's/^/HOLYCI price notification: /'
adb shell dumpsys package $P | grep -E "versionName|versionCode" | head -2 | tr -d '\r' | sed 's/^/HOLYCI now: /'
grep -q "android.title=Holy يراقب" $OUT/n13.txt && say "FAIL watcher line still says «Holy يراقب»" || say "PASS watcher line no longer says «يراقب»"
grep -E "mId='watch'" $OUT/n13.txt | head -1 | cut -c1-240 | sed 's/^/HOLYCI watch channel: /'
dump warm >/dev/null                      # the first uiautomator call after «adb root» comes back empty ⇒ warm it up
adb shell am start -n $P/.MainActivity --es go app >/dev/null; sleep 8; dump app13; shot app13
hx=$(python3 ci/ci_tools.py find $OUT/ui_app13.xml "أخفيه")
if [ -n "$hx" ]; then say "PASS panel offers to hide the watcher line"; tap "أخفيه" app13
elif grep -q "أخفيه" $OUT/ui_app13.xml; then say "INFO the 🙈 row is in the page but has no size — this WebView ($(adb shell dumpsys package com.google.android.webview | grep -m1 versionName | tr -d '\r ')) can't lay out the dashboard's windows (CSS inset needs Chrome 87+) ⇒ opening Android's page directly"
  adb shell am start -a android.settings.CHANNEL_NOTIFICATION_SETTINGS --es android.provider.extra.APP_PACKAGE $P --es android.provider.extra.CHANNEL_ID watch >/dev/null
else say "FAIL no hide row in the panel (screen dump: $(grep -c '<node' $OUT/ui_app13.xml 2>/dev/null) nodes) ⇒ opening Android's page directly to still test hiding"
  adb shell am start -a android.settings.CHANNEL_NOTIFICATION_SETTINGS --es android.provider.extra.APP_PACKAGE $P --es android.provider.extra.CHANNEL_ID watch >/dev/null; fi
sleep 4; dump chan; shot chan
adb shell dumpsys activity activities | grep -m1 -E "mResumedActivity|topResumedActivity" | sed 's/^/HOLYCI top: /'
xy=$(python3 ci/ci_tools.py switch $OUT/ui_chan.xml)
if [ -n "$xy" ]; then adb shell input tap $xy; say "turned the watcher line off at $xy"; else say "INFO no switch on the channel page"; fi
sleep 2; shot chan2; adb shell input keyevent 4; sleep 4
adb shell dumpsys notification --noredact > $OUT/n13b.txt
grep -E "mId='watch'" $OUT/n13b.txt | grep -q "mImportance=0" && say "PASS watcher line turned off" || say "FAIL watcher line still on"
say "watcher services with the line off: $(svc)"
note HIDE1; got HIDE1 40 && say "PASS line off ⇒ alerts still arrive" || say "FAIL line off ⇒ no alert"
grep -c "pkg=$P" $OUT/n13b.txt | sed 's/^/HOLYCI our notifications with the line off (before HIDE1): /'
dump app13b; shot app13b
grep -q "مخفي" $OUT/ui_app13b.xml && say "PASS panel shows «مخفي»" || say "FAIL panel doesn't show «مخفي»"
fi
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
# the download + Android's installer screen can take a while on a slow emulator ⇒ look for the installer's button a few times
asked=""
for t in 1 2 3 4 5 6; do
  sleep 8; dump upd2
  for b in "Update" "UPDATE" "Install" "INSTALL"; do if grep -q "text=\"$b\"" $OUT/ui_upd2.xml; then tap "$b" upd2; say "PASS Android installer asked to confirm («$b»)"; asked=1; break; fi; done
  [ -n "$asked" ] && break
done
shot upd2
[ -z "$asked" ] && say "FAIL Android installer screen never showed"
sleep 15
t1=$(adb shell dumpsys package $P | grep -m1 lastUpdateTime | tr -d '\r')
[ "$t0" != "$t1" ] && say "PASS app updated itself ($t0 → $t1)" || say "FAIL app not updated ($t1)"
sleep 5
adb shell dumpsys activity services $P | grep -E "WatchService|isForeground" | head -3 | sed 's/^/HOLYCI after-update svc: /'
pid=$(adb shell pidof $P | tr -d '\r'); say "app pid after update: ${pid:-NONE}"
# ── unlink from the dashboard ⇒ «انفصل» on the phone at once · no silent re-link next time ──
id=$(curl -s -X POST localhost:8099/api/app/devices -H 'Content-Type: application/json' -d '{"act":"list"}' | python3 -c "import sys,json;d=json.load(sys.stdin)['devs'];print(d[0]['id'] if d else '')")
if [ -z "$id" ]; then say "SKIP unlink test — this phone never linked (its system WebView cannot run the page)"; else
  say "unlinking device $id"
  api /api/app/devices "{\"act\":\"del\",\"id\":\"$id\"}" | head -c 100; echo
  sleep 10
  adb shell dumpsys notification --noredact | grep -q "انفصل هذا الموبايل" && say "PASS unlinked phone shows «انفصل» at once" || say "FAIL no unlink notice"
  adb shell am force-stop $P; adb shell am start -n $P/.MainActivity >/dev/null; sleep 15
  n=$(curl -s -X POST localhost:8099/api/app/devices -H 'Content-Type: application/json' -d '{"act":"list"}' | python3 -c "import sys,json;print(len(json.load(sys.stdin)['devs']))")
  [ "$n" = "0" ] && say "PASS no silent re-link after unlink" || say "FAIL re-linked by itself ($n)"
fi
say "crash buffer:"; adb logcat -d -b crash | head -40 | sed 's/^/HOLYCI crash: /'
adb logcat -d | grep -E "holy|Holy|AndroidRuntime|chromium.*CONSOLE|ActivityManager.*$P" | grep -v chatty | tail -70 | sed 's/^/HOLYCI log: /'
pkill -f Holy_Dashboard.pyw || true      # the CI step ends only when nothing it started is still running
say "done"
