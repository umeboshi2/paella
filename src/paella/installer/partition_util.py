from operator import and_, or_
import parted
from paella.base.defaults import MB, GB


def to_mb(num, size):
    return float(num * size) / MB

def to_gb(num, size):
    return float(num * size) / GB

def mb_to_sectors(num, size):
    return long((num * MB) / size)

def gb_to_sectors(num, size):
    return long((num * GB) / size)

def get_devices():
    return parted.get_devices()

def has_extended(disk):
    extended = parted.PED_PARTITION_EXTENDED
    parts = [p for p in disk.get_part_list()]
    is_ext = map(lambda p : p.get_type() == extended, parts)
    return reduce(or_, is_ext)

def get_partitions(disk):
    return [part for part in disk.get_part_list()]

def get_path(disk, part):
    return disk.get_dev().get_path() + str(part.get_num)

