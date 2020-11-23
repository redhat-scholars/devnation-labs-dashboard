import os
import csv
import codecs
import datetime
from re import search
from os import environ, path


from flask import Flask
from flask import render_template
from flask import request
from flask import redirect


from flask_sqlalchemy import SQLAlchemy

DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', 'my-secret-pw')
DB_HOST = os.getenv('DB_HOST', 'localhost')  
DB_NAME = os.getenv('DB_NAME', 'cluster_booking2')

SQLALCHEMY_DATABASE_URI_TMPL = "mysql+pymysql://%(user)s:%(passwd)s@%(host)s/%(name)s"

SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_TMPL % {
    'user': DB_USER,
    'passwd': DB_PASS,
    'host': DB_HOST,
    'name': DB_NAME
}


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

geo_dict = {}
geo_dict["AMER"] = ["wdc"]
geo_dict["EMEA"] = ["fr0","ams0"]
geo_dict["APAC"] = ["che01"]

db = SQLAlchemy(app)

class Cluster(db.Model):
    id = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    event_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    name = db.Column(db.String(50), unique=True, nullable=False)
    geo = db.Column(db.String(4), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=True, nullable=False)
    login_url = db.Column(db.String(2500), nullable=False)
    workshop_url = db.Column(db.String(2500), nullable=False)
    assigned = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return "<ID: {}>".format(self.id)


class User(db.Model):
    email = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    event_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    geo = db.Column(db.String(4), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    def __repr__(self):
        return "<Email: {}>".format(self.email)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("user.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    clusters = None
    users = None
    clusters = Cluster.query.all()
    users = User.query.all()
    return render_template("admin.html", clusters=clusters, users=users)

@app.route("/user/assign", methods=["POST"])
def assign_user():
    try:
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            print("User found: " + email)
            cluster = Cluster.query.filter_by(assigned=email).first()
            if not cluster:
                cluster = Cluster.query.filter_by(geo=user.geo, assigned=None).first()
                cluster.assigned = email
                print("Assigning Cluster" + cluster.id + " to user: " + email)
                db.session.commit()
            return render_template("registration.html", cluster=cluster)
        else:
            render_template("404.html")

    except Exception as e:
        print("Couldn't update cluster title")
        print(e)
    return redirect("/")

@app.route("/cluster/upload", methods=["POST"])
def upload_cluster():
    if request.method == 'POST':
            
            flask_file = request.files['fileupload']  

            if not flask_file:
                return 'Upload a CSV file'
            
            data = []
            stream = codecs.iterdecode(flask_file.stream, 'utf-8')
            i = 0
            for row in csv.reader(stream, dialect=csv.excel):
                if i > 0 and row:
                    if (all(item != '' for item in row)):
                        try:
                            geo = None
                            for key in geo_dict:
                                print(key)
                                for item in geo_dict[key]:
                                    print("Item:" + item)
                                    print("Name: " + row[1])
                                    if search(item, row[1]):
                                        geo = key

                            print("Geo " + geo)
                            cluster = Cluster(id=row[0],
                                                name=row[1],
                                                username=row[2],
                                                password=row[3],
                                                login_url=row[4],
                                                workshop_url=row[5],
                                                geo=geo)
                            db.session.add(cluster)
                            db.session.commit()
                        except Exception as e:
                            print("Failed to add Cluster")
                            print(e)
                i += 1
            print(data)
    clusters = Cluster.query.all()
    users = User.query.all()
    return render_template("admin.html", clusters=clusters, users=users)

@app.route("/user/upload", methods=["POST"])
def upload_user():
    if request.method == 'POST':

            # Create variable for uploaded file
            flask_file = request.files['fileupload']  

            if not flask_file:
                return 'Upload a CSV file'
            
            data = []
            stream = codecs.iterdecode(flask_file.stream, 'utf-8')
            i = 0
            for row in csv.reader(stream, dialect=csv.excel):
                if i > 0 and row:
                    if row[0] != '' and row[1] != '' and row[3] != '':
                        try:
                            user = User(email=row[1],
                                        name=row[0],
                                        geo=row[3],
                                        company=row[9])
                            db.session.add(user)
                            db.session.commit()
                        except Exception as e:
                            print("Failed to add User")
                            print(e)
                i += 1
            print(data)
    clusters = Cluster.query.all()
    users = User.query.all()
    return render_template("admin.html", clusters=clusters, users=users)

@app.route("/cluster/update", methods=["POST"])
def update():
    try:
        assigned = request.form.get("assigned")
        id = request.form.get("id")
        cluster = Cluster.query.filter_by(id=id).first()
        cluster.assigned = assigned
        db.session.commit()
    except Exception as e:
        print("Couldn't update cluster assigned")
        print(e)
    return redirect("/")


@app.route("/user/delete", methods=["POST"])
def delete_user():
    try:
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        db.session.delete(user)
        db.session.commit()
        print("Delete?")
    except Exception as e:
        print("Couldn't update user deletion")
        print(e)
    return redirect("/admin")

@app.route("/cluster/delete", methods=["POST"])
def delete_cluster():
    try:
        id = request.form.get("id")
        cluster = Cluster.query.filter_by(id=id).first()
        db.session.delete(cluster)
        db.session.commit()
        print("Delete?")
    except Exception as e:
        print("Couldn't update cluster deletion")
        print(e)
    return redirect("/admin")




if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)
