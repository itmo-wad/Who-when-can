from flask import Flask, session, request, redirect, url_for, render_template, flash, jsonify, make_response
from . forms import  AuthForm, MeetingForm, DaysAndHoursForm
from main import app
import hashlib
import json
import hmac
import base64
from flask_pymongo import PyMongo
from bson import ObjectId
import json2table

app.config["MONGO_URI"] = "mongodb://localhost:27017/whowhencandb"
mongo = PyMongo(app)

pepper ='*VrLQjDX&ZhmEmQV%3Q<'
key=b'super_secret_k3y_y0u_will_n3v3r_gue$$'

@app.route('/')
def index():        	
    try:
        if session['user_available']:
            return redirect(url_for('create_step_1')) ## change endpoint to: redirect to the list of the meetings (?)
    except:
        pass
    return redirect(url_for('create_step_1'))

# 
# function for authentication for client and creator
#

def Auth(authform): 
    if request.method == 'POST' and authform.validate_on_submit():
        try:
            #check if name+username+password already exists 
            user = mongo.db.users.find_one({'name': authform.name.data, 'username': authform.username.data, 'password': authform.password.data})
            if user != None:
                session['current_user_id'] = str(user['_id'])
                pass ## do something. go to your meeting list for example
            else:
                #if not, register him
                session['current_user_id'] = str(mongo.db.users.insert_one({'name': authform.name.data, 'username': authform.username.data, 'password': authform.password.data}).inserted_id)
            session['user_available'] = True
            return True
        except Exception as e:
            flash("Something wrong")
            print(e)
    return False


def table_filling(daysandhoursform):
    if request.method == 'POST':
        try:
            #insert username and his choosen dates to the db
            mongo.db.meetings.update_one({'_id': ObjectId(session['meeting_id'])}, {"$set":{'users.'+session['current_user_id']:{'selected_dates':json.loads(daysandhoursform.selecteddaysandhours.data)}}})
            return 'Updated'
        except Exception as e:
            flash("Something wrong")
            print(e)
    else:
        #extract dates for this meeting from db and create HTML table from it
        available_dates_json = mongo.db.meetings.find_one({'_id':ObjectId(session['meeting_id'])})['available_dates']
        build_direction = "TOP_TO_BOTTOM"
        #table_attributes = {"style": "width:100%"}
        #table = json2table.convert(infoFromJson,build_direction=build_direction,table_attributes=table_attributes))
        table = json2table.convert(available_dates_json,build_direction=build_direction)
        return table
    return False


####################################################################
###########                   creator part            ##############
####################################################################
@app.route('/create_step_1', methods=['GET', 'POST'])
def create_step_1():
    authform = AuthForm(request.form)
    if Auth(authform):
        return redirect(url_for('create_step_2'))
    else:
        return render_template('create_step_1.html', authform=authform)
    


@app.route('/create_step_2', methods=['GET','POST']) #fill meting name, some info and choose dates
def create_step_2():
    if session['user_available'] != True:
        return redirect(url_for('create_step_1'))
    else:
        meetingform = MeetingForm(request.form)
        if request.method == 'POST' and meetingform.validate_on_submit():
            try:
                #insert creator name, meeting name, some info and choosen dates to the db
                session['meeting_id'] = str(mongo.db.meetings.insert_one({'name': meetingform.meetingname.data, 'info': meetingform.info.data, 'creator':ObjectId(session['current_user_id']), 'available_dates': json.loads(meetingform.available_dates.data),'users':{}}).inserted_id)
                return redirect(url_for('create_step_3'))
            except Exception as e:
                flash("Something wrong")
                print(e)
    return render_template('create_step_2.html', meetingform=meetingform)


@app.route('/create_step_3', methods=['GET','POST']) ##choose availabe dates for admin. 
def create_step_3():
    if session['user_available'] != True:
        return redirect(url_for('create_step_1'))
    else:
        daysandhoursform = DaysAndHoursForm(request.form)
        result = table_filling(daysandhoursform)
        if result == 'Updated':
            meeting_id_hash = hashlib.sha256(pepper.encode('UTF-8')+ session['meeting_id'].encode('UTF-8')).hexdigest()
            mongo.db.meetings.update_one({'_id': ObjectId(session['meeting_id'])}, {"$set":{'meeting_id_hash':meeting_id_hash}})
            return redirect(url_for('meeting_created',id=meeting_id_hash))
        elif result != False:
            return render_template('create_step_3.html', table=result, daysandhoursform=daysandhoursform)
    return redirect(url_for('index'))

@app.route('/meeting_created/<id>')
def meeting_created(id):        	
    try:
        if session['user_available']:
            return render_template('meeting_created.html', id=id) ## change endpoint to: redirect to the list of the meetings (?)
    except:
        flash("Sorry, there is no meeting you trying to access")
    return redirect(url_for('create_step_1'))
#
#create page after meeting creation for id copy and instructions
#

####################################################################
###########                    client part            ##############
####################################################################

@app.route('/meetings/<id>', methods=['GET']) # page for id validation
def meetings(id):
    try:
        #check if meeting ID exists 
        meeting_id = str(mongo.db.meetings.find_one({'meeting_id_hash': id})['_id']) 
        if meeting_id == None:
            flash("Sorry, there is no meeting you trying to access")
        else:
            session['meeting_id'] = meeting_id
            return redirect(url_for('meeting_login'))
    except Exception as e:
            flash("Something wrong")
            print(e)
    return render_template('error.html')        


@app.route('/meeting_login', methods=['GET', 'POST']) #authentication page for table filling
def meeting_login():
    authform = AuthForm(request.form)
    if Auth(authform):
        return redirect(url_for('time_picking'))
    else:
        return render_template('meeting_login.html', authform=authform)


@app.route('/time_picking', methods=['GET', 'POST'])
def time_picking():
    if session['user_available'] != True:
        return redirect(url_for('meeting_login'))
    else:
        daysandhoursform = DaysAndHoursForm(request.form)
        result = table_filling(daysandhoursform)
        if result == 'Updated':
            return redirect(url_for('finish'))
        elif result != False:
            return render_template('time_picking.html', table=result, daysandhoursform=daysandhoursform)
    return redirect(url_for('index'))


@app.route('/finish')
def finish():
    try:
        if session['user_available']:
            return render_template('success.html') ## change endpoint to: redirect to the list of the meetings (?)
    except Exception as e:
            flash("Sorry, there is no meeting you trying to access")
            print(e) 
    return render_template('error.html')    
