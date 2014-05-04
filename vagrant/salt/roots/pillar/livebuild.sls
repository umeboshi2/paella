# -*- mode: yaml -*-

include:
  - base

# FIXME
<% paella_server_ip = '10.0.4.1' %>

livebuild:
  distribution: wheezy
  parent_distribution: wheezy
  architectures_i386: i386
  architectures_amd64: amd64
  mirror: http://ftp.us.debian.org/debian
  mirror_security: http://security.debian.org/
  bootloader: syslinux
  binary_images: netboot
  net_root_server: ${paella_server_ip}
  net_root_filesystem: nfs
  net_root_path: /srv/debian-live
  apt_key: http://localhost/debrepos/paella.gpg
  local_mirror: http://localhost/debrepos/debian
  local_security_mirror: http://localhost/debrepos/security
  lan_mirror: http://${paella_server_ip}/debrepos/debian
  lan_security_mirror: http://${paella_server_ip}/debrepos/security
  enable_xfce_desktop: False







