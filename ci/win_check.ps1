# 💻 Holy Windows app check on a real Windows machine (GitHub windows-latest):
#   the dashboard serves the app with its address inside · first run ⇒ shortcuts + saved address · Edge opens the dashboard
#   FULL SCREEN in app mode with its own profile · the window is the dashboard · --setup shows the address window ·
#   an address that doesn't answer ⇒ the warning (and nothing opens) · a screenshot (base64 in the log, lines HOLYSHOT).
#   Results: lines starting with HOLYWIN in the job log.
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
Check "the dashboard knows the Windows app" ($info.win.size -gt 50000 -and $info.win.name -eq "1.0") "size=$($info.win.size) name=$($info.win.name) apk=$($info.apk.name)"
Invoke-WebRequest "$base/app/holy.exe?u=$([uri]::EscapeDataString($base))" -OutFile "$A\TheHolyDashboard.exe" -UseBasicParsing
$bytes = [IO.File]::ReadAllBytes("$A\TheHolyDashboard.exe")
$txt = [Text.Encoding]::ASCII.GetString($bytes)
$i = $txt.IndexOf("HOLY-URL-SLOT:")
Check "downloaded with the address inside" ($i -gt 0 -and $txt.Substring($i + 14, $base.Length) -eq $base) "bytes=$($bytes.Length) slot=$i"
$sig = Get-AuthenticodeSignature "$A\TheHolyDashboard.exe"
Write-Host "HOLYWIN ℹ️ signature: $($sig.Status) (unsigned ⇒ SmartScreen asks once)"
$vi = (Get-Item "$A\TheHolyDashboard.exe").VersionInfo
Check "version info" ($vi.ProductName -eq "The Holy Dashboard" -and $vi.ProductVersion -eq "1.0") "$($vi.ProductName) $($vi.ProductVersion)"
$fav = Invoke-WebRequest "$base/favicon.ico" -UseBasicParsing
Check "favicon.ico served (no login needed)" ($fav.StatusCode -eq 200 -and $fav.RawContentLength -gt 10000) "len=$($fav.RawContentLength)"

# 2) --setup ⇒ the address window (RTL, the icon) · closing it ⇒ nothing opens
$p = Start-Process "$A\TheHolyDashboard.exe" -ArgumentList "--setup" -PassThru
$hw = [IntPtr]::Zero
for ($k = 0; $k -lt 40 -and $hw -eq [IntPtr]::Zero; $k++) { Start-Sleep -Milliseconds 250; $hw = [W]::FindWindow("HolySetup", $null) }
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

# 4) the real run: first start ⇒ address saved · shortcuts · Edge full screen on the dashboard
$p = Start-Process "$A\TheHolyDashboard.exe" -PassThru
$p.WaitForExit(20000) | Out-Null
Check "the app hands over to the browser and exits" ($p.HasExited -and $p.ExitCode -eq 0) "exit=$($p.ExitCode)"
$ini = Get-Content "$env:APPDATA\HolyDashboard\holy.ini" -Raw -ErrorAction SilentlyContinue
Check "address saved to %APPDATA%\HolyDashboard\holy.ini" ($ini -match [regex]::Escape("url=$base")) ($ini -replace "`r?`n", " ")
$sh = New-Object -ComObject WScript.Shell
foreach ($lnk in @("$([Environment]::GetFolderPath('Desktop'))\The Holy Dashboard.lnk", "$([Environment]::GetFolderPath('Programs'))\The Holy Dashboard.lnk")) {
  $t = if (Test-Path $lnk) { $sh.CreateShortcut($lnk).TargetPath } else { "" }
  Check "shortcut $([IO.Path]::GetFileName([IO.Path]::GetDirectoryName($lnk)))" ($t -eq "$A\TheHolyDashboard.exe") $t
}
$title = ""; $win = $null
for ($k = 0; $k -lt 60; $k++) {
  Start-Sleep -Milliseconds 500
  $rows = [W]::List() -split "`n" | Where-Object { $_ -match "\|Chrome_WidgetWin_1\|" }
  $win = $rows | Where-Object { $_ -match "Holy Dashboard" } | Select-Object -First 1
  if ($win) { break }
}
$cl = (Get-CimInstance Win32_Process -Filter "name='msedge.exe'" | Where-Object { $_.CommandLine -match "holyapp=win" } | Select-Object -First 1).CommandLine
Check "Edge started in app mode · full screen · own profile · the dashboard address" ($cl -match "--app=" -and $cl -match "--start-fullscreen" -and $cl -match "HolyDashboard\\Browser" -and $cl -match [regex]::Escape("127.0.0.1:8099/?holyapp=win")) $cl
Check "the window is the dashboard (title «The Holy Dashboard»)" ($win -ne $null) $win
Start-Sleep -Seconds 6     # the opening animation ends, the numbers load
if ($win) {
  $f = $win -split "\|"; $rc = $f[4] -split ","
  $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  Check "…covers the whole screen" ([int]$rc[0] -le 0 -and [int]$rc[1] -le 0 -and [int]$rc[2] -ge $b.Width -and [int]$rc[3] -ge $b.Height) "window=$($f[4]) screen=$($b.Width)x$($b.Height)"
}
Shot "dashboard"
Write-Host "HOLYWIN windows: $(([W]::List() -split "`n" | Select-Object -First 12) -join ' ;; ')"

# 5) open it again ⇒ no new shortcut prompts, the saved address is used (Shift not held)
$p = Start-Process "$A\TheHolyDashboard.exe" -PassThru; $p.WaitForExit(20000) | Out-Null
Check "second start uses the saved address (exits 0, no dialog)" ($p.HasExited -and $p.ExitCode -eq 0 -and -not ([W]::FindWindow("HolySetup", $null) -ne [IntPtr]::Zero)) ""
Write-Host "HOLYWIN dash.log: $((Get-Content "$D\dash.log" -Tail 6 -ErrorAction SilentlyContinue) -join ' ;; ')"
Write-Host "HOLYWIN dash.err: $((Get-Content "$D\dash.err" -Tail 6 -ErrorAction SilentlyContinue) -join ' ;; ')"
Write-Host "HOLYWIN TOTAL $ok ok · $bad failed"
if ($bad) { exit 1 }
