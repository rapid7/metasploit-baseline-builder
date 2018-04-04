$ChocoInstallPath = "$env:SystemDrive\ProgramData\Chocolatey\bin"

if (!(Test-Path $ChocoInstallPath)) {
  $env:chocolateyVersion = '0.10.8' # hack as 0.10.9 is broken - for https://github.com/chocolatey/choco/issues/1529
  iex ((new-object net.webclient).DownloadString('https://chocolatey.org/install.ps1'))
}
