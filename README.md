# DevNation Labs (HOWL) Dashboard

Python tiny CRUD application with Flask, SQLAlchemy and Bootstrap

It uses MariaDB as DB.

## Local Development


### Setup MariaDB

Get MariaDB from Dockerhub:

```
docker pull mariadb
```

Run MariaDB:
```
docker run --rm -d --name mariadb -v /some/local/dir:/var/lib/mysql:z -p 3306:3306 -e MYSQL_ROOT_PASSWORD=foo -ti mariadb
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


### Docker/Podman

The `docker-entrypoint.sh` is not initializating the db, it runs only the upgrades, thus it need to be done by another container or locally

#### Build

```
docker build -f Dockerfile.alpine -t devnationa-labs:latest
```


#### Run

```
docker run -e DB_USER="mariadb" -e DB_PASS="mariadb" -e DB_HOST="<SERVICE_OR_LAN_IP>" -p 8080:8080 -ti devnationa-labs
```

## OpenShift

### Create a new project

```
oc new-project devnation-labs
```

### Get MariaDB

```
oc new-app mariadb-persistent -p DATABASE_SERVICE_NAME=mariadb -p MYSQL_USER=mariadb -p MYSQL_PASSWORD=mariadb -p MYSQL_ROOT_PASSWORD=mariadb -p MYSQL_DATABASE=cluster_booking
```

### Deploy

Overriding S2I run script at `.s2i/bin/run` to run migrations and start the app.

#### Upload from local working dir

```
oc new-build --name devnation-labs -i python --binary=true
oc start-build devnation-labs --from-dir=.
oc new-app devnation-labs -e DB_USER=mariadb -e DB_PASS=mariadb -e DB_HOST=mariadb -e DB_NAME=cluster_booking
oc create route edge --service=devnation-labs
```

#### oc new-app with private repo on GitHub

```
oc create secret generic github --type=kubernetes.io/basic-auth --from-literal=username=<YOUR-GITHUB-USER> --from-literal=password=<YOUR_ACCESS_TOKEN>
oc new-app https://github.com/redhat-scholars/devnation-labs-dashboard.git -e DB_USER=mariadb -e DB_PASS=mariadb -e DB_HOST=mariadb -e DB_NAME=cluster_booking --source-secret=github
oc create route edge --service=devnation-labs-dashboard

```


#### odo (Experimental)

odo should been able to [link services](https://docs.openshift.com/container-platform/latest/cli_reference/developer_cli_odo/creating-instances-of-services-managed-by-operators.html#listing-available-services-from-the-operators-installed-on-the-cluster_creating-instances-of-services-managed-by-operators) like MariaDB, however there's no MariaDB yet inside OCP OperatorHub.

```
odo project create devnation-labs
odo create python --s2i
odo push
odo url create --port 8080 --secure
odo push
```

## Usage

- `/`: Student cluster booking form
- `/admin/panel`: Administrator panel (Upload clusters and users via CSV, assigning manually clusters)

# Reference

- https://github.com/macagua/example.flask.crud-app.git
- https://docs.sqlalchemy.org/en/latest/orm/tutorial.html


