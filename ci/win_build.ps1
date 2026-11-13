# 💻 build the Windows program 2.0 on GitHub's Windows machine: MSVC x86 · /MT (no runtime DLL) · Microsoft's static WebView2 loader
#   (NuGet Microsoft.Web.WebView2) · then put it into the dashboard checked out here (windows/embed.py) · and print it (base64 lines
#   HOLYEXE) so it can be taken from the log and put into the repository's dashboard.
$ErrorActionPreference = "Stop"
$V = "1.0.2903.40"
Invoke-WebRequest "https://api.nuget.org/v3-flatcontainer/microsoft.web.webview2/$V/microsoft.web.webview2.$V.nupkg" -OutFile wv2.zip -UseBasicParsing
Expand-Archive wv2.zip -DestinationPath wv2 -Force
$vs = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
$bat = Join-Path $vs "VC\Auxiliary\Build\vcvarsall.bat"
Write-Host "HOLYBUILD vcvarsall: $bat"
$inc = (Resolve-Path "wv2\build\native\include").Path; $lib = (Resolve-Path "wv2\build\native\x86\WebView2LoaderStatic.lib").Path
$cmd = "`"$bat`" x86 >nul && cd windows && rc /nologo /fo holy_win.res holy_win.rc && cl /nologo /O1 /MT /utf-8 /W3 /GS /DUNICODE /D_UNICODE /I`"$inc`" holy_win.c holy_win.res /Fe:..\TheHolyDashboard.exe /link /SUBSYSTEM:WINDOWS /MANIFEST:NO /OPT:REF /OPT:ICF `"$lib`""
cmd /c $cmd 2>&1 | ForEach-Object { Write-Host "HOLYBUILD $_" }
if (-not (Test-Path TheHolyDashboard.exe)) { throw "the build failed (see HOLYBUILD lines)" }
python windows/embed.py Holy_Dashboard.pyw TheHolyDashboard.exe
if ($LASTEXITCODE) { throw "embed failed" }
$h = (Get-FileHash TheHolyDashboard.exe -Algorithm SHA256).Hash.ToLower(); $n = (Get-Item TheHolyDashboard.exe).Length
$b = [Convert]::ToBase64String([IO.File]::ReadAllBytes("TheHolyDashboard.exe"))
Write-Host "HOLYEXE-BEGIN $h $n"
for ($i = 0; $i -lt $b.Length; $i += 4000) { Write-Host ("HOLYEXE " + $b.Substring($i, [Math]::Min(4000, $b.Length - $i))) }
Write-Host "HOLYEXE-END"
