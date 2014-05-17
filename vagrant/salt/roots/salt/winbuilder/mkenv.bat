@echo off

if not %Z%. == . goto got_drive
set Z=Z:
:got_drive

:: If drive is already mapped, do nothing
if not %Z_PATH%. == . goto got_path
set Z_PATH=\\paella\incoming
:got_path

:try_again
set COUNT=x%COUNT%
if not %COUNT% == xxxxxxxxxxxxxxxxxxxxxx goto mapit
echo Too many failed attempts; sorry...
goto hang

:mapit
echo Mapping %Z_PATH% on %Z%

net use %Z% %Z_PATH% /persistent:no
if exist %Z%\ goto mapped
net use %Z% /delete
echo Mapping failed, retry in
:: wait for ten seconds
ping -n 10 localhost > nul
goto try_again

:mapped
:: if not exist $Z%\ goto mapit
echo Finished
goto end

:hang
goto hang

:end

cd /D %Z%\windows

if "%PROCESSOR_ARCHITECTURE%" == "AMD64" goto install_python64
:install_python32
echo Install Python %PROCESSOR_ARCHITECTURE% 32bit
msiexec /qb /i python-2.7.6.msi ALLUSERS=1
goto run_install


:install_python64
echo Install Python %PROCESSOR_ARCHITECTURE% 64bit
msiexec /qb /i python-2.7.6.amd64.msi ALLUSERS=1
goto run_install


:run_install
:: FIXME do this in install.py script
:: echo Install ez_setup.py
:: c:\Python27\python %Z%\windows\ez_setup.py

echo Run install
c:\Python27\python %Z%\install.py


@pause