import sys
from qt import *

class MainWindow(QMainWindow):

    def __init__(self, *args):
        apply(QMainWindow.__init__, (self, ) + args)

        self.mainWidget=QWidget(self);                     

        self.vlayout = QVBoxLayout(self.mainWidget, 10, 5)

        self.lsv = QListView(self.mainWidget)              
        self.lsv.addColumn("First column")
        self.lsv.setSelectionMode(QListView.Multi)
        self.lsv.insertItem(QListViewItem(self.lsv, "One"))
        self.lsv.insertItem(QListViewItem(self.lsv, "Two"))
        self.lsv.insertItem(QListViewItem(self.lsv, "Three"))

        self.bn = QPushButton("Push Me", self.mainWidget)  
        
        self.vlayout.addWidget(self.lsv)
        self.vlayout.addWidget(self.bn)

        QObject.connect(self.bn, SIGNAL("clicked()"),      
                        self.lsv, SLOT("invertSelection()"))

        self.setCentralWidget(self.mainWidget)

def main(args):
    app=QApplication(args)
    win=MainWindow()
    win.show()
    app.connect(app, SIGNAL("lastWindowClosed()")
                , app
                , SLOT("quit()")
                )
    app.exec_loop()
  
if __name__=="__main__":
        main(sys.argv)
