# -*- mode: yaml -*-

/usr/local/bin/build-live-images:
  file.managed:
    - source: salt://files/build-live-images
    - user: root
    - group: root
    - mode: 755

/usr/local/bin/backup-livebuild-cache:
  file.managed:
    - source: salt://files/backup-livebuild-cache
    - user: root
    - group: root
    - mode: 755

/usr/local/bin/generate-gpg-key:
  file.managed:
    - source: salt://files/generate-gpg-key
    - user: root
    - group: root
    - mode: 755

/usr/local/bin/setup-local-debrepos:
  file.managed:
    - source: salt://files/setup-local-debrepos
    - user: root
    - group: root
    - mode: 755
  

/etc/network/interfaces:
  file.managed:
    - source: salt://files/network-interfaces
    - user: root
    - group: root
    - mode: 644


/usr/local/bin/install-netboot:
  file.absent
