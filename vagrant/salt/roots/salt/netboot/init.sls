# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}

include:
  - debianlive
  - winpe
  - mainserver
  - driverpacks
  - netboot.debian-installer
  - netboot.services


/var/lib/tftpboot/pxelinux.cfg/default:
  file.managed:
    - source: salt://netboot/pxelinux-cfg
    - template: mako
    - makedirs: True
    - user: {{ user }}

/var/lib/tftpboot/splash.png:
  file.managed:
    - source: salt://netboot/splash.png
    - user: {{ user }}

/var/lib/tftpboot/paella-splash.png:
  file.managed:
    - source: salt://netboot/paella-splash.png
    - user: {{ user }}


#####################################

# debian live
# the local debian repository must be ready

/var/cache/netboot/livebuild:
  file.directory:
    - user: root
    - group: root
    - makedirs: True


# FIXME:  These scripts aren't really that great and
# are not really good for salt states.  They will 
# generally work to help build the basic development
# environment, but better methods should be used to 
# build and manage live images in the production 
# environment.
build-live-image-script:
  file.managed:
    - require:
      - sls: debrepos
      - file: /var/cache/netboot/livebuild
    - name: /usr/local/bin/make-live-image
    - source: salt://scripts/make-live-image.sh
    - mode: 755

{% for arch in ['i386', 'amd64']: %}
{% set lbdir = '/var/cache/netboot/livebuild/%s' % arch %}
build-live-image-{{ arch }}:
  cmd.run:
    - require:
      - sls: winpe
      - file: build-live-image-script
    - unless: test -r {{ lbdir }}/binary/md5sum.txt
    - name: make-live-image {{ arch }}
    - cwd: {{ lbdir }}

livebuild-filesystem-share-{{ arch }}:
  file.directory:
    - name: /srv/debian-live/{{ arch }}
    - makedirs: True

install-live-filesystem-{{ arch }}:
  cmd.script:
    - require:
      - cmd: build-live-image-{{ arch }}
      - file: livebuild-filesystem-share-{{ arch }}
    - unless: test -r /srv/debian-live/{{ arch }}/FIXME
    - source: salt://scripts/install-netboot-filesystem.sh
    - env:
      - ARCH: {{ arch }}

live-{{ arch }}.cfg:
  file.copy:
    - name: /var/lib/tftpboot/live-{{ arch }}.cfg
    - source: {{ lbdir }}/tftpboot/live.cfg

live-{{ arch }}-directory:
  file.directory:
    - name: /var/lib/tftpboot/live-{{ arch }}
    - makedirs: True
    - user: {{ user }}

edit-live-{{ arch }}.cfg:
  file.replace:
    - name: /var/lib/tftpboot/live-{{ arch }}.cfg
    - pattern: /live/
    - repl: /live-{{ arch }}/


{% if arch == 'i386': %}
{% for ver in ['1', '2']: %}
livebuild-bootfile-vmlinuz{{ ver }}-{{ arch }}:
  file.copy:
    - name: /var/lib/tftpboot/live-{{ arch }}/vmlinuz{{ ver }}
    - source: {{ lbdir }}/binary/live/vmlinuz{{ ver }}
    - makedirs: True
    - require:
      - file: live-{{ arch }}-directory
livebuild-bootfile-initrd{{ ver }}.img-{{ arch }}:
  file.copy:
    - name: /var/lib/tftpboot/live-{{ arch }}/initrd{{ ver }}.img
    - source: {{ lbdir }}/binary/live/initrd{{ ver }}.img
    - makedirs: True
    - require:
      - file: live-{{ arch }}-directory
{% endfor %}
{% elif arch == 'amd64': %}
{% for filename in ['vmlinuz', 'initrd.img']: %}
livebuild-bootfile-{{ filename }}-{{ arch }}:
  file.copy:
    - name: /var/lib/tftpboot/live-{{ arch }}/{{ filename }}
    - source: {{ lbdir }}/binary/live/{{ filename }}
    - makedirs: True
    - require:
      - file: live-{{ arch }}-directory
{% endfor %}
{% endif %}

{% endfor %}

# FIXME this may not work in jinja
# copy syslinux files to tftpboot
{% set statenames = [] %}
{% for filename in ['chain.c32', 'gpxelinux.0', 'memdisk', 'pxelinux.0', 'vesamenu.c32']: %}
{% set sname = 'copy-%s' % filename %}
{% set ignore = statenames.append(sname) %}
{{ sname }}:
  file.copy:
    - name: /var/lib/tftpboot/{{ filename }}
    - source: /usr/lib/syslinux/{{ filename }}
    - require:
      - file: /var/lib/tftpboot
{% endfor %}

syslinux-files-installed:
  cmd.run:
    - name: echo "syslinux-files-installed"
    - requires:
      {% for sname in statenames: %}
      - {{ sname }}
      {% endfor %}

ipxe-boot-file:
  cmd.run:
    - name: cp -a /usr/lib/ipxe/undionly.kpxe /var/lib/tftpboot
    - unless: test -r /var/lib/tftpboot/undionly.kpxe
    - requires:
      - cmd: syslinux-files-installed



# FIXME:  This command always runs!  Figure out when it's
# necessary from the other states.
vagrant-owns-tftpboot:
  cmd.run:
    - name: chown -R vagrant:vagrant /var/lib/tftpboot
    - require:
      - cmd: syslinux-files-installed
      - cmd: ipxe-boot-file


