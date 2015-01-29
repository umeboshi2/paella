# -*- mode: yaml -*-
{% from 'config.jinja' import paella %}

{% set apt_http_proxy = "http://127.0.0.1:8000/" %}
{% if paella.use_local_apt_cache_proxy %}
{% set apt_http_proxy = paella.local_apt_cache_proxy %}
{% endif %}
{% set archs = paella.debian_release_archs[paella.live_system_dist] %}

livebuild:
  debootstrap: cdebootstrap
  architectures_to_build: {{ archs }}
  apt_http_proxy: {{ apt_http_proxy }}
  base_directory: /var/cache/netboot/livebuild
  distribution: {{ paella.live_system_dist }}
  parent_distribution: {{ paella.live_system_dist }}
  bootloader: syslinux
  binary_images: netboot
  net_root_server: {{ paella.paella_server_ip }}
  net_root_filesystem: nfs
  net_root_path: /srv/debian-live
  apt_key: http://localhost/debrepos/paella.gpg
  mirror: {{ paella.debian_mirror }}
  mirror_security: {{ paella.debian_security_mirror }}
  local_mirror: {{ paella.debian_mirror }}
  local_security_mirror: {{ paella.debian_security_mirror }}
  lan_mirror: {{ paella.debian_mirror }}
  lan_security_mirror: {{ paella.debian_security_mirror }}
  enable_xfce_desktop: True

