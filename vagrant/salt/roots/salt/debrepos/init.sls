# -*- mode: yaml -*-

reprepro:
  pkg:
    - latest

# This fake-random-source state is
# is to quickly generate gpg keys
# to sign the package repository.
# The keys made with this should 
# not be used outside the vagrant 
# environment.
fake-random-source:
  pkg.latest:
    - name: rng-tools
  service:
    - running
    - name: rng-tools
  file.managed:
    - name: /etc/default/rng-tools
    - source: salt://debrepos/rng-tools


/srv/debrepos/debian/conf:
  file.directory:
    - makedirs: True


i386-udeb-list-upstream:
  file.managed:
    - name: /srv/debrepos/debian/conf/i386-udeb-list-upstream
    - source: http://ftp.us.debian.org/debian/dists/wheezy/main/installer-i386/current/images/udeb.list
    - source_hash: sha256=15ce82c5c843a4d752932e05596a3ae22d7575e4b713a27a4367a7d2697a5777


cat /srv/debrepos/debian/conf/i386-udeb-list-upstream | awk '{print $1 "\tinstall"}' > /srv/debrepos/debian/conf/i386-udeb-list:
  cmd.run:
    - requires:
        - file: i386-udeb-list-upstream
    - creates: /srv/debrepos/debian/conf/i386-udeb-list


/srv/debrepos/debian/conf/updates:
  file.managed:
    - source: salt://debrepos/updates

local-packages:
  cmd.run:
    - creates: /srv/debrepos/debian/conf/local-packages
    - name: dpkg --get-selections > /srv/debrepos/debian/conf/local-packages
