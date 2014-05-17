import os, sys
import subprocess

base_python_path = 'c:\\Python27'
python_scripts_path = os.path.join(base_python_path, 'Scripts')
print "Placing python in PATH"
oldpath = os.environ['PATH']
newpath = '%s;%s;%s' % (oldpath, base_python_path, python_scripts_path)
os.environ['PATH'] = newpath
del oldpath
del newpath

# http://ascend4.org/Setting_up_a_MinGW-w64_build_environment
start_dir = os.getcwd()
print start_dir



CROSSCOMPILE = False

msiexec_prefix = ['msiexec', '/qb', '/i']
arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()

msi_apps = []

if arch == 'amd64':
    sevenzip = '7z920-x64.msi'
    msi_apps.append(sevenzip)
    perldirname = 'c:\\Perl64'
    if not os.path.isdir(perldirname):
        ActivePerl = 'ActivePerl-5.18.2.1802-MSWin32-x64-298023.msi'
        msi_apps.append(ActivePerl)
else:
    sevenzip = '7z920.msi'
    msi_apps.append(sevenzip)
    perldirname = 'c:\\Perl'
    if not os.path.isdir(perldirname):
        ActivePerl = 'ActivePerl-5.18.2.1802-MSWin32-x86-64int-298023.msi'
        msi_apps.append(ActivePerl)
    
chrome = 'google-chrome-enterprise.msi'
msi_apps.append(chrome)

for app in msi_apps:
    cmd = msiexec_prefix + [app]
    print "Installing %s" % app
    subprocess.check_call(cmd)

if CROSSCOMPILE and arch == 'amd64':
    python32 = 'python-2.7.6.msi'
    pyinstall_cmd = ['msiexec', '/qb', '/i', python32, 'ALLUSERS=1',
                     'TARGETDIR=C:\\Python27_32']
    print "Installing python32", python32
    subprocess.check_call(pyinstall_cmd)

# http://wpkg.org/Inno_Setup

gedit_dir = 'c:\\Program Files\\gedit'
if arch == 'amd64':
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

# setup ez_install
home_directory = '%s%s' % (os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
ez_setup_script = os.path.join(start_dir, 'ez_setup.py')
ez_setup_cmd = ['python', ez_setup_script, '--insecure']
os.chdir(home_directory)
print "Installing ez_install for python"
subprocess.check_call(ez_setup_cmd)

# install pip
print "Installing pip"
cmd = ['easy_install', 'pip']
subprocess.check_call(cmd)

# use pip to install some python packages
packages = ['requests', 'winshell', 'Mako']
for p in packages:
    cmd = ['pip', 'install', p]
    subprocess.check_call(cmd)
    



if arch == 'x86':
    szip_exe = 'C:\\Program Files\\7-Zip\\7z.exe'
else:
    raise RuntimeError, "amd64 not supported yet"




# make parent mingw path
mingw_parent_path = 'c:\\MinGW'
mingw_get_bin_install_path = mingw_parent_path
if not os.path.isdir(mingw_get_bin_install_path):
    os.makedirs(mingw_get_bin_install_path)
os.chdir(mingw_get_bin_install_path)


mingw_get_exe = os.path.join(mingw_get_bin_install_path, 'bin', 'mingw-get.exe')
if not os.path.isfile(mingw_get_exe):
    mingw_get_zipfile = os.path.join(start_dir, 'mingw-get-bin.zip')
    print "Unzipping", mingw_get_zipfile
    cmd = [szip_exe, 'x', mingw_get_zipfile]
    subprocess.check_call(cmd)


if CROSSCOMPILE:
    defaults_filename = os.path.join(mingw_get_bin_install_path,
                                     'var', 'lib', 'mingw-get',
                                     'data', 'defaults.xml')
    if not os.path.isfile(defaults_filename):
        raise RuntimeError, "%s doesn't exist." % defaults_filename

    print "Updating", defaults_filename

    contents = file(defaults_filename).read()
    contents = contents.replace('%R/msys/1.0', '%R/../msys')
    with file(defaults_filename, 'w') as df:
        df.write(contents)


    

msys_packages = ['core', 'base', 'vim', 'wget', 'patch', 'flex', 'bison']
msys_packages = ['msys-%s' % p for p in msys_packages]
cmd = [mingw_get_exe, 'install'] + msys_packages
print "Executing:", ' '.join(cmd)
subprocess.check_call(cmd)

fstab = os.path.join(mingw_parent_path, 'msys', '1.0', 'etc', 'fstab')
with file(fstab, 'w') as outfile:
    fstab_lines = [
        'c:/MinGW\t/mingw\n',
        ]
    for line in fstab_lines:
        outfile.write(line)


mingw_packages = ['gcc', 'g++']
cmd = [mingw_get_exe, 'install'] + mingw_packages
print "Executing:", ' '.join(cmd)
subprocess.check_call(cmd)

                 

print "Everything installed!"
print os.environ['PATH']


