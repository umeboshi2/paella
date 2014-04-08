#!/bin/bash
set -e

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

echo "Moving tftpboot files............."

livebuild=/var/cache/netboot/livebuild

tftpbootdir=/var/lib/tftpboot


if ! [ -d $livebuild ]; then
    echo "ERROR: $livebuild not present"
    exit 1
fi

tftpdir=$livebuild/tftpboot

rsync -avHX $tftpdir/ $tftpbootdir/live/

echo "Rsync complete."

for filename in pxelinux.0 vesamenu.c32 ; do
    if ! [ -r $tftpbootdir/$filename ]; then
	echo "Linking $filename"
	ln $tftpbootdir/live/$filename $tftpbootdir/$filename
    fi
done

for num in 1 2; do
    for f in vmlinuz$num initrd$num.img ; do
	if ! [ -r $tftpbootdir/live/$f ] ; then
	    echo "Linking $tftpbootdir/live/$f"
	    ln $tftpbootdir/live/live/$f $tftpbootdir/live/$f
	fi
    done
done

touch $tftpbootdir/.ready
