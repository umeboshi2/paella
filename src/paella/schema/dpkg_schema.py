
from paella.sqlgen.classes import Column, Table
from paella.sqlgen.defaults import Text
from paella.sqlgen.defaults import PkBigname, Bigname, Name, Num

dpkg_tables = ['available', 'status', 'filelist', 'md5sums', 'conffiles']
other_tables = ['current']


common_columns = [
    PkBigname('package'),
    Name('essential'),
    Name('priority'),
    Name('section'),
    Num('installedsize'),
    Bigname('maintainer'),
    Name('version')
    ]
    

#columns for /var/lib/dpkg/status
status_columns = common_columns + [
    Name('status'),
    Text('replaces'),
    Text('provides'),
    Text('predepends'),
    Text('conflicts'),
    Bigname('source'),
    Text('suggests'),
    Text('recommends'),
    Text('depends'),
    Text('conffiles'),
    Text('description'),
    Bigname('origin'),
    Text('bugs'),
    Text('enhances'),
    Name('md5sum'),
    Bigname('configversion')
    ]


#columns for /var/lib/dpkg/available
available_columns = common_columns + [
    Text('replaces'),
    Text('provides'),
    Text('predepends'),
    Text('conflicts'),
    Bigname('source'),
    Text('suggests'),
    Text('recommends'),
    Text('depends'),
    Text('conffiles'),
    Text('description'),
    Bigname('origin'),
    Text('bugs'),
    Text('enhances'),
    Name('md5sum'),
    Bigname('filename'),
    Name('architecture'),
    Num('size'),
    Bigname('task'),
    Bigname('url')
    ]

filelist_columns = [Bigname('package'), Bigname('filename')]

md5sums_columns = filelist_columns + [Name('md5sum')]


#this table lists all systems we have dpkg db's for
class SystemTable(Table):
    def __init__(self, name):
        cols = [Name('system')]
        Table.__init__(self, name, system)

#this is a table for .list and .conffiles
class FilelistTable(Table):
    def __init__(self, name):
        Table.__init__(self, name, filelist_columns)

#this is a table for .md5sums
class Md5sumsTable(Table):
    def __init__(self, name):
        Table.__init__(self, name, md5sums_columns)

class StatusTable(Table):
    def __init__(self, name):
        Table.__init__(self, name, status_columns)

class AvailableTable(Table):
    def __init__(self, name):
        Table.__init__(self, name, available_columns)
        

        
    
if __name__ == '__main__':
    pass
