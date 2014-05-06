#!/usr/bin/env python
import os, sys
import operator
import time

from debrepos.microsoft.torrent import session, start_session
from debrepos.microsoft.torrent import add_torrent
from debrepos.microsoft.driverpacks import parse_rss_feed
from debrepos.microsoft.driverpacks import get_driverpacks, get_torrents

from debrepos.microsoft.driverpacks import DriverPack


EXTRA_PACKS = dict()
EXTRA_PACKS['DriverPack LAN 12.05 for Windows 2000/XP/2003 (x86)'] = \
    'http://driverpacks.net/driverpacks/windows/xp/x86/lan/12.05'
EXTRA_PACKS['DriverPack WLAN 12.02 for Windows 2000/XP/2003 (x86)'] = \
    'http://driverpacks.net/driverpacks/windows/xp/x86/wlan/12.02'


def add_extra_driverpacks(driverpacks):
    for title, link in EXTRA_PACKS.items():
        dp = DriverPack(title, link)
        driverpacks.append(dp)
        


parser = parse_rss_feed()
driverpacks = get_driverpacks(parser)
add_extra_driverpacks(driverpacks)
print "extra driverpacks added"
torrent_dir = 'torrents'

here = os.getcwd()
if not os.path.isdir(torrent_dir):
    os.mkdir(torrent_dir)
os.chdir(torrent_dir)
get_torrents(driverpacks)
os.chdir(here)




torrents = os.listdir('torrents')

start_session()

handles = []
for torrent in torrents:
    filename = os.path.join('torrents', torrent)
    handle = add_torrent(filename)
    handles.append(handle)

all_seeded = False
while not all_seeded:
    seeded = [h.is_seed() for h in handles]
    all_seeded = reduce(operator.and_, seeded)
    for h in handles:
        if not h.is_seed():
            print "downloading", h.name()
    print 50*'='
    downloading = len([h for h in handles if not h.is_seed()])
    print "Downloading %d torrents" % downloading
    print time.asctime()
    print 50*'='
    time.sleep(10)
    
