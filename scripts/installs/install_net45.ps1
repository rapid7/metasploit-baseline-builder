$Logfile = "C:\Windows\Temp\dotnet-install.log"
function LogWrite {
   Param ([string]$logstring)
   $now = Get-Date -format s
   Add-Content $Logfile -value "$now $logstring"
   Write-Host $logstring
}

$is_64bit = [IntPtr]::size -eq 8
$isWin7 = wmic os get caption | find /i '" 7 "'
$isWin2008r2 = wmic os get caption | find /i '" 2008 R2 "'
$isWin8 = wmic os get caption | find /i '" 8 "'
$isWin81 = wmic os get caption | find /i '" 8.1 "'
$isWin2012 = wmic os get caption | find /i '" 2012 "'
$isWin2012r2 = wmic os get caption | find /i '" 2012 R2"'

if (!($isWin7 -or $isWin8 -or $isWin81 -or $isWin2008r2 -or $isWin2012 -or $isWin2012r2)){
  LogWrite "Skipping net45 install not required for OS"
  exit 0
}

LogWrite "Starting installation process..."
try {
    Start-Process -FilePath "C:\vagrant\resources\windows_pre_downloads\dotnet.exe" -ArgumentList "/I /q /norestart" -Wait -PassThru
} catch {
    LogWrite $_.Exception | Format-List -force
    LogWrite "Exception during install process."
}
shutdown.exe /r /t 15