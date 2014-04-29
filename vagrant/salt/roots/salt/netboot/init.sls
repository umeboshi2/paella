# -*- mode: yaml -*-


# debian installer files for tftpboot

/var/lib/tftpboot/installer:
  file.directory:
    - makedirs: True

# FIXME make better names for multi architecture support
<% checksums = pillar['debian_installer_i386_checksums'] %>


/var/lib/tftpboot/installer/i386/initrd.gz:
  file.managed:
    - source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/current/images/netboot/debian-installer/i386/initrd.gz
    - source_hash: ${checksums['initrd']}

/var/lib/tftpboot/installer/i386/linux:
  file.managed:
    - source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/current/images/netboot/debian-installer/i386/linux
    - source_hash: ${checksums['linux']}

/var/lib/tftpboot/installer/i386/installer.cfg:
  file.managed:
    - source: salt://netboot/installer.cfg
    - template: mako

/var/lib/tftpboot/pxelinux.cfg/default:
  file.managed:
    - source: salt://netboot/pxelinux-cfg

/var/lib/tftpboot/splash.png:
  file.managed:
    - source: salt://netboot/splash.png

/var/lib/tftpboot/paella-splash.png:
  file.managed:
    - source: salt://netboot/paella-splash.png

# FIXME:  This isn't really needed anymore
preseed-example:
  file.managed:
    - name: /var/www/preseeds/preseed-example
    - source: salt://netboot/preseed-example
    - makedirs: True
    - template: mako


#####################################

# debian live
# the local debian repository must be ready

include:
  - debrepos
  - tftpd



/var/cache/netboot/livebuild:
  file.directory:
    - user: root
    - group: root
    - makedirs: True


# FIXME:  These scripts aren't really that great and
# are not really good for salt states.  They will 
# generally work to help build the basic development
# environment, but better methods should be used to 
# build and manage live images in the production 
# environment.
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


copy-chainloader:
  cmd.run:
    - name: cp -a /usr/lib/syslinux/chain.c32 /var/lib/tftpboot
    - unless: test -r /var/lib/tftpboot/chain.c32
    - requires:
      - file: /var/lib/tftpboot

# FIXME:  This command always runs!  Figure out when it's
# necessary from the other states.
vagrant-owns-tftpboot:
  cmd.run:
    - name: chown -R vagrant:vagrant /var/lib/tftpboot
    - require:
      - cmd: install-tftpboot-files
      - cmd: copy-chainloader

