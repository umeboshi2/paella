# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}


/srv/debrepos/paella.gpg:
  file.managed:
    - source: salt://debrepos/keys/paella-insecure-pub.gpg

/home/vagrant/paella-insecure-sec.gpg:
  file.managed:
    - source: salt://debrepos/keys/paella-insecure-sec.gpg
    - user: {{ user }}
    - group: {{ group }}
    - mode: 400

/home/vagrant/saltrepos.gpg:
  file.managed:
    - source: salt://debrepos/keys/saltrepos.gpg
    - user: {{ user }}
    - group: {{ group }}
    - mode: 644

import-insecure-gpg-key:
  cmd.run:
    - name: gpg --import paella-insecure-sec.gpg
    - unless: gpg --list-key 62804AE5
    - user: {{ user }}
    - group: {{ group }}
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/paella-insecure-sec.gpg

import-saltrepos-key:
  cmd.run:
    - name: gpg --import saltrepos.gpg
    - unless: gpg --list-key F2AE6AB9
    - user: {{ user }}
    - group: {{ group }}
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/saltrepos.gpg

{% if pget('paella:make_local_partial_mirror', False) %}        
/home/vagrant/wheezy-stable.gpg:
  file.managed:
    - source: salt://debrepos/keys/wheezy-stable.gpg
    - user: {{ user }}
    - group: {{ group }}
    - mode: 644

/home/vagrant/wheezy-automatic.gpg:
  file.managed:
    - source: salt://debrepos/keys/wheezy-automatic.gpg
    - user: {{ user }}
    - group: {{ group }}
    - mode: 644

import-wheezy-automatic-key:
  cmd.run:
    - name: gpg --import wheezy-automatic.gpg
    - unless: gpg --list-key 46925553
    - user: {{ user }}
    - group: {{ group }}
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/wheezy-automatic.gpg


import-wheezy-stable-key:
  cmd.run:
    - name: gpg --import wheezy-stable.gpg
    - unless: gpg --list-key 65FFB764
    - user: {{ user }}
    - group: {{ group }}
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/wheezy-stable.gpg

/home/vagrant/ubuntu-automatic.gpg:
  file.managed:
    - source: salt://debrepos/keys/ubuntu-automatic.gpg
    - user: {{ user }}
    - group: {{ group }}
    - mode: 644
      
import-ubuntu-automatic-key:
  cmd.run:
    - name: gpg --import ubuntu-automatic.gpg
    - unless: gpg --list-key C0B21F32
    - user: {{ user }}
    - group: {{ group }}
    - cwd: /home/vagrant
    - requires:
      - file: /home/vagrant/ubuntu-automatic.gpg
{% endif %}

keyring-ready:
  cmd.run:
    - name: echo "Keyring Ready"
    - unless: gpg --list-key 65FFB764
    - user: {{ user }}
    - group: {{ group }}
    - cwd: /home/vagrant
    - requires:
      - cmd: import-insecure-gpg-key
      - cmd: import-saltrepos-key
      {%- if pget('paella:make_local_partial_mirror', False) %}        
      - cmd: import-wheezy-stable-key
      - cmd: import-wheezy-automatic-key
      - cmd: import-ubuntu-automatic-key
      {% endif %}


# This key goes into the web server's
# document root so that the early command
# can replace the archive.gpg key in the
# debian-installer system
create-binary-pubkey:
  cmd.run:
    - name: gpg --export 62804AE5 > /srv/debrepos/paella.bin.gpg
    - unless: test -r /srv/debrepos/paella.bin.gpg
    - user: {{ user }}
    - requires:
      - cmd: keyring-ready

add-local-apt-key:
  cmd.run:
    - name: apt-key add /srv/debrepos/paella.gpg
    - unless: apt-key list | grep 62804AE5
    - require:
      - cmd: keyring-ready
