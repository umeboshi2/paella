# -*- mode: yaml -*-

{% set parent_path = '/vagrant/vagrant/cache/windows' %}
internet_resources:
  msysgit:
    source: https://github.com/msysgit/msysgit/releases/download/Git-1.9.2-preview20140411/Git-1.9.2-preview20140411.exe
    source_hash: sha256=0d459304a9994292635d341e698a2b8a275c0294d7159ba57ab8f917da968c7a
    name: {{ parent_path }}/msysgit/Git-1.9.2-preview20140411.exe
  
  devkit-ruby-mingw-i386:
    source: http://cdn.rubyinstaller.org/archives/devkits/DevKit-mingw64-32-4.7.2-20130224-1151-sfx.exe
    source_hash: md5=9383f12958aafc425923e322460a84de
    name: {{ parent_path }}/DevKit-mingw64-32-4.7.2-20130224-1151-sfx.exe

  devkit-ruby-mingw-amd64:
    source: http://cdn.rubyinstaller.org/archives/devkits/DevKit-mingw64-64-4.7.2-20130224-1432-sfx.exe
    source_hash: md5=ce99d873c1acc8bffc639bd4e764b849
    name: {{ parent_path }}/DevKit-mingw64-64-4.7.2-20130224-1432-sfx.exe

  zeromq-3.2.4-windows-source-zip:
    name: {{ parent_path }}/zeromq-3.2.4.zip
    source: http://download.zeromq.org/zeromq-3.2.4.zip
    source_hash: sha1=7e2bd51a8dfd4510049170f2f041bcbd82ec84c0

  openssl-source-tarball:
    name: {{ parent_path }}/openssl-1.0.1g.tar.gz
    source: http://www.openssl.org/source/openssl-1.0.1g.tar.gz
    source_hash: sha1=b28b3bcb1dc3ee7b55024c9f795be60eb3183e3c

  pywin32-219-zip:
    source: http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/pywin32-219.zip/download
    source_hash: sha256=30c3dbcd45d0c126ad9102d4bbcdeb6b9846869d0b1721faa4f8c9b563ccdb49
    name: {{ parent_path }}/pywin32-219.zip

  activestate-perl-i386-msi:
    source: http://downloads.activestate.com/ActivePerl/releases/5.18.2.1802/ActivePerl-5.18.2.1802-MSWin32-x86-64int-298023.msi
    name: {{ parent_path }}/ActivePerl-5.18.2.1802-MSWin32-x86-64int-298023.msi
    source_hash: sha256=b6b46b7d16c83aad9c76934143dbb6fabb8624009ef9e5d542ba891e90bce2a0

  activestate-perl-amd64-msi:
    source: http://downloads.activestate.com/ActivePerl/releases/5.18.2.1802/ActivePerl-5.18.2.1802-MSWin32-x64-298023.msi
    name: {{ parent_path }}/ActivePerl-5.18.2.1802-MSWin32-x64-298023.msi
    source_hash: sha256=4d0bbe46d6e1bba5d197bbc49ee2eb4901bec8277f213abfb52deb01473d0c71

  mingw-w64-x86:
    source: http://downloads.sourceforge.net/project/mingwbuilds/host-windows/releases/4.8.1/32-bit/threads-win32/sjlj/x32-4.8.1-release-win32-sjlj-rev5.7z
    source_hash: sha256=6d00011b9fb8c916f2a3ba8b57941ebe90352c987258a53302137f757fcc0e00
    name: {{ parent_path }}/x32-4.8.1-release-win32-sjlj-rev5.7z

  mingw-w64-x64:
    source: http://downloads.sourceforge.net/project/mingwbuilds/host-windows/releases/4.8.1/64-bit/threads-win32/seh/x64-4.8.1-release-win32-seh-rev5.7z
    source_hash: sha256=8a8c23e72478a4f8fec2ecc8a6e35225aaa2334fb235aac9e2b3ffc3ffd77f7e
    name: {{ parent_path }}/x64-4.8.1-release-win32-seh-rev5.7z

  nsis-exe:
    source: http://prdownloads.sourceforge.net/nsis/nsis-2.46-setup.exe?download
    source_hash: sha256=69c2ae5c9f2ee45b0626905faffaa86d4e2fc0d3e8c118c8bc6899df68467b32
    name: {{ parent_path }}/nsis-2.46-setup.exe

  mingw-get-setup-exe:
    source: http://sourceforge.net/projects/mingw/files/Installer/mingw-get-setup.exe/download
    source_hash: sha256=aab27bd5547d35dc159288f3b5b8760f21b0cfec86e8f0032b49dd0410f232bc
    name: {{ parent_path }}/mingw-get-setup.exe

  mingw-get-bin-zip:
    source: http://sourceforge.net/projects/mingw/files/Installer/mingw-get/mingw-get-0.6.2-beta-20131004-1/mingw-get-0.6.2-mingw32-beta-20131004-1-bin.zip/download
    source_hash: sha256=2e0e9688d42adc68c5611759947e064156e169ff871816cae52d33ee0655826d
    name: {{ parent_path }}/mingw-get-bin.zip

  swigwin-3.0.0-zip:
    source: http://sourceforge.net/projects/swig/files/swigwin/swigwin-3.0.0/swigwin-3.0.0.zip/download
    source_hash: sha256=be829be4b87cc6a24d88cd9771a8c3c2eabcc72095f4d370d01a0080aae1a060
    name: {{ parent_path }}/swigwin-3.0.0.zip

  ez_setup_py:
    source: https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py
    source_hash: sha256=28f6a6398e1b2037af9e8ea521d2355cbd195c496a896a88c4237ca6e49889d1
    name: {{ parent_path }}/ez_setup.py

  codeblocks-setup-exe:
    source: http://prdownload.berlios.de/codeblocks/codeblocks-13.12-setup.exe
    source_hash: sha256=aa2df2f614f24ff3f3a9799e30708577ef15e5582c2ab967e710729aa18ae097
    name: {{ parent_path }}/codeblocks-13.12-setup.exe

  dotnet-4.5-exe:
    source: http://download.microsoft.com/download/1/6/7/167F0D79-9317-48AE-AEDB-17120579F8E2/NDP451-KB2858728-x86-x64-AllOS-ENU.exe
    source_hash: sha256=5ded8628ce233a5afa8e0efc19ad34690f05e9bb492f2ed0413508546af890fe
    name: {{ parent_path }}/microsoft-dotnet-4.5.exe

  dotnet-4.0-exe:
    source: http://download.microsoft.com/download/9/5/A/95A9616B-7A37-4AF6-BC36-D6EA96C8DAAE/dotNetFx40_Full_x86_x64.exe
    source_hash: sha256=65e064258f2e418816b304f646ff9e87af101e4c9552ab064bb74d281c38659f
    name: {{ parent_path }}/dotNetFx40_Full_x86_x64.exe


