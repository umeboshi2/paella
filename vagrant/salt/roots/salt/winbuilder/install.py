import os, sys
import subprocess


# http://ascend4.org/Setting_up_a_MinGW-w64_build_environment
print "hello world"

start_dir = os.getcwd()
print start_dir

msiexec_prefix = ['msiexec', '/qb', '/i']
sevenzip = '7z920-x64.msi'
ActivePerl = 'ActivePerl-5.18.2.1802-MSWin32-x64-298023.msi'
chrome = 'google-chrome-enterprise.msi'

apps = [sevenzip, ActivePerl, chrome]
for app in apps:
    cmd = msiexec_prefix + [app]
    print "Installing %s" % app
    subprocess.check_call(cmd)


python32 = 'python-2.7.6.msi'
pyinstall_cmd = ['msiexec', '/qb', '/i', python32, 'ALLUSERS=1',
                 'TARGETDIR=C:\\Python27_32']
print "Installing python32", python32
subprocess.check_call(pyinstall_cmd)

# http://wpkg.org/Inno_Setup

gedit_dir = 'c:\\Program Files (x86)\\gedit'
if not os.path.isdir(gedit_dir):
    gedit = 'gedit-setup-2.30.1-1.exe'
    gedit_install_cmd = [gedit, '/sp-', '/silent', '/norestart']
    print "Installing gedit", gedit
    subprocess.check_call(gedit_install_cmd)
else:
    print "gedit seems to be installed."
    
# http://wpkg.org/Nullsoft_Install_System

nsis = 'nsis-2.46-setup.exe'
nsis_install_cmd = [nsis, '/S']
print "Installing NSIS", nsis
subprocess.check_call(nsis_install_cmd)

szip_exe = 'C:\\Program Files\\7-Zip\\7z.exe'

# make parent mingw path
mingw_parent_path = 'c:\\MinGW'
mingw_get_bin_install_path = os.path.join(mingw_parent_path, '32')
if not os.path.isdir(mingw_get_bin_install_path):
    os.makedirs(mingw_get_bin_install_path)
os.chdir(mingw_get_bin_install_path)



mingw_get_exe = os.path.join(mingw_get_bin_install_path, 'bin', 'mingw-get.exe')
if not os.path.isfile(mingw_get_exe):
    mingw_get_zipfile = os.path.join(start_dir, 'mingw-get-bin.zip')
    print "Unzipping", mingw_get_zipfile
    cmd = [szip_exe, 'x', mingw_get_zipfile]
    subprocess.check_call(cmd)


msys_parent_path = os.path.join(mingw_parent_path, 'msys')

msys_packages = ['core', 'base', 'vim', 'wget', 'patch', 'flex', 'bison']
msys_packages = ['msys-%s' % p for p in msys_packages]
cmd = [mingw_get_exe, 'install'] + msys_packages
print "Executing:", ' '.join(cmd)
subprocess.check_call(cmd)

fstab = os.path.join(msys_parent_path, 'etc', 'fstab')
with file(fstab, 'w') as outfile:
    mingw_line = '%s\t/mingw\n' % mingw_get_bin_install_path
    outfile.write(mingw_line)
    

print "Everything installed!"

