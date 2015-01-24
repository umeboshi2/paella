import os, sys
import subprocess
import json

filename = 'build.coffee'
if not os.path.isfile(filename):
    raise RuntimeError, "No build.coffee"


if __name__ == '__main__':
    cmd = ['coffee', '-bc', filename]
    subprocess.check_call(cmd)
    built_filename = 'build.js'
    if not os.path.isfile(built_filename):
        raise RuntimeError, "problem with build"
    contents = file(built_filename).read()
    contents = contents.strip()
    while contents.endswith(';'):
        contents = contents[:-1]
    with file(built_filename, 'w') as output:
        output.write(contents)
        
