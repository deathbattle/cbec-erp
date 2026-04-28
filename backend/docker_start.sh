#!/bin/bash
# python manage.py makemigrations
# python manage.py migrate
# python manage.py init -y
uvicorn application.asgi:application --port 56901 --host 0.0.0.0 --workers 4
# python3 manage.py runserver 0.0.0.0:56901 &
