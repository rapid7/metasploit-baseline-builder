#!/bin/bash

echo 'LC_ALL="en_US.UTF-8"' >> /etc/default/locale

# These packages are available on CentOS 6, 7 and 8.
yum -y install \
  gcc gpg openssl-devel bzip2-devel \
  gcc-c++ patch readline readline-devel zlib zlib-devel \
  libffi-devel make \
  bzip2 autoconf automake libtool bison sqlite-devel \
  curl gnupg2 && \
yum -y install java-1.8.0-openjdk.x86_64 && \

# CentOS 8 doesn't have some of the packages that are present in 6 & 7.
# e.g. python -> python2.7
# CentOS 6 doesn't have issues with missing packages currently.
# https://endoflife.date/centos
if grep -q -i "release 8" /etc/centos-release ; then
  # python2 installs python2.7 and pip, but pip isn't available in PATH.
  # install it using the get-pip script to ensure it works.
  yum -y install python2
  # Install python-pip with a script instead, similar to what old Ubuntu versions do.
  curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
  sudo python2.7 get-pip.py
  # https://serverfault.com/questions/997896/how-to-enable-powertools-repository-in-centos-8
  yum -y install dnf-plugins-core
  yum config-manager --set-enabled powertools
  yum -y install libyaml-devel
else
  yum -y install python python-pip libyaml-devel
fi

yum clean all && \
rm -r /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUBY_VERSION='2.4.0'
su ${SSH_USERNAME} -c 'command curl -sSL https://rvm.io/mpapis.asc | gpg2 --import - && \
  command curl -sSL https://rvm.io/pkuczynski.asc | gpg2 --import - && \
  curl -L -sSL https://get.rvm.io | bash -s stable'
su ${SSH_USERNAME} -c "/bin/bash -l -c 'rvm autolibs disable && \
  rvm install ${RUBY_VERSION} && \
  rvm ${RUBY_VERSION} do gem install bundler -v 1.17.3 && \
  rvm cleanup all'"
