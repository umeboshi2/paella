# Autoinstaller partition code for MS-DOS style partitions.

# Copyright (c) 2001 Progeny Linux Systems, Inc.
# Written by Jeff Licquia.

# This module assumes that the parted subsystem has already been
# initialized fully; it simply stands in for certain calls that may be
# different for different partition types.

# from python-parted package
import parted

class Partition:
    def __init__(self, drive):
        self.drive = drive
        self.disk = None

        self.primarynum = 0
        self.extnum = 0
        self.isext = 0

    def get_freespace(self):
        if self.disk is None:
            self.disk = self.drive.disk_open()

        if self.disk is not None:
            freelist = []
            partlist = self.disk.get_part_list()
            for part in partlist:
                partnum = part.get_num()
                if part.get_type() == parted.PED_PARTITION_PRIMARY:
                    self.primarynum = partnum + 1
                elif part.get_type() == parted.PED_PARTITION_EXTENDED:
                    self.extnum = partnum + 1
                elif part.get_type() == parted.PED_PARTITION_LOGICAL:
                    self.isext = 1
                elif part.get_type() == parted.PED_PARTITION_FREESPACE:
                    freelist.append([part.get_geom().get_start(),
                                     part.get_geom().get_end()])

            if not self.primarynum:
                if self.isext:
                    self.primarynum = 2
                else:
                    self.primarynum = 1
            if not self.extnum:
                self.extnum = 5
            
            return freelist
        else:
            return None

    def create_partition_table(self):
        self.primarynum = 1
        self.extnum = 5
        self.isext = 0

        self.disk = self.drive.disk_create(parted.disk_type_get("msdos"))
        return self.get_freespace()

    def create_partition(self, start, end, type, hints):
        drvsectors = self.drive.get_length()
        if self.disk is None:
            self.disk = self.drive.disk_open()
        if self.disk is None:
            raise RuntimeError, "drive has no partition table"

        if "primary" in hints:
            if self.primarynum > 4:
                raise RuntimeError, "out of primary partitions"
            if self.isext:
                raise RuntimeError, "cannot create primary partition after extended partition"
            partnum = self.primarynum
            self.primarynum = self.primarynum + 1
            parttypecode = parted.PED_PARTITION_PRIMARY
        else:
            if not self.isext:
                if self.primarynum > 4:
                    raise RuntimeError, "out of slots for extended partition"
                self.disk.add_partition(
                    parted.Partition(self.disk,
                                     parted.PED_PARTITION_EXTENDED,
                                     None, start, drvsectors - 1))
            self.primarynum = self.primarynum + 1
            self.isext = 1
            partnum = self.extnum
            self.extnum = self.extnum + 1
            parttypecode = parted.PED_PARTITION_LOGICAL

        drvnewpart = parted.Partition(self.disk, parttypecode, type,
                                      start, end)
        self.disk.add_partition(drvnewpart)

        partdevice = "%s%d" % (self.drive.get_path(), partnum)
        return partdevice

    def commit_changes(self):
        if self.disk is not None:
            self.disk.write()
            self.disk.close()
            self.disk = None
            self.drive.sync()
