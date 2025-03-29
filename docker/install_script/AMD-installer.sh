#!/bin/bash
AMD_DRIVER=amdgpu-pro-18.10-572953.tar.xz
AMD_DRIVER_URL=https://www2.ati.com/drivers/linux/ubuntu

apt-get update \
&& apt-get install -y wget curl

mkdir -p /tmp/opencl-driver-amd
cd /tmp/opencl-driver-amd

echo AMD_DRIVER is $AMD_DRIVER; \
    curl --referer $AMD_DRIVER_URL -O $AMD_DRIVER_URL/$AMD_DRIVER; \
    tar -Jxvf $AMD_DRIVER; \
    cd amdgpu-pro-*; \
    ./amdgpu-install; \
    apt-get install -y opencl-amdgpu-pro; \
    rm -rf /tmp/opencl-driver-amd;
