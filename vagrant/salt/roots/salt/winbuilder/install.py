import os, sys
import subprocess
print "hello world"

print os.getcwd()

msiexec_prefix = ['msiexec', '/qb', '/i']

sevenzip = '7z920-x64.msi'
ActivePerl = 'ActivePerl-5.18.2.1802-MSWin32-x64-298023.msi'
chrome = 'google-chrome-enterprise.msi'

apps = [sevenzip, ActivePerl, chrome]
for app in apps:
    cmd = msiexec_prefix + [app]
    print "Installing %s" % app
    subprocess.check_call(cmd)

print "Everything installed!"

