# -*- mode: yaml -*-


/usr/local/bin/build-live-images:
  file.managed:
    - source: salt://scripts/make-live-image.sh
    - user: root
    - group: root
    - mode: 755

/usr/local/bin/build-keyring-package:
  file.managed:
    - source: salt://scripts/build-keyring-package.sh
    - user: root
    - group: root
    - mode: 755
  



# These scripts are used during development
# and have limited usefulness otherwise.
/usr/local/bin/recreate-paella-database:
  file.managed:
    - source: salt://files/recreate-paella-database
    - mode: 755
    - template: mako


/usr/local/bin/destroy-livebuild-states:
  file.managed:
    - source: salt://scripts/destroy-livebuild-states.sh
    - mode: 755

/usr/local/bin/generate-gpg-key:
  file.managed:
    - source: salt://files/generate-gpg-key
    - user: root
    - group: root
    - mode: 755

