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

msiexec /qb /i python-2.7.6.amd64.msi ALLUSERS=1

c:\Python27\python %Z%\install.py


@pause