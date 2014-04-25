# -*- mode: yaml -*-

samba-support-packages:
  pkg.installed:
    - pkgs:
      - smbclient

samba-server:
  pkg.installed:
    - name: samba
    - requires:
      - pkg: samba-support-packages

  service:
    - name: samba
    - running
    #- watch:
    #  - file: /etc/apache2/paella.wsgi
    #  - file: /etc/apache2/conf.d/debrepos
    #  - file: /etc/apache2/conf.d/paella
  

%if pillar['paella_enable_software_download_states']:

win7-ultimate-i386-iso:
  file.managed:
    - source: http://msft.digitalrivercontent.net/win/X17-59463.iso
    - source_hash: sha256=e2c009a66d63a742941f5087acae1aa438dcbe87010bddd53884b1af6b22c940
    - name: /vagrant/vagrant/cache/win7-ultimate-i386.iso

kb3aik_en.iso:
  file.managed:
    - source: http://download.microsoft.com/download/8/E/9/8E9BBC64-E6F8-457C-9B8D-F6C9A16E6D6A/KB3AIK_EN.iso
    - source_hash: sha256=c6639424b2cebabff3e851913e5f56410f28184bbdb648d5f86c05d93a4cebba
    - name: /vagrant/vagrant/cache/kb3aik.iso


%endif
