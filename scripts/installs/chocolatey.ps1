$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$isWin7 = wmic os get caption | find /i '" 7 "'
$isWin8 = wmic os get caption | find /i '" 8 "'
$isWinServer2008 = wmic os get caption | find /i '" 2008 "'
$isWin10_1511 = wmic os get version | find /i '"10.0.10586"'
$isWin2012 = wmic os get caption | find /i '" 2012 "'

$skip_wrapping = $isWin8 -or $isWin2012

# These versions support up to and including dotNet 4.6
# That also means that their installed Chocolatey version is limited to 1.4.0 and below.
$needs_older_versions=$isWin7 -or $isWin8 -or $isWin10_1511 -or $isWinServer2008

if($needs_older_versions) {
    Start-Process -FilePath 'powershell.exe' -ArgumentList @('C:\vagrant\resources\pre_downloads\windows\install.ps1', '-ChocolateyDownloadUrl', 'C:\vagrant\resources\pre_downloads\windows\chocolatey.1.4.0.nupkg', '-UseNativeUnzip') -Wait -PassThru
} else {
    Start-Process -FilePath 'powershell.exe' -ArgumentList @('C:\vagrant\resources\pre_downloads\windows\install.ps1') -Wait -PassThru
}

Write-Host "Installing Chocolatey finished"

# cribbed from https://gist.github.com/jstangroome/882528
