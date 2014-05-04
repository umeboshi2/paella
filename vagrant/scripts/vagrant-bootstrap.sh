#!/bin/bash

if [ -x /usr/bin/salt-minion ]; then
    echo "Salt Minion already installed, skipping....."
    exit 0
fi

if [ -d /vagrant/vagrant/debrepos/debian/dists ]; then
    apt-key add /vagrant/vagrant/debrepos/paella.gpg
    echo "deb file:///vagrant/vagrant/debrepos/debian wheezy main contrib non-free" > /etc/apt/sources.list
    echo "deb http://mirrors.kernel.org/debian wheezy main contrib non-free" >> /etc/apt/sources.list
    echo "deb-src http://mirrors.kernel.org/debian wheezy main contrib non-free" >> /etc/apt/sources.list
    echo >> /etc/apt/sources.list
    if [ -d /vagrant/vagrant/debrepos/security ]; then
	echo "deb file:///vagrant/vagrant/debrepos/security wheezy/updates main contrib non-free" >> /etc/apt/sources.list
	echo "deb http://security.debian.org/ wheezy/updates main contrib non-free" >> /etc/apt/sources.list
	echo >> /etc/apt/sources.list
    fi
    if [ -d /vagrant/vagrant/debrepos/salt ]; then
	echo "deb file:///vagrant/vagrant/debrepos/salt wheezy-saltstack main" >> /etc/apt/sources.list
	echo >> /etc/apt/sources.list
    fi
fi



key_url=http://debian.saltstack.com/debian-salt-team-joehealy.gpg.key
key_fingerprint="102E 2FE7 D514 1DBD 12B2  60FC B09E 40B0 F2AE 6AB9"

if ! apt-key --keyring /etc/apt/trusted.gpg finger | grep "$key_fingerprint"; then
    wget -O - $key_url | apt-key add -
fi

if ! [ -f /etc/apt/sources.list.d/salt.list ]; then
    echo "adding sources list for salt"
    echo "deb http://debian.saltstack.com/debian wheezy-saltstack main" \
	> /etc/apt/sources.list.d/salt.list
fi

apt-get -y update
apt-get -y install salt-minion

# FIXME (do I need this? what was I doing?)
if [ -d /etc/salt ]; then
    if [ -d /etc/salt.orig ]; then
	echo "removing /etc/salt"
	rm -rf /etc/salt
    else
	echo "moving config to /etc/salt.orig"
	mv /etc/salt /etc/salt.orig
    fi
fi


echo "Finished with vagrant bootstrap."

