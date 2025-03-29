#!/bin/bash
celery -A cas_web_app worker -l info --logfile=${RESULTS_DIR}/celery_log
