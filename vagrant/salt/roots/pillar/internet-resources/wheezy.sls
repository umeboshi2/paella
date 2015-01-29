# -*- mode: yaml -*-

{% set wheezy_installer_i386 = 'http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/20130613+deb7u2+b4/images' %}
{% set wheezy_installer_amd64 = 'http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-amd64/20130613+deb7u2+b4/images' %}
{% set parent_path = '/vagrant/cache/debinstall/wheezy' %}
{% set udeb_i386 = '/srv/debrepos/debian/conf/udebs-wheezy-i386-upstream' %}
{% set udeb_amd64 = '/srv/debrepos/debian/conf/udebs-wheezy-amd64-upstream' %}

internet_resources:
  {% if 'i386' in pget('paella.debian_release_archs.wheezy') %}
  debian_pxe_installer_wheezy_i386_udeb_list:
    source: {{ wheezy_installer_i386 }}/udeb.list
    source_hash: sha256=c1d5e75677a1d64e2f485f186ae7cbddacede8deec91dc011f17a50029e97277
    name: {{ udeb_i386 }}
  debian_pxe_installer_wheezy_i386_linux:
    source: {{ wheezy_installer_i386 }}/netboot/debian-installer/i386/linux
    source_hash: sha256=269c3b05657817a11ead163268f4489ea20e757f62046484c59ceeada3dd8a85
    name: {{ parent_path }}/i386/linux
  debian_pxe_installer_wheezy_i386_initrd_console:
    source: {{ wheezy_installer_i386 }}/netboot/debian-installer/i386/initrd.gz
    source_hash: sha256=838a4eaa8dcb5cb71fbf3f3aa1c2aaaa57b44457a3b0f61f2f89da2848541b58
    name: {{ parent_path }}/i386/initrd-console.gz
  debian_pxe_installer_wheezy_i386_initrd_gtk:
    source: {{ wheezy_installer_i386 }}/netboot/gtk/debian-installer/i386/initrd.gz
    source_hash: sha256=0dbeb38d980d929b8e16de4ad1bc6afb752d89c4a00edb7554e82ffa493ab4c7
    name: {{ parent_path }}/i386/initrd-gtk.gz
  {% endif %}
  {% if 'amd64' in pget('paella.debian_release_archs.wheezy') %}
  debian_pxe_installer_wheezy_amd64_udeb_list:
    source: {{ wheezy_installer_amd64 }}/udeb.list
    source_hash: sha256=a55f929587778fc0e73dae0fcdca90f401721b16c8b0e945bfd7ba16afb2d4e9
    name: {{ udeb_amd64 }}
  debian_pxe_installer_wheezy_amd64_linux:
    source: {{ wheezy_installer_amd64 }}/netboot/debian-installer/amd64/linux
    source_hash: sha256=726cdc20aac7fb4e11630469f14f4c03e42bb5878498bf4ebede7b238220b50f
    name: {{ parent_path }}/amd64/linux
  debian_pxe_installer_wheezy_amd64_initrd_console:
    source: {{ wheezy_installer_amd64 }}/netboot/debian-installer/amd64/initrd.gz
    source_hash: sha256=7ff6bf2c90647fb530c730efad3cbacdbba531ff9542d40f7b87a2acd9914cb3
    name: {{ parent_path }}/amd64/initrd-console.gz
  debian_pxe_installer_wheezy_amd64_initrd_gtk:
    source: {{ wheezy_installer_amd64 }}/netboot/gtk/debian-installer/amd64/initrd.gz
    source_hash: sha256=c9a92f2a102d3031b9e37295fb61906a51a409ca7e700b0f65e55bc25184b9c8
    name: {{ parent_path }}/amd64/initrd-gtk.gz
  {% endif %}
