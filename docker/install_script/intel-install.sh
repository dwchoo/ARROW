#!/bin/bash
dir_path=/tmp/opencl-driver-intel/
file_name=l_opencl_p_18.1.0.015

apt-get update \
&& apt-get install -y wget curl\
&& apt-get install -y libnuma1 zlib1g libxml2 lsb-core clinfo cpio
mkdir -p $dir_path
cd $dir_path

curl -O https://registrationcenter-download.intel.com/akdlm/irc_nas/vcp/15532/l_opencl_p_18.1.0.015.tgz
tar -zxf *.tgz
sed -i 's/ACCEPT_EULA=decline/ACCEPT_EULA=accept/' $dir_path/${file_name}/silent.cfg
cd $dir_path/${file_name}/
./install.sh -s silent.cfg
rm -rf /tmp/opencl-driver-intel
