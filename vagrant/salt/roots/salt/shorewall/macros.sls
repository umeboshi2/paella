#!pydsl
# -*- mode: python -*-

def macro_deploy_path(macro):
    return '/etc/shorewall/macro.%s' % macro

def template_path(macro):
    return 'salt://shorewall/templates/macros/macro.%s' % macro




macros = ['BootpC','BootpS', 'DHCP','GkrellmD',
          'MountD', 'NFS', 'Portmap', 'StatD',
          'ManageSieve', 'SaltMaster']


for macro in macros:
    mfile = state(macro_deploy_path(macro))
    mfile.file('managed',
               source=template_path(macro),
               template='mako',
               user='root',
               group='root',
               mode='0644')
    

