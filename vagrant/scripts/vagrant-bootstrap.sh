#!/bin/bash

DEBMIRROR=http://ftp.us.debian.org/debian
DEBDIST=wheezy
SALTBRANCH=2014-07
#SALTBRANCH=2014-01

if [ -x /usr/bin/salt-minion ]; then
    echo "Salt Minion already installed, skipping....."
    exit 0
fi

if [ -d /vagrant/vagrant/debrepos/debian/dists ]; then
    apt-key add /vagrant/vagrant/salt/roots/salt/debrepos/keys/paella-insecure-pub.gpg
    echo "deb file:///vagrant/vagrant/debrepos/debian wheezy main contrib non-free" > /etc/apt/sources.list
    echo "deb $DEBMIRROR ${DEBDIST} main contrib non-free" >> /etc/apt/sources.list
    echo "deb-src $DEBMIRROR ${DEBDIST} main contrib non-free" >> /etc/apt/sources.list
    echo >> /etc/apt/sources.list
    if [ -d /vagrant/vagrant/debrepos/security ]; then
	echo "deb file:///vagrant/vagrant/debrepos/security ${DEBDIST}/updates main contrib non-free" >> /etc/apt/sources.list
	echo "deb http://security.debian.org/ ${DEBDIST}/updates main contrib non-free" >> /etc/apt/sources.list
	echo >> /etc/apt/sources.list
    fi
    if [ -d /vagrant/vagrant/debrepos/salt ]; then
	echo "deb file:///vagrant/vagrant/debrepos/salt ${DEBDIST}-saltstack-${SALTBRANCH} main" >> /etc/apt/sources.list
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
    echo "deb http://debian.saltstack.com/debian ${DEBDIST}-saltstack-${SALTBRANCH} main" \
	> /etc/apt/sources.list.d/salt.list
fi

apt-get -y update
apt-get -y install python-git salt-minion

if ! [ -d /vagrant/repos/formulae ]; then
    if ! [ -d /vagrant/repos/ ]; then
	mkdir /vagrant/repos/
    fi
    git clone https://github.com/umeboshi2/saltstack-formulae.git /vagrant/repos/formulae
fi

if ! [ -d /vagrant/repos/paella-states ]; then
    if ! [ -d /vagrant/repos/ ]; then
	mkdir /vagrant/repos/
    fi
    git clone https://github.com/umeboshi2/paella-states.git /vagrant/repos/paella-states
fi

echo "Finished with vagrant bootstrap."

