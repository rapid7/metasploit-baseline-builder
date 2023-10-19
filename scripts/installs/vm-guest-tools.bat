reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set OS=32BIT || set OS=64BIT

wmic os get caption | find /i "7" > NUL && set TOOLS_VER=OLD || set TOOLS_VER=NEW

if %TOOLS_VER%==NEW (
  wmic os get caption | find /i "2008" > NUL && set TOOLS_VER=OLD || set TOOLS_VER=NEW
)

if not exist "C:\Windows\Temp\windows.iso" (
    if %TOOLS_VER%==OLD (
      copy C:\vagrant\resources\pre_downloads\windows\tools-windows.tar C:\Windows\Temp\vmware-tools.tar
      cmd /c ""C:\Program Files\7-Zip\7z.exe" x C:\Windows\Temp\vmware-tools.tar -oC:\Windows\Temp"
      FOR /r "C:\Windows\Temp" %%a in (VMware-tools-windows-*.iso) DO REN "%%~a" "windows.iso"
    ) else (
      copy C:\vagrant\resources\pre_downloads\windows\VMware-tools-windows-10.1.7-5541682.iso C:\Windows\Temp\windows.iso
    )
)

cmd /c ""C:\Program Files\7-Zip\7z.exe" x "C:\Windows\Temp\windows.iso" -oC:\Windows\Temp\VMWare"

if %OS%==64BIT (
    cmd /c C:\Windows\Temp\VMWare\setup64.exe /S /v "/qn /l*v ""%TEMP%\vmmsi.log"" REBOOT=R ADDLOCAL=ALL"
    goto :done
)

cmd /c C:\Windows\Temp\VMWare\setup.exe /S /v "/qn /l*v ""%TEMP%\vmmsi.log"" REBOOT=R ADDLOCAL=ALL"

:done
