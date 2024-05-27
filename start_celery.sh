#!/bin/bash

source .venv/bin/activate
celery -A app.celery_single_worker worker --loglevel=info &
celery -A app.celery_worker worker --loglevel=info &
celery -A app.celery_worker beat -s --loglevel=info &
