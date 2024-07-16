#!/bin/sh

celery -A app.celery_single_worker worker --loglevel=info &
celery -A app.celery_worker worker --loglevel=info &
celery -A app.celery_worker beat -s --loglevel=info &

python start.py
