#!/bin/bash
set -e

workspace=/home/vagrant/workspace
pkg=debian-archive-keyring
version=2014.1~deb7u1
pkgdir=$workspace/$pkg-$version


if [ "$(id -un)" != "vagrant" ]; then
    echo "This script must be run as the vagrant user" 1>&2
    exit 1
fi


if ! [ -d $workspace ]; then
    echo "Creating $workspace"
    mkdir -p $workspace
fi

pushd $workspace
apt-get source debian-archive-keyring

pushd $pkgdir

# This will always put a debian revision on a 
# package that can always be expected to be 
# a debian native package.
dch -l-paella 'add paella key'
dch -r 'wheezy'
cp /home/vagrant/add-paella-insecure active-keys/
cp /home/vagrant/add-paella-insecure team-members/

pushd active-keys
sha256=`sha256sum add-paella-insecure|awk '{print$1}'`
echo "sha256-$sha256  add-paella-insecure" >> index
unset sha256
# the index was already signed with the package
# maintainer's key.  Remove it and sign the index
# with the paella key.
rm index.gpg
gpg --no-tty --output index.gpg -a --detach-sign index
popd

pushd team-members
sha256=`sha256sum add-paella-insecure|awk '{print$1}'`
echo "sha256-$sha256  add-paella-insecure" > index
unset sha256
popd

pushd removed-keys
rm index.gpg
gpg --no-tty --output index.gpg -a --detach-sign index
popd


# In order to build the package and verify the results,
# it is necessary to attempt to build this manually, then
# sign the resulting keyrings and replace the signatures in 
# the keyrings directory.
pushd keyrings
active=debian-archive-keyring.gpg.asc
removed=debian-archive-removed-keys.gpg.asc
rm -f $active
rm -f $removed

cat <<EOF > $active
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1.4.12 (GNU/Linux)

iEYEABECAAYFAlRhMFYACgkQOJcw62KASuU4AgCeKEw3A6EPmQ8DsyrE+SXEWVyA
2GkAoIfM/s9LSTw9oZPLWF9nJMlk2Fnp
=In4K
-----END PGP SIGNATURE-----
EOF

cat <<EOF > $removed
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1.4.12 (GNU/Linux)

iEYEABECAAYFAlRhMIAACgkQOJcw62KASuU+SACePbE4FHvDREdLKKB9m73lQECR
eYcAn2aB38/k/SVBw/UJh0wHYocx32jV
=Lkh+
-----END PGP SIGNATURE-----
EOF
popd

debuild --no-tgz-check --no-lintian -us -uc > ../build.log

popd

echo 'back in workspace'
ls

pkgname="debian-archive-keyring_${version}-paella1_all.deb"
pkgdirname='/srv/debrepos/debian/pool/main/d/debian-archive-keyring'

if ! [ -r $pkgdirname/$pkgname ]; then
    reprepro -b /srv/debrepos/debian/ --ignore=wrongdistribution includedeb wheezy $pkgname
fi

pkgname="debian-archive-keyring-udeb_${version}-paella1_all.udeb"
if ! [ -r $pkgdirname/$pkgname ]; then
    reprepro -b /srv/debrepos/debian/ --ignore=wrongdistribution includeudeb wheezy $pkgname
fi

popd
