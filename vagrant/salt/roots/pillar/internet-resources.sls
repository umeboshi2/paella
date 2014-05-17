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

python27-amd64-msi:
  source: https://www.python.org/ftp/python/2.7.6/python-2.7.6.amd64.msi
  source_hash: sha256=3793cb8874f5e156a161239fea04ad98829d4ecf623d52d43513780837eb4807
  name: python-2.7.6.amd64.msi


MicrosoftDeploymentToolkit2012_x86.msi:
  name: mdt2012/MicrosoftDeploymentToolkit2012_x86.msi
  source: http://download.microsoft.com/download/b/3/a/b3a89fae-f7bf-4e7c-b208-223b991e9c30/MicrosoftDeploymentToolkit2012_x86.msi
  source_hash: sha256=bf52b31e7c127d153206d9c6433fe0269547a00f176ddce74d936d9c95496e28


msysgit:
  source: https://github.com/msysgit/msysgit/releases/download/Git-1.9.2-preview20140411/Git-1.9.2-preview20140411.exe
  source_hash: sha256=0d459304a9994292635d341e698a2b8a275c0294d7159ba57ab8f917da968c7a
  name: msysgit/Git-1.9.2-preview20140411.exe
  
7zip-install.msi:
  source: http://downloads.sourceforge.net/project/sevenzip/7-Zip/9.20/7z920.msi
  source_hash: sha256=fe4807b4698ec89f82de7d85d32deaa4c772fc871537e31fb0fccf4473455cb8
  name: 7z920.msi

7zip-install-x64-msi:
  source: http://downloads.sourceforge.net/sevenzip/7z920-x64.msi
  source_hash: sha256=62df458bc521001cd9a947643a84810ecbaa5a16b5c8e87d80df8e34c4a16fe2
  name: 7z920-x64.msi

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

pywin32-219-zip:
  source: http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/pywin32-219.zip/download
  source_hash: sha256=30c3dbcd45d0c126ad9102d4bbcdeb6b9846869d0b1721faa4f8c9b563ccdb49
  name: pywin32-219.zip

activestate-perl-i386-msi:
  source: http://downloads.activestate.com/ActivePerl/releases/5.18.2.1802/ActivePerl-5.18.2.1802-MSWin32-x86-64int-298023.msi
  name: ActivePerl-5.18.2.1802-MSWin32-x86-64int-298023.msi
  source_hash: sha256=b6b46b7d16c83aad9c76934143dbb6fabb8624009ef9e5d542ba891e90bce2a0

activestate-perl-amd64-msi:
  source: http://downloads.activestate.com/ActivePerl/releases/5.18.2.1802/ActivePerl-5.18.2.1802-MSWin32-x64-298023.msi
  name: ActivePerl-5.18.2.1802-MSWin32-x64-298023.msi
  source_hash: sha256=4d0bbe46d6e1bba5d197bbc49ee2eb4901bec8277f213abfb52deb01473d0c71



mingw-w64-x86:
  source: http://downloads.sourceforge.net/project/mingwbuilds/host-windows/releases/4.8.1/32-bit/threads-win32/sjlj/x32-4.8.1-release-win32-sjlj-rev5.7z
  source_hash: sha256=6d00011b9fb8c916f2a3ba8b57941ebe90352c987258a53302137f757fcc0e00
  name: x32-4.8.1-release-win32-sjlj-rev5.7z

mingw-w64-x64:
  source: http://downloads.sourceforge.net/project/mingwbuilds/host-windows/releases/4.8.1/64-bit/threads-win32/seh/x64-4.8.1-release-win32-seh-rev5.7z
  source_hash: sha256=8a8c23e72478a4f8fec2ecc8a6e35225aaa2334fb235aac9e2b3ffc3ffd77f7e
  name: x64-4.8.1-release-win32-seh-rev5.7z

gedit-exe:
  source: http://ftp.gnome.org/pub/GNOME/binaries/win32/gedit/2.30/gedit-setup-2.30.1-1.exe
  source_hash: sha256=a611e9c233321c29cf8307d94d37e5a9028b2d99bba9ecd06ebb9a670cfb29a2
  name: gedit-setup-2.30.1-1.exe

nsis-exe:
  source: http://prdownloads.sourceforge.net/nsis/nsis-2.46-setup.exe?download
  source_hash: sha256=69c2ae5c9f2ee45b0626905faffaa86d4e2fc0d3e8c118c8bc6899df68467b32
  name: nsis-2.46-setup.exe

mingw-get-setup-exe:
  source: http://sourceforge.net/projects/mingw/files/Installer/mingw-get-setup.exe/download
  source_hash: sha256=aab27bd5547d35dc159288f3b5b8760f21b0cfec86e8f0032b49dd0410f232bc
  name: mingw-get-setup.exe

mingw-get-bin-zip:
  source: http://sourceforge.net/projects/mingw/files/Installer/mingw-get/mingw-get-0.6.2-beta-20131004-1/mingw-get-0.6.2-mingw32-beta-20131004-1-bin.zip/download
  source_hash: sha256=2e0e9688d42adc68c5611759947e064156e169ff871816cae52d33ee0655826d
  name: mingw-get-bin.zip
  #name: mingw-get-0.6.2-mingw32-beta-20131004-1-bin.zip

swigwin-3.0.0-zip:
  source: http://sourceforge.net/projects/swig/files/swigwin/swigwin-3.0.0/swigwin-3.0.0.zip/download
  source_hash: sha256=be829be4b87cc6a24d88cd9771a8c3c2eabcc72095f4d370d01a0080aae1a060
  name: swigwin-3.0.0.zip

ez_setup_py:
  source: https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
  source_hash: sha256=bda2153493b18212a87c6720d6c581887a980f14c8cacceb2fe864b88efc5424
  name: ez_setup.py

codeblocks-setup-exe:
  source: http://prdownload.berlios.de/codeblocks/codeblocks-13.12-setup.exe
  source_hash: sha256=aa2df2f614f24ff3f3a9799e30708577ef15e5582c2ab967e710729aa18ae097
  name: codeblocks-13.12-setup.exe


# http://sourceforge.net/projects/mingw/files/Installer/mingw-get/mingw-get-0.6.2-beta-20131004-1/mingw-get-0.6.2-mingw32-beta-20131004-1-bin.zip/download

dotnet-4.5-exe:
  source: http://download.microsoft.com/download/1/6/7/167F0D79-9317-48AE-AEDB-17120579F8E2/NDP451-KB2858728-x86-x64-AllOS-ENU.exe
  source_hash: sha256=5ded8628ce233a5afa8e0efc19ad34690f05e9bb492f2ed0413508546af890fe
  name: microsoft-dotnet-4.5.exe

dotnet-4.0-exe:
  source: http://download.microsoft.com/download/9/5/A/95A9616B-7A37-4AF6-BC36-D6EA96C8DAAE/dotNetFx40_Full_x86_x64.exe
  source_hash: sha256=65e064258f2e418816b304f646ff9e87af101e4c9552ab064bb74d281c38659f
  name: dotNetFx40_Full_x86_x64.exe


cached_windows_files:
  - chrome_standalone_enterprise_msi
  - 7zip-install.msi
  - 7zip-install-x64-msi
  - python27-amd64-msi
  - python27-msi
  - activestate-perl-i386-msi
  - activestate-perl-amd64-msi
  - mingw-w64-x86
  - mingw-w64-x64
  - mingw-get-bin-zip
  - mingw-get-setup-exe
  - swigwin-3.0.0-zip
  - ez_setup_py
  - msysgit
  - gedit-exe
  - nsis-exe
  - MicrosoftDeploymentToolkit2012_x86.msi
  - zeromq-3.2.4-windows-source-zip
  # use MinGW to build openssl source tarball
  - openssl-source-tarball
  - pywin32-219-zip
  # this won't be needed for autobuilding but will
  # help get things going
  - codeblocks-setup-exe
  - dotnet-4.0-exe


#http://www.freecommander.com/FreeCommanderXE_portable.zip

#http://sourceforge.net/projects/mingw-w64/files/latest/download?source=files

#http://prdownloads.sourceforge.net/nsis/nsis-2.46-setup.exe

#####################################################
## Not using these resources
#####################################################
mdt-i386_msi:
  source: http://download.microsoft.com/download/B/F/5/BF5DF779-ED74-4BEC-A07E-9EB25694C6BB/MicrosoftDeploymentToolkit2013_x86.msi

mdt-amd64_msi:
  source: http://download.microsoft.com/download/B/F/5/BF5DF779-ED74-4BEC-A07E-9EB25694C6BB/MicrosoftDeploymentToolkit2013_x64.msi

mdt-docs_zip:
  source: http://download.microsoft.com/download/B/F/5/BF5DF779-ED74-4BEC-A07E-9EB25694C6BB/MDT%202013%20Documentation.zip


win-builds-bundle-zip:
  source: http://win-builds.org/stable/win-builds-bundle-1.3.0.zip
  source_hash: sha256=39452620ad67bb292d6910bba9dd79fcce17ddd5e9774d26c0b27ea8ddec4c5e
  name: win-builds-bundle-1.3.0.zip


vcredist_x86.exe:
  source: http://download.microsoft.com/download/d/d/9/dd9a82d0-52ef-40db-8dab-795376989c03/vcredist_x86.exe
  source_hash: sha256=41f45a46ee56626ff2699d525bb56a3bb4718c5ca5f4fb5b3b38add64584026b
  name: vcredist/vcredist_x86.exe
