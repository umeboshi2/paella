# -*- mode: yaml -*-

{% set jessie_installer_i386 = 'http://d-i.debian.org/daily-images/i386/20141224-00:11' %}
{% set jessie_installer_amd64 = 'http://d-i.debian.org/daily-images/amd64/20141224-00:17' %}
debian_pxe_installer:
  jessie:
    ###############################
    i386:
      udeb_list:
        source: {{ jessie_installer_i386 }}/udeb.list
        source_hash: sha256=d44da99f25e81fcafa42906390ae4964ce16c8de8ca5ea9bb44e066f2aa97270
      linux:
        source: {{ jessie_installer_i386 }}/netboot/debian-installer/i386/linux
        source_hash: sha256=bea1333a6a366f907d0acd91f8b0cef0e9cbbca316e23d44519611e0eb25b7d6
      initrd:
        console:
          source: {{ jessie_installer_i386 }}/netboot/debian-installer/i386/initrd.gz
          source_hash: sha256=886d41ff2dd2d10acfde01b30e1c9a9684178aa89c820b4d483c7eead98e37e8
        gtk:
          source: {{ jessie_installer_i386 }}/netboot/gtk/debian-installer/i386/initrd.gz
          source_hash: sha256=fbc8e590dd274bf1c27f8129dcce0e02b9d5b003383209ff0655f3d45884ca0c
    ###############################
    amd64:
      udeb_list:
        source: {{ jessie_installer_amd64 }}/udeb.list
        source_hash: sha256=220cc624c10cc12dd57beccec0cf886183914169cd6ed0f0b5a11bb6370317b0
      linux:
        source: {{ jessie_installer_amd64 }}/netboot/debian-installer/amd64/linux
        source_hash: sha256=7f5fbeb9b3191b4c1311860a678ebcdd3946f10b6776932cf16720b44413d9bd
      initrd:
        console:
          source: {{ jessie_installer_amd64 }}/netboot/debian-installer/amd64/initrd.gz
          source_hash: sha256=e5c9b02215770803aa740fc2cdb1ecb081db763c9da0513ceeaa8c94ce359c62
        gtk:
          source: {{ jessie_installer_amd64 }}/netboot/gtk/debian-installer/amd64/initrd.gz
          source_hash: sha256=cb6828db5fac400a5062af74fea3e9be7bbef5e6030571f7f9ba9eee6fdd4efe

