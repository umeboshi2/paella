from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import list_public_methods

from paella.debian.repos_base import RepositoryConnection
from paella.debian.repos_base import RepositoryManager
from paella.debian.repos_local import LocalRepository

debsrc = 'deb file:/mirrors/debian sid main contrib non-free'

class ReposManagerServer(SimpleXMLRPCServer):
    def __init__(self, *args):
        SimpleXMLRPCServer.__init__(self, *args)
        self.conn = RepositoryConnection()
        self._repos = RepositoryManager(self.conn)
        
    def _dispatch(self, method, params):
        try:
            # We are forcing the 'export_' prefix on methods that are
            # callable through XML-RPC to prevent potential security
            # problems
            func = getattr(self, 'export_' + method)
        except AttributeError:
            raise Exception('method "%s" is not supported' % method)
        else:
            return func(*params)
    

    def export_add_source(self, name, source):
        self._repos.add_source(name, source)
        return '%s added' % name
    
    def export_update_source(self, name):
        self._repos.update_source(name)
        return '%s updated' % name

    def export_set(self, name):
        self._repos.set(name)
        return 'current source set to %s' % name

    def export_locate(self, section):
        return self._repos.locate(section)

    def export_check(self, section):
        return self._repos.check(section)

    def export_check_section(self, section, name):
        return self._repos.check_section(section, name)

    def export_current(self):
        return self._repos.current

    def export_remote(self):
        return self._repos.remote
    


class LocalReposManagerServer(SimpleXMLRPCServer):
    def __init__(self, *args):
        SimpleXMLRPCServer.__init__(self, *args)
        self.conn = RepositoryConnection()
        self._repos = LocalRepository(self.conn, 'pwoody', 'deb')
        
    def _dispatch(self, method, params):
        try:
            # We are forcing the 'export_' prefix on methods that are
            # callable through XML-RPC to prevent potential security
            # problems
            func = getattr(self, 'export_' + method)
        except AttributeError:
            raise Exception('method "%s" is not supported' % method)
        else:
            return func(*params)
    
    def export_release_exist(self):
        return self._repos.check_release_file_exists()

    def export_check_dist_sections(self):
        rows = [dict(row.items()) for row in self._repos.check_all_dist_sections()]
        return rows
    

def run_server():
    #server = ReposManagerServer(('premio', 8000))
    server = LocalReposManagerServer(('premio', 8000))
    server.register_introspection_functions()
    server.serve_forever()



if __name__ == '__main__':
    run_server()
    
