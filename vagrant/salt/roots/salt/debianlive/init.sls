# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set mswin = pget('paella:install_mswindows_machines', False) %}

include:
  - default.pkgsets

{% set basedir = pget('livebuild:base_directory') %}
# This is modified to accept a url with the _KEY variable
#/usr/lib/live/build/bootstrap_archive-keys:
#  file.managed:
#    - source: salt://debianlive/bootstrap_archive-keys
#    - user: root
#    - group: root
#    - mode: 755


{% for arch in pget('livebuild:architectures_to_build', ['amd64']) %}
{% set configdir = '%s/%s/config' % (basedir, arch) %}
livebuild-configdir-{{ arch }}:
  file.directory:
    - name: {{ configdir }}
    - user: root
    - group: root
    - mode: 755
    - makedirs: True

{% for cfile in ['binary', 'bootstrap', 'chroot', 'common', 'source']: %}
livebuild-config-{{ arch }}-{{ cfile }}:
  file.managed:
    - name: {{ configdir }}/{{ cfile }}
    - source: salt://debianlive/templates/{{ cfile }}
    - template: jinja
    - defaults:
        arch: {{ arch }}
    - require:
      - file: livebuild-configdir-{{ arch }}
{% endfor %}

{{ configdir }}/archives:
  file.directory:
    - mode: 755
    - makedirs: True

{{ configdir }}/package-lists:
  file.directory:
    - mode: 755
    - makedirs: True

livebuild-{{ arch }}-paella-apt-chroot:
  file.managed:
    - name: {{ configdir }}/archives/paella.list.chroot
    - source: salt://debianlive/paella.list.chroot
    - template: mako
    - require:
      - file: {{ configdir }}/archives

livebuild-{{ arch }}-paella-apt-chroot-gpg:
  file.managed:
    - name: {{ configdir }}/archives/paella.key.chroot
    - source: salt://debrepos/keys/paella-insecure-pub.gpg
    - require:
      - file: {{ configdir }}/archives


livebuild-{{ arch }}-paella-apt-binary:
  file.managed:
    - name: {{ configdir }}/archives/paella.list.binary
    - source: salt://debianlive/paella.list.binary
    - template: mako
    - require:
      - file: {{ configdir }}/archives

livebuild-{{ arch }}-paella-apt-binary-gpg:
  file.managed:
    - name: {{ configdir }}/archives/paella.key.binary
    - source: salt://debrepos/keys/paella-insecure-pub.gpg
    - require:
      - file: {{ configdir }}/archives


livebuild-{{ arch }}-paella-package-list:
  file.managed:
    - name: {{ configdir }}/package-lists/paella.list.chroot
    - source: salt://debianlive/paella.package.list.chroot
    - template: jinja
    - defaults:
        arch: {{ arch }}
    - require:
      - file: {{ configdir }}/package-lists



livebuild-{{ arch }}-user-setup-conf:
  file.managed:
    - makedirs: True
    - name: {{ configdir }}/includes.chroot/etc/live/config/user-setup.conf
    - source: salt://debianlive/user-setup.conf
    - template: mako
    - require:
      - file: livebuild-configdir-{{ arch }}
        
livebuild-{{ arch }}-fstab:
  file.managed:
    - makedirs: True
    - name: {{ configdir }}/includes.chroot/etc/fstab
    - source: salt://debianlive/fstab
    - template: mako
    - require:
      - file: livebuild-{{ arch }}-srv-incoming

livebuild-{{ arch }}-srv-incoming:
  file.directory:
    - makedirs: True
    - name: {{ configdir }}/includes.chroot/srv/incoming
    - require:
      - file: livebuild-configdir-{{ arch }}
        
{% if mswin %}
make-win7-system-{{ arch }}:
  file.managed:
    - makedirs: True
    - name: {{ configdir }}/includes.chroot/usr/local/bin/make-win7-system
    - mode: 755
    - source: salt://paella-client/make-win7-disk.parted.sh
    - require:
      - file: livebuild-configdir-{{ arch }}

install-win7-image-{{ arch }}:
  file.managed:
    - makedirs: True
    - name: {{ configdir }}/includes.chroot/usr/local/bin/install-win7-image
    - mode: 755
    - source: salt://debianlive/install-win7-image.sh
    - require:
      - file: livebuild-configdir-{{ arch }}

{% endif %}
{% endfor %}


