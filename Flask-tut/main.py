from fileinput import filename

from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug import secure_filename
import json
from flask_mail import Mail
import os
import math

with open('config.json', 'r') as c:
    params =  json.load(c) ["params"]

local_server= True
app = Flask(__name__)
app.config['UPLOAD_FOLDER']= params["upload_location"]
app.secret_key= 'king-of-avalon'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD = params['gmail_password']
)
mail=Mail(app)

if(local_server==True):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_no = db.Column(db.Integer, unique=True, nullable=False)
    mes = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    contant = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)
    subtitles = db.Column(db.String(80), nullable=False)

@app.route("/")
def home():
    posts= Posts.query.filter_by().all() #[0:params['no_of_posts']]
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page= request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts= posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if(page==1):
        prev="#"
        next="/?page="+ str(page+1)
    elif(page==last):
        prev= "/?page="+ str(page-1)
        next="#"
    else:
        prev= "/?page="+ str(page-1)
        next="/?page="+ str(page+1)
    return render_template("index.html", params=params, posts=posts, prev=prev, next=next)

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method== 'POST':
            box_title= request.form.get('title')
            subt= request.form.get('subtitles')
            content= request.form.get('content')
            img= request.form.get('image')
            slug= request.form.get('slug')
            date=datetime.now()

            if(sno=='0'):
                post=Posts(title=box_title, subtitles=subt, contant=content, img_file=img, slug=slug, date=datetime.now())
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title= box_title
                post.subtitles= subt
                post.contant= content
                post.img_file= img
                post.slug=slug
                post.date=date
                db.session.commit()
                return redirect('/edit/'+sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template("edit.html", params=params, post=post,  sno=sno)

@app.route("/about")
def about():
    return render_template("about.html", params=params)

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if('user' in session and session['user']== params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method=='POST':
        username= request.form.get('user')
        password= request.form.get('password')
        if(username==params['admin_user'] and password==params['admin_password']):
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)

    else:
        return render_template("login.html", params=params)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        '''ADD ENTRY TO THE DATABASE'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone_no')
        message = request.form.get('message')

        entry = Contacts(name=name, email=email, phone_no=phone, mes=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New messege from'+ name,
                          sender='email',
                          recipients=[params['gmail_user']],
                          body = message + "\n" + phone
                          )
    return render_template("contact.html", params=params)

@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if(request.method== 'POST'):
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded Successfully"

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", params=params, post=post)


app.run(debug=True)
