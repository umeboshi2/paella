#!/bin/bash
set -e

. /var/lib/paella/venv/bin/activate

if [ -z `pip freeze | grep paella` ]; then
    echo "Installing paella to virtualenv"
    pushd /srv/src/paella
    python setup.py develop
    popd
else
    echo "paella already installed to virtualenv"
fi


