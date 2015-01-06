# -*- mode: yaml -*-

{% set wheezy_installer_i386 = 'http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/current/images' %}
{% set wheezy_installer_amd64 = 'http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-amd64/current/images' %}
{% set parent_path = '/vagrant/vagrant/cache/debinstall/wheezy' %}
{% set udeb_i386 = '/srv/debrepos/debian/conf/udebs-wheezy-i386-upstream' %}
{% set udeb_amd64 = '/srv/debrepos/debian/conf/udebs-wheezy-amd64-upstream' %}

internet_resources:
  debian_pxe_installer_wheezy_i386_udeb_list:
    source: {{ wheezy_installer_i386 }}/udeb.list
    source_hash: sha256=a4bce242e3b8a32a68f980cd4011fbb3f20ec6a1370f2bee10a046a41a2f80d0
    name: {{ udeb_i386 }}
  debian_pxe_installer_wheezy_i386_linux:
    source: {{ wheezy_installer_i386 }}/netboot/debian-installer/i386/linux
    source_hash: sha256=1f256c7d273247fc257cdd3d40046c8e32f3a9f8e78bbfecc925999ff69d7b82
    name: {{ parent_path }}/i386/linux
  debian_pxe_installer_wheezy_i386_initrd_console:
    source: {{ wheezy_installer_i386 }}/netboot/debian-installer/i386/initrd.gz
    source_hash: sha256=ae122861a3f1eaceb0de9591e17f1c8eadd6761e06eacfffe0b49d6c34e8ca6e
    name: {{ parent_path }}/i386/initrd-console.gz
  debian_pxe_installer_wheezy_i386_initrd_gtk:
    source: {{ wheezy_installer_i386 }}/netboot/gtk/debian-installer/i386/initrd.gz
    source_hash: sha256=f623c3dc53fce89106aa31a1607a550f40899cbc7fcfaf0cfefbd565e35bc6e3
    name: {{ parent_path }}/i386/initrd-gtk.gz
  debian_pxe_installer_wheezy_amd64_udeb_list:
    source: {{ wheezy_installer_amd64 }}/udeb.list
    source_hash: sha256=6d2a05b7b1f7ecc9a8ab868905c9b1254e3e82fc47bce8b5eef78b26cca1cc2c
    name: {{ udeb_amd64 }}
  debian_pxe_installer_wheezy_amd64_linux:
    source: {{ wheezy_installer_amd64 }}/netboot/debian-installer/amd64/linux
    source_hash: sha256=487e2dc3635e22f3f7d6e90e36d6dccbf9c5e09a747179d0aa42bc6b063d492a
    name: {{ parent_path }}/amd64/linux
  debian_pxe_installer_wheezy_amd64_initrd_console:
    source: {{ wheezy_installer_amd64 }}/netboot/debian-installer/amd64/initrd.gz
    source_hash: sha256=c91a2216fe00ddb9bd42a8000e19997b5df897a561f904b0a88e03a65f6c6dad
    name: {{ parent_path }}/amd64/initrd-console.gz
  debian_pxe_installer_wheezy_amd64_initrd_gtk:
    source: {{ wheezy_installer_amd64 }}/netboot/gtk/debian-installer/amd64/initrd.gz
    source_hash: sha256=b177215ff00ca5d0432d0a85fdd01c70b06ef35469371809e629416e51bd3003
    name: {{ parent_path }}/amd64/initrd-gtk.gz
