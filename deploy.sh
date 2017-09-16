source venv/bin/python
python manage.py collectstatic
python manage.py compress --force
supervisorctl restart rinja