#!/bin/bash
set -e
{% set pget = salt['pillar.get'] %}

. {{ pget('paella_virtualenv_basedir', '/var/lib/paella') }}/venv/bin/activate
if [ -z `pip freeze | grep paella` ]; then
    echo "Installing paella to virtualenv"
    pushd /srv/src/paella
    python setup.py develop
    popd
else
    echo "paella already installed to virtualenv"
fi


