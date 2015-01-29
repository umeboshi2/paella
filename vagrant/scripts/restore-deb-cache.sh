#!/bin/bash
set -e
NAME=squid-deb-proxy
SRCDIR=/vagrant/cache
DESTDIR=/var/cache

if [ -d $DESTDIR/$NAME ]; then
    echo "${NAME} directory already present, skipping restore."
    exit 0
fi

if ! [ -d $SRCDIR/$NAME ]; then
    echo "No cache backup found, exiting."
    exit 0
fi

if ! [ -x /usr/bin/rsync ]; then
    echo "Installing rsync"
    apt-get -y update
    apt-get -y install rsync
fi

echo "Restoring cache to ${DESTDIR}/squid-deb-proxy"
rsync -a $SRCDIR/$NAME $DESTDIR/
echo "Changing ownership to proxy:proxy"
chown -R proxy:proxy $DESTDIR/$NAME

exit 0
