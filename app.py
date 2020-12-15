import os
import csv
import codecs
import csv
import io
import xlsxwriter

from io import BytesIO
from re import search
from os import environ, path





from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask import url_for
from flask import make_response
from flask import send_file


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_


#from flask_migrate import Migrate

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import login_user, logout_user, login_required, LoginManager







app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)


geo_dict = {}
geo_dict["AMER"] = ["wdc"]
geo_dict["EMEA"] = ["fra0","ams0"]
geo_dict["APAC"] = ["che01"]

geo_twin = {}
geo_twin["AMER"] = ["EMEA"]
geo_twin["EMEA"] = ["AMER", "APAC"]
geo_twin["APAC"] = ["EMEA"]


db = SQLAlchemy(app)
#migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)



from models import *



@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("user.html")

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return Admin.query.get(int(user_id))

@app.route('/admin/login', methods=["GET"])
def login():
    return render_template('login.html')

@app.route('/admin/login', methods=['POST'])
def login_post():
    try:
        email = request.form.get("email")
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        admin = Admin.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not admin or not check_password_hash(admin.password, password):
            flash('Please check your login details and try again')
            print('Invalid login attempt for admin: {}', email)
            return redirect("/admin/login") # if the user doesn't exist or password is wrong, reload the page

        print(admin)
        # if the above check passes, then we know the user has the right credentials
        login_user(admin, remember=remember)
        return redirect("/admin/panel")
    except Exception as e:
        print("Couldn't login admin: {}", email)
        print(e)
        db.session.rollback()
    return redirect("/admin/login")

@app.route("/admin/logout")
@login_required
def logout():
    logout_user()
    return redirect("/admin/login")

@app.route("/admin/panel", methods=["GET"])
@login_required
def admin():
    clusters = None
    users = None
    db.session.commit()
    clusters = Cluster.query.all()
    users = User.query.all()

    i = 0

    for cluster in clusters:
        if cluster.assigned is not None:
            i += 1
    print("Refresh Clusters count: ", len(clusters))
    print("Refresh Users count: ", len(users))
    return render_template("admin.html", clusters=clusters, users=users, assigned=i)

@app.route("/user/assign", methods=["POST"])
def assign_user():
    try:
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            print("User found: " + email)
            cluster = Cluster.query.with_for_update(of=Cluster).populate_existing().filter_by(assigned=email).first()
            if not cluster:
                cluster = Cluster.query.with_for_update(of=Cluster).populate_existing().filter_by(assigned=None, geo=user.geo).first()

                if not cluster:
                    print("Cluster not found in user's region {}, trying in near regions {}".format(user.geo, geo_twin[user.geo]))
                    cluster =  Cluster.query.with_for_update(of=Cluster).populate_existing().filter(Cluster.assigned==None).filter(or_(Cluster.geo == g for g in geo_twin[user.geo])).first()

                if cluster:
                    cluster.assigned = email
                    print("Assigning Cluster: " + cluster.id + " to user: " + email)
                    db.session.commit()
                else:
                    flash('No available clusters for user {} in region {}'.format(email, user.geo))
                    print('No available clusters for user {} in region {}'.format(email, user.geo))
                    return render_template("user.html")
            return render_template("registration.html", cluster=cluster)
        else:
            flash('User {} not found'.format(email))
            print('User {} not found'.format(email))
            return render_template("user.html")

    except Exception as e:
        print("Couldn't assign a cluster to: {}", email)
        print(e)
        db.session.rollback()
    return redirect("/")

@app.route("/cluster/upload", methods=["POST"])
@login_required
def upload_cluster():
    if request.method == 'POST':
            
            flask_file = request.files['fileupload']  

            if not flask_file:
                return 'Please upload a CSV file'
            
            data = []
            stream = codecs.iterdecode(flask_file.stream, 'utf-8')
            i = 0
            for row in csv.reader(stream, dialect=csv.excel):
                if i > 0 and row:
                    if (all(item != '' for item in row)):
                        try:
                            geo = None
                            for key in geo_dict:
                                #print(key)
                                for item in geo_dict[key]:
                                    #print("Item:" + item)
                                    #print("Name: " + row[1])
                                    if search(item, row[1]):
                                        geo = key

                            print("Geo found:" + geo)
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
                            print("Failed to add Cluster: {}", row[0])
                            print(e)
                            db.session.rollback()
                i += 1
            print("Row: ", i)
    return redirect("/admin/panel")

@app.route("/user/upload", methods=["POST"])
@login_required
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
                    if row[1] != '' and row[3] != '':
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
                            print("Failed to add User: {}", row[1])
                            print(e)
                            db.session.rollback()
                i += 1
            print(data)
    return redirect("/admin/panel")

@app.route("/cluster/update", methods=["POST"])
@login_required
def update():
    try:
        assigned = request.form.get("assigned")
        id = request.form.get("id")
        cluster = Cluster.query.filter_by(id=id).first()
        cluster.assigned = assigned
        db.session.commit()
    except Exception as e:
        print("Couldn't assign cluster {} to {}", id, assigned)
        print(e)
        db.session.rollback()
    return redirect("/admin/panel")


@app.route("/user/delete", methods=["POST"])
@login_required
def delete_user():
    try:
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        db.session.delete(user)
        db.session.commit()
        print("Deleted user: ", email)
    except Exception as e:
        print("Couldn't delete user: {}", email)
        print(e)
        db.session.rollback()
    return redirect(url_for('admin'))


@app.route("/user/add", methods=["POST"])
@login_required
def add_user():
    try:
        email = request.form.get("c_email")
        name = request.form.get("c_fullname")
        company = request.form.get("c_company")
        geo = request.form.get("c_geo")
        country = request.form.get("c_country")
        city = request.form.get("c_city")
        job_role = request.form.get("c_job_role")

        user = User(email=email,
                    name=name,
                    company=company,
                    geo=geo,
                    country=country,
                    location=city,
                    job_role=job_role)
        db.session.add(user)
        db.session.commit()
        print("Added new user: {}", user)
    except Exception as e:
        print("Couldn't add user {}:", email)
        print(e)
        db.session.rollback()
    return redirect(url_for('admin'))

@app.route("/cluster/delete", methods=["POST"])
@login_required
def delete_cluster():
    try:
        id = request.form.get("id")
        cluster = Cluster.query.filter_by(id=id).first()
        db.session.delete(cluster)
        db.session.commit()
        print("Deleted cluster: {} ", id)
    except Exception as e:
        print("Couldn't delete cluster: {}", id)
        print(e)
        db.session.rollback()
    return redirect("/admin/panel")

@app.route("/admin/data/export", methods=["GET"])
@login_required
def export_csv():
    csvList = [("name","email","location","GEO",
               "Company Name","Country","What is your job role/title?",
               "Cluster ID", "Cluster Name","Username","User Password",
               "Login URL", "Workshop URL")]
    try:
        results = db.session.execute("""
            SELECT u.name, u.email, u.location, u.geo, u.company, u.country,
                u.job_role, c.id, c.name, c.username, c.password, c.login_url, c.workshop_url 
            FROM cluster c 
            RIGHT OUTER JOIN user u ON c.assigned=u.email
            ORDER BY c.name DESC""")
        for row in results:
            csvList.append(row)
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerows(csvList)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    except Exception as e:
        print("Couldn't export CSV data")
        print(e)
        db.session.rollback()

@app.route("/admin/data/export_xlsx", methods=["GET"])
@login_required
def export_xlsx():
    assigned_clusters_header = ["name","email","location","GEO",
               "Company Name","Country","What is your job role/title?",
               "Cluster ID", "Cluster Name","Username","User Password",
               "Login URL", "Workshop URL"]
    unused_clusters_header = [ "id", "name"]

    try:
        results = db.session.execute("""
            SELECT u.name, u.email, u.location, u.geo, u.company, u.country,
                u.job_role, c.id, c.name, c.username, c.password, c.login_url, c.workshop_url 
            FROM cluster c 
            RIGHT OUTER JOIN user u ON c.assigned=u.email
            ORDER BY c.name DESC""")


        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet_assigned = workbook.add_worksheet('Registered+Assigned')
        worksheet_unused = workbook.add_worksheet('Unused clusters')
        

        bold = workbook.add_format({'bold': 1,'font_size':11})
        worksheet_assigned.set_column(0, 1, 30)
        worksheet_assigned.set_column(2, 2, 20)
        worksheet_assigned.set_column(4, 6, 20)
        worksheet_assigned.set_column(7, 8, 30)


        col = 0
        for item in assigned_clusters_header:
            worksheet_assigned.write(0, col, item, bold)
            col += 1

        col = 0
        for i, row in enumerate(results):
            worksheet_assigned.write_row(i+1, 0, row)
            col += 1

        
        results = db.session.execute("""
            SELECT id, name 
            FROM cluster
            WHERE assigned is NULL 
            ORDER BY name DESC""")
        
        worksheet_unused.set_column(0, 1, 30)
        
        col = 0
        for item in unused_clusters_header:
            worksheet_unused.write(0, col, item, bold)
            col += 1
        
        col = 0
        for i, row in enumerate(results):
            worksheet_unused.write_row(i+1, 0, row)
            col += 1
        

        workbook.close()

        output.seek(0)

        filename = "HOWL-{}-ClustersData.xlsx".format(datetime.datetime.now().strftime('%m/%d/%Y'))
        return send_file(output,
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                         as_attachment=True,
                         attachment_filename=filename)

    except Exception as e:
        print("Couldn't export XLSX data")
        print(e)
        db.session.rollback()


if __name__ == "__main__":
    #db.create_all()
    admin = Admin.query.filter_by(email=app.config['ADMIN_USER']).first()
    if not admin:
        try:
            admin = Admin(email=app.config['ADMIN_USER'], password=generate_password_hash(app.config['ADMIN_PASS'], method='sha256'))
            db.session.add(admin)
            db.session.commit()
        except Exception as e:
            print("Couldn't add admin {}", app.config['ADMIN_USER'])
            print(e)
            db.session.rollback()
    app.run(host='0.0.0.0', port=8080, debug=True)
