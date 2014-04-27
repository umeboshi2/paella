# -*- mode: yaml -*-

%if pillar['paella_enable_software_download_states']:
<% cache = '/vagrant/vagrant/cache' %>

%if False:
win7-ultimate-i386-iso:
  file.managed:
    - source: http://msft.digitalrivercontent.net/win/X17-59463.iso
    - source_hash: sha256=e2c009a66d63a742941f5087acae1aa438dcbe87010bddd53884b1af6b22c940
    - name: ${cache}/win7-ultimate-i386.iso

kb3aik_en.iso:
  file.managed:
    - source: http://download.microsoft.com/download/8/E/9/8E9BBC64-E6F8-457C-9B8D-F6C9A16E6D6A/KB3AIK_EN.iso
    - source_hash: sha256=c6639424b2cebabff3e851913e5f56410f28184bbdb648d5f86c05d93a4cebba
    - name: ${cache}/kb3aik.iso
%endif

<% nu2_directory = '%s/nu2-files' % cache %>
nu2_files_directory:
  file.directory:
    - name: ${nu2_directory}
    - makedirs: True

nu2-bfd.zip:
  file.managed:
    - source: ${pillar['nu2_mirror']}/bfd107.zip
    - source_hash: sha256=768467860ce870010e977a051a26fae712ad853b96667bd242a71122ea049c01
    - name: ${nu2_directory}/bfd107.zip

%endif

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

win7_share_directory:
  file.directory:
    - name: /srv/shares/win7
    - require:
      - file: shares_directory


win7-iso-exists:
  file.exists:
    - name: ${cache}/win7-ultimate-i386.iso

win7_share_mounted:
  mount.mounted:
    - name: /srv/shares/win7
    - device: ${cache}/win7-ultimate-i386.iso
    - fstype: udf
    - mkmnt: True
    - opts:
      - defaults
      - loop
    - require:
      - file: win7-iso-exists

samba_incoming_share_directory:
  file.directory:
    - name: /srv/shares/incoming
    - makedirs: True
    - mode: 777

samba-support-packages:
  pkg.installed:
    - pkgs:
      - smbclient

samba-server-package:
  pkg.installed:
    - name: samba
    - requires:
      - pkg: samba-support-packages


smb.conf:
  file.managed:
    - name: /etc/samba/smb.conf
    - source: salt://samba/smb.conf
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

