# -*- mode: yaml -*-

include:
  - debrepos
  - tftpd
  - netboot.debian-installer



/var/lib/tftpboot/pxelinux.cfg/default:
  file.managed:
    - source: salt://netboot/pxelinux-cfg
    - template: mako

/var/lib/tftpboot/splash.png:
  file.managed:
    - source: salt://netboot/splash.png

/var/lib/tftpboot/paella-splash.png:
  file.managed:
    - source: salt://netboot/paella-splash.png


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

%for arch in ['i386', 'amd64']:
<% lbdir = '/var/cache/netboot/livebuild/%s' % arch %>
build-live-image-${arch}:
  cmd.run:
    - require:
      - sls: debrepos
      - file: build-live-image-script
    - unless: test -r ${lbdir}/binary.netboot.tar
    - name: make-live-image ${arch}
    - cwd: ${lbdir}

install-live-filesystem-${arch}:
  cmd.script:
    - require:
      - cmd: build-live-image-${arch}
    - unless: test -r /srv/debian-live/${arch}/FIXME
    - source: salt://scripts/install-netboot-filesystem.sh
    - env:
      - ARCH: ${arch}
%endfor


# copy syslinux files to tftpboot
<% statenames = [] %>
%for filename in ['chain.c32', 'gpxelinux.0', 'memdisk']:
<% sname = 'copy-%s' % filename %>
<% statenames.append(sname) %>
${sname}:
  cmd.run:
    - name: cp -a /usr/lib/syslinux/${filename} /var/lib/tftpboot
    - unless: test -r /var/lib/tftpboot/${filename}
    - requires:
      - file: /var/lib/tftpboot
%endfor

syslinux-files-installed:
  cmd.run:
    - name: echo "syslinux-files-installed"
    - requires:
      %for sname in statenames:
      - ${sname}
      %endfor

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
      - cmd: install-tftpboot-files
      - cmd: syslinux-files-installed


