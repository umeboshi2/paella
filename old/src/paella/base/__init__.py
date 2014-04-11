import os
from useless.base.config import Configuration, list_rcfiles

class PaellaConfig(Configuration):
    def __init__(self, section=None, files=list_rcfiles('paellarc')):
        if section is None:
            section = 'database'
        Configuration.__init__(self, section=section, files=files)
        if 'PAELLARC' in os.environ:
            paellarc = os.environ['PAELLARC']
            print 'reading paellarc at', paellarc
            self.read([paellarc])

    def get_dsn(self):
        return Configuration.get_dsn(self, fields=['dbname', 'dbhost', 'dbusername', 'dbpassword'])
    
            

if __name__ == '__main__':
    print 'hello there'
