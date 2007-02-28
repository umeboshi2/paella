from misc import make_interfaces_simple
from filesystem import make_fstab
from misc import set_root_passwd, myline
from aptsources import make_sources_list


#this is done after bootstrap or
#this is done after extracting the base tar
def ready_base_for_install(target, conn, suite, fstabobj):
    set_root_passwd(target, myline)
    make_sources_list(conn, target, suite)
    make_interfaces_simple(target)
    make_fstab(fstabobj, target)
    

