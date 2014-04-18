# -*- mode: yaml -*-

<% user = pillar['paella_user'] %>
<% group = pillar['paella_group'] %>

/srv/debrepos/paella.gpg:
  file.managed:
    - source: salt://debrepos/keys/paella-insecure-pub.gpg

/home/vagrant/paella-insecure-sec.gpg:
  file.managed:
    - source: salt://debrepos/keys/paella-insecure-sec.gpg
    - user: ${user}
    - group: ${group}
    - mode: 400

/home/vagrant/wheezy-stable.gpg:
  file.managed:
    - source: salt://debrepos/keys/wheezy-stable.gpg
    - user: ${user}
    - group: ${group}
    - mode: 644

/home/vagrant/wheezy-automatic.gpg:
  file.managed:
    - source: salt://debrepos/keys/wheezy-automatic.gpg
    - user: ${user}
    - group: ${group}
    - mode: 644

/home/vagrant/saltrepos.gpg:
  file.managed:
    - source: salt://debrepos/keys/saltrepos.gpg
    - user: ${user}
    - group: ${group}
    - mode: 644

import-insecure-gpg-key:
  cmd.run:
    - name: gpg --import paella-insecure-sec.gpg
    - unless: gpg --list-key 62804AE5
    - user: ${user}
    - group: ${group}
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/paella-insecure-sec.gpg

import-wheezy-automatic-key:
  cmd.run:
    - name: gpg --import wheezy-automatic.gpg
    - unless: gpg --list-key 46925553
    - user: ${user}
    - group: ${group}
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/wheezy-automatic.gpg


import-wheezy-stable-key:
  cmd.run:
    - name: gpg --import wheezy-stable.gpg
    - unless: gpg --list-key 65FFB764
    - user: ${user}
    - group: ${group}
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/wheezy-stable.gpg

import-saltrepos-key:
  cmd.run:
    - name: gpg --import saltrepos.gpg
    - unless: gpg --list-key F2AE6AB9
    - user: ${user}
    - group: ${group}
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/saltrepos.gpg

keyring-ready:
  cmd.run:
    - name: echo "Keyring Ready"
    - unless: gpg --list-key 65FFB764
    - user: ${user}
    - group: ${group}
    - cwd: /home/vagrant
    - requires:
      - cmd: import-wheezy-stable-key
      - cmd: import-wheezy-automatic-key
      - cmd: import-insecure-gpg-key
      - cmd: import-saltrepos-key


# This key goes into the web server's
# document root so that the early command
# can replace the archive.gpg key in the
# debian-installer system
create-binary-pubkey:
  cmd.run:
    - name: gpg --export 62804AE5 > /srv/debrepos/paella.bin.gpg
    - unless: test -r /srv/debrepos/paella.bin.gpg
    - user: ${user}
    - requires:
      - cmd: keyring-ready

