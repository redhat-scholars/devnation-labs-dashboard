# DevNation Labs (HOWL) Dashboard

Python tiny CRUD application with Flask, SQLAlchemy and Bootstrap

It uses MariaDB as DB.

## Local Development


### Setup MariaDB

Get MariaDB from Dockerhub:

```
podman run --rm -d --name mariadb -v /some/local/dir:/var/lib/mysql:z -p 3306:3306 -e MYSQL_ROOT_PASSWORD=foo -ti mariadb
```

### Setup Python

Start local Python 3 env:

```
virtualenv --python=/usr/bin/python3 venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

### Run locally

#### Run Migrations

```
python manage.py db init
DB_USER=user DB_PASS=pass DB_HOST=127.0.0.1 DB_NAME=cluster_booking python manage.py db migrate
DB_USER=user DB_PASS=pass DB_HOST=127.0.0.1 DB_NAME=cluster_booking python manage.py db upgrade
```

#### Run the app
 
```
DB_USER=user DB_PASS=pass DB_HOST=127.0.0.1 DB_NAME=cluster_booking python app.py
```

Open at your Web browser the following link http://127.0.0.1:8080

## OpenShift

### Create a new project

```
oc new-project devnation-labs
```

### Get MariaDB

```
oc new-app mariadb-persistent -p DATABASE_SERVICE_NAME=mariadb -p MYSQL_USER=mariadb -p MYSQL_PASSWORD=mariadb -p MYSQL_ROOT_PASSWORD=mariadb -p MYSQL_DATABASE=cluster_booking
```

### Run on OCP (upload from local directory)

Overriding S2I run script at `.s2i/bin/run` to run migrations and start the app.

```
oc new-build --name devnation-labs -i python --binary=true
oc start-build devnation-labs --from-dir=.
oc new-app devnation-labs -e DB_USER=mariadb -e DB_PASS=mariadb -e DB_HOST=mariadb -e DB_NAME=cluster_booking
oc create route edge --service=devnation-labs
```

## Usage

- `/`: Student cluster booking form
- `/admin/panel`: Administrator panel (Upload clusters and users via CSV, assigning manually clusters)

# Reference

- https://github.com/macagua/example.flask.crud-app.git
- https://docs.sqlalchemy.org/en/latest/orm/tutorial.html


