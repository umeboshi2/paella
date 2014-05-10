#!/bin/bash
set -e

. ${pillar['paella_virtualenv_basedir']}/venv/bin/activate
if [ -z `pip freeze | grep paella` ]; then
    echo "Installing paella to virtualenv"
    pushd /srv/src/paella
    python setup.py develop
    popd
else
    echo "paella already installed to virtualenv"
fi


