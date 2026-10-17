#!/bin/bash
# 📱 Holy APK on a real Android emulator — every result line starts with HOLYCI / HOLYUI / HOLYIMG / HOLYNOTIF
set -u
P=com.holy.dash
OUT=ci_out; mkdir -p $OUT
say(){ echo "HOLYCI $*"; }
# uiautomator can die once (e.g. right after «adb root» restarts adbd) ⇒ an empty screen ⇒ try again
# · it also needs 1 s with no screen change ⇒ «could not get idle state» while live prices tick (that part runs with OKX :8443 paused — see quiet())
dump(){ local e=""; for t in 1 2 3 4 5 6; do rm -f $OUT/ui_$1.xml; adb shell rm -f /sdcard/ui.xml >/dev/null 2>&1
  e=$(adb shell uiautomator dump /sdcard/ui.xml 2>&1 | tr -d '\r' | grep -v "^UI hierchary dumped" | tail -1)
  adb pull /sdcard/ui.xml $OUT/ui_$1.xml >/dev/null 2>&1
  grep -q "<node" $OUT/ui_$1.xml 2>/dev/null && break
  [ "$t" = 1 ] && say "uiautomator ($1): ${e:-no answer} ⇒ retry"
  adb shell 'for p in $(pidof uiautomator); do kill -9 $p; done' >/dev/null 2>&1; sleep 3; done; python3 ci/ci_tools.py texts $OUT/ui_$1.xml "$1"; }
# live OKX prices (wss :8443) change the screen several times a second ⇒ pause them on this runner for the screen-reading part
quiet(){ if [ "$1" = on ]; then sudo iptables -I OUTPUT -p tcp --dport 8443 -j REJECT 2>/dev/null && sudo iptables -I INPUT -p tcp --sport 8443 -j DROP 2>/dev/null && say "INFO live prices (OKX :8443) paused while the screen is read"
  else sudo iptables -D OUTPUT -p tcp --dport 8443 -j REJECT 2>/dev/null; sudo iptables -D INPUT -p tcp --sport 8443 -j DROP 2>/dev/null; say "INFO live prices back"; fi; }
shot(){ adb exec-out screencap -p > $OUT/$1.png 2>/dev/null; python3 ci/ci_tools.py img $OUT/$1.png "$1"; }
tap(){ xy=$(python3 ci/ci_tools.py find $OUT/ui_$2.xml "$1"); if [ -n "$xy" ]; then adb shell input tap $xy; say "tap «$1» at $xy"; else say "tap «$1» NOT FOUND"; fi; }
api(){ curl -s -X POST "localhost:8099$1" -H 'Content-Type: application/json' -d "$2"; echo; }
# a button inside a dashboard window that may sit below the fold: dump ⇒ exact text on screen? tap : scroll the window a bit ⇒ again (never a «contains» guess)
seek(){ local xy=""; for i in 1 2 3 4 5 6 7 8; do dump "$2" >/dev/null; xy=$(python3 ci/ci_tools.py findx $OUT/ui_$2.xml "$1"); [ -n "$xy" ] && break
  adb shell input swipe $((SW/2)) $((SH*7/10)) $((SW/2)) $((SH*35/100)) 500; sleep 1.5; done
  if [ -n "$xy" ]; then adb shell input tap $xy; say "tap «$1» at $xy (after $((i-1)) scrolls)"; return 0; fi; say "tap «$1» NOT FOUND on screen after scrolling"; return 1; }

API=$(adb shell getprop ro.build.version.sdk | tr -d '\r')
ssz=$(adb shell wm size | grep -oE "[0-9]+x[0-9]+" | tail -1); SW=${ssz%x*}; SH=${ssz#*x}
say "android api $API · webview $(adb shell dumpsys package com.google.android.webview 2>/dev/null | grep -m1 versionName | tr -d '\r ')"
adb logcat -c
# ── start from the previous app (1.7 — taken from the v3.27.0 release commit) ⇒ the real update path to 1.8 (📊 indicator alerts on their own channel · 🔐 fingerprint · tone · lock · 120 fps) ──
OLDC=594cb5c4189a2c01437f6b888ad23233ea25bd46
if git fetch -q --depth=1 origin $OLDC 2>/dev/null && git show FETCH_HEAD:Holy_Dashboard.pyw | python3 ci/ci_tools.py apk > old.apk 2>/dev/null && [ -s old.apk ]; then
  adb install old.apk 2>&1 | tail -1 | sed 's/^/HOLYCI install previous: /'
  adb shell dumpsys package $P | grep -m1 versionName | tr -d '\r' | sed 's/^/HOLYCI before update: /'
  adb shell am start -n $P/.MainActivity >/dev/null; sleep 8
  adb shell dumpsys notification --noredact | grep -oE "mId='(trade2|alert2|price|info|watch)'[^}]{0,40}" | sort -u | head -5 | sed 's/^/HOLYCI previous channel: /'
  adb shell am force-stop $P
else say "INFO couldn't fetch the 1.7 app ⇒ fresh install only"; fi
adb install -r holy.apk 2>&1 | tail -1 | sed 's/^/HOLYCI install: /'
adb shell pm list packages | grep -q "$P" && say "PASS installed" || { say "FAIL install"; exit 1; }
adb shell dumpsys package $P | grep -E "versionCode|versionName|targetSdk|signatures|pkgFlags" | head -6 | sed 's/^/HOLYCI pkg: /'
[ "$API" -ge 33 ] && adb shell pm grant $P android.permission.POST_NOTIFICATIONS
adb shell am start -n $P/.MainActivity --es url http://10.0.2.2:8099 >/dev/null
# a slow emulator may still be «Preparing for setup…» ⇒ the launcher stays in front ⇒ wait for the link screen, open the app again if it isn't up
sleep 7; for i in 1 2 3 4 5 6; do dump setup >/dev/null; grep -q "اتصال" $OUT/ui_setup.xml && break
  say "INFO link screen not in front yet (try $i) ⇒ open the app again"; adb shell am start -n $P/.MainActivity --es url http://10.0.2.2:8099 >/dev/null; sleep 6; done
dump setup; shot setup
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
# the channel of the notification carrying tag $1 in dump $2 = the last «channel=» seen before the tag (the record header sits above its extras)
rch(){ awk -v T="$1" 'match($0,/channel=[a-z0-9]+/){c=substr($0,RSTART,RLENGTH)} index($0,T){print c; exit}' "$2" | tr -d '\r'; }
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
# the 1.3 → 1.4 channel clean-up (trade/alert deleted) was proved in the v3.26.7 runs · this run starts from 1.4 ⇒ only OUR app's list counts (other apps have an «alert» channel too)
awk -v P="$P" 'index($0,"AppSettings: " P " "){f=1;next} /AppSettings: /{f=0} f' $OUT/n14.txt > $OUT/n14_ours.txt
if [ -s $OUT/n14_ours.txt ]; then
  say "our channels: $(grep -oE "mId='[a-z0-9]+'" $OUT/n14_ours.txt | sort -u | tr '\n' ' ')"
  for ch in trade alert; do
    line=$(grep -oE "mId='$ch'.{0,900}" $OUT/n14_ours.txt | head -1)
    if [ -z "$line" ] || echo "$line" | grep -q "mDeleted=true"; then say "PASS no live 1.3 channel «$ch» in our app"; else say "FAIL our app still has the 1.3 channel «$ch» — $(echo "$line" | cut -c1-160)"; fi
  done
else say "INFO couldn't cut our app's channel list out of dumpsys (1.3 channels were checked in the v3.26.7 runs)"; fi
say "price notification: $(rch PRICE1 $OUT/n14.txt)"
# ── 1.8: 📊 indicator alerts on their OWN channel «ind» (Holy tone · own group) — apart from 📈 prices (the owner: «تاتيني معا») ──
api /api/app/devices '{"act":"test","sample":"ind","tag":"IND1"}' >/dev/null
got IND1 30 && say "PASS 1.8: indicator test notification arrived" || say "FAIL 1.8: indicator test notification never arrived"
adb shell dumpsys notification --noredact > $OUT/n18.txt
line=$(grep -oE "mId='ind'.{0,700}" $OUT/n18.txt | head -1)
echo "$line" | grep -q "mSound=android.resource://$P/" && say "PASS 1.8: channel ind («📊 تنبيهات المؤشرات») rings the Holy tone" || say "FAIL 1.8: channel ind: no Holy tone — $(echo "$line" | cut -c1-220)"
ich=$(rch IND1 $OUT/n18.txt)
[ "$ich" = "channel=ind" ] && say "PASS 1.8: the indicator alert sits on channel «ind» (not «price»)" || say "FAIL 1.8: indicator alert channel: ${ich:-none}"
pch=$(rch PRICE1 $OUT/n18.txt)
[ "$pch" = "channel=price" ] && say "PASS 1.8: price alerts still on «price»" || say "INFO 1.8: price alert channel now: ${pch:-gone from the shade}"
adb shell dumpsys package $P | grep -E "versionName|versionCode" | head -2 | tr -d '\r' | sed 's/^/HOLYCI now: /'
grep -q "android.title=Holy يراقب" $OUT/n13.txt && say "FAIL watcher line still says «Holy يراقب»" || say "PASS watcher line no longer says «يراقب»"
grep -E "mId='watch'" $OUT/n13.txt | head -1 | cut -c1-240 | sed 's/^/HOLYCI watch channel: /'
quiet on
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
# ── 1.5 🎞️ refresh rate: ⚙️ «الفريمات» ⇒ the window asks the screen for the closest real mode (the emulator has one 60 Hz mode) ──
pf(){ adb shell cat /data/data/$P/shared_prefs/holy.xml 2>/dev/null | tr -d '\r'; }
pf | grep -q "<map" && say "app settings file readable (root)" || say "INFO app settings file not readable here (no root) ⇒ the checks read the screen only"
pf | grep -oE '<(int|boolean) name="(fps|lock)" value="[^"]*"' | sed 's/^/HOLYCI prefs before: /'
adb shell dumpsys window windows | grep -E "com.holy.dash/com.holy.dash.MainActivity" -A40 | grep -oE "preferredDisplayModeId=[0-9]+|preferredRefreshRate=[0-9.]+" | sort -u | head -3 | sed 's/^/HOLYCI window: /'
adb shell dumpsys window windows | grep -E "com.holy.dash/com.holy.dash.MainActivity" -A40 | grep -qE "preferredDisplayModeId=[1-9]|preferredRefreshRate=[1-9]" && say "PASS 1.5: the app window asks the screen for a refresh rate" || say "FAIL 1.5: the app window asks for no refresh rate"
# the dashboard's windows need Chrome 87+ (CSS inset) ⇒ on an older system WebView the ⚙️/📱 rows have no size ⇒ nothing to tap
WVM=$(adb shell dumpsys package com.google.android.webview 2>/dev/null | grep -m1 versionName | grep -oE '[0-9]+' | head -1)
if [ "${WVM:-0}" -lt 87 ]; then say "INFO WebView ${WVM:-?} < 87 ⇒ the ⚙️/📱 windows can't open here ⇒ 🎞️/🔐 taps skipped on this phone (Android 14 runs them)"; else
adb shell am start -n $P/.MainActivity --es go set >/dev/null; sleep 6; dump set15; shot set15
if grep -q "الفريمات" $OUT/ui_set15.xml; then say "PASS ⚙️ «الفريمات» row shown"; grep -oE 'text="[^"]*Hz[^"]*"' $OUT/ui_set15.xml | head -1 | sed 's/^/HOLYCI fps note: /'
  seek "60" set15s; sleep 3
  if pf | grep -q "<map"; then pf | grep -q '<int name="fps" value="60"' && say "PASS 60 saved by the app (HolyApp.setFps)" || say "FAIL fps not saved: $(pf | grep -o 'name="fps"[^/]*')"; fi
  adb shell dumpsys window windows | grep -E "com.holy.dash/com.holy.dash.MainActivity" -A40 | grep -oE "preferredRefreshRate=[0-9.]+" | head -1 | sed 's/^/HOLYCI window after 60: /'
  dump set15b; grep -qE "الشاشة هسه .{0,12}60 Hz" $OUT/ui_set15b.xml && say "PASS row shows the screen at 60 Hz" || say "FAIL row text: $(grep -oE 'text="[^"]*Hz[^"]*"' $OUT/ui_set15b.xml | head -1)"
  seek "120" set15c; sleep 3
  if pf | grep -q "<map"; then pf | grep -q '<int name="fps" value="120"' && say "PASS back to 120 (saved)" || say "FAIL 120 not saved: $(pf | grep -o 'name="fps"[^/]*')"; fi
else say "FAIL «الفريمات» row not on the ⚙️ screen ($(grep -c '<node' $OUT/ui_set15.xml 2>/dev/null) nodes)"; fi
# ── 1.5 🔐 fingerprint lock: a test PIN on the phone ⇒ turn on (asks the PIN) ⇒ 33 s in the background ⇒ locked ⇒ PIN ⇒ open ⇒ turn off ⇒ PIN removed ──
#    (the emulator has no finger ⇒ the system sheet offers the phone's PIN — the same path a phone without a fingerprint takes)
pin(){ sleep 4; adb shell input text 1111; sleep 1; adb shell input keyevent 66; sleep 5; }
locked(){ grep -qE "Holy مقفول|افتح لوحتك" $OUT/ui_$1.xml; }
dashv(){ grep -qE "The Holy Dashboard|v3\.[0-9]+" $OUT/ui_$1.xml; }
adb shell locksettings set-pin 1111 >/dev/null 2>&1 && say "test PIN set" || say "INFO couldn't set a test PIN"
adb shell am start -n $P/.MainActivity --es go app >/dev/null; sleep 7; dump lk1
if grep -q "قفل بالبصمة" $OUT/ui_lk1.xml; then
  say "PASS 📱 panel shows «🔐 قفل بالبصمة»"; seek "تشغيل" lk1s; sleep 3; dump lk1p; shot lk1p
  grep -qE "تأكيد تشغيل القفل|Enter your PIN|Use PIN|Enter PIN" $OUT/ui_lk1p.xml && say "PASS turning it on asks the phone's PIN/fingerprint first" || say "FAIL turning it on didn't ask ($(python3 ci/ci_tools.py texts $OUT/ui_lk1p.xml lk1p | cut -c1-160))"
  pin; dump lk1q
  if pf | grep -q "<map"; then pf | grep -q '<boolean name="lock" value="true"' && say "PASS lock turned ON after the PIN" || say "FAIL lock not on: $(pf | grep -o 'name="lock"[^/]*')"
  else grep -q "شغّال — يطلب البصمة" $OUT/ui_lk1q.xml && say "PASS lock turned ON after the PIN (panel says شغّال)" || say "FAIL lock not on (panel)"; fi
  adb shell input keyevent KEYCODE_HOME; sleep 4
  adb shell am start -n $P/.MainActivity >/dev/null; sleep 5; dump lk2
  if locked lk2; then say "FAIL back within 30 s ⇒ asked again (should open straight away)"; elif dashv lk2; then say "PASS back within 30 s ⇒ open without a new fingerprint"; else say "FAIL back within 30 s ⇒ screen unreadable"; fi
  adb shell input keyevent KEYCODE_HOME; sleep 34
  adb shell am start -n $P/.MainActivity >/dev/null; sleep 5; dump lk3; shot lk3
  locked lk3 && say "PASS back after 34 s ⇒ locked (dashboard covered · asks)" || say "FAIL back after 34 s ⇒ not locked ($(python3 ci/ci_tools.py texts $OUT/ui_lk3.xml lk3 | cut -c1-160))"
  pin; dump lk4; shot lk4
  if grep -q "Holy مقفول" $OUT/ui_lk4.xml; then say "FAIL still locked after the PIN"; elif dashv lk4; then say "PASS PIN ⇒ dashboard open again"; else say "FAIL after the PIN: screen unreadable"; fi
  # ── 1.7 🔐 lock on ⇒ the fingerprint opens the dashboard instead of its password (the password stays the root · the key never printed) ──
  JAR=$OUT/jar.txt; rm -f $JAR
  apic(){ curl -s -b $JAR -c $JAR -X POST "localhost:8099$1" -H 'Content-Type: application/json' -d "$2"; echo; }
  bio_of(){ apic /api/app/devices '{"act":"list"}' | python3 -c "import sys,json;d=json.load(sys.stdin).get('devs') or [{}];print(d[0].get('bio'))" 2>/dev/null; }
  pkey(){ pf | grep -c '<string name="bio">[^<]' | tr -d '\r'; }   # a non-empty key (a refused key is saved as "" ⇒ no key)
  login(){ apic /api/login '{"pw":"1234"}' >/dev/null; }
  askpin(){ grep -qE "Enter your PIN|Use PIN|Enter PIN|افتح لوحتك" $OUT/ui_$1.xml && { say "INFO the PIN sheet is up ($1) ⇒ PIN"; pin; dump $1b >/dev/null; }; }
  dash_restart(){ pkill -f Holy_Dashboard.pyw; sleep 2; (cd /tmp/holy && setsid nohup python3 Holy_Dashboard.pyw >> dash.log 2>&1 < /dev/null &)
    for i in $(seq 1 40); do curl -sf localhost:8099/ >/dev/null && break; sleep 1; done; }
  sleep 3
  [ "$(bio_of)" = "True" ] && say "PASS 1.7: lock on ⇒ the dashboard linked the fingerprint to this phone (📱 list: bio)" || say "FAIL 1.7: no fingerprint link after the lock went on ($(bio_of))"
  pf | grep -q "<map" && { [ "$(pkey)" = "1" ] && say "PASS 1.7: the app holds the fingerprint key (value not shown)" || say "FAIL 1.7: no key in the app settings"; }
  api /api/set_pw '{"new":"1234"}' | head -c 120; echo
  say "dashboard password set ⇒ sessions + fingerprint links reset"
  sleep 16; dump bio1; askpin bio1; sleep 4; dump bio1
  pf | grep -q "<map" && { [ "$(pkey)" = "0" ] && say "PASS 1.7: password changed ⇒ the old key refused (401) ⇒ cleared in the app" || say "FAIL 1.7: the old key is still in the app"; }
  if grep -q "لوحة التحكم محمية" $OUT/ui_bio1.xml; then say "PASS 1.7: …⇒ the password page (type it once)"
    xy=$(python3 ci/ci_tools.py edit $OUT/ui_bio1.xml)
    if [ -n "$xy" ]; then adb shell input tap $xy; sleep 1; adb shell input text 1234; sleep 1; adb shell input keyevent 66; say "typed the password once"; else say "FAIL no password box on the page"; fi
    sleep 14; dump bio2; shot bio2; login
    dashv bio2 && ! grep -q "لوحة التحكم محمية" $OUT/ui_bio2.xml && say "PASS 1.7: password typed ⇒ dashboard open" || say "FAIL 1.7: still not in after the password ($(python3 ci/ci_tools.py texts $OUT/ui_bio2.xml bio2 | cut -c1-160))"
    [ "$(bio_of)" = "True" ] && say "PASS 1.7: …⇒ the dashboard linked the fingerprint again by itself" || say "FAIL 1.7: not linked again ($(bio_of))"
    adb shell input keyevent KEYCODE_HOME; sleep 2
    dash_restart; say "dashboard restarted (every session gone) — the phone in the background"
    sleep 32
    adb shell am start -n $P/.MainActivity >/dev/null; sleep 5; dump bio3; shot bio3
    locked bio3 && say "PASS 1.7: back after 34 s ⇒ locked" || say "INFO 1.7: back after 34 s ⇒ $(python3 ci/ci_tools.py texts $OUT/ui_bio3.xml bio3 | cut -c1-120)"
    pin; sleep 8; dump bio4; askpin bio4; sleep 4; dump bio4; shot bio4
    if grep -q "لوحة التحكم محمية" $OUT/ui_bio4.xml; then say "FAIL 1.7: the password page showed after the PIN (the fingerprint should open it)"
    elif dashv bio4; then say "PASS 1.7: session gone + PIN/fingerprint only ⇒ dashboard open — no password typed"
    else say "FAIL 1.7: after the PIN: $(python3 ci/ci_tools.py texts $OUT/ui_bio4.xml bio4 | cut -c1-160)"; fi
    grep -q "فتح اللوحة بالبصمة انرفض" /tmp/holy/dash.log && say "INFO a refused fingerprint unlock in the log (the stale key — expected once)"
  else say "FAIL 1.7: no password page after the password was set ($(python3 ci/ci_tools.py texts $OUT/ui_bio1.xml bio1 | cut -c1-160))"; fi
  adb shell am start -n $P/.MainActivity --es go app >/dev/null; sleep 6; seek "إطفاء" lk5; pin
  if pf | grep -q "<map"; then pf | grep -q '<boolean name="lock" value="false"' && say "PASS lock turned OFF after the PIN" || say "FAIL lock still on: $(pf | grep -o 'name="lock"[^/]*')"
  else dump lk6; grep -q "مطفي — أي واحد" $OUT/ui_lk6.xml && say "PASS lock turned OFF after the PIN (panel says مطفي)" || say "FAIL lock still on (panel)"; fi
  sleep 4; login
  [ "$(bio_of)" = "False" ] && say "PASS 1.7: lock off ⇒ the fingerprint no longer opens the dashboard (📱 list)" || say "FAIL 1.7: still linked after the lock went off ($(bio_of))"
  pf | grep -q "<map" && { [ "$(pkey)" = "0" ] && say "PASS 1.7: …and the app dropped its key" || say "FAIL 1.7: the app kept its key"; }
  apic /api/set_pw '{"cur":"1234","new":"","disable":true}' | head -c 120; echo
  curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8099/api/app/devices -H 'Content-Type: application/json' -d '{"act":"list"}' | grep -q 200 && say "dashboard password removed again" || say "FAIL the test password is still on"
else say "FAIL 🔐 row not in the 📱 panel ($(grep -c '<node' $OUT/ui_lk1.xml 2>/dev/null) nodes)"; fi
adb shell locksettings clear --old 1111 >/dev/null 2>&1; adb shell locksettings set-disabled true >/dev/null 2>&1; say "test PIN removed"
adb shell input keyevent KEYCODE_WAKEUP; adb shell wm dismiss-keyguard >/dev/null 2>&1
fi
fi
quiet off
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
