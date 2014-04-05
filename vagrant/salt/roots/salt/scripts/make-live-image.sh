#!/bin/bash
set -e

echo "Make live image started"


echo "Install netboot script initialized............."

pushd /var/lib/tftpboot
gzip -cd /var/cache/netboot/netboot-i386.tar.gz | tar x
chown vagrant:vagrant -R /var/lib/tftpboot
popd


