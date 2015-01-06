# -*- mode: yaml -*-

schroot-parent-directory:
  file.directory:
    - name: /srv/roots


schroot.conf:
  file.managed:
    - name: /etc/schroot/schroot.conf
    - source: salt://schroot/schroot.conf
    - template: jinja

