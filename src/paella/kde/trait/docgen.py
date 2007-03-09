from forgetHTML import Table, TableRow, TableCell
from forgetHTML import Anchor, Ruler
from forgetHTML import UnorderedList, ListItem
from forgetHTML import Paragraph

from paella.db.trait import Trait

from paella.kde.docgen.base import SimpleTitleElement
from paella.kde.docgen.base import RecordTable
from paella.kde.docgen.base import BaseFieldTable, BaseDocument
from paella.kde.docgen.base import TraitTable


class TraitEnvTable(RecordTable):
    def __init__(self, trait, env, **atts):
        fields = env.keys()
        fields.sort()
        RecordTable.__init__(self, fields, 'trait', None, env, **atts)


class PackageTable(Table):
    def __init__(self, rows, **atts):
        Table.__init__(self, **atts)
        packages = []
        package_actions = {}
        for row in rows:
            if row.package not in packages:
                packages.append(row.package)
                package_actions[row.package] = [row.action]
            else:
                package_actions[row.package].append(row.action)
        for package in packages:
            tablerow = TableRow()
            tablerow.append(TableCell(package))
            tablerow.append(TableCell(', '.join(package_actions[package])))
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
        self.set_rows(rows)
        
    def set_rows(self, rows):
        for row in rows:
            tablerow = TableRow()
            fake_template = row.template.replace('.', ',')
            show_anchor = Anchor(row.template, href='show.template.%s' % fake_template)
            tablerow.append(TableCell(show_anchor))
            template_data = '%s:%s (%s)' % (row.owner, row.grp_owner, row.mode)
            data_anchor = Anchor(template_data, href='edit.templatedata.%s' % fake_template)
            edit_anchor = Anchor('(edit)', href='edit.template.%s' % fake_template)
            del_anchor = Anchor('(delete)', href='delete.template.%s' % fake_template)
            tablerow.append(TableCell(data_anchor))
            cmdcell = TableCell()
            cmdcell.set(edit_anchor)
            cmdcell.append(del_anchor)
            tablerow.append(cmdcell)
            #tablerow.append(TableCell(edit_anchor))
            #tablerow.append(TableCell(del_anchor))
            self.append(tablerow)

    def clear_rows(self):
        self._content = []
        
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
        title = SimpleTitleElement('%s Packages' % self.suite)
        title['bgcolor'] = 'IndianRed'
        title['width'] = '100%'
        self.body.set(title)
        for row in self.cursor.select(clause=clause):
            self.body.append(PackageFieldTable(row, bgcolor='MistyRose2'))
            self.body.append(Ruler())
            
class TraitDocument(BaseDocument):
    def __init__(self, app, **atts):
        BaseDocument.__init__(self, app, **atts)
        self.trait = Trait(self.conn)
        #self.title = SectionTitle('Trait Document')
        #self.title.attributes.update(dict(bgcolor='IndianRed', width='100%'))
        self._sectitle_atts = dict(bgcolor='IndianRed', width='100%')
        self._show_description = False

    def show_description(self):
        self._show_description = True

    def hide_description(self):
        self._show_description = False

    def toggle_description(self):
        if self._show_description:
            self.hide_description()
        else:
            self.show_description()
            
    def _make_trait_title(self, trait):
        title = SimpleTitleElement('Trait:  %s' % trait, **self._sectitle_atts)
        title.cell.append(Anchor('(description)', href='edit.description.%s' % trait))
        show = '(show)'
        if self._show_description:
            show = '(hide)'
        title.cell.append(Anchor(show, href='show.description.%s' % trait))
        return title

    def _make_desc_section(self, trait):
        return self.trait.get_description()
    
    def _make_parent_section(self, trait):
        parent_section = SimpleTitleElement('Parents', **self._sectitle_atts)
        parent_section.create_rightside_table()
        parent_url = 'edit.parents.%s' % trait
        parent_section.append_rightside_anchor(Anchor('edit', href=parent_url))
        return parent_section
    
    def _make_parent_list(self, trait):
        plist = UnorderedList()
        parents = self.trait.parents(trait=trait)
        for parent in parents:
            pp = Anchor(parent, href='show.parent.%s' % parent)
            plist.append(ListItem(pp))
        return plist

    def _make_packages_section(self, trait):
        ptitle = SimpleTitleElement('Packages', **self._sectitle_atts)
        ptitle_anchor = Anchor('(new)', href='new.package.%s' % trait)
        cell = TableCell(ptitle_anchor)
        ptitle.row.append(cell)
        return ptitle

    def _make_packages_table(self, trait):
        rows = self.trait.packages(trait=trait, action=True)
        if rows:
            return PackageTable(rows, bgcolor='SkyBlue3', width='100%')
        else:
            return None
        
    def _make_templates_section(self, trait):
        ttitle = Anchor('Templates', href='edit.templates.%s' % trait)
        return SimpleTitleElement(ttitle, **self._sectitle_atts)

    def _make_templates_table(self, trait):
        rows = self.trait.templates(trait=trait, fields=['*'])
        if rows:
            return TemplateTable(rows, bgcolor='DarkSeaGreen3', width='100%')
        else:
            return None
        
    def _make_variables_section(self, trait):
        vtitle = Anchor('Variables', href='edit.variables.%s' % trait)
        return SimpleTitleElement(vtitle, **self._sectitle_atts)
    
    def _make_variables_table(self, trait):
        if len(self.trait.environ.keys()):
            return TraitEnvTable(trait, self.trait.environ, bgcolor='MistyRose3', width='100%')
        else:
            return None
        
    def _make_scripts_section(self, trait):
        stitle = SimpleTitleElement('Scripts', **self._sectitle_atts)
        stitle.create_rightside_table()
        stitle.append_rightside_anchor(Anchor('new', href='new.script.%s' % trait))
        return stitle

    def _make_scripts_list(self, trait):
        rows = self.trait._scripts.scripts(trait=trait)
        if rows:
            slist = UnorderedList()
            for row in rows:
                script  = row.script
                p = Paragraph()
                sa = Anchor(script, href='show.script.%s' % script)
                ea = Anchor('(edit)', href='edit.script.%s' % script)
                p.append(sa)
                p.append(ea)
                slist.append(ListItem(p))
            return slist
        else:
            return None
        
    def set_trait(self, trait):
        self.clear_body()
        self.trait.set_trait(trait)
        order = [self._make_trait_title]
        if self._show_description:
            order.append(self._make_desc_section)
        order += [
                 self._make_parent_section,
                 self._make_parent_list,
                 self._make_packages_section,
                 self._make_packages_table,
                 self._make_templates_section,
                 self._make_templates_table,
                 self._make_variables_section,
                 self._make_variables_table,
                 self._make_scripts_section,
                 self._make_scripts_list
                 ]
        for method in order:
            chunk = method(trait)
            if chunk is not None:
                self.body.append(chunk)

