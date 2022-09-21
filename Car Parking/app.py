from flask import Flask, render_template, Response, request, redirect, url_for, session
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from ParkingSpacePicker import parkingspacepicker
from main import generate_frame
import json
import os
from datetime import datetime

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num=phone, msg=message, date=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=message + "\n" + email + "\n" + phone)

    return render_template('contact.html', params=params)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    error = None
    if request.method == 'POST':
        if request.form['uname'] != 'mihir' or request.form['pass'] != 'mihir123':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('detection'))
    return render_template('dashboard.html', error=error)


@app.route('/detection', methods=['GET', 'POST'])
def detection():
    if request.method == "POST":
        if 'upload' not in request.files:
            print("no file part")
            return redirect("/")
        file = request.files['upload']
        if file.filename == '':
            print('No image selected for uploading')
            return redirect(request.url)
        else:
            # base_path = os.path.abspath(os.path.dirname(__file__))
            # print(base_path)
            # upload_path = os.path.join(base_path, "video")
            # print(upload_path)
            # f.save(os.path.join(upload_path, secure_filename(f.filename)))
            # filename = secure_filename(file.filename)
            filename = "output.mp4"
            print(filename)
            file.save(os.path.join("output video", filename))
            # print('upload_video filename: ' + filename)
            print("successful")
            # flash('Video successfully uploaded and displayed below')
            return render_template('detection.html', filename=filename)
    return render_template('detection.html')


@app.route('/anotation')
def anotation():
    # display = 0
    return render_template('anotation.html')


@app.route('/video/<filename>')
def video(filename):
    print('display_video filename: ' + filename)
    display = filename
    return Response(generate_frame(display), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/videocam')
def videocam():
    display = 0
    return Response(parkingspacepicker(), mimetype='multipart/x-mixed-replace; boundary=frame')


app.run(debug=True)
