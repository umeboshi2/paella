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
  name: chrome/google-chrome-enterprise.msi

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
  name: python/python-2.7.6.msi

vcredist_x86.exe:
  source: http://download.microsoft.com/download/d/d/9/dd9a82d0-52ef-40db-8dab-795376989c03/vcredist_x86.exe
  source_hash: sha256=41f45a46ee56626ff2699d525bb56a3bb4718c5ca5f4fb5b3b38add64584026b
  name: vcredist/vcredist_x86.exe

MicrosoftDeploymentToolkit2012_x86.msi:
  name: mdt2012/MicrosoftDeploymentToolkit2012_x86.msi
  source: http://download.microsoft.com/download/b/3/a/b3a89fae-f7bf-4e7c-b208-223b991e9c30/MicrosoftDeploymentToolkit2012_x86.msi
  source_hash: sha256=bf52b31e7c127d153206d9c6433fe0269547a00f176ddce74d936d9c95496e28


msysgit:
  source: https://github.com/msysgit/msysgit/releases/download/Git-1.9.2-preview20140411/Git-1.9.2-preview20140411.exe
  source_hash: sha256=0d459304a9994292635d341e698a2b8a275c0294d7159ba57ab8f917da968c7a
  name: msysgit/Git-1.9.2-preview20140411.exe
  
7zip-install.exe:
  source: http://downloads.sourceforge.net/project/sevenzip/7-Zip/9.20/7z920.exe?r=http%3A%2F%2Fwww.7-zip.org%2F&ts=1399403652&use_mirror=superb-dca2
  source_hash: sha256=1e2f2a8fb52d3972b9b65b8ad1bebb66965c47a2994f89b3d652c31e6f6e4c3c
  name: 7zip/7zip-install.exe


devkit-ruby-mingw-i386:
  source: http://cdn.rubyinstaller.org/archives/devkits/DevKit-mingw64-32-4.7.2-20130224-1151-sfx.exe
  source_hash: md5=9383f12958aafc425923e322460a84de
  name: DevKit-mingw64-32-4.7.2-20130224-1151-sfx.exe

devkit-ruby-mingw-amd64:
  source: http://cdn.rubyinstaller.org/archives/devkits/DevKit-mingw64-64-4.7.2-20130224-1432-sfx.exe
  source_hash: md5=ce99d873c1acc8bffc639bd4e764b849
  name: DevKit-mingw64-64-4.7.2-20130224-1432-sfx.exe

zeromq-3.2.4-windows-source-zip:
  name: zeromq-3.2.4.zip
  source: http://download.zeromq.org/zeromq-3.2.4.zip
  source_hash: sha1=7e2bd51a8dfd4510049170f2f041bcbd82ec84c0

openssl-source-tarball:
  name: openssl-1.0.1g.tar.gz
  source: http://www.openssl.org/source/openssl-1.0.1g.tar.gz
  source_hash: sha1=b28b3bcb1dc3ee7b55024c9f795be60eb3183e3c


activestate-perl-i386-msi:
  source: http://downloads.activestate.com/ActivePerl/releases/5.18.2.1802/ActivePerl-5.18.2.1802-MSWin32-x86-64int-298023.msi
  name: ActivePerl-5.18.2.1802-MSWin32-x86-64int-298023.msi
  source_hash: sha256=b6b46b7d16c83aad9c76934143dbb6fabb8624009ef9e5d542ba891e90bce2a0

activestate-perl-amd64-msi:
  source: http://downloads.activestate.com/ActivePerl/releases/5.18.2.1802/ActivePerl-5.18.2.1802-MSWin32-x64-298023.msi
  name: ActivePerl-5.18.2.1802-MSWin32-x64-298023.msi
  source_hash: sha256=4d0bbe46d6e1bba5d197bbc49ee2eb4901bec8277f213abfb52deb01473d0c71

win-builds-bundle-zip:
  source: http://win-builds.org/stable/win-builds-bundle-1.3.0.zip
  source_hash: sha256=39452620ad67bb292d6910bba9dd79fcce17ddd5e9774d26c0b27ea8ddec4c5e
  name: win-builds-bundle-1.3.0.zip


cached_windows_files:
  - chrome_standalone_enterprise_msi
  - python27-msi
  # vcredist_x86 should be removed if possible
  - vcredist_x86.exe
  - msysgit
  - MicrosoftDeploymentToolkit2012_x86.msi
  - 7zip-install.exe
  - zeromq-3.2.4-windows-source-zip
  # use MinGW to build openssl source tarball
  - openssl-source-tarball
  - activestate-perl-i386-msi
  - activestate-perl-amd64-msi
  - win-builds-bundle-zip


#http://www.freecommander.com/FreeCommanderXE_portable.zip

#http://sourceforge.net/projects/mingw-w64/files/latest/download?source=files

#http://prdownloads.sourceforge.net/nsis/nsis-2.46-setup.exe

# mingw-64 x86
#http://downloads.sourceforge.net/project/mingwbuilds/host-windows/releases/4.8.1/32-bit/threads-win32/sjlj/x32-4.8.1-release-win32-sjlj-rev5.7z

# mingw-64 x64
#http://downloads.sourceforge.net/project/mingwbuilds/host-windows/releases/4.8.1/64-bit/threads-win32/seh/x64-4.8.1-release-win32-seh-rev5.7z