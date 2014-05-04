#!/bin/bash
set -e

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

echo "Moving live images............."

livebuild=/var/cache/netboot/livebuild/${ARCH}


if ! [ -d $livebuild ]; then
    echo "ERROR: $livebuild not present"
    exit 1
fi

bindir=$livebuild/binary


rsync -avHX $bindir/ /srv/debian-live/${ARCH}/

echo "Rsync complete."
