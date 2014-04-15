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
    - require:
      - file: livebuild-configdir
%endfor

/var/cache/netboot/livebuild/config/archives:
  file.directory:
    - mode: 755
    - makedirs: True

/var/cache/netboot/livebuild/config/package-lists:
  file.directory:
    - mode: 755
    - makedirs: True

livebuild-paella-apt-chroot:
  file.managed:
    - name: /var/cache/netboot/livebuild/config/archives/paella.list.chroot
    - source: salt://debianlive/paella.list.chroot
    - template: mako
    - require:
      - file: /var/cache/netboot/livebuild/config/archives


livebuild-paella-apt-binary:
  file.managed:
    - name: /var/cache/netboot/livebuild/config/archives/paella.list.binary
    - source: salt://debianlive/paella.list.binary
    - template: mako
    - require:
      - file: /var/cache/netboot/livebuild/config/archives


livebuild-paella-package-list:
  file.managed:
    - name: /var/cache/netboot/livebuild/config/package-lists/paella.list.chroot
    - source: salt://debianlive/paella.package.list.chroot
    - template: mako
    - require:
      - file: /var/cache/netboot/livebuild/config/package-lists



