$Logfile = "C:\Windows\Temp\dotnet-install.log"
function LogWrite {
   Param ([string]$logstring)
   $now = Get-Date -format s
   Add-Content $Logfile -value "$now $logstring"
   Write-Host $logstring
}

$isWin7 = wmic os get caption | find /i '" 7 "'
$isWin8 = wmic os get caption | find /i '" 8 "'
$isWinServer2008 = wmic os get caption | find /i '" 2008 "'
$isWin10_1511 = wmic os get version | find /i '"10.0.10586"'

# These versions support up to and including dotNet 4.6
# That also means that their installed Chocolatey version is limited to 1.4.0 and below.
$needs_older_versions=$isWin7 -or $isWin8 -or $isWin10_1511 -or $isWinServer2008

if ($needs_older_versions) {
    $dotnet_version = 4.6
    LogWrite "Running an older Windows version that supports up to dotNet $dotnet_version"
    LogWrite "Copying the installer from pre-downloads..."
    Copy-Item -Path "C:\vagrant\resources\pre_downloads\windows\NDP46-KB3045557-x86-x64-AllOS-ENU.exe" -Destination "C:\Windows\Temp\dotnet-installer.exe"
} else {
    $dotnet_version = 4.8
    LogWrite "Running a Windows version that can download & run dotNet $dotnet_version"

    try {
        LogWrite "Downloading dotNet installer."
        (New-Object System.Net.WebClient).DownloadFile('https://download.visualstudio.microsoft.com/download/pr/2d6bb6b2-226a-4baa-bdec-798822606ff1/8494001c276a4b96804cde7829c04d7f/ndp48-x86-x64-allos-enu.exe', 'C:\Windows\Temp\dotnet-installer.exe')
    } catch {
        LogWrite $_.Exception | Format-List -force
        LogWrite "Failed to download file."
    }
}

LogWrite "Starting installation process for dotNet $dotnet_version..."
try {
    Start-Process -FilePath "C:\Windows\Temp\dotnet-installer.exe" -ArgumentList @("/I", "/q", "/norestart", "/log", "C:\Windows\Temp\dotnet-installer.log") -Wait -PassThru
} catch {
    LogWrite $_.Exception | Format-List -force
    LogWrite "Exception during install process."
}
