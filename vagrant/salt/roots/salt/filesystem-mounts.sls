# -*- mode: yaml -*-

# FIXME  these states used to be in the samba state tree
# for paella.

include:
  - default.pkgsets
  - managed-files
  
{% set cache = '/vagrant/vagrant/cache' %}


shares_directory:
  file.directory: 
    - name: /srv/shares


aik_share_directory:
  file.directory:
    - name: /srv/shares/aik
    - require:
      - file: shares_directory

aik_share_mounted:
  mount.mounted:
    - name: /srv/shares/aik
    - device: {{ cache }}/kb3aik.iso
    - fstype: udf
    - mkmnt: True
    - opts:
      - defaults
      - loop

{% for arch in ['i386', 'amd64']: %}
win7_{{ arch }}_share_directory:
  file.directory:
    - name: /srv/shares/win7/{{ arch }}
    - makedirs: True

win7_{{ arch }}_share_mounted:
  mount.mounted:
    - name: /srv/shares/win7/{{ arch }}
    - device: {{ cache }}/win7-ultimate-{{ arch }}.iso
    - fstype: udf
    - mkmnt: True
    - opts:
      - defaults
      - loop
{% endfor %}

samba_incoming_share_directory:
  file.directory:
    - name: /srv/shares/incoming
    - makedirs: True
    - mode: 777

samba_winstall_share_directory:
  file.directory:
    - name: /srv/shares/winstall
    - makedirs: True
    - mode: 777

samba_winstall_base_directory:
  file.directory:
    - name: /srv/shares/winstall/base
    - makedirs: True

install_samba_winstall_base_directory:
  cmd.run:
    - name: cp -sa /srv/shares/win7/* base
    - cwd: /srv/shares/winstall
    - unless: test -r /srv/shares/winstall/base/i386/setup.exe

rsync-windows-files:
  cmd.run:
    - name: rsync -avHX /vagrant/vagrant/cache/windows/ /srv/shares/incoming/windows/
    - require:
      - file: samba_incoming_share_directory
  