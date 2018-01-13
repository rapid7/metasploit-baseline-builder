chocolatey feature enable -n=allowGlobalConfirmation

wmic os get caption | find /i "7" > NUL && set NEED_2015=YES || set NEED_2015=NO

if %NEED_2015%==NO (
  wmic os get caption | find /i "8" > NUL && set NEED_2015=YES || set NEED_2015=NO
)

if %NEED_2015%==YES (
    choco install vcredist2015
)

chocolatey feature disable -n=allowGlobalConfirmation
