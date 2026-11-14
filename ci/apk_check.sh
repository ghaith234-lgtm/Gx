#!/bin/bash
# 📱 Holy APK on a real Android emulator — every result line starts with HOLYCI / HOLYUI / HOLYIMG / HOLYNOTIF
set -u
P=com.holy.dash
OUT=ci_out; mkdir -p $OUT
say(){ echo "HOLYCI $*"; case "$*" in PASS*) echo P >> $OUT/cnt;; FAIL*) echo F >> $OUT/cnt;; esac; }
rm -f $OUT/cnt
# one line at the end with the totals (the log is too big to read whole: screenshots are inlined)
summ(){ echo "HOLYCI SUMMARY $(awk '/^P/{p++} /^F/{f++} END{printf "%d PASS · %d FAIL", p, f}' $OUT/cnt 2>/dev/null)"; }
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
# v3.36.38: the same, for a list row whose text holds more than its title (⚙️ rows: title + value + switch) — «contains», scrolling
seekc(){ local xy=""; for i in 1 2 3 4 5 6 7 8; do dump "$2" >/dev/null; xy=$(python3 ci/ci_tools.py find $OUT/ui_$2.xml "$1"); [ -n "$xy" ] && break
  adb shell input swipe $((SW/2)) $((SH*7/10)) $((SW/2)) $((SH*35/100)) 500; sleep 1.5; done
  if [ -n "$xy" ]; then adb shell input tap $xy; say "tap «$1» at $xy (after $((i-1)) scrolls)"; return 0; fi; say "tap «$1» NOT FOUND on screen after scrolling"; return 1; }

API=$(adb shell getprop ro.build.version.sdk | tr -d '\r')
ssz=$(adb shell wm size | grep -oE "[0-9]+x[0-9]+" | tail -1); SW=${ssz%x*}; SH=${ssz#*x}
say "android api $API · webview $(adb shell dumpsys package com.google.android.webview 2>/dev/null | grep -m1 versionName | tr -d '\r ')"
adb logcat -c
# ── 2.0: start from the previous app 1.9 (the OLD signing key — taken from the v3.36.31 release) ⇒ the owner's one-time move to 2.0 (a new key):
#    Android refuses 2.0 over 1.9 · the dashboard offers 1.9 no update · inside 1.9 the 📱 panel opens by itself with «⬇️ احفظها» ⇒ the very 2.0
#    file lands in Downloads/Holy · 1.9 removed · THAT saved file installed · the old phone unlinked (step 4 of the panel) ──
OLDC=5f434fa97e2701c379569074bd1e67fdc276f228
NEWSHA=$(sha256sum holy.apk | cut -d' ' -f1); INST=holy.apk
# v3.36.38: the app's version from android/version.json (2.1 · 12 …) — the move from 1.x is the same for every version after 2.0
NV=$(python3 -c "import json;print(json.load(open('android/version.json'))['name'])"); NC=$(python3 -c "import json;print(json.load(open('android/version.json'))['code'])")
devs(){ curl -s -X POST localhost:8099/api/app/devices -H 'Content-Type: application/json' -d '{"act":"list"}' | python3 -c "import sys,json;print(' '.join(d['id'] for d in json.load(sys.stdin)['devs']))"; }
if git fetch -q --depth=1 origin $OLDC 2>/dev/null && git show FETCH_HEAD:Holy_Dashboard.pyw | python3 ci/ci_tools.py apk > old.apk 2>/dev/null && [ -s old.apk ]; then
  adb install old.apk 2>&1 | tail -1 | sed 's/^/HOLYCI install previous: /'
  adb shell dumpsys package $P | grep -m1 versionName | tr -d '\r' | sed 's/^/HOLYCI before the move: /'
  r=$(adb install -r holy.apk 2>&1 | tr -d '\r' | grep -m1 -oE "Success|Failure.*|INSTALL_[A-Z_]+.*")   # (run 89: the last line was empty on Android 9)
  echo "$r" | grep -q "UPDATE_INCOMPATIBLE" && say "PASS 2.0: Android refuses 2.0 over 1.9 (a new signing key) ⇒ the move is manual, once" || say "INFO 2.0 over 1.9: $r"
  ci=$(curl -s localhost:8099/api/app/info -A "HolyApp/1.9" | python3 -c "import sys,json;print(json.load(sys.stdin)['apk']['code'])")
  cn=$(curl -s localhost:8099/api/app/info -A "HolyApp/$NV" | python3 -c "import sys,json;print(json.load(sys.stdin)['apk']['code'])")
  [ "$ci" = 0 ] && [ "$cn" = "$NC" ] && say "PASS 2.0: /api/app/info offers 1.9 no update (code $ci) · $NV sees code $cn" || say "FAIL 2.0: /api/app/info — 1.9 gets $ci · 2.0 gets $cn"
  [ "$API" -ge 33 ] && adb shell pm grant $P android.permission.POST_NOTIFICATIONS
  [ "$API" -le 28 ] && adb shell pm grant $P android.permission.WRITE_EXTERNAL_STORAGE      # saving into Downloads on Android 9 (the app asks; granted here ahead)
  adb shell am start -n $P/.MainActivity --es url http://10.0.2.2:8099 >/dev/null
  sleep 7; for i in 1 2 3 4 5 6; do dump old0 >/dev/null; grep -q "اتصال" $OUT/ui_old0.xml && break
    adb shell am start -n $P/.MainActivity --es url http://10.0.2.2:8099 >/dev/null; sleep 6; done
  tap "اتصال" old0
  mv=""; for i in $(seq 1 10); do sleep 4; dump old1 >/dev/null; grep -q "الانتقال إلى Holy" $OUT/ui_old1.xml && { mv=1; break; }
    grep -q "بعدين" $OUT/ui_old1.xml && tap "بعدين" old1
    # run 103: 1.9's own «بعدين» dialog came early and the app ended up behind the home screen ⇒ open it again (the panel opens by itself inside it)
    grep -q 'package="'$P'"' $OUT/ui_old1.xml || { adb shell am start -n $P/.MainActivity >/dev/null; say "INFO 1.9 was behind the home screen — opened it again"; }; done
  shot old1
  WV0=$(adb shell dumpsys package com.google.android.webview 2>/dev/null | grep -m1 versionName | grep -oE '[0-9]+' | head -1)
  if [ -n "$mv" ]; then say "PASS 2.0: inside 1.9 the 📱 panel opened by itself with «الانتقال إلى Holy 2.0 — مرة واحدة»"
    if seek "⬇️ احفظها" old2; then
      got=""; for i in $(seq 1 20); do sleep 1; adb pull /sdcard/Download/Holy/Holy-$NV.apk moved.apk >/dev/null 2>&1 && [ -s moved.apk ] && { got=1; break; }; done
      if [ -n "$got" ] && [ "$(sha256sum moved.apk | cut -d' ' -f1)" = "$NEWSHA" ]; then say "PASS 2.0: «⬇️ احفظها» saved Downloads/Holy/Holy-$NV.apk = the dashboard's $NV (sha256)"; INST=moved.apk
      else say "FAIL 2.0: «⬇️ احفظها» — no Holy-$NV.apk in Downloads/Holy, or not the same file ($(adb shell ls /sdcard/Download/Holy 2>&1 | tr -d '\r' | tr '\n' ' '))"; fi
      dump old3 >/dev/null; shot old3
    elif [ "${WV0:-0}" -lt 87 ]; then say "INFO 2.0: this WebView (${WV0:-?}) lays the panel's buttons out with no size ⇒ «⬇️ احفظها» not tapped here (Android 14 runs it)"
    else say "FAIL 2.0: «⬇️ احفظها» not found in the 1.9 panel ($(python3 ci/ci_tools.py texts $OUT/ui_old2.xml old2 | grep -o '.\{0,40\}احفظها.\{0,10\}' | head -2 | tr '\n' ' '))"
    fi
  elif ! timeout 15 adb get-state >/dev/null 2>&1; then say "FAIL 2.0: the emulator stopped answering during the 1.9 phase (adb: no device — run 90, Android 11, lost it right after «اتصال»)"
  elif [ "${WV0:-0}" -lt 87 ]; then say "INFO 2.0: this system WebView (${WV0:-?}) can't open the dashboard's windows ⇒ the 1.9 panel isn't checked here (Android 11/14 run it)"
  else say "FAIL 2.0: inside 1.9 the move panel never opened ($(python3 ci/ci_tools.py texts $OUT/ui_old1.xml old1 | cut -c1-200))"; fi
  old=$(devs); adb uninstall $P 2>&1 | tail -1 | sed 's/^/HOLYCI 1.9 removed: /'
  for id in $old; do api /api/app/devices "{\"act\":\"del\",\"id\":\"$id\"}" >/dev/null; done
  [ -n "$old" ] && say "INFO the 1.9 phone ($old) unlinked from the dashboard (the panel's step 4)"
else say "INFO couldn't fetch the 1.9 app ⇒ fresh install only"; fi
adb install -r $INST 2>&1 | tail -1 | sed "s/^/HOLYCI install ($INST): /"
adb shell pm list packages | grep -q "$P" && say "PASS installed" || { say "FAIL install"; exit 1; }
adb shell dumpsys package $P | grep -E "versionCode|versionName|targetSdk|signatures|pkgFlags" | head -6 | sed 's/^/HOLYCI pkg: /'
[ "$API" -ge 33 ] && adb shell pm grant $P android.permission.POST_NOTIFICATIONS
adb shell am start -n $P/.MainActivity --es url http://10.0.2.2:8099 >/dev/null
# a slow emulator may still be «Preparing for setup…» ⇒ the launcher stays in front ⇒ wait for the link screen, open the app again if it isn't up
sleep 7; for i in 1 2 3 4 5 6; do dump setup >/dev/null; grep -q "اتصال" $OUT/ui_setup.xml && break
  say "INFO link screen not in front yet (try $i) ⇒ open the app again"; adb shell am start -n $P/.MainActivity --es url http://10.0.2.2:8099 >/dev/null; sleep 6; done
dump setup; shot setup
# 1.9 📱 Android lists the home-screen widget (⇒ «Holy» in the launcher's widget list) — every phone, linked or not · after the first start (a never-opened app is «stopped» on Android 9) · min = raw dp units (250dp = 64001)
WCMP="$P/$P.HolyWidget"
adb shell dumpsys appwidget > $OUT/aw0.txt
grep -q "cmp:ComponentInfo{$WCMP}" $OUT/aw0.txt && say "PASS 1.9: Android lists the Holy widget ($(grep -A3 "cmp:ComponentInfo{$WCMP}" $OUT/aw0.txt | grep -m2 -oE "min=\([^)]*\)|updatePeriodMillis=[0-9]+" | tr '\n' ' '))" || say "FAIL 1.9: Android doesn't list the Holy widget"
tap "اتصال" setup
sleep 18; dump dash1
if grep -q "متصفح النظام قديم" $OUT/ui_dash1.xml; then say "PASS old system WebView ⇒ the app asks to update it"; tap "لاحقاً" dash1; sleep 2; dump dash1; fi
if grep -q "لاحقاً" $OUT/ui_dash1.xml; then say "PASS battery dialog shown after linking"; tap "لاحقاً" dash1; sleep 2; fi   # 2.2: «بعدين» ⇒ «لاحقاً» (MSA)
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
# ── 1.9 📱 the home-screen widget (1): /api/app/widget answers this phone's key only (Android listing it is checked right after the install) ──
tok=$(adb shell cat /data/data/$P/shared_prefs/holy.xml 2>/dev/null | tr -d '\r' | grep -oE '<string name="token">[^<]+' | sed 's/.*>//')   # the phone's key — used, never printed
if [ -n "$tok" ]; then
  c1=$(curl -s -o $OUT/wd.json -w "%{http_code}" localhost:8099/api/app/widget -H "X-Holy-Device: $tok"); c0=$(curl -s -o /dev/null -w "%{http_code}" localhost:8099/api/app/widget)
  cw=$(curl -s -o /dev/null -w "%{http_code}" localhost:8099/api/app/widget -H "X-Holy-Device: ${tok}x")
  [ "$c1" = 200 ] && [ "$c0" = 401 ] && [ "$cw" = 401 ] && say "PASS 1.9: /api/app/widget — this phone's key ⇒ 200 · no key / a wrong key ⇒ 401 · $(python3 -c "import json;j=json.load(open('$OUT/wd.json'));print(j['run'],'/',j['n'],'running ·',' · '.join(k[0]+' '+k[1] for k in j['k']))")" \
    || say "FAIL 1.9: /api/app/widget — key $c1 · none $c0 · wrong $cw"
else say "INFO 1.9: the phone's key isn't readable here (no root) ⇒ the widget's own fetch is checked on the home screen"; fi
unset tok
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
# v3.36.39: a phone that never chose starts at 60 (the dashboard asks the app once — the owner: «60 ⇒ no stutter»)
if pf | grep -q "<map"; then pf | grep -q '<int name="fps" value="60"' && say "PASS never chosen ⇒ the app starts at 60 (asked once by the dashboard)" || say "FAIL never chosen ⇒ not 60: $(pf | grep -o 'name="fps"[^/]*')"; fi
adb shell dumpsys window windows | grep -E "com.holy.dash/com.holy.dash.MainActivity" -A40 | grep -oE "preferredDisplayModeId=[0-9]+|preferredRefreshRate=[0-9.]+" | sort -u | head -3 | sed 's/^/HOLYCI window: /'
adb shell dumpsys window windows | grep -E "com.holy.dash/com.holy.dash.MainActivity" -A40 | grep -qE "preferredDisplayModeId=[1-9]|preferredRefreshRate=[1-9]" && say "PASS 1.5: the app window asks the screen for a refresh rate" || say "FAIL 1.5: the app window asks for no refresh rate"
# the dashboard's windows need Chrome 87+ (CSS inset) ⇒ on an older system WebView the ⚙️/📱 rows have no size ⇒ nothing to tap
WVM=$(adb shell dumpsys package com.google.android.webview 2>/dev/null | grep -m1 versionName | grep -oE '[0-9]+' | head -1)
if [ "${WVM:-0}" -lt 87 ]; then say "INFO WebView ${WVM:-?} < 87 ⇒ the ⚙️/📱 windows can't open here ⇒ 🎞️/🔐 taps skipped on this phone (Android 14 runs them)"; else
adb shell am start -n $P/.MainActivity --es go set >/dev/null; sleep 6; dump set15; shot set15
if grep -q "الفريمات" $OUT/ui_set15.xml; then say "PASS ⚙️ «الفريمات» row shown"
  # v3.36.35: ⚙️ is a list — the «الفريمات» row opens its choices on a tap
  seekc "الفريمات" set15r; sleep 2; dump set15o >/dev/null; shot set15o   # v3.36.38: more rows above it ⇒ scroll to it
  grep -oE 'text="[^"]*Hz[^"]*"' $OUT/ui_set15o.xml | head -1 | sed 's/^/HOLYCI fps note: /'
  seek "60" set15s; sleep 3
  if pf | grep -q "<map"; then pf | grep -q '<int name="fps" value="60"' && say "PASS 60 saved by the app (HolyApp.setFps)" || say "FAIL fps not saved: $(pf | grep -o 'name="fps"[^/]*')"; fi
  adb shell dumpsys window windows | grep -E "com.holy.dash/com.holy.dash.MainActivity" -A40 | grep -oE "preferredRefreshRate=[0-9.]+" | head -1 | sed 's/^/HOLYCI window after 60: /'
  dump set15b; grep -qE "الشاشة (هسه|الآن) .{0,12}60 Hz" $OUT/ui_set15b.xml && say "PASS row shows the screen at 60 Hz" || say "FAIL row text: $(grep -oE 'text="[^"]*Hz[^"]*"' $OUT/ui_set15b.xml | head -1)"
  seek "120" set15c; sleep 3
  if pf | grep -q "<map"; then pf | grep -q '<int name="fps" value="120"' && say "PASS back to 120 (saved)" || say "FAIL 120 not saved: $(pf | grep -o 'name="fps"[^/]*')"; fi
else say "FAIL «الفريمات» row not on the ⚙️ screen ($(grep -c '<node' $OUT/ui_set15.xml 2>/dev/null) nodes)"; fi
# ── 2.1 📲 the phone's buttons (back · home): ⚙️ 📱 «أزرار الهاتف» ⇒ shown (the app keeps them, the page sits above them) · again ⇒ hidden ──
nb(){ adb shell dumpsys window 2>/dev/null | tr -d '\r' | grep -ciE "navigationBars.*visible=true|type=ITYPE_NAVIGATION_BAR.*mVisible=true|NavigationBar.*isVisible=true|navigationBars mVisible=true"; }
adb shell am start -n $P/.MainActivity --es go set >/dev/null; sleep 5; nb0=$(nb)
xy=""; for i in 1 2 3 4 5 6 7 8 9 10; do dump nav0 >/dev/null; xy=$(python3 ci/ci_tools.py find $OUT/ui_nav0.xml "أزرار الهاتف"); [ -n "$xy" ] && break
  adb shell input swipe $((SW/2)) $((SH*7/10)) $((SW/2)) $((SH*35/100)) 500; sleep 1.2; done
if [ -n "$xy" ]; then say "PASS 2.1: ⚙️ 📱 shows «أزرار الهاتف»"; adb shell input tap $xy; sleep 3; shot nav1; nb1=$(nb)
  if pf | grep -q "<map"; then pf | grep -q '<boolean name="nav_bar" value="true"' && say "PASS 2.1: «أزرار الهاتف» on ⇒ kept by the app (nav_bar = true)" || say "FAIL 2.1: nav_bar not saved: $(pf | grep -o 'name=\"nav_bar\"[^/]*')"; fi
  say "INFO 2.1: the system's navigation-bar lines that say «visible» — before $nb0 · after showing $nb1"
  dump nav1 >/dev/null; xy=$(python3 ci/ci_tools.py find $OUT/ui_nav1.xml "أزرار الهاتف"); [ -n "$xy" ] && adb shell input tap $xy; sleep 3; shot nav2
  if pf | grep -q "<map"; then pf | grep -q '<boolean name="nav_bar" value="false"' && say "PASS 2.1: again ⇒ hidden (nav_bar = false)" || say "FAIL 2.1: nav_bar not false after the second tap"; fi
else say "FAIL 2.1: no «أزرار الهاتف» row in ⚙️ ($(python3 ci/ci_tools.py texts $OUT/ui_nav0.xml nav0 | grep -o '.\{0,40\}التطبيقات.\{0,60\}' | head -1))"; fi
# ── 1.9 📱 the home-screen widget (2): ⚙️ 📱 «📌 أضفه» ⇒ Android's own «add» sheet ⇒ placed · it fetches with the phone's key and draws · a tap opens Holy ──
WX=""; WY=""
adb shell am start -n $P/.MainActivity --es go app >/dev/null; sleep 7; dump wd0
if grep -q "ويدجت الشاشة الرئيسية" $OUT/ui_wd0.xml; then say "PASS 1.9: 📱 panel shows «🧩 ويدجت الشاشة الرئيسية»"; else say "FAIL 1.9: no widget row in the 📱 panel"; fi
if seek "📌 أضفه" wd1; then
  sleep 4; dump wd2; shot wd2; asked=""
  for b in "Add automatically" "ADD AUTOMATICALLY" "Add to home screen" "ADD TO HOME SCREEN" "Add" "ADD"; do
    xy=$(python3 ci/ci_tools.py findb $OUT/ui_wd2.xml "$b"); [ -n "$xy" ] && { adb shell input tap $xy; say "PASS 1.9: Android's own «add widget» sheet ⇒ tap «$b»"; asked=1; break; }; done
  [ -z "$asked" ] && say "FAIL 1.9: no «add widget» sheet from the home screen ($(python3 ci/ci_tools.py texts $OUT/ui_wd2.xml wd2 | cut -c1-200))"
  sleep 6
fi
nw=$(adb shell dumpsys appwidget | tr -d '\r' | grep -c "provider=ProviderId{.*cmp:ComponentInfo{$WCMP}")
[ "${nw:-0}" -ge 1 ] && say "PASS 1.9: the widget is on the home screen ($nw)" || say "FAIL 1.9: no Holy widget placed"
if [ "${nw:-0}" -ge 1 ]; then
  sleep 4; dump wd3
  grep -q "مضاف إلى الشاشة الرئيسية" $OUT/ui_wd3.xml && say "PASS 1.9: the panel now says «مضاف إلى الشاشة الرئيسية ✓»" || say "INFO 1.9: panel text after adding: $(python3 ci/ci_tools.py texts $OUT/ui_wd3.xml wd3 | grep -oE 'ويدجت[^|]{0,90}' | head -1)"
  adb shell input keyevent KEYCODE_HOME; sleep 10
  wj=$(adb shell cat /data/data/$P/shared_prefs/holy_widget.xml 2>/dev/null | tr -d '\r')
  if [ -n "$wj" ]; then echo "$wj" | grep -qE '&quot;ok&quot;: ?true' && say "PASS 1.9: the widget fetched /api/app/widget with the phone's key (its last answer kept for no-connection)" || say "FAIL 1.9: the widget has no answer saved"; fi
  if [ -n "$wj" ]; then echo "$wj" | grep -q '&quot;kb&quot;' && say "PASS 2.0: the widget's answer carries the six numbers «kb» (today · yesterday · 7 days · 30 days · month · total)" || say "FAIL 2.0: no «kb» in the widget's answer"; fi
  dump wd4; shot wd4
  wd=$(python3 ci/ci_tools.py desc $OUT/ui_wd4.xml "Holy —")
  for pg in 2 3; do      # the launcher puts a new widget where there is room — not always the first home page (run 71, Android 14)
    [ -n "$wd" ] && break
    sz=$(adb shell wm size | tr -d '\r' | grep -oE '[0-9]+x[0-9]+' | tail -1); SW=${sz%x*}; SH=${sz#*x}
    adb shell input swipe $((SW*85/100)) $((SH/2)) $((SW*15/100)) $((SH/2)) 300; sleep 3
    dump wd4; shot wd4; wd=$(python3 ci/ci_tools.py desc $OUT/ui_wd4.xml "Holy —")
    [ -n "$wd" ] && say "INFO 1.9: the launcher put the widget on home page $pg"
  done
  if [ -n "$wd" ]; then
    set -- $wd; WX=$1; WY=$2; python3 ci/ci_tools.py imgc $OUT/wd4.png widget $3 $4 $5 $6
    say "PASS 1.9: the widget on the home screen ($3,$4–$5,$6) reads «${wd#* * * * * * }»"
    adb shell input tap $WX $WY; sleep 5
    adb shell dumpsys activity activities | grep -m1 -E "mResumedActivity|topResumedActivity" | grep -q "$P/.MainActivity" && say "PASS 1.9: a tap on the widget opens Holy" || say "FAIL 1.9: a tap on the widget didn't open Holy ($(adb shell dumpsys activity activities | grep -m1 -E 'mResumedActivity|topResumedActivity' | tr -d '\r'))"
  else say "FAIL 1.9: the widget isn't on home pages 1–3 / has no summary ($(python3 ci/ci_tools.py texts $OUT/ui_wd4.xml wd4 | cut -c1-200))"; fi
fi
# ── 1.5 🔐 fingerprint lock: a test PIN on the phone ⇒ turn on (asks the PIN) ⇒ 33 s in the background ⇒ locked ⇒ PIN ⇒ open ⇒ turn off ⇒ PIN removed ──
#    (the emulator has no finger ⇒ the system sheet offers the phone's PIN — the same path a phone without a fingerprint takes)
pin(){ sleep 4; adb shell input text 1111; sleep 1; adb shell input keyevent 66; sleep 5; }
locked(){ grep -qE "Holy (مقفول|مقفل)|افتح لوحتك" $OUT/ui_$1.xml; }
dashv(){ grep -qE "The Holy Dashboard|v3\.[0-9]+" $OUT/ui_$1.xml; }
adb shell locksettings set-pin 1111 >/dev/null 2>&1 && say "test PIN set" || say "INFO couldn't set a test PIN"
adb shell am start -n $P/.MainActivity --es go app >/dev/null; sleep 7; dump lk1
if grep -q "قفل بالبصمة" $OUT/ui_lk1.xml; then
  say "PASS 📱 panel shows «🔐 قفل بالبصمة»"; seek "تشغيل" lk1s; sleep 3; dump lk1p; shot lk1p
  grep -qE "تأكيد تشغيل القفل|Enter your PIN|Use PIN|Enter PIN" $OUT/ui_lk1p.xml && say "PASS turning it on asks the phone's PIN/fingerprint first" || say "FAIL turning it on didn't ask ($(python3 ci/ci_tools.py texts $OUT/ui_lk1p.xml lk1p | cut -c1-160))"
  pin; dump lk1q
  if pf | grep -q "<map"; then pf | grep -q '<boolean name="lock" value="true"' && say "PASS lock turned ON after the PIN" || say "FAIL lock not on: $(pf | grep -o 'name="lock"[^/]*')"
  else grep -qE "(شغّال|مفعّل) — يطلب البصمة" $OUT/ui_lk1q.xml && say "PASS lock turned ON after the PIN (panel says شغّال)" || say "FAIL lock not on (panel)"; fi
  adb shell input keyevent KEYCODE_HOME; sleep 4
  adb shell am start -n $P/.MainActivity >/dev/null; sleep 5; dump lk2
  if locked lk2; then say "FAIL back within 30 s ⇒ asked again (should open straight away)"; elif dashv lk2; then say "PASS back within 30 s ⇒ open without a new fingerprint"; else say "FAIL back within 30 s ⇒ screen unreadable"; fi
  adb shell input keyevent KEYCODE_HOME; sleep 34
  adb shell am start -n $P/.MainActivity >/dev/null; sleep 5; dump lk3; shot lk3
  locked lk3 && say "PASS back after 34 s ⇒ locked (dashboard covered · asks)" || say "FAIL back after 34 s ⇒ not locked ($(python3 ci/ci_tools.py texts $OUT/ui_lk3.xml lk3 | cut -c1-160))"
  pin; dump lk4; shot lk4
  if grep -qE "Holy (مقفول|مقفل)" $OUT/ui_lk4.xml; then say "FAIL still locked after the PIN"; elif dashv lk4; then say "PASS PIN ⇒ dashboard open again"; else say "FAIL after the PIN: screen unreadable"; fi
  # 1.9: the widget is a door, not a key — after 34 s away a tap on it lands on the lock first
  if [ -n "$WX" ]; then
    adb shell input keyevent KEYCODE_HOME; sleep 34; adb shell input tap $WX $WY; sleep 5; dump lkw; shot lkw
    locked lkw && say "PASS 1.9: the lock on ⇒ a tap on the widget after 34 s asks for the fingerprint/PIN first" || say "FAIL 1.9: the widget opened Holy past the lock ($(python3 ci/ci_tools.py texts $OUT/ui_lkw.xml lkw | cut -c1-160))"
    pin; dump lkw2; dashv lkw2 && say "PASS 1.9: …PIN ⇒ dashboard open" || say "INFO 1.9: after the PIN: $(python3 ci/ci_tools.py texts $OUT/ui_lkw2.xml lkw2 | cut -c1-120)"
  fi
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
    grep -qE "فتح اللوحة بالبصمة انرفض|رُفض فتح اللوحة بالبصمة" /tmp/holy/dash.log && say "INFO a refused fingerprint unlock in the log (the stale key — expected once)"
  else say "FAIL 1.7: no password page after the password was set ($(python3 ci/ci_tools.py texts $OUT/ui_bio1.xml bio1 | cut -c1-160))"; fi
  adb shell am start -n $P/.MainActivity --es go app >/dev/null; sleep 6; seek "إطفاء" lk5; pin
  if pf | grep -q "<map"; then pf | grep -q '<boolean name="lock" value="false"' && say "PASS lock turned OFF after the PIN" || say "FAIL lock still on: $(pf | grep -o 'name="lock"[^/]*')"
  else dump lk6; grep -qE "مطفي — أي واحد|متوقف — أي شخص" $OUT/ui_lk6.xml && say "PASS lock turned OFF after the PIN (panel says مطفي)" || say "FAIL lock still on (panel)"; fi
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
# a slow emulator can take 20+ s to finish installing after the tap (run 69, Android 9: tap 14:21:55 · installed 14:22:18) ⇒ wait for it, up to 60 s
# run 73 (Android 9 + 14): adb lost the emulator during the install ("error: closed") ⇒ t1 came back EMPTY, which differs from t0 and read as
#   a pass, and every later adb call waited for the device until the job's 45 min limit ⇒ an empty answer is not a pass · bounded waits ·
#   one reconnect try · if the emulator is still gone, the later checks are skipped with a FAIL (the job ends instead of hanging)
t1="$t0"; for i in $(seq 1 12); do sleep 5; t1=$(timeout 30 adb shell dumpsys package $P | grep -m1 lastUpdateTime | tr -d '\r'); [ -n "$t1" ] && [ "$t0" != "$t1" ] && break; done
if [ -n "$t1" ] && [ "$t0" != "$t1" ]; then say "PASS app updated itself ($t0 → $t1 · ~$((i*5)) s after the tap)"
elif [ -z "$t1" ]; then say "FAIL adb got no answer while the update installed (emulator connection lost)"
else say "FAIL app not updated ($t1)"; fi
LOST=""
if ! timeout 15 adb get-state >/dev/null 2>&1; then
  say "emulator not answering after the update — reconnecting"; adb reconnect >/dev/null 2>&1; sleep 5
  timeout 120 adb wait-for-device || LOST=1
fi
if [ -n "$LOST" ]; then
  say "FAIL emulator gone after the update (adb: device not found) — unlink and log checks skipped"
  pkill -f Holy_Dashboard.pyw || true
  summ; say "done"; exit 0
fi
sleep 5
adb shell dumpsys activity services $P | grep -E "WatchService|isForeground" | head -3 | sed 's/^/HOLYCI after-update svc: /'
pid=$(adb shell pidof $P | tr -d '\r'); say "app pid after update: ${pid:-NONE}"
# ── unlink from the dashboard ⇒ «انفصل» on the phone at once · no silent re-link next time ──
id=$(curl -s -X POST localhost:8099/api/app/devices -H 'Content-Type: application/json' -d '{"act":"list"}' | python3 -c "import sys,json;d=json.load(sys.stdin)['devs'];print(d[0]['id'] if d else '')")
if [ -z "$id" ]; then say "SKIP unlink test — this phone never linked (its system WebView cannot run the page)"; else
  say "unlinking device $id"
  api /api/app/devices "{\"act\":\"del\",\"id\":\"$id\"}" | head -c 100; echo
  sleep 10
  adb shell dumpsys notification --noredact | grep -qE "انفصل هذا الموبايل|فُصل هذا الهاتف" && say "PASS unlinked phone shows «انفصل» at once" || say "FAIL no unlink notice"
  adb shell am force-stop $P; adb shell am start -n $P/.MainActivity >/dev/null; sleep 15
  n=$(curl -s -X POST localhost:8099/api/app/devices -H 'Content-Type: application/json' -d '{"act":"list"}' | python3 -c "import sys,json;print(len(json.load(sys.stdin)['devs']))")
  [ "$n" = "0" ] && say "PASS no silent re-link after unlink" || say "FAIL re-linked by itself ($n)"
fi
say "crash buffer:"; timeout 60 adb logcat -d -b crash | head -40 | sed 's/^/HOLYCI crash: /'
timeout 60 adb logcat -d | grep -E "holy|Holy|AndroidRuntime|chromium.*CONSOLE|ActivityManager.*$P" | grep -v chatty | tail -70 | sed 's/^/HOLYCI log: /'
pkill -f Holy_Dashboard.pyw || true      # the CI step ends only when nothing it started is still running
summ
say "done"
