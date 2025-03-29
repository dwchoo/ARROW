#!/bin/bash
# intel
dir_path=/tmp/opencl-driver-intel/
file_name=l_opencl_p_18.1.0.015

export DEBIAN_FRONTEND=noninteractive
apt-get update \
&& apt-get install -y apt-utils wget curl unzip \
libnuma1 zlib1g libxml2 lsb-core clinfo;
mkdir -p $dir_path
cd $dir_path

curl -O https://registrationcenter-download.intel.com/akdlm/irc_nas/vcp/15532/l_opencl_p_18.1.0.015.tgz
tar -zxf *.tgz
sed -i 's/ACCEPT_EULA=decline/ACCEPT_EULA=accept/' $dir_path/${file_name}/silent.cfg
cd $dir_path/${file_name}/
./install.sh -s silent.cfg
rm -rf /tmp/opencl-driver-intel

# nvidia
mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd

# cas-offinder install
CAS_OFFINDER_DIR=/tmp/cas-offinder/
apt-get install -y gcc g++ cmake ocl-icd-opencl-dev
mkdir -p $CAS_OFFINDER_DIR
cd $CAS_OFFINDER_DIR
#wget https://github.com/snugel/cas-offinder/archive/master.zip -O cas-offinder.zip
wget https://github.com/snugel/cas-offinder/releases/download/2.4.1/cas-offinder_linux_x86-64.zip -O cas-offinder.zip
unzip cas-offinder.zip
chmod 755 cas-offinder
cp cas-offinder /usr/local/bin/cas-offinder
rm -rf $CAS_OFFINDER_DIR
