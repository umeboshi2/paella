#!/bin/bash
set -e

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi


# remove from tftpboot selectively to
# keep from dowloading debian netboot files
# unecessarily
rm /var/lib/tftpboot/* -f || true
rm /var/lib/tftpboot/live -fr
rm /var/lib/tftpboot/pxelinux.cfg -fr
rm /var/lib/tftpboot/.ready -f

# remove the filesystem
rm /srv/debian-live -fr

# remove the build area
rm /var/cache/netboot/livebuild -fr
