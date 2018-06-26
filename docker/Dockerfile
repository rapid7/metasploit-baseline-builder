# To build the dev environment.
# docker build -t rapid7/build:payload-lab .

FROM ubuntu:14.04.5
MAINTAINER Jeffrey Martin <jeffrey_martin@rapid7.com> 

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
	apt-get dist-upgrade -y && \
	apt-get -y install software-properties-common && \
	apt-get -y install \
		bison flex gcc gcc-multilib jam make wget git curl \
		gawk libreadline6-dev zlib1g-dev \
		libssl-dev libyaml-dev autoconf unzip \
		libncurses5-dev automake libtool pkg-config \
		libffi-dev libpcap-dev libsqlite3-dev libbz2-dev && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN curl -L https://releases.hashicorp.com/packer/1.2.4/packer_1.2.4_linux_amd64.zip > /root/packer_1.2.4_linux_amd64.zip && \
	cd /usr/local/bin && \
	unzip ~/packer_1.2.4_linux_amd64.zip

ENV JENKINS_HOME /var/jenkins_home
RUN useradd -d "$JENKINS_HOME" -u 1001 -m -s /bin/sh jenkins

# TODO: this needs to run as jenkins user
RUN su jenkins -c "curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash" 
RUN echo 'PATH="/var/jenkins_home/.pyenv/bin:$PATH"' >> /var/jenkins_home/.bash_profile 
RUN echo 'eval "$(pyenv init -)"' >> $JENKINS_HOME/.bash_profile
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> $JENKINS_HOME/.bash_profile

RUN su jenkins -c "/bin/bash -l -c 'pyenv install 2.7.13 && pyenv global 2.7.13'"
RUN su jenkins -c "/bin/bash -l -c 'pip install --upgrade cpe-utils'"
RUN su jenkins -c "/bin/bash -l -c 'pip install --upgrade pyvmomi'"
RUN su jenkins -c "/bin/bash -l -c 'pip install --upgrade python-packer'"
RUN su jenkins -c "/bin/bash -l -c 'pip install --upgrade tqdm'"
RUN su jenkins -c "/bin/bash -l -c 'pip install --upgrade vm-automation'"

VOLUME "$JENKINS_HOME"
RUN chown -R jenkins "$JENKINS_HOME"

