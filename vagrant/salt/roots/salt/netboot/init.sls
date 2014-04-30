# -*- mode: yaml -*-

include:
  - debrepos
  - tftpd
  - netboot.debian-installer



/var/lib/tftpboot/pxelinux.cfg/default:
  file.managed:
    - source: salt://netboot/pxelinux-cfg
    - template: mako

/var/lib/tftpboot/splash.png:
  file.managed:
    - source: salt://netboot/splash.png

/var/lib/tftpboot/paella-splash.png:
  file.managed:
    - source: salt://netboot/paella-splash.png


#####################################

# debian live
# the local debian repository must be ready

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


# copy syslinux files to tftpboot
%for filename in ['chain.c32', 'gpxelinux.0', 'memdisk']:
copy-${filename}:
  cmd.run:
    - name: cp -a /usr/lib/syslinux/${filename} /var/lib/tftpboot
    - unless: test -r /var/lib/tftpboot/${filename}
    - requires:
      - file: /var/lib/tftpboot
%endfor

# FIXME:  This command always runs!  Figure out when it's
# necessary from the other states.
vagrant-owns-tftpboot:
  cmd.run:
    - name: chown -R vagrant:vagrant /var/lib/tftpboot
    - require:
      - cmd: install-tftpboot-files
      %for filename in ['chain.c32', 'gpxelinux.0', 'memdisk']:
      - cmd: copy-${filename}
      %endfor


