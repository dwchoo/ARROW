#!/bin/bash
redis-server &
bash celery_command.sh &
python $(dirname "$0")/manage.py runserver 0:8080 --insecure
