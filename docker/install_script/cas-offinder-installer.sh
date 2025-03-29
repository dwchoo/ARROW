#!/bin/bash
#apt-get udpate
CAS_OFFINDER_DIR=/tmp/cas-offinder
apt-get install -y gcc g++ cmake ocl-icd-opencl-dev
mkdir -p $CAS_OFFINDER_DIR
cd $CAS_OFFINDER_DIR
#wget https://github.com/snugel/cas-offinder/archive/master.zip -O cas-offinder.zip
wget https://github.com/snugel/cas-offinder/releases/download/2.4.1/cas-offinder_linux_x86-64.zip -O cas-offinder.zip
unzip cas-offinder.zip
#cd $CAS_OFFINDER_DIR/cas-offinder-master/
#cmake -G "Unix Makefiles"
#make
chmod 755 cas-offinder
cp cas-offinder /usr/local/bin/cas-offinder
rm -rf $CAS_OFFINDER_DIR
