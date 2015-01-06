#!/bin/bash
set -e

# In order to keep the development base and partial
# debian repository reasonably small, the building 
# of the doc package is bypassed.  The tests are 
# also bypassed as they require extra build depends,
# as well as being root, instead of fakeroot.  The
# tests for this build passed when the package was 
# built manually.

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
