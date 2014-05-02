#!/bin/bash
set -e

DRIVE=$1
parted -s $DRIVE "mklabel msdos"
parted -s $DRIVE "mkpart primary ntfs 1 200MB"
parted -s $DRIVE "set 1 boot on"
parted -s $DRIVE "mkpart primary ntfs 200MB -0"

sysdevice=${DRIVE}1
windevice=${DRIVE}2

echo "Formatting system partition"
mkfs.ntfs -f -L System $sysdevice

echo "Formatting windows partition"
mkfs.ntfs -f -L Windows $windevice

echo "applying WIM $2 to $windevice"
wimlib-imagex apply $2 $windevice

echo "Copying bootloader to master boot record."
dd if=/mnt/bootloader.bin $DRIVE
