#!/bin/bash -e
# also test if this is env on a platform that needs these files, can I pass the OS verions to this script?

if [ -f "pre_downloads/windows/dotnet.exe" ]; then
  echo "Using existing dotnet downlaod"
else
  curl -L --output pre_downloads/windows/dotnet.exe https://download.microsoft.com/download/E/2/1/E21644B5-2DF2-47C2-91BD-63C560427900/NDP452-KB2901907-x86-x64-AllOS-ENU.exe
fi
if [ -f "pre_downloads/windows/Win8.1-KB3191564-x86.msu" ]; then
  echo "Using existing wmf downlaod"
else
  curl -L --output pre_downloads/windows/W2K12-KB3191565-x64.msu https://download.microsoft.com/download/6/F/5/6F5FF66C-6775-42B0-86C4-47D41F2DA187/W2K12-KB3191565-x64.msu
  curl -L --output pre_downloads/windows/Win7AndW2K8R2-KB3191566-x64.zip https://download.microsoft.com/download/6/F/5/6F5FF66C-6775-42B0-86C4-47D41F2DA187/Win7AndW2K8R2-KB3191566-x64.zip
  curl -L --output pre_downloads/windows/Win7-KB3191566-x86.zip https://download.microsoft.com/download/6/F/5/6F5FF66C-6775-42B0-86C4-47D41F2DA187/Win7-KB3191566-x86.zip
  curl -L --output pre_downloads/windows/Win8.1AndW2K12R2-KB3191564-x64.msu https://download.microsoft.com/download/6/F/5/6F5FF66C-6775-42B0-86C4-47D41F2DA187/Win8.1AndW2K12R2-KB3191564-x64.msu
  curl -L --output pre_downloads/windows/Win8.1-KB3191564-x86.msu https://download.microsoft.com/download/6/F/5/6F5FF66C-6775-42B0-86C4-47D41F2DA187/Win8.1-KB3191564-x86.msu
fi
