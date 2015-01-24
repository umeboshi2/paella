#!/bin/bash
set -e

pushd /vagrant

echo "Installing node packages"
npm install

echo "Installing bower components"
bower install

echo "Building trumpet resources"
grunt

echo "Building python environment"

python setup.py develop

popd
