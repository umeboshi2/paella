#!/bin/bash
set -e

echo "Install netboot script initialized............."

pushd /var/lib/tftpboot
gzip -cd /var/cache/netboot/netboot-i386.tar.gz | tar x
chown vagrant:vagrant -R /var/lib/tftpboot
popd

