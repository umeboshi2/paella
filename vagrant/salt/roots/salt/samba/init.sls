# -*- mode: yaml -*-

samba-support-packages:
  pkg.installed:
    - pkgs:
      - smbclient

samba-server:
  pkg.installed:
    - name: samba
    - requires:
      - pkg: samba-support-packages

  service:
    - name: samba
    - running
    #- watch:
    #  - file: /etc/apache2/paella.wsgi
    #  - file: /etc/apache2/conf.d/debrepos
    #  - file: /etc/apache2/conf.d/paella
  

