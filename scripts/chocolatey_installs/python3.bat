chocolatey feature enable -n=allowGlobalConfirmation
choco install python --version 3.4.4

REM -- Tesing if on windows 7, do not attempt to install 3.6.x as will hangs
wmic os get caption | find /i "7" > NUL && set IS_WIN7=YES || set IS_WIN7=NO

if %IS_WIN7%==NO (
  choco install python --version 3.6.1
)

chocolatey feature disable -n=allowGlobalConfirmation
