#!/bin/bash
set -e

dpkg --get-selections | cut -f1 -d: | awk '{print $1 "\tinstall"}' > /srv/debrepos/debian/conf/local-packages

