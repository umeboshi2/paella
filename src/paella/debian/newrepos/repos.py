from paella.base import debug, Error
from paella.base.config import Configuration

from base import RepositorySource, make_source
from repos_base import RepositoryConnection
from repos_base import RepositoryManager
from repos_local import LocalRepository





if __name__ == '__main__':
    cfg = Configuration()
    conn = RepositoryConnection()

    r = RepositoryManager(conn)
    #ls = LocalRepository(conn)

    
    def dtables():
        for t in r.main.tables():
            r.main.execute('drop table %s'%t)
        

    s = make_source('deb file:/mirrors/debian sid main non-free contrib')
