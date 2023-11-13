#!/bin/bash

output_dir=../../../resources/pre_downloads/windows
mkdir -p $output_dir

# sha256
ssh_key_checksum=55009a554ba2d409565018498f1ad5946854bf90fa8d13fd3fdc2faa102c1122
ssh_key_file=vagrant.pub
ssh_key_link=https://raw.githubusercontent.com/hashicorp/vagrant/main/keys/vagrant.pub

if [[ ! -f $output_dir/$ssh_key_file ]] ||
[[ `sha256sum $output_dir/$ssh_key_file | awk '{ print $1 }'` != $ssh_key_checksum ]]; then
  curl -L --output $output_dir/$ssh_key_file $ssh_key_link
else
  echo 'vagrant.pub exists with correct file hash; not re-downloading.'
fi
