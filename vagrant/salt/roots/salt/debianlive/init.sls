# -*- mode: yaml -*-

live-build:
  pkg:
    - installed

<% configdir = '/var/cache/netboot/livebuild/config' %>

<% basedir = '/var/cache/netboot/livebuild' %>
# This is modified to accept a url with the _KEY variable
/usr/lib/live/build/bootstrap_archive-keys:
  file.managed:
    - source: salt://debianlive/bootstrap_archive-keys
    - user: root
    - group: root
    - mode: 755


%for arch in ['i386', 'amd64']:
<% configdir = '%s/%s/config' % (basedir, arch) %>
livebuild-configdir-${arch}:
  file.directory:
    - name: ${configdir}
    - user: root
    - group: root
    - mode: 755
    - makedirs: True

%for cfile in ['binary', 'common', 'source']:
livebuild-config-${arch}-${cfile}:
  file.managed:
    - name: ${configdir}/${cfile}
    - source: salt://debianlive/templates/${cfile}
    - template: mako
    - require:
      - file: livebuild-configdir-${arch}
%endfor
%for cfile in ['bootstrap', 'chroot']:
livebuild-config-${arch}-${cfile}:
  file.managed:
    - name: ${configdir}/${cfile}
    - source: salt://debianlive/templates/${cfile}.${arch}
    - template: mako
    - require:
      - file: livebuild-configdir-${arch}
%endfor


${configdir}/archives:
  file.directory:
    - mode: 755
    - makedirs: True

${configdir}/package-lists:
  file.directory:
    - mode: 755
    - makedirs: True

livebuild-${arch}-paella-apt-chroot:
  file.managed:
    - name: ${configdir}/archives/paella.list.chroot
    - source: salt://debianlive/paella.list.chroot
    - template: mako
    - require:
      - file: ${configdir}/archives


livebuild-${arch}-paella-apt-binary:
  file.managed:
    - name: ${configdir}/archives/paella.list.binary
    - source: salt://debianlive/paella.list.binary
    - template: mako
    - require:
      - file: ${configdir}/archives


livebuild-${arch}-paella-package-list:
  file.managed:
    - name: ${configdir}/package-lists/paella.list.chroot
    - source: salt://debianlive/paella.package.list.chroot.${arch}
    - template: mako
    - require:
      - file: ${configdir}/package-lists



livebuild-${arch}-user-setup-conf:
  file.managed:
    - makedirs: True
    - name: ${configdir}/includes.chroot/etc/live/config/user-setup.conf
    - source: salt://debianlive/user-setup.conf
    - template: mako
    - require:
      - file: livebuild-configdir-${arch}

make-win7-system-${arch}:
  file.managed:
    - makedirs: True
    - name: ${configdir}/includes.chroot/usr/local/bin/make-win7-system
    - mode: 755
    - source: salt://paella-client/make-win7-disk.parted.sh
    - require:
      - file: livebuild-configdir-${arch}

livebuild-${arch}-srv-incoming:
  file.directory:
    - makedirs: True
    - name: ${configdir}/includes.chroot/srv/incoming
    - require:
      - file: livebuild-configdir-${arch}

livebuild-${arch}-fstab:
  file.managed:
    - makedirs: True
    - name: ${configdir}/includes.chroot/etc/fstab
    - source: salt://debianlive/fstab
    - template: mako
    - require:
      - file: livebuild-${arch}-srv-incoming

%endfor


