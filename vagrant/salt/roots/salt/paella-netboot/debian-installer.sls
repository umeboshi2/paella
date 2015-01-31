# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}
include:
  - managed-files

# debian installer files for tftpboot

/var/lib/tftpboot/installer:
  file.directory:
    - makedirs: True


{% for dist in pget('paella:debian_releases', ['wheezy']) %}
{% for arch in pget('livebuild:architectures_to_build', ['amd64']) %}
{% set prefix = 'debian_pxe_installer_%s_%s' % (dist, arch) %}
{% set cachepath = '/vagrant/cache/debinstall/%s/%s' % (dist, arch) %}
{% set basepath = '/var/lib/tftpboot/debinstall/%s/%s' % (dist, arch) %}

{{ basepath }}-directory:
  file.directory:
    - name: {{ basepath }}
    - makedirs: True


{% for sfile in ['linux']: %}
{{ basepath }}/{{ sfile }}:
  file.copy:
    - makedirs: True
    - require:
      - file: {{ basepath }}-directory
      - file: {{ prefix }}_{{ sfile }}
    - source: {{ cachepath }}/{{ sfile }}
    - unless: test -r {{ basepath }}/{{ sfile }}
{% endfor %}


{% for sfile in ['console', 'gtk']: %}
{% set cachefile = '%s/initrd-%s.gz' % (cachepath, sfile) %}
{% set mainfile = '%s/initrd-%s.gz' % (basepath, sfile) %}
{{ mainfile }}:
  file.copy:
    - makedirs: True
    - require:
      - file: {{ basepath }}-directory
      - file: {{ prefix }}_initrd_{{ sfile }}
    - source: {{ cachefile }}
    - unless: test -r {{ mainfile }}
{% endfor %}

{% endfor %}
{% endfor %}

