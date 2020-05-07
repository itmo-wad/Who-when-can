from flask import Flask, session, request, redirect, url_for, render_template, flash, jsonify, make_response
from . forms import  SignUpForm, SignInForm, ChangeForm
from main import app
import hashlib
import json
import bcrypt
import hmac
import glob, os
import base64
from werkzeug.utils import secure_filename

from flask_pymongo import PyMongo

app.config["MONGO_URI"] = "mongodb://localhost:27017/task5"
mongo = PyMongo(app)

allowed = ['jpeg', 'jpg', 'gif', 'png', 'apng', 'svg', 'bmp']
key=b'super_secret_k3y_y0u_will_n3v3r_gue$$'

@app.route('/')
def index():        	
    if session['user_available']:
        return redirect(url_for('secret'))
    else:
        flash('You are not authenticated')
    return redirect(url_for('signin'))


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
        if session['user_available']:
            return redirect(url_for('secret'))
    except Exception:
        pass
    signupform = SignUpForm(request.form)
    if request.method == 'POST' and signupform.validate_on_submit():
        try:
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw((signupform.password.data).encode('utf-8'), salt)
            data = {'username': signupform.username.data, 'password': password.decode("utf-8"), 'salt':salt.decode("utf-8"), 'avatar':''}
            mongo.db.users.insert_one(data)
        except Exception as e:
            flash("Something wrong")
            print(e)
            return render_template('signup.html', signupform=signupform)
        return redirect(url_for('signin'))
    return render_template('signup.html', signupform=signupform)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    try: 
        if session['user_available']:
            return redirect(url_for('secret'))
    except Exception:
        pass
    signinform = SignInForm(request.form)
    if request.method == 'POST':
        if signinform.validate_on_submit():
            username = signinform.username.data
            log =  mongo.db.users.find_one({'username':username})
            if log!=None:
                if log['password'].encode('utf-8') == bcrypt.hashpw(signinform.password.data.encode('utf-8'), log['salt'].encode('utf-8')):
                    current_user = log['username']
                    session['current_user'] = current_user
                    session['user_available'] = True
                    return redirect(url_for('secret'))
                else:
                    flash('Wrong login or password') 
            else:
                flash('Wrong login or password')
    return render_template('signin.html', signinform=signinform)

@app.route('/change_pass', methods=['GET', 'POST'])
def change_pass():
    try: 
        if session['user_available']:
            print(1)
            if request.method == 'POST':
                changeform = ChangeForm(request.form)
                print(2)
                if changeform.validate_on_submit():
                    try:
                        print(3)
                        salt = bcrypt.gensalt()
                        mongo.db.users.update_one({'username': session['current_user']}, {"$set":{'password': bcrypt.hashpw((changeform.password.data).encode("utf-8"), salt).decode("utf-8"), 'salt':salt.decode("utf-8")}})
                        flash('Success') 
                    except Exception as e:
                        print(e)
                else:
                    flash('Wrong something') 
            return redirect(url_for('secret'))
    except Exception as e:
        print(e)
    return  redirect(url_for('signin'))

@app.route('/logout')
def logout():
    session.clear()
    session['user_available'] = False
    return redirect(url_for('signin'))

if __name__ == '__main__':
    app.run()
