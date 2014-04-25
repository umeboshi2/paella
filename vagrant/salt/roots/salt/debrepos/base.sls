# -*- mode: yaml -*-

<% user = pillar['paella_user'] %>
<% group = pillar['paella_group'] %>


reprepro:
  pkg:
    - installed

# use germinate to help build
# small partial debian repository
# capable of debootstrap
germinate:
  pkg:
    - installed


# This fake-random-source state is
# is to quickly generate gpg keys
# to sign the package repository.
# The keys made with this should 
# not be used outside the vagrant 
# environment.

# There is no more fake-random-source state.
# Instead, a pregenerated set of keys will 
# be used in the vagrant environment.

#fake-random-source:
#  pkg.installed:
#    - name: rng-tools
#  service:
#    - running
#    - name: rng-tools
#  file.managed:
#    - name: /etc/default/rng-tools
#    - source: salt://debrepos/rng-tools

# add this script to debian-archive-keyring package
/home/vagrant/add-paella-insecure:
  file.managed:
    - source: salt://debrepos/add-paella-insecure
    - user: ${user}
    - group: ${group}
    - mode: 644



#build-keyring-package:
#  cmd.script:
#    - source: salt://scripts/build-keyring-package.sh
#    - unless: test -d /home/vagrant/workspace
#    - user: ${user}
#    - group: ${group}
#    - requires:
#      - cmd: update-debrepos

