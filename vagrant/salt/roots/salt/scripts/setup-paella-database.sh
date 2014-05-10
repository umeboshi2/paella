#!/bin/bash
set -e

. ${pillar['paella_virtualenv_basedir']}/venv/bin/activate

if true; then
    echo "Initializing paella database"
    pushd /srv/src/paella
    initialize_paella_db development.ini
    popd
else
    echo "Paella database already initialized."
fi


