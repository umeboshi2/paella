    
class Trait(object):
    def __init__(self, conn, suite='sarge'):
        object.__init__(self)
        self.conn = conn
        self.suite = suite
        #self._alltraits = AllTraits(self.conn)
        #self._traits = Traits(self.conn, self.suite)
        #self._parents = TraitParent(self.conn, self.suite)
        #self._packages = TraitPackage(self.conn, self.suite)
        #self._templates = TraitTemplate(self.conn, self.suite)
        #self._debconf = TraitDebconf(self.conn, self.suite)
        #self._scripts = TraitScript(self.conn, self.suite)
        #self.current_trait = None
        self.environ = {}
        
    def set_trait(self, trait):
        self.current_trait = trait
        self.environ = TraitEnvironment(self.conn, self.suite, trait)
        #self._parents.set_trait(trait)
        #self._packages.set_trait(trait)
        #self._templates.set_trait(trait)
        #self._debconf.set_trait(trait)
        #self._scripts.set_trait(trait)

    def get_parents(self, trait=None):
        return [x.parent for x in self._parents.parents(trait)]
    
    def get_templates(self, trait=None, fields=None):
        rows = self._templates.templates(trait, fields)
        if fields is None:
            return [row.template for row in rows]
        else:
            return rows

    def get_package_rows(self):
        return self._packages.packages([self.current_trait])

    def get_traits(self):
        return self._traits.select(fields=['trait'])

    def get_trait_list(self):
        return [row.trait for row in self.get_traits()]
    
    def get_template_rows(self):
        return self._templates.templates(self.current_trait)
    
    def set_action(self, action, packages):
        self._packages.set_action(action, packages)

    def get_traitset(self):
        return self._parents.get_traitset([self.current_trait])

    def insert_packages(self, packages):
        self._packages.insert_packages(packages)

    def insert_parents(self, traits):
        self._parents.insert_parents(traits)

    def insert_template(self, template_data):
        self._templates.insert_template(template_data)

    def update_template(self, template_data):
        self._templates.update_template(template_data)

    def delete_parents(self, parents):
        self._parents.delete(parents)

    def create_trait(self, trait):
        insert_data = {'trait' : trait}
        if trait not in self._alltraits.list():
            self._alltraits.insert(data=insert_data)
        if trait not in self._traits.list():
            self._traits.insert(data=insert_data)
        else:
            raise ExistsError, '%s already exists' % trait

    def delete_trait(self, trait):
        environ = TraitEnvironment(self.conn, self.suite, trait)
        environ.clear()
        self._templates.delete_trait(trait)
        self._parents.delete_trait(trait)
        self._packages.delete_trait(trait)
        self._debconf.delete_trait(trait)
        self._scripts.delete_trait(trait)
        self._traits.set_clause([('trait', trait)])
        self._traits.delete()
        self._traits.clear(clause=True)

    def import_trait(self, ipath, suite=None):
        trait = TraitXml(file(join(path, 'trait.xml')))
        if suite is not None:
            trait.suite = suite
        all = Set([x.trait for x in self._alltraits.select()])
        suite_traits = Set([x.trait for x in self._traits.select()])
        parents = Set(trait.parents)
        debug(parents)
        if not parents.issubset(suite_traits):
            raise UnbornError, 'Parent Unborn'        
        if trait.name in suite_traits:
            raise Error, 'trait exists'
        idata ={'trait' : trait.name}
        if trait.name not in all:
            self._alltraits.insert(data=idata)
        if trait.name not in suite_traits:
            self._traits.insert(data=idata)
        lasttrait = self.current_trait
        self._parents.set_trait(trait.name)
        self._packages.set_trait(trait.name)
        self._templates.set_trait(trait.name)
        self._debconf.set_trait(trait.name)
        self._scripts.set_trait(trait.name)
        self._parents.insert_parents(trait.parents)
        for package, action in trait.packages.items():
            self._packages.insert_package(package, action)
        n = 0
        for package, template, data in trait.templates:
            #print template, data
            #templatefile = tar.get_template(data['package'], template)
            templatefile = file(join(path, 'template-%d' % n))
            idata = {'template' : template}
            #print idata
            idata.update(data)
            #print idata
            self._templates.insert_template(idata, templatefile)
            n += 1
        for debconf in trait.debconf.values():
            self._debconf.insert(debconf, trait.name)
        for script in trait.scripts:
            #scriptfile = tar.get_script(script)
            scriptfile = file(join(path, 'script-%s' % script))
            self._scripts.insert_script(script, scriptfile)
        environ = TraitEnvironment(self.conn, suite, trait.name)
        environ.update(trait.environ)
        self.set_trait(lasttrait)

    def export_templates(self, epath):
        pass
    def export_scripts(self, epath):
        pass

    def export_trait(self, epath):
        xmldata = TraitElement(self.conn, self.suite)
        xmldata.set(self.current_trait)
        bkup_path = join(tball_path, self.current_trait)
        makepaths(bkup_path)
        xmlfile = file(join(bkup_path, 'trait.xml'), 'w')
        xmlfile.write(xmldata.toprettyxml())
        xmlfile.close()
        self.export_templates(epath)
        self.export_scripts(epath)
