# small stuff here
from qt import QWidget
from qt import QGridLayout
from qt import QLabel

from kdeui import KProgress

from useless.kdebase import get_application_pointer

class SimpleProgress(KProgress):
    def __init__(self, parent, name='SimpleProgress'):
        KProgress.__init__(self, parent, name)
        self.app = get_application_pointer()
        
    # ignore args here
    def step_progress(self, *args):
        self.setProgress(self.progress() + 1)
        self.app.processEvents()


class LabeledProgress(QWidget):
    def __init__(self, parent, text='', name='LabeledProgress'):
        QWidget.__init__(self, parent, name)
        self.grid = QGridLayout(self, 2, 1, 5, 7)
        self.label = QLabel(self)
        if text:
            self.label.setText(text)
        self.progressbar = SimpleProgress(self)
        self.grid.addWidget(self.label, 0, 0)
        self.grid.addWidget(self.progressbar, 1, 0)
                  
    def setTotalSteps(self, total):
        self.progressbar.setTotalSteps(total)

    def step_progress(self, *args):
        self.progressbar.step_progress(*args)
        
        
class SuiteProgress(LabeledProgress):
    def step_progress(self, suite):
        self.label.setText('Exported suite %s' % suite)
        LabeledProgress.step_progress(self)

class TraitProgress(LabeledProgress):
    def step_progress(self, trait, path):
        print 'in TraitProgress, export trait', trait
        self.label.setText('Exported trait %s' % trait)
        LabeledProgress.step_progress(self)
        
class ProfileProgress(LabeledProgress):
    def step_progress(self, profile, path):
        self.label.setText('Profile %s exported' % profile)
        LabeledProgress.step_progress(self)
        
class FamilyProgress(LabeledProgress):
    def step_progress(self, family, path):
        self.label.setText('Family %s exported' % family)
        LabeledProgress.step_progress(self)
        
