import os

DEBUG = False
TESTING = False
CSRF_ENABLED = True
SECRET_KEY = os.getenv('SECRET_KEY','2621a03cd4e5881cac070d675dac75d2d973c46f466aa1b5')
DB_USER = os.getenv('DB_USER', 'mariadb')
DB_PASS = os.getenv('DB_PASS', 'mariadb')
DB_HOST = os.getenv('DB_HOST', 'localhost')  
DB_NAME = os.getenv('DB_NAME', 'cluster_booking')
ADMIN_USER = os.getenv('ADMIN_USER', 'admin@email.tld')
ADMIN_PASS = os.getenv('ADMIN_PASS', '_some_difficult_pass@')

SQLALCHEMY_DATABASE_URI_TMPL = "mysql+pymysql://%(user)s:%(passwd)s@%(host)s/%(name)s"

SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_TMPL % {
    'user': DB_USER,
    'passwd': DB_PASS,
    'host': DB_HOST,
    'name': DB_NAME
}
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Avoids 'MySQL server has gone away' errors
# https://docs.sqlalchemy.org/en/13/core/pooling.html#pool-disconnects
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 3600 
}
