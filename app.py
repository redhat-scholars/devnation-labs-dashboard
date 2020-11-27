import os
import csv
import codecs
from re import search
from os import environ, path


from flask import Flask
from flask import render_template
from flask import request
from flask import redirect


from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate

from werkzeug.security import generate_password_hash, check_password_hash






app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)


geo_dict = {}
geo_dict["AMER"] = ["wdc"]
geo_dict["EMEA"] = ["fr0","ams0"]
geo_dict["APAC"] = ["che01"]

db = SQLAlchemy(app)
#migrate = Migrate(app, db)


from models import *


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("user.html")

@app.route("/_masters_page", methods=["GET", "POST"])
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
        user = User.query.filter_by(email=email).first_or_404(description='User {} not found, please contact Assistants via Slack'.format(email))
        if user:
            print("User found: " + email)
            cluster = Cluster.query.filter_by(assigned=email).first()
            if not cluster:
                cluster = Cluster.query.filter_by(geo=user.geo, assigned=None).first_or_404(description='No available cluster for region {}, please contact Assistants via Slack'.format(user.geo))
                cluster.assigned = email
                print("Assigning Cluster" + cluster.id + " to user: " + email)
                db.session.commit()
            return render_template("registration.html", cluster=cluster)
        else:
            render_template("user.html")

    except Exception as e:
        print("Couldn't update cluster assignment")
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
    return redirect("/_masters_page")

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
                                        location=row[2],
                                        company=row[8],
                                        country=row[9],
                                        job_role=row[10])
                            db.session.add(user)
                            db.session.commit()
                        except Exception as e:
                            print("Failed to add User")
                            print(e)
                i += 1
            print(data)
    return redirect("/_masters_page")

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
    return redirect("/_masters_page")


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
    return redirect("/_masters_page")

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
    return redirect("/_masters_page")




if __name__ == "__main__":
    #db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)
