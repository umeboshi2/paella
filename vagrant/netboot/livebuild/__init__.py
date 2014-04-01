import hashlib


BLOCK_SIZE = 1024

def md5sum(afile):
    """returns the standard md5sum hexdigest
    for a file object"""
    m = hashlib.md5()
    block = afile.read(BLOCK_SIZE)
    while block:
        m.update(block)
        block = afile.read(BLOCK_SIZE)
    return m.hexdigest()

if __name__ == '__main__':
    pass

    
