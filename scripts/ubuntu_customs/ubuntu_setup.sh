#!/bin/bash

echo 'LC_ALL="en_US.UTF-8"' >> /etc/default/locale

apt-get update && \
	apt-get dist-upgrade -y && \
	apt-get -y install software-properties-common && \
	dpkg --add-architecture i386 && \
	add-apt-repository ppa:openjdk-r/ppa && \
	apt-add-repository ppa:brightbox/ruby-ng && \
	apt-get clean && \
  apt-get update && \
	sudo apt-get -y install \
		gpgv2 apache2 php5 libapache2-mod-php5 python-pip python2.7 \
		bison flex gcc gcc-multilib jam make wget \
		ruby2.4 rake bundler git \
		default-jdk && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
