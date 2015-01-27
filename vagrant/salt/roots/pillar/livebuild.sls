# -*- mode: yaml -*-
{% from 'bvars.jinja' import paella %}


node_version: 0.10.25

  
livebuild:
  architectures_to_build:
    - amd64
    #- i386
  apt_http_proxy: http://{{ paella.paella_server_ip }}:8000
  base_directory: /var/cache/netboot/livebuild
  distribution: wheezy
  parent_distribution: wheezy
  architectures_i386: i386
  architectures_amd64: amd64
  bootloader: syslinux
  binary_images: netboot
  net_root_server: {{ paella.paella_server_ip }}
  net_root_filesystem: nfs
  net_root_path: /srv/debian-live
  apt_key: http://localhost/debrepos/paella.gpg
  mirror: http://ftp.us.debian.org/debian
  mirror_security: http://security.debian.org/
  local_mirror: http://ftp.us.debian.org/debian
  local_security_mirror: http://security.debian.org/
  lan_mirror: http://ftp.us.debian.org/debian
  lan_security_mirror: http://security.debian.org/
  enable_xfce_desktop: True

