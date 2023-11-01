#!/bin/bash -eux

# Right now, only CentOS 6 needs the vault repos.
# In the future, this may need to be changed to CentOS 7 as well once that reaches EOL.
cat /etc/centos-release
if grep -q -i "release 6" /etc/redhat-release ; then
  echo "==> Changing to vault repositories"
  sudo sed -i -e "s|mirrorlist=|#mirrorlist=|g" /etc/yum.repos.d/CentOS-*
  sudo sed -i -e "s|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g" /etc/yum.repos.d/CentOS-*
fi
