#!/bin/bash
set -e

echo "Install netboot script initialized............."

pushd /var/lib/tftpboot
if ! [ -f pxelinux.0 ]; then
    gzip -cd /var/cache/netboot/netboot-i386.tar.gz | tar x
fi
chown vagrant:vagrant -R /var/lib/tftpboot
popd


