#!/bin/bash
PYTHON_ver_num="3.8"
PYTHON_ver="python${PYTHON_ver_num}"

#
#일단 여기 셋팅은 건드리지 않는다. spacevim 설치하면서 python이 설치되고 덮어쓰기 때문에
#여기서 파이썬 설치하고 셋팅해도 다 없어진다.
#일단 여기에서 필요한 라이브러리는 django_app.sh에서 설치하자
#배표용 만들 때는 이 부분에서 주석을 제거하고 테스트하자
#
apt-get autoremove -y python python-* python3*
apt-get install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update
#
## install python
apt-get install -y $PYTHON_ver python3-pip ${PYTHON_ver}-dev ${PYTHON_ver}-distutils
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
$PYTHON_ver get-pip.py
$PYTHON_ver -m pip --no-cache-dir install --upgrade pip setuptools
ln -s $(which $PYTHON_ver) /usr/local/bin/python

