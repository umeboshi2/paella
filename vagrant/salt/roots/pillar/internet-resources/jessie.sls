# -*- mode: yaml -*-

{% set jessie_installer_i386 = 'http://d-i.debian.org/daily-images/i386/20141224-00:11' %}
{% set jessie_installer_amd64 = 'http://ftp.nl.debian.org/debian/dists/jessie/main/installer-amd64/20150107/images' %}
{% set parent_path = '/vagrant/cache/debinstall/jessie' %}
{% set udeb_i386 = '/srv/debrepos/debian/conf/udebs-jessie-i386-upstream' %}
{% set udeb_amd64 = '/srv/debrepos/debian/conf/udebs-jessie-amd64-upstream' %}

internet_resources:
  debian_pxe_installer_jessie_i386_udeb_list:
    source: {{ jessie_installer_i386 }}/udeb.list
    source_hash: sha256=ea522e25ce8a7602a58d3e7c3c453ba91b923fdb5fbc3715c6336d397b80643d
    name: {{ udeb_i386 }}
  debian_pxe_installer_jessie_i386_linux:
    source: {{ jessie_installer_i386 }}/netboot/debian-installer/i386/linux
    source_hash: sha256=bea1333a6a366f907d0acd91f8b0cef0e9cbbca316e23d44519611e0eb25b7d6
    name: {{ parent_path }}/i386/linux
  debian_pxe_installer_jessie_i386_initrd_console:
    source: {{ jessie_installer_i386 }}/netboot/debian-installer/i386/initrd.gz
    source_hash: sha256=057cf92c30925b7c3e03d7b591e3f12c42fd5ede17a72c907b99a25c52e0efe4
    name: {{ parent_path }}/i386/initrd-console.gz
  debian_pxe_installer_jessie_i386_initrd_gtk:
    source: {{ jessie_installer_i386 }}/netboot/gtk/debian-installer/i386/initrd.gz
    source_hash: sha256=24dd0bb071333df00c46c62ad8aeba56974692a25f237c428236791acc72b501
    name: {{ parent_path }}/i386/initrd-gtk.gz
  debian_pxe_installer_jessie_amd64_udeb_list:
    source: {{ jessie_installer_amd64 }}/udeb.list
    source_hash: sha256=37ea482475d91adb7a0873c605c127b68513582357fa07fb6b635d88139d4b75
    name: {{ udeb_amd64 }}
  debian_pxe_installer_jessie_amd64_linux:
    source: {{ jessie_installer_amd64 }}/netboot/debian-installer/amd64/linux
    source_hash: sha256=7f5fbeb9b3191b4c1311860a678ebcdd3946f10b6776932cf16720b44413d9bd
    name: {{ parent_path }}/amd64/linux
  debian_pxe_installer_jessie_amd64_initrd_console:
    source: {{ jessie_installer_amd64 }}/netboot/debian-installer/amd64/initrd.gz
    source_hash: sha256=924385bce7977f48a6620a2f7f017276b25833598ccc5619c5e1d568e299e0f2
    name: {{ parent_path }}/amd64/initrd-console.gz
  debian_pxe_installer_jessie_amd64_initrd_gtk:
    source: {{ jessie_installer_amd64 }}/netboot/gtk/debian-installer/amd64/initrd.gz
    source_hash: sha256=ac24a42bbb2a7c52f5ba52f69a3ceae6e63b6fb0709f63e95b5bfcf1fd3bdae9
    name: {{ parent_path }}/amd64/initrd-gtk.gz

