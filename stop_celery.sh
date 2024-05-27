#!/bin/bash

ps aux | grep 'celery -A app.celery_' | grep -v grep | awk '{print $2}' | xargs kill -9
