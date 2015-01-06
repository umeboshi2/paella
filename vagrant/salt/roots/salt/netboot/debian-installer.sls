# -*- mode: yaml -*-
{% set pget = salt['pillar.get'] %}
{% set user = pget('paella:paella_user', 'vagrant') %}
{% set group = pget('paella:paella_group', 'vagrant') %}


# debian installer files for tftpboot

/var/lib/tftpboot/installer:
  file.directory:
    - makedirs: True
{% set installer = pget('debian_pxe_installer') %}
{% for release in installer: %}
{% for arch in installer[release]: %}
{% set cachepath = '/vagrant/vagrant/cache/debinstall/%s/%s' % (release, arch) %}
{% set basepath = '/var/lib/tftpboot/debinstall/%s/%s' % (release, arch) %}
{{ basepath }}-directory:
  file.directory:
    - name: {{ basepath }}
    - makedirs: True

{% for sfile in ['linux']: %}
{% set base = installer[release][arch][sfile] %}
{{ cachepath }}/{{ sfile }}:
  file.managed:
    - makedirs: True
    - source: {{ base['source'] }}
    - source_hash: {{ base['source_hash'] }}
{{ basepath }}/{{ sfile }}:
  file.copy:
    - makedirs: True
    - require:
      - file: {{ basepath }}-directory
      - file: {{ cachepath }}/{{ sfile }}
    - source: {{ cachepath }}/{{ sfile }}
    - unless: test -r {{ basepath }}/{{ sfile }}
{% endfor %}


{% for sfile in ['console', 'gtk']: %}
{% set base = installer[release][arch]['initrd'][sfile] %}
{% set cachefile = '%s/initrd-%s.gz' % (cachepath, sfile) %}
{% set mainfile = '%s/initrd-%s.gz' % (basepath, sfile) %}
{{ cachefile }}:
  file.managed:
    - makedirs: True
    - source: {{ base['source'] }}
    - source_hash: {{ base['source_hash'] }}
{{ mainfile }}:
  file.copy:
    - makedirs: True
    - require:
      - file: {{ basepath }}-directory
      - file: {{ cachefile }}
    - source: {{ cachefile }}
    - unless: test -r {{ mainfile }}
{% endfor %}

{% endfor %}
{% endfor %}

