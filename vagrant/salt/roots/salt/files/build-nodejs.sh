#!/bin/bash

echo "Preparing to build nodejs"

mkdir /tmp/make-nodejs

pushd /tmp/make-nodejs

echo "WARNING: Need to pull or track specific revision"
git clone https://github.com/mark-webster/node-debian

pushd node-debian

node_version=$NODE_VERSION
arch=`dpkg --print-architecture`
echo "Node Version: $node_version, arch $arch"

./build.sh $node_version

node_deb=nodejs_$node_version-1_$arch.deb

if [ -f $node_deb ]; then
    echo "Installing $node_deb"
    dpkg -i $node_deb
    echo "Moving $node_deb to /root"
    mv -i $node_deb /root
fi

popd

popd

