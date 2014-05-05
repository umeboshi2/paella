#!/bin/bash
set -e

if ! [ -d debian ]; then
    echo "ERROR: no debian subdirectory, is the cwd correct?"
    exit 1
fi

echo "Removing doc install files..."
rm -f debian/wimlib-doc.docs debian/wimlib-doc.examples 

echo "Running ./bootstrap"
./bootstrap 

echo "Building Package"
env DEB_BUILD_OPTIONS=nocheck DEBUILD_DPKG_BUILDPACKAGE_OPTS="-B" debuild --preserve-envvar=DEB_BUILD_OPTIONS --preserve-envvar=DEBUILD_DPKG_BUILDPACKAGE_OPTS --no-lintian --no-tgz-check -us -uc -d -B

echo "Build Complete."
