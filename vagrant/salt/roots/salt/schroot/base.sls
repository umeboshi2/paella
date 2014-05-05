# -*- mode: yaml -*-

schroot-packages:
  pkg.installed:
    - pkgs:
      - schroot

schroot-parent-directory:
  file.directory:
    - name: /srv/roots


schroot.conf:
  file.managed:
    - name: /etc/schroot/schroot.conf
    - source: salt://schroot/schroot.conf
    - template: mako

