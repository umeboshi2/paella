#!/usr/bin/python -i

import sys
import os
import popen2
import stat
import traceback
import signal
import string
import time
import copy
import parted

# Arch-specific modules
import partition

try:

        drvlist = []
        parted.init()
        parted.device_probe_all()

        print "Examining drives..."
        try:
           drvinstlist = [parted.get_devices()[0]]
        except:
           print "No available drives found!"
           killsystem()

        bootdrv = ""

        for drv in drvinstlist:
            if not bootdrv:
                bootdrv = drv.get_path()

            drvdisk = drv.disk_open()
            if drvdisk is not None:
                partlist = drvdisk.get_part_list()
                isdata = 0
                for part in partlist:
                    if part.get_type() != parted.PARTITION_FREESPACE:
                        isdata = 1

                drvdisk.close()

    # Partition and format drive.
        for drv in drvinstlist:
            print "Partitioning drive %s..." % drv.get_path()

            drvobj = partition.Partition(drv)
            drvsectors = drv.get_length()
            drvobj.create_partition_table()

            partabssect = 0
            # for reference, partcfg at this point looks like:
            # [['ext2', '80%', '/', ['primary']], ['swap', '256M', 'swap', ['primary']]]
            for partinfo in partcfg:
                if partinfo[2] == "/":
                    rootpart = partinfo
                partsizetype = string.upper(partinfo[1][-1])
                if partsizetype == "M":
                    partsize = string.atoi(partinfo[1][:-1])
                    partsect = int(float(partsize) * 1024 * 1024 / parted.SECTOR_SIZE)
                    partabssect = partabssect + partsect
                elif partsizetype != "%":
                    raise RuntimeError, "invalid partition size specifier"
            partremsect = drvsectors - partabssect - curpartend

            for (partfs, partsizestr, partmount, parthints) in partcfg:
                print "Creating %s partition for %s..." % (partfs, partmount)
                partsizetype = string.upper(partsizestr[-1])
                partsize = string.atoi(partsizestr[:-1])

                if partfs == "swap":
                    partfs = "linux-swap"
                partfstype = parted.file_system_type_get(partfs)

                if partsizetype == "%":
                    partsect = int(partremsect * (float(partsize) / 100))
                else:
                    partsect = int(float(partsize) * 1024 * 1024 / parted.SECTOR_SIZE)

                partdevice = drvobj.create_partition(curpartend,
                                                     curpartend + partsect - 1,
                                                     partfstype, parthints)
                mountlist.append([partdevice, partmount, partfs])
                curpartend = curpartend + partsect

            drvobj.commit_changes()

            drvdisk = drv.disk_open()
            for (partdevice, partmount, partfs) in mountlist:
                print "Creating %s file system on %s..." % (partfs, partdevice)

                drvpartnumstr = partdevice[-2:]
                if drvpartnumstr[0] not in string.digits:
                    drvpartnumstr = drvpartnumstr[1]
                drvpartnum = string.atoi(drvpartnumstr)

                partfstype = parted.file_system_type_get(partfs)
                drvnewpart = drvdisk.get_partition(drvpartnum)
                parted.FileSystem(drvnewpart.get_geom(), partfstype).close()

            drvdisk.close()
            drv.close()

    # Since we're done with partitioning, we can call this now.  This
    # ensures that the partition table is reread by the system.  It's
    # important not to call parted for anything after this.

        parted.done()

