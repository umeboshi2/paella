# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}


# add this script to debian-archive-keyring package
/home/vagrant/add-paella-insecure:
  file.managed:
    - source: salt://debrepos/add-paella-insecure
    - user: {{ user }}
    - group: {{ group }}
    - mode: 644

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

