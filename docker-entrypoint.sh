#!/bin/bash
set -e

python manage.py migrate &&
  python manage.py loaddata rinja/fixtures/rinja_stock.json &&
  python manage.py loaddata rinja/fixtures/django_site.json &&
  python manage.py loaddata rinja/fixtures/socialaccount_socialapp.json &&
  python manage.py collectstatic --noinput &&
  python manage.py runserver 0.0.0.0:8000
