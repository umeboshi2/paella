# -*- mode: yaml -*-


# debian installer files for tftpboot

/var/lib/tftpboot/installer:
  file.directory:
    - makedirs: True
<% installer = pillar['debian_pxe_installer'] %>
%for release in installer:
%for arch in installer[release]:
<% cachepath = '/vagrant/vagrant/cache/debinstall/%s/%s' % (release, arch) %>
<% basepath = '/var/lib/tftpboot/debinstall/%s/%s' % (release, arch) %>
%for sfile in ['linux', 'initrd.gz']:
<% base = installer[release][arch][sfile] %>
${cachepath}/${sfile}:
  file.managed:
    - makedirs: True
    - source: ${base['source']}
    - source_hash: ${base['source_hash']}
${basepath}/${sfile}:
  file.copy:
    - makedirs: True
    - require:
      - file: ${cachepath}/${sfile}
    - source: ${cachepath}/${sfile}
%endfor
%endfor
%endfor

