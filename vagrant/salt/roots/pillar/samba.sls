# -*- mode: yaml -*-
{% from 'bvars.jinja' import paella %}
{% set mswin = paella.install_mswindows_machines %}

samba:
  samba_sections:
    global:
      # browsing id
      workgroup: WORKGROUP
      server_string: '%h server'
      dns_proxy: 'no'
      name_resolve_order: lmhosts host wins
      # debug/accounting
      log_file: '/var/log/samba/log.%m'
      max_log_size: 1000
      syslog: 0
      panic_action: '/usr/share/samba/panic-action %d'
      # authentication
      security: user
      passdb_backend: tdbsam
      obey_pam_restrictions: 'yes'
      unix_password_sync: 'yes'
      passwd_program: '/usr/bin/passwd %u'
      passwd_chat: '*Enter\snew\s*\spassword:* %n\n *Retype\snew\s*\spassword:* %n\n *password\supdated\ssuccessfully* .'
      pam_password_change: 'yes'
      map_to_guest: bad user
      # domains
      #domain_logons: 'yes'
      usershare_allow_guests: 'yes'
    homes:
      comment: Home Directories
      browseable: 'no'
      read_only: 'yes'
      create_mask: '0700'
      directory_mask: '0700'
      valid_users: '%S'
    printers:
      comment: All Printers
      browseable: 'no'
      path: /var/spool/samba
      printable: 'yes'
      guest_ok: 'no'
      read_only: 'yes'
      create_mask: '0700'
    print$:
      comment: Printer Drivers
      path: /var/lib/samba/printers
      browseable: 'yes'
      read_only: 'yes'
      guest_ok: 'no'
    # mounted iso files need disabled oplocks
    # oplocks need to be disabled for auto install
    # to work faster.  Locks are not necessary on
    # a read only filesystem.
    win7-i386:
      comment: Win7 i386 share
      read_only: 'yes'
      locking: 'no'
      path: /srv/shares/win7/i386
      guest_ok: 'yes'
      oplocks: 'no'
    win7-amd64:
      comment: Win7 amd64 share
      read_only: 'yes'
      locking: 'no'
      path: /srv/shares/win7/amd64
      guest_ok: 'yes'
      oplocks: 'no'
    aik:
      comment: AIK share
      read_only: 'yes'
      locking: 'no'
      path: /srv/shares/aik
      guest_ok: 'yes'
      oplocks: 'no'
    incoming:
      comment: incoming share
      read_only: 'no'
      locking: 'no'
      path: /srv/shares/incoming
      guest_ok: 'yes'
      oplocks: 'no'
    winstall:
      comment: windows install share
      read_only: 'no'
      locking: 'no'
      path: /srv/shares/winstall
      guest_ok: 'yes'
    
    
