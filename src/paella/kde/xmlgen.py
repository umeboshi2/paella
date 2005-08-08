from xml.dom.minidom import Text

from useless.sqlgen.clause import Eq
from useless.xmlgen.base import BaseElement, TextElement
from useless.xmlgen.base import Anchor, Html, Body
from useless.xmlgen.base import ListItem, UnorderedList
from useless.xmlgen.base import BR, HR, Bold, TR, TD, Paragraph
from useless.xmlgen.base import SimpleTitleElement

from useless.db.midlevel import StatementCursor
from paella.db.trait import Trait
from paella.db.profile import Profile
from paella.db.family import Family
from paella.db.machine import MachineHandler

def color_header(table, color='cornsilk3'):
    table.header.firstChild.setAttribute('bgcolor', color)
    
class RecordElement(BaseElement):
    def __init__(self, fields, idcol, action, record, **atts):
        BaseElement.__init__(self, 'table', **atts)
        self.record = record
        refdata = None
        if hasattr(record, '_refdata'):
            refdata = record._refdata
        for field in fields:
            row = BaseElement('tr')
            key = TD(bgcolor='DarkSeaGreen')
            key.appendChild(Bold(field))
            row.appendChild(key)
            val = TD()
            if refdata is not None and field in refdata.cols:
                ridcol = refdata.cols[field]
                refrec =  refdata.data[field][record[ridcol]]
                node = refdata.object[field](refrec)
                if action:
                    url = '.'.join(map(str, [action, field, record[idcol]]))
                    val.appendChild(Anchor(url, node))
                else:
                    val.appendChild(node)
            elif action:
                url = '.'.join(map(str, [action, field, record[idcol]]))
                val.appendChild(Anchor(url, record[field]))
            else:
                node = Text()
                node.data = record[field]
                val.appendChild(node)
            row.appendChild(val)
            self.val = val
            self.key = key
            self.appendChild(row)

class BaseDocument(BaseElement):
    def __init__(self, app, **atts):
        BaseElement.__init__(self, 'html', **atts)
        self.app = app
        self.conn = app.conn
        self.body = Body()
        self.appendChild(self.body)

    def clear_body(self):
        while self.body.hasChildNodes():
            del self.body.childNodes[0]

class TxtTD(TextElement):
    def __init__(self, text):
        TextElement.__init__(self, 'td', text)
        
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

class BaseFieldTable(BaseElement):
    def __init__(self, fields, row, **atts):
        BaseElement.__init__(self, 'table', **atts)
        for field in fields:
            trow = TR()
            p = TxtTD(field)
            trow.appendChild(p)
            a = TxtTD(row[field])
            trow.appendChild(a)
            self.appendChild(trow)
        
class PackageFieldTable(BaseFieldTable):
    def __init__(self, row, **atts):
        fields = ['package', 'priority', 'section', 'installedsize',
                  'maintainer', 'version', 'description']
        BaseFieldTable.__init__(self, fields, row, **atts)
        
class MachineFieldTable(BaseFieldTable):
    def __init__(self, row, **atts):
        fields = ['machine', 'machine_type', 'kernel', 'profile', 'filesystem']
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
        ptitle = Anchor('edit.packages.%s' % trait, 'Packages')
        self.body.appendChild(SectionTitle(ptitle))
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
        
class TraitTable(BaseElement):
    def __init__(self, rows, **atts):
        BaseElement.__init__(self, 'table', **atts)
        hrow = TR()
        hrow.appendChild(TxtTD(Bold('Trait')))
        hrow.appendChild(TxtTD(Bold('Order')))
        self.appendChild(hrow)
        for row in rows:
            trow = TR()
            trow.appendChild(TxtTD(row.trait))
            trow.appendChild(TxtTD(row.ord))
            self.appendChild(trow)

class PVarTable(BaseElement):
    def __init__(self, rows, **atts):
        BaseElement.__init__(self, 'table', **atts)
        hrow = TR(bgcolor='MistyRose3')
        hrow.appendChild(TxtTD('Trait'))
        hrow.appendChild(TxtTD('Name'))
        hrow.appendChild(TxtTD('Value'))
        self.appendChild(hrow)
        for row in rows:
            trow = TR()
            trow.appendChild(TxtTD(row.trait))
            trow.appendChild(TxtTD(row.name))
            trow.appendChild(TxtTD(row.value))
            self.appendChild(trow)
            
class ProfileDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.profile = Profile(self.conn)

    def set_profile(self, profile):
        self.clear_body()
        self.profile.set_profile(profile)
        title = SimpleTitleElement('Profile:  %s' % profile, bgcolor='IndianRed',
                                   width='100%')
        self.body.appendChild(title)
        rows = self.profile.get_trait_rows()
        ptitle = Anchor('edit.traits.%s' % self.profile.current.profile, 'Traits')
        self.body.appendChild(SectionTitle(ptitle))
        #self.body.appendChild(SectionTitle('Traits'))
        if len(rows):
            self.body.appendChild(TraitTable(rows, bgcolor='IndianRed1'))
        vtitle = Anchor('edit.variables.%s' % self.profile.current.profile, 'Variables')
        self.body.appendChild(SectionTitle(vtitle))
        erows = self.profile._env.get_rows()
        if len(erows):
            self.body.appendChild(PVarTable(erows, bgcolor='MistyRose2'))
        etitle = Anchor('edit.families.%s' % self.profile.current.profile, 'Families')
        self.body.appendChild(SectionTitle(etitle))
        families = self.profile.get_families()
        flist = UnorderedList()
        for f in families:
            flist.appendChild(ListItem(f))
        self.body.appendChild(flist)
        
class FamilyDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.family = Family(self.conn)
        
    def set_family(self, family):
        self.family.set_family(family)
        parents = self.family.parents()
        erows = self.family.environment_rows()
        self.clear_body()
        title = SimpleTitleElement('Family:  %s' % family, bgcolor='IndianRed',
                                   width='100%')
        self.body.appendChild(title)
        self.body.appendChild(SectionTitle('Parents'))
        if len(parents):
            plist = UnorderedList()
            for p in parents:
                plist.appendChild(ListItem(p))
            self.body.appendChild(plist)
        vtitle = Anchor('edit.variables.%s' % self.family.current, 'Variables')
        self.body.appendChild(SectionTitle(vtitle))
        if len(erows):
            self.body.appendChild(PVarTable(erows, bgcolor='MistyRose2'))
            
class _MachineBaseDocument(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.cursor = StatementCursor(self.conn)
    
    def _add_table_row(self, table, fields, row):
        trow = TR()
        for field in fields:
            trow.appendChild(TxtTD(row[field]))
        table.appendChild(trow)

    def _add_table_header(self, table, fields, **atts):
        th = BaseElement('th', **atts)
        trow = TR()
        th.appendChild(trow)
        for field in fields:
            trow.appendChild(TxtTD(Bold(field)))
        table.appendChild(th)
        table.header = th

    def _make_table(self, fields, rows, **atts):
        table = BaseElement('table', **atts)
        self._add_table_header(table, fields)
        for row in rows:
            self._add_table_row(table, fields, row)
        return table

    def _make_footer_anchors(self, name, value):
        newanchor = Anchor('new.%s.foo' % name, 'new')
        editanchor = Anchor('edit.%s.%s' % (name, value), 'edit')
        deleteanchor = Anchor('delete.%s.%s' % (name, value), 'delete')
        self.body.appendChild(HR())
        self.body.appendChild(editanchor)
        self.body.appendChild(BR())
        self.body.appendChild(deleteanchor)
        self.body.appendChild(BR())
        self.body.appendChild(newanchor)
    
class MachineDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.machine = MachineHandler(self.conn)

    def set_machine(self, machine):
        self.machine.set_machine(machine)
        self.clear_body()
        title = SimpleTitleElement('Machine:  %s' % machine, bgcolor='IndianRed',
                                   width='100%')
        self.body.appendChild(title)
        mtable = BaseElement('table')
        for k,v in self.machine.current.items():
            trow = TR()
            trow.appendChild(TxtTD(Bold(k)))
            trow.appendChild(TxtTD(v))
            mtable.appendChild(trow)
        self.body.appendChild(mtable)
        newanchor = Anchor('new.machine.foo', 'new')
        editanchor = Anchor('edit.machine.%s' % machine, 'edit')
        self.body.appendChild(HR())
        self.body.appendChild(editanchor)
        self.body.appendChild(BR())
        self.body.appendChild(newanchor)
        
    def set_clause(self, clause):
        print 'clause---->', clause, type(clause)
        #self.machine.cursor.clause = clause
        self.clear_body()
        title = SimpleTitleElement('Machines', bgcolor='IndianRed', width='100%')
        self.body.appendChild(title)
        for row in self.machine.cursor.select(clause=clause):
            self.body.appendChild(MachineFieldTable(row, bgcolor='MistyRose3'))
            self.body.appendChild(HR())

class MachineTypeDoc(_MachineBaseDocument):
    def set_machine_type(self, machine_type):
        clause = Eq('machine_type', machine_type)
        self.clear_body()
        title = SimpleTitleElement('MachineType:  %s' % machine_type,
                                   bgcolor='IndianRed', width='100%')
        self.body.appendChild(title)

        rows = self.cursor.select(table='machine_disks', clause=clause)
        self._setup_section('Disks', ['diskname', 'device'], rows)
        modrows =  self.cursor.select(table='machine_modules', clause=clause,
                                      order=['ord'])
        self._setup_section('Modules', ['module', 'ord'], modrows)
        famrows = self.cursor.select(table='machine_type_family', clause=clause,
                                     order='family')
        self._setup_section('Families', ['family'], famrows)
        scripts = self.cursor.select(table='machine_type_scripts', clause=clause,
                                     order='script')
        self._setup_section('Scripts', ['script'], scripts)
        vars_ = self.cursor.select(table='machine_type_variables', clause=clause,
                                   order=['trait', 'name'])
        self._setup_section('Variables', ['trait', 'name', 'value'], vars_)
        self._make_footer_anchors('machine_type', machine_type)

    def _setup_section(self, name, fields, rows):
        title = SimpleTitleElement(name)
        title.set_font(color='RoyalBlue')
        self.body.appendChild(title)
        if len(rows):
            table = self._make_table(fields, rows)
            color_header(table)
            self.body.appendChild(table)
            
class FilesystemDoc(_MachineBaseDocument):
    def set_filesystem(self, filesystem):
        clause = Eq('filesystem', filesystem)
        self.clear_body()
        title = SimpleTitleElement('Filesystem:  %s' % filesystem,
                                   bgcolor='IndianRed', width='100%')
        self.body.appendChild(title)
        self.body.appendChild(TextElement('h2', 'Filesystem Mounts'))
        rows = self.cursor.select(table='filesystem_mounts', clause=clause,
                                  order=['ord'])
        fields = ['mnt_name', 'partition', 'ord']
        mounttable = self._make_table(fields, rows, bgcolor='DarkSeaGreen')
        self.body.appendChild(mounttable)
        self._make_footer_anchors('filesystem', filesystem)
