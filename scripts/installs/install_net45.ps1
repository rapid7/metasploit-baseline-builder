$Logfile = "C:\Windows\Temp\dotnet-install.log"
function LogWrite {
   Param ([string]$logstring)
   $now = Get-Date -format s
   Add-Content $Logfile -value "$now $logstring"
   Write-Host $logstring
}

$isWin7 = wmic os get caption | find /i '" 7 "'
$isWin2008r2 = wmic os get caption | find /i '" 2008 R2 "'
$isSp1 = wmic os get CSDVersion | find /i '" Pack 1"'
$isWin8 = wmic os get caption | find /i '" 8 "'
$isWin81 = wmic os get caption | find /i '" 8.1 "'
$isWin2012 = wmic os get caption | find /i '" 2012 "'
$isWin2012r2 = wmic os get caption | find /i '" 2012 R2"'

if (!($isWin7 -or $isWin8 -or $isWin81 -or $isWin2008r2 -or $isWin2012 -or $isWin2012r2)){
  LogWrite "Skipping net45 install not required for OS"
  exit 0
}

$installFile = "C:\vagrant\resources\pre_downloads\windows\NDP452-KB2901907-x86-x64-AllOS-ENU.exe"
LogWrite "Starting installation process..."
try {
    if(($isWin7 -or $isWin2008r2) -and !$isSp1){
      # Win2008r2 core hangs on defualt install, since background task adds delay only used when required
      $installCmd = "powershell.exe -ExecutionPolicy Bypass -Command " + '"' + ${installFile} + " /I /q /norestart" + '"'
      New-Item C:\Windows\Temp\install_dotnet.bat -ItemType "file"

      Set-Content C:\Windows\Temp\install_dotnet.bat $installCmd

      $Taskname = "updatedotnet"

      SCHTASKS /CREATE /sc ONCE /st 00:00 /TN $Taskname /RU SYSTEM /RL HIGHEST /TR "C:\Windows\Temp\install_dotnet.bat"
      schtasks /Run /TN $Taskname
      start-sleep -s 60
      schtasks /delete /tn $Taskname /f
      start-sleep -s 300
    } else {
      Start-Process -FilePath $installFile -ArgumentList "/I /q /norestart" -Wait -PassThru
    }
} catch {
    LogWrite $_.Exception | Format-List -force
    LogWrite "Exception during install process."
}
shutdown.exe /r /t 15
