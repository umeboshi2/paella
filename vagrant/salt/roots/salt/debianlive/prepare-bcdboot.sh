#!/bin/bash
set -e

DRIVE=$1

#echo "Copying bootloader to master boot record."
#dd if=/mnt/bootloader.bin $DRIVE

echo "Creating WinPE Virtual Machine"

VBoxManage createvm --name winpe --register

echo "Giving WinPE Virtual Machine 256MB of memory"

VBoxManage modifyvm winpe --memory 256

echo "Creating VMDK to point to $DRIVE"

VBoxManage internalcommands createrawvmdk -filename ~/sysdrive.vmdk -rawdisk $DRIVE

echo "Creating SATA controller on WinPE Virtual Machine for cdrom"

VBoxManage storagectl winpe --name "ide-controller-main" --add ide

echo "Attaching BCD Auto ISO to WinPE Virtual Machine"

VBoxManage storageattach winpe --storagectl "ide-controller-main" \
    --port 0 --device 0 --type dvddrive --medium /srv/incoming/bcdauto.iso 

echo "Creating SATA controller on WinPE Virtual Machine for system disk"

VBoxManage storagectl winpe --name "sata-controller-main" --add sata 


echo "Attaching System Hard Drive to WinPE Virtual Machine"

VBoxManage storageattach winpe --storagectl "sata-controller-main" \
    --port 0 --device 0 --type hdd --medium ~/sysdrive.vmdk

echo "Executing WinPE Virtual Machine......(please wait)..."

VBoxHeadless --startvm winpe

echo "WinPE Virtual Machine execution complete."
echo "System should be ready to boot!"