#!/bin/bash

echo 'LC_ALL="en_US.UTF-8"' >> /etc/default/locale

yum -y install \
  gcc gpg openssl-devel bzip2-devel \
  gcc-c++ patch readline readline-devel zlib zlib-devel \
  libyaml-devel libffi-devel make \
  bzip2 autoconf automake libtool bison sqlite-devel \
  python-pip python curl gnupg2 && \
yum -y install java-1.8.0-openjdk.x86_64 && \
yum clean && \
rm -r /var/lib/apt/lists/* /tmp/* /var/tmp/*

  RUBY_VERSION='2.4.0'
    su ${SSH_USERNAME} -c 'command curl -sSL https://rvm.io/mpapis.asc | gpg2 --import - && \
  	  command curl -sSL https://rvm.io/pkuczynski.asc | gpg2 --import - && \
  	  curl -L -sSL https://get.rvm.io | bash -s stable'
    su ${SSH_USERNAME} -c "/bin/bash -l -c 'rvm autolibs disable && \
    	rvm install ${RUBY_VERSION} && \
    	rvm ${RUBY_VERSION} do gem install bundler -v 1.17.3 && \
      rvm cleanup all'"
