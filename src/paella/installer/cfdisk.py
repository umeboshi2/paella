import os
from os.path import join
import commands

from parted import Disk, Partition, Device
import parted

from paella.base.util import makepaths
from paella.contrib.pyparsing import Word, alphas, Literal, nums, Suppress
from paella.contrib.pyparsing import restOfLine, Optional, Dict, ZeroOrMore
from paella.contrib.pyparsing import Group

from paella.db.midlevel import StatementCursor
from paella.sqlgen.statement import Statement
from paella.sqlgen.clause import Eq




def PartitionParser():
    start_ = Suppress('start') + Suppress('=') + Word(nums)
    size_ = Suppress('size') + Suppress('=') + Word(nums)
    id_ = Suppress('Id') + Suppress('=') + Word(nums)
    device_ = Word(alphas+nums+'/')
    comment_ = '#' + Optional(restOfLine)
    unit_ = Literal('unit') + Optional(Suppress(':') + Word(alphas + nums)+ restOfLine)

    pinfo = start_ + Suppress(',') 
    pinfo += size_ + Suppress(',')
    pinfo += id_ + restOfLine
    partition = Group(device_ + Suppress(':') + pinfo)
    partition.ignore(comment_)
    partition.ignore(unit_)
    #partition = ZeroOrMore(partition)
    
    return Dict(ZeroOrMore(partition))

class DiskManager(object):
    def __init__(self, conn):
        self.conn = conn
        self.parser = PartitionParser()
        self.cursor = StatementCursor(self.conn)
        
    def _quick_partition(self, device, data):
        i, o = os.popen2('sfdisk %s' % device)
        i.write(data)
        i.close()
        

    def get_partition_info(self, device, parser=None):
        if parser is None:
            parser = self.parser
        command = 'bash -c "sfdisk -d %s | grep %s"' % (device, device)
        part_info = commands.getoutput(command)
        return self._parse_diskconfig(device, part_info)

    def _parse_diskconfig(self, device, astring):
        parsed = self.parser.parseString(astring)
        partitions = []
        for p in parsed:
            pnum = p[0].split(device)[1]
            pdict = dict(partition=pnum, start=p[1], size=p[2], Id=p[3])
            partitions.append(pdict)
        return partitions

    def _submit_diskconfig(self, diskname, device, astring):
        workspace = 'partition_workspace'
        self.cursor.delete(table=workspace, clause=(Eq('diskname', diskname)))
        row = dict(diskname=diskname)
        for partition in self._parse_diskconfig(device, astring):
            print 'submitting', partition
            row.update(partition)
            self.cursor.insert(table=workspace, data=row)

    def submit_partitions(self, diskname, device):
        self.cursor.set_table('partition_workspace')
        self.cursor.delete(clause=(Eq('diskname', diskname)))
        row = dict(diskname=diskname)
        print 'submitting', device
        for partition in self.get_partition_info(device):
            print 'submitting', partition
            row.update(partition)
            self.cursor.insert(data=row)

    def approve_disk(self, diskname):
        clause = Eq('diskname', diskname)
        workspace = 'partition_workspace'
        sql = Statement('select')
        sql.table = workspace
        sql.clause = clause
        new_rows = sql.select(order='partition')
        if diskname not in [r.diskname for r in self.cursor.select(table='disks')]:
            self.cursor.insert(table='disks', data=dict(diskname=diskname))
        else:
            self.cursor.delete(table='partitions', clause=clause)
        self.cursor.execute('insert into partitions %s' % new_rows)
    
    def get_partitions_by_name(self, diskname):
        return self.cursor.select(table='partitions',
                             clause=Eq('diskname', diskname),
                             order='partition')


    def make_partition_dump(self, device, partitions):
        output = '# partition table of %s\n'
        output += 'unit: sectors\n'
        for p in partitions:
            line = '%s%s : start= %8d, size= %8d, Id=%2d' % \
                   (device, p.partition, p.start, p.size, p.id)
            output += line + '\n'
        return output

    def partition_disk(self, diskname, device):
        partitions = self.get_partitions_by_name(diskname)
        data = self.make_partition_dump(device, partitions)
        self._quick_partition(device, data)

    def clear_partition_table(self, device):
        command = 'dd if=/dev/zero of=%s count=1 bs=512' % device
        os.system(command)
        



def _quick_insert_disks(conn):
    dm = DiskManager(conn)
    

if __name__ == '__main__':
    from paella.profile.base import PaellaConnection
    conn = PaellaConnection(cfg)
    s = StatementCursor(conn)
    
    dm = DiskManager(conn)
