#!/bin/bash

VERSION=1.71.0
URL_VERSION=1_71_0

PWD=`pwd`

wget https://dl.bintray.com/boostorg/release/${VERSION}/source/boost_${URL_VERSION}.tar.gz
gunzip boost_${URL_VERSION}.tar.gz
tar -xvf boost_${URL_VERSION}.tar
rm -v boost_${URL_VERSION}.tar.gz
sudo mv -v boost_${URL_VERSION}/ /opt/
sudo chown -R root:root /opt/boost_${URL_VERSION}

cd /opt/boost_${URL_VERSION}

sudo ./bootstrap.sh
sudo ./b2 install

cd ${PWD}