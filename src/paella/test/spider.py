'''
This is a skeletal working web spider, with virtually no error-checking.
You need to pass in an URL that points to a directory (e.g. 
http://www.foo.com/bar/).

This version uses a thread pool, passing in each URL to be retrieved to 
a queue and getting back the list of links in another queue.  It's more 
efficient than the brute-force version because threads are re-used and
because there's no polling.
'''


import sys
import string
import urllib
import urlparse
import htmllib
import formatter
from cStringIO import StringIO
import threading
import Queue
import time



MAX_THREADS = 3






def xor(a,b):
    from operator import truth
    return truth(a) ^ truth(b)



class Token:
    def __init__(self, URL=None, shutdown=None):
        if not xor(URL, shutdown):
            raise "Tsk, tsk, need to set either URL or shutdown (not both)"
        self.URL = URL
        self.shutdown = shutdown



class Retriever(threading.Thread):
    def __init__(self, inputQueue, outputQueue):
        threading.Thread.__init__(self)
        self.inputQueue = inputQueue
        self.outputQueue = outputQueue

    def run(self):
        while 1:
            token = self.inputQueue.get()
            if token.shutdown:
                break
            else:
                self.URL = token.URL
                self.getPage()
                self.outputQueue.put(self.getLinks())

    def getPage(self):
        print "Retrieving:", self.URL
        self.page = urllib.urlopen(self.URL)
        self.body = self.page.read()
        self.page.close()
        self.parse()

    def getLinks(self):
        # Handle relative links
        links = []
        for link in self.parser.anchorlist:
	        links.append( urlparse.urljoin(self.URL, link) )
        return links

    def parse(self):
        # We're using the parser just to get the HREFs
        # We should also use it to e.g. respect <META NOFOLLOW>
        w = formatter.DumbWriter(StringIO())
        f = formatter.AbstractFormatter(w)
        self.parser = htmllib.HTMLParser(f)
        self.parser.feed(self.body)
        self.parser.close()



class RetrievePool:
    def __init__(self, numThreads):
        self.retrievePool = []
        self.inputQueue = Queue.Queue()
        self.outputQueue = Queue.Queue()
        for i in range(numThreads):
            retriever = Retriever(self.inputQueue, self.outputQueue)
            retriever.start()
            self.retrievePool.append(retriever)

    def put(self, URL):
        self.inputQueue.put(Token(URL=URL))

    def get(self):
        return self.outputQueue.get()

    def shutdown(self):
        for i in self.retrievePool:
            self.inputQueue.put(Token(shutdown=1))
        for thread in self.retrievePool:
            thread.join()



class Spider:
    def __init__(self, startURL, maxThreads):
        self.URLs = []
        self.queue = [startURL]
        self.URLdict = {startURL: 1}
        self.include = startURL
        self.numPagesQueued = 0
        self.retriever = RetrievePool(maxThreads)

    def checkInclude(self, URL):
        return string.find(URL, self.include) == 0

    def run(self):
        self.startPages()
        while self.numPagesQueued > 0:
            self.queueLinks()
            self.startPages()
        self.retriever.shutdown()
        self.URLs = self.URLdict.keys()
        self.URLs.sort()

    def startPages(self):
        while self.queue:
            URL = self.queue.pop()
            self.retriever.put(URL)
            self.numPagesQueued += 1

    def queueLinks(self):
        links = self.retriever.get()
        self.processLinks(links)
        self.numPagesQueued -= 1

    def processLinks(self, links):
        for link in links:
            print "Checking:", link
            # Make sure this is a new URL and is within the current site
            if ( not self.URLdict.has_key(link) ) and self.checkInclude(link):
                self.URLdict[link] = 1
                self.queue.append(link)


if __name__ == '__main__':
    startURL = sys.argv[1]
    spider = Spider(startURL, MAX_THREADS)
    spider.run()
    print
    for URL in spider.URLs:
        print URL
