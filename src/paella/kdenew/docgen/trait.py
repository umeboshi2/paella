from forgetHTML import Table, TableRow, TableCell
from forgetHTML import Anchor, Ruler
from forgetHTML import UnorderedList, ListItem
from forgetHTML import Paragraph

from paella.db.trait import Trait

from base import RecordTable
from base import SectionTitle
from base import BaseFieldTable, BaseDocument
from base import TraitTable


class TraitEnvTable(RecordTable):
    def __init__(self, trait, env, **atts):
        fields = env.keys()
        fields.sort()
        RecordTable.__init__(self, fields, 'trait', None, env, **atts)


class PackageTable(Table):
    def __init__(self, rows, **atts):
        Table.__init__(self, **atts)
        for row in rows:
            tablerow = TableRow()
            tablerow.append(TableCell(row.package))
            tablerow.append(TableCell(row.action))
            anchor = Anchor('delete', href='delete.package.%s|%s' % (row.package, row.action))
            tablerow.append(anchor)
            self.append(tablerow)

class PackageFieldTable(BaseFieldTable):
    def __init__(self, row, **atts):
        fields = ['package', 'priority', 'section', 'installedsize',
                  'maintainer', 'version', 'description']
        BaseFieldTable.__init__(self, fields, row, **atts)
        
class TemplateTable(Table):
    def __init__(self, rows, **atts):
        Table.__init__(self, **atts)
        for row in rows:
            tablerow = TableRow()
            fake_template = row.template.replace('.', ',')
            show_anchor = Anchor(row.template, href='show.template.%s' % fake_template)
            tablerow.append(TableCell(show_anchor))
            edit_anchor = Anchor('(edit)', href='edit.template.%s' % fake_template)
            tablerow.append(TableCell(edit_anchor))
            self.append(tablerow)
        
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
        title = SectionTitle('%s Packages' % self.suite)
        title['bgcolor'] = 'IndianRed'
        title['width'] = '100%'
        self.body.set(title)
        for row in self.cursor.select(clause=clause):
            self.body.append(PackageFieldTable(row, bgcolor='MistyRose2'))
            self.body.append(Ruler())
            
class TraitDoc(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.trait = Trait(self.conn)

    def set_trait(self, trait):
        self.clear_body()
        self.trait.set_trait(trait)
        title = SectionTitle('Trait:  %s' % trait)
        title['bgcolor'] = 'IndianRed'
        title['width'] = '100%'
        self.body.set(title)
        self.body.append(Ruler())
        plist = UnorderedList()
        parents = self.trait.parents(trait=trait)
        parent_section = SectionTitle('Parents')
        parent_section.create_rightside_table()
        parent_url = 'edit.parents.%s' % trait
        parent_section.append_rightside_anchor(Anchor('edit', href=parent_url))
        self.body.append(parent_section)
        for parent in parents:
            pp = Anchor(parent, href='show.parent.%s' % parent)
            plist.append(ListItem(pp))
        self.body.append(plist)
        #ptitle_anchor = Anchor('edit.packages.%s' % trait, 'Packages')
        ptitle = SectionTitle('Packages')
        ptitle_anchor = Anchor('(new)', href='new.package.%s' % trait)
        cell = TableCell(ptitle_anchor)
        ptitle.row.append(cell)
        self.body.append(ptitle)
        rows = self.trait.packages(trait=trait, action=True)
        self.body.append(PackageTable(rows, bgcolor='SkyBlue3'))
        
        ttitle = Anchor('Templates', href='edit.templates.%s' % trait)
        self.body.append(SectionTitle(ttitle))
        rows = self.trait.templates(trait=trait, fields=['package', 'template', 'templatefile'])
        if len(rows):
            self.body.append(TemplateTable(rows, bgcolor='DarkSeaGreen3'))
        vtitle = Anchor('Variables', href='edit.variables.%s' % trait)
        self.body.append(SectionTitle(vtitle))
        if len(self.trait.environ.keys()):
            env = TraitEnvTable(trait, self.trait.environ, bgcolor='MistyRose3')
            self.body.append(env)
        stitle = SectionTitle('Scripts')
        stitle.create_rightside_table()
        stitle.append_rightside_anchor(Anchor('new', href='new.script.%s' % trait))
        self.body.append(stitle)
        slist = UnorderedList()
        for row in self.trait._scripts.scripts(trait=trait):
            script  = row.script
            p = Paragraph()
            sa = Anchor(script, href='show.script.%s' % script)
            ea = Anchor('(edit)', href='edit.script.%s' % script)
            p.append(sa)
            p.append(ea)
            slist.append(ListItem(p))
        self.body.append(slist)

# first draft complete

