#!/bin/bash

apt-get update && \
	apt-get dist-upgrade -y && \
	apt-get -y install software-properties-common && \
	dpkg --add-architecture i386 && \
	apt-get update && \
	apt-get -y install \
		gpgv2 php7.0-cli python python3 \
		bison flex gcc gcc-multilib jam make wget \
		ruby rake bundler git \
		maven openjdk-8-jdk curl \
		gawk libreadline6-dev zlib1g-dev p7zip-full \
		libssl-dev libyaml-dev libsqlite3-dev \
		sqlite3 autoconf libgmp-dev libgdbm-dev \
		libncurses5-dev automake libtool pkg-config \
		libffi-dev libpcap-dev nmap && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
	wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
        apt-get update && \
        apt-get upgrade

DB_CREATE="CREATE USER msf WITH PASSWORD 'pass123'; ALTER USER msf CREATEDB; CREATE DATABASE metasploit_pro_development;"

apt-get -y install postgresql-9.6 postgresql-server-dev-9.6 linux-libc-dev tzdata && \
	sleep 5 && service postgresql start && \
	cd /var/lib/postgresql && \
	echo ${DB_CREATE} | sudo -u postgres psql 


su ${SSH_USERNAME} -c 'mkdir ~/rapid7 && \
  cd ~/rapid7 && \
  git clone https://github.com/rapid7/metasploit-framework && \
  mkdir -p test_artifacts/test_scripts'

RUBY_VERSION=`cat /home/${SSH_USERNAME}/rapid7/metasploit-framework/.ruby-version`
su ${SSH_USERNAME} -c "curl -sSL https://rvm.io/mpapis.asc | gpg --import -"
su ${SSH_USERNAME} -c "/bin/bash -l -c 'curl -sSL https://get.rvm.io | bash -s stable'"
su ${SSH_USERNAME} -c "/bin/bash -l -c 'rvm autolibs disable && \
  rvm install ${RUBY_VERSION} && \
  rvm ${RUBY_VERSION} do gem install bundler --no-rdoc --no-ri && \
  rvm cleanup all'"

su ${SSH_USERNAME} -c 'git remote add upstream https://github.com/rapid7/metasploit-framework && \
  /bin/bash -l -c "ruby tools/dev/add_pr_fetch.rb" && \
  git config --global user.name   "Metasploit Tesing Lab User" && \
  git config --global user.email  "IamNotReal@findthe.robot" && \
  git config --global github.user "master"'

su ${SSH_USERNAME} -c "curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash"

ADD_BASH='export PATH="~/.pyenv/bin:$PATH"'
su ${SSH_USERNAME} -c "echo '${ADD_BASH}' >> ~/.bash_profile"
ADD_BASH='eval "$(pyenv init -)"'
su ${SSH_USERNAME} -c "echo '${ADD_BASH}' >> ~/.bash_profile"
ADD_BASH='eval "$(pyenv virtualenv-init -)"'
su ${SSH_USERNAME} -c "echo '${ADD_BASH}' >> ~/.bash_profile"
su ${SSH_USERNAME} -c "/bin/bash -l -c 'pyenv install 2.7.13 && pyenv global 2.7.13'"

su ${SSH_USERNAME} -c '/bin/bash -l -c "cd ~/rapid7/metasploit-framework && \
  gem install bundler --no-doc --no-ri && \
  bundle install"'

