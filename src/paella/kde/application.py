from qt import SIGNAL

from kdecore import KApplication
from kdecore import KStandardDirs

from paella.base import PaellaConfig
from paella.db import PaellaConnection

class DbConnectionError(RuntimeError):
    pass

class AlreadyConnectedError(DbConnectionError):
    pass

class NotConnectedError(DbConnectionError):
    pass

class PaellaMainApplication(KApplication):
    def __init__(self):
        KApplication.__init__(self)
        self.set_config()
        self.conn = None
        dirs = KStandardDirs()
        self.tmpdir = str(dirs.findResourceDir('tmp', '/'))
        self.datadir = str(dirs.findResourceDir('data', '/'))
        # I probably don't need the socket dir
        self.socketdir = str(dirs.findResourceDir('socket', '/'))

    def connect_database(self, cfg=None):
        if self.conn is not None:
            raise AlreadyConnectedError, 'already connected to a database'
        self.conn = PaellaConnection(cfg=cfg)

    def disconnect_database(self):
        if self.conn is not None:
            self.conn.close()
            del self.conn
            self.conn = None
        else:
            raise NotConnectedError, 'not connected to a database.'

    def set_config(self, cfg=None):
        if cfg is None:
            cfg = PaellaConfig()
        self.cfg = cfg

    def _set_default_connection(self):
        self.connect_database(cfg=PaellaConfig())
