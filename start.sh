#!/bin/bash
set -e
python manage.py migrate --noinput
exec gunicorn pet_trash.wsgi
