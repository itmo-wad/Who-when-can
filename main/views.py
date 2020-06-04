from flask import Flask, session, request, redirect, url_for, render_template, flash, jsonify, make_response, send_from_directory
from . forms import  AuthForm, MeetingForm, DaysAndHoursForm
from main import app, config
from flask_pymongo import PyMongo
from bson import ObjectId
import hashlib, json, hmac, base64, json2table, datetime

app.config["MONGO_URI"] = config.mongo_uri
mongo = PyMongo(app)

#security stuff
@app.after_request
def add_headers(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN; DENY"
    response.headers["X-XSS-Protection"]="1; mode=block"
    response.headers["X-Content-Type-Options"]="nosniff"
    #response.headers["Cache-control"]="no-store"
    #response.headers["Pragma"]="no-cache"
    response.headers["Server"]="no server for you, dear hacker"
    return response


@app.route('/logout')
def logout():        	
    try:
        if session['user_available']:
            session.clear()
            session['user_available']=False
            return redirect(url_for('create_step_1')) ## change endpoint to: redirect to the list of the meetings (?)
    except:
        pass
    return redirect(url_for('create_step_1'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/img', 'favicon.ico')

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
                session['current_user'] = authform.username.data
                return 'exists'
            else:
                #if not, register him
                session['current_user_id'] = str(mongo.db.users.insert_one({'name': authform.name.data, 'username': authform.username.data, 'password': authform.password.data}).inserted_id)
            session['user_available'] = True
            session['current_user'] = authform.username.data
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
        dates_json = mongo.db.meetings.find_one({'_id':ObjectId(session['meeting_id'])})
        available_dates_json = dates_json['available_dates']
        duration = dates_json['duration']
        print(available_dates_json)
        print(duration)
        for day in available_dates_json['days']:
            for hour in day['hours']:
                 day['hours'][hour] = day['hours'][hour] + ' - ' + ':'.join([str(elem) for elem in (str(datetime.datetime.strptime(day['hours'][hour], '%H:%M') + datetime.timedelta(hours=int(duration.split(':')[0]), minutes=int(duration.split(':')[1]))).split()[1].split(':')[:-1])]) # oneliner to make interval from start and duration
        build_direction = "TOP_TO_BOTTOM"
        table_attributes = {"class": "result__table"}
        #table = json2table.convert(infoFromJson,build_direction=build_direction,table_attributes=table_attributes))
        table = json2table.convert(available_dates_json,build_direction=build_direction, table_attributes=table_attributes)
        return table
    return False


####################################################################
###########                   creator part            ##############
####################################################################
@app.route('/create_step_1', methods=['GET', 'POST'])
def create_step_1():
    try:
        session['user_available']
    except:
        session['user_available'] = False
    if session['user_available'] != True:
        authform = AuthForm(request.form)
        if Auth(authform):
            return redirect(url_for('create_step_2'))
        else:
            return render_template('create_step_1.html', authform=authform)
    else:
        return redirect(url_for('create_step_2'))
    


@app.route('/create_step_2', methods=['GET','POST']) #fill meting name, some info and choose dates
def create_step_2():
    try:
        session['user_available']
    except:
        session['user_available']=False
    if session['user_available'] != True:
        return redirect(url_for('create_step_1'))
    else:
        meetingform = MeetingForm(request.form)
        if request.method == 'POST' and meetingform.validate_on_submit():
            try:
                #insert creator name, meeting name, some info and choosen dates to the db
                session['meeting_id'] = str(mongo.db.meetings.insert_one({'name': meetingform.meetingname.data, 'info': meetingform.info.data, 'duration': str(meetingform.duration.data), 'creator':ObjectId(session['current_user_id']), 'available_dates': json.loads(meetingform.available_dates.data),'users':{}}).inserted_id)
                return redirect(url_for('create_step_3'))
            except Exception as e:
                flash("Something wrong")
                print(e)
    return render_template('create_step_2.html', meetingform=meetingform)


@app.route('/create_step_3', methods=['GET','POST']) ##choose availabe dates for admin. 
def create_step_3():
    try:
        session['user_available']
        session['meeting_id']
    except:
        session['user_available']=False
        return redirect(url_for('create_step_1'))
    
    if session['user_available'] != True:
        return redirect(url_for('create_step_1'))
    else:
        daysandhoursform = DaysAndHoursForm(request.form)
        result = table_filling(daysandhoursform)
        if result == 'Updated':
            meeting_id_hash = hashlib.sha256(config.pepper.encode('UTF-8')+ session['meeting_id'].encode('UTF-8')).hexdigest()
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
            session['meeting_id_hash'] = id
            session['meeting_id'] = meeting_id
            return redirect(url_for('meeting_login'))
    except Exception as e:
            flash("Something wrong")
            print(e)
    return render_template('error.html')        


@app.route('/meeting_login', methods=['GET', 'POST']) #authentication page for table filling
def meeting_login():
    authform = AuthForm(request.form)
    resp = Auth(authform)
    if resp:
        if resp=='exists':
            user = mongo.db.meetings.find_one({'meeting_id_hash': session['meeting_id_hash']})
            print(user)
            if user.get('creator') == ObjectId(session['current_user_id']):
                session['creator']=session['meeting_id_hash']
                return redirect(url_for('meeting_edit_creator'))
            elif session['current_user_id'] in user["users"]:
                session['user']=session['meeting_id_hash']
                return redirect(url_for('meeting_edit'))
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



####################################################################
###########                    edit   part            ##############
####################################################################

####################################################################
###########           UNDER CONSTRUCTION  HELP!!!111  ##############
####################################################################

@app.route('/meeting_edit_creator') # page for creator meeting edit
def meeting_edit_creator():
    try:
        if session['user_available'] and session['creator']==session['meeting_id_hash']:
            return render_template('success.html') 
    except Exception as e:
            flash("Sorry, there is no meeting you trying to access")
            print(e) 
    return render_template('error.html')  


@app.route('/meeting_edit') # page for user time repick
def meeting_edit():
    try:
        if session['user_available'] and session['user']==session['meeting_id_hash']:
            return render_template('success.html')
    except Exception as e:
            flash("Sorry, there is no meeting you trying to access")
            print(e) 
    return render_template('error.html')  