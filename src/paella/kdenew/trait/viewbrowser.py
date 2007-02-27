import tarfile

from qt import SIGNAL

from kdeui import KMessageBox

from kfile import KFileDialog

from useless.kdebase.dialogs import BaseRecordDialog

from paella.db.trait import Trait
from paella.kdenew.base import split_url
from paella.kdenew.base.viewbrowser import ViewBrowser

from base import ParentAssigner
from base import ViewWindow
from base import ScriptNameDialog

from docgen import TraitDoc
from template import TemplateViewWindow


class TraitView(ViewBrowser):
    # The TraitDoc holds the main traitdb object
    def __init__(self, parent):
        ViewBrowser.__init__(self, parent, TraitDoc)
        # setup dialog pointers
        # just one now
        self._dialog = None
        
    def set_trait(self, trait):
        self.doc.set_trait(trait)
        self.setText(self.doc.output())

    def resetView(self):
        self.set_trait(self.doc.trait.current_trait)

    def set_suite(self, suite):
        self.doc.suite = suite
        self.doc.trait = Trait(self.app.conn, suite=suite)

    # handle url
    # this method is too long in original TraitView browser
    # this needs to split up into more methods
    def setSource(self, url):
        action, context, ident = split_url(url)
        if action == 'show':
            self._perform_show_action(context, ident)
        elif action == 'edit':
            self._perform_edit_action(context, ident)
        elif action == 'new':
            self._perform_new_action(context, ident)
        elif action == 'delete':
            self._perform_delete_action(context, ident)
        else:
            raise NotImplementedError(self, url)

    # add package to trait from dialog
    def slotAddPackage(self):
        win = self._dialog
        data = win.getRecordData()
        self.doc.trait.add_package(data['package'], data['action'])
        self.resetView()
        

    # tarball selected in dialog, make another dialog with url tar://filename
    def fileSelected(self):
        win = self._dialog
        filename = str(win.selectedFile())
        win = KFileDialog('.', '', self, 'SystemTarball', True)
        win.setURL(KURL('tar://%s' % filename))
        win.connect(win, SIGNAL('okClicked()'), self.newTemplateSelected)
        win.tarball_filename = filename
        win.show()
        self._dialog = win
        
    # template selected from tarball dialog
    def newTemplateSelected(self):
        win = self._dialog
        kurl = win.selectedURL()
        print 'url', str(kurl.url())
        print 'path in tar is', str(kurl.path())
        fullpath = str(kurl.path())
        tarball = win.tarball_filename
        if fullpath.startswith(tarball):
            print 'fullpath', fullpath, 'tarball', tarball
            tpath = fullpath.split(tarball)[1]
            while tpath.startswith('/'):
                tpath = tpath[1:]
            tarfileobj = tarfile.open(tarball)
            self.doc.trait.insert_template_from_tarfile(tpath, tarfileobj)
            self.resetView()
        else:
            raise RuntimeError, '%s does not contain %s' % (fullpath, tarball)

        
    # don't know what job was supposed to be here
    def slotGetFromTarDone(self, job):
        raise MethodNotImplementedError(self, 'TraitView.slotGetFromTarDone')

    def slotMakeNewScript(self):
        scriptname = self._dialog.scriptname()
        KMessageBox.information(self, 'make new %s script' % scriptname)

    def _convert_template_id(self, ident):
        newid = ident.replace(',', '.')
        package, template = newid.split('...')
        return package, template
    
    def _perform_show_action(self, context, ident):
        if context == 'parent':
            winclass = self.parent().__class__
            if winclass.__name__ == 'TraitMainWindow':
                win = winclass(self.parent(), self.doc.suite)
                win.mainView.set_trait(ident)
            else:
                msg = 'Unable to show parent with class %s' % winclass.__name__
                raise RuntimeError, msg
        elif context == 'template':
            win = TemplateViewWindow(self)
            package, template = self._convert_template_id(ident)
            filedata = self.doc.trait._templates.templatedata(package, template)
            win.mainView.setText(filedata)
        elif context == 'script':
            # need to call public method here
            scriptfile = self.doc.trait._scripts.scriptdata(ident)
            win = ViewWindow(self.parent(), SimpleEdit, name='ScriptView')
            win.mainView.setText(scriptfile)
        else:
            raise MethodNotImplementedError(self, 'TraitView._perform_show_action')
        win.show()
        
    def _perform_edit_action(self, context, ident):
        if context == 'templates':
            win = KFileDialog('.', '', self, 'SystemTarball', True)
            win.connect(win, SIGNAL('okClicked()'), self.fileSelected)
            win.show()
            self._dialog = win
            
        elif context == 'packages':
            raise RuntimeError, 'packages not implemented yet'
        elif context == 'script':
            self.doc.trait.edit_script(ident)
        elif context == 'parents':
            win = ParentAssigner(self, ident, self.doc.suite)
            win.connect(win, SIGNAL('okClicked()'), self.resetView)
            win.show()
        elif context == 'variables':
            KMessageBox.information(self, 'edit variables')
        elif context == 'template':
            package, template = self._convert_template_id(ident)
            self.doc.trait.edit_template(package, template)
        else:
            raise MethodNotImplementedError(self, 'TraitView._perform_edit_action')
        
    def _perform_new_action(self, context, ident):
        if context == 'package':
            win = BaseRecordDialog(self, ['package', 'action'])
            win.connect(win, SIGNAL('okClicked()'), self.slotAddPackage)
            win.setRecordData(dict(action='install'))
            win.show()
            self._dialog = win
        elif context == 'script':
            win = ScriptNameDialog(self)
            win.connect(win, SIGNAL('okClicked()'), self.slotMakeNewScript)
            win.show()
            self._dialog = win
        else:
            raise MethodNotImplementedError(self, 'TraitView._perform_new_action')

    def _perform_delete_action(self, context, ident):
        if context == 'package':
            debug(context, ident)
            package, action = ident.split('|')
            debug('delete package', package, action)
            self.doc.trait.delete_package(package, action)
            self.resetView()
        else:
            raise RuntimeError, '%s context not implemented' % context
        
