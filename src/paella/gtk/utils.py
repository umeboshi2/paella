from paella.base.objects import DownloadThread
from paella.base.objects import DlWorker, DownloadQueue

from paella.gtk import dialogs
from paella.gtk.windows import MenuWindow

import pycurl

from gtk import ProgressBar, VBox, Label, Button, HBox
from gtk import mainloop, mainquit, TRUE, FALSE
from gtk import threads_enter, threads_leave, threads_init


class DownloadStatus(VBox):
    def __init__(self, url, path):
        VBox.__init__(self)
        self.label = Label(path)
        self.label.show()
        self.pack_start(self.label, FALSE, FALSE, 0)
        self.pbar = ProgressBar()
        self.pack_end(self.pbar, FALSE, FALSE, 0)
        self.pbar.show()
        self.show()
        self._done = 0
        #self.thread = DownloadThread(url, path, self.progress)
        self.thread = DownloadThread(url, path, self.progress)
        #self.button = Button('start')
        #self.button.connect('clicked', self.start)
        #self.button.show()
        #self.pack_end(self.button, FALSE, FALSE, 0)
        self._started = False
        
    def progress(self, dt, dd, ut, ud):
        threads_enter()
        print 'in progress', dt, dd, ut, ud
        if dt == 0:
            self._done += 0.1
            if self._done >= 1:
                self._done = 0
        else:
            self._done = float(dd) / float(dt)
        print '_done', self._done
        self.pbar.set_fraction(self._done)
        threads_leave()
        
    def start(self, *args):
        if not self._started:
            self.thread.start()
            self._started = True

class _DownloadStatus(HBox):
    def __init__(self, queue):
        HBox.__init__(self)
        self.thread = DlWorker(queue, self.progress, self.set_url)
        self.label = Label('hello')
        self.pbar = ProgressBar()
        self.pack_start(self.label, FALSE, FALSE, 0)
        self.pack_end(self.pbar, FALSE, FALSE, 0)
        self.label.show()
        self.pbar.show()
        self.show()
        self._done = False
        self._started = False

    def progress(self, dt, dd, ut, ud):
        threads_enter()
        print 'in progress', dt, dd, ut, ud
        if dt == 0:
            self._done += 0.1
            if self._done >= 1:
                self._done = 0
        else:
            self._done = float(dd) / float(dt)
        print '_done', self._done
        self.pbar.set_fraction(self._done)
        threads_leave()

    def set_url(self, url):
        self.label.set_text(url)
        
    def start(self, *args):
        if not self._started:
            self.thread.start()
            self._started = True        

class DownloadPoolBox(VBox):
    def __init__(self, maxthreads=3):
        VBox.__init__(self)
        self.threads = []
        self.queue = DownloadQueue()
        self.show()
        for i in range(maxthreads):
            thread = _DownloadStatus(self.queue)
            thread.start()
            self.threads.append(thread)
            self.pack_end(thread, FALSE, FALSE, 0)

    def put(self, url, path):
        self.queue.put(url, path)
        
        
if __name__ == '__main__':
    threads_init()
    win = MenuWindow()
    win.connect('destroy', mainquit)
    win.set_usize(200, 100)
    #url = 'http://paella/debian/dists/sid/Release'
    mirror = 'paella'
    #mirror = 'ftp.us.debian.org'
    url = 'http://%s/debian/dists/sid/main/binary-i386/Packages.gz' %mirror
    dl = DownloadStatus(url, 'hellothere')
    win.vbox.add(dl)
    #threads_enter()
    #dl.start()
    mainloop()
    #threads_leave()
