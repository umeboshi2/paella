import sys
from qt import QLabel, QApplication
from qtsql import QSqlDatabase, QSqlCursor
from qtsql import QDataTable, QSqlQuery

from paella.base import Error
from paella.sqlgen.statement import Statement
from paella.profile.base import PaellaConfig

dbdriver = 'QPSQL7'

cfg = PaellaConfig('database')

app = QApplication(sys.argv)

db = QSqlDatabase.addDatabase(dbdriver)
if db:
    db.setHostName(cfg['dbhost'])
    db.setDatabaseName(cfg['dbname'])
    db.setUserName(cfg['dbusername'])
    
    db.open()
else:
    raise Error, 'bad db'
s = Statement()
cursor = QSqlCursor(None, True, QSqlDatabase.database(dbdriver, True))
#s.table = 'suites'
s.table = 'gunny_templates'
#query = QSqlQuery(q)
#cursor = query
print cursor.execQuery(str(s))
#print q
print cursor.size()
print dir(cursor)
fields = cursor.driver().recordInfo(cursor)
for f in fields:
    cursor.append(f)
cursor.setName(s.table)
#cursor.setMode(QSqlCursor.ReadOnly)
#cursor.execQuery(str(s))
dt = QDataTable(None)
dt.show()
dt.setSqlCursor(cursor, True, True)
#dt.setSort(cursor.primaryIndex())
dt.refresh()
#dt.refresh(QDataTable.RefreshAll)
hello = QLabel('<font color=blue>%s <i>Qt!</i></font>' % str(s), None)
app.setMainWidget(dt)
hello.setText('rows returned: %s' % str(cursor.size()))
hello.show()
app.exec_loop()
