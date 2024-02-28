#!/bin/bash

fileArray=( # format as sha256::URL
  # vmware tools
  "a3072c357826f1cbc9abf362f4f6a04af3a0813c15acf263943dc8a366c25872::http://softwareupdate.vmware.com/cds/vmw-desktop/ws/12.0.0/2985596/windows/packages/tools-windows.tar"
  "c6d1da22b160b057b94ffab81b8fad307c1601a37350e78f29dccf3a098be522::https://packages.vmware.com/tools/esx/6.5u1/windows/VMware-tools-windows-10.1.7-5541682.iso"
  # windows dotnet 4.5 and wmf 5
  "4a1385642c1f08e3be7bc70f4a9d74954e239317f50d1a7f60aa444d759d4f49::https://download.microsoft.com/download/6/F/5/6F5FF66C-6775-42B0-86C4-47D41F2DA187/W2K12-KB3191565-x64.msu"
  "eb7e2c4ce2c6cb24206474a6cb8610d9f4bd3a9301f1cd8963b4ff64e529f563::https://download.microsoft.com/download/6/F/5/6F5FF66C-6775-42B0-86C4-47D41F2DA187/Win7-KB3191566-x86.zip"
  "f383c34aa65332662a17d95409a2ddedadceda74427e35d05024cd0a6a2fa647::https://download.microsoft.com/download/6/F/5/6F5FF66C-6775-42B0-86C4-47D41F2DA187/Win7AndW2K8R2-KB3191566-x64.zip"
  "f3430a90be556a77a30bab3ac36dc9b92a43055d5fcc5869da3bfda116dbd817::https://download.microsoft.com/download/6/F/5/6F5FF66C-6775-42B0-86C4-47D41F2DA187/Win8.1-KB3191564-x86.msu"
  "a8d788fa31b02a999cc676fb546fc782e86c2a0acd837976122a1891ceee42c0::https://download.microsoft.com/download/6/F/5/6F5FF66C-6775-42B0-86C4-47D41F2DA187/Win8.1AndW2K12R2-KB3191564-x64.msu"
  "6c2c589132e830a185c5f40f82042bee3022e721a216680bd9b3995ba86f3781::https://download.microsoft.com/download/E/2/1/E21644B5-2DF2-47C2-91BD-63C560427900/NDP452-KB2901907-x86-x64-AllOS-ENU.exe"
)

output_dir=../../../resources/pre_downloads/windows
mkdir -p $output_dir

for key in ${fileArray[@]}; do
  parts=(${key//::/ })
  sha256sum=${parts[0]}
  file=${parts[1]##*/}
  echo "processing $file"
  if [[ ! -f $output_dir/$file ]] ||
  [[ `shasum -a 256 $output_dir/$file | awk '{ print $1 }'` != $sha256sum ]]; then
    curl -L --output $output_dir/$file ${parts[1]}
  else
    echo "$file exists with correct file hash; not re-downloading."
  fi
done