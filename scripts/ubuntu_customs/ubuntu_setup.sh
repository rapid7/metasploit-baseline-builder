#!/bin/bash

echo 'LC_ALL="en_US.UTF-8"' >> /etc/default/locale

apt-get update && \
	apt-get dist-upgrade -y && \
	apt-get -y install software-properties-common && \
	apt-get -y install \
		gpgv2 python-pip python2.7 \
		bison flex gcc gcc-multilib jam make wget \
		ruby rake bundler git && \
	apt-get -y install openjdk-7-jdk >> /root/installing_java.txt 2>&1 && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

	export JAVA_HOME="/usr/lib/jvm/openjdk-7-jdk"
	export PATH=${PATH}:"'${JAVA_HOME}'/bin"

	RUBY_VERSION='2.3.3'
	su ${SSH_USERNAME} -c 'command curl -sSL https://rvm.io/mpapis.asc | gpg --import - && \
	  command curl -sSL https://rvm.io/pkuczynski.asc | gpg --import - && \
	  curl -L -sSL https://get.rvm.io | bash -s stable'
	su ${SSH_USERNAME} -c "/bin/bash -l -c 'rvm autolibs disable && \
	  rvm install ${RUBY_VERSION} && \
	  rvm ${RUBY_VERSION} do gem install bundler -v 1.17.3 && \
	  rvm cleanup all'"
