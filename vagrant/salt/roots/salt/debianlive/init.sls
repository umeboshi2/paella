# -*- mode: yaml -*-

live-build:
  pkg:
    - installed


# This is modified to accept a url with the _KEY variable
/usr/lib/live/build/bootstrap_archive-keys:
  file.managed:
    - source: salt://debianlive/bootstrap_archive-keys
    - user: root
    - group: root
    - mode: 755


livebuild-configdir:
  file.directory:
    - name: /var/cache/netboot/livebuild/config
    - user: root
    - group: root
    - mode: 755
    - makedirs: True


%for cfile in ['binary', 'bootstrap', 'chroot', 'common', 'source']:
livebuild-config-${cfile}:
  file.managed:
    - name: /var/cache/netboot/livebuild/config/${cfile}
    - source: salt://debianlive/templates/${cfile}
    - template: mako
%endfor
