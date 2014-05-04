# -*- mode: yaml -*-


# debian installer files for tftpboot

/var/lib/tftpboot/installer:
  file.directory:
    - makedirs: True
<% installer = pillar['debian_pxe_installer'] %>
%for release in installer:
%for arch in installer[release]:
<% basepath = '/var/lib/tftpboot/debinstall/%s/%s' % (release, arch) %>
%for sfile in ['linux', 'initrd.gz']:
${basepath}/${sfile}:
  <% base = installer[release][arch][sfile] %>
  file.managed:
    - makedirs: True
    - source: ${base['source']}
    - source_hash: ${base['source_hash']}
%endfor
%endfor
%endfor

