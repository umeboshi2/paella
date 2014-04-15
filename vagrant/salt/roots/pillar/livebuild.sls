# -*- mode: yaml -*-

livebuild:
  distribution: wheezy
  parent_distribution: wheezy
  architectures: i386
  mirror: http://ftp.us.debian.org/debian
  mirror_security: http://security.debian.org/
  bootloader: syslinux
  binary_images: netboot
  net_root_server: 10.0.4.1
  net_root_filesystem: nfs
  net_root_path: /srv/debian-live
  apt_key: http://localhost/debrepos/paella.gpg
  local_mirror: http://localhost/debrepos/debian
  local_security_mirror: http://localhost/debrepos/security
  lan_mirror: http://10.0.4.1/debrepos/debian
  lan_security_mirror: http://10.0.4.1/debrepos/security







