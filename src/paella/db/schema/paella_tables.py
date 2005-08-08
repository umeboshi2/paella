from useless.base import Error, debug
from useless.base.util import ujoin

from useless.sqlgen.classes import Table, Sequence
from useless.sqlgen.defaults import Text, DefaultNamed, Bool, PkNum
from useless.sqlgen.defaults import PkBigname, Bigname, Name, Num, Oid
from useless.sqlgen.defaults import PkBignameTable, PkNameTable, PkName
from useless.sqlgen.defaults import RelationalTable
from useless.sqlgen.statement import Statement

PRIORITIES = ['first', 'high', 'pertinent', 'none', 'postinstall', 'last']
SUITES = ['sid', 'woody'] 
#SCRIPTS = ['chroot', 'pre', 'post', 'config']
SCRIPTS = ['pre', 'remove', 'install', 'templates', 'config', 'chroot', 'reconfig', 'post']
MTSCRIPTS = ['pre', 'setup_disks', 'mount_target',
             'bootstrap', 'make_device_entries',
             'apt_sources_installer', 'ready_base',
             'mount_target_proc',
             'pre_install', 'install', 'post_install',
             'install_modules', 'install_kernel', 'apt_sources_final',
             'install_fstab', 'umount_target_proc', 'post'
             ]

def getcolumn(name, columns):
    ncols = [column for column in columns if column.name == name]
    if len(ncols) == 1:
        return ncols[0]
    else:
        raise Error, 'key not found'

class TextFileIdentifier(Sequence):
    def __init__(self):
        Sequence.__init__(self, 'textfile_ident')
        

class TextFilesTable(Table):
    def __init__(self):
        idcol = PkNum('fileid')
        idcol.set_auto_increment('textfile_ident')
        mcol = Name('md5size')
        mcol.constraint.unique = True
        dcol = Text('data')
        columns = [idcol, mcol, dcol]
        Table.__init__(self, 'textfiles', columns)
        
def family_env_columns():
    return [
        PkName('family'),
        PkName('trait'),
        PkBigname('name'),
        Text('value')]


#family table
class FamilyTable(Table):
    def __init__(self):
        columns = [PkName('family'),
                   Name('type')]
        Table.__init__(self, 'families', columns)

class FamilyParentsTable(Table):
    def __init__(self):
        fcol = PkName('family')
        fcol.set_fk('families')
        pcol = PkName('parent')
        pcol.set_fk('families')
        Table.__init__(self, 'family_parent', [fcol, pcol])

class FamilyEnviromentTable(Table):
    def __init__(self):
        columns = family_env_columns()
        columns[0].set_fk('families')
        columns[1].set_fk('traits')
        Table.__init__(self, 'family_environment', columns)
        
#profiles_table
def profile_columns():
    return [
        PkName('profile'),
        Name('suite'),
        Bigname('template'),
        Text('description')]

class ProfileTable(Table):
    def __init__(self, suite_table):
        columns = profile_columns()
        suite = getcolumn('suite', columns)
        suite.set_fk(suite_table)
        Table.__init__(self, 'profiles', columns)
        
class ProfileFamilyTable(Table):
    def __init__(self):
        pcol = PkName('profile')
        pcol.set_fk('profiles')
        fcol = PkName('family')
        fcol.set_fk('families')
        Table.__init__(self, 'profile_family', [pcol, fcol])
        
#traits
def trait_columns():
    return [
        PkName('trait'),
        Name('priority'),
        Text('description')]

class TraitTable(Table):
    def __init__(self, suite, traits_table, prio_table):
        tablename = ujoin(suite, 'traits')
        columns = trait_columns()
        trait = getcolumn('trait', columns)
        priority = getcolumn('priority', columns)
        trait.set_fk(traits_table)
        priority.set_fk(prio_table)
        Table.__init__(self, tablename, columns)

#packages
def packages_columns():
    return [
        PkBigname('package'),
        Name('priority'),
        Bigname('section'),
        Num('installedsize'),
        Bigname('filename'),
        Bigname('maintainer'),
        Bigname('size'),
        Name('md5sum'),
        Bigname('version'),
        Text('description')]

class PackagesTable(Table):
    def __init__(self, suite):
        tablename = ujoin(suite, 'packages')
        Table.__init__(self, tablename, packages_columns())


#relations
class _ProfileRelation(RelationalTable):
    def __init__(self, profiles_table, tablename, other_columns):
        RelationalTable.__init__(self, tablename, profiles_table, PkName('profile'),
                                 other_columns)

class _TraitRelation(RelationalTable):
    def __init__(self, traits_table, tablename, other_columns):
        RelationalTable.__init__(self, tablename, traits_table, PkName('trait'),
                                 other_columns)
    
class TraitPackage(_TraitRelation):
    def __init__(self, suite, traits_table, packages_table):
        packs_column = PkBigname('package')
        packs_column.set_fk(packages_table)
        action_column = PkName('action')
        action_column.constraint.default = 'install'
        columns = [packs_column, action_column]
        tablename = ujoin(suite, 'trait', 'package')
        _TraitRelation.__init__(self, traits_table, tablename, columns)

class TraitParent(_TraitRelation):
    def __init__(self, suite, traits_table):
        parent_column = PkName('parent')
        parent_column.set_fk(traits_table, 'trait')
        columns = [parent_column]
        tablename = ujoin(suite, 'trait', 'parent')
        _TraitRelation.__init__(self, traits_table, tablename, columns)

class TraitEnvironment(_TraitRelation):
    def __init__(self, suite, traits_table):
        cols = [PkBigname('name'), Text('value')]
        tablename = ujoin(suite, 'variables')
        _TraitRelation.__init__(self, traits_table, tablename, cols)

def template_columns():
    return [
        PkBigname('template'),
        Name('mode'),
        Name('owner'),
        Name('grp_owner'),
        Num('templatefile')]

class TraitTemplate(_TraitRelation):
    def __init__(self, suite, traits_table, packages_table):
        tablename = ujoin(suite, 'templates')
        packs_column = PkBigname('package')
        packs_column.set_fk(packages_table)
        tcolumns = template_columns()
        tcolumns[-1].set_fk('textfiles')
        columns = tcolumns[:1] + [packs_column] + tcolumns[1:]
        _TraitRelation.__init__(self, traits_table, tablename, columns)

def debconf_columns():
    return [
        PkBigname('name'),
        Bigname('value'),
        Bigname('owners'),
        Bigname('flags'),
        Bigname('template'),
        Text('variables')]

class TraitDebConf(_TraitRelation):
    def __init__(self, suite, traits_table, packages_table):
        tablename = ujoin(suite, 'debconf')
        _TraitRelation.__init__(self, traits_table, tablename, debconf_columns())

class TraitScript(_TraitRelation):
    def __init__(self, suite, traits_table):
        tablename = ujoin(suite, 'scripts')
        script_column = PkName('script')
        script_column.set_fk('scriptnames')
        sfile_column = Num('scriptfile')
        sfile_column.set_fk('textfiles')
        script_columns = [script_column, sfile_column]
        _TraitRelation.__init__(self, traits_table, tablename, script_columns)

class ProfileEnvironment(Table):
    def __init__(self, profiles_table):
        profile_col = PkName('profile')
        profile_col.set_fk(profiles_table)
        trait_col = PkName('trait')
        name_col = PkBigname('name')
        value_col = Text('value')
        cols = [profile_col, trait_col, name_col, value_col]
        tablename = ujoin('profile', 'variables')
        Table.__init__(self, tablename, cols)

class ProfileTrait(Table):
    def __init__(self, profiles_table, traits_table):
        profile_col = PkName('profile')
        profile_col.set_fk(profiles_table)
        trait_col = PkName('trait')
        trait_col.set_fk(traits_table)
        ord_col = Num('ord')
        Table.__init__(self, 'profile_trait', [profile_col, trait_col, ord_col])

class ProfileDebConf(_ProfileRelation):
    def __init__(self, profiles_table):
        tablename = 'profiledebconf'
        _ProfileRelation.__init__(self, profiles_table, debconf_columns)



class DisksTable(Table):
    def __init__(self, name='disks'):
        Table.__init__(self, name, [PkName('diskname')])


class MachineTypesTable(Table):
    def __init__(self, name='machine_types'):
        Table.__init__(self, name, [PkName('machine_type')])

def mounts_columns():
    return [
        PkName('mnt_name'),
        Name('mnt_point'),
        Name('fstype'),
        Name('mnt_opts'),
        Name('dump'),
        Name('pass')
        ]

class MountsTable(Table):
    def __init__(self, name='mounts'):
        Table.__init__(self, name, mounts_columns())

class KernelsTable(Table):
    def __init__(self, name='kernels'):
        Table.__init__(self, name, [PkName('kernel')])
        

def partition_columns():
    return [
        PkName('partition'),
        Num('start'),
        Num('size'),
        Num('Id')
        ]

class PartitionsTable(Table):
    def __init__(self, name, disks_table):
        diskname_col = PkName('diskname')
        diskname_col.set_fk(disks_table)
        columns = [diskname_col] + partition_columns()
        Table.__init__(self, name, columns)

class MachineTypeFamilyTable(Table):
    def __init__(self, mach_types_table):
        mtype_col = PkName('machine_type')
        mtype_col.set_fk(mach_types_table)
        fcol = PkName('family')
        fcol.set_fk('families')
        Table.__init__(self, 'machine_type_family', [mtype_col, fcol])
        
class MachineTypeEnvironment(Table):
    def __init__(self, mach_types_table):
        mtype_col = PkName('machine_type')
        mtype_col.set_fk(mach_types_table)
        trait_col = PkName('trait')
        name_col = PkBigname('name')
        value_col = Text('value')
        cols = [mtype_col, trait_col, name_col, value_col]
        tablename = ujoin('machine_type', 'variables')
        Table.__init__(self, tablename, cols)

class MachineTypeScript(Table):
    def __init__(self, mach_types_table):
        mtype_col = PkName('machine_type')
        mtype_col.set_fk(mach_types_table)
        tablename = ujoin('machine_type', 'scripts')
        script_column = PkName('script')
        script_column.set_fk('scriptnames')
        sfile_column = Num('scriptfile')
        sfile_column.set_fk('textfiles')
        script_columns = [mtype_col, script_column, sfile_column]
        Table.__init__(self, tablename, script_columns)

class MachineDisksTable(Table):
    def __init__(self, name, mach_types_table, disks_table):
        mtype_col = PkName('machine_type')
        mtype_col.set_fk(mach_types_table)
        diskname_col = PkName('diskname')
        diskname_col.set_fk(disks_table)
        columns = [mtype_col, diskname_col, PkName('device')]
        Table.__init__(self, name, columns)

class MachineModulesTable(Table):
    def __init__(self, name, mach_types_table):
        mtype_col = PkName('machine_type')
        mtype_col.set_fk(mach_types_table)
        columns = [mtype_col, PkName('module'), Num('ord')]
        Table.__init__(self, name, columns)
    

class FilesystemsTable(Table):
    def __init__(self):
        fs_col = PkName('filesystem')
        Table.__init__(self, 'filesystems', [fs_col])
        
class FilesystemMountsTable(Table):
    def __init__(self, fs_table, mounts_table):
        fs_col = PkName('filesystem')
        fs_col.set_fk(fs_table)
        mnt_name_col = PkName('mnt_name')
        mnt_name_col.set_fk(mounts_table)
        ord_col = Num('ord')
        partition_column = Num('partition')
        size = Name('size')
        columns = [fs_col, mnt_name_col, ord_col, partition_column, size]
        Table.__init__(self, 'filesystem_mounts', columns)

class FilesystemDisksTable(Table):
    def __init__(self, fs_table, disks_table):
        fs_col = PkName('filesystem')
        fs_col.set_fk(fs_table)
        diskname_col = PkName('diskname')
        diskname_col.set_fk(disks_table)
        columns = [fs_col, diskname_col]
        Table.__init__(self, 'filesystem_disks', columns)

class PartitionMountsTable(Table):
    def __init__(self, mounts_table):
        mnt_name_col = PkName('mnt_name')
        mnt_name_col.set_fk(mounts_table)
        partition_col = Num('partition')
        columns = [mnt_name_col, partition_col]
        Table.__init__(self, 'partition_mounts', columns)
        

class MachinesTable(Table):
    def __init__(self, mach_types_table, kernels_table, profiles_table,
                 filesystem_table):
        machine_col = PkName('machine')
        mtype_col = Name('machine_type')
        mtype_col.set_fk(mach_types_table)
        kernel_col = Name('kernel')
        kernel_col.set_fk(kernels_table)
        profile_col = Name('profile')
        profile_col.set_fk(profiles_table)
        fs_col = Name('filesystem')
        fs_col.set_fk(filesystem_table, 'filesystem')
        columns = [machine_col, mtype_col, kernel_col, profile_col, fs_col]
        Table.__init__(self, 'machines', columns)
        

def suite_tables(suite):
    pack_table = PackagesTable(suite)
    trait_table = TraitTable(suite, 'traits', 'priorities')
    trait_parent = TraitParent(suite, trait_table.name)
    trait_package = TraitPackage(suite, trait_table.name, pack_table.name)
    trait_variable = TraitEnvironment(suite, trait_table.name)
    trait_template = TraitTemplate(suite, trait_table.name, pack_table.name)
    trait_scripts = TraitScript(suite, trait_table.name)
    trait_debconf = TraitDebConf(suite, trait_table.name, pack_table.name)
    tables = [pack_table, trait_table, trait_parent, trait_package, trait_variable,
              trait_template, trait_scripts, trait_debconf]
    return tables

def currentenv_columns():
    return [
        PkName('hostname'),
        PkBigname('name'),
        Text('value')]

def defaultenv_columns():
    return [
        PkName('section'),
        PkBigname('option'),
        Text('value')]

def suite_columns():
    return [
        PkName('suite'),
        Bool('nonUS'),
        Bool('updates'),
        Bool('local'),
        Bool('common')]

def primary_sequences():
    return [TextFileIdentifier()]

    
def primary_tables():
    tables = []
    #Textfiles
    tables.append(TextFilesTable())
    #All Suites
    tables.append(Table('suites', suite_columns()))
    #All Traits
    tables.append(PkNameTable('traits', 'trait'))
    #All Priorities
    tables.append(PkNameTable('priorities', 'priority'))
    #All Families
    tables.append(FamilyTable())
    #Family Parents
    tables.append(FamilyParentsTable())
    #Family Environment
    tables.append(FamilyEnviromentTable())
    #All Profiles
    profiles = ProfileTable('suites')
    tables.append(profiles)
    #All Script Names
    scripts = PkNameTable('scriptnames', 'script')
    tables.append(scripts)
    #Profile - Trait relation
    profile_trait_table = ProfileTrait('profiles', 'traits')
    tables.append(profile_trait_table)
    #Profile Environment
    profile_variables = ProfileEnvironment('profiles')
    tables.append(profile_variables)
    #Profile Family
    tables.append(ProfileFamilyTable())
    #Default Environment
    defaultenv = Table('default_environment', defaultenv_columns())
    tables.append(defaultenv)
    #Current Environment
    currentenv = Table('current_environment', currentenv_columns())
    tables.append(currentenv)
    #Disks
    tables.append(DisksTable())
    #Machine Types
    tables.append(MachineTypesTable())
    #Mounts
    tables.append(MountsTable())
    #Kernels
    tables.append(KernelsTable())
    #Partitions
    tables.append(PartitionsTable('partitions', 'disks'))
    #Partition Workspace
    pwcols = [PkName('diskname')] + partition_columns()
    tables.append(Table('partition_workspace', pwcols))
    #MachineTypesTables
    mtfamily = MachineTypeFamilyTable('machine_types')
    tables.append(mtfamily)
    mtenviron = MachineTypeEnvironment('machine_types')
    tables.append(mtenviron)
    mtscript = MachineTypeScript('machine_types')
    tables.append(mtscript)
    #Machine Disks
    machine_disks = MachineDisksTable('machine_disks', 'machine_types', 'disks')
    tables.append(machine_disks)
    #Machine Modules
    machine_modules = MachineModulesTable('machine_modules', 'machine_types')
    tables.append(machine_modules)
    #Filesystems
    tables.append(FilesystemsTable())
    #Filesystem Mounts
    tables.append(FilesystemMountsTable('filesystems', 'mounts'))
    #Filesystem Disks
    tables.append(FilesystemDisksTable('filesystems', 'disks'))
    #Machines
    machines = MachinesTable('machine_types', 'kernels', 'profiles', 'filesystems')
    tables.append(machines)

    return tables, dict([(t.name, t) for t in tables])

    
    
    



if __name__ == '__main__':
    from useless.db.midlevel import StatementCursor
    from useless.sqlgen.statement import Statement
    from paella.debian.base import parse_packages, full_parse
    from paella.db import PaellaConnection
    def dtable():
        cmd.execute('drop table ptable')

    def dtables():
        for t in cmd.tables():
            if t != 'footable':
                cmd.execute('drop table %s' %t)

