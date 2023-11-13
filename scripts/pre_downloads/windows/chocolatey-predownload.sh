#!/bin/bash

output_dir=../../../resources/pre_downloads/windows
mkdir -p $output_dir

# sha256
chocolatey_checksum=1660261edd358ff5ea84a503ca3f01a24ddb0e281002bd4237b1071289161a26
chocolatey_script_checksum=b2980c92c1e3efb45e3efa428e2ef26eac846f8b2606da0d2b1342ac26d36b97
dot_net_46_checksum=b21d33135e67e3486b154b11f7961d8e1cfd7a603267fb60febb4a6feab5cf87

choco_file=chocolatey.1.4.0.nupkg
choco_script=install.ps1
dot_net_file=NDP46-KB3045557-x86-x64-AllOS-ENU.exe

choco_link=https://github.com/chocolatey/choco/releases/download/1.4.0/chocolatey.1.4.0.nupkg
choco_script_link=https://community.chocolatey.org/install.ps1
dot_net_link=https://download.microsoft.com/download/6/F/9/6F9673B1-87D1-46C4-BF04-95F24C3EB9DA/enu_netfx/NDP46-KB3045557-x86-x64-AllOS-ENU_exe/NDP46-KB3045557-x86-x64-AllOS-ENU.exe

if [[ ! -f $output_dir/$choco_file ]] ||
[[ `sha256sum $output_dir/$choco_file | awk '{ print $1 }'` != $chocolatey_checksum ]]; then
  curl -L --output $output_dir/$choco_file $choco_link
else
  echo 'chocolatey.1.4.0.nupkg exists with correct file hash; not re-downloading.'
fi

if [[ ! -f $output_dir/$choco_script ]] ||
[[ `sha256sum $output_dir/$choco_script | awk '{ print $1 }'` != $chocolatey_script_checksum ]]; then
  curl -L --output $output_dir/$choco_script $choco_script_link
else
  echo 'install.ps1 exists with correct file hash; not re-downloading.'
fi

if [[ ! -f $output_dir/$dot_net_file ]] ||
[[ `sha256sum $output_dir/$dot_net_file | awk '{ print $1 }'` != $dot_net_46_checksum ]]; then
  curl -L --output $output_dir/$dot_net_file $dot_net_link
else
  echo 'NDP46-KB3045557-x86-x64-AllOS-ENU.exe exists with correct file hash; not re-downloading.'
fi
