# -*- mode: yaml -*-

include:
  - samba.base

%if pillar['paella_enable_software_download_states']:
<% cache = '/vagrant/vagrant/cache' %>

%if pillar['paella_really_download_or_check_the_large_iso_files']:
<% win7 = pillar['win7_ultimate_iso'] %>
%for arch in ['i386', 'amd64']:
win7-ultimate-${arch}-iso:
  file.managed:
    - source: ${win7[arch]['source']}
    - source_hash: ${win7[arch]['source_hash']}
    - name: ${cache}/win7-ultimate-${arch}.iso
%endfor

%for iso in pillar['cached_iso_files']:
${iso}_iso:
  <% i = pillar[iso] %>
  file.managed:
    - source: ${i['source']}
    - source_hash: ${i['source_hash']}
    - name: ${cache}/${i['name']}
%endfor
%endif

%for filename in pillar['cached_windows_files']:
cached_windoes_file_${filename}:
  <% f = pillar[filename] %>
  file.managed:
    - source: ${f['source']}
    - source_hash: ${f['source_hash']}
    - name: ${cache}/windows/${f['name']}
    - makedirs: True
%endfor



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


# I really don't feel like grepping through a server
# log where the daemon is forced to run -vvv

#win7pxelinux:
#  file.managed:
#    - source: http://www.ultimatedeployment.org/win7pxelinux.tgz
#    - source_hash: sha256=8e061380278785b47130a42a2af5772a500e55bd197e1c1cd938195cfab04e91
#    - name: ${cache}/win7pxelinux.tgz


# pebuilder is only for windows xp

#pebuilder.zip:
#  file.managed:
#    - source: ${pillar['nu2_mirror']}/pebuilder3110a.zip
#    - source_hash: sha256=e706e30bffcb4279e7906c2b3f044c10740cf9cb0c53d328597ded9604ad1f75
#    - name: ${nu2_directory}/pebuilder3110a.zip

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
