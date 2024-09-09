#!/bin/bash
cd "`dirname $0`"
. .venv/bin/activate && \
nohup python manage.py runserver 0.0.0.0:8000 >/var/log/laguna.log 2>&1 &