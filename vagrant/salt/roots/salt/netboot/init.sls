# -*- mode: yaml -*-

# debian installer files for tftpboot

/var/lib/tftpboot/installer:
  file.directory:
    - makedirs: True

/var/lib/tftpboot/installer/i386/initrd.gz:
  file.managed:
    - source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/20130613+deb7u1+b2/images/netboot/debian-installer/i386/initrd.gz
    - source_hash: sha256=ec9cd8f2f4113b6cea59165672e9a41f676ce1fe47643d8a57933d672245bd93

/var/lib/tftpboot/installer/i386/linux:
  file.managed:
    - source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/20130613+deb7u1+b2/images/netboot/debian-installer/i386/linux
    - source_hash: sha256=b60550692a0528b856f2dac883e79ec8388d392413a0954873c31f89172e0a59

/var/lib/tftpboot/installer/i386/installer.cfg:
  file.managed:
    - source: salt://netboot/installer.cfg

/var/lib/tftpboot/pxelinux.cfg/default:
  file.managed:
    - source: salt://netboot/pxelinux-cfg

/var/lib/tftpboot/splash.png:
  file.managed:
    - source: salt://netboot/splash.png

preseed-example:
  file.managed:
    - name: /var/www/preseeds/preseed-example
    - source: salt://netboot/preseed-example
    - makedirs: True

#####################################

# debian live

# the local debian repository must be ready

include:
  - debrepos


/var/cache/netboot/livebuild:
  file.directory:
    - user: root
    - group: root
    - makedirs: True

build-live-images:
  cmd.script:
    - require:
      - sls: debrepos
      - file: /var/cache/netboot/livebuild
    - unless: test -r /var/cache/netboot/livebuild/binary.netboot.tar
    - source: salt://scripts/make-live-image.sh

install-binary-filesystem:
  cmd.script:
    - require:
      - cmd: build-live-images
    - unless: test -r /srv/debian-live/live/filesystem.squashfs
    - source: salt://scripts/install-netboot-filesystem.sh

install-tftpboot-files:
  cmd.script:
    - require:
      - cmd: install-binary-filesystem
    - unless: test -r /var/lib/tftpboot/.ready
    - source: salt://scripts/install-tftpboot-files.sh

install-netboot:
  cmd.script:
    - require:
      - file: /var/lib/tftpboot
      - sls: debrepos
    - source: salt://scripts/install-netboot.sh
    - user: root
    - group: root
    - shell: /bin/bash

