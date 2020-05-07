from flask import Flask, session, request, redirect, url_for, render_template, flash, jsonify, make_response
from . forms import  AuthForm, MeetingForm
from main import app
import hashlib
import json
#import bcrypt
import hmac
#import glob, os
import base64
#from werkzeug.utils import secure_filename

from flask_pymongo import PyMongo

app.config["MONGO_URI"] = "mongodb://localhost:27017/task5"
mongo = PyMongo(app)


key=b'super_secret_k3y_y0u_will_n3v3r_gue$$'

@app.route('/')
def index():        	
    try:
        if session['user_available']:
            return redirect(url_for('create_step_1')) ## change endpoint to: redirect to the list of the mitings (?)
    except:
        pass
    return redirect(url_for('create_step_1'))


@app.route('/create_step_1', methods=['GET', 'POST'])
def create_step_1():
    authform = AuthForm(request.form)
    if request.method == 'POST' and authform.validate_on_submit():
        #try:
        session['current_user'] = mongo.db.users.find_one({'username': authform.name.data, 'username': authform.username.data, 'password': authform.password.data})
        print(session['current_user']) ## remove
        if session['current_user']:
            pass ## do something
        else:
            mongo.db.users.insert_one({'username': authform.name.data, 'username': authform.username.data, 'password': authform.password.data})
        session['user_available'] = True
        return redirect(url_for('create_step_2'))
        #except Exception as e:
        #    flash("Something wrong")
        #    print(e)
    return render_template('create_step_1.html', authform=authform)


@app.route('/create_step_2', methods=['GET','POST'])
def create_step_2():
    if session['user_available'] != True:
        return redirect(url_for('create_step_1'))
    else:
        if request.method == 'POST' and MeetingForm.validate_on_submit():
            try:
                mongo.db.meetings.insert_one({'name': MeetingForm.meetingname.data, 'info': MeetingForm.info.data, 'creator':session['current_user'], available_dates: MeetingForm.available_dates.data})
                return "OK"
            except Exception as e:
                flash("Something wrong")
                print(e)
    return render_template('create_step_2.html', MeetingForm=MeetingForm)


@app.route('/create_step_3', methods=['GET','POST']) ##choose availabe dates for admin. mb change to user with auth
def create_step_3():
    if !session['user_available']:
        return redirect(url_for('create_step_1'))
    else:
        if request.method == 'POST':
            try:
                mongo.db.meetings.update_one({'username': session['current_user']}, {"$set":{'avatar':base64.b64encode(f.read()).decode()}})
                return redirect(url_for('create_step_3'))
            except Exception as e:
                flash("Something wrong")
                print(e)
    return render_template('create_step_3.html', MeetingForm=MeetingForm)
    

    
    
    '''



@app.route('/upload', methods = ['POST'])
def upload():
    if session['user_available']:
            if 'file' not in request.files:
                flash('No file part')
                return redirect(url_for('secret'))
            f = request.files['file']
            if f.filename.split(".")[-1] in allowed:
                mongo.db.users.update_one({'username': session['current_user']}, {"$set":{'avatar':base64.b64encode(f.read()).decode()}})
                flash('File uploaded successfully')
            else:
                flash('Screw hakers!!11')
            return redirect(url_for('secret'))
    else:
        flash('You are not authenticated')
   

@app.route('/secret', methods=['GET'])
def secret():
    if session['user_available']:
            avatar =  mongo.db.users.find_one({'username':session['current_user']})['avatar']
            return render_template('secret.html',changeform=ChangeForm(request.form),avatar=avatar)
    else:
        flash('You are not authenticated')
    return redirect(url_for('signin'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        