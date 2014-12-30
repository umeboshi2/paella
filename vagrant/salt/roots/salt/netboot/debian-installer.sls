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
${basepath}-directory:
  file.directory:
    - name: ${basepath}
    - makedirs: True

%for sfile in ['linux']:
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
      - file: ${basepath}-directory
      - file: ${cachepath}/${sfile}
    - source: ${cachepath}/${sfile}
    - unless: test -r ${basepath}/${sfile}
%endfor


%for sfile in ['console', 'gtk']:
<% base = installer[release][arch]['initrd'][sfile] %>
<% cachefile = '%s/initrd-%s.gz' % (cachepath, sfile) %>
<% mainfile = '%s/initrd-%s.gz' % (basepath, sfile) %>
${cachefile}:
  file.managed:
    - makedirs: True
    - source: ${base['source']}
    - source_hash: ${base['source_hash']}
${mainfile}:
  file.copy:
    - makedirs: True
    - require:
      - file: ${basepath}-directory
      - file: ${cachefile}
    - source: ${cachefile}
    - unless: test -r ${mainfile}
%endfor

%endfor
%endfor

