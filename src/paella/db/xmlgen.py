from xml.dom.minidom import Element

#from paella.base.xmlfile import TableElement
#from midlevel import StatementCursor
#####################
#####################
#####################
#####################
#this module isn't called or needed

#generate xml        
class XmlDatabase(object):
    def __init__(self, conn, path):
        object.__init__(self)
        self.conn = conn
        self.path = path
        self.cursor = StatementCursor(self.conn, name='XmlDatabase')
        self.element = Element('Database')

    def table(self, name, key=None):
        rows = self.cursor.select(table=name, order=key)
        return TableElement(name, rows, key)

    def tables(self):
        element = Element('tables')
        for table in self.cursor.tables():
            element.appendChild(self.table(table))
        return element
    

def backup_database(conn, path):
    element = Element('xml_database')
    cursor = StatementCursor(conn, 'backup_database')


if __name__ == '__main__':
    from paella.db.lowlevel import LocalConnection
    conn = LocalConnection('repos_db')
    s = StatementCursor(conn)
