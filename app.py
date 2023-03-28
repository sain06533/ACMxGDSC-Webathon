from flask import Flask, flash, render_template, request, redirect, url_for, session, g
import requests
import json
from flask_bcrypt import Bcrypt
import os
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.message import EmailMessage
import sqlite3

app= Flask(__name__)

bcrypt = Bcrypt(app)
email_sender = '22075A0523@vnrvjiet.in'
email_pass = "iwvpoglercuiwrxz"
email_receiver = 'abbojushanthan@gmail.com'


basedir = os.path.abspath(os.path.dirname(__file__))
baseDB = os.path.join(basedir, 'likhijr.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + baseDB
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///' + baseDB
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



@app.before_request
def before_request():
    g.firstname = None

    if 'firstname' in session:
        g.firstname = session['firstname']

class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(length=30), nullable=False)
    lastname = db.Column(db.String(length=30), nullable=False)
    email = db.Column(db.String(length=50), nullable=True, unique=True)
    password = db.Column(db.String(length=60), nullable=False)
    phnumber  = db.Column(db.String(), nullable=False, unique=True)
    aadhar = db.Column(db.String(), nullable=False)
    noofper = db.Column(db.Integer(), nullable=False)
  
        


@app.route('/')
def home():
    return render_template('index.html')
    

@app.route('/login',methods =['GET', 'POST'])
def login():
     
    if request.method == 'POST' :       
        user = User.query.filter_by(phnumber=request.form['phnumber']).first()  
        if user:
            session.pop('firstname',None)

            if (bcrypt.check_password_hash(user.password,request.form['password'])) == True :
                session['loggedin'] = True
                session['id'] = user.id             
                session['firstname'] = user.firstname           
                flash('Success! You are logged in as: ' + session['firstname'], category='success')
                return redirect(url_for('search'))
            else:
                flash('Username and password are not match! Please try again', category='danger')
                return render_template('login.html')
        else:
            flash('Username and password are not match! Please try again', category='danger')
            return render_template('login.html')
    else:
        return render_template('login.html')

   
@app.route('/register', methods =['GET', 'POST'])
def register():

    if request.method == 'POST' :     
        user = User.query.filter_by(phnumber=request.form['phnumber']).first()
        if user:
            flash('Phone Number already exists !', category='danger')
            
        else:
            pwd = request.form['password']           
            hash_password = bcrypt.generate_password_hash(pwd)
            
            new_user = User(firstname=request.form['firstname'],lastname=request.form['lastname'],email=request.form['email'],password=hash_password,phnumber=request.form['phnumber'],aadhar=request.form['aadhar'],noofper=request.form['aadhar'])
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully!", category='success')                                     
    return render_template('login.html')


@app.route('/about-us')
def aboutus():
    return render_template('about-us.html')


@app.route('/contact-us', methods =['GET', 'POST'])
def contactus():
    if request.method == 'POST' :
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        subject = "New Contact"
        body = "From " + name + ",\n"+ email +",\n\n"+ message
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)
        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(email_sender,email_pass)
        server.sendmail(email_sender,email_receiver,em.as_string())
        flash("You have succesfully contacted us, we will soon look through it", category='success')     
        if g.firstname: 
            return redirect(url_for('jobsearch'))
        else :
            return render_template('index.html')
    else:
        return render_template('contact.html')

@app.route('/search', methods =['GET', 'POST'])         
def search():
    if g.firstname:
        if request.method == 'POST':
            where = request.form['loc']
            type = request.form['type']
            conn = sqlite3.connect("C:\\Users\\abboj\\OneDrive\\Desktop\\job-recommender-main\\likhijr.db")
            c = conn.cursor()

            if type=='hg':
                print(where)
                c.execute(f"SELECT * FROM housing where city = '{where}';")
                tmplist = c.fetchall()
                conn.commit()
                conn.close()

                return render_template('searchhg.html', data= tmplist)
            elif type=='hc':
                c.execute(f"SELECT * FROM healthcare where city = '{where}';")
                tmplist = c.fetchall()
                conn.commit()
                conn.close()

                return render_template('searchhc.html', data= tmplist)

            elif type=='jt':
                c.execute(f"SELECT * FROM jobtraining where city = '{where}';")
                tmplist = c.fetchall()
                conn.commit()
                conn.close()

                return render_template('searchjt.html', data= tmplist)
            
            
                
           
        else:
            return render_template('search.html')
    else:
        return redirect(url_for('login'))

@app.route('/jobsearch', methods =['GET', 'POST'])
def jobsearch():
    if g.firstname:
        if request.method == 'POST':
            what = request.form['search']
            where = request.form['location']

            req=requests.get(f'https://api.adzuna.com/v1/api/jobs/in/search/1?app_id=e37ee2b8&app_key=859675e385b76041aeee54442e5dff48&results_per_page=50&what={what}&where={where}&content-type=application/json')
            data=json.loads(req.content)
            return render_template('jobsearch.html', data=data["results"])
                
           
        else:
            return render_template('jobsearch.html')
    else:
        return redirect(url_for('login'))


@app.route('/jobsearch/<what>/<where>/<salary_min>')
def jobsearch1(what,where,salary_min):
    if g.firstname:

        req=requests.get(f'https://api.adzuna.com/v1/api/jobs/in/search/1?app_id=e37ee2b8&app_key=859675e385b76041aeee54442e5dff48&results_per_page=50&what={what}&where={where}&salary_min={salary_min}&content-type=application/json')
        data = json.loads(req.content) 
        
        return render_template('jobsearch.html', data=data["results"])
           
            
    else:
        return redirect(url_for('login'))
    
@app.route('/nearbyme', methods =['GET', 'POST'])
def nearbyme():
    if g.firstname:
        if request.method == 'POST':
            what = request.form['search']
            where = request.form['location']
            url = "https://api.foursquare.com/v3/places/search"

            params = {
                "query": what,
                "near": where,
                "sort":"DISTANCE"
            }

            headers = {
                "Accept": "application/json",
                "Authorization": "fsq3iQSlbl27t0r5qEReFsilO1V/d4eazl4/1jmnNwG53T0="
            }

            response = requests.request("GET", url, params=params, headers=headers)

            data=json.loads(response.content)
            return render_template('nearbyme.html', data=data["results"])
                
           
        else:
            return render_template('nearbyme.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/registerhg', methods =['GET', 'POST'])
def registerhg():
    if request.method == 'POST':
        conn = sqlite3.connect("C:\\Users\\abboj\\OneDrive\\Desktop\\job-recommender-main\\likhijr.db")
        c = conn.cursor()
        name= request.form['name']
        city= request.form['city']
        address= request.form['address']
        noofrooms= request.form['noofrooms']
        rent= request.form['rent']
        contact= request.form['contact']
        c.execute(f"INSERT INTO housing (name,city,address,noofrooms,rent,contact) values ('{name}','{city}','{address}','{noofrooms}','{rent}','{contact}');")
        conn.commit()
        conn.close()
        flash("Details added successfully", category='success') 
        return render_template('index.html')
    else:
        return render_template('housingregister.html')

@app.route('/registerhc', methods =['GET', 'POST'])
def registerhc():
    if request.method == 'POST':
        conn = sqlite3.connect("C:\\Users\\abboj\\OneDrive\\Desktop\\job-recommender-main\\likhijr.db")
        c = conn.cursor()
        name= request.form['name']
        city= request.form['city']
        address= request.form['address']
        type= request.form['type']

        contact= request.form['contact']
        c.execute(f"INSERT INTO healthcare (name,city,address,type,contact) values ('{name}','{city}','{address}','{type}','{contact}');")
        conn.commit()
        conn.close()
        flash("Details added successfully", category='success') 
        return render_template('index.html')
    else:
        
        return render_template('healthcareregister.html')

@app.route('/registerjt', methods =['GET', 'POST'])
def registerjt():
    if request.method == 'POST':
        conn = sqlite3.connect("C:\\Users\\abboj\\OneDrive\\Desktop\\job-recommender-main\\likhijr.db")
        c = conn.cursor()
        name= request.form['name']
        city= request.form['city']
        address= request.form['address']
        type= request.form['type']
        des= request.form['des']
        contact= request.form['contact']
        c.execute(f"INSERT INTO jobtraining (name,city,address,type,description,contact) values ('{name}','{city}','{address}','{type}','{des}','{contact}');")
        conn.commit()
        conn.close()
        flash("Details added successfully", category='success') 
        return render_template('index.html')
    else:
        
        return render_template('jobtrainingregister.html')

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('firstname', None)
   g.firstname= None
  
   return redirect(url_for('home')) 


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0',debug = True,port = 8081)