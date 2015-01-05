# -*- mode: yaml -*-

{% set parent_path = '/vagrant/vagrant/cache' %}
internet_resources:
  win7_ultimate_iso_i386:
    source: http://msft.digitalrivercontent.net/win/X17-59463.iso
    source_hash: sha256=e2c009a66d63a742941f5087acae1aa438dcbe87010bddd53884b1af6b22c940
    name: {{ parent_path }}/win7-ultimate-i386.iso
    
  win7_ultimate_iso_amd64:
    source: http://msft.digitalrivercontent.net/win/X17-59465.iso
    source_hash: sha256=36f4fa2416d0982697ab106e3a72d2e120dbcdb6cc54fd3906d06120d0653808
    name: {{ parent_path }}/win7-ultimate-amd64.iso

  aik_iso:
    source: http://download.microsoft.com/download/8/E/9/8E9BBC64-E6F8-457C-9B8D-F6C9A16E6D6A/KB3AIK_EN.iso
    source_hash: sha256=c6639424b2cebabff3e851913e5f56410f28184bbdb648d5f86c05d93a4cebba
    name: {{ parent_path}}/kb3aik.iso
