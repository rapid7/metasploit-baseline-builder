$Logfile = "C:\Windows\Temp\wmf-install.log"
function LogWrite {
   Param ([string]$logstring)
   $now = Get-Date -format s
   Add-Content $Logfile -value "$now $logstring"
   Write-Host $logstring
}

New-Item -ItemType Directory -Path ../../../resources/pre_downloads/windows <NUL

LogWrite "Downloading tools-windows.tar"
try {
    (New-Object System.Net.WebClient).DownloadFile('http://softwareupdate.vmware.com/cds/vmw-desktop/ws/12.0.0/2985596/windows/packages/tools-windows.tar', '../../../resources/pre_downloads/windows/tools-windows.tar')
} catch {
    LogWrite $_.Exception | Format-List -force
    LogWrite "Failed to download file."
}

LogWrite "Downloading VMware-tools-windows-10.1.7-5541682.iso"
try {
    (New-Object System.Net.WebClient).DownloadFile('https://packages.vmware.com/tools/esx/6.5u1/windows/VMware-tools-windows-10.1.7-5541682.iso', '../../../resources/pre_downloads/windows/VMware-tools-windows-10.1.7-5541682.iso')
} catch {
    LogWrite $_.Exception | Format-List -force
    LogWrite "Failed to download file."
}
