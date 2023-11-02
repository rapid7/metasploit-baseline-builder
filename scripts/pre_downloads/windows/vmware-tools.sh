#!/bin/bash

mkdir -p ../../../resources/pre_downloads/windows

# sha256
tools_windows_checksum=a3072c357826f1cbc9abf362f4f6a04af3a0813c15acf263943dc8a366c25872
vmware_tools_windows_checksum=c6d1da22b160b057b94ffab81b8fad307c1601a37350e78f29dccf3a098be522

if [[ ! -f ../../../resources/pre_downloads/windows/tools-windows.tar ]] ||
[[ $(sha256sum ../../../resources/pre_downloads/windows/tools-windows.tar) = tools_windows_checksum ]]; then
  curl -L --output ../../../resources/pre_downloads/windows/tools-windows.tar http://softwareupdate.vmware.com/cds/vmw-desktop/ws/12.0.0/2985596/windows/packages/tools-windows.tar
else
  echo 'tools-windows.tar exists with correct file hash; not re-downloading.'
fi

if [[ ! -f ../../../resources/pre_downloads/windows/VMware-tools-windows-10.1.7-5541682.iso ]] ||
[[ $(sha256sum ../../../resources/pre_downloads/windows/VMware-tools-windows-10.1.7-5541682.iso) = vmware_tools_windows_checksum ]]; then
  curl -L --output ../../../resources/pre_downloads/windows/VMware-tools-windows-10.1.7-5541682.iso https://packages.vmware.com/tools/esx/6.5u1/windows/VMware-tools-windows-10.1.7-5541682.iso
else
  echo 'VMware-tools-windows-10.1.7-5541682.iso exists with correct file hash; not re-downloading.'
fi
