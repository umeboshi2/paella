import threading, Queue, time
# The worker thread gets jobs off the queue.  When the queue is empty, it 
# assumes there will be no more work and exits.  
# (Realistically workers will run until terminated.)

import pycurl

from paella.gtk import dialogs
import gtk


class DownloadThread(Thread):
    def __init__(self, url, path, progress_function):
        Thread.__init__(self)
        self.file = file(path, 'w')
        self.progress = progress_function
        self.curl = pycurl.Curl()
        self.url = url
        c = self.curl
        c.setopt(c.URL, self.url)
        c.setopt(c.WRITEFUNCTION, self.file.write)
        c.setopt(c.MAXREDIRS, 5)
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.NOPROGRESS, 0)
        c.setopt(c.PROGRESSFUNCTION, self.progress)
        c.setopt(c.NOSIGNAL, 1)
        Thread.start(self)

    def run(self):
        self.curl.perform()
        self.curl.close()
        self.file.close()
        self.progress(1, 1, 0, 0)


def func(label):
    n = 0
    while 1:
        gtk.threads_enter()
        label.set_text(str(n))
        n += 1
        gtk.threads_leave()
        time.sleep(0.1)
        
        
def worker ():
    print 'Running worker'
    time.sleep(0.1)
    while True:
        try:
            arg = q.get(block=False)
        except Queue.Empty:
            print 'Worker', threading.currentThread(),
            print 'queue empty'
            break
        else:
            print 'Worker', threading.currentThread(),
            print 'running with argument', arg
            time.sleep(0.5)

if __name__ == '__main__':
    gtk.threads_init()
    win = gtk.Window()
    win.show()
    box = gtk.VBox()
    box.show()
    win.add(box)
    label = gtk.Label('foo')
    label.show()
    box.add(label)
    threading.Thread(target=func, args=[label]).start()
    win.connect('destroy', gtk.mainquit)
    gtk.mainloop()

if False:
    # Create queue
    q = Queue.Queue()
    
    # Start a pool of 5 workers
    for i in range(5):
        t = threading.Thread(target=worker, name='worker %i' % (i+1))
        t.start()
        
    # Begin adding work to the queue
    for i in range(50):
        q.put(i)
            
    # Give threads time to run
    print 'Main thread sleeping'
    time.sleep(5)
            

