#!/bin/bash -eux

SSH_USER=${SSH_USERNAME:-vagrant}
SSH_USER_HOME=${SSH_USER_HOME:-/home/${SSH_USER}}

# Right now, only CentOS 6 & 8 needs the vault repos.
# In the future, this may need to be changed to CentOS 7 as well once that reaches EOL.
# https://endoflife.date/centos
if grep -q -i "release 6" /etc/centos-release || grep -q -i "release 8" /etc/centos-release ; then
  echo "==> Changing to vault repositories"
  sudo sed -i -e "s|mirrorlist=|#mirrorlist=|g" /etc/yum.repos.d/CentOS-*
  sudo sed -i -e "s|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g" /etc/yum.repos.d/CentOS-*
fi

if grep -q -i "release 8" /etc/centos-release ; then
  echo "==> Updating libmodulemd"
  # Stop libmodulemd from spamming `Module yaml error: Unexpected key in data: static_context [line 9 col 3]`
  yum update -y libmodulemd 2>/dev/null
fi

function install_open_vm_tools {
    echo "==> Installing Open VM Tools"
    # Install open-vm-tools so we can mount shared folders
    yum --enablerepo=extras install -y epel-release
    yum install -y open-vm-tools
    # Add /mnt/hgfs so the mount works automatically with Vagrant
    mkdir -p /mnt/hgfs
}

if [[ $PACKER_BUILDER_TYPE =~ vmware ]]; then
    echo "==> Installing VMware Tools"
    cat /etc/redhat-release
    if grep -q -i "release 6" /etc/redhat-release ; then
        # Uninstall fuse to fake out the vmware install so it won't try to
        # enable the VMware blocking filesystem
        yum erase -y fuse
    fi
    # Assume that we've installed all the prerequisites:
    # kernel-headers-$(uname -r) kernel-devel-$(uname -r) gcc make perl
    # from the install media via ks.cfg

    KERNEL_VERSION="$(uname -r)"
    KERNEL_MAJOR_VERSION="${KERNEL_VERSION%%.*}"
    KERNEL_MINOR_VERSION_START="${KERNEL_VERSION#*.}"
    KERNEL_MINOR_VERSION="${KERNEL_MINOR_VERSION_START%%.*}"
    echo "Kernel version ${KERNEL_MAJOR_VERSION}.${KERNEL_MINOR_VERSION}"
      install_open_vm_tools
fi
