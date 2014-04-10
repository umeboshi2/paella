#!/bin/bash
set -e

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

echo "Building live images............."

echo "Merging config"

livebuild=/var/cache/netboot/livebuild

if ! [ -d $livebuild ]; then
    echo "Creating $livebuild"
    mkdir -p $livebuild
fi

echo "Syncing work tree with $livebuild/config"
rsync -avHX /srv/livebuild/config/ $livebuild/config/

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
lb build


echo "Build Complete."
popd