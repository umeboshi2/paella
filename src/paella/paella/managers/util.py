import os, sys
import subprocess

import tempfile


def prepare_recipe(content):
    one_space = chr(32)
    two_spaces = one_space * 2
    # convert new lines to spaces
    content = content.replace('\n', one_space)
    # convert tabs to spaces
    content = content.replace('\t', one_space)
    # convert all double spaces to single spaces
    while two_spaces in content:
        content = content.replace(two_spaces, one_space)
    return content

def remove_directory(directory):
    cmd = ['rm', '-fr', directory]
    return not subprocess.check_call(cmd)
    
def gen_key_command(name, directory):
    return ['salt-key', '--gen-keys=%s' % name,
            '--gen-keys-dir=%s' % directory,
            '--quiet',]


def generate_minion_keys(name):
    filepath = tempfile.mkdtemp(prefix='salt-key-')
    if not os.path.isdir(filepath):
        raise RuntimeError, "Failed to create directory %s" % filepath
    cmd = gen_key_command(name, filepath)
    retcode = subprocess.check_call(cmd)
    if retcode:
        raise RuntimeError, "Failure in salt-key -> %d" % retcode
    pem_fileame = os.path.join(filepath, '%s.pem' % name)
    pub_filename = os.path.join(filepath, '%s.pub' % name)
    data = dict(name=name,
                public=file(pub_filename).read(),
                private=file(pem_fileame).read())
    if not remove_directory(filepath):
        raise RuntimeError, "Unable to remove %s" % filepath
    # second check
    if os.path.isdir(filepath):
        raise RuntimeError, "Unable to remove %s" % filepath
    return data



if __name__ == '__main__':
    genkeys = generate_minion_keys
    
