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

Start the app:

```
DB_USER=user DB_PASS=pass DB_HOST=127.0.0.1 DB_NAME=cluster_booking python app.py
```

Open at your Web browser the following link http://127.0.0.1:8080

## OpenShift

### Get MariaDB

```
oc new-app mariadb-persistent -p DATABASE_SERVICE_NAME=mariadb -p MYSQL_USER=mariadb -p MYSQL_PASSWORD=mariadb -p MYSQL_ROOT_PASSWORD=mariadb -p MYSQL_DATABASE=cluster_booking
```

### Run on OCP (upload from local directory)

```
oc new-build --name devnation-labs -i python .
oc start-build devnation-labs --from-dir=.
oc new-app devnation-labs -e DB_USER=mariadb DB_PASS=mariadb DB_HOST=mariadb DB_NAME=cluster_booking
oc expose svc/devnation-labs
```


# Reference

- https://github.com/macagua/example.flask.crud-app.git
- https://docs.sqlalchemy.org/en/latest/orm/tutorial.html


