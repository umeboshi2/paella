# -*- mode: yaml -*-

include:
  - samba.base
  - samba.isofiles
  - samba.winfiles

# FIXME
# The three iso's that are mounted in this sls need to be
# in the fstab so that they are present on reboot.  Currently
# the vagrant machine must be provisioned on each boot,
# partially because these iso's are not in fstab but must be
# mounted.
<% cache = '/vagrant/vagrant/cache' %>


shares_directory:
  file.directory: 
    - name: /srv/shares


aik_share_directory:
  file.directory:
    - name: /srv/shares/aik
    - require:
      - file: shares_directory

aik-iso-exists:
  file.exists:
    - name: ${cache}/kb3aik.iso


aik_share_mounted:
  mount.mounted:
    - name: /srv/shares/aik
    - device: ${cache}/kb3aik.iso
    - fstype: udf
    - mkmnt: True
    - opts:
      - defaults
      - loop
    - require:
      - file: aik-iso-exists

%for arch in ['i386', 'amd64']:
win7_${arch}_share_directory:
  file.directory:
    - name: /srv/shares/win7/${arch}
    - makedirs: True

win7-${arch}-iso-exists:
  file.exists:
    - name: ${cache}/win7-ultimate-${arch}.iso

win7_${arch}_share_mounted:
  mount.mounted:
    - name: /srv/shares/win7/${arch}
    - device: ${cache}/win7-ultimate-${arch}.iso
    - fstype: udf
    - mkmnt: True
    - opts:
      - defaults
      - loop
    - require:
      - file: win7-${arch}-iso-exists
%endfor

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

smb.conf:
  file.managed:
    - name: /etc/samba/smb.conf
    - source: salt://samba/smb.conf
    - template: mako
    - requires:
      - pkg: samba-server-package

samba-server-service:
  service:
    - name: samba
    - running
    - watch:
      - file: smb.conf
    - requires:
      - mount: aik_share_mounted
      - mount: win7_share_mounted


rsync-windows-files:
  cmd.run:
    - name: rsync -avHX /vagrant/vagrant/cache/windows/ /srv/shares/incoming/windows/
    - require:
      - file: samba_incoming_share_directory
