from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import list_public_methods


from paella.base.config import Configuration
from paella.base.util import ujoin
from paella.debian.repos_stable import LocalRepos
from paella.debian.base_stable import RepositorySource

debsrc = 'deb file:/mirrors/debian sid main contrib non-free'



class ReposManagerServer(SimpleXMLRPCServer):
    def __init__(self, *args):
        SimpleXMLRPCServer.__init__(self, *args)
        self.suites = ['sid', 'sarge', 'woody', 'woody/non-US']
        self.cfg = Configuration('repos')
        self.repos = dict([(suite, LocalRepos(self._srcline_(suite))) for suite in self.suites])
        self._fully_parsed = {}
        for suite, repos in self.repos.items():        
            repos.parse_release()
            repos.parse()
            for section in repos.source.sections:
                if suite == 'woody/non-US':
                    suite = 'woody'
                key = ujoin(suite, section)
                self._fully_parsed[key] = repos.full_parse(section)
            
            
    def _srcline_(self, suite):
        sections = 'main contrib non-free'
        return 'deb file:%s %s %s' % (self.cfg['local_mirror'], suite, sections)
    
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

    def export_full_path(self, suite, package):
        try:
            return self.repos[suite].full_path(package)
        except UnboundLocalError:
            return self.repos['woody/non-US'].full_path(package)
        
    def export_full_parse(self, suite, section, package):
        return self._fully_parsed[ujoin(suite, section)][package]

    def export_fp_keys(self, suite, section):
        return self._fully_parsed[ujoin(suite, section)].keys()

    def export_sections(self, suite):
        return self.repos[suite].source.sections
        
    def export_source(self, suite):
        return str(self.repos[suite].source)

def run_server():
    server = ReposManagerServer(('premio', 8000))
    server.register_introspection_functions()
    server.serve_forever()



if __name__ == '__main__':
    run_server()
    
