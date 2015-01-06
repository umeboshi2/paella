# -*- mode: yaml -*-
#http://archive.ubuntu.com/ubuntu/dists/trusty-updates/main/installer-i386/20101020ubuntu318.12/images/SHA256SUMS
#http://archive.ubuntu.com/ubuntu/dists/trusty-updates/main/installer-amd64/20101020ubuntu318.12/images/SHA256SUMS
{% set trusty_installer_i386 = 'http://archive.ubuntu.com/ubuntu/dists/trusty-updates/main/installer-i386/20101020ubuntu318.12/images' %}
{% set trusty_installer_amd64 = 'http://archive.ubuntu.com/ubuntu/dists/trusty-updates/main/installer-amd64/20101020ubuntu318.12/images' %}
{% set parent_path = '/vagrant/vagrant/cache/debinstall/trusty' %}
{% set udeb_i386 = '/srv/debrepos/debian/conf/udebs-trusty-i386-upstream' %}
{% set udeb_amd64 = '/srv/debrepos/debian/conf/udebs-trusty-amd64-upstream' %}

internet_resources:
  debian_pxe_installer_trusty_i386_udeb_list:
    source: {{ trusty_installer_i386 }}/udeb.list
    source_hash: sha256=2a2016205e603f96dca0543efab85f40191ea87d105bd694b6b469c1ca4d8c3d
    name: {{ udeb_i386 }}
  debian_pxe_installer_trusty_i386_linux:
    source: {{ trusty_installer_i386 }}/netboot/ubuntu-installer/i386/linux
    source_hash: sha256=7388fde70872337b895c6a02d6a63cc1e24d1ab4d6770c93b96435a30e40201f
    name: {{ parent_path }}/i386/linux
  debian_pxe_installer_trusty_i386_utopic_linux:
    source: {{ trusty_installer_i386 }}/utopic-netboot/ubuntu-installer/i386/linux
    source_hash: sha256=e01b3dc60ebdaf02aadabbd0bd64c515097bc11f27b737ca19a763f5c10be9aa
    name: {{ parent_path }}/i386/utopic-linux
  debian_pxe_installer_trusty_i386_initrd_console:
    source: {{ trusty_installer_i386 }}/netboot/ubuntu-installer/i386/initrd.gz
    source_hash: sha256=e603d808a7d30e1d37dabbada41f0575ff54d4fd82f123aac6b73116cc27a105
    name: {{ parent_path }}/i386/initrd-console.gz
  debian_pxe_installer_trusty_i386_initrd_utopic:
    source: {{ trusty_installer_i386 }}/utopic-netboot/ubuntu-installer/i386/initrd.gz
    source_hash: sha256=710e56b45602ec7de3683d58bda0d8b295d03bf4fdfcf17aa08c24dcd514f5bc
    name: {{ parent_path }}/i386/utopic-initrd.gz
  debian_pxe_installer_trusty_amd64_udeb_list:
    source: {{ trusty_installer_amd64 }}/udeb.list
    source_hash: sha256=c6cd8b74ddc32dbe4b0b62086e03d126ba0885efe6f6ded7ad66ab03214f90a1
    name: {{ udeb_amd64 }}
  debian_pxe_installer_trusty_amd64_linux:
    source: {{ trusty_installer_amd64 }}/netboot/ubuntu-installer/amd64/linux
    source_hash: sha256=cf8b9379717083ee7f78e18456b4408f4348ee425954bbca23d16c66089f8b7f
    name: {{ parent_path }}/amd64/linux
  debian_pxe_installer_trusty_amd64_utopic_linux:
    source: {{ trusty_installer_amd64 }}/utopic-netboot/ubuntu-installer/amd64/linux
    source_hash: sha256=89522408b3327cf9961160fc6731ad9d1feb5e252602fddf1c54fb74e8943fd0
    name: {{ parent_path }}/amd64/utopic-linux
  debian_pxe_installer_trusty_amd64_initrd_console:
    source: {{ trusty_installer_amd64 }}/netboot/ubuntu-installer/amd64/initrd.gz
    source_hash: sha256=177ebf498d5b976b4b1b14d1452af9a82ad0d7a5f9053c85f92973c06f8cebfa
    name: {{ parent_path }}/amd64/initrd-console.gz
  debian_pxe_installer_trusty_amd64_initrd_gtk:
    source: {{ trusty_installer_amd64 }}/utopic-netboot/ubuntu-installer/amd64/initrd.gz
    source_hash: sha256=23b5f4d8fffed0fb4d9086bd6a1e9318cde4cb334f4b3c452b0df5648bd5c3a3
    name: {{ parent_path }}/amd64/utopic-initrd.gz

