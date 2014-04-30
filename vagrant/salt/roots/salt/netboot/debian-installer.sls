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

# FIXME:  This isn't really needed anymore
preseed-example:
  file.managed:
    - name: /var/www/preseeds/preseed-example
    - source: salt://netboot/preseed-example
    - makedirs: True
    - template: mako


