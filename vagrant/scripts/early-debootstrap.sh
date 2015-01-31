#!/bin/bash
DBCHROOT=/var/cache/netboot/livebuild/amd64/chroot

if [ -d $DBCHROOT ]; then
    echo "$DBCHROOT already exists......."
    exit 0
fi

mkdir -p $DBCHROOT
apt-get -y update
apt-get -y install debootstrap cdebootstrap

cdebootstrap --download-only wheezy /var/cache/netboot/livebuild/amd64/chroot http://slartibardfast.gtlib.gatech.edu/debian

