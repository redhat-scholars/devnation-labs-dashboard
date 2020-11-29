#!/bin/sh

set -e

python manage.py db upgrade

exec python app.py
