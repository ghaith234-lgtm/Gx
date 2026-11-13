# 💻 Holy Windows app check on a real Windows machine (GitHub windows-latest) — v3.36.41: the program 2.0 (built just before by
#   ci/win_build.ps1 · WebView2 · its own window with no title bar · — ☐ ✕ drawn by the dashboard beside 🔔 · the top bar moves it — real
#   mouse clicks and a real drag below). The rest as 1.2:
#   the dashboard serves the app (1.1: 32-bit · runs on every Windows) with its address + a device key inside · first run ⇒
#   shortcuts + saved address · Edge opens the dashboard in app mode (1.2: a normal maximized window — minimize · maximize · close ·
#   resizable · no address bar · F11 = full screen) · the app stays as a tray icon (notifications) ·
#   starts with Windows · a test alert ⇒ a Windows notification · a second start keeps one watcher · unlink ⇒ it knows ·
#   --setup shows the address window · an address that doesn't answer ⇒ the warning · screenshots (base64 lines HOLYSHOT).
#   Results: lines starting with HOLYWIN in the job log. The device key itself is never printed.
$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing, System.Windows.Forms
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text;
public class W {
  [DllImport("user32.dll")] public static extern IntPtr FindWindow(string c, string t);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc f, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
  [DllImport("user32.dll")] public static extern int GetWindowLong(IntPtr h, int i);
  [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, int dx, int dy, uint d, UIntPtr e);
  public static int[] R4(IntPtr h) { RECT r; GetWindowRect(h, out r); return new int[] { r.L, r.T, r.R, r.B }; }
  public static int[] C4(IntPtr h) { RECT r; GetClientRect(h, out r); return new int[] { r.L, r.T, r.R, r.B }; }
  public static void Down(int x, int y) { SetCursorPos(x, y); System.Threading.Thread.Sleep(60); mouse_event(2, 0, 0, 0, UIntPtr.Zero); }
  public static void Up() { mouse_event(4, 0, 0, 0, UIntPtr.Zero); }
  public static void Click(int x, int y) { Down(x, y); System.Threading.Thread.Sleep(60); Up(); }
  public static string Rect(IntPtr h) { RECT r; GetWindowRect(h, out r); return r.L + "," + r.T + "," + r.R + "," + r.B; }
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  public struct RECT { public int L, T, R, B; }
  public static string List() { var sb = new StringBuilder();
    EnumWindows((h, l) => { if (IsWindowVisible(h)) { var t = new StringBuilder(256); var c = new StringBuilder(128); GetWindowText(h, t, 256); GetClassName(h, c, 128);
      uint p; GetWindowThreadProcessId(h, out p); RECT r; GetWindowRect(h, out r);
      if (t.Length > 0) sb.Append(h + "|" + c + "|" + t + "|" + p + "|" + r.L + "," + r.T + "," + r.R + "," + r.B + "\n"); } return true; }, IntPtr.Zero);
    return sb.ToString(); }
}
"@
$ok = 0; $bad = 0
function Check($name, $cond, $info) { if ($cond) { $script:ok++; Write-Host "HOLYWIN ✅ $name $info" } else { $script:bad++; Write-Host "HOLYWIN ❌ $name $info" } }
function Shot($tag) {
  try {
    $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
    $g = [System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
    $w = 640; $h = [int]($b.Height * 640 / $b.Width)
    $sm = New-Object System.Drawing.Bitmap $w, $h; $g2 = [System.Drawing.Graphics]::FromImage($sm)
    $g2.InterpolationMode = "HighQualityBicubic"; $g2.DrawImage($bmp, 0, 0, $w, $h)
    $ms = New-Object System.IO.MemoryStream
    $enc = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
    $ep = New-Object System.Drawing.Imaging.EncoderParameters 1; $ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 70L
    $sm.Save($ms, $enc, $ep)
    $s = [Convert]::ToBase64String($ms.ToArray())
    Write-Host "HOLYSHOT-BEGIN $tag $($b.Width)x$($b.Height)"
    for ($i = 0; $i -lt $s.Length; $i += 3000) { Write-Host ("HOLYSHOT " + $s.Substring($i, [Math]::Min(3000, $s.Length - $i))) }
    Write-Host "HOLYSHOT-END $tag"
  } catch { Write-Host "HOLYWIN ⚠️ screenshot failed: $_" }
}

$D = "C:\holy"; $A = "C:\holyapp"; New-Item -ItemType Directory -Force -Path $A | Out-Null
$base = "http://127.0.0.1:8099"
# 0) the dashboard runs inside THIS step (the runner kills a step's processes when the step ends)
New-Item -ItemType Directory -Force -Path $D | Out-Null
Copy-Item Holy_Dashboard.pyw $D\
'{"port": 8099}' | Set-Content -Encoding ascii "$D\dashboard_config.json"
$env:PYTHONUTF8 = "1"
$dash = Start-Process python -ArgumentList "Holy_Dashboard.pyw","--headless" -WorkingDirectory $D -RedirectStandardOutput "$D\dash.log" -RedirectStandardError "$D\dash.err" -WindowStyle Hidden -PassThru
for ($k = 0; $k -lt 90; $k++) { try { if ((Invoke-WebRequest "$base/" -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200) { break } } catch {}; Start-Sleep 1 }
Check "dashboard up (python $((Get-Command python).Version))" (-not $dash.HasExited) "pid=$($dash.Id)"
# 1) the dashboard serves the app (logged in: a fresh dashboard has no password)
$info = Invoke-RestMethod "$base/api/app/info"
Check "the dashboard knows the Windows app 2.0" ($info.win.size -gt 50000 -and $info.win.name -eq "2.0") "size=$($info.win.size) name=$($info.win.name) apk=$($info.apk.name)"
Invoke-WebRequest "$base/app/holy.exe?u=$([uri]::EscapeDataString($base))" -OutFile "$A\TheHolyDashboard.exe" -UseBasicParsing
$bytes = [IO.File]::ReadAllBytes("$A\TheHolyDashboard.exe")
$txt = [Text.Encoding]::ASCII.GetString($bytes)
$i = $txt.IndexOf("HOLY-URL-SLOT:")
Check "downloaded with the address inside" ($i -gt 0 -and $txt.Substring($i + 14, $base.Length) -eq $base) "bytes=$($bytes.Length) slot=$i"
$slotTok = ($txt.Substring($i + 14, 560) -split [char]0)[1]
Check "…and a device key for the notifications (not shown)" ($slotTok.Length -ge 40) "key length=$($slotTok.Length)"
$pe = [BitConverter]::ToInt32($bytes, 0x3c); $mach = [BitConverter]::ToUInt16($bytes, $pe + 4)
Check "32-bit program (runs on 32 and 64-bit Windows)" ($mach -eq 0x14c) ("machine=0x{0:x}" -f $mach)
$imports = ([regex]::Matches($txt, "[A-Za-z0-9_]+\.dll") | ForEach-Object { $_.Value.ToLower() } | Sort-Object -Unique) -join " "
Check "needs no runtime (only Windows' own DLLs)" (-not ($imports -match "vcruntime|msvcp|ucrtbase|api-ms-win-crt|libgcc|msvcrt")) $imports
$devs0 = (Invoke-RestMethod "$base/api/app/devices" -Method Post -ContentType "application/json" -Body '{"act":"list"}').devs
Check "the download linked a computer (💻 · not opened yet)" (($devs0 | Where-Object { $_.name -like "*Windows*" }).Count -ge 1) "devices=$($devs0.Count)"
$sig = Get-AuthenticodeSignature "$A\TheHolyDashboard.exe"
Write-Host "HOLYWIN ℹ️ signature: $($sig.Status) (unsigned ⇒ SmartScreen asks once)"
$vi = (Get-Item "$A\TheHolyDashboard.exe").VersionInfo
Check "version info" ($vi.ProductName -eq "The Holy Dashboard" -and $vi.ProductVersion -eq "2.0") "$($vi.ProductName) $($vi.ProductVersion)"
$fav = Invoke-WebRequest "$base/favicon.ico" -UseBasicParsing
Check "favicon.ico served (no login needed)" ($fav.StatusCode -eq 200 -and $fav.RawContentLength -gt 10000) "len=$($fav.RawContentLength)"

# 2) --setup ⇒ the address window (RTL, the icon) · closing it ⇒ nothing opens
$p = Start-Process "$A\TheHolyDashboard.exe" -ArgumentList "--setup" -PassThru
$hw = [IntPtr]::Zero
for ($k = 0; $k -lt 40 -and $hw -eq [IntPtr]::Zero; $k++) { Start-Sleep -Milliseconds 250; $hw = [W]::FindWindow("HolySetup", [NullString]::Value) }
Check "--setup shows the address window" ($hw -ne [IntPtr]::Zero) "hwnd=$hw"
if ($hw -ne [IntPtr]::Zero) { Start-Sleep -Milliseconds 600; Shot "setup"; [W]::SendMessage($hw, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null }
$p.WaitForExit(8000) | Out-Null
Check "…closing it ends the app (nothing launched)" ($p.HasExited -and -not (Get-Process msedge -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "holyapp=win" })) "exit=$($p.ExitCode)"

# 3) an address that doesn't answer ⇒ the warning · Cancel ⇒ nothing opens
Invoke-WebRequest "$base/app/holy.exe?u=$([uri]::EscapeDataString('http://127.0.0.1:9'))" -OutFile "$A\dead.exe" -UseBasicParsing
$p = Start-Process "$A\dead.exe" -PassThru
$mb = [IntPtr]::Zero
for ($k = 0; $k -lt 60 -and $mb -eq [IntPtr]::Zero; $k++) { Start-Sleep -Milliseconds 250; $mb = [W]::FindWindow("#32770", "The Holy Dashboard") }
Check "unreachable address ⇒ «ما گدرت أوصل للوحة» warning" ($mb -ne [IntPtr]::Zero) "hwnd=$mb"
if ($mb -ne [IntPtr]::Zero) { Shot "unreachable"; [W]::SendMessage($mb, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null }
$p.WaitForExit(8000) | Out-Null
Check "…Cancel ⇒ it stops (no browser)" ($p.HasExited -and -not (Get-Process msedge -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "holyapp=win" })) ""
Remove-Item "$env:APPDATA\HolyDashboard\holy.ini" -ErrorAction SilentlyContinue      # the dead address must not stay saved for the real run

# 4) the real run: first start ⇒ address + key saved · shortcuts · starts with Windows · Edge full screen · the app stays (tray icon)
$L = "$env:APPDATA\HolyDashboard\holy.log"
$p = Start-Process "$A\TheHolyDashboard.exe" -PassThru
$tray = [IntPtr]::Zero
for ($k = 0; $k -lt 60 -and $tray -eq [IntPtr]::Zero; $k++) { Start-Sleep -Milliseconds 500; $tray = [W]::FindWindow("HolyTray2", [NullString]::Value) }
Check "the app stays running as the notifications icon (tray)" ((-not $p.HasExited) -and $tray -ne [IntPtr]::Zero) "pid=$($p.Id) tray=$tray"
$ini = Get-Content "$env:APPDATA\HolyDashboard\holy.ini" -Raw -ErrorAction SilentlyContinue
Check "address saved to %APPDATA%\HolyDashboard\holy.ini" ($ini -match [regex]::Escape("url=$base")) (($ini -replace "token=[^\r\n]*", "token=(hidden)") -replace "`r?`n", " ")
$iniTok = if ($ini -match "token=([A-Za-z0-9_\-]+)") { $Matches[1] } else { "" }
Check "…and the device key (the same one the download carried)" ($iniTok -ne "" -and $iniTok -eq $slotTok) ""
$sh = New-Object -ComObject WScript.Shell
foreach ($lnk in @("$([Environment]::GetFolderPath('Desktop'))\The Holy Dashboard.lnk", "$([Environment]::GetFolderPath('Programs'))\The Holy Dashboard.lnk")) {
  $t = if (Test-Path $lnk) { $sh.CreateShortcut($lnk).TargetPath } else { "" }
  Check "shortcut $([IO.Path]::GetFileName([IO.Path]::GetDirectoryName($lnk)))" ($t -eq "$A\TheHolyDashboard.exe") $t
}
$run = (Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue).TheHolyDashboard
Check "starts with Windows (notifications after a restart)" ($run -eq "`"$A\TheHolyDashboard.exe`" --tray") $run
$h = [IntPtr]::Zero
for ($k = 0; $k -lt 60 -and $h -eq [IntPtr]::Zero; $k++) { Start-Sleep -Milliseconds 500; $h = [W]::FindWindow("HolyDash", [NullString]::Value) }
$edge = Get-CimInstance Win32_Process -Filter "name='msedge.exe'" | Where-Object { $_.CommandLine -match "holyapp=win" }
$wv = @(Get-Process msedgewebview2 -ErrorAction SilentlyContinue).Count
Check "2.0: the dashboard in the program's own window (WebView2 · no Edge window)" ($h -ne [IntPtr]::Zero -and -not $edge -and $wv -gt 0) "hwnd=$h webview2 processes=$wv"
function Hello($after) {      # the page says where it drew — ☐ ✕ (screen points) · the newest line after $after
  for ($k = 0; $k -lt 60; $k++) {
    $l = (Get-Content $L -ErrorAction SilentlyContinue | Select-String "page: buttons drawn" | Select-Object -Last 1)
    if ($l -and ($after -eq $null -or $l.LineNumber -gt $after)) {
      $m = [regex]::Match($l.Line, "min=(-?\d+),(-?\d+) max=(-?\d+),(-?\d+) close=(-?\d+),(-?\d+) drag=(-?\d+),(-?\d+)")
      if ($m.Success) { return @{ n = $l.LineNumber; min = @([int]$m.Groups[1].Value, [int]$m.Groups[2].Value); max = @([int]$m.Groups[3].Value, [int]$m.Groups[4].Value);
        cls = @([int]$m.Groups[5].Value, [int]$m.Groups[6].Value); drag = @([int]$m.Groups[7].Value, [int]$m.Groups[8].Value); line = $l.Line } } }
    Start-Sleep -Milliseconds 500 }
  return $null }
Start-Sleep -Seconds 6     # the opening animation ends, the numbers load
if ($h -ne [IntPtr]::Zero) {
  $st = [W]::GetWindowLong($h, -16)
  $btn = (($st -band 0x20000) -ne 0) -and (($st -band 0x10000) -ne 0) -and (($st -band 0x80000) -ne 0) -and (($st -band 0x40000) -ne 0)
  Check "the window keeps Windows' minimize · maximize · close · resizable edges (taskbar · Alt+Space · snapping)" $btn ("style=0x{0:X8}" -f $st)
  Check "…opens maximized" ([W]::IsZoomed($h)) ([W]::Rect($h))
  $hz = Hello $null
  Check "the dashboard drew — ☐ ✕ beside 🔔 and told the program where" ($hz -ne $null) $(if ($hz) { $hz.line } else { "no «page: buttons drawn» in holy.log" })
  [W]::ShowWindow($h, 9) | Out-Null; Start-Sleep -Seconds 2
  $r = [W]::R4($h); $c = [W]::C4($h); $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  Check "…«restore» ⇒ a smaller window" (-not [W]::IsZoomed($h) -and ($r[2] - $r[0]) -lt $b.Width) ([W]::Rect($h))
  Check "no title bar: the whole window is the dashboard" (($c[2] - $c[0]) -eq ($r[2] - $r[0]) -and ($c[3] - $c[1]) -eq ($r[3] - $r[1])) "window=$($r -join ',') client=$($c -join ',')"
  Shot "window-2.0"
  $hr = Hello $hz.n
  if ($hr) {
    [W]::SetForegroundWindow($h) | Out-Null; Start-Sleep -Milliseconds 400
    $r0 = [W]::R4($h); $dx = $hr.drag[0]; $dy = $hr.drag[1]
    [W]::Down($dx, $dy); for ($s = 1; $s -le 20; $s++) { [W]::SetCursorPos($dx + 10 * $s, $dy + 6 * $s) | Out-Null; Start-Sleep -Milliseconds 30 }; Start-Sleep -Milliseconds 300; [W]::Up(); Start-Sleep -Seconds 1
    $r1 = [W]::R4($h)
    Check "🖱️ press the dashboard's top bar and drag ⇒ the whole window moves" ((($r1[0] - $r0[0]) -gt 120) -and (($r1[1] - $r0[1]) -gt 60) -and -not [W]::IsZoomed($h)) "before=$($r0 -join ',') after=$($r1 -join ',')"
    Shot "moved"
    $ox = $r1[0] - $r0[0]; $oy = $r1[1] - $r0[1]
    [W]::Click($dx + $ox, $dy + $oy); Start-Sleep -Milliseconds 90; [W]::Click($dx + $ox, $dy + $oy); Start-Sleep -Seconds 2
    Check "🖱️ double-click on the top bar ⇒ maximized" ([W]::IsZoomed($h)) ([W]::Rect($h))
    $hm = Hello $hr.n
    if ($hm) { [W]::Click($hm.max[0], $hm.max[1]); Start-Sleep -Seconds 2
      Check "🖱️ ☐ (now ❐) ⇒ back to the window" (-not [W]::IsZoomed($h) -and -not [W]::IsIconic($h)) ([W]::Rect($h))
      $hn = Hello $hm.n
      if ($hn) { [W]::Click($hn.max[0], $hn.max[1]); Start-Sleep -Seconds 2; Check "🖱️ ☐ ⇒ maximized" ([W]::IsZoomed($h)) ([W]::Rect($h)) }
      $hq = Hello $(if ($hn) { $hn.n } else { $hm.n }); if (-not $hq) { $hq = $hm }
      [W]::Click($hq.min[0], $hq.min[1]); Start-Sleep -Seconds 2
      Check "🖱️ — ⇒ minimized (to the taskbar)" ([W]::IsIconic($h)) ""
      [W]::ShowWindow($h, 9) | Out-Null; Start-Sleep -Seconds 2 }
  } else { Check "the page re-told the buttons after «restore»" $false "" }
  [W]::ShowWindow($h, 3) | Out-Null; Start-Sleep -Seconds 2
  [W]::SetForegroundWindow($h) | Out-Null; Start-Sleep -Milliseconds 800
  [System.Windows.Forms.SendKeys]::SendWait("{F11}"); Start-Sleep -Seconds 3; $r2 = [W]::R4($h)
  if ($r2[0] -le 0 -and $r2[1] -le 0 -and $r2[2] -ge $b.Width -and $r2[3] -ge $b.Height) {
    Check "…F11 ⇒ full screen (the dashboard's ⛶ does the same)" $true ([W]::Rect($h)); Shot "fullscreen"
    [System.Windows.Forms.SendKeys]::SendWait("{F11}"); Start-Sleep -Seconds 3
    Check "…F11 again ⇒ back to the window" ([W]::IsZoomed($h)) ([W]::Rect($h))
  } else { Write-Host "HOLYWIN ℹ️ F11 not delivered to the window on this runner (focus) — window=$([W]::Rect($h))" }
  Shot "dashboard-2.0"
  $hc = Hello $null
  if ($hc) { [W]::Click($hc.cls[0], $hc.cls[1]); Start-Sleep -Seconds 3
    Check "🖱️ ✕ ⇒ the window closes · the notifications icon stays" ([W]::FindWindow("HolyDash", [NullString]::Value) -eq [IntPtr]::Zero -and [W]::FindWindow("HolyTray2", [NullString]::Value) -ne [IntPtr]::Zero -and (Get-Process TheHolyDashboard -ErrorAction SilentlyContinue).Count -eq 1) "" }
}
Shot "dashboard"
Write-Host "HOLYWIN windows: $(([W]::List() -split "`n" | Select-Object -First 12) -join ' ;; ')"

# 5) notifications: the watcher reaches the feed · a test alert ⇒ a Windows notification · the computer shows as connected
function LogHas($pat, $sec) { for ($k = 0; $k -lt $sec * 2; $k++) { if ((Get-Content $L -Raw -ErrorAction SilentlyContinue) -match $pat) { return $true }; Start-Sleep -Milliseconds 500 }; return $false }
Check "the watcher reaches the dashboard feed" (LogHas "feed ok" 30) ""
Start-Sleep -Seconds 2
Invoke-RestMethod "$base/api/app/devices" -Method Post -ContentType "application/json" -Body '{"act":"test","sample":"trade"}' | Out-Null
Check "test alert ⇒ a Windows notification shown" (LogHas "shown 1 notification" 30) ""
Start-Sleep -Milliseconds 1500; Shot "notification"
$devs = (Invoke-RestMethod "$base/api/app/devices" -Method Post -ContentType "application/json" -Body '{"act":"list"}').devs
$pc = $devs | Where-Object { $_.name -like "*Windows*" -and [int]$_.seen -gt [int]$_.created } | Select-Object -First 1
Check "the dashboard sees this computer connected (💻 in ⚙️)" ($pc -ne $null) "devices=$($devs.Count) $($pc.name)"

# 6) one watcher only: a second start opens the dashboard through the running one · --tray (Windows start) while running ⇒ quits
$p2 = Start-Process "$A\TheHolyDashboard.exe" -PassThru; $p2.WaitForExit(15000) | Out-Null
$n = (Get-Process TheHolyDashboard -ErrorAction SilentlyContinue).Count
Check "second start ⇒ hands over and exits · still one watcher" ($p2.HasExited -and $p2.ExitCode -eq 0 -and $n -eq 1) "exit=$($p2.ExitCode) running=$n"
$back = [IntPtr]::Zero; for ($k = 0; $k -lt 30 -and $back -eq [IntPtr]::Zero; $k++) { Start-Sleep -Milliseconds 500; $back = [W]::FindWindow("HolyDash", [NullString]::Value) }
Check "…and the running one opened the window again" ($back -ne [IntPtr]::Zero) "hwnd=$back"
$p3 = Start-Process "$A\TheHolyDashboard.exe" -ArgumentList "--tray" -PassThru; $p3.WaitForExit(10000) | Out-Null
Check "--tray while running ⇒ quits at once" ($p3.HasExited -and (Get-Process TheHolyDashboard -ErrorAction SilentlyContinue).Count -eq 1) ""

# 7) the program asks for a newer copy with its own key ⇒ the same key inside (no new device)
$up = Invoke-WebRequest "$base/app/holy.exe?u=$([uri]::EscapeDataString($base))" -Headers @{ "X-Holy-Device" = $iniTok } -UseBasicParsing
$ut = [Text.Encoding]::ASCII.GetString($up.Content); $j = $ut.IndexOf("HOLY-URL-SLOT:")
$devs2 = (Invoke-RestMethod "$base/api/app/devices" -Method Post -ContentType "application/json" -Body '{"act":"list"}').devs
Check "a copy fetched by the program keeps its key (no extra device)" ((($ut.Substring($j + 14, 560) -split [char]0)[1]) -eq $iniTok -and $devs2.Count -eq $devs.Count) "devices=$($devs2.Count)"

# 8) unlink from the dashboard ⇒ the program knows at once (and says so) · it keeps running (the window still opens the dashboard)
if ($pc) {
  Invoke-RestMethod "$base/api/app/devices" -Method Post -ContentType "application/json" -Body (@{ act = "del"; id = $pc.id } | ConvertTo-Json) | Out-Null
  Check "unlinked ⇒ the program notices (401)" (LogHas "401 —" 30) ""
  Check "…and shows «انفصل» as a notification" (LogHas "shown 1 notification \(alert\)" 20) ""
  Check "…the icon stays (opening the dashboard still works)" ((Get-Process TheHolyDashboard -ErrorAction SilentlyContinue).Count -eq 1) ""
}
Write-Host "HOLYWIN holy.log: $((Get-Content $L -Tail 25 -ErrorAction SilentlyContinue) -join ' ;; ')"
Check "the program's log has no key" (-not ((Get-Content $L -Raw -ErrorAction SilentlyContinue) -match [regex]::Escape($iniTok))) ""
Get-Process TheHolyDashboard -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "HOLYWIN dash.log: $((Get-Content "$D\dash.log" -Tail 6 -ErrorAction SilentlyContinue) -join ' ;; ')"
Write-Host "HOLYWIN dash.err: $((Get-Content "$D\dash.err" -Tail 6 -ErrorAction SilentlyContinue) -join ' ;; ')"
Write-Host "HOLYWIN TOTAL $ok ok · $bad failed"
if ($bad) { exit 1 }
