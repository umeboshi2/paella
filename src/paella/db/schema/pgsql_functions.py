import os

from useless.base import Error, debug
from useless.base.util import ujoin, makepaths
from useless.base.util import readfile, wget, strfile

from paella.debian.base import RepositorySource
from paella.debian.repos import LocalRepos
from paella.debian.repos import RemoteRepos

from useless.sqlgen.classes import Column, Table
from useless.sqlgen.defaults import Text, DefaultNamed, Bool
from useless.sqlgen.defaults import PkBigname, Bigname, Name, Num
from useless.sqlgen.defaults import PkBignameTable, PkNameTable, PkName

from useless.sqlgen.statement import Statement
from useless.sqlgen.admin import grant_public
from useless.sqlgen.clause import Eq

from useless.db.lowlevel import OperationalError
from useless.db.midlevel import StatementCursor

from useless.db.plsql import pgsql_delete

from paella_tables import suite_tables, primary_tables, primary_sequences
from paella_tables import packages_columns, SCRIPTS
from paella_tables import MTSCRIPTS

from paella import deprecated

PRIORITIES = ['first', 'high', 'pertinent', 'none', 'postinstall', 'last']
SUITES = ['sid', 'woody'] 




plpgsql_delete_trait = """create or replace function delete_trait(varchar, varchar) returns integer as '
	begin
	execute ''delete from '' || $1 || ''_scripts where trait = '' || quote_literal($2) ;
	execute ''delete from '' || $1 || ''_templates where trait = ''|| quote_literal($2) ;
	execute ''delete from '' || $1 || ''_trait_package where trait = ''|| quote_literal($2) ;
	execute ''delete from '' || $1 || ''_trait_parent where trait = ''|| quote_literal($2) ;
	execute ''delete from '' || $1 || ''_debconf where trait = ''|| quote_literal($2) ;
	execute ''delete from '' || $1 || ''_variables where trait = ''|| quote_literal($2) ;
	execute ''delete from '' || $1 || ''_traits where trait = ''|| quote_literal($2) ;
	return 0 ;
	end ;
' language 'plpgsql';
"""
def pgsql_delete_family():
    tables = ['family_environment', 'family_parent', 'families']
    return pgsql_delete('delete_family', tables, 'family')

def pgsql_delete_profile():
    tables = ['profile_variables', 'profile_family', 'profile_trait', 'profiles']
    return pgsql_delete('delete_profile', tables, 'profile')

def pgsql_delete_disk():
    tables = ['partitions', 'disk']
    return pgsql_delete('delete_disk', tables, 'diskname')

def pgsql_delete_mtype():
    tables = ['machine_disks', 'machine_modules', 'machine_types']
    return pgsql_delete('delete_mtype', tables, 'machine_type')

def pgsql_delete_filesystem():
    tables = ['filesystem_mounts', 'filesystems']
    return pgsql_delete('delete_filesystem', tables, 'filesystem')


    

if __name__ == '__main__':
    from useless.db.lowlevel import QuickConn
    from useless.db.midlevel import StatementCursor
    from paella.debian.base import parse_packages, full_parse
    #cmd = CommandCursor(c, 'dsfsdf')
    def dtable():
        cmd.execute('drop table ptable')

