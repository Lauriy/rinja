#!/bin/bash
set -e

python manage.py migrate &&
  python manage.py loaddata rinja/fixtures/auth_user.json &&
  python manage.py loaddata rinja/fixtures/rinja_stock.json &&
  python manage.py runserver 0.0.0.0:8000
