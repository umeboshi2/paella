# -*- mode: yaml -*-


# nu2_mirror CANNOT end with a trailing /
#nu2_mirror: http://ftp.rz.tu-bs.de/pub/mirror/www.nu2.nu/nu2files
#nu2_mirror: http://securitywonks.org/n2u/mirrorfiles
nu2_mirror: ftp://dl.xs4all.nl/pub/mirror/nu2files

debian_pxe_installer:
  wheezy:
    i386:
      linux:
        source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/current/images/netboot/debian-installer/i386/linux
        source_hash: sha256=de2603ec02171643ecbb615373a834302fdab2804294472edb673ec0055c9955
      initrd.gz:
        source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-i386/current/images/netboot/debian-installer/i386/initrd.gz
        source_hash: sha256=0aef8471b5092000991d7549be503d46b7e301cf89582d2c68619b14cedea50f
      udeb_list:
        source: http://ftp.us.debian.org/debian/dists/wheezy/main/installer-i386/current/images/udeb.list
        source_hash: sha256=d9ffa71c7f1be047f5eafb8f5a3359d86dd34e7ce09acd0ea5d44e9aaff8cc20
    amd64:
      linux:
        source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-amd64/current/images/netboot/debian-installer/amd64/linux
        source_hash: sha256=175b487eac5b11ccff9ffff9f759f6530e3852ac179cab6f4c04b0b413b62ec8
      initrd.gz:
        source: http://ftp.nl.debian.org/debian/dists/wheezy/main/installer-amd64/current/images/netboot/debian-installer/amd64/initrd.gz
        source_hash: sha256=a74a88d3396aba220a557bba0f8f60de87c4c05a7c993503f300afec54aba4a5
      udeb_list:
        source: http://ftp.us.debian.org/debian/dists/wheezy/main/installer-amd64/current/images/udeb.list
        source_hash: sha256=a9a8f2b3f1abf921356240cf1f9a2eb31eaaece25cd2aa1849cd58259ff45cb5
  jessie:
    i386:
      linux:
        source: http://ftp.nl.debian.org/debian/dists/jessie/main/installer-i386/20140316/images/netboot/debian-installer/i386/linux
        source_hash: sha256=17a5a290a5c83478394e604877653058d7a5bb6a1198d40dde32e4b988af3df9
      initrd.gz:
        source: http://ftp.nl.debian.org/debian/dists/jessie/main/installer-i386/20140316/images/netboot/debian-installer/i386/initrd.gz
        source_hash: sha256=04627b4d2ba7feaa70fc970884524fecf1ed39b3446f677f626b89058a9887cd
      udeb_list:
        source: http://ftp.nl.debian.org/debian/dists/jessie/main/installer-i386/20140316/images/udeb.list
        source_hash: sha256=a5a9e0a7ecc78df2183feaceffabfd4b563e167faf37383fa7072abb2419461b
debian_installer_i386_checksums:
  udeb_list: sha256=d9ffa71c7f1be047f5eafb8f5a3359d86dd34e7ce09acd0ea5d44e9aaff8cc20
  initrd: sha256=0aef8471b5092000991d7549be503d46b7e301cf89582d2c68619b14cedea50f
  linux: sha256=de2603ec02171643ecbb615373a834302fdab2804294472edb673ec0055c9955


win7_ultimate_iso:
  i386:
    source: http://msft.digitalrivercontent.net/win/X17-59463.iso
    source_hash: sha256=e2c009a66d63a742941f5087acae1aa438dcbe87010bddd53884b1af6b22c940
  
  amd64:
    source: http://msft.digitalrivercontent.net/win/X17-59465.iso
    source_hash: sha256=36f4fa2416d0982697ab106e3a72d2e120dbcdb6cc54fd3906d06120d0653808

aik_iso:
  source: http://download.microsoft.com/download/8/E/9/8E9BBC64-E6F8-457C-9B8D-F6C9A16E6D6A/KB3AIK_EN.iso
  source_hash: sha256=c6639424b2cebabff3e851913e5f56410f28184bbdb648d5f86c05d93a4cebba
  name: kb3aik.iso

clonezilla_iso:
  source: http://downloads.sourceforge.net/project/clonezilla/clonezilla_live_stable/2.2.2-37/clonezilla-live-2.2.2-37-i686-pae.iso
  source_hash: sha256=e057437c82127dc7188b5b52b012c5476b6e73a31863c6232874e52fac097e71
  name: clonezilla-i386.iso

chrome_standalone_enterprise_msi:
  source: https://dl.google.com/edgedl/chrome/install/GoogleChromeStandaloneEnterprise.msi
  source_hash: sha256=c7090500b6761af8bdd51a4814b13ddae764dffbb332e569ef4b10441bb3ca89
  name: google-chrome-enterprise.msi

mdt-i386_msi:
  source: http://download.microsoft.com/download/B/F/5/BF5DF779-ED74-4BEC-A07E-9EB25694C6BB/MicrosoftDeploymentToolkit2013_x86.msi

mdt-amd64_msi:
  source: http://download.microsoft.com/download/B/F/5/BF5DF779-ED74-4BEC-A07E-9EB25694C6BB/MicrosoftDeploymentToolkit2013_x64.msi

mdt-docs_zip:
  source: http://download.microsoft.com/download/B/F/5/BF5DF779-ED74-4BEC-A07E-9EB25694C6BB/MDT%202013%20Documentation.zip


salt_windows_installer_files:
  i386:
    source: https://docs.saltstack.com/downloads/Salt-Minion-2014.1.3-1-win32-Setup.exe
  amd64:
    source: https://docs.saltstack.com/downloads/Salt-Minion-2014.1.3-1-AMD64-Setup.exe

cached_iso_files:
  - aik_iso
  - clonezilla_iso

python27-msi:
  source: https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi
  source_hash: sha256=cfa801a6596206ec7476e9bc2687fcd331c514b3dd92ffc3cd7d63e749ba0b2f
  name: python-2.7.6.msi


cached_windows_files:
  - chrome_standalone_enterprise_msi
  - python27-msi

  
