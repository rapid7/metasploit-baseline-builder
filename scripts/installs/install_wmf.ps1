$Logfile = "C:\Windows\Temp\wmf-install.log"
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

if (!($isWin7 -r $isWin8 -or $isWin81 -or $isWin2012 -or $isWin2012)){
  LogWrite "Skipping WMF 5.1 install not required for OS"
  exit 0
}


LogWrite "Extracting Archive..."

$filesLocation = "C:\vagrant\resources\windows_pre_downloads"
$extractLocation = ${filesLocation} + "\wmf_install"
New-Item -Path $extractLocation -ItemType Directory

$shell = New-Object -ComObject shell.application
if (is_64bit) {
  $zip = $shell.NameSpace(${filesLocation} + "\Win7AndW2K8R2-KB3191566-x64.zip")
} else {
  $zip = $shell.NameSpace(${filesLocation} + "\Win7-KB3191566-x86.zip")
}

foreach ($item in $zip.items()) {
  $shell.Namespace($extractLocation).CopyHere($item)
}

Set-Location -Path $extractLocation -PassThru
# Windows 8.1, 2012, and 2012 R2
if ($isWin81 -or $isWin2012r2){
  if ($is_64bit){
    $extractLocation = ${filesLocation} + "\Win8.1AndW2K12R2-KB3191564-x64.msu"  
  } else {
    $extractLocation = ${filesLocation} + "\Win8.1-KB3191564-x86.msu"
  }
}else{
  if ($isWin2012) {
    $extractLocation = ${filesLocation} + "\W2K12-KB3191565-x64.msu"
  }
}

# Windows 7 and 2008 R2 
if ($isWin7 -or $isWin2008r2){
  $installCmd = "powershell.exe -ExecutionPolicy Bypass -Command " + '"' + ${extractLocation} + "\Install-WMF5.1.ps1 -AcceptEula" + '"'
}else{
  $installCmd = "powershell.exe -ExecutionPolicy Bypass -Command " + '"' + ${extractLocation} + " /quiet /norestart" + '"'
}

LogWrite "Starting installation process..."

New-Item C:\vagrant\resources\windows_pre_downloads\wmf_install\install_wmf.bat -ItemType "file"
Set-Content C:\vagrant\resources\windows_pre_downloads\wmf_install\install_wmf.bat $installCmd

$Taskname = "updatepsh"

SCHTASKS /CREATE /sc ONCE /st 00:00 /TN $Taskname /RU SYSTEM /RL HIGHEST /TR "C:\vagrant\resources\windows_pre_downloads\wmf_install\install_wmf.bat"
schtasks /Run /TN $Taskname
start-sleep -s 5
schtasks /delete /tn $Taskname /f
start-sleep -s 30
