#!/bin/bash


echo "Preparing salt roots"

if ! [ -d /vagrant/repos/formulae ]; then
    repo=https://github.com/umeboshi2/saltstack-formulae.git
    echo "Cloning $repo"
    if ! [ -d /vagrant/repos/ ]; then
	mkdir /vagrant/repos/
    fi
    git clone $repo /vagrant/repos/formulae
fi

if ! [ -d /vagrant/repos/paella-states ]; then
    repo=https://github.com/umeboshi2/paella-states.git
    echo "Cloning $repo"
    if ! [ -d /vagrant/repos/ ]; then
	mkdir /vagrant/repos/
    fi
    git clone $repo /vagrant/repos/paella-states
fi

echo "Finished with prepare-salt-roots."

