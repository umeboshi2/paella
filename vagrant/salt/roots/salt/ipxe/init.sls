# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}
{% set reposdir = '/vagrant/repos' % cachedir %}

include:
  - iscdhcp



cache-ipxe-dhcpd-files-gist-repos:
  git.latest:
    - name: https://gist.github.com/robinsmidsrod/4008017.git
    - target: {{ reposdir }}/dchpd-conf-ipxe
    - user: {{ user }}
    - rev: 17a55e4de91fcae87f8b90b6db4890c27c15b0f6
  
cache-ipxe-git-repos:
  git.latest:
    - name: git://git.ipxe.org/ipxe.git
    - target: {{ reposdir }}/ipxe
    - user: {{ user }}
    - rev: d38bac05e7d0eb67fc19f3532a6b4fa00804106e
      
  
