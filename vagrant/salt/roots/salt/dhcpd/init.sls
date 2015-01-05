# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user') %}
{% set group = pget('paella:paella_group') %}

include:
  - default
  - network
  - dhcpd.base



{% set cachedir = '/vagrant/vagrant/cache' %}
{% set reposdir = '%s/repos' % cachedir %}
cache-ipxe-dhcpd-files-gist-repos:
  git.latest:
    - name: https://gist.github.com/robinsmidsrod/4008017.git
    - target: {{ reposdir }}/dchpd-conf-ipxe
    - user: {{ user }}
    - rev: 17a55e4de91fcae87f8b90b6db4890c27c15b0f6
  
isc-dhcp-server:
  service:
    - running
    - require:
        - pkg: isc-dhcp-server-package
        - file: /etc/dhcp/dhcpd.conf
        - file: /etc/default/isc-dhcp-server
        - file: /etc/network/interfaces
        - cmd: enable-eth1
    - watch:
        - file: /etc/dhcp/dhcpd.conf
        - file: /etc/default/isc-dhcp-server
        - file: /etc/network/interfaces


