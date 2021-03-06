#!/bin/bash
set -e
{% set pget = salt['pillar.get'] %}

. {{ pget('paella:virtualenv_basedir', '/var/lib/paella') }}/venv/bin/activate

if true; then
    echo "Initializing paella database"
    pushd /srv/src/paella
    initialize_paella_db development.ini
    popd
else
    echo "Paella database already initialized."
fi


