$Logfile = "C:\Windows\Temp\wmf-install.log"
function LogWrite {
   Param ([string]$logstring)
   $now = Get-Date -format s
   Add-Content $Logfile -value "$now $logstring"
   Write-Host $logstring
}

if (-Not (Test-Path -Path ../../../resources/pre_downloads/windows)) {
    New-Item -ItemType Directory -Path ../../../resources/pre_downloads/windows
}

# sha256
$tools_windows_checksum="a3072c357826f1cbc9abf362f4f6a04af3a0813c15acf263943dc8a366c25872".ToUpper()
$vmware_tools_windows_checksum="c6d1da22b160b057b94ffab81b8fad307c1601a37350e78f29dccf3a098be522".ToUpper()

$tools_exists=Test-Path "../../../resources/pre_downloads/windows/tools-windows.tar"
# SilentlyContinue lets us have an empty variable and not error out.
$tools_hash_on_disk=Get-FileHash -Path "../../../resources/pre_downloads/windows/tools-windows.tar" -Algorithm SHA256 -ErrorAction SilentlyContinue
if (-Not $tools_exists -Or ($tools_hash_on_disk.hash -ne $tools_windows_checksum)) {
    LogWrite "Downloading tools-windows.tar"
    try {
        (New-Object System.Net.WebClient).DownloadFile('http://softwareupdate.vmware.com/cds/vmw-desktop/ws/12.0.0/2985596/windows/packages/tools-windows.tar', '../../../resources/pre_downloads/windows/tools-windows.tar')
    } catch {
        LogWrite $_.Exception | Format-List -force
        LogWrite "Failed to download file."
    }
} else {
    LogWrite "tools-windows.tar exists with correct file hash; not re-downloading."
}

$vmware_tools_exists=Test-Path "../../../resources/pre_downloads/windows/VMware-tools-windows-10.1.7-5541682.iso"
$vmware_tools_hash_on_disk=Get-FileHash -Path "../../../resources/pre_downloads/windows/VMware-tools-windows-10.1.7-5541682.iso" -Algorithm SHA256 -ErrorAction SilentlyContinue
if (-Not $vmware_tools_exists -Or ($vmware_tools_hash_on_disk.hash -ne $vmware_tools_windows_checksum)) {
    LogWrite "Downloading VMware-tools-windows-10.1.7-5541682.iso"
    try {
        (New-Object System.Net.WebClient).DownloadFile('https://packages.vmware.com/tools/esx/6.5u1/windows/VMware-tools-windows-10.1.7-5541682.iso', '../../../resources/pre_downloads/windows/VMware-tools-windows-10.1.7-5541682.iso')
    } catch {
        LogWrite $_.Exception | Format-List -force
        LogWrite "Failed to download file."
    }
} else {
    LogWrite "VMware-tools-windows-10.1.7-5541682.iso exists with correct file hash; not re-downloading."
}
