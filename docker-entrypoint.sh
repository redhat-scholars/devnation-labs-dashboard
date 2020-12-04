#!/bin/sh

set -e

if [ -n "$INIT_DB" -a "$INIT_DB" == "yes" ]; then
    python manage.py db init
    python manage.py db migrate
fi

python manage.py db upgrade

exec python app.py
