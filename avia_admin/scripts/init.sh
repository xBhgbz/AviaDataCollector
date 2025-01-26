#!/bin/bash

set -e

python manage.py migrate

python manage.py add_admin

exec python manage.py runserver 0.0.0.0:8000