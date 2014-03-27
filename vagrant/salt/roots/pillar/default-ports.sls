#!py
# -*- mode: python -*-

import os

ports = dict(mountd=50919,
             statd=50920,
             nfs=2049,
             bootpc=68,
             bootps=67, # this is same as dhcp
             dhcp=67,
             gkrellmd=19150,
             portmap=111,
             manage_sieve=2020)


def run():
    return {'default-ports' : ports}

            


