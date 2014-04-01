#!/usr/bin/env python
import os, sys
import subprocess

from livebuild.path import path


def is_loop_loaded():
    loop_loaded = False
    for line in file('/proc/modules'):
        name, mem, instances, deps, state, offset = line.split()
        if name == 'loop':
            loop_loaded = True
    return loop_loaded

def enable_loop_module():
    if not is_loop_loaded():
        cmd = ['modprobe', 'loop']
        subprocess.check_call(cmd)

def attach_loop(loop_device, filename):
    cmd = ['losetup', loop_device, filename]
    subprocess.check_call(cmd)

def detach_loop(loop_device):
    cmd = ['losetup', '-d', loop_device]
    subprocess.check_call(cmd)
    

    

if __name__ == "__main__":
    m = 'snoopy'
    arch = 'i386'
