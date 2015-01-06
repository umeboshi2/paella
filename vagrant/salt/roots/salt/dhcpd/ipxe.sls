# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}

include:
  - default.pkgsets
  - network
  - dhcpd.base



{% set cachedir = '/vagrant/vagrant/cache' %}
{% set reposdir = '%s/repos' % cachedir %}
cache-ipxe-git-repos:
  git.latest:
    - name: git://git.ipxe.org/ipxe.git
    - target: {{ reposdir }}/ipxe
    - user: {{ user }}
    #- rev: 
  
