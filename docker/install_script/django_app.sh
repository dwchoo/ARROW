#!/bin/bash
# celery redis install
#pip install -U django
#pip install celery[redis]==4.4.7
#pip install -U redis django-celery-beat django-celery-results

apt install -y python3-gi-cairo

pip install -r $(dirname "$0")/requirements.txt

# install redis
apt install -y pkg-config
wget http://download.redis.io/redis-stable.tar.gz 
tar -xvzf redis-stable.tar.gz
cd redis-stable
make install


# python lib
#pip install -U numpy pandas plotly fastparquet pyarrow \
#	django-tables2 django-ajax-tables django-filter django-extensions
