# -*- mode: yaml -*-

{% set parent_path = '/vagrant/vagrant/cache/windows' %}
internet_resources:
  salt_windows_installer_i386:
    source: http://docs.saltstack.com/downloads/Salt-Minion-2014.7.0-1-win32-Setup.exe
    source_hash: md5=91872fcdca3f94f961fe40737e5b9aea
    name: {{ parent_path }}/salt-minion-i386-setup.exe
  salt_windows_installer_amd64:
    source: http://docs.saltstack.com/downloads/Salt-Minion-2014.7.0-AMD64-Setup.exe
    source_hash: md5=9ed83f28b5b620c4f51befc40aea7784
    name: {{ parent_path }}/salt-minion-amd64-setup.exe
    
  7zip-install.msi:
    source: http://downloads.sourceforge.net/project/sevenzip/7-Zip/9.20/7z920.msi
    source_hash: sha256=fe4807b4698ec89f82de7d85d32deaa4c772fc871537e31fb0fccf4473455cb8
    name: {{ parent_path }}/7z920.msi

  7zip-install-x64-msi:
    source: http://downloads.sourceforge.net/sevenzip/7z920-x64.msi
    source_hash: sha256=62df458bc521001cd9a947643a84810ecbaa5a16b5c8e87d80df8e34c4a16fe2
    name: {{ parent_path }}/7z920-x64.msi

  python27-msi:
    source: https://www.python.org/ftp/python/2.7.6/python-2.7.6.msi
    source_hash: sha256=cfa801a6596206ec7476e9bc2687fcd331c514b3dd92ffc3cd7d63e749ba0b2f
    name: {{ parent_path }}/python-2.7.6.msi
  python27-amd64-msi:
    source: https://www.python.org/ftp/python/2.7.6/python-2.7.6.amd64.msi
    source_hash: sha256=3793cb8874f5e156a161239fea04ad98829d4ecf623d52d43513780837eb4807
    name: {{ parent_path }}/python-2.7.6.amd64.msi


  MicrosoftDeploymentToolkit2012_x86.msi:
    name: {{ parent_path }}/mdt2012/MicrosoftDeploymentToolkit2012_x86.msi
    source: http://download.microsoft.com/download/b/3/a/b3a89fae-f7bf-4e7c-b208-223b991e9c30/MicrosoftDeploymentToolkit2012_x86.msi
    source_hash: sha256=bf52b31e7c127d153206d9c6433fe0269547a00f176ddce74d936d9c95496e28


  gedit-exe:
    source: http://ftp.gnome.org/pub/GNOME/binaries/win32/gedit/2.30/gedit-setup-2.30.1-1.exe
    source_hash: sha256=a611e9c233321c29cf8307d94d37e5a9028b2d99bba9ecd06ebb9a670cfb29a2
    name: {{ parent_path }}/gedit-setup-2.30.1-1.exe


  #chrome_standalone_enterprise_msi:
  #  source: https://dl.google.com/edgedl/chrome/install/GoogleChromeStandaloneEnterprise.msi
  #  source_hash: sha256=f5520d79d8f85929931b369040095530a9c1201d55415884b50cbb9c087f94cc
  #  name: {{ parent_path }}/google-chrome-enterprise.msi
  
    



