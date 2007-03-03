from useless.db.plsql import pgsql_delete

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

def create_pgsql_functions(cursor):
    cursor.execute(plpgsql_delete_trait)
    cursor.execute(pgsql_delete_profile())
    cursor.execute(pgsql_delete_family())
    cursor.execute(pgsql_delete_disk())
    cursor.execute(pgsql_delete_mtype())
    cursor.execute(pgsql_delete_filesystem())


    

if __name__ == '__main__':
    pass
