import os

DEBUG = False
TESTING = False
CSRF_ENABLED = True
DB_USER = os.getenv('DB_USER', 'mariadb')
DB_PASS = os.getenv('DB_PASS', 'mariadb')
DB_HOST = os.getenv('DB_HOST', 'localhost')  
DB_NAME = os.getenv('DB_NAME', 'cluster_booking')
ADMIN_USER = os.getenv('ADMIN_PASS', 'devnation@redhat.com')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'devnati@n!')

SQLALCHEMY_DATABASE_URI_TMPL = "mysql+pymysql://%(user)s:%(passwd)s@%(host)s/%(name)s"

SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_TMPL % {
    'user': DB_USER,
    'passwd': DB_PASS,
    'host': DB_HOST,
    'name': DB_NAME
}
SQLALCHEMY_TRACK_MODIFICATIONS = False
