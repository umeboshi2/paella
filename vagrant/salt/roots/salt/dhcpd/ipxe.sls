# -*- mode: yaml -*-

include:
  - default
  - network
  - dhcpd.base



<% cachedir = '/vagrant/vagrant/cache' %>
<% reposdir = '%s/repos' % cachedir %>
cache-ipxe-git-repos:
  git.latest:
    - name: git://git.ipxe.org/ipxe.git
    - target: ${reposdir}/ipxe
    - user: ${pillar['paella_user']}
    #- rev: 
  
