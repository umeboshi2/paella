#from xml.dom.minidom import Text

#from useless.sqlgen.clause import Eq
from useless.xmlgen.base import BaseElement, TextElement
from useless.xmlgen.base import Anchor, Html, Body
from useless.xmlgen.base import ListItem, UnorderedList
from useless.xmlgen.base import BR, HR, Bold, TR, TD, Paragraph
from useless.xmlgen.base import SimpleTitleElement

#from useless.db.midlevel import StatementCursor
from paella.db.trait import Trait
#from paella.db.profile import Profile
#from paella.db.family import Family
#from paella.db.machine import MachineHandler
#from paella.db.machine.mtype import MachineTypeHandler

from base import RecordElement, TxtTD
from base import BaseFieldTable, BaseDocument
from base import TraitTable


class TraitEnvTable(RecordElement):
    def __init__(self, trait, env, **atts):
        fields = env.keys()
        fields.sort()
        RecordElement.__init__(self, fields, 'trait', None, env, **atts)
        
class SectionTitle(SimpleTitleElement):
    def __init__(self, text, **atts):
        atts['width'] = '75%'
        atts['bgcolor'] = 'IndianRed'
        SimpleTitleElement.__init__(self, text, **atts)

class PackageTable(BaseElement):
    def __init__(self, rows, **atts):
        BaseElement.__init__(self, 'table', **atts)
        for row in rows:
            trow = TR()
            p = TxtTD(row.package)
            trow.appendChild(p)
            a = TxtTD(row.action)
            trow.appendChild(a)
            self.appendChild(trow)

class PackageFieldTable(BaseFieldTable):
    def __init__(self, row, **atts):
        fields = ['package', 'priority', 'section', 'installedsize',
                  'maintainer', 'version', 'description']
        BaseFieldTable.__init__(self, fields, row, **atts)
        
class TemplateTable(BaseElement):
    def __init__(self, rows, **atts):
        BaseElement.__init__(self, 'table', **atts)
        for row in rows:
            trow = TR()
            fake_template = ',,,'.join([row.package, row.template.replace('.', ',')])
            ta = Anchor('show.template.%s' % fake_template, row.template)
            td = TD()
            td.appendChild(ta)
            trow.appendChild(td)
            p = TxtTD(row.package)
            trow.appendChild(p)
            self.appendChild(trow)
        
class PackageDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.suite = None
        self.cursor = StatementCursor(self.conn)

    def set_suite(self, suite):
        self.suite = suite
        self.cursor.set_table('%s_packages' % self.suite)

    def set_clause(self, clause):
        print 'clause---->', clause, type(clause)
        self.cursor.clause = clause
        self.clear_body()
        title = SimpleTitleElement('%s Packages' % self.suite, bgcolor='IndianRed', width='100%')
        self.body.appendChild(title)
        for row in self.cursor.select(clause=clause):
            self.body.appendChild(PackageFieldTable(row, bgcolor='MistyRose2'))
            self.body.appendChild(HR())
            
class TraitDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.trait = Trait(self.conn)

    def set_trait(self, trait):
        self.clear_body()
        self.trait.set_trait(trait)
        title = SimpleTitleElement('Trait: %s' % trait, bgcolor='IndianRed', width='100%')
        self.body.appendChild(title)
        self.body.appendChild(HR())
        plist = UnorderedList()
        parents = self.trait.parents(trait=trait)
        parent_section = SectionTitle('Parents')
        parent_section.create_rightside_table()
        parent_section.append_rightside_anchor(Anchor('hello.there.dude', 'edit'))
        parent_section.append_rightside_anchor(Anchor('hello.there.dudee', 'edit2'))
        self.body.appendChild(parent_section)
        for parent in parents:
            pp = Anchor('show.parent.%s' % parent, parent)
            plist.appendChild(ListItem(pp))
        self.body.appendChild(plist)
        #ptitle_anchor = Anchor('edit.packages.%s' % trait, 'Packages')
        ptitle = SectionTitle('Packages')
        ptitle_anchor = Anchor('new.package.%s' % trait, '(new)')
        td = TD()
        td.appendChild(ptitle_anchor)
        ptitle.row.appendChild(td)
        self.body.appendChild(ptitle)
        rows = self.trait.packages(trait=trait, action=True)
        self.body.appendChild(PackageTable(rows, bgcolor='SkyBlue3'))
        ttitle = Anchor('edit.templates.%s' % trait, 'Templates')
        self.body.appendChild(SectionTitle(ttitle))
        rows = self.trait.templates(trait=trait, fields=['package', 'template', 'templatefile'])
        if len(rows):
            self.body.appendChild(TemplateTable(rows, bgcolor='DarkSeaGreen3'))
        self.body.appendChild(SectionTitle('Variables', href='foo.var.ick'))
        if len(self.trait.environ.keys()):
            env = TraitEnvTable(trait, self.trait.environ, bgcolor='MistyRose3')
            self.body.appendChild(env)
        self.body.appendChild(SectionTitle('Scripts'))
        slist = UnorderedList()
        for row in self.trait._scripts.scripts(trait=trait):
            script  = row.script
            sa = Anchor('show.script.%s' % script, script)
            slist.appendChild(ListItem(sa))
        self.body.appendChild(slist)
        
