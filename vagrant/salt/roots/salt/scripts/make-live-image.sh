#!/bin/bash
set -e

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

echo "Building live images............."

arch=$1

livebuild=/var/cache/netboot/livebuild/$1


if ! [ -d $livebuild ]; then
    echo "ERROR: $livebuild absent"
    exit 1
fi


pushd $livebuild

if [ -d /vagrant/cache ]; then
    echo "updating cache"
    rsync -aHX /vagrant/cache ./
    if [ -f /vagrant/cache-bootstrap.tar.gz ]; then
	if ! [ -d cache/bootstrap/ ]; then
	    pushd cache
	    echo "Untarring bootstrap"
	    gzip -cd /vagrant/cache-bootstrap.tar.gz | tar x
	    popd
	fi
    fi
fi


echo "Building live image......"
lb build > live-build.log



echo "Build Complete."
popd
