#!/bin/sh -e
if ! [ -d `pwd`/debian ]; then
    echo "no debian directory found."
    echo "this script needs to be run from the toplevel of the source directory."
    exit 1
else
    echo "found debian/ , we presume we're in the right place"
fi
version=`dpkg-parsechangelog | grep ^Version | awk '{print $2}' | cut -f1 -d-`
echo "version is " $version
# although we have two checks for the upstream
# tarballs, one download from uscan should get both
# of them.
if ! [ -e ../guspat-$version-required.tar.gz ]; then
    echo "downloading upstream sources"
    uscan --verbose --force-download --no-symlink
fi
# The uscan here should only run if the optional
# tarball has somehow been deleted.  This will
# also re-download the required tarball, overwriting
# the one that's present.
if ! [ -e ../guspat-$version-optional.tar.gz ]; then
    echo "downloading upstream sources"
    uscan --verbose --force-download --no-symlink
fi

mkdir timidity-guspat-installer
pushd timidity-guspat-installer
gzip -cd ../../guspat-$version-required.tar.gz | tar x
gzip -cd ../../guspat-$version-optional.tar.gz | tar x
popd
# this will overwrite the .orig.tar.gz if it exists.
tar c timidity-guspat-installer | gzip > ../timidity-guspat-installer_$version.orig.tar.gz
rm timidity-guspat-installer -fr
gzip -cd ../timidity-guspat-installer_$version.orig.tar.gz | tar x --strip-components 1
#mv timidity-guspat-installer/timidity .
#rmdir timidity-guspat-installer
# here we will be warned that there are deletions that will be ignored
# this is ok, and will not be a problem when you use dpkg-source -x 
# on the .dsc file that's created after this.
dpkg-buildpackage -S
