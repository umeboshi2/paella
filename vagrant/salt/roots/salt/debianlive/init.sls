# -*- mode: yaml -*-

live-build:
  pkg:
    - installed

<% configdir = '/var/cache/netboot/livebuild/config' %>

# This is modified to accept a url with the _KEY variable
/usr/lib/live/build/bootstrap_archive-keys:
  file.managed:
    - source: salt://debianlive/bootstrap_archive-keys
    - user: root
    - group: root
    - mode: 755


livebuild-configdir:
  file.directory:
    - name: ${configdir}
    - user: root
    - group: root
    - mode: 755
    - makedirs: True


%for cfile in ['binary', 'bootstrap', 'chroot', 'common', 'source']:
livebuild-config-${cfile}:
  file.managed:
    - name: ${configdir}/${cfile}
    - source: salt://debianlive/templates/${cfile}
    - template: mako
    - require:
      - file: livebuild-configdir
%endfor

${configdir}/archives:
  file.directory:
    - mode: 755
    - makedirs: True

${configdir}/package-lists:
  file.directory:
    - mode: 755
    - makedirs: True

livebuild-paella-apt-chroot:
  file.managed:
    - name: ${configdir}/archives/paella.list.chroot
    - source: salt://debianlive/paella.list.chroot
    - template: mako
    - require:
      - file: ${configdir}/archives


livebuild-paella-apt-binary:
  file.managed:
    - name: ${configdir}/archives/paella.list.binary
    - source: salt://debianlive/paella.list.binary
    - template: mako
    - require:
      - file: ${configdir}/archives


livebuild-paella-package-list:
  file.managed:
    - name: ${configdir}/package-lists/paella.list.chroot
    - source: salt://debianlive/paella.package.list.chroot
    - template: mako
    - require:
      - file: ${configdir}/package-lists



livebuild-user-setup-conf:
  file.managed:
    - makedirs: True
    - name: ${configdir}/includes.chroot/etc/live/config/user-setup.conf
    - source: salt://debianlive/user-setup.conf
    - template: mako
    - require:
      - file: livebuild-configdir

make-win7-system:
  file.managed:
    - makedirs: True
    - name: ${configdir}/includes.chroot/usr/local/bin/make-win7-system
    - mode: 755
    - source: salt://paella-client/make-win7-disk.parted.sh
    - require:
      - file: livebuild-configdir

livebuild-srv-incoming:
  file.directory:
    - makedirs: True
    - name: ${configdir}/includes.chroot/srv/incoming
    - require:
      - file: livebuild-configdir

livebuild-fstab:
  file.managed:
    - makedirs: True
    - name: ${configdir}/includes.chroot/etc/fstab
    - source: salt://debianlive/fstab
    - template: mako
    - require:
      - file: livebuild-srv-incoming

