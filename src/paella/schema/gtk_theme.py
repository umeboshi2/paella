
from paella.gtk.theme import Rgbdb, Style, GtkrcTemplate
from paella.gtk.theme import style_elements, _bg_widget

from paella.sqlgen.defaults import NameTable
from paella.sqlgen.write import insert, update


class ThemeTable(NameTable):
    def __init__(self, name):
        columns = ['element'] + element_states
        NameTable.__init__(self, name, columns)

def _setup_db(cursor):
    cmd = cursor
    t = NameTable('themes', ['theme'])
    cmd.execute('create table %s' %t)
    cmd.execute(insert('themes', {'theme':'themebase'}))
    t = ThemeTable('themebase')
    cmd.execute('create table %s' %t)
    cols = [x.name for x in t.columns]
    #print cmd.tables()

    q1 = insert('themebase',
                dict(zip(cols, ['fg', 'black', 'seashell', 'black', 'sky blue', 'plum'])))
    q2 = insert('themebase',
                dict(zip(cols, ['bg', 'cyan3', 'seashell',
                                'cyan4', 'light coral', 'grey'])))
    q3 = insert('themebase',
                dict(zip(cols, ['base', 'light sea green',
                                'lavender', 'azure3', 'yellow', 'aquamarine'])))
    q4 = insert('themebase',
                dict(zip(cols, ['text', 'wheat', 'black',
                                'black', 'black', 'dark violet'])))
    map(cmd.execute, [q1, q2, q3, q4])
    
        
        
        
        
if __name__ == '__main__':
    from paella.classes.config import Configuration
    dsn = Configuration().get_dsn()
    dsn['dbname'] = 'themes'
    c = QuickConn(dsn)
    win = ColorThingyWindow(cd, c)
    t = NameTable('themes', ['theme'])
    
    cmd = CommandCursor(c, 'dsfsdf')
    def dtable():
        cmd.execute('drop table themebase')
    def dtables():
        for t in cmd.tables():
            if t not in  ['footable']:
                cmd.execute('drop table %s' %t)
    #dtables()
    mainloop()
