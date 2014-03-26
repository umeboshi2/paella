#!/bin/bash

if ! apt-key --keyring /etc/apt/trusted.gpg finger | grep "5474 5E6F 55BB BD92 6373  0B26 45CE 3377 14BB F15F"; then
    wget -O - http://debrepos.littledebian.org/littledebian.key | apt-key add -
fi

if ! [ -f /etc/apt/sources.list.d/salt.list ]; then
    echo "adding sources list for salt"
    echo "deb http://debrepos.littledebian.org/salt wheezy-saltstack main" \
	> /etc/apt/sources.list.d/salt.list
fi

# update package list and upgrade system
#apt-get -y update
#apt-get -y upgrade

# install salt-minion
#apt-get -y install salt-minion

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

